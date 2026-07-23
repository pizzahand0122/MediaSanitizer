"""Safe repair-plan primitives for metadata-only Matroska changes."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
from collections.abc import Callable


_LANGUAGE_TAG = re.compile(
    r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$"
)


@dataclass(frozen=True)
class TrackMetadataChange:
    """Permitted metadata changes for one Matroska track.

    ``None`` means leave a property unchanged. An empty name is allowed and
    explicitly removes an existing track name.
    """

    track_uid: int
    default: bool | None = None
    name: str | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.track_uid, int)
            or isinstance(self.track_uid, bool)
            or self.track_uid <= 0
        ):
            raise ValueError("track UID must be a positive integer")
        if self.default is not None and not isinstance(self.default, bool):
            raise TypeError("default-track flag must be a boolean or None")
        if self.name is not None and any(
            ord(character) < 32 for character in self.name
        ):
            raise ValueError("track name cannot contain control characters")
        if self.language is not None and not _LANGUAGE_TAG.fullmatch(
            self.language
        ):
            raise ValueError("language must be a valid BCP 47 language tag")
        if self.default is None and self.name is None and self.language is None:
            raise ValueError("track change must modify at least one property")

    def property_assignments(self) -> tuple[str, ...]:
        """Return only mkvpropedit metadata assignments allowed by this model."""
        assignments: list[str] = []
        if self.default is not None:
            assignments.append(f"flag-default={int(self.default)}")
        if self.name is not None:
            assignments.append(f"name={self.name}")
        if self.language is not None:
            assignments.append(f"language-ietf={self.language}")
        return tuple(assignments)


@dataclass(frozen=True)
class MkvRepairPlan:
    """A validated, metadata-only repair plan for one MKV file."""

    path: Path
    changes: tuple[TrackMetadataChange, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "changes", tuple(self.changes))
        if self.path.suffix.lower() != ".mkv":
            raise ValueError("repair plans are limited to MKV files")
        if not self.changes:
            raise ValueError("repair plan must contain at least one change")
        if not all(
            isinstance(change, TrackMetadataChange) for change in self.changes
        ):
            raise TypeError("repair plan changes must be track metadata changes")
        track_uids = [change.track_uid for change in self.changes]
        if len(track_uids) != len(set(track_uids)):
            raise ValueError("repair plan cannot contain duplicate track UIDs")

    def command(self, executable: str = "mkvpropedit") -> tuple[str, ...]:
        """Compile the plan to a metadata-only mkvpropedit invocation."""
        arguments = [executable, str(self.path)]
        for change in self.changes:
            arguments.extend(("--edit", f"track:={change.track_uid}"))
            for assignment in change.property_assignments():
                arguments.extend(("--set", assignment))
        return tuple(arguments)

    def preview(self, executable: str = "mkvpropedit") -> str:
        """Return a shell-readable dry-run preview without executing anything."""
        return shlex.join(self.command(executable))


class ConfirmationRequiredError(RuntimeError):
    """Raised when execution was not explicitly confirmed."""


class RepairRollbackError(RuntimeError):
    """Raised when both the repair and its automatic rollback fail."""


@dataclass(frozen=True)
class RepairResult:
    """Details of a successfully applied repair."""

    path: Path
    backup_path: Path | None
    command: tuple[str, ...]


class MkvRepairExecutor:
    """Apply a validated plan with confirmation, backup, and rollback guards."""

    def __init__(
        self,
        executable: str = "mkvpropedit",
        *,
        runner: Callable[..., object] = subprocess.run,
        validator: Callable[[MkvRepairPlan], None] | None = None,
        validation_executable: str = "mkvmerge",
        validation_runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.executable = executable
        self._runner = runner
        self._validator = validator
        self.validation_executable = validation_executable
        self._validation_runner = validation_runner

    def execute(
        self,
        plan: MkvRepairPlan,
        *,
        confirmed: bool = False,
        keep_backup: bool = False,
    ) -> RepairResult:
        """Apply ``plan`` only after confirmation and a safe backup.

        The backup is removed after successful validation unless
        ``keep_backup=True``. Execution or validation failure atomically moves
        it over the possibly modified original.
        """
        if not isinstance(plan, MkvRepairPlan):
            raise TypeError("executor requires an MKV repair plan")
        if confirmed is not True:
            raise ConfirmationRequiredError(
                "repair requires explicit confirmation (confirmed=True)"
            )

        path = plan.path
        if not path.is_file():
            raise FileNotFoundError(f"repair target is not a file: {path}")

        backup_path = path.with_name(f"{path.name}.mediasanitizer.bak")
        if backup_path.exists():
            raise FileExistsError(
                f"refusing to overwrite existing backup: {backup_path}"
            )

        command = plan.command(self.executable)
        shutil.copy2(path, backup_path)
        try:
            self._runner(command, check=True)
            if self._validator is None:
                self._validate(plan)
            else:
                self._validator(plan)
        except Exception as repair_error:
            try:
                os.replace(backup_path, path)
            except Exception as rollback_error:
                raise RepairRollbackError(
                    f"repair failed and rollback failed; backup remains at "
                    f"{backup_path}"
                ) from rollback_error
            raise repair_error

        retained_backup = backup_path if keep_backup else None
        if not keep_backup:
            backup_path.unlink()
        return RepairResult(path, retained_backup, command)

    def _validate(self, plan: MkvRepairPlan) -> None:
        """Verify that the edited file is readable and has requested values."""
        command = (
            self.validation_executable,
            "--identify",
            "--identification-format",
            "json",
            str(plan.path),
        )
        completed = self._validation_runner(
            command, check=True, capture_output=True, text=True
        )
        document = json.loads(completed.stdout)
        tracks = {
            track.get("properties", {}).get("uid"): track
            for track in document.get("tracks", ())
        }
        for change in plan.changes:
            try:
                properties = tracks[change.track_uid]["properties"]
            except (KeyError, TypeError) as error:
                raise ValueError(
                    f"validation could not find track UID {change.track_uid}"
                ) from error
            expected = {
                "default_track": change.default,
                "track_name": change.name,
                "language_ietf": change.language,
            }
            for property_name, expected_value in expected.items():
                if expected_value is None:
                    continue
                actual_value = properties.get(property_name)
                if property_name == "track_name" and actual_value is None:
                    actual_value = ""
                if actual_value != expected_value:
                    raise ValueError(
                        f"validation failed for track UID {change.track_uid}: "
                        f"{property_name} is {actual_value!r}, expected "
                        f"{expected_value!r}"
                    )
