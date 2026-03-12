from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont


@dataclass(slots=True)
class AppSettingsState:
    appearance_mode: str = "system"  # system | light | dark
    font_family: str = ""
    font_point_size: int = 10
    preview_debounce_ms: int = 80


class SettingsStore:
    def __init__(self) -> None:
        self._settings = QSettings()

    def load(self) -> AppSettingsState:
        return AppSettingsState(
            appearance_mode=str(self._settings.value("appearance/mode", "system")),
            font_family=str(self._settings.value("appearance/font_family", "")),
            font_point_size=int(self._settings.value("appearance/font_point_size", 10)),
            preview_debounce_ms=int(self._settings.value("behavior/preview_debounce_ms", 80)),
        )

    def save(self, state: AppSettingsState) -> None:
        self._settings.setValue("appearance/mode", state.appearance_mode)
        self._settings.setValue("appearance/font_family", state.font_family)
        self._settings.setValue("appearance/font_point_size", state.font_point_size)
        self._settings.setValue("behavior/preview_debounce_ms", state.preview_debounce_ms)
        self._settings.sync()


DEFAULT_FONT = QFont()
