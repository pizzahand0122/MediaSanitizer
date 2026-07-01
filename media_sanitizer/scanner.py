from pathlib import Path


MEDIA_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
}


def scan(path: str):
    for file in Path(path).rglob("*"):
        if file.suffix.lower() in MEDIA_EXTENSIONS:
            yield file