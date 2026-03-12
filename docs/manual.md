# LightCraft Manual

## 1. What this build can do

This build covers Phase 4 of the current workflow editor plan.
You can:

- Open one image file
- View it in the main canvas
- Zoom in, zoom out, and fit the image to the window
- Adjust exposure, contrast, white balance, saturation, sharpening, denoise, and shadows
- Rotate and crop the image
- Watch the histogram update as the preview changes
- Open the Settings dialog and switch between light mode and dark mode
- Replace the application font with any installed font from your computer
- See image-analysis guidance in the left workflow column
- Browse and apply six built-in presets
- Let the app recommend a preset based on image descriptors
- Reset the entire editing session back to the original image
- Reset each adjustment individually

This build does **not** include compare mode, export, edit history, or Hugging Face AI yet.

## 2. Launch

Use Python 3.13 with `uv`.

```bash
uv python install 3.13
uv sync
uv run lightcraft
```

## 3. Main UI layout

### Left column

Shows:

- workflow stages
- workflow-specific guidance
- scene-analysis summary
- image metadata
- current preset tag
- quick buttons for recommended preset, reset, and settings

### Center column

Shows:

- the main preview canvas
- zoom and fit interactions

### Right column

Shows:

- **Develop** tab: histogram and technical correction controls
- **Transform** tab: rotation and crop controls
- **Style** tab: presets and recommendation text

## 4. Opening an image

1. Start the application.
2. Choose **File > Open Image...**
3. Select a JPG, JPEG, PNG, BMP, TIFF, or WEBP file.
4. The image will load into the main canvas.
5. Metadata, histogram, analysis text, and preset recommendation update automatically.

## 5. Scene analysis and guidance

The application computes lightweight descriptors from the current preview image:

- mean brightness
- contrast spread
- saturation level
- warm/cool tendency
- edge density

These descriptors feed two user-facing outputs:

1. a short analysis summary in the left column
2. a preset recommendation in the Style tab and the left column button

This is intentionally explainable. It is a rule-based analysis layer, not a black-box AI model.

## 6. Adjustment controls

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

## 7. Transform controls

### Rotate
Straightens a tilted image.

### Crop Left / Top / Right / Bottom
Trims the frame with percentage-based controls.
Rotation is applied before crop.

## 8. Presets

This phase includes six built-in presets:

- **Auto Clean**
  - general correction pass for ordinary images
- **Portrait Soft**
  - softer portrait rendering with lighter warmth and more denoise
- **Landscape Clear**
  - extra contrast, saturation, and sharpening for detailed scenes
- **Night Rescue**
  - raises brightness and shadows while controlling noise
- **Food Warm**
  - warmer, richer indoor and food look
- **B&W Contrast**
  - monochrome high-contrast interpretation

### How to use

1. Correct obvious issues first in the Develop and Transform tabs.
2. Open the **Style** tab.
3. Read the recommendation.
4. Apply a preset.
5. Fine-tune the sliders again if needed.

### Important limitation

Presets set several controls at once and remain fully editable.
The current system stores only the **active preset tag**, not a user-editable preset file.
That is intentional. User-defined presets should be added after edit history is stable.

## 9. Settings dialog

Open the settings window from either:

- **Settings > Settings...** in the menu bar
- **Open Settings** button in the left workflow column

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

## 10. Reset behavior

### Reset one control
Press the **Reset** button next to that control.

### Reset the whole image
Use **Edit > Reset to Original** or press **Ctrl+R**.
This restores all adjustment and transform values to defaults and rebuilds the preview from the original source buffer.

## 11. What comes next

The most natural next milestones are:

- compare mode
- export flow
- edit history with undo/redo and jump-to-step
- Hugging Face integration for preset ranking and coaching
- optional morphology and feature-analysis tools for advanced guidance
