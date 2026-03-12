from __future__ import annotations

from dataclasses import dataclass

from .analysis_service import ImageAnalysis
from .models import EditState


@dataclass(frozen=True, slots=True)
class PresetDefinition:
    preset_id: str
    name: str
    summary: str
    when_to_use: str
    settings: dict[str, float]


class PresetRegistry:
    def __init__(self) -> None:
        self._presets = [
            PresetDefinition(
                preset_id="auto_clean",
                name="Auto Clean",
                summary="Small correction pass for ordinary photos.",
                when_to_use="General images that need a cleaner technical baseline.",
                settings={
                    "exposure": 0.2,
                    "contrast": 8.0,
                    "white_balance_temp": 0.0,
                    "saturation": 6.0,
                    "sharpening": 8.0,
                    "denoise": 4.0,
                    "shadows": 8.0,
                },
            ),
            PresetDefinition(
                preset_id="portrait_soft",
                name="Portrait Soft",
                summary="Gentle portrait look with softer detail and moderate warmth.",
                when_to_use="People photos and close subjects where skin should stay smooth.",
                settings={
                    "exposure": 0.25,
                    "contrast": 4.0,
                    "white_balance_temp": 10.0,
                    "saturation": 4.0,
                    "sharpening": 2.0,
                    "denoise": 10.0,
                    "shadows": 12.0,
                },
            ),
            PresetDefinition(
                preset_id="landscape_clear",
                name="Landscape Clear",
                summary="Clear outdoor look with extra structure and color.",
                when_to_use="Scenery, city views, and travel photos with detail.",
                settings={
                    "exposure": 0.15,
                    "contrast": 14.0,
                    "white_balance_temp": -4.0,
                    "saturation": 12.0,
                    "sharpening": 16.0,
                    "denoise": 2.0,
                    "shadows": 10.0,
                },
            ),
            PresetDefinition(
                preset_id="night_rescue",
                name="Night Rescue",
                summary="Brightens dark frames while controlling noise.",
                when_to_use="Night scenes and dim indoor photos.",
                settings={
                    "exposure": 0.7,
                    "contrast": 6.0,
                    "white_balance_temp": 2.0,
                    "saturation": 5.0,
                    "sharpening": 4.0,
                    "denoise": 18.0,
                    "shadows": 22.0,
                },
            ),
            PresetDefinition(
                preset_id="food_warm",
                name="Food Warm",
                summary="Warm, appetizing color for dishes and indoor table shots.",
                when_to_use="Food, cafe, and warm ambient indoor scenes.",
                settings={
                    "exposure": 0.2,
                    "contrast": 10.0,
                    "white_balance_temp": 14.0,
                    "saturation": 10.0,
                    "sharpening": 8.0,
                    "denoise": 4.0,
                    "shadows": 6.0,
                },
            ),
            PresetDefinition(
                preset_id="bw_contrast",
                name="B&W Contrast",
                summary="High-contrast monochrome interpretation.",
                when_to_use="Graphic scenes, architecture, and mood-driven edits.",
                settings={
                    "exposure": 0.1,
                    "contrast": 22.0,
                    "white_balance_temp": 0.0,
                    "saturation": -100.0,
                    "sharpening": 10.0,
                    "denoise": 3.0,
                    "shadows": 8.0,
                },
            ),
        ]
        self._by_id = {preset.preset_id: preset for preset in self._presets}

    def all(self) -> list[PresetDefinition]:
        return list(self._presets)

    def get(self, preset_id: str) -> PresetDefinition | None:
        return self._by_id.get(preset_id)

    def apply(self, edit_state: EditState, preset_id: str) -> EditState:
        preset = self.get(preset_id)
        if preset is None:
            return edit_state
        for key, value in preset.settings.items():
            setattr(edit_state, key, value)
        edit_state.applied_preset_id = preset_id
        return edit_state

    def recommend(self, analysis: ImageAnalysis | None) -> PresetDefinition | None:
        if analysis is None:
            return self.get("auto_clean")
        if analysis.is_dark and analysis.is_low_contrast:
            return self.get("night_rescue")
        if analysis.scene_hint == "Food / indoor warm scene":
            return self.get("food_warm")
        if analysis.scene_hint == "Landscape / outdoor detail":
            return self.get("landscape_clear")
        if analysis.scene_hint == "Portrait / soft subject":
            return self.get("portrait_soft")
        if not analysis.is_colorful and analysis.contrast_std > 0.22:
            return self.get("bw_contrast")
        return self.get("auto_clean")
