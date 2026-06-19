from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ScreenData:
    """
    Raw screenshot data captured from the desktop.
    Coordinates and dimensions here are in PHYSICAL pixels.
    """
    screenshot_bytes: bytes
    width: int
    height: int
    monitor_left: int = 0
    monitor_top: int = 0
    monitor_width: int = 0
    monitor_height: int = 0
    timestamp: float = 0.0


@dataclass(slots=True)
class Target:
    """
    Target UI element selected by the reasoning system.
    Coordinates are stored in PHYSICAL pixels.
    """
    bbox_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    label: str = ""
    confidence: float = 0.0

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    def contains_point(self, x: int, y: int) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2