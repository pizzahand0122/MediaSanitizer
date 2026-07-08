from media_sanitizer.display import display_media
from media_sanitizer.repairs.models import RepairAction
from media_sanitizer.summary import ISSUE_TITLES, ScanSummary


def print_summary(summary: ScanSummary):
    print("\nScan Summary")
    print("============")
    print(f"Files scanned: {summary.files_scanned}")
    print(f"Healthy files: {summary.healthy_files}")
    print(f"Files with issues: {summary.files_with_issues}")

    if summary.issue_counts:
        print("\nIssue Summary")
        print("-------------")

        titles = [
            ISSUE_TITLES.get(code, code)
            for code in summary.issue_counts
        ]

        width = max(len(title) for title in titles)

        for code, count in sorted(summary.issue_counts.items()):
            title = ISSUE_TITLES.get(code, code)
            print(f"{title:.<{width + 6}}{count}")
    else:
        print("\nNo issues found. 🎉")


def print_repair_preview(
    media_path: str,
    actions: list[RepairAction],
):
    media = display_media(media_path)

    print(f"\n{media.title}")

    for action in actions:
        print(f"    {action.summary}")