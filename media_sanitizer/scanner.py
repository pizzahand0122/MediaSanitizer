from pathlib import Path

MEDIA_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
    ".m4v",
    ".mov",
}


def scan(path: str):
    root = Path(path)

    media = []

    for file in root.rglob("*"):
        if file.is_file() and file.suffix.lower() in MEDIA_EXTENSIONS:
            media.append(file)

    return sorted(media)