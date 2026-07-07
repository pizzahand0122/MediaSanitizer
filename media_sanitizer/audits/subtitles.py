from media_sanitizer.models import MediaFile


def default_subtitle_issues(media: MediaFile) -> list[str]:
    defaults = [track for track in media.subtitle_tracks() if track.default]

    if len(defaults) == 0 and len(media.subtitle_tracks()) > 0:
        return ["No default subtitle track."]

    if len(defaults) > 1:
        ids = ", ".join(str(track.id) for track in defaults)
        return [f"Multiple default subtitle tracks (IDs: {ids})."]

    return []


def run_subtitle_audits(media: MediaFile) -> list[str]:
    issues = []

    issues.extend(default_subtitle_issues(media))

    return issues