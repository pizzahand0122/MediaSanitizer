import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from media_sanitizer.models import FileScanResult
from media_sanitizer.scanner import detect_file_issues, scan, scan_library


class ScanTests(unittest.TestCase):
    def test_finds_supported_media_files_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = {
                root / "movie.mp4",
                root / "nested" / "episode.MKV",
            }

            for file in expected:
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch()

            (root / "notes.txt").touch()
            (root / "video.mp4.backup").touch()

            self.assertEqual(set(scan(directory)), expected)

    def test_returns_empty_list_when_no_media_files_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes.txt").touch()

            self.assertEqual(scan(directory), [])

    def test_returns_empty_list_for_missing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"

            self.assertEqual(scan(str(missing)), [])

    def test_returns_files_in_path_order_and_accepts_path_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = [root / "zeta.mp4", root / "alpha.mkv"]

            for file in files:
                file.touch()

            self.assertEqual(scan(root), sorted(files))


class ScanLibraryTests(unittest.TestCase):
    def test_inspects_each_media_file_found_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clean = root / "clean.mp4"
            issue = root / "nested" / "issue.mkv"
            issue.parent.mkdir()
            clean.touch()
            issue.touch()
            inspected = []

            def detect_issues(path):
                inspected.append(path)
                return ("problem",) if path == issue else ()

            results = scan_library(root, detect_issues)

            self.assertEqual(inspected, sorted([clean, issue]))
            self.assertEqual(
                results,
                [
                    FileScanResult(clean),
                    FileScanResult(issue, ("problem",)),
                ],
            )

    def test_default_detector_marks_nonempty_files_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "movie.mp4"
            file.write_bytes(b"media data")

            self.assertEqual(scan_library(directory), [FileScanResult(file)])

    def test_default_detector_reports_empty_files(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "empty.mp4"
            file.touch()

            self.assertEqual(
                scan_library(directory),
                [FileScanResult(file, ("file is empty",))],
            )


class DetectFileIssuesTests(unittest.TestCase):
    def test_reports_stat_errors_as_file_issues(self):
        file = Path("unreadable.mp4")

        with patch.object(Path, "stat", side_effect=OSError("access denied")):
            issues = detect_file_issues(file)

        self.assertEqual(issues, ("cannot inspect file: access denied",))


if __name__ == "__main__":
    unittest.main()
