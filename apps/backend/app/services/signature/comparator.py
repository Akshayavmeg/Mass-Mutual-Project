"""Signature comparison (docs/18_Signature_Analysis.md S10-S13).

Computes a weighted Euclidean distance between two SignatureFeatures
vectors and converts it into a bounded 0.00-1.00 similarity score. Per-
feature normalization constants match the scale used during this
milestone's empirical calibration (see the Milestone 6 report) so the
configured weights are comparable across features of very different raw
magnitude (density is a tiny fraction; bbox extents are 0-1; aspect
ratio and component count are small integers/ratios).
"""

from __future__ import annotations

import math

from app.core.config import settings
from app.services.signature.feature_extractor import SignatureFeatures

_NORMALIZATION = {
    "density": 1000.0,   # density is O(0.01-0.1) -> scale to O(10-100)
    "component_count": 1.0,
    "bbox_width": 1.0,
    "bbox_height": 1.0,
    "aspect_ratio": 0.1,  # aspect ratio can be several units -> down-scale
}


def _weighted_distance(a: SignatureFeatures, b: SignatureFeatures) -> float:
    weights = settings.signature_feature_weights
    total = 0.0
    for name, scale in _NORMALIZATION.items():
        wa = getattr(a, name) * scale
        wb = getattr(b, name) * scale
        weight = weights.get(name, 1.0)
        total += weight * (wa - wb) ** 2
    return math.sqrt(total)


def similarity(a: SignatureFeatures, b: SignatureFeatures) -> float:
    distance = _weighted_distance(a, b)
    return 1.0 / (1.0 + distance / settings.signature_similarity_distance_scale)


def best_match(current: SignatureFeatures, references: list[tuple[str, SignatureFeatures]]) -> tuple[str | None, float]:
    """Compares `current` against every reference and returns the
    (signature_id, similarity) of the best (highest-similarity) match --
    docs/18 S28: "may use the highest ... similarity score" when multiple
    reference signatures are available, since genuine signatures
    naturally vary."""
    if not references:
        return None, 0.0
    best_id, best_score = None, -1.0
    for signature_id, features in references:
        score = similarity(current, features)
        if score > best_score:
            best_id, best_score = signature_id, score
    return best_id, best_score
