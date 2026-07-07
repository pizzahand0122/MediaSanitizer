import argparse

from media_sanitizer.audits.audio import run_audio_audits
from media_sanitizer.audits.language import run_language_audits
from media_sanitizer.audits.subtitles import run_subtitle_audits
from media_sanitizer.audits.summary import run_summary_audits
from media_sanitizer.inspector import inspect
from media_sanitizer.report import print_report
from media_sanitizer.scanner import scan


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
        for file in scan(args.path):
            media = inspect(str(file))

            issues = []

            issues.extend(run_audio_audits(media))
            issues.extend(run_subtitle_audits(media))
            issues.extend(run_language_audits(media))
            issues.extend(run_summary_audits(media))

            print_report(media, issues)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()