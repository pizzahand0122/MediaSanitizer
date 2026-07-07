from media_sanitizer.models import Issue, MediaFile


def missing_english_audio_issues(media: MediaFile) -> list[Issue]:
    if not media.has_english_audio():
        return [
            Issue(
                code="ENGLISH_AUDIO",
                title="English Audio",
                message="No English audio track found.",
            )
        ]

    return []


def missing_english_subtitle_issues(media: MediaFile) -> list[Issue]:
    if media.subtitle_tracks() and not media.has_english_subtitles():
        return [
            Issue(
                code="ENGLISH_SUBTITLE",
                title="English Subtitle",
                message="No English subtitle track found.",
            )
        ]

    return []


def run_language_audits(media: MediaFile) -> list[Issue]:
    issues = []

    issues.extend(missing_english_audio_issues(media))
    issues.extend(missing_english_subtitle_issues(media))

    return issues