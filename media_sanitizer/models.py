from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileScanResult:
    """The outcome of scanning one media file."""

    path: Path
    issues: tuple[str, ...] = ()

    @property
    def is_clean(self) -> bool:
        """Return whether the file has no reported issues."""
        return not self.issues


@dataclass(frozen=True)
class ScanSummary:
    """Aggregate counts for a completed library scan."""

    total_files: int
    clean_files: int
    files_with_issues: int

    def __post_init__(self) -> None:
        counts = (self.total_files, self.clean_files, self.files_with_issues)
        if any(count < 0 for count in counts):
            raise ValueError("scan summary counts cannot be negative")
        if self.clean_files + self.files_with_issues != self.total_files:
            raise ValueError(
                "clean files and files with issues must equal total files"
            )

    @classmethod
    def from_results(cls, results: Iterable[FileScanResult]) -> "ScanSummary":
        """Build a summary while consuming scan results only once."""
        total_files = 0
        clean_files = 0

        for result in results:
            total_files += 1
            clean_files += result.is_clean

        return cls(
            total_files=total_files,
            clean_files=clean_files,
            files_with_issues=total_files - clean_files,
        )
