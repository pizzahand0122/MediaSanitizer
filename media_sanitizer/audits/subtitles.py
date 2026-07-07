from media_sanitizer.models import Issue, MediaFile


def default_subtitle_issues(media: MediaFile) -> list[Issue]:
    defaults = [track for track in media.subtitle_tracks() if track.default]

    if len(defaults) == 0 and len(media.subtitle_tracks()) > 0:
        return [
            Issue(
                title="Default Subtitle",
                message="No default subtitle track.",
            )
        ]

    if len(defaults) > 1:
        ids = ", ".join(str(track.id) for track in defaults)
        return [
            Issue(
                title="Default Subtitle",
                message=f"Multiple default subtitle tracks (IDs: {ids}).",
            )
        ]

    return []


def run_subtitle_audits(media: MediaFile) -> list[Issue]:
    issues = []

    issues.extend(default_subtitle_issues(media))

    return issues