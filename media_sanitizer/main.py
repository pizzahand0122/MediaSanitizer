import sys
from collections.abc import Sequence
from pathlib import Path

from media_sanitizer.models import ScanSummary
from media_sanitizer.scanner import scan_library


def main(argv: Sequence[str] | None = None) -> int:
    """Scan the requested directory and print a library health summary."""
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) != 1:
        print("Usage: python -m media_sanitizer.main <directory>")
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
