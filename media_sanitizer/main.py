import sys

from media_sanitizer.inspector import inspect
from media_sanitizer.report import print_report


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <file>")
        return

    media = inspect(sys.argv[1])
    print_report(media)


if __name__ == "__main__":
    main()