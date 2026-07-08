from media_sanitizer.display import display_media
from media_sanitizer.models import Issue, MediaFile
from media_sanitizer.repairs.models import RepairAction
from media_sanitizer.summary import ISSUE_TITLES, ScanSummary
from media_sanitizer.utils import language_name


def print_report(media: MediaFile, issues: list[Issue]):
    print(f"\n{media.path}")
    print("=" * len(media.path))

    print(f"\nVideo Tracks ({len(media.video_tracks())})")
    for track in media.video_tracks():
        line = f"  ID {track.id}"

        if track.name:
            line += f" | Name: {track.name}"

        print(line)

    print(f"\nAudio Tracks ({len(media.audio_tracks())})")
    for track in media.audio_tracks():
        line = (
            f"  ID {track.id} | "
            f"Language: {language_name(track.language)} | "
            f"Default: {'Yes' if track.default else 'No'}"
        )

        if track.name:
            line += f" | Name: {track.name}"

        print(line)

    print(f"\nSubtitle Tracks ({len(media.subtitle_tracks())})")
    for track in media.subtitle_tracks():
        line = (
            f"  ID {track.id} | "
            f"Language: {language_name(track.language)} | "
            f"Default: {'Yes' if track.default else 'No'}"
        )

        if track.name:
            line += f" | Name: {track.name}"

        print(line)

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  - [{issue.title}] {issue.message}")
    else:
        print("\n✓ No issues found.")


def print_summary(summary: ScanSummary):
    print("\nScan Summary")
    print("============")
    print(f"Files scanned: {summary.files_scanned}")
    print(f"Healthy files: {summary.healthy_files}")
    print(f"Files with issues: {summary.files_with_issues}")

    if summary.issue_counts:
        print("\nIssue Summary")
        print("-------------")

        titles = [
            ISSUE_TITLES.get(code, code)
            for code in summary.issue_counts
        ]

        width = max(len(title) for title in titles)

        for code, count in sorted(summary.issue_counts.items()):
            title = ISSUE_TITLES.get(code, code)
            print(f"{title:.<{width + 6}}{count}")
    else:
        print("\nNo issues found. 🎉")


def print_repair_preview(
    media_path: str,
    actions: list[RepairAction],
):
    media = display_media(media_path)

    print(f"\n{media.title}")

    for action in actions:
        print(f"    {action.summary}")