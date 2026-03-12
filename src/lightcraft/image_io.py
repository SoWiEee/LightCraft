from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .models import ImageMetadata


class ImageLoadError(RuntimeError):
    """Raised when an image cannot be loaded or decoded."""


SUPPORTED_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp);;All Files (*)"


def load_image(path: str | Path) -> tuple[np.ndarray, ImageMetadata]:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise ImageLoadError(f"File does not exist: {file_path}")
    if not file_path.is_file():
        raise ImageLoadError(f"Path is not a file: {file_path}")

    raw = np.fromfile(file_path, dtype=np.uint8)
    if raw.size == 0:
        raise ImageLoadError(f"File is empty or unreadable: {file_path}")

    image = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if image is None or image.size == 0:
        raise ImageLoadError(f"OpenCV failed to decode image: {file_path}")

    # Normalize to 8-bit BGR or BGRA for UI display in this phase.
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        # keep BGRA as-is
        pass
    elif image.ndim == 3 and image.shape[2] == 3:
        pass
    else:
        raise ImageLoadError(f"Unsupported channel layout: shape={image.shape}")

    metadata = ImageMetadata(
        path=file_path,
        width=int(image.shape[1]),
        height=int(image.shape[0]),
        channels=int(image.shape[2]) if image.ndim == 3 else 1,
        file_size_bytes=file_path.stat().st_size,
    )
    return image, metadata
