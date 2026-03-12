# LightCraft Phase 5+ History

LightCraft is a workflow-based desktop photo editor for beginner photographers.
This build adds edit history and time-travel navigation, moves image metadata into a dedicated File tab, and introduces UI language switching for English and Traditional Chinese.

## Implemented in this build

- Single-image session with immutable source buffer
- Non-destructive preview re-render from `source_image + EditState`
- Scrollable image canvas with zoom in/out and fit-to-window
- Three-column workflow UI
- Left panel split into:
  - **Workflow** tab for guidance, analysis, compare, and history
  - **File** tab for image metadata and session actions
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
  - UI language: English / Traditional Chinese
  - Installed font selection from local computer fonts
  - UI font size
  - Preview debounce interval
- Scene analysis service with fast, explainable descriptors
- Six built-in presets in a registry module
- Recommended preset based on image descriptors
- Compare modes:
  - Edited only
  - Split compare
  - Toggle compare
- Export flow:
  - JPEG / PNG / WEBP / BMP / TIFF
  - JPEG quality option
  - PNG compression option
  - Unicode-safe file writing via encoded buffer output
- Edit history / time travel:
  - commit-based history entries
  - Undo / Redo
  - jump directly to an earlier committed state
  - future-branch pruning after time travel

## Not in this build yet

- Hugging Face AI assistant
- Morphology-based local cleanup tools
- Feature-descriptor matching or object-level recognition
- Batch export
- User-defined preset files
- Qt Linguist `.ts/.qm` localization pipeline

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
lightcraft/
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
        ├── compare_view.py
        ├── crop_rotate.py
        ├── document.py
        ├── export_dialog.py
        ├── export_service.py
        ├── histogram.py
        ├── history.py
        ├── i18n.py
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

This build keeps the app maintainable by isolating responsibilities:

- `RenderEngine` owns pixel processing
- `ImageDocument` owns source buffer, preview buffer, metadata, and current edit state
- `HistoryManager` owns committed edit-state snapshots and time travel
- `CompareView` owns compare presentation and zoom synchronization
- `ExportDialog` owns export UI choices
- `ExportService` owns file encoding and disk write behavior
- `PresetRegistry` owns preset definitions and recommendation
- `Localizer` owns language selection and UI string lookup

That separation matters because future work stays localized. A Hugging Face scene classifier can attach to the analysis/preset boundary. Batch export can extend `ExportService`. Richer localization can replace the string catalog with Qt translation files without rewriting the whole window.

## Development note

This repository was prepared in a build environment that did not include a runnable PySide6 GUI runtime, so the code was syntax-checked with `compileall`, but the interactive window behavior still needs to be verified on your machine.
