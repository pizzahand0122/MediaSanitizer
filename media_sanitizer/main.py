import sys

from media_sanitizer.scanner import scan


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <directory>")
        return

    files = scan(sys.argv[1])

    print(f"Found {len(files)} media files.")


if __name__ == "__main__":
    main()