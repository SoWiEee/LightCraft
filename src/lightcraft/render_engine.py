from __future__ import annotations

import numpy as np

from .models import EditState


class RenderEngine:
    """Rebuild a preview image from source image + edit state.

    Phase 1 intentionally performs no visual adjustments yet.
    The contract already matches future phases so later adjustment steps
    can be added without changing the caller interface.
    """

    def render_preview(self, source_image: np.ndarray, edit_state: EditState) -> np.ndarray:
        _ = edit_state
        # Always rebuild from source to preserve non-destructive behavior.
        return source_image.copy()
