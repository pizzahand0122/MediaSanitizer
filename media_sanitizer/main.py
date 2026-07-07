import argparse

from media_sanitizer.commands.inspect import run_inspect


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

    inspect_parser.add_argument(
        "--repair-plan",
        action="store_true",
        help="Show possible repairs",
    )

    args = parser.parse_args()

    if args.command == "inspect":
        run_inspect(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()