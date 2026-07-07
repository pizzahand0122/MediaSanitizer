from pathlib import Path


MEDIA_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
}


def scan(path: str):
    path = Path(path)

    if path.is_file():
        if path.suffix.lower() in MEDIA_EXTENSIONS:
            yield path
        return

    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() in MEDIA_EXTENSIONS:
            yield file