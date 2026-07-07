from media_sanitizer.models import Issue, MediaFile
from media_sanitizer.repairs.audio import repair_default_audio
from media_sanitizer.repairs.models import RepairAction


def build_repair_plan(
    media: MediaFile,
    issues: list[Issue],
) -> list[RepairAction]:
    actions = []

    print("\nDEBUG: Issues received:")
    for issue in issues:
        print(issue)

    for issue in issues:
        match issue.code:
            case "DEFAULT_AUDIO":
                print("DEBUG: Matched DEFAULT_AUDIO")
                actions.extend(repair_default_audio(media))

    print(f"DEBUG: Actions generated: {len(actions)}")

    return actions