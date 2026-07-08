import subprocess

from media_sanitizer.repairs.models import RepairAction


def execute(actions: list[RepairAction]) -> tuple[int, int]:
    successful = 0
    failed = 0

    for action in actions:
        result = subprocess.run(
            action.command,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            successful += 1
        else:
            failed += 1

    return successful, failed