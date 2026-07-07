import json
import subprocess

from media_sanitizer.models import (
    AudioTrack,
    MediaFile,
    SubtitleTrack,
    VideoTrack,
)


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
        properties = track["properties"]

        if track["type"] == "video":
            tracks.append(
                VideoTrack(
                    id=track["id"],
                    language=properties.get("language", "und"),
                    default=properties.get("default_track", False),
                    name=properties.get("track_name"),
                )
            )

        elif track["type"] == "audio":
            tracks.append(
                AudioTrack(
                    id=track["id"],
                    language=properties.get("language", "und"),
                    default=properties.get("default_track", False),
                    name=properties.get("track_name"),
                )
            )

        elif track["type"] == "subtitles":
            tracks.append(
                SubtitleTrack(
                    id=track["id"],
                    language=properties.get("language", "und"),
                    default=properties.get("default_track", False),
                    name=properties.get("track_name"),
                )
            )

    return MediaFile(
        path=path,
        tracks=tracks,
    )