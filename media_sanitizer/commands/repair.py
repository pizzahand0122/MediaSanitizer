from media_sanitizer.display import display_media
from media_sanitizer.output import (
    print_repair_preview,
    print_summary,
)
from media_sanitizer.pipeline import inspect_library
from media_sanitizer.repairs.executor import execute
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

    current_series = None
    current_season = None

    total_success = 0
    total_failed = 0
    total_actions = 0

    repair_plans = []

    for media, issues in inspect_library(args.path):
        update_summary(summary, issues)

        actions = build_repair_plan(media, issues)

        if not actions:
            continue

        repair_plans.append((media, actions))

        total_actions += len(actions)

        if args.dry_run:
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

    if not args.dry_run:
        print(f"\n{total_actions} repair(s) will be applied.")

        answer = input("Continue? [y/N]: ").strip().lower()

        if answer != "y":
            print("\nCancelled.")
            return

        print("\nApplying repairs...\n")

        for _, actions in repair_plans:
            successful, failed = execute(actions)
            total_success += successful
            total_failed += failed

        print("Finished.\n")
        print(f"Successful repairs: {total_success}")
        print(f"Failed repairs: {total_failed}")

    print_summary(summary)