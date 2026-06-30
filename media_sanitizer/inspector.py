import json
import subprocess

from media_sanitizer.models import MediaFile, Track


def inspect(path: str) -> MediaFile:
    result = subprocess.run(
        ["mkvmerge", "-J", path],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    tracks = []

    for track in data["tracks"]:
        tracks.append(
            Track(
                id=track["id"],
                type=track["type"],
                language=track["properties"].get("language", "und"),
                default=track["properties"].get("default_track", False),
            )
        )

    return MediaFile(
        path=path,
        tracks=tracks,
    )