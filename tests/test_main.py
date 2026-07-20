import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from media_sanitizer.main import main
from media_sanitizer.models import FileScanResult


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


if __name__ == "__main__":
    unittest.main()
