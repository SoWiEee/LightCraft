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
        image_u8, alpha = self._apply_rotation(image_u8, alpha, edit_state.rotation_deg)
        image_u8, alpha = self._apply_crop(image_u8, alpha, edit_state)

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

    @staticmethod
    def _apply_rotation(image: np.ndarray, alpha: np.ndarray | None, rotation_deg: float) -> tuple[np.ndarray, np.ndarray | None]:
        if abs(rotation_deg) < 1e-6:
            return image, alpha
        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)
        matrix = cv2.getRotationMatrix2D(center, -rotation_deg, 1.0)
        cos = abs(matrix[0, 0])
        sin = abs(matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        matrix[0, 2] += (new_width / 2.0) - center[0]
        matrix[1, 2] += (new_height / 2.0) - center[1]
        rotated = cv2.warpAffine(
            image,
            matrix,
            (new_width, new_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )
        rotated_alpha = None
        if alpha is not None:
            rotated_alpha = cv2.warpAffine(
                alpha,
                matrix,
                (new_width, new_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0,
            )
            if rotated_alpha.ndim == 2:
                rotated_alpha = rotated_alpha[:, :, None]
        return rotated, rotated_alpha

    @staticmethod
    def _apply_crop(image: np.ndarray, alpha: np.ndarray | None, edit_state: EditState) -> tuple[np.ndarray, np.ndarray | None]:
        height, width = image.shape[:2]
        left = int(round(width * edit_state.crop_left_pct / 100.0))
        top = int(round(height * edit_state.crop_top_pct / 100.0))
        right = width - int(round(width * edit_state.crop_right_pct / 100.0))
        bottom = height - int(round(height * edit_state.crop_bottom_pct / 100.0))

        min_width = 32
        min_height = 32
        if right - left < min_width:
            excess = min_width - (right - left)
            left = max(0, left - excess // 2)
            right = min(width, right + excess - excess // 2)
        if bottom - top < min_height:
            excess = min_height - (bottom - top)
            top = max(0, top - excess // 2)
            bottom = min(height, bottom + excess - excess // 2)

        left = max(0, min(left, width - 1))
        top = max(0, min(top, height - 1))
        right = max(left + 1, min(right, width))
        bottom = max(top + 1, min(bottom, height))

        if left == 0 and top == 0 and right == width and bottom == height:
            return image, alpha

        cropped = image[top:bottom, left:right]
        cropped_alpha = alpha[top:bottom, left:right] if alpha is not None else None
        return cropped, cropped_alpha
