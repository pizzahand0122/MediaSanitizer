from media_sanitizer.models import Issue, MediaFile


def default_audio_issues(media: MediaFile) -> list[Issue]:
    defaults = [track for track in media.audio_tracks() if track.default]

    if len(defaults) == 0:
        return [
            Issue(
                code="DEFAULT_AUDIO",
                title="Default Audio",
                message="No default audio track.",
            )
        ]

    if len(defaults) > 1:
        ids = ", ".join(str(track.id) for track in defaults)
        return [
            Issue(
                code="DEFAULT_AUDIO",
                title="Default Audio",
                message=f"Multiple default audio tracks (IDs: {ids}).",
            )
        ]

    default = defaults[0]

    if default.language != "eng" and media.has_english_audio():
        return [
            Issue(
                code="DEFAULT_AUDIO",
                title="Default Audio",
                message=(
                    f'Default audio is "{default.language}" '
                    "but English audio is available."
                ),
            )
        ]

    return []


def commentary_issues(media: MediaFile) -> list[Issue]:
    issues = []

    for track in media.audio_tracks():
        if track.name and "commentary" in track.name.lower():
            issues.append(
                Issue(
                    code="COMMENTARY",
                    title="Commentary",
                    message=f"Commentary audio track detected (Track ID {track.id}).",
                )
            )

    return issues


def run_audio_audits(media: MediaFile) -> list[Issue]:
    issues = []

    issues.extend(default_audio_issues(media))
    issues.extend(commentary_issues(media))

    return issues