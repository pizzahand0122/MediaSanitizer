from dataclasses import dataclass


@dataclass
class Track:
    id: int
    language: str
    default: bool


@dataclass
class VideoTrack(Track):
    pass


@dataclass
class AudioTrack(Track):
    pass


@dataclass
class SubtitleTrack(Track):
    pass


@dataclass
class MediaFile:
    path: str
    tracks: list[Track]