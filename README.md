# LightCraft Phase 4

LightCraft is a workflow-based desktop photo editor for beginner photographers.
This build keeps the three-column workflow UI and adds an extensible preset system with explainable scene analysis.

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
- Transform controls:
  - Rotate
  - Crop Left / Top / Right / Bottom
- Settings dialog:
  - Theme mode: system, light, dark
  - Installed font selection from local computer fonts
  - UI font size
  - Preview debounce interval
- Phase 4 additions:
  - Scene analysis service with fast, explainable descriptors
  - Six built-in presets in a registry module
  - Recommended preset based on image descriptors
  - Style tab for preset browsing and applying

## Not in this phase yet

- Before / after compare mode
- Export
- Edit history timeline with undo/redo
- Hugging Face AI assistant
- Morphology-based local cleanup tools
- Feature-descriptor matching or object-level recognition

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
lightcraft_phase4/
├── docs/
│   └── manual.md
├── pyproject.toml
├── README.md
└── src/
    └── lightcraft/
        ├── adjustments.py
        ├── analysis_service.py
        ├── app_window.py
        ├── canvas_view.py
        ├── crop_rotate.py
        ├── document.py
        ├── histogram.py
        ├── image_io.py
        ├── main.py
        ├── models.py
        ├── preset_panel.py
        ├── presets.py
        ├── render_engine.py
        ├── settings.py
        ├── settings_dialog.py
        └── theme.py
```

## Architecture note

This phase intentionally moves scene analysis and presets out of the main window and into separate modules.
That keeps the UI thinner and makes future work easier:

- user presets can extend `PresetRegistry`
- AI ranking can replace or augment the current recommendation rule
- histogram and descriptor analysis can be reused by an AI coach
- future controls can be added to the render engine without changing the left workflow column

## Development note

This repository was prepared in a build environment that did not include a runnable PySide6 GUI runtime, so the code was syntax-checked with `compileall`, but the interactive window behavior still needs to be verified on your machine.
