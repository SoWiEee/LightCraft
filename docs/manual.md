# LightCraft Manual

## 1. What this build can do

This build extends the workflow editor with two major additions:

- **Edit History and Time Travel**
- **UI language switching for English and Traditional Chinese**

You can now:

- Open one image file
- View it in the main canvas
- Zoom in, zoom out, and fit the image to the window
- Adjust exposure, contrast, white balance, saturation, sharpening, denoise, and shadows
- Rotate and crop the image
- Watch the histogram update as the preview changes
- Open the Settings dialog and switch theme mode
- Change UI language between English and Traditional Chinese
- Replace the application font with any installed font from your computer
- See image-analysis guidance in the left Workflow tab
- Browse image metadata in the left File tab
- Browse and apply six built-in presets
- Let the app recommend a preset based on image descriptors
- Compare original and edited output using split or toggle mode
- Export the current edited result to common image formats
- Use Undo / Redo on committed edit states
- Jump directly to an earlier committed state to time-travel through the edit
- Reset the entire editing session back to the original image
- Reset each adjustment individually

This build still does **not** include Hugging Face AI, morphology-based local cleanup, or object-level recognition.

## 2. Launch

Use Python 3.13 with `uv`.

```bash
uv python install 3.13
uv sync
uv run lightcraft
```

## 3. Main UI layout

### Left column

The left column now contains two tabs.

#### Workflow tab

Shows:

- workflow stages
- workflow-specific guidance
- scene-analysis summary
- compare tips and compare buttons
- edit history list
- undo / redo / jump controls

#### File tab

Shows:

- image metadata
- current render state
- queued preview count
- current preset / compare state
- file/session actions such as open, reset, settings, export

### Center column

Shows:

- the main preview canvas
- edited-only mode
- split compare mode
- toggle compare mode
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
4. The image loads into the main canvas.
5. Metadata, histogram, analysis text, preset recommendation, and history baseline update automatically.

The first history entry is the loaded original state.

## 5. Scene analysis and guidance

The application computes lightweight descriptors from the current preview image:

- mean brightness
- contrast spread
- saturation level
- warm/cool tendency
- edge density

These descriptors feed two user-facing outputs:

1. a short analysis summary in the Workflow tab
2. a preset recommendation in the Style tab and the Workflow tab button

This is intentionally explainable. It is a rule-based analysis layer, not a black-box AI model.

## 6. Compare mode

Compare belongs late in the workflow for a reason. You should use it after adjustment and style decisions, then again before export.

### Edited only

Shows the edited result only. This is the fastest mode while actively changing sliders.

### Split compare

Shows original and edited images side by side. Zoom is synchronized between both views.
Use this to catch over-sharpening, over-saturation, crushed shadows, or bad crop decisions.

### Toggle compare

Shows one image at a time without changing zoom.
Press **Tab** or use the **Swap Original / Edited** button to flip between the original and edited image.
Use this when you want to focus on one frame position instead of reading two panels at once.

## 7. Edit History and Time Travel

History records **committed** edit states.
A slider drag can trigger preview updates, but a history entry is created when the adjustment is committed.
This keeps the timeline readable.

### What creates a history entry

- loading a new image
- releasing an adjustment slider
- releasing a transform slider
- applying a preset
- resetting the edit

### Undo / Redo

Use any of these:

- **Edit > Undo**
- **Edit > Redo**
- keyboard shortcuts such as **Ctrl+Z** and **Ctrl+Shift+Z / Ctrl+Y** depending on platform
- buttons inside the Workflow tab

### Jump to Selected

Select any history entry in the list and press **Jump to Selected**.
The app restores that exact committed `EditState`, re-renders the preview, and syncs the controls.

### Clear Future Branch

If you time-travel backward and want to discard later states, use **Clear Future Branch**.
This keeps the history linear again.

## 8. Adjustment controls

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

## 9. Transform controls

### Rotate
Straightens a tilted image.

### Crop Left / Top / Right / Bottom
Trims the frame with percentage-based controls.
Rotation is applied before crop.

## 10. Presets

This build includes six built-in presets:

- **Auto Clean**
- **Portrait Soft**
- **Landscape Clear**
- **Night Rescue**
- **Food Warm**
- **B&W Contrast**

### How to use

1. Correct obvious issues first in the Develop and Transform tabs.
2. Open the **Style** tab.
3. Read the recommendation.
4. Apply a preset.
5. Fine-tune the sliders again if needed.
6. Switch to compare mode before exporting.

## 11. Export

Open export from either:

- **File > Export...**
- **Export Current Edit** button in the File tab

### Supported formats

- JPEG
- PNG
- WEBP
- BMP
- TIFF

### Export options

- output format
- JPEG quality
- PNG compression
- preserve alpha when supported

### Important limitation

This export flow writes the **current edited render**.
There is no export preset system, no resize pipeline, and no batch export yet.

## 12. Settings dialog

Open the settings window from either:

- **Settings > Settings...** in the menu bar
- **Open Settings** button in the File tab

### Appearance tab

- **Theme mode**
  - Follow system
  - Light
  - Dark
- **Language**
  - English
  - Traditional Chinese
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

## 13. Reset behavior

### Reset one control
Press the **Reset** button next to that control.

### Reset the whole image
Use **Edit > Reset to Original** or press **Ctrl+R**.
This restores all adjustment and transform values to defaults and rebuilds the preview from the original source buffer.
A reset is also stored as a new history entry.

## 14. Notes on localization

This build uses an in-app string catalog for English and Traditional Chinese.
That keeps packaging simple.
A future release can move to Qt Linguist and translation files if you need a more formal localization workflow.

## 15. What comes next

The most natural next milestones are:

- Hugging Face scene classification and coaching
- richer feature extraction for better preset ranking
- optional morphology and local-mask refinement tools
- export profiles and batch export
- interactive crop overlay
- user-defined preset files
