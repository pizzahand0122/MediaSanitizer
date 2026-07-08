from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class DisplayMedia:
    library: str | None
    series: str | None
    season: str | None
    title: str


def display_media(path: str) -> DisplayMedia:
    p = Path(path)

    parts = p.parts

    library = None
    series = None
    season = None
    title = p.stem

    if "Shows" in parts:
        i = parts.index("Shows")
        library = "Shows"

        if len(parts) > i + 1:
            series = parts[i + 1]

        if len(parts) > i + 2:
            season = parts[i + 2]

        match = re.search(
            r"(S\d{2}E\d{2}\s*-\s*.+?)(?:\s*\(.*)?$",
            title,
        )

        if match:
            title = match.group(1)

    elif "Movies" in parts:
        i = parts.index("Movies")
        library = "Movies"

    return DisplayMedia(
        library=library,
        series=series,
        season=season,
        title=title,
    )