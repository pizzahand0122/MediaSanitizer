import argparse

from media_sanitizer.audits.audio import run_audio_audits
from media_sanitizer.audits.language import run_language_audits
from media_sanitizer.audits.subtitles import run_subtitle_audits
from media_sanitizer.audits.summary import run_summary_audits
from media_sanitizer.inspector import inspect
from media_sanitizer.report import print_report
from media_sanitizer.repairs.runner import build_repair_plan
from media_sanitizer.scanner import scan
from media_sanitizer.summary import ScanSummary, update_summary


def main():
    parser = argparse.ArgumentParser(
        prog="mediasanitizer",
        description="Audit and repair media libraries safely."
    )

    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect a media file or directory"
    )

    inspect_parser.add_argument(
        "path",
        help="Path to a media file or directory"
    )

    inspect_parser.add_argument(
        "--details",
        action="store_true",
        help="Print a detailed report for every file"
    )

    inspect_parser.add_argument(
        "--repair-plan",
        action="store_true",
        help="Show possible repairs"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        summary = ScanSummary()

        for file in scan(args.path):
            media = inspect(str(file))

            issues = []

            issues.extend(run_audio_audits(media))
            issues.extend(run_subtitle_audits(media))
            issues.extend(run_language_audits(media))
            issues.extend(run_summary_audits(media))

            update_summary(summary, issues)

            if args.details:
                print_report(media, issues)

            if args.repair_plan:
                actions = build_repair_plan(media, issues)

                if actions:
                    print(f"\nRepair Plan for {media.path}")

                    for action in actions:
                        print(f"  ✓ {action.title}")
                        print("    " + " ".join(action.command))

        print("\nScan Summary")
        print("============")
        print(f"Files scanned: {summary.files_scanned}")
        print(f"Healthy files: {summary.healthy_files}")
        print(f"Files with issues: {summary.files_with_issues}")

        if summary.issue_counts:
            print("\nIssue Summary")
            print("-------------")

            width = max(len(code) for code in summary.issue_counts)

            for code, count in sorted(summary.issue_counts.items()):
                print(f"{code:.<{width + 6}}{count}")

        else:
            print("\nNo issues found. 🎉")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()