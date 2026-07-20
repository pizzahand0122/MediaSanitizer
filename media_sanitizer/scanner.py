from collections.abc import Callable
from pathlib import Path

from media_sanitizer.models import FileScanResult

MEDIA_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
    ".m4v",
    ".mov",
}


def scan(path: str | Path) -> list[Path]:
    """Return media files under a directory in deterministic path order."""
    root = Path(path)

    return sorted(
        file
        for file in root.rglob("*")
        if file.is_file() and file.suffix.lower() in MEDIA_EXTENSIONS
    )


IssueDetector = Callable[[Path], tuple[str, ...]]


def detect_file_issues(path: Path) -> tuple[str, ...]:
    """Return basic filesystem-level issues for a media file."""
    try:
        if path.stat().st_size == 0:
            return ("file is empty",)
    except OSError as error:
        return (f"cannot inspect file: {error}",)

    return ()


def scan_library(
    path: str | Path,
    detect_issues: IssueDetector | None = None,
) -> list[FileScanResult]:
    """Recursively scan a library and inspect every supported media file."""
    detector = detect_issues or detect_file_issues
    return [FileScanResult(file, detector(file)) for file in scan(path)]
