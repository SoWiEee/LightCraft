from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .presets import PresetDefinition


class PresetPanel(QWidget):
    preset_apply_requested = Signal(str)
    preset_clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._items_by_id: dict[str, QListWidgetItem] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.recommendation_label = QLabel("Recommendation will appear after image analysis.")
        self.recommendation_label.setWordWrap(True)
        layout.addWidget(self.recommendation_label)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_item_selected)
        layout.addWidget(self.list_widget, 1)

        self.details_label = QLabel("Pick a preset to read what it is for.")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)

        self.apply_button = QPushButton("Apply Selected Preset")
        self.apply_button.clicked.connect(self._apply_current)
        layout.addWidget(self.apply_button)

        self.clear_button = QPushButton("Clear Preset Tag")
        self.clear_button.clicked.connect(self.preset_clear_requested)
        layout.addWidget(self.clear_button)

    def set_presets(self, presets: list[PresetDefinition]) -> None:
        self.list_widget.clear()
        self._items_by_id.clear()
        for preset in presets:
            item = QListWidgetItem(preset.name)
            item.setData(Qt.ItemDataRole.UserRole, preset)
            item.setToolTip(preset.summary)
            self.list_widget.addItem(item)
            self._items_by_id[preset.preset_id] = item
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def set_recommendation(self, text: str, *, preset_id: str | None = None) -> None:
        self.recommendation_label.setText(text)
        if preset_id and preset_id in self._items_by_id:
            self.list_widget.setCurrentItem(self._items_by_id[preset_id])

    def set_active_preset(self, preset_id: str | None) -> None:
        if preset_id and preset_id in self._items_by_id:
            self.list_widget.setCurrentItem(self._items_by_id[preset_id])

    def _on_item_selected(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if current is None:
            self.details_label.setText("Pick a preset to read what it is for.")
            return
        preset = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(preset, PresetDefinition):
            self.details_label.setText(
                f"{preset.summary}\n\nUse when: {preset.when_to_use}"
            )

    def _apply_current(self) -> None:
        current = self.list_widget.currentItem()
        if current is None:
            return
        preset = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(preset, PresetDefinition):
            self.preset_apply_requested.emit(preset.preset_id)
