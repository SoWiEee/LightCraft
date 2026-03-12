# LightCraft Phase 3

LightCraft is a workflow-based desktop photo editor for beginner photographers.
This Phase 3 build adds a live histogram, seven global adjustment controls, and a settings dialog with light/dark mode plus installed-font selection.

## Implemented in this build

- Single-image session with immutable source buffer
- Non-destructive preview re-render from `source_image + EditState`
- Scrollable image canvas with zoom in/out and fit-to-window
- Histogram panel that updates after image load and preview refresh
- Global adjustment controls:
  - Exposure
  - Contrast
  - White Balance
  - Saturation
  - Sharpening
  - Denoise
  - Shadows
- Per-control reset button
- Settings dialog:
  - Theme mode: system, light, dark
  - Installed font selection from local computer fonts
  - UI font size
  - Preview debounce interval

## Not in this phase yet

- Crop / rotate workflow
- Before / after compare mode
- Export
- Preset system
- Edit history timeline
- Hugging Face AI assistant

## Requirements

- Python 3.13
- `uv`

## Quick start

```bash
uv python install 3.13
uv sync
uv run lightcraft
```

## Project structure

```text
lightcraft_phase2/
├── docs/
│   └── manual.md
├── pyproject.toml
├── README.md
└── src/
    └── lightcraft/
        ├── adjustments.py
        ├── app_window.py
        ├── canvas_view.py
        ├── document.py
        ├── histogram.py
        ├── image_io.py
        ├── main.py
        ├── models.py
        ├── render_engine.py
        ├── settings.py
        ├── settings_dialog.py
        └── theme.py
```

## Run notes

The app is designed around Qt Widgets via PySide6 and image processing via OpenCV.
If your machine is missing Qt runtime dependencies, install them first and then rerun `uv sync`.

## Development note

This repository was prepared in a build environment that did not include a runnable PySide6 GUI runtime, so the code was syntax-checked and structure-checked, but the interactive window behavior still needs to be verified on your machine.


## Phase 3 additions

- Three-column UI: workflow guidance on the left, canvas in the center, technical controls on the right.
- New Transform tab with rotate + crop controls.
- Right sidebar reserves space for future controls such as blur, texture, vignette, and color-noise tuning.
