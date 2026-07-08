from media_sanitizer.display import display_media
from media_sanitizer.output import (
    print_repair_preview,
    print_summary,
)
from media_sanitizer.pipeline import inspect_library
from media_sanitizer.repairs.runner import build_repair_plan
from media_sanitizer.summary import ScanSummary, update_summary


def run_repair(args):
    summary = ScanSummary()

    print("\nRepair Preview")
    print("==============")

    current_series = None
    current_season = None

    for media, issues in inspect_library(args.path):
        update_summary(summary, issues)

        actions = build_repair_plan(media, issues)

        if not actions:
            continue

        display = display_media(media.path)

        if display.series != current_series:
            current_series = display.series
            current_season = None

            if current_series:
                print(f"\n{current_series}")
                print("-" * len(current_series))

        if display.season != current_season:
            current_season = display.season

            if current_season:
                print(f"\n{current_season}")

        print_repair_preview(media.path, actions)

    print_summary(summary)