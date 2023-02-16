from dataclasses import dataclass


@dataclass(frozen=True)
class Style:
    pass


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
