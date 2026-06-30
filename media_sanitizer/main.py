import sys

from media_sanitizer.inspector import inspect


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <file>")
        return

    media = inspect(sys.argv[1])

    print(f"\n{media.path}\n")

    for track in media.tracks:
        print(
            f"{track.id:2} | "
            f"{track.type:9} | "
            f"{track.language:3} | "
            f"default={track.default}"
        )


if __name__ == "__main__":
    main()