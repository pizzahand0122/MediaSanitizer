import json
import subprocess


def inspect(path: str) -> dict:
    """Return mkvmerge metadata for a media file."""

    result = subprocess.run(
        ["mkvmerge", "-J", path],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)