from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(slots=True)
class EditState:
    exposure: float = 0.0
    contrast: float = 0.0
    white_balance_temp: float = 0.0
    saturation: float = 0.0
    sharpening: float = 0.0
    denoise: float = 0.0
    shadows: float = 0.0
    rotation_deg: float = 0.0
    crop_left_pct: float = 0.0
    crop_top_pct: float = 0.0
    crop_right_pct: float = 0.0
    crop_bottom_pct: float = 0.0
    applied_preset_id: str | None = None

    def clone(self) -> "EditState":
        return replace(self)


@dataclass(slots=True)
class ImageMetadata:
    path: Path
    width: int
    height: int
    channels: int
    file_size_bytes: int

    @property
    def filename(self) -> str:
        return self.path.name
