from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)


@dataclass(slots=True)
class ExportOptions:
    format_name: str
    jpeg_quality: int = 95
    png_compression: int = 3
    preserve_alpha: bool = True


_FORMAT_ITEMS = [
    ("JPEG", ".jpg"),
    ("PNG", ".png"),
    ("WEBP", ".webp"),
    ("BMP", ".bmp"),
    ("TIFF", ".tif"),
]


class ExportDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Settings")
        self.setModal(True)
        self.resize(380, 220)

        self._format_combo = QComboBox()
        for fmt, ext in _FORMAT_ITEMS:
            self._format_combo.addItem(f"{fmt} ({ext})", userData=fmt)

        self._jpeg_quality = QSpinBox()
        self._jpeg_quality.setRange(1, 100)
        self._jpeg_quality.setValue(95)

        self._png_compression = QSpinBox()
        self._png_compression.setRange(0, 9)
        self._png_compression.setValue(3)

        self._preserve_alpha = QCheckBox("Preserve alpha channel when supported")
        self._preserve_alpha.setChecked(True)

        form = QFormLayout()
        form.addRow("Format", self._format_combo)
        form.addRow("JPEG quality", self._jpeg_quality)
        form.addRow("PNG compression", self._png_compression)

        hint = QLabel(
            "Export uses the current edited preview at full current render resolution. "
            "JPEG ignores alpha. PNG and TIFF preserve alpha if the image has one."
        )
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._preserve_alpha)
        layout.addWidget(hint)
        layout.addWidget(buttons)

    def selected_options(self) -> ExportOptions:
        return ExportOptions(
            format_name=str(self._format_combo.currentData()),
            jpeg_quality=int(self._jpeg_quality.value()),
            png_compression=int(self._png_compression.value()),
            preserve_alpha=bool(self._preserve_alpha.isChecked()),
        )

    @staticmethod
    def default_suffix_for(format_name: str) -> str:
        for fmt, ext in _FORMAT_ITEMS:
            if fmt == format_name:
                return ext
        return ".png"
