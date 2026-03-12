from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True, slots=True)
class TransformSpec:
    key: str
    label: str
    minimum: int
    maximum: int
    default: int
    explanation: str
    suffix: str = ""

    def format_value(self, slider_value: int) -> str:
        return f"{slider_value}{self.suffix}"


TRANSFORM_SPECS: list[TransformSpec] = [
    TransformSpec("rotation_deg", "Rotate", -180, 180, 0, "Rotate the image clockwise or counterclockwise.", "°"),
    TransformSpec("crop_left_pct", "Crop Left", 0, 45, 0, "Trim away pixels from the left edge.", "%"),
    TransformSpec("crop_top_pct", "Crop Top", 0, 45, 0, "Trim away pixels from the top edge.", "%"),
    TransformSpec("crop_right_pct", "Crop Right", 0, 45, 0, "Trim away pixels from the right edge.", "%"),
    TransformSpec("crop_bottom_pct", "Crop Bottom", 0, 45, 0, "Trim away pixels from the bottom edge.", "%"),
]


class TransformRow(QFrame):
    value_changed = Signal(str, float)
    slider_released_value = Signal(str, float)

    def __init__(self, spec: TransformSpec, parent=None) -> None:
        super().__init__(parent)
        self.spec = spec
        self._build_ui()
        self.set_value(float(spec.default), emit_signal=False)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.name_label = QLabel(self.spec.label)
        self.name_label.setToolTip(self.spec.explanation)
        self.value_label = QLabel(self.spec.format_value(self.spec.default))
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._reset_clicked)
        top.addWidget(self.name_label)
        top.addStretch(1)
        top.addWidget(self.value_label)
        top.addWidget(self.reset_button)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(self.spec.minimum, self.spec.maximum)
        self.slider.setToolTip(self.spec.explanation)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderReleased.connect(self._on_slider_released)

        layout.addLayout(top)
        layout.addWidget(self.slider)

    def _on_slider_changed(self, slider_value: int) -> None:
        self.value_label.setText(self.spec.format_value(slider_value))
        self.value_changed.emit(self.spec.key, float(slider_value))

    def _on_slider_released(self) -> None:
        self.slider_released_value.emit(self.spec.key, float(self.slider.value()))

    def _reset_clicked(self) -> None:
        self.slider.setValue(self.spec.default)
        self._on_slider_released()

    def set_value(self, value: float, *, emit_signal: bool = False) -> None:
        slider_value = int(round(value))
        blocked = self.slider.blockSignals(not emit_signal)
        self.slider.setValue(slider_value)
        self.slider.blockSignals(blocked)
        self.value_label.setText(self.spec.format_value(slider_value))


class TransformPanel(QWidget):
    transform_preview_changed = Signal(str, float)
    transform_committed = Signal(str, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows: dict[str, TransformRow] = {}
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(8)

        for row_index, spec in enumerate(TRANSFORM_SPECS):
            row = TransformRow(spec)
            row.value_changed.connect(self.transform_preview_changed)
            row.slider_released_value.connect(self.transform_committed)
            self.rows[spec.key] = row
            layout.addWidget(row, row_index, 0)
        layout.setRowStretch(len(TRANSFORM_SPECS), 1)

    def set_control_value(self, key: str, value: float, *, emit_signal: bool = False) -> None:
        row = self.rows.get(key)
        if row is None:
            return
        row.set_value(value, emit_signal=emit_signal)

    def reset_all(self) -> None:
        for spec in TRANSFORM_SPECS:
            self.set_control_value(spec.key, float(spec.default), emit_signal=False)
