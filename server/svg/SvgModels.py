from dataclasses import dataclass

@dataclass
class SvgLineSegment:
    start: tuple[float, float]
    end: tuple[float, float]

@dataclass(frozen=True)
class SvgCircle:
    cx: float
    cy: float

@dataclass
class SvgRectangle:
    x: float
    y: float
    width: float
    height: float

@dataclass
class SvgRgbMatch: # positive = must be higher, negative = must be lower
    r: int
    g: int
    b: int

@dataclass
class SvgMetaData:
    width: str
    height: str
    viewBox: str

@dataclass
class SvgText:
    text: str
    x: float
    y: float
