import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from media_sanitizer.main import main
from media_sanitizer.models import FileScanResult
from media_sanitizer.repair import RepairResult


class MainTests(unittest.TestCase):
    def test_reports_scan_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "movie.mp4").write_bytes(b"media data")
            (root / "notes.txt").touch()
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main([directory])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                output.getvalue(),
                "Total files: 1\n"
                "Clean files: 1\n"
                "Files with issues: 0\n",
            )

    def test_summary_counts_files_with_detected_issues(self):
        results = [
            FileScanResult(Path("clean.mp4")),
            FileScanResult(Path("issue.mkv"), ("problem",)),
        ]
        output = StringIO()

        with tempfile.TemporaryDirectory() as directory:
            with patch("media_sanitizer.main.scan_library", return_value=results):
                with redirect_stdout(output):
                    exit_code = main([directory])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue(),
            "Total files: 2\n"
            "Clean files: 1\n"
            "Files with issues: 1\n",
        )

    def test_default_scan_counts_empty_media_as_an_issue(self):
        output = StringIO()

        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "empty.mkv").touch()

            with redirect_stdout(output):
                exit_code = main([directory])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue(),
            "Total files: 1\n"
            "Clean files: 0\n"
            "Files with issues: 1\n",
        )

    def test_rejects_missing_directory_argument(self):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main([])

        self.assertEqual(exit_code, 2)
        self.assertEqual(
            output.getvalue(),
            "Usage: python -m media_sanitizer.main <directory>\n",
        )

    def test_rejects_extra_arguments(self):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(["first", "second"])

        self.assertEqual(exit_code, 2)

    def test_rejects_missing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main([str(missing)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(
                output.getvalue(),
                f"Error: not a directory: {missing}\n",
            )

    def test_rejects_file_path(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "movie.mp4"
            file.touch()
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main([str(file)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(
                output.getvalue(),
                f"Error: not a directory: {file}\n",
            )


class RepairCliTests(unittest.TestCase):
    class RecordingExecutor:
        executable = "mkvpropedit"

        def __init__(self):
            self.calls = []

        def execute(self, plan, *, confirmed=False, keep_backup=False):
            self.calls.append((plan, confirmed, keep_backup))
            return RepairResult(
                plan.path,
                (
                    plan.path.with_name(f"{plan.path.name}.mediasanitizer.bak")
                    if keep_backup
                    else None
                ),
                plan.command(),
            )

    def test_dry_run_prints_preview_without_prompting_or_executing(self):
        executor = self.RecordingExecutor()
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "repair",
                    "My Movie.mkv",
                    "42",
                    "--default",
                    "true",
                    "--name",
                    "Main Audio",
                    "--language",
                    "en-US",
                    "--dry-run",
                ],
                input_fn=lambda: self.fail("dry run must not prompt"),
                repair_executor=executor,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(executor.calls, [])
        self.assertIn("Repair plan (metadata only):\n", output.getvalue())
        self.assertIn("'My Movie.mkv'", output.getvalue())
        self.assertIn("--set flag-default=1", output.getvalue())
        self.assertIn("--set 'name=Main Audio'", output.getvalue())
        self.assertIn("--set language-ietf=en-US", output.getvalue())
        self.assertTrue(output.getvalue().endswith("Dry run: no changes made.\n"))

    def test_requires_full_yes_after_showing_preview(self):
        executor = self.RecordingExecutor()
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                ["repair", "movie.mkv", "7", "--default", "false"],
                input_fn=lambda: "y",
                repair_executor=executor,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(executor.calls, [])
        self.assertLess(
            output.getvalue().index("mkvpropedit"),
            output.getvalue().index("Type 'yes'"),
        )
        self.assertTrue(output.getvalue().endswith("Repair cancelled.\n"))

    def test_explicit_yes_executes_confirmed_plan(self):
        executor = self.RecordingExecutor()
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                ["repair", "movie.mkv", "7", "--name", "Commentary"],
                input_fn=lambda: " YES ",
                repair_executor=executor,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(executor.calls), 1)
        plan, confirmed, keep_backup = executor.calls[0]
        self.assertTrue(confirmed)
        self.assertFalse(keep_backup)
        self.assertEqual(plan.changes[0].name, "Commentary")
        self.assertIn("Repair applied and validated.", output.getvalue())

    def test_keep_backup_is_an_explicit_option(self):
        executor = self.RecordingExecutor()
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "repair",
                    "movie.mkv",
                    "7",
                    "--name",
                    "Commentary",
                    "--keep-backup",
                ],
                input_fn=lambda: "yes",
                repair_executor=executor,
            )

        self.assertEqual(exit_code, 0)
        self.assertTrue(executor.calls[0][2])
        self.assertIn("Backup retained at:", output.getvalue())

    def test_rejects_repair_without_a_metadata_change(self):
        executor = self.RecordingExecutor()
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                ["repair", "movie.mkv", "7", "--dry-run"],
                repair_executor=executor,
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("at least one property", output.getvalue())
        self.assertEqual(executor.calls, [])


if __name__ == "__main__":
    unittest.main()
