# LightCraft Manual

## 1. Scope of this build

This build implements **Phase 1** only.

Available features:
- Load one image from disk
- Scrollable canvas
- Zoom in / zoom out / fit to window
- Reset to original
- Non-destructive source-image session model
- File and image metadata panel

Not yet implemented:
- Histogram
- Exposure / contrast / white balance / saturation / sharpening / denoise / shadows
- Crop / rotate
- Before / after compare
- Export
- Presets
- AI recommendation
- Edit history

## 2. Supported formats

- JPEG
- PNG
- Any format OpenCV can decode in the local environment

## 3. Launch

```bash
uv sync
uv run lightcraft
```

## 4. Basic usage

### Open an image

Use one of these:
- `File -> Open Image...`
- `Ctrl+O`

### Reset the session

Use:
- `Edit -> Reset to Original`
- `Ctrl+R`

### Zoom controls

Use:
- `View -> Zoom In`
- `View -> Zoom Out`
- `View -> Fit to Window`

## 5. Workflow panel

The left panel is intentionally present in Phase 1 even though most stages are placeholders.
This keeps the project aligned with the SDD and avoids redesigning the UI later.

Workflow stages shown in the UI:
1. Load
2. Analyze
3. Adjust
4. Style
5. Compare
6. Export

## 6. Metadata panel

The metadata panel currently shows:
- file name
- full path
- pixel dimensions
- number of channels
- file size
- current zoom
- render state

This is enough for Phase 1 verification and debugging.

## 7. Presets

Phase 1 does **not** implement presets yet.
The intended preset set for later phases is documented here so UI labels remain stable.

Planned presets:
1. Auto Starter
2. Landscape Pop
3. Portrait Soft
4. Night Clean
5. Food Warm
6. Monochrome Contrast

These names are placeholders in Phase 1 and are **not selectable** yet.

## 8. Troubleshooting

### App opens but no image is shown
- Confirm the selected file is a valid image.
- Confirm the file is not locked by another process.
- Confirm OpenCV can decode the format in your environment.

### Reset appears to do nothing
This is expected in Phase 1 because no adjustments exist yet.
The reset command still verifies that the source buffer remains untouched and the preview is rebuilt from source.

### Very large image feels slow
Phase 1 renders full-resolution previews. Later phases should introduce preview downscaling and render debouncing.
