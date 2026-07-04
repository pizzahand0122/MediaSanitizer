from media_sanitizer.models import MediaFile


def default_audio_issues(media: MediaFile) -> list[str]:
    defaults = [track for track in media.audio_tracks() if track.default]

    if len(defaults) == 0:
        return ["No default audio track."]

    if len(defaults) > 1:
        return ["Multiple default audio tracks."]

    return []
