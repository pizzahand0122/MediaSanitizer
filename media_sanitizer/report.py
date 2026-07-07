from media_sanitizer.models import Issue, MediaFile


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
            f"Language: {track.language} | "
            f"Default: {track.default}"
        )

        if track.name:
            line += f" | Name: {track.name}"

        print(line)

    print(f"\nSubtitle Tracks ({len(media.subtitle_tracks())})")
    for track in media.subtitle_tracks():
        line = (
            f"  ID {track.id} | "
            f"Language: {track.language} | "
            f"Default: {track.default}"
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