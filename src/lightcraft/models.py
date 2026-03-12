from __future__ import annotations

from dataclasses import dataclass
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
    crop_rect: tuple[int, int, int, int] | None = None
    applied_preset_id: str | None = None


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
