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

    def video_tracks(self):
        return [t for t in self.tracks if isinstance(t, VideoTrack)]

    def audio_tracks(self):
        return [t for t in self.tracks if isinstance(t, AudioTrack)]

    def subtitle_tracks(self):
        return [t for t in self.tracks if isinstance(t, SubtitleTrack)]

    def default_audio(self):
        for track in self.audio_tracks():
            if track.default:
                return track

        return None      

    def has_english_audio(self):
        return any(
            track.language == "eng"
            for track in self.audio_tracks()
        )