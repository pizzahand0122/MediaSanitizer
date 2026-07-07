from media_sanitizer.models import Issue, MediaFile


def run_summary_audits(media: MediaFile) -> list[Issue]:
    return []