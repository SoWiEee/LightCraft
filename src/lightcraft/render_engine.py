from __future__ import annotations

import cv2
import numpy as np

from .models import EditState


class RenderEngine:
    """Rebuild a preview image from source image + edit state."""

    def render_preview(self, source_image: np.ndarray, edit_state: EditState) -> np.ndarray:
        if source_image.ndim != 3:
            raise ValueError("Expected HxWxC image")

        alpha = None
        working = source_image
        if source_image.shape[2] == 4:
            alpha = source_image[:, :, 3:4].copy()
            working = source_image[:, :, :3]

        image = working.astype(np.float32) / 255.0
        image = self._apply_exposure(image, edit_state.exposure)
        image = self._apply_contrast(image, edit_state.contrast)
        image = self._apply_white_balance(image, edit_state.white_balance_temp)
        image = self._apply_saturation(image, edit_state.saturation)
        image = self._apply_shadows(image, edit_state.shadows)
        image = np.clip(image, 0.0, 1.0)
        image_u8 = (image * 255.0).astype(np.uint8)
        image_u8 = self._apply_denoise(image_u8, edit_state.denoise)
        image_u8 = self._apply_sharpening(image_u8, edit_state.sharpening)

        if alpha is not None:
            image_u8 = np.concatenate([image_u8, alpha], axis=2)
        return image_u8

    @staticmethod
    def _apply_exposure(image: np.ndarray, exposure: float) -> np.ndarray:
        if abs(exposure) < 1e-6:
            return image
        factor = 2.0 ** exposure
        return image * factor

    @staticmethod
    def _apply_contrast(image: np.ndarray, contrast: float) -> np.ndarray:
        if abs(contrast) < 1e-6:
            return image
        alpha = 1.0 + contrast / 100.0
        midpoint = 0.5
        return (image - midpoint) * alpha + midpoint

    @staticmethod
    def _apply_white_balance(image: np.ndarray, wb: float) -> np.ndarray:
        if abs(wb) < 1e-6:
            return image
        amount = wb / 100.0
        bgr = image.copy()
        red_gain = 1.0 + max(0.0, amount) * 0.25 - max(0.0, -amount) * 0.10
        blue_gain = 1.0 + max(0.0, -amount) * 0.25 - max(0.0, amount) * 0.10
        green_gain = 1.0 - abs(amount) * 0.05
        bgr[:, :, 2] *= red_gain
        bgr[:, :, 1] *= green_gain
        bgr[:, :, 0] *= blue_gain
        return bgr

    @staticmethod
    def _apply_saturation(image: np.ndarray, saturation: float) -> np.ndarray:
        if abs(saturation) < 1e-6:
            return image
        hsv = cv2.cvtColor((np.clip(image, 0.0, 1.0) * 255.0).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= 1.0 + saturation / 100.0
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0.0, 255.0)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0

    @staticmethod
    def _apply_shadows(image: np.ndarray, shadows: float) -> np.ndarray:
        if abs(shadows) < 1e-6:
            return image
        luminance = 0.114 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.299 * image[:, :, 2]
        shadow_mask = np.clip(1.0 - luminance / 0.5, 0.0, 1.0)
        adjustment = (shadows / 100.0) * 0.35 * shadow_mask[:, :, None]
        return image + adjustment

    @staticmethod
    def _apply_denoise(image: np.ndarray, denoise: float) -> np.ndarray:
        if denoise <= 0:
            return image
        strength = max(1, int(denoise / 8))
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)

    @staticmethod
    def _apply_sharpening(image: np.ndarray, sharpening: float) -> np.ndarray:
        if sharpening <= 0:
            return image
        blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=1.2)
        amount = sharpening / 100.0 * 1.8
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)
