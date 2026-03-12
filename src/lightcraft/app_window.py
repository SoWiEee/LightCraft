from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .adjustments import ADJUSTMENT_SPECS, AdjustmentPanel
from .canvas_view import CanvasView
from .crop_rotate import TRANSFORM_SPECS, TransformPanel
from .document import ImageDocument
from .histogram import HistogramWidget
from .image_io import ImageLoadError, SUPPORTED_FILTER
from .settings import SettingsStore
from .settings_dialog import SettingsDialog
from .theme import ThemeManager

WORKFLOW_STEPS = [
    "1. Load",
    "2. Analyze",
    "3. Adjust",
    "4. Style",
    "5. Compare",
    "6. Export",
]

WORKFLOW_HINTS: dict[str, str] = {
    "1. Load": "Start with a technically usable image. Avoid duplicates, screenshots, and extremely compressed files.",
    "2. Analyze": "Read the histogram first. Check clipping, flat contrast, color cast, and whether the subject is underexposed.",
    "3. Adjust": "Fix tone and transform before style. Exposure, contrast, shadows, crop, and rotation should come before presets.",
    "4. Style": "Style should be the last 10 percent. Do not hide bad exposure behind a preset.",
    "5. Compare": "Compare against the original and ask one question: does the edit solve the problem you identified earlier?",
    "6. Export": "Export after the edit looks correct at fit view and at 100 percent zoom. Avoid oversharpening and aggressive denoise.",
}


class AppWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LightCraft — Phase 3")
        self.resize(1600, 960)

        self.document = ImageDocument()
        self.canvas = CanvasView()
        self.canvas.zoom_changed.connect(self._on_zoom_changed)

        self.settings_store = SettingsStore()
        self.theme_manager = ThemeManager()
        self.app_settings = self.settings_store.load()
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._apply_preview_render)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._filename_label = QLabel("—")
        self._path_label = QLabel("—")
        self._dimensions_label = QLabel("—")
        self._channels_label = QLabel("—")
        self._filesize_label = QLabel("—")
        self._zoom_label = QLabel("100%")
        self._render_state_label = QLabel("Idle")
        self._pending_status_label = QLabel("0")
        self._workflow_list = QListWidget()
        self._workflow_hint_label = QLabel(WORKFLOW_HINTS[WORKFLOW_STEPS[0]])
        self._workflow_hint_label.setWordWrap(True)
        self._histogram_widget = HistogramWidget()
        self._adjustment_panel = AdjustmentPanel()
        self._adjustment_panel.adjustment_preview_changed.connect(self._on_adjustment_preview_changed)
        self._adjustment_panel.adjustment_committed.connect(self._on_adjustment_committed)
        self._transform_panel = TransformPanel()
        self._transform_panel.transform_preview_changed.connect(self._on_transform_preview_changed)
        self._transform_panel.transform_committed.connect(self._on_transform_committed)

        self._init_actions()
        self._init_menu_bar()
        self._init_ui()
        self._sync_settings_to_runtime()
        self._update_status_bar(file_name="No image", dimensions="—", render_state="Idle")
        self.canvas.clear_image()

    def _init_actions(self) -> None:
        self.open_action = QAction("Open Image...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_image_dialog)

        self.reset_action = QAction("Reset to Original", self)
        self.reset_action.setShortcut(QKeySequence("Ctrl+R"))
        self.reset_action.triggered.connect(self.reset_document)

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(QApplication.instance().quit)

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(self.canvas.zoom_in)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(self.canvas.zoom_out)

        self.fit_action = QAction("Fit to Window", self)
        self.fit_action.setShortcut(QKeySequence("Ctrl+0"))
        self.fit_action.triggered.connect(self.canvas.fit_to_window)

        self.settings_action = QAction("Settings...", self)
        self.settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        self.settings_action.triggered.connect(self.open_settings_dialog)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)

    def _init_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.reset_action)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.fit_action)

        settings_menu = self.menuBar().addMenu("&Settings")
        settings_menu.addAction(self.settings_action)

        self.menuBar().addMenu("&Presets")
        self.menuBar().addMenu("&AI")

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _init_ui(self) -> None:
        central = QWidget()
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_center_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([320, 960, 380])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        root_layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(380)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        workflow_box = QGroupBox("Workflow Progress")
        workflow_layout = QVBoxLayout(workflow_box)
        for text in WORKFLOW_STEPS:
            self._workflow_list.addItem(QListWidgetItem(text))
        self._workflow_list.setCurrentRow(0)
        self._workflow_list.currentItemChanged.connect(self._on_workflow_selection_changed)
        workflow_layout.addWidget(self._workflow_list)

        hint_box = QGroupBox("Editing Guidance")
        hint_layout = QVBoxLayout(hint_box)
        hint_intro = QLabel("Use the workflow to avoid random slider-tweaking. Fix the problem you can name.")
        hint_intro.setWordWrap(True)
        hint_layout.addWidget(hint_intro)
        hint_layout.addWidget(self._workflow_hint_label)

        metadata_box = QGroupBox("Image Metadata")
        metadata_layout = QFormLayout(metadata_box)
        metadata_layout.addRow("Filename", self._filename_label)
        metadata_layout.addRow("Path", self._path_label)
        metadata_layout.addRow("Dimensions", self._dimensions_label)
        metadata_layout.addRow("Channels", self._channels_label)
        metadata_layout.addRow("File size", self._filesize_label)
        metadata_layout.addRow("Zoom", self._zoom_label)
        metadata_layout.addRow("Render state", self._render_state_label)
        metadata_layout.addRow("Queued preview", self._pending_status_label)

        session_box = QGroupBox("Session")
        session_layout = QVBoxLayout(session_box)
        info = QLabel(
            "Phase 3 adds transform controls and a workflow-first UI.\n\n"
            "The left column explains what to do next. The right column holds the technical controls."
        )
        info.setWordWrap(True)
        reset_button = QPushButton("Reset to Original")
        reset_button.clicked.connect(self.reset_document)
        settings_button = QPushButton("Open Settings")
        settings_button.clicked.connect(self.open_settings_dialog)
        session_layout.addWidget(info)
        session_layout.addWidget(reset_button)
        session_layout.addWidget(settings_button)
        session_layout.addStretch(1)

        layout.addWidget(workflow_box)
        layout.addWidget(hint_box)
        layout.addWidget(metadata_box)
        layout.addWidget(session_box)
        layout.addStretch(1)
        return panel

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Main Canvas")
        header.setStyleSheet("font-size: 16px; font-weight: 600; padding: 4px 0;")
        header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        subheader = QLabel("Keep the preview large. Controls belong in the sidebars, not on top of the image.")
        subheader.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(subheader)
        layout.addWidget(self.canvas, 1)
        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(340)
        panel.setMaximumWidth(460)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.addTab(self._build_develop_tab(), "Develop")
        tabs.addTab(self._build_transform_tab(), "Transform")
        layout.addWidget(tabs)
        return panel

    def _build_develop_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        histogram_box = QGroupBox("Histogram")
        histogram_layout = QVBoxLayout(histogram_box)
        histogram_layout.addWidget(self._histogram_widget)

        adjustment_box = QGroupBox("Tone & Detail")
        adjustment_layout = QVBoxLayout(adjustment_box)
        adjustment_hint = QLabel("Global corrections first. Avoid trying to solve every problem with one slider.")
        adjustment_hint.setWordWrap(True)
        adjustment_layout.addWidget(adjustment_hint)
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setWidget(self._adjustment_panel)
        adjustment_layout.addWidget(scroller, 1)

        future_box = QGroupBox("Planned Controls")
        future_layout = QVBoxLayout(future_box)
        future_hint = QLabel(
            "Reserved for later phases: temperature fine-tune, blur, texture, vignette, color noise, and other detail controls."
        )
        future_hint.setWordWrap(True)
        future_layout.addWidget(future_hint)

        layout.addWidget(histogram_box)
        layout.addWidget(adjustment_box, 1)
        layout.addWidget(future_box)
        return page

    def _build_transform_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        transform_box = QGroupBox("Crop & Rotate")
        transform_layout = QVBoxLayout(transform_box)
        transform_hint = QLabel(
            "Straighten first, then crop. Rotation changes the canvas bounds, so keep an eye on empty black corners."
        )
        transform_hint.setWordWrap(True)
        transform_layout.addWidget(transform_hint)
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setWidget(self._transform_panel)
        transform_layout.addWidget(scroller, 1)

        composition_box = QGroupBox("Composition Notes")
        composition_layout = QVBoxLayout(composition_box)
        composition_text = QLabel(
            "Cropping is a decision, not a rescue tool. Remove dead space, level the horizon, and keep the subject placement intentional."
        )
        composition_text.setWordWrap(True)
        composition_layout.addWidget(composition_text)

        layout.addWidget(transform_box, 1)
        layout.addWidget(composition_box)
        return page

    def open_image_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", str(Path.home()), SUPPORTED_FILTER)
        if filename:
            self.open_image(filename)

    def open_image(self, path: str) -> None:
        self._set_render_state("Loading...")
        try:
            self.document.open_image(path)
            if self.document.preview_image is None or self.document.metadata is None:
                raise ImageLoadError("Loaded image but preview or metadata is missing")
            self.canvas.set_image_array(self.document.preview_image, preserve_zoom=False)
            self._adjustment_panel.reset_all()
            self._transform_panel.reset_all()
            self._populate_metadata()
            self._update_histogram()
            self._set_workflow_step("2. Analyze")
            self.canvas.fit_to_window()
            self._set_render_state("Ready")
        except ImageLoadError as exc:
            self._set_render_state("Load failed")
            QMessageBox.critical(self, "Failed to open image", str(exc))

    def reset_document(self) -> None:
        if not self.document.has_image():
            return
        self._set_render_state("Resetting...")
        self.document.reset()
        self._adjustment_panel.reset_all()
        self._transform_panel.reset_all()
        if self.document.preview_image is not None:
            self.canvas.set_image_array(self.document.preview_image, preserve_zoom=False)
            self.canvas.fit_to_window()
        self._update_histogram()
        self._populate_metadata()
        self._set_workflow_step("2. Analyze")
        self._set_render_state("Ready")

    def open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec():
            self.app_settings = dialog.selected_state()
            self.settings_store.save(self.app_settings)
            self._sync_settings_to_runtime()

    def show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "About LightCraft",
            "LightCraft Phase 3\n\n"
            "A workflow-based desktop photo editor for beginner photographers.\n"
            "This build adds crop/rotate tools and a three-column workflow UI.",
        )

    def _sync_settings_to_runtime(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        self.theme_manager.apply(app, self.app_settings)
        self._preview_timer.setInterval(self.app_settings.preview_debounce_ms)

    def _populate_metadata(self) -> None:
        metadata = self.document.metadata
        if metadata is None:
            return
        self._filename_label.setText(metadata.filename)
        self._path_label.setText(str(metadata.path))
        self._path_label.setToolTip(str(metadata.path))
        self._dimensions_label.setText(f"{metadata.width} × {metadata.height}")
        self._channels_label.setText(str(metadata.channels))
        self._filesize_label.setText(self._format_file_size(metadata.file_size_bytes))
        self._zoom_label.setText(f"{self.canvas.scale_factor * 100:.0f}%")
        self._update_status_bar(
            file_name=metadata.filename,
            dimensions=f"{metadata.width} × {metadata.height}",
            render_state=self._render_state_label.text(),
        )

    def _on_zoom_changed(self, scale: float) -> None:
        self._zoom_label.setText(f"{scale * 100:.0f}%")
        dimensions = self._dimensions_label.text() if self.document.metadata else "—"
        file_name = self.document.metadata.filename if self.document.metadata else "No image"
        self._update_status_bar(file_name=file_name, dimensions=dimensions, render_state=self._render_state_label.text())

    def _on_adjustment_preview_changed(self, key: str, value: float) -> None:
        self._queue_edit_change(key, value, workflow_step="3. Adjust")

    def _on_adjustment_committed(self, key: str, value: float) -> None:
        self._commit_edit_change(key, value, workflow_step="3. Adjust")

    def _on_transform_preview_changed(self, key: str, value: float) -> None:
        self._queue_edit_change(key, value, workflow_step="3. Adjust")

    def _on_transform_committed(self, key: str, value: float) -> None:
        self._commit_edit_change(key, value, workflow_step="3. Adjust")

    def _queue_edit_change(self, key: str, value: float, *, workflow_step: str) -> None:
        if not self.document.has_image():
            return
        setattr(self.document.edit_state, key, value)
        self._pending_status_label.setText("1")
        self._set_workflow_step(workflow_step)
        self._set_render_state("Preview queued")
        self._preview_timer.start()

    def _commit_edit_change(self, key: str, value: float, *, workflow_step: str) -> None:
        if not self.document.has_image():
            return
        setattr(self.document.edit_state, key, value)
        self._set_workflow_step(workflow_step)
        self._apply_preview_render()
        self._set_render_state(f"Committed {self._pretty_key(key)}")

    def _apply_preview_render(self) -> None:
        if not self.document.has_image():
            return
        try:
            self.document.rerender()
            if self.document.preview_image is not None:
                self.canvas.set_image_array(self.document.preview_image, preserve_zoom=True)
            self._update_histogram()
            self._pending_status_label.setText("0")
            self._populate_metadata()
            self._set_render_state("Ready")
        except Exception as exc:  # noqa: BLE001
            self._pending_status_label.setText("0")
            self.statusBar().showMessage(f"Preview render failed: {exc}", 5000)
            self._set_render_state("Preview failed")

    def _update_histogram(self) -> None:
        self._histogram_widget.set_histogram_image(self.document.preview_image)

    def _set_render_state(self, state: str) -> None:
        self._render_state_label.setText(state)
        file_name = self.document.metadata.filename if self.document.metadata else "No image"
        dimensions = self._dimensions_label.text() if self.document.metadata else "—"
        self._update_status_bar(file_name=file_name, dimensions=dimensions, render_state=state)

    def _set_workflow_step(self, step_text: str) -> None:
        matching = self._workflow_list.findItems(step_text, Qt.MatchFlag.MatchExactly)
        if not matching:
            return
        item = matching[0]
        self._workflow_list.setCurrentItem(item)
        self._workflow_hint_label.setText(WORKFLOW_HINTS.get(step_text, ""))

    def _on_workflow_selection_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if current is None:
            return
        self._workflow_hint_label.setText(WORKFLOW_HINTS.get(current.text(), ""))

    def _update_status_bar(self, *, file_name: str, dimensions: str, render_state: str) -> None:
        self._status.showMessage(
            f"File: {file_name}   |   Resolution: {dimensions}   |   Zoom: {self.canvas.scale_factor * 100:.0f}%   |   Render: {render_state}"
        )

    @staticmethod
    def _format_file_size(num_bytes: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        value = float(num_bytes)
        for unit in units:
            if value < 1024.0 or unit == units[-1]:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{num_bytes} B"

    @staticmethod
    def _pretty_key(key: str) -> str:
        mapping = {spec.key: spec.label for spec in ADJUSTMENT_SPECS}
        mapping.update({spec.key: spec.label for spec in TRANSFORM_SPECS})
        return mapping.get(key, key)
