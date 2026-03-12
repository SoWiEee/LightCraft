# LightCraft Phase 1

LightCraft is a workflow-based desktop photo editor aimed at beginner photographers.
This repository contains **Phase 1** of the project defined in the SDD:

- open a single JPEG/PNG image
- display it in a scrollable desktop canvas
- preserve an immutable source image in memory
- separate `EditState` from the source image
- re-render the preview from source + current state
- reset to original
- show filename, resolution, file size, and basic session metadata placeholders

Phase 1 deliberately excludes histogram, adjustment sliders, export, presets, AI features, and edit history.

## Why this stack

Qt for Python provides a well-supported pattern for desktop image viewers using `QLabel` inside `QScrollArea`, which matches the needs of a scrollable image canvas. citeturn570845search0turn570845search11

The project uses OpenCV for image decoding and buffer handling. OpenCV documents that decoded color images are stored in BGR order, which is what the render pipeline assumes internally. citeturn570845search3

The project is configured through `pyproject.toml`, which is the standard Python project metadata format, and `uv` supports dependency and project management directly from it. citeturn570845search1turn570845search6turn570845search9

Qt for Python release notes state that Python 3.13 support has been added, which is why this project targets Python 3.13 with a recent PySide6 release. citeturn457932search13

## Project layout

```text
lightcraft_phase1/
├── docs/
│   └── manual.md
├── pyproject.toml
├── README.md
└── src/
    └── lightcraft/
        ├── __init__.py
        ├── app_window.py
        ├── canvas_view.py
        ├── document.py
        ├── image_io.py
        ├── main.py
        ├── models.py
        └── render_engine.py
```

## Requirements

- Python 3.13
- `uv`

## Run with uv

Create the environment and install dependencies:

```bash
uv sync
```

Run the app:

```bash
uv run lightcraft
```

Or run the module directly:

```bash
uv run python -m lightcraft.main
```

## Current workflow

1. Launch the app
2. Use **File → Open Image...**
3. Inspect the loaded image in the central canvas
4. Use **Edit → Reset to Original** to verify non-destructive reset behavior
5. Use **View** actions to zoom in, zoom out, or fit to window

## Notes

- This phase stores the original image as an immutable session buffer and rebuilds the preview from the source image via the render engine.
- The render engine is intentionally simple in Phase 1 so that later phases can add adjustments without rewriting the application shell.
- Unicode file paths are handled through `numpy.fromfile(...) + cv2.imdecode(...)`, which avoids the common path-handling issues seen with direct `cv2.imread(...)` on some platforms.
