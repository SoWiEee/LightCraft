from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSplitter, QStackedWidget, QVBoxLayout, QWidget

from .canvas_view import CanvasView
from .i18n import Localizer


class CompareMode(str, Enum):
    OFF = "off"
    SPLIT = "split"
    TOGGLE = "toggle"


class CompareView(QWidget):
    zoom_changed = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.localizer = Localizer()
        self._mode = CompareMode.OFF
        self._last_single_view = "edited"

        self._edited_single = CanvasView()
        self._original_single = CanvasView()
        self._original_split = CanvasView()
        self._edited_split = CanvasView()

        self._edited_single.zoom_changed.connect(self._sync_zoom_from_edited_single)
        self._original_single.zoom_changed.connect(self._sync_zoom_from_original_single)
        self._original_split.zoom_changed.connect(self._sync_zoom_from_original_split)
        self._edited_split.zoom_changed.connect(self._sync_zoom_from_edited_split)

        self._stack = QStackedWidget()
        self._single_container = QWidget()
        single_layout = QVBoxLayout(self._single_container)
        single_layout.setContentsMargins(0, 0, 0, 0)
        self._single_title = QLabel("Edited Preview")
        self._single_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        single_layout.addWidget(self._single_title)
        single_layout.addWidget(self._edited_single)

        self._splitter_container = QWidget()
        split_layout = QVBoxLayout(self._splitter_container)
        split_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        original_wrap = QWidget()
        original_wrap_layout = QVBoxLayout(original_wrap)
        original_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self._original_split_label = QLabel("Original")
        original_label = self._original_split_label
        original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        original_wrap_layout.addWidget(original_label)
        original_wrap_layout.addWidget(self._original_split)

        edited_wrap = QWidget()
        edited_wrap_layout = QVBoxLayout(edited_wrap)
        edited_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self._edited_split_label = QLabel("Edited")
        edited_label = self._edited_split_label
        edited_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edited_wrap_layout.addWidget(edited_label)
        edited_wrap_layout.addWidget(self._edited_split)

        splitter.addWidget(original_wrap)
        splitter.addWidget(edited_wrap)
        splitter.setSizes([600, 600])
        split_layout.addWidget(splitter)

        self._stack.addWidget(self._single_container)
        self._stack.addWidget(self._splitter_container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)


    def set_localizer(self, localizer: Localizer) -> None:
        self.localizer = localizer
        self._original_split_label.setText(self.localizer.tr("Original"))
        self._edited_split_label.setText(self.localizer.tr("Edited"))
        self._sync_single_title()

    @property
    def scale_factor(self) -> float:
        active = self._active_canvas()
        return active.scale_factor if active is not None else 1.0

    def clear_images(self) -> None:
        for canvas in self._all_canvases():
            canvas.clear_image()

    def set_images(self, *, original_image, edited_image, preserve_zoom: bool = True) -> None:
        for canvas in (self._edited_single, self._edited_split):
            canvas.set_image_array(edited_image, preserve_zoom=preserve_zoom)
        for canvas in (self._original_single, self._original_split):
            canvas.set_image_array(original_image, preserve_zoom=preserve_zoom)

        active = self._active_canvas()
        if active is not None:
            self.zoom_changed.emit(active.scale_factor)

    def set_mode(self, mode: CompareMode) -> None:
        self._mode = mode
        if mode == CompareMode.SPLIT:
            self._stack.setCurrentWidget(self._splitter_container)
        else:
            self._stack.setCurrentWidget(self._single_container)
            self._sync_single_title()
        self.zoom_changed.emit(self.scale_factor)

    def toggle_single_view(self) -> None:
        if self._mode != CompareMode.TOGGLE:
            return
        self._last_single_view = "original" if self._last_single_view == "edited" else "edited"
        self._sync_single_title()

    def show_original_only(self) -> None:
        self._last_single_view = "original"
        self._sync_single_title()

    def show_edited_only(self) -> None:
        self._last_single_view = "edited"
        self._sync_single_title()

    def zoom_in(self) -> None:
        active = self._active_canvas()
        if active is not None:
            active.zoom_in()

    def zoom_out(self) -> None:
        active = self._active_canvas()
        if active is not None:
            active.zoom_out()

    def fit_to_window(self) -> None:
        if self._mode == CompareMode.SPLIT:
            self._original_split.fit_to_window()
            self._edited_split.fit_to_window()
            self._edited_split.set_zoom(self._original_split.scale_factor)
            self.zoom_changed.emit(self._original_split.scale_factor)
            return
        active = self._active_canvas()
        if active is not None:
            active.fit_to_window()
            self.zoom_changed.emit(active.scale_factor)

    def set_zoom(self, value: float) -> None:
        if self._mode == CompareMode.SPLIT:
            self._original_split.set_zoom(value)
            self._edited_split.set_zoom(value)
            self.zoom_changed.emit(self._edited_split.scale_factor)
            return
        active = self._active_canvas()
        if active is not None:
            active.set_zoom(value)
            self.zoom_changed.emit(active.scale_factor)

    def _sync_single_title(self) -> None:
        if self._last_single_view == "original":
            self._single_title.setText(f"{self.localizer.tr("Original")} Preview")
            self._edited_single.hide()
            self._original_single.setParent(self._single_container)
            layout = self._single_container.layout()
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
            layout.addWidget(self._original_single)
        else:
            self._single_title.setText(f"{self.localizer.tr("Edited")} Preview")
            self._original_single.hide()
            self._edited_single.setParent(self._single_container)
            layout = self._single_container.layout()
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
            layout.addWidget(self._edited_single)

    def _all_canvases(self) -> tuple[CanvasView, ...]:
        return self._edited_single, self._original_single, self._original_split, self._edited_split

    def _active_canvas(self) -> CanvasView | None:
        if self._mode == CompareMode.SPLIT:
            return self._edited_split
        return self._original_single if self._last_single_view == "original" else self._edited_single

    def _sync_zoom_from_edited_single(self, scale: float) -> None:
        if self._mode != CompareMode.OFF or self._last_single_view != "edited":
            self.zoom_changed.emit(scale)
            return
        self.zoom_changed.emit(scale)

    def _sync_zoom_from_original_single(self, scale: float) -> None:
        if self._mode == CompareMode.TOGGLE and self._last_single_view == "original":
            self.zoom_changed.emit(scale)

    def _sync_zoom_from_original_split(self, scale: float) -> None:
        if self._mode != CompareMode.SPLIT:
            return
        if abs(self._edited_split.scale_factor - scale) > 1e-6:
            self._edited_split.set_zoom(scale)
        self.zoom_changed.emit(scale)

    def _sync_zoom_from_edited_split(self, scale: float) -> None:
        if self._mode != CompareMode.SPLIT:
            return
        if abs(self._original_split.scale_factor - scale) > 1e-6:
            self._original_split.set_zoom(scale)
        self.zoom_changed.emit(scale)
