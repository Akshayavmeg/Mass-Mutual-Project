"""Preprocessing orchestrator (docs/13_Image_Preprocessing.md S5, S24, S27).

Ties together quality assessment and the individual operations into the
documented pipeline, decides which operations are actually needed for a
given image, and produces the processing metadata later modules (and this
milestone's API) will read.

The original image is never touched by this module -- it operates only on
an in-memory copy loaded from the already-saved original file, and writes
its result to a separate processed-image path (docs/13 S4).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import cv2
import numpy as np
from PIL import Image

from app.services.cheque import storage
from app.services.cheque.exceptions import CorruptedFileError
from app.services.preprocessing.operations import (
    convert_to_grayscale,
    correct_skew,
    crop_to_content,
    enhance_contrast,
    reduce_noise,
    resize_if_needed,
)
from app.services.preprocessing.quality_assessment import QualityResult, assess_image_quality


@dataclass
class PreprocessingResult:
    preprocessing_status: str  # "COMPLETED" | "FAILED"
    quality: QualityResult
    operations: list[str] = field(default_factory=list)
    processed_image_path: str | None = None
    processed_width: int | None = None
    processed_height: int | None = None
    processing_time_ms: float = 0.0
    error_message: str | None = None

    def as_dict(self) -> dict:
        return {
            "preprocessing_status": self.preprocessing_status,
            "operations": self.operations,
            "processed_image_path": self.processed_image_path,
            "processed_width": self.processed_width,
            "processed_height": self.processed_height,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "error_message": self.error_message,
            "quality": self.quality.as_dict() if self.quality else None,
        }


def load_image_bgr(path_or_bytes) -> np.ndarray:
    """Loads an image via Pillow (broad format tolerance) and converts to
    an OpenCV-style BGR numpy array."""
    with Image.open(path_or_bytes) as img:
        rgb = img.convert("RGB")
        arr = np.array(rgb)
    return arr[:, :, ::-1].copy()


def preprocess_image(cheque_id: str, image: np.ndarray) -> PreprocessingResult:
    """Runs the documented preprocessing pipeline on an already-loaded
    image (for a PDF, the caller passes the already-rendered first page;
    for a plain image upload, the caller passes the decoded original)."""
    start = time.perf_counter()
    operations: list[str] = []

    try:
        quality = assess_image_quality(image)

        working = convert_to_grayscale(image)
        operations.append("grayscale")

        noise_factor = next(f for f in quality.factors if f.name == "noise")
        if noise_factor.status == "WARNING":
            working = reduce_noise(working)
            operations.append("noise_reduction")

        contrast_factor = next(f for f in quality.factors if f.name == "contrast")
        if contrast_factor.status == "WARNING":
            working = enhance_contrast(working)
            operations.append("contrast_enhancement")

        if abs(quality.skew_angle_degrees) > 0:
            skew_factor = next(f for f in quality.factors if f.name == "skew")
            if skew_factor.status == "WARNING":
                working = correct_skew(working, quality.skew_angle_degrees)
                operations.append("deskew")

        cropped, was_cropped = crop_to_content(working)
        if was_cropped:
            working = cropped
            operations.append("crop")

        resolution_factor = next(f for f in quality.factors if f.name == "resolution")
        if resolution_factor.status == "WARNING":
            resized, was_resized = resize_if_needed(working)
            if was_resized:
                working = resized
                operations.append("resize")

        processed_path = storage.processed_file_path(cheque_id)
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(processed_path), working)

        elapsed_ms = (time.perf_counter() - start) * 1000
        height, width = working.shape[:2]

        return PreprocessingResult(
            preprocessing_status="COMPLETED",
            quality=quality,
            operations=operations,
            processed_image_path=str(processed_path),
            processed_width=int(width),
            processed_height=int(height),
            processing_time_ms=elapsed_ms,
        )
    except Exception as exc:  # noqa: BLE001 - preprocessing must fail safely, never crash the request
        elapsed_ms = (time.perf_counter() - start) * 1000
        fallback_quality = QualityResult(quality_status="UNSUITABLE", factors=[])
        return PreprocessingResult(
            preprocessing_status="FAILED",
            quality=fallback_quality,
            operations=operations,
            processing_time_ms=elapsed_ms,
            error_message=str(exc) if isinstance(exc, CorruptedFileError) else "Preprocessing failed.",
        )
