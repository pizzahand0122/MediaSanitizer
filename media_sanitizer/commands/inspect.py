from media_sanitizer.output import print_summary
from media_sanitizer.pipeline import inspect_library
from media_sanitizer.report import print_report
from media_sanitizer.summary import ScanSummary, update_summary


def run_inspect(args):
    summary = ScanSummary()

    for media, issues in inspect_library(args.path):
        update_summary(summary, issues)

        if args.details:
            print_report(media, issues)

    print_summary(summary)