from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .export_dialog import ExportOptions


class ExportError(RuntimeError):
    pass


class ExportService:
    def export_image(self, image: np.ndarray, target_path: str | Path, options: ExportOptions) -> Path:
        path = Path(target_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        image_to_save = image
        ext = path.suffix.lower()
        params: list[int] = []

        if options.format_name == "JPEG":
            ext = ".jpg"
            if image_to_save.ndim == 3 and image_to_save.shape[2] == 4:
                image_to_save = cv2.cvtColor(image_to_save, cv2.COLOR_BGRA2BGR)
            params = [cv2.IMWRITE_JPEG_QUALITY, int(options.jpeg_quality)]
        elif options.format_name == "PNG":
            ext = ".png"
            if not options.preserve_alpha and image_to_save.ndim == 3 and image_to_save.shape[2] == 4:
                image_to_save = cv2.cvtColor(image_to_save, cv2.COLOR_BGRA2BGR)
            params = [cv2.IMWRITE_PNG_COMPRESSION, int(options.png_compression)]
        elif options.format_name == "WEBP":
            ext = ".webp"
            params = [cv2.IMWRITE_WEBP_QUALITY, int(options.jpeg_quality)]
        elif options.format_name == "BMP":
            ext = ".bmp"
            if image_to_save.ndim == 3 and image_to_save.shape[2] == 4:
                image_to_save = cv2.cvtColor(image_to_save, cv2.COLOR_BGRA2BGR)
        elif options.format_name == "TIFF":
            ext = ".tif"
            if not options.preserve_alpha and image_to_save.ndim == 3 and image_to_save.shape[2] == 4:
                image_to_save = cv2.cvtColor(image_to_save, cv2.COLOR_BGRA2BGR)

        final_path = path.with_suffix(ext)
        ok, encoded = cv2.imencode(ext, image_to_save, params)
        if not ok or encoded is None:
            raise ExportError(f"OpenCV failed to encode export for format {options.format_name}")
        try:
            encoded.tofile(final_path)
        except OSError as exc:
            raise ExportError(f"Failed to write export file: {final_path}") from exc
        return final_path.resolve()
