from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class FilterValue:
    id: int
    title: str
    order: int
    checked: bool


class FilterOrientation(Enum):
    FILTER = 0
    LINE = 1
    COLUMN = 2
    GROUP = 3


@dataclass
class FilterField:
    id: int
    # order: int
    title: str
    orientation: FilterOrientation
    values: List[FilterValue]
