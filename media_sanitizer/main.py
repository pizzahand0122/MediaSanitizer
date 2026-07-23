import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from media_sanitizer.models import ScanSummary
from media_sanitizer.repair import (
    MkvRepairExecutor,
    MkvRepairPlan,
    TrackMetadataChange,
)
from media_sanitizer.scanner import scan_library


_SCAN_USAGE = "Usage: python -m media_sanitizer.main <directory>"
_REPAIR_USAGE = (
    "Usage: python -m media_sanitizer.main repair <file.mkv> <track-uid> "
    "[--default true|false] [--name <name>] [--language <tag>] [--dry-run] "
    "[--keep-backup]"
)


def _parse_repair_arguments(
    arguments: Sequence[str],
) -> tuple[MkvRepairPlan, bool, bool]:
    if len(arguments) < 3:
        raise ValueError(_REPAIR_USAGE)

    path = Path(arguments[1])
    try:
        track_uid = int(arguments[2])
    except ValueError as error:
        raise ValueError("track UID must be a positive integer") from error

    values: dict[str, object] = {"track_uid": track_uid}
    dry_run = False
    keep_backup = False
    position = 3
    while position < len(arguments):
        option = arguments[position]
        if option == "--dry-run":
            if dry_run:
                raise ValueError("--dry-run may only be specified once")
            dry_run = True
            position += 1
            continue
        if option == "--keep-backup":
            if keep_backup:
                raise ValueError("--keep-backup may only be specified once")
            keep_backup = True
            position += 1
            continue
        if option not in {"--default", "--name", "--language"}:
            raise ValueError(f"unknown repair option: {option}")
        key = option[2:]
        if key in values:
            raise ValueError(f"{option} may only be specified once")
        if position + 1 >= len(arguments):
            raise ValueError(f"{option} requires a value")
        value: object = arguments[position + 1]
        if option == "--default":
            normalized = str(value).casefold()
            if normalized not in {"true", "false"}:
                raise ValueError("--default must be true or false")
            value = normalized == "true"
        values[key] = value
        position += 2

    change = TrackMetadataChange(**values)
    return MkvRepairPlan(path, (change,)), dry_run, keep_backup


def _run_repair(
    arguments: Sequence[str],
    *,
    input_fn: Callable[[], str],
    executor: MkvRepairExecutor,
) -> int:
    try:
        plan, dry_run, keep_backup = _parse_repair_arguments(arguments)
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")
        return 2

    print("Repair plan (metadata only):")
    print(plan.preview(executor.executable))
    if dry_run:
        print("Dry run: no changes made.")
        return 0

    print("Type 'yes' to apply this repair: ", end="", flush=True)
    try:
        response = input_fn()
    except EOFError:
        response = ""
    if response.strip().casefold() != "yes":
        print("Repair cancelled.")
        return 0

    try:
        result = executor.execute(
            plan, confirmed=True, keep_backup=keep_backup
        )
    except Exception as error:
        print(f"Error: repair failed: {error}")
        return 1

    if result.backup_path is None:
        print("Repair applied and validated.")
    else:
        print(f"Repair applied. Backup retained at: {result.backup_path}")
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[], str] = input,
    repair_executor: MkvRepairExecutor | None = None,
) -> int:
    """Scan a directory or preview and confirm a metadata-only MKV repair."""
    arguments = sys.argv[1:] if argv is None else argv

    if arguments and arguments[0] == "repair":
        return _run_repair(
            arguments,
            input_fn=input_fn,
            executor=repair_executor or MkvRepairExecutor(),
        )

    if len(arguments) != 1:
        print(_SCAN_USAGE)
        return 2

    directory = Path(arguments[0])
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}")
        return 1

    summary = ScanSummary.from_results(scan_library(directory))

    print(f"Total files: {summary.total_files}")
    print(f"Clean files: {summary.clean_files}")
    print(f"Files with issues: {summary.files_with_issues}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
