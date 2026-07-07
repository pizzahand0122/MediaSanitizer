from media_sanitizer.output import print_summary
from media_sanitizer.pipeline import inspect_library
from media_sanitizer.report import print_report
from media_sanitizer.repairs.runner import build_repair_plan
from media_sanitizer.summary import ScanSummary, update_summary


def run_inspect(args):
    summary = ScanSummary()

    for media, issues in inspect_library(args.path):
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

    print_summary(summary)