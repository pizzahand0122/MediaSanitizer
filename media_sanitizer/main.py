import argparse

from media_sanitizer.audits.audio import run_audio_audits
from media_sanitizer.inspector import inspect
from media_sanitizer.report import print_report


def main():
    parser = argparse.ArgumentParser(
        prog="mediasanitizer",
        description="Audit and repair media libraries safely."
    )

    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect a single media file"
    )
    inspect_parser.add_argument(
        "file",
        help="Path to the media file"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        media = inspect(args.file)
        print_report(media)

        issues = run_audio_audits(media)

        if issues:
            print("\nIssues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ No default audio issues found.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
