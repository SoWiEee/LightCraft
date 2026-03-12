# LightCraft Manual

## 1. What this build can do

This build covers Phase 2 of the current SDD.
You can:

- Open one image file
- View it in the main canvas
- Zoom in, zoom out, and fit the image to the window
- Adjust exposure, contrast, white balance, saturation, sharpening, denoise, and shadows
- Watch the histogram update as the preview changes
- Open the Settings dialog and switch between light mode and dark mode
- Replace the application font with any installed font from your computer
- Reset the entire editing session back to the original image
- Reset each adjustment individually

This build does **not** include presets, export, compare mode, or AI yet.

## 2. Launch

Use Python 3.13 with `uv`.

```bash
uv python install 3.13
uv sync
uv run lightcraft
```

## 3. Main UI layout

### Workflow tab

Shows:

- the workflow stages
- image metadata
- current zoom
- render state
- queued preview indicator
- quick buttons for reset and settings

### Adjust tab

Shows:

- live RGB histogram
- adjustment sliders
- numeric values
- reset button per adjustment

## 4. Opening an image

1. Start the application.
2. Choose **File > Open Image...**
3. Select a JPG, JPEG, PNG, BMP, TIFF, or WEBP file.
4. The image will load into the main canvas.
5. Metadata and histogram update automatically.

## 5. Adjustment controls

### Exposure
Brightens or darkens the whole image.

### Contrast
Expands or compresses the difference between dark and bright regions.

### White Balance
Moves the image toward cooler or warmer tones.

### Saturation
Controls how strong the colors appear.

### Sharpening
Increases edge clarity.

### Denoise
Reduces visible noise, especially in darker areas.

### Shadows
Lifts or deepens darker regions while preserving brighter areas as much as possible.

## 6. Settings dialog

Open the settings window from either:

- **Settings > Settings...** in the menu bar
- **Open Settings** button in the Workflow tab

### Appearance tab

- **Theme mode**
  - Follow system
  - Light
  - Dark
- **Installed font**
  - Choose any font available on your local computer
- **Font size**
  - Changes the application UI font size
- **Use default UI font**
  - Resets the custom font choice back to the default

### Behavior tab

- **Preview debounce**
  - Controls how quickly preview rendering reacts while sliders are being dragged
  - Lower values update faster but can cost more CPU

## 7. Reset behavior

### Reset one control
Press the **Reset** button next to that control.

### Reset the whole image
Use **Edit > Reset to Original** or press **Ctrl+R**.
This restores all adjustment values to defaults and rebuilds the preview from the original source buffer.

## 8. Presets

Presets are not implemented in this phase.
They are planned for a later phase. The current built-in preset list target is:

- Auto Clean
- Portrait Soft
- Landscape Clear
- Night Rescue
- Food Warm
- B&W Contrast

## 9. AI features

Hugging Face recommendation and coaching are not implemented in this phase.
They are planned for a later phase after presets and edit-history support are stable.


## Phase 3 manual additions

### UI layout

- **Left sidebar**: workflow progress, editing guidance, metadata, and session actions.
- **Center**: large preview canvas.
- **Right sidebar**: histogram, tone/detail adjustments, and transform controls.

### Crop and rotate

- Use **Transform > Rotate** to straighten a tilted image.
- Use **Crop Left/Top/Right/Bottom** to trim the frame.
- Rotation is applied before crop.
- Crop sliders are percentage-based to keep the Phase 3 implementation simple and non-destructive.

### Planned controls

The right sidebar now includes a reserved section for later controls such as temperature fine-tune, blur, texture, vignette, and color-noise reduction.
