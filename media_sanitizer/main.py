import argparse

from media_sanitizer.audits.audio import run_audio_audits
from media_sanitizer.audits.language import run_language_audits
from media_sanitizer.audits.subtitles import run_subtitle_audits
from media_sanitizer.audits.summary import run_summary_audits
from media_sanitizer.inspector import inspect
from media_sanitizer.report import print_report
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

            print_report(media, issues)

        print("\nScan Summary")
        print("============")
        print(f"Files scanned: {summary.files_scanned}")
        print(f"Healthy files: {summary.healthy_files}")
        print(f"Files with issues: {summary.files_with_issues}")
        print()
        print(f"Default audio issues: {summary.default_audio_issues}")
        print(f"Default subtitle issues: {summary.default_subtitle_issues}")
        print(f"English audio issues: {summary.english_audio_issues}")
        print(f"English subtitle issues: {summary.english_subtitle_issues}")
        print(f"Commentary tracks: {summary.commentary_tracks}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()