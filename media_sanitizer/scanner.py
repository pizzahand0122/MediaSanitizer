from pathlib import Path

MEDIA_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
    ".m4v",
    ".mov",
}


def scan(path: str) -> list[Path]:
    """Return a list of media files found under a directory."""
    root = Path(path)

    return [
        file
        for file in root.rglob("*")
        if file.is_file() and file.suffix.lower() in MEDIA_EXTENSIONS
    ]