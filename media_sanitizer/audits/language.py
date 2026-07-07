from media_sanitizer.models import MediaFile


def missing_english_audio_issues(media: MediaFile) -> list[str]:
    if not media.has_english_audio():
        return ["No English audio track found."]

    return []


def missing_english_subtitle_issues(media: MediaFile) -> list[str]:
    if media.subtitle_tracks() and not media.has_english_subtitles():
        return ["No English subtitle track found."]

    return []


def run_language_audits(media: MediaFile) -> list[str]:
    issues = []

    issues.extend(missing_english_audio_issues(media))
    issues.extend(missing_english_subtitle_issues(media))

    return issues