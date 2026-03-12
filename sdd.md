# Software Design Description (SDD) v0.2

## 1. Document Control

- Project Name: Workflow-based Photo Editor for Beginners
- Working Title: LightCraft Desktop
- Document Type: Software Design Description
- Version: 0.2
- Status: Draft 2
- Date: 2026-03-12
- Target Platform: Desktop
- Intended Implementation Language: Python 3.11+
- Primary UI Framework: PySide6
- Image Processing Core: OpenCV + NumPy
- Optional AI Integration: Hugging Face Transformers
- Package Goal: MVP for course final project

## 2. Purpose

This document defines the software design for a workflow-based desktop photo editor targeted at photography beginners. The product goal is to help a novice take one photo from import to shareable output through a guided editing workflow with fast visual feedback, reversible edits, and optional AI assistance.

This version is more implementation-oriented than the first draft. It adds subsystem boundaries, object responsibilities, state transitions, sequence flows, quality attributes, UI structure, acceptance criteria, and fallback behavior so the design can be used as the baseline for task decomposition, sprint planning, and implementation.

## 3. Design Goals

### 3.1 Product Goals

1. Reduce beginner confusion by exposing a fixed workflow:
   Import → Analyze → Correct → Style → Compare → Export
2. Make core editing operations discoverable and reversible.
3. Keep latency low enough for interactive preview on common laptop hardware.
4. Provide explainable AI assistance rather than opaque auto-editing.
5. Preserve the original image through non-destructive editing.

### 3.2 Engineering Goals

1. Keep the MVP feasible within a student course project.
2. Separate UI, image-processing, persistence, and AI layers.
3. Represent edits as parameterized operations so history, undo/redo, and export remain consistent.
4. Keep AI optional and failure-tolerant.
5. Make the architecture extensible for future RAW support, local masking, and batch export.

## 4. Scope

### 4.1 In Scope

1. Load image from local filesystem
2. Show histogram
3. Global adjustments:
   - Exposure
   - Contrast
   - White balance
   - Saturation
   - Sharpening
   - Denoising
   - Shadow recovery
4. Crop
5. Rotate
6. Six curated presets
7. Before/after comparison
8. Export edited image
9. AI preset recommendation
10. AI editing chat coach
11. Edit history
12. Undo/redo
13. Jump from history step to associated control area

### 4.2 Out of Scope for MVP

1. Full catalog management
2. Cloud synchronization
3. Multi-image batch pipeline
4. Professional-grade masking and healing
5. Full RAW parity with commercial editors
6. Plugin marketplace
7. Collaboration features
8. Mobile version

## 5. External Technical Basis

Qt for Python documents the Qt Widgets stack for desktop applications, plus the signal-slot pattern and model/view architecture for synchronized UI state. These are directly relevant to this project’s desktop interaction model and history panel design. citeturn664195search0turn664195search8turn664195search12turn664195search15

OpenCV documents histogram calculation and histogram analysis primitives, which support the histogram panel and basic image-analysis layer used for recommendations and feedback. citeturn664195search1turn664195search19turn664195search16

Hugging Face Transformers documents pipelines for image classification and zero-shot image classification. These are suitable for scene-type inference and preset recommendation. The general pipeline API also supports text generation style tasks for the chat coach integration. citeturn664195search2turn664195search6turn664195search10turn664195search14

RawTherapee documents non-destructive editing, sidecar-based persistence, and a history stack that lets users navigate previous edits. That design informs the history and undo/redo behavior in this project. citeturn664195search3turn664195search7

## 6. Assumptions and Constraints

### 6.1 Assumptions

1. The first release targets JPEG and PNG. RAW is deferred.
2. The project will run on one user machine at a time.
3. AI functionality can be disabled without breaking the editing workflow.
4. Export is single-image only in MVP.
5. The user works on a single active image per session.

### 6.2 Constraints

1. Implementation language must remain Python.
2. The interface should remain simple enough for novice users.
3. The project schedule favors correctness and completeness of core flow over feature breadth.
4. The application should work offline except for optional model download.
5. Memory usage should remain reasonable on a typical student laptop.

## 7. System Context

The system is a local desktop application with optional access to locally cached or remotely downloaded Hugging Face models.

### External Entities

- End user
- Local filesystem
- Optional Hugging Face model hub / cache
- Optional GPU / accelerator
- OS image codec stack used through Python libraries

### Context Interactions

1. User opens an image file.
2. Application decodes the file and initializes an edit session.
3. User edits through sliders, crop tools, preset buttons, and history controls.
4. Processing engine recomputes preview output and histogram.
5. AI service may analyze the image and return preset recommendations and guidance text.
6. User exports final output to disk.

## 8. Quality Attributes

### 8.1 Usability

- Controls must be grouped by workflow stage.
- Presets must have clear names and use cases.
- AI suggestions must include a plain-language explanation.

### 8.2 Performance

- Preview refresh target: under 150 ms for common slider changes on 1920px-long-edge preview images.
- Export target: under 5 seconds for a typical 12 MP JPEG on a student laptop, excluding AI.

### 8.3 Reliability

- The original image must never be modified.
- Failed AI inference must not break manual editing.
- Undo/redo must remain consistent after preset application and parameter edits.

### 8.4 Maintainability

- UI, domain, and infrastructure code must remain separated.
- Editing operations must be represented as explicit data structures, not hidden widget state.

### 8.5 Extensibility

- New adjustments and presets should be addable without redesigning the application shell.
- AI providers should be swappable through an adapter interface.

## 9. High-Level Architecture

The application uses a layered modular architecture with event-driven UI and explicit state models.

### 9.1 Layer Overview

1. Presentation Layer
   - Main window
   - Image canvas
   - Workflow navigator
   - Control sidebar
   - Histogram panel
   - Preset panel
   - History panel
   - AI coach panel
   - Export dialog

2. Application Layer
   - Session controller
   - Workflow controller
   - Command dispatcher
   - History manager
   - Render scheduler
   - Export coordinator
   - AI coordinator

3. Domain Layer
   - Edit session
   - Image document
   - Adjustment state
   - Crop state
   - Preset model
   - History entry
   - Recommendation result
   - Chat message
   - Export profile

4. Infrastructure Layer
   - Image IO adapter
   - OpenCV processing adapter
   - Histogram service
   - EXIF reader
   - Sidecar storage adapter
   - Hugging Face adapter
   - Threading / job execution utilities

### 9.2 Architectural Style

The system is MVC/MVVM-inspired, implemented with Qt signal-slot patterns. UI widgets publish intent. Controllers mutate domain state. Rendering services consume domain state and emit preview images and histogram data. The state object remains the single source of truth.

## 10. Workflow Model

The product centers on a fixed editing workflow for beginners.

1. Import
2. Analyze
3. Correct
4. Style
5. Compare
6. Export

### 10.1 Stage Responsibilities

#### Import
- Select file
- Decode image
- Read metadata
- Initialize edit session
- Compute base preview and histogram

#### Analyze
- Compute quick descriptors:
  - mean luminance
  - luminance distribution
  - basic color cast score
  - saturation estimate
  - edge density
- Run optional AI recommendation
- Present scene guess and recommended preset

#### Correct
- Adjust global correction controls

#### Style
- Apply curated presets
- Fine-tune if desired

#### Compare
- Switch between original and edited image
- Split-view or toggle comparison

#### Export
- Render full-resolution output
- Write output file
- Save optional sidecar

## 11. UI Design

## 11.1 Main Window Layout

Suggested layout:

```text
+----------------------------------------------------------------------------------+
| Menu / Toolbar                                                                   |
+----------------------+-------------------------------------+----------------------+
| Workflow + History   | Image Canvas / Compare View         | Controls / Presets   |
|                      |                                     |                      |
| - Import             |                                     | - Analyze            |
| - Analyze            |                                     | - Adjustments        |
| - Correct            |                                     | - Crop/Rotate        |
| - Style              |                                     | - Presets            |
| - Compare            |                                     | - AI Coach           |
| - Export             |                                     |                      |
+----------------------+-------------------------------------+----------------------+
| Status Bar: file name, zoom, render status, AI status                             |
+----------------------------------------------------------------------------------+
```

## 11.2 Core UI Components

### MainWindow
Top-level frame, menu, toolbar, status bar, child panel composition.

### WorkflowPanel
Lists stages in order. Highlights current stage. Supports quick navigation.

### CanvasView
Displays preview image. Handles zoom, pan, crop overlay, rotation preview, before/after split.

### AdjustmentPanel
Contains grouped sliders for:
- exposure
- contrast
- white balance temperature
- saturation
- sharpening
- denoising
- shadows

### HistogramPanel
Displays RGB or luminance histogram.

### PresetPanel
Shows six preset buttons with labels and descriptions.

### HistoryPanel
Lists edit events in chronological order. Supports click-to-jump and undo/redo.

### AICoachPanel
Shows recommendation summary, explanation, chat history, and prompt input.

### ExportDialog
Lets user choose file name, path, format, quality, and size options.

## 11.3 UI Navigation Rules

1. Import must happen before other stages become active.
2. Compare view is read-only.
3. Export is enabled only when a valid session exists.
4. History click changes the active state snapshot.
5. Crop mode is modal. Sliders are temporarily disabled while crop interaction is active.

## 12. Module Decomposition

## 12.1 Presentation Layer Modules

### MainWindow
Responsibilities:
- Compose UI
- Register actions and shortcuts
- Bind widget signals to controllers

### ImageCanvasWidget
Responsibilities:
- Display preview pixmap
- Support zoom and pan
- Support compare mode
- Support crop interaction overlay

### AdjustmentWidget
Responsibilities:
- Display sliders and numeric values
- Emit parameter change intents
- Reset section to defaults

### PresetWidget
Responsibilities:
- Display six curated presets
- Show preset explanations
- Emit preset selected event

### HistogramWidget
Responsibilities:
- Render histogram data
- Switch histogram channels

### HistoryWidget
Responsibilities:
- Render history entries
- Highlight active state
- Emit jump-to-entry event

### AICoachWidget
Responsibilities:
- Display recommendation
- Handle chat text input
- Show AI service availability

## 12.2 Application Layer Modules

### SessionController
Responsibilities:
- Start and end sessions
- Load image into domain objects
- Broadcast session changes

### WorkflowController
Responsibilities:
- Manage current workflow stage
- Gate UI transitions when needed

### AdjustmentController
Responsibilities:
- Handle slider and crop/rotate actions
- Create commands
- Submit commands to history manager

### HistoryManager
Responsibilities:
- Maintain command stack
- Maintain materialized state snapshots
- Support undo, redo, and jump

### RenderScheduler
Responsibilities:
- Debounce frequent UI changes
- Dispatch preview renders off main UI thread
- Drop obsolete preview jobs

### ExportCoordinator
Responsibilities:
- Validate export settings
- Trigger full-resolution render
- Save image and optional sidecar

### AICoordinator
Responsibilities:
- Trigger scene analysis
- Request preset recommendation
- Handle chat coach requests
- Fallback gracefully when AI unavailable

## 12.3 Domain Layer Modules

### EditSession
Fields:
- session_id
- source_image_path
- source_metadata
- original_image_ref
- current_state
- history
- ai_state
- export_profiles

### AdjustmentState
Fields:
- exposure: float
- contrast: float
- white_balance_temp: float
- saturation: float
- sharpening: float
- denoise: float
- shadows: float

### CropState
Fields:
- enabled: bool
- rect_norm: [x, y, w, h]
- rotation_deg: float
- aspect_lock: optional string

### Preset
Fields:
- preset_id
- name
- description
- target_scenarios
- parameter_overrides

### HistoryEntry
Fields:
- entry_id
- timestamp
- action_type
- label
- delta
- snapshot_ref
- target_panel

### AIState
Fields:
- availability
- model_info
- last_scene_guess
- recommendation
- chat_messages
- error

### ExportProfile
Fields:
- format
- quality
- resize_mode
- long_edge
- output_path

## 12.4 Infrastructure Layer Modules

### ImageIOAdapter
- load JPEG / PNG
- save JPEG / PNG
- convert between OpenCV arrays and Qt image objects

### OpenCVProcessingAdapter
- apply full edit pipeline
- calculate intermediate images
- expose deterministic pure functions where possible

### HistogramService
- compute luminance histogram
- compute RGB histograms
- normalize for display

### MetadataService
- extract EXIF when available

### SidecarRepository
- save and load session metadata and edit state as JSON sidecar

### HuggingFaceAdapter
- initialize pipelines
- run scene-type classification or zero-shot classification
- run chat-coach text generation or LLM calls
- expose timeout and fallback behavior

## 13. Data Model

## 13.1 Core State Snapshot

```json
{
  "session_id": "uuid",
  "source_image_path": "path/to/image.jpg",
  "adjustments": {
    "exposure": 0.0,
    "contrast": 0.0,
    "white_balance_temp": 0.0,
    "saturation": 0.0,
    "sharpening": 0.0,
    "denoise": 0.0,
    "shadows": 0.0
  },
  "crop": {
    "enabled": false,
    "rect_norm": [0.0, 0.0, 1.0, 1.0],
    "rotation_deg": 0.0,
    "aspect_lock": null
  },
  "applied_preset_id": null,
  "history_pointer": 0
}
```

## 13.2 History Storage Strategy

The system uses a hybrid strategy:

1. Command log for semantic actions
2. State snapshots for fast jump and restore

Reason:
- Pure command replay is simple but slow when history grows.
- Pure snapshots are easy but memory-heavy.
- Hybrid storage balances speed and simplicity.

### Snapshot Policy

- Create full snapshot after:
  - image import
  - preset apply
  - crop commit
  - export settings save
  - every N slider commits, default N = 5
- Create command entry for every committed user action

## 13.3 Slider Commit Policy

This is critical for usability and history cleanliness.

- During drag:
  - update preview live
  - do not append history on every tick
- On slider release:
  - create one history entry
  - merge intermediate values into final delta

This avoids history spam and improves undo behavior.

## 14. Preset Design

## 14.1 Preset Principles

1. Six presets only
2. Each preset must correspond to a beginner-understandable scenario
3. Presets are parameter bundles, not separate code paths
4. Presets remain editable after application

## 14.2 Proposed Presets

1. Everyday Clean
   - for casual daylight photos
2. Portrait Soft
   - gentler contrast and color
3. Landscape Pop
   - stronger contrast, color, and moderate sharpening
4. Night Rescue
   - shadow lift, denoise, mild contrast compensation
5. Food Warm
   - warmer white balance, mild saturation boost
6. B&W Contrast
   - monochrome conversion preset with contrast emphasis

## 14.3 Preset Data Example

```json
{
  "preset_id": "night_rescue",
  "name": "Night Rescue",
  "description": "Lift dark areas and reduce visible noise for low-light photos.",
  "target_scenarios": ["night", "indoor low light", "street at night"],
  "parameter_overrides": {
    "exposure": 0.25,
    "contrast": 0.05,
    "white_balance_temp": 0.03,
    "saturation": -0.03,
    "sharpening": 0.08,
    "denoise": 0.30,
    "shadows": 0.35
  }
}
```

## 15. Image Processing Pipeline

## 15.1 Processing Order

The preview and export pipeline should remain deterministic.

Recommended order:

1. Decode source image
2. Crop and rotate geometry transform
3. White balance
4. Exposure
5. Contrast
6. Shadow recovery
7. Saturation
8. Denoise
9. Sharpen
10. Histogram computation for rendered preview

Reasoning:
- Geometry first simplifies downstream processing.
- Denoise before sharpen prevents sharpening noise.
- Histogram should reflect current preview state.

## 15.2 Parameter Definitions

Initial proposed normalized ranges:

| Parameter | Internal Range | UI Default | UI Step | Notes |
|---|---:|---:|---:|---|
| Exposure | -1.0 to +1.0 | 0.0 | 0.01 | mapped to brightness/exposure transform |
| Contrast | -1.0 to +1.0 | 0.0 | 0.01 | linear or curve-based |
| White Balance Temp | -1.0 to +1.0 | 0.0 | 0.01 | cool to warm bias |
| Saturation | -1.0 to +1.0 | 0.0 | 0.01 | HSV / HSL based |
| Sharpening | 0.0 to 1.0 | 0.0 | 0.01 | unsharp mask strength |
| Denoise | 0.0 to 1.0 | 0.0 | 0.01 | bilateral / fastNlMeans style |
| Shadows | 0.0 to 1.0 | 0.0 | 0.01 | shadow lift only |

These ranges are implementation defaults for MVP, not photographic absolutes. They can be remapped to more user-friendly labels later.

## 15.3 Preview Strategy

To keep UI responsive:

1. Maintain a preview-resolution working image.
2. Render preview from scaled source.
3. Render export from original resolution.
4. Recompute histogram from preview render unless full-quality export histogram is explicitly needed.

## 16. AI Integration Design

## 16.1 AI Feature Scope

### AI Preset Recommendation
Goal:
- Suggest one to three presets based on image content and simple descriptors.

Inputs:
- preview image
- optional descriptors
- candidate preset labels

Outputs:
- ranked presets
- confidence scores
- explanation text

### AI Editing Chat Coach
Goal:
- answer beginner questions
- explain what a slider does
- explain why a preset is suggested
- recommend next action

Inputs:
- current state summary
- selected preset
- image descriptors
- user chat prompt

Outputs:
- concise coaching response
- optional suggested UI action

## 16.2 AI Architecture

The AI subsystem has two layers:

1. Recommendation Engine
   - zero-shot image classification or standard image classification
   - rule mapping from scene labels to presets

2. Coach Engine
   - local or remote language model through an adapter
   - grounded on current edit state and preset descriptions

## 16.3 Recommendation Strategy

### Primary Strategy
- Use Hugging Face image or zero-shot image classification to infer scene categories such as:
  - portrait
  - landscape
  - food
  - night
  - indoor
  - monochrome-friendly

### Mapping Strategy
Map inferred labels to preset candidates through a small deterministic rule table.

Example:

| Scene Label | Recommended Preset |
|---|---|
| portrait | Portrait Soft |
| landscape | Landscape Pop |
| indoor low light | Night Rescue |
| food | Food Warm |
| casual daylight | Everyday Clean |

### Fallback Strategy
If classification fails:
1. use heuristic descriptors
2. recommend Everyday Clean as safe default
3. explain that recommendation confidence is low

## 16.4 Chat Coach Guardrails

The chat coach must:
- answer only about editing guidance, current image state, and available app features
- avoid pretending to have made changes unless the user explicitly clicks a control
- explain uncertainty
- provide short answers suited to beginners

## 16.5 AI Failure Handling

Possible failures:
- no model downloaded
- slow inference
- unsupported hardware
- pipeline exception
- no internet during first model fetch

Required behavior:
- show AI unavailable state
- keep all manual tools active
- log error internally
- allow retry

## 17. Concurrency and Responsiveness

## 17.1 Threading Principles

1. UI thread must remain reserved for widget interaction and image display updates.
2. Preview rendering runs in worker threads.
3. AI inference runs in separate worker threads or tasks.
4. Only the latest render request should update the UI.

Qt examples and guidance on signals/slots and threaded task patterns support this event-driven approach. citeturn664195search4turn664195search12

## 17.2 Render Job Policy

- debounce slider change bursts with short delay, e.g. 30 to 60 ms
- cancel or ignore obsolete jobs
- only commit final result with matching generation token

## 18. Persistence Design

## 18.1 Files

1. Original image file
2. Optional sidecar JSON file
3. Exported output image

### Sidecar Example

`image.jpg.lightcraft.json`

## 18.2 Sidecar Contents

- image path
- edit state
- preset ID
- history summary
- export presets
- app version

This follows the non-destructive idea used by tools that store edits separately from the source image. citeturn664195search7turn664195search3

## 19. Error Handling

## 19.1 Import Errors

- unsupported format
- corrupted file
- permission denied

Behavior:
- show clear error
- keep previous session open if one exists

## 19.2 Render Errors

- invalid parameter state
- OpenCV failure

Behavior:
- revert to last good preview
- surface friendly error in status bar

## 19.3 Export Errors

- invalid path
- permission denied
- codec write failure

Behavior:
- preserve session
- show actionable message

## 19.4 AI Errors

- model unavailable
- inference timeout
- runtime exception

Behavior:
- degrade to non-AI flow
- preserve edit session

## 20. Security and Privacy

1. All editing works locally by default.
2. AI model download may access external network only if the user enables AI and the model is not cached.
3. No image upload is required for the base product.
4. The app should clearly indicate if any future cloud AI mode is introduced.

## 21. Sequence Flows

## 21.1 Import Image

```text
User
 -> MainWindow: Open file
 -> SessionController: load_image(path)
 -> ImageIOAdapter: decode(path)
 -> MetadataService: extract(path)
 -> EditSession: initialize()
 -> HistogramService: compute(original preview)
 -> RenderScheduler: request preview
 -> MainWindow: render initial preview and histogram
```

## 21.2 Adjust Slider

```text
User
 -> AdjustmentWidget: drag exposure slider
 -> AdjustmentController: update transient state
 -> RenderScheduler: request preview
 -> OpenCVProcessingAdapter: render preview
 -> MainWindow: update canvas and histogram

User
 -> AdjustmentWidget: release slider
 -> HistoryManager: commit command
 -> EditSession: update durable state
 -> HistoryWidget: append entry
```

## 21.3 Apply Preset

```text
User
 -> PresetWidget: select preset
 -> AdjustmentController: apply preset parameters
 -> HistoryManager: commit preset command
 -> RenderScheduler: request preview
 -> MainWindow: update preview
 -> AICoachWidget: optionally explain why preset fits the image
```

## 21.4 Jump to History Step

```text
User
 -> HistoryWidget: select entry
 -> HistoryManager: restore snapshot
 -> SessionController: publish state changed
 -> MainWindow: update controls, preview, histogram
 -> WorkflowPanel: focus target panel
```

## 21.5 Export Image

```text
User
 -> ExportDialog: confirm settings
 -> ExportCoordinator: validate settings
 -> OpenCVProcessingAdapter: render full resolution
 -> ImageIOAdapter: save output
 -> SidecarRepository: save session metadata
 -> MainWindow: show export success
```

## 21.6 AI Recommendation

```text
SessionController
 -> AICoordinator: analyze image
 -> HuggingFaceAdapter: classify scene
 -> AICoordinator: map scene to presets
 -> MainWindow: show ranked suggestions and explanation
```

## 22. Class Design Sketch

```text
MainWindow
 ├─ WorkflowPanel
 ├─ ImageCanvasWidget
 ├─ AdjustmentWidget
 ├─ HistogramWidget
 ├─ PresetWidget
 ├─ HistoryWidget
 ├─ AICoachWidget
 └─ ExportDialog

SessionController
 ├─ WorkflowController
 ├─ AdjustmentController
 ├─ HistoryManager
 ├─ RenderScheduler
 ├─ ExportCoordinator
 └─ AICoordinator

AICoordinator
 └─ HuggingFaceAdapter

RenderScheduler
 └─ OpenCVProcessingAdapter

ExportCoordinator
 ├─ OpenCVProcessingAdapter
 ├─ ImageIOAdapter
 └─ SidecarRepository
```

## 23. State Machine

## 23.1 Session State

```text
NoSession
 -> Loading
 -> Ready
 -> Editing
 -> Exporting
 -> Ready
 -> Closed
```

### Rules
- Loading failure returns to NoSession.
- Export failure returns to Ready.
- AI busy is a sub-state overlay, not a separate session state.

## 23.2 Crop Mode State

```text
Idle
 -> CropActive
 -> CropPreview
 -> CropCommitted
 -> Idle
```

Cancel path:
`CropActive -> Idle`

## 24. Acceptance Criteria

## 24.1 Functional Acceptance Criteria

1. User can open a valid JPEG or PNG and see it in the canvas.
2. Histogram updates after image load.
3. Changing each slider updates the preview.
4. Releasing a slider creates one history entry.
5. Crop and rotate modify preview and export output consistently.
6. Six presets are available and selectable.
7. Applying a preset creates a history entry.
8. Before/after comparison shows original and current result.
9. Export writes a valid image file.
10. Undo and redo work across slider edits, crop, rotate, and preset application.
11. Clicking a history entry restores the matching state.
12. If AI is available, the app shows preset suggestions.
13. If AI fails, manual editing still works.

## 24.2 Non-Functional Acceptance Criteria

1. Preview remains interactive during slider drag on a test laptop.
2. App does not overwrite original files.
3. Session survives AI errors without restart.
4. Sidecar save and load reproduces the same visible state.

## 25. Testing Strategy

## 25.1 Unit Tests

- parameter mapping
- preset application logic
- history merge policy
- sidecar serialization / deserialization
- recommendation mapping rules

## 25.2 Integration Tests

- load → edit → export flow
- history jump restoration
- crop + rotate + export consistency
- AI adapter fallback flow

## 25.3 Manual UI Tests

- slider responsiveness
- compare toggle correctness
- crop overlay usability
- invalid export path behavior

## 25.4 Evaluation Tests

Because this is a beginner-focused editor, at least one usability evaluation should be included:
- recruit 5 to 10 novice users
- ask them to improve a photo with and without preset suggestions
- measure task completion time, subjective confidence, and output satisfaction

## 26. Technology Stack

- Python 3.11+
- PySide6
- OpenCV
- NumPy
- Pillow if needed for image bridging
- transformers
- torch or other backend required by chosen model
- pytest
- optional pydantic / dataclasses for state schemas

## 27. Project Structure Proposal

```text
lightcraft/
  app/
    main.py
    ui/
      main_window.py
      widgets/
        canvas.py
        workflow_panel.py
        adjustments.py
        histogram.py
        presets.py
        history.py
        ai_coach.py
        export_dialog.py
    controllers/
      session_controller.py
      workflow_controller.py
      adjustment_controller.py
      history_manager.py
      render_scheduler.py
      export_coordinator.py
      ai_coordinator.py
    domain/
      session.py
      state.py
      presets.py
      history.py
      export.py
      ai_models.py
    services/
      image_io.py
      processing.py
      histogram_service.py
      metadata_service.py
      sidecar_repository.py
      hf_adapter.py
    tests/
  docs/
    spec.md
    sdd.md
  README.md
```

## 28. Open Issues

1. Final choice of AI model for local inference
2. Exact preview cache policy
3. Histogram display mode: RGB only or RGB + luminance
4. Whether B&W Contrast is implemented as a preset only or as a reusable monochrome mode
5. Whether sidecar autosave is enabled by default
6. Whether crop aspect presets are included in MVP

## 29. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---:|---|
| AI model too slow | High | Medium | make AI optional, use fallback heuristics |
| Preview rendering lags | High | Medium | render from preview-sized image, debounce jobs |
| Undo/redo bugs | High | Medium | use explicit command model and snapshot checkpoints |
| Crop UI complexity | Medium | Medium | keep crop tool simple and modal |
| Feature creep | High | High | freeze MVP scope and postpone RAW/masking/healing |

## 30. MVP Cutline

### Must Have
- load image
- histogram
- global adjustments
- crop/rotate
- six presets
- compare mode
- export
- history with undo/redo
- history jump
- sidecar save/load
- AI recommendation fallback path

### Should Have
- AI chat coach
- EXIF summary
- RGB/luminance histogram switch

### Could Have
- RAW input
- aspect-ratio crop presets
- export presets
- keyboard shortcut help

## 31. Implementation Plan Hooks

Recommended implementation order:

1. image load + canvas + histogram
2. adjustment state + processing pipeline
3. preview rendering loop
4. history and undo/redo
5. crop/rotate
6. presets
7. export
8. sidecar persistence
9. AI recommendation
10. AI chat coach

## 32. Traceability to Specification

| Spec Feature | SDD Coverage |
|---|---|
| Load Image | Sections 10, 12, 21, 24 |
| Histogram | Sections 11, 12, 15, 24 |
| Global Adjustments | Sections 11, 12, 15, 24 |
| Crop / Rotate | Sections 11, 12, 21, 24 |
| Six Presets | Sections 14, 21, 24 |
| Before / After | Sections 10, 11, 24 |
| Export | Sections 18, 21, 24 |
| AI Model Assistance | Sections 16, 19, 21, 24 |
| Edit History | Sections 13, 21, 24 |

## 33. References

1. Qt for Python Widgets documentation
2. Qt model/view documentation
3. Qt signal-slot guidance and examples
4. OpenCV histogram tutorials
5. Hugging Face Transformers pipelines documentation
6. Hugging Face zero-shot image classification guide
7. RawTherapee RawPedia non-destructive editing and history documentation

