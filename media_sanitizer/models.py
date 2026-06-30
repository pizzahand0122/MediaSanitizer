from dataclasses import dataclass


@dataclass
class Track:
    id: int
    type: str
    language: str
    default: bool


@dataclass
class MediaFile:
    path: str
    tracks: list[Track]