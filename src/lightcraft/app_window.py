from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .canvas_view import CanvasView
from .document import ImageDocument
from .image_io import ImageLoadError, SUPPORTED_FILTER


class AppWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LightCraft — Phase 1")
        self.resize(1400, 900)

        self.document = ImageDocument()
        self.canvas = CanvasView()
        self.canvas.zoom_changed.connect(self._on_zoom_changed)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._filename_label = QLabel("—")
        self._path_label = QLabel("—")
        self._dimensions_label = QLabel("—")
        self._channels_label = QLabel("—")
        self._filesize_label = QLabel("—")
        self._zoom_label = QLabel("100%")
        self._render_state_label = QLabel("Idle")

        self._init_actions()
        self._init_menu_bar()
        self._init_ui()
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
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(380)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        workflow_box = QGroupBox("Workflow")
        workflow_layout = QVBoxLayout(workflow_box)
        workflow_list = QListWidget()
        for text in ["1. Load", "2. Analyze", "3. Adjust", "4. Style", "5. Compare", "6. Export"]:
            item = QListWidgetItem(text)
            workflow_list.addItem(item)
        workflow_list.setCurrentRow(0)
        workflow_layout.addWidget(workflow_list)

        metadata_box = QGroupBox("Image Metadata")
        metadata_layout = QFormLayout(metadata_box)
        metadata_layout.addRow("Filename", self._filename_label)
        metadata_layout.addRow("Path", self._path_label)
        metadata_layout.addRow("Dimensions", self._dimensions_label)
        metadata_layout.addRow("Channels", self._channels_label)
        metadata_layout.addRow("File size", self._filesize_label)
        metadata_layout.addRow("Zoom", self._zoom_label)
        metadata_layout.addRow("Render state", self._render_state_label)

        session_box = QGroupBox("Session")
        session_layout = QVBoxLayout(session_box)
        info = QLabel(
            "Phase 1 keeps the source image immutable and rebuilds the preview from source + EditState.\n\n"
            "Histogram, sliders, export, presets, AI, and history arrive in later phases."
        )
        info.setWordWrap(True)
        reset_button = QPushButton("Reset to Original")
        reset_button.clicked.connect(self.reset_document)
        session_layout.addWidget(info)
        session_layout.addWidget(reset_button)
        session_layout.addStretch(1)

        layout.addWidget(workflow_box)
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

        layout.addWidget(header)
        layout.addWidget(self.canvas, 1)
        return panel

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
            self.canvas.set_image_array(self.document.preview_image)
            self._populate_metadata()
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
        if self.document.preview_image is not None:
            self.canvas.set_image_array(self.document.preview_image)
            self.canvas.fit_to_window()
        self._populate_metadata()
        self._set_render_state("Ready")

    def show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "About LightCraft",
            "LightCraft Phase 1\n\n"
            "A workflow-based desktop photo editor shell for beginner photographers.\n"
            "This build focuses on image loading, scrollable viewing, non-destructive state separation, and reset behavior.",
        )

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

    def _set_render_state(self, state: str) -> None:
        self._render_state_label.setText(state)
        file_name = self.document.metadata.filename if self.document.metadata else "No image"
        dimensions = self._dimensions_label.text() if self.document.metadata else "—"
        self._update_status_bar(file_name=file_name, dimensions=dimensions, render_state=state)

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
