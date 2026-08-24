"""Fraud Detection Engine orchestrator (docs/17_Fraud_Detection.md S3-S4,
S25 workflow; ADR-0004).

Composes independent detectors -- rule-based, image tampering,
multi-level duplicate, and transaction pattern -- into one explainable
FraudResult. Mirrors the "clean, addable/replaceable" composition ADR-0004
and this milestone's instructions ask for:

    FraudDetectionEngine
        - RuleBasedDetector      (rule_based_detector.py)
        - ImageTamperingDetector (image_tampering_detector.py)
        - DuplicateDetector      (duplicate_detector.py)
        - PatternDetector        (pattern_detector.py)
        - FutureMLDetector       (not implemented -- see module docstring
                                   note below)

No supervised ML model is trained or invoked here (ADR-0004: "introducing
a trained ML fraud model is out of scope until a labeled dataset and
evaluation methodology exist"); `model_prediction`/`model_name` always
reflect the rule-based engine so nothing is misrepresented as ML output.

Module boundary (docs/17 S42, S31): this service produces evidence for
the Risk Scoring/Decision Engine (Milestones 6/7). It never approves,
rejects, or performs signature comparison itself.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError, get_banking_repository
from app.repositories.cheque_repository import get_cheque_repository
from app.services.cheque import storage
from app.services.fraud.detectors import duplicate_detector, image_tampering_detector, pattern_detector, rule_based_detector
from app.services.fraud.detectors.image_hasher import average_hash_of_bytes
from app.services.fraud.exceptions import ChequeNotValidatedError
from app.services.fraud.models import FraudIndicator, FraudResult, RuleViolation, classify_risk_level
from app.services.preprocessing.preprocessing_service import load_image_bgr

_RISK_PRECEDENCE = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def _field_value(fields: dict, name: str):
    return fields.get(name, {}).get("value")


def _original_image_bytes(cheque_id: str) -> bytes | None:
    """Original (unpreprocessed) upload bytes, if a plain image was
    uploaded -- used for perceptual hashing so results stay comparable
    with the Milestone 1 reference hashes, which were computed on the
    untouched rendered images (see image_hasher.py's module docstring).
    Returns None for PDFs or if the file cannot be located/decoded."""
    for candidate in sorted(settings.runtime_original_dir.glob(f"{cheque_id}.*")):
        try:
            return candidate.read_bytes()
        except OSError:
            return None
    return None


def _processed_image(cheque_id: str):
    path = storage.processed_file_path(cheque_id)
    if not path.exists():
        return None
    try:
        return load_image_bgr(path)
    except Exception:  # noqa: BLE001 - a corrupt/unreadable image must never crash fraud analysis
        return None


def analyze_fraud(
    cheque_id: str,
    *,
    processing_date: date | None = None,
    banking_repo: BankingDataRepository | None = None,
    signature_result: dict | None = None,
) -> FraudResult:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    validation = record.get("validation")
    if validation is None:
        raise ChequeNotValidatedError(
            "Cheque has not completed Milestone 4 validation yet; fraud analysis cannot run."
        )

    banking_repo = banking_repo or get_banking_repository()
    processing_date = processing_date or datetime.now(timezone.utc).date()

    extraction = record.get("extraction") or {}
    fields = extraction.get("fields", {})
    account_number = _field_value(fields, "account_number")
    cheque_number = _field_value(fields, "cheque_number")
    amount = _field_value(fields, "amount")
    date_value = _field_value(fields, "date")

    validation_checks = validation.get("checks", {})
    unavailable_inputs: list[str] = []

    # --- Duplicate detection (Levels 1-3 + rule D4) ---
    current_file_hash = record.get("file_hash")
    original_bytes = _original_image_bytes(cheque_id)
    current_perceptual_hash = None
    if original_bytes is not None:
        try:
            current_perceptual_hash = average_hash_of_bytes(original_bytes, settings.duplicate_perceptual_hash_size)
        except Exception:  # noqa: BLE001 - unsupported/corrupt image must not crash fraud analysis
            current_perceptual_hash = None

    dup_result = duplicate_detector.detect(
        account_number=account_number, cheque_number=cheque_number, amount=amount, date_value=date_value,
        validation_duplicate_check=validation_checks.get("DUPLICATE_CHECK"),
        current_perceptual_hash=current_perceptual_hash, current_file_hash=current_file_hash,
        banking_repo=banking_repo,
    )
    if dup_result.analysis_status != "COMPLETED":
        unavailable_inputs.append("DUPLICATE_DETECTION")

    # --- Image tampering detection ---
    image_bgr = _processed_image(cheque_id)
    tampering_result = image_tampering_detector.analyze(image_bgr)
    if tampering_result.analysis_status != "COMPLETED":
        unavailable_inputs.append("IMAGE_TAMPERING_ANALYSIS")

    # --- Transaction pattern indicators ---
    try:
        banking_repo.get_account_transactions(account_number) if account_number else None
        pattern_data_available = True
    except BankingDataUnavailableError:
        pattern_data_available = False
        unavailable_inputs.append("TRANSACTION_HISTORY")
    pattern_indicators = pattern_detector.analyze(
        account_number=account_number, cheque_number=cheque_number, amount=amount,
        processing_date=processing_date, banking_repo=banking_repo,
    ) if pattern_data_available else []

    # --- Signature (Milestone 6 responsibility; never fabricated here) ---
    if signature_result is None:
        unavailable_inputs.append("SIGNATURE_ANALYSIS")

    # --- Rule-based detector (RULE-001..RULE-005 + validation signals) ---
    rule_indicators, rule_violations = rule_based_detector.evaluate(
        validation_checks=validation_checks, duplicate_status=dup_result.duplicate_status,
        signature_result=signature_result,
    )

    indicators: list[FraudIndicator] = list(rule_indicators) + list(pattern_indicators)

    weights = settings.fraud_score_weights
    if tampering_result.image_tampering_score is not None and tampering_result.image_tampering_score >= settings.tampering_score_review_threshold:
        score = tampering_result.image_tampering_score
        indicators.append(FraudIndicator(
            type="IMAGE_TAMPERING",
            severity="HIGH" if score >= 0.75 else "MEDIUM",
            reason=(
                f"Image tampering score {score:.2f} exceeds the configured review threshold "
                f"({len(tampering_result.indicators)} region-level indicator(s) contributed)."
            ),
            contribution=weights["tampering"] * score,
            evidence={"image_tampering_score": round(score, 4), "region_indicators": tampering_result.indicators},
        ))

    if dup_result.d4_inconsistency:
        indicators.append(FraudIndicator(
            type="CHEQUE_NUMBER_REUSE_INCONSISTENCY", severity="HIGH",
            reason=(
                "Same account and cheque number as a previously processed cheque, but the amount "
                "and/or date differ (docs/19 Rule D4) -- this is a high-risk inconsistency, not "
                "automatically a confirmed duplicate."
            ),
            contribution=weights["duplicate"] * 0.4,
            evidence={"matched_cheque_id": dup_result.d4_matched_cheque_id},
        ))

    fraud_risk_score = min(100.0, sum(ind.contribution for ind in indicators))
    risk_level = classify_risk_level(fraud_risk_score, settings.fraud_risk_bands)

    # RULE-005: multiple high-risk indicators -> mandatory manual-review escalation.
    high_risk_count = sum(1 for ind in indicators if ind.severity in ("HIGH", "CRITICAL"))
    rule005_triggered = high_risk_count >= settings.fraud_multi_indicator_review_threshold
    if rule005_triggered:
        rule_violations.append(RuleViolation(
            "RULE-005", "IF multiple high-risk indicators exist THEN route to manual review.",
            triggered_by=[ind.type for ind in indicators if ind.severity in ("HIGH", "CRITICAL")],
        ))
        if _RISK_PRECEDENCE[risk_level] < _RISK_PRECEDENCE["HIGH"]:
            risk_level = "HIGH"

    recommendation = {
        "LOW": "NO_ACTION_REQUIRED", "MEDIUM": "MONITOR",
        "HIGH": "MANUAL_REVIEW", "CRITICAL": "MANUAL_REVIEW",
    }[risk_level]

    total_sources = 5  # validation, duplicate/banking data, image, transaction history, signature
    available_sources = 1  # validation is guaranteed present at this point
    available_sources += 0 if "DUPLICATE_DETECTION" in unavailable_inputs else 1
    available_sources += 0 if "IMAGE_TAMPERING_ANALYSIS" in unavailable_inputs else 1
    available_sources += 0 if "TRANSACTION_HISTORY" in unavailable_inputs else 1
    available_sources += 0 if "SIGNATURE_ANALYSIS" in unavailable_inputs else 1
    confidence = available_sources / total_sources

    result = FraudResult(
        cheque_id=cheque_id,
        fraud_risk_score=fraud_risk_score,
        risk_level=risk_level,
        model_prediction="LEGITIMATE" if risk_level == "LOW" else "SUSPICIOUS",
        indicators=indicators,
        rule_violations=rule_violations,
        confidence=confidence,
        analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        engine_version=settings.fraud_engine_version,
        recommendation=recommendation,
        unavailable_inputs=unavailable_inputs,
    )

    persisted = {
        **result.as_dict(),
        "duplicate_analysis": dup_result.as_dict(),
        "image_analysis": tampering_result.as_dict(),
    }
    repo.update(cheque_id, {"fraud_analysis": persisted, "processing_status": "FRAUD_ANALYZED"})

    return result


def get_fraud_result(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("fraud_analysis")
