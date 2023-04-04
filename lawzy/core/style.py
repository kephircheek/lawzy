from dataclasses import dataclass
from enum import Enum
from typing import Union


class Stylist(Enum):
    REDUCER = "reducer"
    TAGSEARCHER = "tag_searcher"
    EXTRACTOR = "extractor"


class Color(Enum):
    GRAY = "#808080"


@dataclass(frozen=True)
class Style:
    stylist: Union[Stylist, None]


@dataclass(frozen=True)
class MarginTop(Style):
    lines: int


@dataclass(frozen=True)
class FirstParagraph(Style):
    pass


@dataclass(frozen=True)
class ParagraphIndent(Style):
    width: int


@dataclass(frozen=True)
class FinalNewline(Style):
    pass


@dataclass(frozen=True)
class Hide(Style):
    pass


@dataclass(frozen=True)
class InPlaceStyle(Style):
    start: int
    end: int


@dataclass(frozen=True)
class Highlight(InPlaceStyle):
    label: str = None
    color: str = "#FF0000"


@dataclass(frozen=True)
class Repetition(Style):
    label: int
    i: int
    n: int


@dataclass(frozen=True)
class Exclusive(Style):
    pass


@dataclass(frozen=True)
class FontColor(Style):
    color: str
