from dataclasses import dataclass

from media_sanitizer.models import Issue


@dataclass
class ScanSummary:
    files_scanned: int = 0
    healthy_files: int = 0
    files_with_issues: int = 0

    default_audio_issues: int = 0
    default_subtitle_issues: int = 0
    english_audio_issues: int = 0
    english_subtitle_issues: int = 0
    commentary_tracks: int = 0


def update_summary(summary: ScanSummary, issues: list[Issue]) -> None:
    summary.files_scanned += 1

    if issues:
        summary.files_with_issues += 1
    else:
        summary.healthy_files += 1

    for issue in issues:
        match issue.title:
            case "Default Audio":
                summary.default_audio_issues += 1

            case "Default Subtitle":
                summary.default_subtitle_issues += 1

            case "English Audio":
                summary.english_audio_issues += 1

            case "English Subtitles":
                summary.english_subtitle_issues += 1

            case "Commentary":
                summary.commentary_tracks += 1