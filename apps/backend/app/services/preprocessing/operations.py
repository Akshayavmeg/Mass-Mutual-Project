"""Individual preprocessing operations (docs/13_Image_Preprocessing.md S8-S15,
S27). Each function does exactly one operation, matching the modular
decomposition docs/13 S27 recommends:

    preprocess_image()
    |-- normalize_image()
    |-- convert_to_grayscale()
    |-- reduce_noise()
    |-- enhance_contrast()
    |-- correct_skew()
    |-- crop_image()
    +-- assess_quality()   (see quality_assessment.py)

None of these operations are applied unconditionally -- the orchestrator
in preprocessing_service.py decides which to run based on the measured
image characteristics (docs/13 S5: "select preprocessing operations based
on the image characteristics so that useful information is not
accidentally removed").
"""

from __future__ import annotations

import cv2
import numpy as np

from app.core.config import settings


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def reduce_noise(gray: np.ndarray) -> np.ndarray:
    """Median filtering (docs/13 S9) -- a mild kernel size is used
    deliberately, since aggressive smoothing can remove thin characters."""
    return cv2.medianBlur(gray, 3)


def enhance_contrast(gray: np.ndarray) -> np.ndarray:
    """CLAHE (docs/13 S10) -- adaptive, so it doesn't over-amplify
    already-well-lit regions of the cheque."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def correct_skew(gray: np.ndarray, angle_degrees: float) -> np.ndarray:
    """Rotates the image to correct the measured skew (docs/13 S12-S13)."""
    if abs(angle_degrees) < 0.01:
        return gray
    height, width = gray.shape[:2]
    center = (width / 2, height / 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
    return cv2.warpAffine(
        gray, rotation_matrix, (width, height),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
    )


def crop_to_content(gray: np.ndarray) -> tuple[np.ndarray, bool]:
    """Detects the cheque boundary and crops unnecessary background
    (docs/13 S14). Returns (image, was_cropped). Falls back to the
    original image (was_cropped=False) whenever the detected region would
    remove an implausibly large fraction of the image, to avoid
    accidentally destroying cheque content (docs/13 S20)."""
    height, width = gray.shape[:2]
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return gray, False

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    area_fraction = (w * h) / float(width * height)
    if area_fraction < 0.35 or area_fraction > 0.99:
        # Detected region is implausibly small or effectively the whole
        # image already -- do not crop rather than risk cutting off
        # cheque content.
        return gray, False

    margin_x = max(int(w * 0.02), 4)
    margin_y = max(int(h * 0.02), 4)
    x0 = max(x - margin_x, 0)
    y0 = max(y - margin_y, 0)
    x1 = min(x + w + margin_x, width)
    y1 = min(y + h + margin_y, height)

    cropped = gray[y0:y1, x0:x1]
    return cropped, True


def resize_if_needed(gray: np.ndarray) -> tuple[np.ndarray, bool]:
    """Controlled resizing (docs/13 S15). Only upscales when the image is
    smaller than the target working size, and caps the scale factor -- per
    docs/13's own caution that "upscaling cannot recreate information that
    was never captured," this is a mild readability aid, not a substitute
    for a higher-quality input."""
    height, width = gray.shape[:2]
    long_side = max(height, width)
    target = settings.target_working_long_side_px
    if long_side >= target:
        return gray, False

    scale = min(target / long_side, settings.max_upscale_factor)
    if scale <= 1.01:
        return gray, False

    new_size = (int(width * scale), int(height * scale))
    resized = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
    return resized, True


def adaptive_threshold(gray: np.ndarray) -> np.ndarray:
    """Adaptive thresholding (docs/13 S11) -- only invoked by the
    orchestrator for images with strongly uneven lighting, since
    thresholding can otherwise damage cheque backgrounds/security
    patterns (docs/13 S11: "should not always be applied blindly")."""
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10,
    )
