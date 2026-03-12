from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .image_io import load_image
from .models import EditState, ImageMetadata
from .render_engine import RenderEngine


@dataclass(slots=True)
class ImageDocument:
    render_engine: RenderEngine = field(default_factory=RenderEngine)
    source_image: np.ndarray | None = None
    preview_image: np.ndarray | None = None
    metadata: ImageMetadata | None = None
    edit_state: EditState = field(default_factory=EditState)

    def has_image(self) -> bool:
        return self.source_image is not None

    def open_image(self, path: str) -> None:
        image, metadata = load_image(path)
        # Immutable session source buffer by convention.
        self.source_image = image.copy()
        self.metadata = metadata
        self.edit_state = EditState()
        self.preview_image = self.render_engine.render_preview(self.source_image, self.edit_state)

    def rerender(self) -> None:
        if self.source_image is None:
            return
        self.preview_image = self.render_engine.render_preview(self.source_image, self.edit_state)

    def reset(self) -> None:
        if self.source_image is None:
            return
        self.edit_state = EditState()
        self.rerender()
