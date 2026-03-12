from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class ImageAnalysis:
    mean_luma: float
    contrast_std: float
    saturation_mean: float
    warm_balance: float
    edge_density: float
    is_dark: bool
    is_low_contrast: bool
    is_colorful: bool
    is_warm: bool
    is_detailed: bool
    scene_hint: str
    guidance: str


class AnalysisService:
    """Fast, explainable image descriptors for workflow guidance and preset suggestion."""

    def analyze(self, image: np.ndarray | None) -> ImageAnalysis | None:
        if image is None:
            return None
        working = image[:, :, :3] if image.ndim == 3 else image
        if working.ndim != 3:
            return None

        hsv = cv2.cvtColor(working, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 160)

        mean_luma = float(gray.mean() / 255.0)
        contrast_std = float(gray.std() / 255.0)
        saturation_mean = float(hsv[:, :, 1].mean() / 255.0)
        warm_balance = float((working[:, :, 2].mean() - working[:, :, 0].mean()) / 255.0)
        edge_density = float(np.count_nonzero(edges) / edges.size)

        is_dark = mean_luma < 0.35
        is_low_contrast = contrast_std < 0.18
        is_colorful = saturation_mean > 0.34
        is_warm = warm_balance > 0.06
        is_detailed = edge_density > 0.08

        scene_hint = self._infer_scene_hint(
            is_dark=is_dark,
            is_low_contrast=is_low_contrast,
            is_colorful=is_colorful,
            is_warm=is_warm,
            is_detailed=is_detailed,
            saturation_mean=saturation_mean,
            edge_density=edge_density,
        )
        guidance = self._build_guidance(
            is_dark=is_dark,
            is_low_contrast=is_low_contrast,
            is_colorful=is_colorful,
            is_warm=is_warm,
            is_detailed=is_detailed,
            scene_hint=scene_hint,
        )
        return ImageAnalysis(
            mean_luma=mean_luma,
            contrast_std=contrast_std,
            saturation_mean=saturation_mean,
            warm_balance=warm_balance,
            edge_density=edge_density,
            is_dark=is_dark,
            is_low_contrast=is_low_contrast,
            is_colorful=is_colorful,
            is_warm=is_warm,
            is_detailed=is_detailed,
            scene_hint=scene_hint,
            guidance=guidance,
        )

    @staticmethod
    def _infer_scene_hint(
        *,
        is_dark: bool,
        is_low_contrast: bool,
        is_colorful: bool,
        is_warm: bool,
        is_detailed: bool,
        saturation_mean: float,
        edge_density: float,
    ) -> str:
        if is_dark and is_low_contrast:
            return "Night / low-light"
        if is_warm and saturation_mean > 0.30:
            return "Food / indoor warm scene"
        if is_colorful and is_detailed and edge_density > 0.10:
            return "Landscape / outdoor detail"
        if not is_detailed and saturation_mean < 0.28:
            return "Portrait / soft subject"
        return "General photo"

    @staticmethod
    def _build_guidance(
        *,
        is_dark: bool,
        is_low_contrast: bool,
        is_colorful: bool,
        is_warm: bool,
        is_detailed: bool,
        scene_hint: str,
    ) -> str:
        notes: list[str] = [f"Detected scene: {scene_hint}."]
        if is_dark:
            notes.append("The image reads dark. Check exposure and shadows before touching style.")
        if is_low_contrast:
            notes.append("Contrast looks flat. Start with exposure and contrast, then revisit saturation.")
        if is_warm:
            notes.append("There is a warm color cast. White balance may need cooling unless the warmth is intentional.")
        if is_colorful:
            notes.append("Color intensity is already present. Avoid stacking a heavy warm preset on top.")
        if is_detailed:
            notes.append("The frame has many edges and fine details. Be conservative with denoise.")
        if len(notes) == 1:
            notes.append("No major technical issue stands out. Keep corrections small and use presets lightly.")
        return " ".join(notes)
