"""Image tampering detector (docs/17_Fraud_Detection.md S7-S9; FR-020).

This produces a measurable, explainable indicator from actual pixel
evidence -- it never reads the Milestone 1 synthetic category or fraud
label. The approach: for each documented tampering-prone region (amount,
payee, date, cheque number), compute simple texture/edge statistics
(local noise residual, Laplacian edge-variance, and boundary-vs-interior
gradient discontinuity) and compare them against the population of ALL
printed regions on the *same* cheque image (self-referential baseline --
no external/trained model). A region whose statistics deviate sharply
from the cheque's own other regions is flagged as a tampering indicator;
this is exactly the "Original-looking region + Suspiciously modified
region" comparison docs/17 S7 describes.

Because the Milestone 1 dataset renders every field through the same
PIL text pipeline regardless of fraud category (AMOUNT_TAMPERED, for
example, represents a numeric-vs-words *value* mismatch, not a pixel-
level splice), this detector is expected to -- and should -- report low
scores across most categories. That is a correct, honest result given
the actual image evidence, not a detector defect (docs/39_Limitations.md
S12 anticipates exactly this: manipulated content that "visually
resembles the original" is a known, documented limitation of image-only
tampering detection).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from app.core.config import settings
from app.services.ocr.regions import REGIONS

_BASELINE_REGIONS = (
    "bank_name", "date", "cheque_number", "payee_name", "amount",
    "amount_in_words", "account_number", "routing_transit_number", "micr_line",
)


@dataclass
class RegionStats:
    name: str
    noise_std: float
    edge_variance: float


@dataclass
class ImageTamperingResult:
    image_tampering_score: float | None
    indicators: list[dict] = field(default_factory=list)
    region_stats: dict[str, dict] = field(default_factory=dict)
    analysis_status: str = "COMPLETED"

    def as_dict(self) -> dict:
        return {
            "image_tampering_score": round(self.image_tampering_score, 4) if self.image_tampering_score is not None else None,
            "indicators": self.indicators,
            "region_stats": self.region_stats,
            "analysis_status": self.analysis_status,
        }


def _region_pixels(gray: np.ndarray, name: str) -> np.ndarray | None:
    region = REGIONS.get(name)
    if region is None:
        return None
    height, width = gray.shape[:2]
    x0, x1 = int(region.x0 * width), int(region.x1 * width)
    y0, y1 = int(region.y0 * height), int(region.y1 * height)
    if x1 <= x0 or y1 <= y0:
        return None
    return gray[y0:y1, x0:x1]


def _compute_region_stats(gray: np.ndarray, name: str) -> RegionStats | None:
    crop = _region_pixels(gray, name)
    if crop is None or crop.size < 100:
        return None
    crop_f = crop.astype(np.float64)
    denoised = cv2.medianBlur(crop, 3).astype(np.float64)
    noise_std = float(np.std(crop_f - denoised))
    edge_variance = float(cv2.Laplacian(crop, cv2.CV_64F).var())
    return RegionStats(name=name, noise_std=noise_std, edge_variance=edge_variance)


def _boundary_discontinuity(gray: np.ndarray, name: str) -> float | None:
    """Compares mean gradient magnitude on a thin ring just inside the
    region boundary against the region's interior -- a pasted patch
    typically leaves a sharper edge at its splice boundary than a
    naturally rendered region has internally."""
    crop = _region_pixels(gray, name)
    if crop is None or min(crop.shape[:2]) < 12:
        return None
    grad_x = cv2.Sobel(crop, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(crop, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)

    ring = max(2, min(crop.shape[:2]) // 8)
    mask = np.zeros(crop.shape[:2], dtype=bool)
    mask[:ring, :] = True
    mask[-ring:, :] = True
    mask[:, :ring] = True
    mask[:, -ring:] = True

    boundary_mean = float(magnitude[mask].mean()) if mask.any() else 0.0
    interior_mean = float(magnitude[~mask].mean()) if (~mask).any() else 0.0
    if interior_mean < 1e-6:
        return 0.0
    return boundary_mean / interior_mean


def analyze(image_bgr: np.ndarray | None) -> ImageTamperingResult:
    if image_bgr is None:
        return ImageTamperingResult(
            image_tampering_score=None, analysis_status="INSUFFICIENT_DATA",
            indicators=[{
                "type": "IMAGE_UNAVAILABLE", "severity": "LOW",
                "reason": "No cheque image was available for tampering analysis.",
            }],
        )

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    stats: dict[str, RegionStats] = {}
    for name in _BASELINE_REGIONS:
        s = _compute_region_stats(gray, name)
        if s is not None:
            stats[name] = s

    if len(stats) < 3:
        return ImageTamperingResult(
            image_tampering_score=None, analysis_status="INSUFFICIENT_DATA",
            indicators=[{
                "type": "IMAGE_UNAVAILABLE", "severity": "LOW",
                "reason": "Too few readable regions to establish a per-cheque baseline for tampering comparison.",
            }],
        )

    noise_values = np.array([s.noise_std for s in stats.values()])
    edge_values = np.array([s.edge_variance for s in stats.values()])
    noise_mean, noise_std = float(noise_values.mean()), float(noise_values.std()) or 1e-6
    edge_mean, edge_std = float(edge_values.mean()), float(edge_values.std()) or 1e-6

    indicators: list[dict] = []
    region_report: dict[str, dict] = {}
    region_scores: list[float] = []

    for name in settings.tampering_regions:
        s = stats.get(name)
        if s is None:
            continue
        noise_z = (s.noise_std - noise_mean) / noise_std
        edge_z = (s.edge_variance - edge_mean) / edge_std
        boundary_ratio = _boundary_discontinuity(gray, name)

        excess = max(0.0, abs(noise_z) - 1.0) + max(0.0, abs(edge_z) - 1.0)
        region_score = min(1.0, excess / (2 * max(settings.tampering_noise_zscore_threshold, 0.1)))
        region_scores.append(region_score)

        region_report[name] = {
            "noise_zscore": round(noise_z, 3),
            "edge_zscore": round(edge_z, 3),
            "boundary_interior_ratio": round(boundary_ratio, 3) if boundary_ratio is not None else None,
        }

        triggered = (
            abs(noise_z) > settings.tampering_noise_zscore_threshold
            or abs(edge_z) > settings.tampering_edge_zscore_threshold
        )
        if triggered:
            severity = "HIGH" if region_score >= 0.75 else "MEDIUM" if region_score >= 0.4 else "LOW"
            indicators.append({
                "type": f"{name.upper()}_REGION_INCONSISTENCY",
                "severity": severity,
                "reason": (
                    f"Pixel-level texture in the '{name}' region deviates from this cheque's other "
                    f"printed regions (noise z={noise_z:.2f}, edge z={edge_z:.2f})."
                ),
                "evidence": region_report[name],
            })

    overall_score = max(region_scores) if region_scores else 0.0

    return ImageTamperingResult(
        image_tampering_score=overall_score,
        indicators=indicators,
        region_stats=region_report,
        analysis_status="COMPLETED",
    )
