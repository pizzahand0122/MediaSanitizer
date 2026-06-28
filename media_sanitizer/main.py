import sys

from media_sanitizer.inspector import inspect


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m media_sanitizer.main <file>")
        return

    media = inspect(sys.argv[1])

    print(media["container"]["type"])

    for track in media["tracks"]:
        print(
            track["type"],
            track["properties"].get("language", "und"),
        )


if __name__ == "__main__":
    main()