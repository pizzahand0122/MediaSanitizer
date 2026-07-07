from dataclasses import dataclass


@dataclass
class RepairAction:
    title: str
    command: list[str]