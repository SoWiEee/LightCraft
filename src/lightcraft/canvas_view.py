from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea, QSizePolicy

import cv2
import numpy as np


class CanvasView(QScrollArea):
    zoom_changed = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setBackgroundRole(self.backgroundRole())
        self._label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._label.setScaledContents(False)

        self.setWidget(self._label)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(480, 320)

        self._base_pixmap: QPixmap | None = None
        self._scale_factor: float = 1.0

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    def clear_image(self) -> None:
        self._label.clear()
        self._label.setText("Open an image to start.")
        self._base_pixmap = None
        self._scale_factor = 1.0
        self.zoom_changed.emit(self._scale_factor)

    def set_image_array(self, image: np.ndarray, *, preserve_zoom: bool = True) -> None:
        pixmap = self._numpy_to_pixmap(image)
        self._base_pixmap = pixmap
        if not preserve_zoom:
            self._scale_factor = 1.0
        self._apply_scaled_pixmap()
        self.zoom_changed.emit(self._scale_factor)

    def zoom_in(self) -> None:
        self.set_zoom(self._scale_factor * 1.25)

    def zoom_out(self) -> None:
        self.set_zoom(self._scale_factor / 1.25)

    def fit_to_window(self) -> None:
        if self._base_pixmap is None:
            return
        viewport_size = self.viewport().size()
        if viewport_size.width() <= 0 or viewport_size.height() <= 0:
            return
        width_ratio = viewport_size.width() / max(1, self._base_pixmap.width())
        height_ratio = viewport_size.height() / max(1, self._base_pixmap.height())
        self.set_zoom(min(width_ratio, height_ratio, 1.0))

    def set_zoom(self, value: float) -> None:
        if self._base_pixmap is None:
            return
        clamped = max(0.05, min(value, 8.0))
        if abs(clamped - self._scale_factor) < 1e-6:
            return
        self._scale_factor = clamped
        self._apply_scaled_pixmap()
        self.zoom_changed.emit(self._scale_factor)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)

    def _apply_scaled_pixmap(self) -> None:
        if self._base_pixmap is None:
            self.clear_image()
            return
        scaled = self._base_pixmap.scaled(
            max(1, int(self._base_pixmap.width() * self._scale_factor)),
            max(1, int(self._base_pixmap.height() * self._scale_factor)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
        self._label.resize(scaled.size())

    @staticmethod
    def _numpy_to_pixmap(image: np.ndarray) -> QPixmap:
        if image.ndim != 3:
            raise ValueError("Expected HxWxC image array")

        height, width, channels = image.shape
        if channels == 3:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            bytes_per_line = rgb.strides[0]
            qimage = QImage(
                rgb.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            ).copy()
        elif channels == 4:
            rgba = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            bytes_per_line = rgba.strides[0]
            qimage = QImage(
                rgba.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGBA8888,
            ).copy()
        else:
            raise ValueError(f"Unsupported channel count: {channels}")
        return QPixmap.fromImage(qimage)
