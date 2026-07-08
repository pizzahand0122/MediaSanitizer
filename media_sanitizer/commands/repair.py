from media_sanitizer.output import (
    print_repair_preview,
    print_summary,
)
from media_sanitizer.pipeline import inspect_library
from media_sanitizer.repairs.runner import build_repair_plan
from media_sanitizer.summary import ScanSummary, update_summary


def run_repair(args):
    summary = ScanSummary()

    if args.dry_run:
        print("\nRepair Preview")
        print("==============")
    else:
        print("\nRepair")
        print("======")

    for media, issues in inspect_library(args.path):
        update_summary(summary, issues)

        actions = build_repair_plan(media, issues)

        if not actions:
            continue

        print_repair_preview(media.path, actions)

    print_summary(summary)