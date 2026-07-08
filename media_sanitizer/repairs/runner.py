from media_sanitizer.models import MediaFile
from media_sanitizer.repairs.models import RepairAction
from media_sanitizer.utils import language_name


def build_repair_plan(
    media: MediaFile,
    issues,
) -> list[RepairAction]:
    actions = []

    for issue in issues:
        match issue.code:
            case "DEFAULT_AUDIO":
                audio_tracks = media.audio_tracks()

                if not audio_tracks:
                    continue

                track = audio_tracks[0]
                language = language_name(track.language)

                actions.append(
                    RepairAction(
                        title=f"Make {language} the default audio",
                        summary=f"Audio: None → {language}",
                        command=[
                            "mkvpropedit",
                            media.path,
                            "--edit",
                            f"track:{track.id + 1}",
                            "--set",
                            "flag-default=1",
                        ],
                    )
                )

            case "DEFAULT_SUBTITLE":
                subtitle_tracks = media.subtitle_tracks()

                english = next(
                    (
                        track
                        for track in subtitle_tracks
                        if track.language == "eng"
                    ),
                    None,
                )

                if english is None:
                    continue

                language = language_name(english.language)

                actions.append(
                    RepairAction(
                        title=f"Make {language} the default subtitle",
                        summary=f"Subtitle: None → {language}",
                        command=[
                            "mkvpropedit",
                            media.path,
                            "--edit",
                            f"track:{english.id + 1}",
                            "--set",
                            "flag-default=1",
                        ],
                    )
                )

    return actions