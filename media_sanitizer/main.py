import sys

from media_sanitizer.scanner import scan


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <directory>")
        return

    files = scan(sys.argv[1])

    print(f"\nFound {len(files):,} media files.\n")

    for file in files[:10]:
        print(file)

    if len(files) > 10:
        print(f"\n...and {len(files) - 10:,} more.")


if __name__ == "__main__":
    main()