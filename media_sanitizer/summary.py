from collections import Counter
from dataclasses import dataclass, field

from media_sanitizer.models import Issue


@dataclass
class ScanSummary:
    files_scanned: int = 0
    healthy_files: int = 0
    files_with_issues: int = 0

    issue_counts: Counter = field(default_factory=Counter)


def update_summary(summary: ScanSummary, issues: list[Issue]) -> None:
    summary.files_scanned += 1

    if issues:
        summary.files_with_issues += 1
    else:
        summary.healthy_files += 1

    for issue in issues:
        summary.issue_counts[issue.code] += 1