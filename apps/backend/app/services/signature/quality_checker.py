"""Signature image-quality assessment (docs/18_Signature_Analysis.md
S19: quality must be checked BEFORE comparison; a poor-quality image
should route to manual review rather than an unreliable automatic
result)."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from app.core.config import settings
from app.services.signature.feature_extractor import SignatureFeatures


@dataclass(frozen=True)
class QualityAssessment:
    quality: str  # "GOOD" | "POOR"
    blur_variance: float
    reason: str | None


def assess_quality(gray: np.ndarray, features: SignatureFeatures) -> QualityAssessment:
    blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    if features.ink_pixel_count < settings.signature_quality_min_ink_pixel_count:
        return QualityAssessment(
            quality="POOR", blur_variance=blur_variance,
            reason="Too little ink detected for a reliable comparison (possible partial capture).",
        )
    if blur_variance < settings.signature_quality_blur_variance_threshold:
        return QualityAssessment(
            quality="POOR", blur_variance=blur_variance,
            reason="Signature region is too blurred/low-contrast for a reliable comparison.",
        )
    return QualityAssessment(quality="GOOD", blur_variance=blur_variance, reason=None)
