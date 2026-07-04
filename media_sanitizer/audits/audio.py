from media_sanitizer.models import MediaFile


def default_audio_issues(media: MediaFile) -> list[str]:
    defaults = [track for track in media.audio_tracks() if track.default]

    if len(defaults) == 0:
        return ["No default audio track."]

    if len(defaults) > 1:
        ids = ", ".join(str(track.id) for track in defaults)
        return [f"Multiple default audio tracks (IDs: {ids})."]

    return []


def run_audio_audits(media: MediaFile) -> list[str]:
    issues = []

    issues.extend(default_audio_issues(media))

    return issues
