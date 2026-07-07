from media_sanitizer.audits.audio import run_audio_audits
from media_sanitizer.audits.language import run_language_audits
from media_sanitizer.audits.subtitles import run_subtitle_audits
from media_sanitizer.audits.summary import run_summary_audits
from media_sanitizer.inspector import inspect
from media_sanitizer.scanner import scan
from media_sanitizer.summary import ScanSummary, update_summary


def inspect_library(path: str):
    summary = ScanSummary()

    for file in scan(path):
        media = inspect(str(file))

        issues = []

        issues.extend(run_audio_audits(media))
        issues.extend(run_subtitle_audits(media))
        issues.extend(run_language_audits(media))
        issues.extend(run_summary_audits(media))

        update_summary(summary, issues)

        yield media, issues

    return summary