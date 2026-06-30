import sys

from media_sanitizer.inspector import inspect


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <file>")
        return

    media = inspect(sys.argv[1])

    print(f"Found {len(media.tracks)} tracks.\n")
    print(f"{media.path}\n")

    for track in media.tracks:
        print(type(track).__name__)


if __name__ == "__main__":
    main()