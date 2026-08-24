"""Signature Analysis orchestrator (docs/18_Signature_Analysis.md S29
processing algorithm; S23 output structure).

Reuses Milestone 3's own signature-region *detection* (ink-ratio check,
already computed during extraction) rather than re-detecting presence --
this module only adds comparison, quality assessment, and risk
classification on top of that (docs/18 S40 module boundary: OCR/
extraction is explicitly NOT this module's responsibility).

Module boundary (docs/18 S17, S40): a signature mismatch is a risk
indicator for the Fraud Detection Engine, never a fraud verdict; a
missing reference signature means verification is UNAVAILABLE, not that
the cheque is fraudulent.
"""

from __future__ import annotations

from datetime import datetime, timezone

import cv2
import numpy as np

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError, get_banking_repository
from app.repositories.cheque_repository import get_cheque_repository
from app.services.cheque import storage
from app.services.preprocessing.preprocessing_service import load_image_bgr
from app.services.signature import comparator
from app.services.signature.exceptions import ChequeNotExtractedForSignatureError
from app.services.signature.feature_extractor import extract_features
from app.services.signature.models import SignatureAnalysisResult
from app.services.signature.quality_checker import assess_quality

_MODEL_NAME = "signature-feature-comparator"


def _field_value(fields: dict, name: str):
    return fields.get(name, {}).get("value")


def _signature_crop_gray(cheque_id: str, bbox: dict) -> np.ndarray | None:
    path = storage.processed_file_path(cheque_id)
    if not path.exists():
        return None
    try:
        image = load_image_bgr(path)
    except Exception:  # noqa: BLE001 - unreadable image must not crash analysis
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x0, y0, w, h = bbox["x"], bbox["y"], bbox["width"], bbox["height"]
    crop = gray[y0:y0 + h, x0:x0 + w]
    return crop if crop.size > 0 else None


def _tampering_score(gray: np.ndarray) -> float:
    """Boundary-vs-interior gradient discontinuity within the signature
    crop itself (same rationale as Milestone 5's image-tampering
    detector, applied here to the one region available): a pasted/
    re-rendered signature patch tends to leave a sharper edge at its
    splice boundary than a naturally captured signature has internally."""
    if min(gray.shape[:2]) < 12:
        return 0.0
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)
    ring = max(2, min(gray.shape[:2]) // 8)
    mask = np.zeros(gray.shape[:2], dtype=bool)
    mask[:ring, :] = True
    mask[-ring:, :] = True
    mask[:, :ring] = True
    mask[:, -ring:] = True
    boundary_mean = float(magnitude[mask].mean()) if mask.any() else 0.0
    interior_mean = float(magnitude[~mask].mean()) if (~mask).any() else 0.0
    if interior_mean < 1e-6:
        return 0.0
    ratio = boundary_mean / interior_mean
    return max(0.0, min(1.0, (ratio - 1.0) / 2.0))


def _risk_level_for_similarity(score: float) -> str:
    thresholds = settings.signature_risk_thresholds
    if score >= thresholds["LOW"]:
        return "LOW"
    if score >= thresholds["MEDIUM"]:
        return "MEDIUM"
    if score >= thresholds["HIGH"]:
        return "HIGH"
    return "CRITICAL"


_RECOMMENDATION_BY_RISK = {"LOW": "PASS", "MEDIUM": "MONITOR", "HIGH": "MANUAL_REVIEW", "CRITICAL": "MANUAL_REVIEW"}


def analyze_signature(
    cheque_id: str, *, banking_repo: BankingDataRepository | None = None,
) -> SignatureAnalysisResult:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    extraction = record.get("extraction")
    if extraction is None:
        raise ChequeNotExtractedForSignatureError(
            "Cheque has not completed OCR/extraction yet; signature analysis cannot run."
        )

    banking_repo = banking_repo or get_banking_repository()
    fields = extraction.get("fields", {})
    account_number = _field_value(fields, "account_number")
    now = datetime.now(timezone.utc).isoformat()

    def _result(**overrides) -> SignatureAnalysisResult:
        base = dict(
            cheque_id=cheque_id, account_number=account_number, signature_present=False,
            image_quality="UNKNOWN", similarity_score=None, analysis_confidence=0.0,
            signature_tampering_score=None, risk_level="UNAVAILABLE", indicator=None,
            recommendation="MANUAL_REVIEW", analysis_status="ERROR",
            model_name=_MODEL_NAME, model_version=settings.signature_engine_version,
            analysis_timestamp=now,
        )
        base.update(overrides)
        result = SignatureAnalysisResult(**base)
        repo.update(cheque_id, {"signature_analysis": result.as_dict(), "processing_status": "SIGNATURE_ANALYZED"})
        return result

    if not extraction.get("signature_region_detected"):
        return _result(
            signature_present=False, image_quality="UNKNOWN", risk_level="HIGH",
            indicator="SIGNATURE_MISSING", recommendation="MANUAL_REVIEW",
            analysis_status="COMPLETED", analysis_confidence=1.0,
        )

    bbox = extraction.get("signature_region_bbox")
    gray = _signature_crop_gray(cheque_id, bbox) if bbox else None
    if gray is None:
        return _result(
            signature_present=True, image_quality="UNKNOWN", risk_level="UNAVAILABLE",
            indicator="SIGNATURE_ANALYSIS_ERROR", recommendation="MANUAL_REVIEW",
            analysis_status="ERROR",
        )

    features = extract_features(gray)
    if features is None:
        return _result(
            signature_present=True, image_quality="UNKNOWN", risk_level="UNAVAILABLE",
            indicator="INSUFFICIENT_IMAGE", recommendation="MANUAL_REVIEW",
            analysis_status="INSUFFICIENT_IMAGE",
        )

    quality = assess_quality(gray, features)
    tampering_score = _tampering_score(gray)

    try:
        references = banking_repo.get_reference_signatures(account_number) if account_number else []
        data_unavailable = False
    except BankingDataUnavailableError:
        references = []
        data_unavailable = True

    if not references:
        indicator = "REFERENCE_SIGNATURE_NOT_FOUND"
        return _result(
            signature_present=True, image_quality=quality.quality, risk_level="UNAVAILABLE",
            indicator=indicator, recommendation="MANUAL_REVIEW",
            analysis_status="INSUFFICIENT_DATA" if data_unavailable else "REFERENCE_SIGNATURE_NOT_FOUND",
            signature_tampering_score=tampering_score,
            evidence={"reason": "No reference signature is on file for this account; verification unavailable."},
        )

    reference_features = []
    reference_matches = []
    for ref in references:
        ref_path = settings.mock_banking_data_path / ref.signature_file
        try:
            ref_gray = cv2.cvtColor(load_image_bgr(ref_path), cv2.COLOR_BGR2GRAY)
        except Exception:  # noqa: BLE001 - a missing/corrupt reference file must not crash analysis
            continue
        ref_feat = extract_features(ref_gray)
        if ref_feat is None:
            continue
        reference_features.append((ref.signature_id, ref_feat))
        reference_matches.append({"signature_id": ref.signature_id, "variant": ref.variant})

    if not reference_features:
        return _result(
            signature_present=True, image_quality=quality.quality, risk_level="UNAVAILABLE",
            indicator="REFERENCE_SIGNATURE_NOT_FOUND", recommendation="MANUAL_REVIEW",
            analysis_status="REFERENCE_SIGNATURE_NOT_FOUND", signature_tampering_score=tampering_score,
            evidence={"reason": "Reference signature file(s) on record could not be read."},
        )

    best_id, score = comparator.best_match(features, reference_features)
    for match in reference_matches:
        match["similarity_score"] = round(comparator.similarity(features, dict(reference_features)[match["signature_id"]]), 4)

    risk_level = _risk_level_for_similarity(score)
    quality_penalty = 1.0 if quality.quality == "GOOD" else 0.5
    reference_bonus = min(0.05, 0.025 * (len(reference_features) - 1))
    confidence = min(1.0, max(0.1, 0.9 * quality_penalty + reference_bonus))

    if quality.quality == "POOR":
        indicator = "SIGNATURE_IMAGE_LOW_QUALITY" if "blurred" in (quality.reason or "") else "INSUFFICIENT_IMAGE"
        analysis_status = "COMPLETED"
        recommendation = "MANUAL_REVIEW"
        risk_level = "UNAVAILABLE" if risk_level == "LOW" else risk_level  # do not let a low-confidence match imply "safe"
    else:
        indicator = None if risk_level == "LOW" else "SIGNATURE_MISMATCH"
        analysis_status = "COMPLETED"
        recommendation = _RECOMMENDATION_BY_RISK[risk_level]

    return _result(
        signature_present=True, image_quality=quality.quality, similarity_score=score,
        analysis_confidence=confidence, signature_tampering_score=tampering_score,
        risk_level=risk_level, indicator=indicator, recommendation=recommendation,
        analysis_status=analysis_status, reference_matches=reference_matches,
        evidence={"best_matched_signature_id": best_id, "blur_variance": round(quality.blur_variance, 2)},
    )


def get_signature_result(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("signature_analysis")
