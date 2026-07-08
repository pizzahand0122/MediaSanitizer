from dataclasses import dataclass


@dataclass
class RepairAction:
    title: str
    summary: str
    command: list[str]