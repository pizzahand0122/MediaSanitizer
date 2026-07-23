import unittest
import json
from pathlib import Path
import subprocess
import tempfile
from unittest import mock

from media_sanitizer.repair import (
    ConfirmationRequiredError,
    MkvRepairExecutor,
    MkvRepairPlan,
    RepairRollbackError,
    TrackMetadataChange,
)


class TrackMetadataChangeTests(unittest.TestCase):
    def test_compiles_only_supported_metadata_properties(self):
        change = TrackMetadataChange(
            track_uid=42,
            default=True,
            name="English Commentary",
            language="en-US",
        )

        self.assertEqual(
            change.property_assignments(),
            (
                "flag-default=1",
                "name=English Commentary",
                "language-ietf=en-US",
            ),
        )

    def test_allows_clearing_a_track_name(self):
        self.assertEqual(
            TrackMetadataChange(7, name="").property_assignments(),
            ("name=",),
        )

    def test_rejects_an_empty_change(self):
        with self.assertRaisesRegex(ValueError, "at least one property"):
            TrackMetadataChange(1)

    def test_rejects_invalid_track_uids(self):
        for uid in (0, -1, True, "1"):
            with self.subTest(uid=uid):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    TrackMetadataChange(uid, default=False)

    def test_rejects_non_boolean_default_flags(self):
        with self.assertRaisesRegex(TypeError, "boolean"):
            TrackMetadataChange(1, default=1)

    def test_rejects_invalid_language_tags(self):
        for language in ("", "e", "languagex", "en_US", "en;rm"):
            with self.subTest(language=language):
                with self.assertRaisesRegex(ValueError, "BCP 47"):
                    TrackMetadataChange(1, language=language)

    def test_rejects_control_characters_in_names(self):
        with self.assertRaisesRegex(ValueError, "control characters"):
            TrackMetadataChange(1, name="Commentary\nTrack")


class MkvRepairPlanTests(unittest.TestCase):
    def test_compiles_metadata_only_command_by_track_uid(self):
        plan = MkvRepairPlan(
            Path("Movie.mkv"),
            (
                TrackMetadataChange(11, default=True, language="eng"),
                TrackMetadataChange(12, default=False, name="Commentary"),
            ),
        )

        self.assertEqual(
            plan.command(),
            (
                "mkvpropedit",
                "Movie.mkv",
                "--edit",
                "track:=11",
                "--set",
                "flag-default=1",
                "--set",
                "language-ietf=eng",
                "--edit",
                "track:=12",
                "--set",
                "flag-default=0",
                "--set",
                "name=Commentary",
            ),
        )

    def test_preview_quotes_arguments_and_does_not_execute(self):
        plan = MkvRepairPlan(
            Path("My Movie.mkv"),
            (TrackMetadataChange(1, name="Director's Commentary"),),
        )

        self.assertEqual(
            plan.preview(),
            "mkvpropedit 'My Movie.mkv' --edit track:=1 --set "
            "'name=Director'\"'\"'s Commentary'",
        )

    def test_rejects_non_mkv_files(self):
        with self.assertRaisesRegex(ValueError, "limited to MKV"):
            MkvRepairPlan(
                Path("movie.mp4"), (TrackMetadataChange(1, default=True),)
            )

    def test_rejects_empty_plans(self):
        with self.assertRaisesRegex(ValueError, "at least one change"):
            MkvRepairPlan(Path("movie.mkv"), ())

    def test_rejects_duplicate_track_uids(self):
        with self.assertRaisesRegex(ValueError, "duplicate track UIDs"):
            MkvRepairPlan(
                Path("movie.mkv"),
                (
                    TrackMetadataChange(1, default=True),
                    TrackMetadataChange(1, name="Main"),
                ),
            )

    def test_rejects_untyped_change_data(self):
        with self.assertRaisesRegex(TypeError, "track metadata changes"):
            MkvRepairPlan(Path("movie.mkv"), ({"track_uid": 1},))

    def test_normalizes_iterable_inputs_to_immutable_values(self):
        changes = [TrackMetadataChange(1, default=True)]
        plan = MkvRepairPlan("movie.MKV", changes)
        changes.append(TrackMetadataChange(2, default=False))

        self.assertEqual(plan.path, Path("movie.MKV"))
        self.assertEqual(len(plan.changes), 1)


class MkvRepairExecutorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.path = Path(self.temporary_directory.name) / "movie.mkv"
        self.path.write_bytes(b"original media")
        self.plan = MkvRepairPlan(
            self.path, (TrackMetadataChange(42, default=True),)
        )

    def test_requires_explicit_confirmation_before_creating_backup(self):
        calls = []

        with self.assertRaisesRegex(ConfirmationRequiredError, "explicit"):
            MkvRepairExecutor(runner=lambda *args, **kwargs: calls.append(args)).execute(
                self.plan
            )

        self.assertEqual(calls, [])
        self.assertFalse(self.path.with_name("movie.mkv.mediasanitizer.bak").exists())

    def test_backs_up_validates_then_removes_temporary_backup(self):
        calls = []
        validations = []

        def validate(plan):
            self.assertEqual(
                self.path.with_name("movie.mkv.mediasanitizer.bak").read_bytes(),
                b"original media",
            )
            validations.append(plan)

        result = MkvRepairExecutor(
            runner=lambda command, **kwargs: calls.append((command, kwargs)),
            validator=validate,
        ).execute(self.plan, confirmed=True)

        self.assertIsNone(result.backup_path)
        self.assertFalse(
            self.path.with_name("movie.mkv.mediasanitizer.bak").exists()
        )
        self.assertEqual(validations, [self.plan])
        self.assertEqual(
            calls,
            [(self.plan.command(), {"check": True})],
        )

    def test_default_validator_identifies_file_and_checks_requested_metadata(self):
        validation_calls = []

        class Completed:
            stdout = json.dumps(
                {
                    "tracks": [
                        {
                            "properties": {
                                "uid": 42,
                                "default_track": True,
                            }
                        }
                    ]
                }
            )

        result = MkvRepairExecutor(
            runner=lambda *args, **kwargs: None,
            validation_runner=lambda command, **kwargs: (
                validation_calls.append((command, kwargs)) or Completed()
            ),
        ).execute(self.plan, confirmed=True)

        self.assertIsNone(result.backup_path)
        self.assertEqual(
            validation_calls,
            [
                (
                    (
                        "mkvmerge",
                        "--identify",
                        "--identification-format",
                        "json",
                        str(self.path),
                    ),
                    {"check": True, "capture_output": True, "text": True},
                )
            ],
        )

    def test_retains_backup_only_when_explicitly_requested(self):
        result = MkvRepairExecutor(
            runner=lambda *args, **kwargs: None,
            validator=lambda plan: None,
        ).execute(self.plan, confirmed=True, keep_backup=True)

        self.assertEqual(result.backup_path.read_bytes(), b"original media")

    def test_restores_original_when_validation_fails(self):
        def editor(command, **kwargs):
            self.path.write_bytes(b"modified media")

        def validator(plan):
            raise ValueError("metadata mismatch")

        with self.assertRaisesRegex(ValueError, "metadata mismatch"):
            MkvRepairExecutor(runner=editor, validator=validator).execute(
                self.plan, confirmed=True
            )

        self.assertEqual(self.path.read_bytes(), b"original media")
        self.assertFalse(
            self.path.with_name("movie.mkv.mediasanitizer.bak").exists()
        )

    def test_restores_original_when_mocked_editor_modifies_then_fails(self):
        def failing_editor(command, **kwargs):
            self.path.write_bytes(b"partially modified media")
            raise subprocess.CalledProcessError(2, command)

        with self.assertRaises(subprocess.CalledProcessError):
            MkvRepairExecutor(runner=failing_editor).execute(
                self.plan, confirmed=True
            )

        self.assertEqual(self.path.read_bytes(), b"original media")
        self.assertFalse(
            self.path.with_name("movie.mkv.mediasanitizer.bak").exists()
        )

    def test_refuses_to_overwrite_an_existing_backup(self):
        backup = self.path.with_name("movie.mkv.mediasanitizer.bak")
        backup.write_bytes(b"previous backup")

        with self.assertRaisesRegex(FileExistsError, "existing backup"):
            MkvRepairExecutor(runner=lambda *args, **kwargs: None).execute(
                self.plan, confirmed=True
            )

        self.assertEqual(backup.read_bytes(), b"previous backup")

    def test_reports_rollback_failure_and_leaves_backup_available(self):
        def failing_editor(command, **kwargs):
            raise subprocess.CalledProcessError(2, command)

        with mock.patch(
            "media_sanitizer.repair.os.replace", side_effect=OSError("locked")
        ):
            with self.assertRaisesRegex(RepairRollbackError, "backup remains"):
                MkvRepairExecutor(runner=failing_editor).execute(
                    self.plan, confirmed=True
                )

        self.assertEqual(
            self.path.with_name("movie.mkv.mediasanitizer.bak").read_bytes(),
            b"original media",
        )


if __name__ == "__main__":
    unittest.main()
