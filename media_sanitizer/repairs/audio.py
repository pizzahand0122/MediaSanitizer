from media_sanitizer.models import MediaFile
from media_sanitizer.repairs.models import RepairAction


def repair_default_audio(media: MediaFile) -> list[RepairAction]:
    default = media.default_audio()

    if default is not None:
        return []

    english_tracks = [
        track for track in media.audio_tracks()
        if track.language == "eng"
    ]

    if not english_tracks:
        return []

    track = english_tracks[0]

    return [
        RepairAction(
            title="Set default audio track",
            command=[
                "mkvpropedit",
                media.path,
                "--edit",
                f"track:{track.id + 1}",
                "--set",
                "flag-default=1",
            ],
        )
    ]