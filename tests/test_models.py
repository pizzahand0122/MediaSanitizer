import unittest
from pathlib import Path

from media_sanitizer.models import FileScanResult, ScanSummary


class FileScanResultTests(unittest.TestCase):
    def test_file_without_issues_is_clean(self):
        result = FileScanResult(Path("movie.mp4"))

        self.assertTrue(result.is_clean)

    def test_file_with_issues_is_not_clean(self):
        result = FileScanResult(Path("movie.mp4"), ("missing title",))

        self.assertFalse(result.is_clean)


class ScanSummaryTests(unittest.TestCase):
    def test_counts_clean_files_and_files_with_issues(self):
        results = (
            FileScanResult(Path("clean.mp4")),
            FileScanResult(Path("one-issue.mkv"), ("missing title",)),
            FileScanResult(
                Path("several-issues.mov"),
                ("missing title", "unexpected metadata"),
            ),
        )

        self.assertEqual(
            ScanSummary.from_results(results),
            ScanSummary(total_files=3, clean_files=1, files_with_issues=2),
        )

    def test_empty_results_produce_zero_counts(self):
        self.assertEqual(
            ScanSummary.from_results([]),
            ScanSummary(total_files=0, clean_files=0, files_with_issues=0),
        )

    def test_accepts_a_single_pass_iterable(self):
        results = (
            result
            for result in (
                FileScanResult(Path("clean.mp4")),
                FileScanResult(Path("issue.mp4"), ("issue",)),
            )
        )

        self.assertEqual(ScanSummary.from_results(results).total_files, 2)

    def test_rejects_inconsistent_counts(self):
        with self.assertRaisesRegex(ValueError, "must equal total files"):
            ScanSummary(total_files=3, clean_files=1, files_with_issues=1)

    def test_rejects_negative_counts(self):
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            ScanSummary(total_files=-1, clean_files=0, files_with_issues=-1)


if __name__ == "__main__":
    unittest.main()
