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
class AdjustmentSpec:
    key: str
    label: str
    minimum: int
    maximum: int
    default: int
    step: int
    scale: float
    explanation: str

    def slider_to_value(self, slider_value: int) -> float:
        return slider_value * self.scale

    def value_to_slider(self, value: float) -> int:
        return int(round(value / self.scale))

    def format_value(self, value: float) -> str:
        if self.scale < 1.0:
            return f"{value:.2f}"
        return f"{value:.0f}"


ADJUSTMENT_SPECS: list[AdjustmentSpec] = [
    AdjustmentSpec("exposure", "Exposure", -40, 40, 0, 1, 0.05, "Brighten or darken the whole photo."),
    AdjustmentSpec("contrast", "Contrast", -100, 100, 0, 1, 1.0, "Increase difference between dark and bright areas."),
    AdjustmentSpec("white_balance_temp", "White Balance", -100, 100, 0, 1, 1.0, "Make the image cooler or warmer."),
    AdjustmentSpec("saturation", "Saturation", -100, 100, 0, 1, 1.0, "Control color intensity."),
    AdjustmentSpec("sharpening", "Sharpening", 0, 100, 0, 1, 1.0, "Enhance edge detail."),
    AdjustmentSpec("denoise", "Denoise", 0, 100, 0, 1, 1.0, "Reduce visible color and luminance noise."),
    AdjustmentSpec("shadows", "Shadows", -100, 100, 0, 1, 1.0, "Recover or deepen darker regions."),
]


class AdjustmentRow(QFrame):
    value_changed = Signal(str, float)
    slider_released_value = Signal(str, float)

    def __init__(self, spec: AdjustmentSpec, parent=None) -> None:
        super().__init__(parent)
        self.spec = spec
        self._build_ui()
        self.set_value(spec.slider_to_value(spec.default), emit_signal=False)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        self.name_label = QLabel(self.spec.label)
        self.name_label.setToolTip(self.spec.explanation)
        self.value_label = QLabel(self.spec.format_value(self.spec.slider_to_value(self.spec.default)))
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip(f"Reset {self.spec.label} to default")
        self.reset_button.clicked.connect(self._reset_clicked)
        top.addWidget(self.name_label)
        top.addStretch(1)
        top.addWidget(self.value_label)
        top.addWidget(self.reset_button)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(self.spec.minimum, self.spec.maximum)
        self.slider.setSingleStep(self.spec.step)
        self.slider.setPageStep(max(1, self.spec.step * 5))
        self.slider.setToolTip(self.spec.explanation)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderReleased.connect(self._on_slider_released)

        layout.addLayout(top)
        layout.addWidget(self.slider)

    def _on_slider_changed(self, slider_value: int) -> None:
        value = self.spec.slider_to_value(slider_value)
        self.value_label.setText(self.spec.format_value(value))
        self.value_changed.emit(self.spec.key, value)

    def _on_slider_released(self) -> None:
        value = self.spec.slider_to_value(self.slider.value())
        self.slider_released_value.emit(self.spec.key, value)

    def _reset_clicked(self) -> None:
        self.slider.setValue(self.spec.default)
        self._on_slider_released()

    def set_value(self, value: float, *, emit_signal: bool = False) -> None:
        slider_value = self.spec.value_to_slider(value)
        blocked = self.slider.blockSignals(not emit_signal)
        self.slider.setValue(slider_value)
        self.slider.blockSignals(blocked)
        self.value_label.setText(self.spec.format_value(value))


class AdjustmentPanel(QWidget):
    adjustment_preview_changed = Signal(str, float)
    adjustment_committed = Signal(str, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows: dict[str, AdjustmentRow] = {}
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(8)

        for row_index, spec in enumerate(ADJUSTMENT_SPECS):
            row = AdjustmentRow(spec)
            row.value_changed.connect(self.adjustment_preview_changed)
            row.slider_released_value.connect(self.adjustment_committed)
            self.rows[spec.key] = row
            layout.addWidget(row, row_index, 0)
        layout.setRowStretch(len(ADJUSTMENT_SPECS), 1)

    def set_control_value(self, key: str, value: float, *, emit_signal: bool = False) -> None:
        row = self.rows.get(key)
        if row is None:
            return
        row.set_value(value, emit_signal=emit_signal)

    def reset_all(self) -> None:
        for spec in ADJUSTMENT_SPECS:
            self.set_control_value(spec.key, spec.slider_to_value(spec.default), emit_signal=False)
