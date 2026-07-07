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