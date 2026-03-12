from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class HistogramWidget(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Histogram will appear after loading an image.")

    def set_histogram_image(self, image: np.ndarray | None) -> None:
        if image is None:
            self.clear()
            self.setText("Histogram will appear after loading an image.")
            return
        pixmap = self._build_histogram_pixmap(image)
        self.setPixmap(pixmap)

    @staticmethod
    def _build_histogram_pixmap(image: np.ndarray) -> QPixmap:
        height = 140
        width = 256
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        channels = [(0, (255, 80, 80)), (1, (80, 255, 80)), (2, (80, 80, 255))]

        working = image[:, :, :3] if image.ndim == 3 else image
        for channel_idx, color in channels:
            hist = cv2.calcHist([working], [channel_idx], None, [256], [0, 256]).flatten()
            if hist.max() <= 0:
                continue
            hist = hist / hist.max()
            points = np.column_stack((np.arange(256), height - 1 - (hist * (height - 10)).astype(np.int32)))
            cv2.polylines(canvas, [points.reshape(-1, 1, 2)], isClosed=False, color=color, thickness=1)

        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        qimage = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format.Format_RGB888).copy()
        return QPixmap.fromImage(qimage)
