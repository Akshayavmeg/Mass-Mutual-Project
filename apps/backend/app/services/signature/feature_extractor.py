"""Signature feature extraction (docs/18_Signature_Analysis.md S11-S12
Method 2 -- feature-based comparison).

Extracts a small set of aggregate structural features from a signature
crop's ink mask: ink density, connected-component ("stroke") count, and
normalized bounding-box extent/aspect ratio. These were chosen after
measuring (see the Milestone 6 report) that raw pixel/perceptual
similarity carries almost no signal on this project's procedurally
generated synthetic signatures, while these aggregate statistics show a
real, if modest, measured separation between genuine and forged samples.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

_INK_THRESHOLD = 200  # grayscale value below which a pixel is "ink"


@dataclass(frozen=True)
class SignatureFeatures:
    density: float
    component_count: int
    bbox_width: float  # normalized 0-1 by canvas width
    bbox_height: float  # normalized 0-1 by canvas height
    aspect_ratio: float
    ink_pixel_count: int


def ink_mask(gray: np.ndarray) -> np.ndarray:
    return (gray < _INK_THRESHOLD).astype(np.uint8)


def extract_features(gray: np.ndarray) -> SignatureFeatures | None:
    """`gray` is a grayscale signature crop. Returns None if the crop
    contains no ink at all (caller should treat this as SIGNATURE_MISSING,
    not as a zero-similarity mismatch)."""
    mask = ink_mask(gray)
    ink_count = int(mask.sum())
    if ink_count == 0:
        return None

    height, width = gray.shape[:2]
    n_components, _ = cv2.connectedComponents(mask, connectivity=8)
    ys, xs = np.where(mask)
    bbox_w = (xs.max() - xs.min()) / max(width, 1)
    bbox_h = (ys.max() - ys.min()) / max(height, 1)
    aspect_ratio = bbox_w / max(bbox_h, 1e-6)

    return SignatureFeatures(
        density=ink_count / mask.size,
        component_count=max(0, n_components - 1),
        bbox_width=bbox_w,
        bbox_height=bbox_h,
        aspect_ratio=aspect_ratio,
        ink_pixel_count=ink_count,
    )
