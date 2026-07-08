import argparse

from media_sanitizer.commands.inspect import run_inspect
from media_sanitizer.commands.repair import run_repair


def main():
    parser = argparse.ArgumentParser(
        prog="mediasanitizer",
        description="Audit and repair media libraries safely.",
    )

    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect a media file or directory",
    )

    inspect_parser.add_argument(
        "path",
        help="Path to a media file or directory",
    )

    inspect_parser.add_argument(
        "--details",
        action="store_true",
        help="Print a detailed report for every file",
    )

    repair_parser = subparsers.add_parser(
        "repair",
        help="Preview or execute media repairs",
    )

    repair_parser.add_argument(
        "path",
        help="Path to a media file or directory",
    )

    repair_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview repairs without modifying files",
    )

    args = parser.parse_args()

    if args.command == "inspect":
        run_inspect(args)

    elif args.command == "repair":
        run_repair(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()