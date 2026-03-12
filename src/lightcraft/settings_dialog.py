from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .settings import AppSettingsState


class SettingsDialog(QDialog):
    def __init__(self, current: AppSettingsState, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(420, 300)
        self._build_ui()
        self._load_state(current)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_appearance_tab(), "Appearance")
        self.tabs.addTab(self._build_behavior_tab(), "Behavior")
        layout.addWidget(self.tabs)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_appearance_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Follow system", "system")
        self.mode_combo.addItem("Light", "light")
        self.mode_combo.addItem("Dark", "dark")

        self.font_combo = QFontComboBox()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)

        reset_row = QHBoxLayout()
        self.reset_font_button = QPushButton("Use default UI font")
        self.reset_font_button.clicked.connect(self._reset_font)
        reset_row.addWidget(self.reset_font_button)
        reset_row.addStretch(1)
        reset_widget = QWidget()
        reset_widget.setLayout(reset_row)

        self.preview_label = QLabel("The quick brown fox jumps over the lazy dog 12345")
        self.preview_label.setWordWrap(True)

        self.font_combo.currentFontChanged.connect(lambda _: self._update_preview_font())
        self.font_size_spin.valueChanged.connect(lambda _: self._update_preview_font())

        form.addRow("Theme mode", self.mode_combo)
        form.addRow("Installed font", self.font_combo)
        form.addRow("Font size", self.font_size_spin)
        form.addRow("Font reset", reset_widget)
        form.addRow("Preview", self.preview_label)
        return page

    def _build_behavior_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.preview_debounce_spin = QSpinBox()
        self.preview_debounce_spin.setRange(30, 300)
        self.preview_debounce_spin.setSingleStep(10)
        self.preview_debounce_spin.setSuffix(" ms")
        form.addRow("Preview debounce", self.preview_debounce_spin)
        return page

    def _load_state(self, state: AppSettingsState) -> None:
        idx = self.mode_combo.findData(state.appearance_mode)
        self.mode_combo.setCurrentIndex(max(0, idx))
        if state.font_family:
            self.font_combo.setCurrentFont(QFont(state.font_family))
        self.font_size_spin.setValue(state.font_point_size)
        self.preview_debounce_spin.setValue(state.preview_debounce_ms)
        self._update_preview_font()

    def _reset_font(self) -> None:
        self.font_combo.setCurrentFont(QFont())
        self.font_size_spin.setValue(10)
        self._update_preview_font()

    def _update_preview_font(self) -> None:
        font = self.font_combo.currentFont()
        font.setPointSize(self.font_size_spin.value())
        self.preview_label.setFont(font)

    def selected_state(self) -> AppSettingsState:
        return AppSettingsState(
            appearance_mode=str(self.mode_combo.currentData()),
            font_family=self.font_combo.currentFont().family(),
            font_point_size=self.font_size_spin.value(),
            preview_debounce_ms=self.preview_debounce_spin.value(),
        )
