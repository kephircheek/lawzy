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
class InPlace(Style):
    start: int
    end: int
