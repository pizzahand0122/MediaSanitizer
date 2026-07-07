from media_sanitizer.models import MediaFile


def default_audio_issues(media: MediaFile) -> list[str]:
    defaults = [track for track in media.audio_tracks() if track.default]

    if len(defaults) == 0:
        return ["No default audio track."]

    if len(defaults) > 1:
        ids = ", ".join(str(track.id) for track in defaults)
        return [f"Multiple default audio tracks (IDs: {ids})."]

    default = defaults[0]

    if default.language != "eng" and media.has_english_audio():
        return [
            f'Default audio is "{default.language}" but English audio is available.'
        ]

    return []


def commentary_audio_issues(media: MediaFile) -> list[str]:
    issues = []

    for track in media.audio_tracks():
        if track.name and "commentary" in track.name.lower():
            issues.append(f'Commentary track detected (Track ID {track.id}).')

    return issues


def run_audio_audits(media: MediaFile) -> list[str]:
    issues = []

    issues.extend(default_audio_issues(media))
    issues.extend(commentary_audio_issues(media))

    return issues