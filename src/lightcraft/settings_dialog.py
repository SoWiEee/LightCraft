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

from .i18n import Localizer
from .settings import AppSettingsState


class SettingsDialog(QDialog):
    def __init__(self, current: AppSettingsState, localizer: Localizer, parent=None) -> None:
        super().__init__(parent)
        self.localizer = localizer
        self.setModal(True)
        self.resize(440, 340)
        self._build_ui()
        self._load_state(current)
        self.retranslate_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.appearance_page = self._build_appearance_tab()
        self.behavior_page = self._build_behavior_tab()
        self.tabs.addTab(self.appearance_page, "")
        self.tabs.addTab(self.behavior_page, "")
        layout.addWidget(self.tabs)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _build_appearance_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)

        self.mode_label = QLabel()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("", "system")
        self.mode_combo.addItem("", "light")
        self.mode_combo.addItem("", "dark")

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Traditional Chinese", "zh_TW")
        self.language_combo.currentIndexChanged.connect(self._preview_language_changed)

        self.font_label = QLabel()
        self.font_combo = QFontComboBox()
        self.font_size_label = QLabel()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)

        reset_row = QHBoxLayout()
        self.reset_font_button = QPushButton()
        self.reset_font_button.clicked.connect(self._reset_font)
        reset_row.addWidget(self.reset_font_button)
        reset_row.addStretch(1)
        reset_widget = QWidget()
        reset_widget.setLayout(reset_row)

        self.font_reset_label = QLabel()
        self.preview_title_label = QLabel()
        self.preview_label = QLabel("The quick brown fox jumps over the lazy dog 12345")
        self.preview_label.setWordWrap(True)

        self.font_combo.currentFontChanged.connect(lambda _: self._update_preview_font())
        self.font_size_spin.valueChanged.connect(lambda _: self._update_preview_font())

        form.addRow(self.mode_label, self.mode_combo)
        form.addRow(self.language_label, self.language_combo)
        form.addRow(self.font_label, self.font_combo)
        form.addRow(self.font_size_label, self.font_size_spin)
        form.addRow(self.font_reset_label, reset_widget)
        form.addRow(self.preview_title_label, self.preview_label)
        return page

    def _build_behavior_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.preview_debounce_label = QLabel()
        self.preview_debounce_spin = QSpinBox()
        self.preview_debounce_spin.setRange(30, 300)
        self.preview_debounce_spin.setSingleStep(10)
        self.preview_debounce_spin.setSuffix(" ms")
        form.addRow(self.preview_debounce_label, self.preview_debounce_spin)
        return page

    def _preview_language_changed(self) -> None:
        preview_localizer = Localizer(language_code=str(self.language_combo.currentData()))
        self.preview_label.setText(preview_localizer.tr("The quick brown fox jumps over the lazy dog 12345"))
        self.mode_combo.setItemText(0, preview_localizer.tr("Follow system"))
        self.mode_combo.setItemText(1, preview_localizer.tr("Light"))
        self.mode_combo.setItemText(2, preview_localizer.tr("Dark"))
        self.tabs.setTabText(0, preview_localizer.tr("Appearance"))
        self.tabs.setTabText(1, preview_localizer.tr("Behavior"))
        self.setWindowTitle(preview_localizer.tr("Settings"))
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(preview_localizer.tr("OK") if preview_localizer.tr("OK") != "OK" else "OK")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(preview_localizer.tr("Cancel") if preview_localizer.tr("Cancel") != "Cancel" else "Cancel")
        self.mode_label.setText(preview_localizer.tr("Theme mode"))
        self.language_label.setText(preview_localizer.tr("Language"))
        self.font_label.setText(preview_localizer.tr("Installed font"))
        self.font_size_label.setText(preview_localizer.tr("Font size"))
        self.font_reset_label.setText(preview_localizer.tr("Font reset"))
        self.preview_title_label.setText(preview_localizer.tr("Preview"))
        self.preview_debounce_label.setText(preview_localizer.tr("Preview debounce"))
        self.preview_debounce_spin.setSuffix(preview_localizer.tr(" ms"))
        self.reset_font_button.setText(preview_localizer.tr("Use default UI font"))

    def retranslate_ui(self) -> None:
        self._preview_language_changed()

    def _load_state(self, state: AppSettingsState) -> None:
        idx = self.mode_combo.findData(state.appearance_mode)
        self.mode_combo.setCurrentIndex(max(0, idx))
        lang_idx = self.language_combo.findData(state.language_code)
        self.language_combo.setCurrentIndex(max(0, lang_idx))
        if state.font_family:
            self.font_combo.setCurrentFont(QFont(state.font_family))
        self.font_size_spin.setValue(state.font_point_size)
        self.preview_debounce_spin.setValue(state.preview_debounce_ms)
        self._update_preview_font()
        self.retranslate_ui()

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
            language_code=str(self.language_combo.currentData()),
            font_family=self.font_combo.currentFont().family(),
            font_point_size=self.font_size_spin.value(),
            preview_debounce_ms=self.preview_debounce_spin.value(),
        )
