from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .app_window import AppWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("LightCraft")
    app.setOrganizationName("LightCraft")

    window = AppWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
