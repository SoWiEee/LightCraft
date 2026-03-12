from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from .settings import AppSettingsState


class ThemeManager:
    def apply(self, app: QApplication, state: AppSettingsState) -> None:
        app.setStyle("Fusion")
        if state.appearance_mode == "dark":
            app.setPalette(self._dark_palette())
        else:
            app.setPalette(app.style().standardPalette())
        self._apply_font(app, state)

    def _apply_font(self, app: QApplication, state: AppSettingsState) -> None:
        base = app.font()
        if state.font_family:
            base.setFamily(state.font_family)
        if state.font_point_size > 0:
            base.setPointSize(state.font_point_size)
        app.setFont(base)

    @staticmethod
    def _dark_palette() -> QPalette:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(15, 15, 15))
        palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 90, 90))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(64, 128, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 160, 255))
        return palette
