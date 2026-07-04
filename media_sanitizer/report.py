from media_sanitizer.models import MediaFile


def print_report(media: MediaFile, issues: list[str]):
    print(f"\n{media.path}")
    print("=" * len(media.path))

    print(f"\nVideo Tracks ({len(media.video_tracks())})")
    for track in media.video_tracks():
        print(f"  ID {track.id}")

    print(f"\nAudio Tracks ({len(media.audio_tracks())})")
    for track in media.audio_tracks():
        print(
            f"  ID {track.id} | "
            f"Language: {track.language} | "
            f"Default: {track.default}"
        )

    print(f"\nSubtitle Tracks ({len(media.subtitle_tracks())})")
    for track in media.subtitle_tracks():
        print(
            f"  ID {track.id} | "
            f"Language: {track.language} | "
            f"Default: {track.default}"
        )

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ No issues found.")
