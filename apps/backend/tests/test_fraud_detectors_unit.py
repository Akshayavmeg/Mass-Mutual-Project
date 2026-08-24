"""Unit tests for each individual Milestone 5 fraud detector, in
isolation from the real Milestone 1 dataset and the orchestrating
fraud_service (that full-pipeline behavior is covered separately in
test_fraud_service_milestone5.py).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from app.repositories.banking_repository import (
    BankingDataUnavailableError,
    ImageHashRecord,
    TransactionRecord,
)
from app.services.fraud.detectors import duplicate_detector, image_tampering_detector, pattern_detector, rule_based_detector


class _FakeBankingRepo:
    """Minimal BankingDataRepository stand-in exposing only the methods
    each detector actually calls, with an `unavailable` switch to
    exercise the fail-safe paths."""

    def __init__(self, *, transactions=None, image_hashes=None, same_key_records=None,
                 cheque_number_history=None, unavailable=False):
        self._transactions = transactions or []
        self._image_hashes = image_hashes or []
        self._same_key_records = same_key_records or []
        self._cheque_number_history = cheque_number_history or []
        self._unavailable = unavailable

    def get_account_transactions(self, account_number):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._transactions

    def get_image_hash_index(self):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._image_hashes

    def find_by_account_and_cheque_number(self, account_number, cheque_number):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._same_key_records

    def get_account_cheque_number_history(self, account_number):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._cheque_number_history


# ------------------------------------------------------------------
# rule_based_detector
# ------------------------------------------------------------------

def _check(status, severity="HIGH", details=None):
    return {"status": status, "severity": severity, "message": "x", "details": details}


def _all_pass_checks(**overrides):
    checks = {
        "ACCOUNT_EXISTS": _check("PASS"), "ACCOUNT_STATUS": _check("PASS"),
        "CHEQUE_SERIES": _check("PASS"), "CHEQUE_STATUS": _check("PASS"),
        "ROUTING_TRANSIT": _check("PASS"), "DATE_WINDOW": _check("PASS"),
        "PAYEE_MATCH": _check("PASS"), "AMOUNT_CONSISTENCY": _check("PASS"),
        "AMOUNT": _check("PASS"), "DUPLICATE_CHECK": _check("PASS"),
    }
    checks.update(overrides)
    return checks


def test_rule001_fires_on_account_does_not_exist():
    checks = _all_pass_checks(ACCOUNT_EXISTS=_check("FAIL"))
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert any(v.rule_id == "RULE-001" for v in violations)
    assert any(i.type == "ACCOUNT_MISMATCH" and i.severity == "CRITICAL" for i in indicators)


def test_rule002_fires_on_confirmed_duplicate():
    checks = _all_pass_checks()
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="CONFIRMED_DUPLICATE", signature_result=None,
    )
    assert any(v.rule_id == "RULE-002" for v in violations)
    assert any(i.type == "DUPLICATE_CHEQUE" and i.severity == "HIGH" for i in indicators)


def test_rule002_does_not_fire_on_potential_duplicate():
    checks = _all_pass_checks()
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="POTENTIAL_DUPLICATE", signature_result=None,
    )
    assert not any(v.rule_id == "RULE-002" for v in violations)
    assert any(i.type == "DUPLICATE_CHEQUE" and i.severity == "MEDIUM" for i in indicators)


def test_rule003_requires_both_payee_and_signature_mismatch():
    checks = _all_pass_checks(PAYEE_MATCH=_check("FAIL"))
    # Without a signature result, RULE-003 cannot fire (M6 not implemented yet).
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert not any(v.rule_id == "RULE-003" for v in violations)
    assert any(i.type == "PAYEE_MISMATCH" for i in indicators)

    # With an injected (test-only) signature mismatch, RULE-003 fires --
    # this proves the rule's logic without wiring real signature analysis.
    indicators2, violations2 = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW",
        signature_result={"status": "MISMATCH", "similarity_score": 0.3},
    )
    assert any(v.rule_id == "RULE-003" for v in violations2)
    assert any(i.type == "PAYEE_AND_SIGNATURE_MISMATCH" and i.severity == "CRITICAL" for i in indicators2)


def test_rule004_fires_on_amount_consistency_failure():
    checks = _all_pass_checks(AMOUNT_CONSISTENCY=_check("FAIL"))
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert any(v.rule_id == "RULE-004" for v in violations)
    assert any(i.type == "AMOUNT_MISMATCH" and i.severity == "HIGH" for i in indicators)


def test_stopped_cheque_gets_critical_severity():
    checks = _all_pass_checks(CHEQUE_STATUS=_check("FAIL", details={"cheque_status": "STOPPED"}))
    indicators, _ = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert any(i.type == "STOPPED_CHEQUE" and i.severity == "CRITICAL" for i in indicators)


def test_multiple_validation_failures_indicator():
    checks = _all_pass_checks(
        CHEQUE_SERIES=_check("FAIL"), ROUTING_TRANSIT=_check("FAIL"),
    )
    indicators, _ = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert any(i.type == "MULTIPLE_VALIDATION_FAILURES" for i in indicators)


def test_no_indicators_for_clean_validation():
    checks = _all_pass_checks()
    indicators, violations = rule_based_detector.evaluate(
        validation_checks=checks, duplicate_status="NEW", signature_result=None,
    )
    assert indicators == []
    assert violations == []


# ------------------------------------------------------------------
# pattern_detector
# ------------------------------------------------------------------

def test_amount_anomaly_detected_for_large_deviation():
    txns = [TransactionRecord(f"T{i}", "ACC1", "2026-07-01", "CHEQUE", amt, "X") for i, amt in enumerate([1000, 1100, 950, 1050, 1000])]
    repo = _FakeBankingRepo(transactions=txns)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=50000.0,
        processing_date=date(2026, 8, 1), banking_repo=repo,
    )
    assert any(i.type == "AMOUNT_ANOMALY" for i in indicators)


def test_amount_anomaly_not_flagged_within_normal_range():
    txns = [TransactionRecord(f"T{i}", "ACC1", "2026-07-01", "CHEQUE", amt, "X") for i, amt in enumerate([1000, 1100, 950, 1050, 1000])]
    repo = _FakeBankingRepo(transactions=txns)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=1020.0,
        processing_date=date(2026, 8, 1), banking_repo=repo,
    )
    assert not any(i.type == "AMOUNT_ANOMALY" for i in indicators)


def test_amount_anomaly_skipped_on_cold_start_insufficient_history():
    txns = [TransactionRecord("T1", "ACC1", "2026-07-01", "CHEQUE", 1000, "X")]
    repo = _FakeBankingRepo(transactions=txns)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=999999.0,
        processing_date=date(2026, 8, 1), banking_repo=repo,
    )
    # Fewer than pattern_min_history_for_amount_baseline transactions --
    # must not fabricate an anomaly from insufficient history.
    assert not any(i.type == "AMOUNT_ANOMALY" for i in indicators)


def test_normal_high_value_cheque_is_not_flagged_when_history_supports_it():
    """docs/17 S16 / this milestone's explicit requirement: an unusually
    large amount must not automatically be fraud if it is consistent with
    the account's own historical pattern."""
    txns = [TransactionRecord(f"T{i}", "ACC1", "2026-07-01", "CHEQUE", amt, "X") for i, amt in enumerate([48000, 51000, 49500, 50500, 50000])]
    repo = _FakeBankingRepo(transactions=txns)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=50200.0,
        processing_date=date(2026, 8, 1), banking_repo=repo,
    )
    assert not any(i.type == "AMOUNT_ANOMALY" for i in indicators)


def test_frequency_anomaly_detected_for_burst_activity():
    baseline = [TransactionRecord(f"T{i}", "ACC1", "2026-07-01", "CHEQUE", 1000, "X") for i in range(2)]
    burst = [TransactionRecord(f"B{i}", "ACC1", "2026-08-01", "CHEQUE", 1000, "X") for i in range(10)]
    repo = _FakeBankingRepo(transactions=baseline + burst)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=1000.0,
        processing_date=date(2026, 8, 2), banking_repo=repo,
    )
    assert any(i.type == "FREQUENCY_ANOMALY" for i in indicators)


def test_sequence_anomaly_detected_for_large_gap():
    history = ["000100", "000101", "000102", "000103"]
    repo = _FakeBankingRepo(cheque_number_history=history)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="005999", amount=1000.0,
        processing_date=date(2026, 8, 2), banking_repo=repo,
    )
    assert any(i.type == "CHEQUE_SEQUENCE_ANOMALY" for i in indicators)


def test_pattern_detector_returns_empty_when_banking_data_unavailable():
    repo = _FakeBankingRepo(unavailable=True)
    indicators = pattern_detector.analyze(
        account_number="ACC1", cheque_number="000100", amount=1000.0,
        processing_date=date(2026, 8, 2), banking_repo=repo,
    )
    assert indicators == []


def test_pattern_detector_returns_empty_without_account_number():
    repo = _FakeBankingRepo()
    indicators = pattern_detector.analyze(
        account_number=None, cheque_number="000100", amount=1000.0,
        processing_date=date(2026, 8, 2), banking_repo=repo,
    )
    assert indicators == []


# ------------------------------------------------------------------
# image_tampering_detector -- proves the score is derived from actual
# pixel evidence, not a constant/fabricated value.
# ------------------------------------------------------------------

def _blank_cheque_canvas() -> np.ndarray:
    """A uniform, low-noise canvas standing in for a cheque image, with
    the same aspect ratio the real REGIONS fractions were calibrated
    against (1200x560)."""
    rng = np.random.default_rng(42)
    canvas = np.full((560, 1200, 3), 250, dtype=np.uint8)
    noise = rng.integers(-2, 3, size=canvas.shape, dtype=np.int16)
    return np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def test_image_tampering_analyze_returns_insufficient_data_for_missing_image():
    result = image_tampering_detector.analyze(None)
    assert result.image_tampering_score is None
    assert result.analysis_status == "INSUFFICIENT_DATA"


def test_image_tampering_score_increases_for_a_region_with_injected_pixel_noise():
    """Direct proof that the score responds to real per-image pixel
    evidence: two images differing ONLY in one region's texture must
    produce different scores, with the noisier region actually flagged."""
    import cv2

    clean = _blank_cheque_canvas()
    tampered = clean.copy()

    # Inject heavy synthetic noise into the amount region's pixel area
    # only (REGIONS["amount"] fractional bbox), simulating a pasted/
    # re-rendered patch with different texture from the rest of the cheque.
    h, w = tampered.shape[:2]
    x0, x1 = int(0.015 * w), int(0.230 * w)
    y0, y1 = int(0.390 * h), int(0.515 * h)
    rng = np.random.default_rng(7)
    heavy_noise = rng.integers(-80, 80, size=(y1 - y0, x1 - x0, 3), dtype=np.int16)
    region = tampered[y0:y1, x0:x1].astype(np.int16)
    tampered[y0:y1, x0:x1] = np.clip(region + heavy_noise, 0, 255).astype(np.uint8)

    clean_result = image_tampering_detector.analyze(clean)
    tampered_result = image_tampering_detector.analyze(tampered)

    assert clean_result.analysis_status == "COMPLETED"
    assert tampered_result.analysis_status == "COMPLETED"
    assert tampered_result.image_tampering_score > clean_result.image_tampering_score
    assert any(ind["type"] == "AMOUNT_REGION_INCONSISTENCY" for ind in tampered_result.indicators)


def test_image_tampering_score_differs_between_two_distinct_clean_images():
    """A constant/fabricated score would be identical for any two inputs;
    real pixel-derived statistics should not be perfectly identical
    across two independently-seeded images."""
    img_a = _blank_cheque_canvas()
    rng = np.random.default_rng(99)
    img_b = np.clip(
        np.full((560, 1200, 3), 250, dtype=np.int16) + rng.integers(-2, 3, size=(560, 1200, 3), dtype=np.int16),
        0, 255,
    ).astype(np.uint8)

    result_a = image_tampering_detector.analyze(img_a)
    result_b = image_tampering_detector.analyze(img_b)
    assert result_a.region_stats != result_b.region_stats


# ------------------------------------------------------------------
# duplicate_detector
# ------------------------------------------------------------------

def test_level2_exact_image_hash_match_confirms_duplicate():
    index = [ImageHashRecord(cheque_id="CHK-OLD", account_number="ACC1", cheque_number="000100",
                              image_hash="deadbeef", perceptual_hash="0000000000000000")]
    repo = _FakeBankingRepo(image_hashes=index)
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=100.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"},
        current_perceptual_hash="ffffffffffffffff", current_file_hash="deadbeef",
        banking_repo=repo,
    )
    assert result.duplicate_status == "CONFIRMED_DUPLICATE"
    assert result.image_match is True
    assert result.matched_cheque_id == "CHK-OLD"


def test_level3_near_duplicate_without_corroboration_is_only_potential():
    # High similarity (distance 1/64) but DIFFERENT account+cheque number
    # -- must not auto-confirm (this is the exact false positive this
    # milestone's instructions warn about).
    index = [ImageHashRecord(cheque_id="CHK-OLD", account_number="ACC-OTHER", cheque_number="000200",
                              image_hash="unrelated-hash", perceptual_hash="0000000000000001")]
    repo = _FakeBankingRepo(image_hashes=index)
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=100.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"},
        current_perceptual_hash="0000000000000000", current_file_hash="current-hash",
        banking_repo=repo,
    )
    assert result.duplicate_status == "POTENTIAL_DUPLICATE"
    assert result.perceptual_similarity is not None and result.perceptual_similarity >= 0.95


def test_level3_near_duplicate_with_account_and_cheque_corroboration_confirms():
    index = [ImageHashRecord(cheque_id="CHK-OLD", account_number="ACC1", cheque_number="000999",
                              image_hash="unrelated-hash", perceptual_hash="0000000000000001")]
    repo = _FakeBankingRepo(image_hashes=index)
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=100.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"},
        current_perceptual_hash="0000000000000000", current_file_hash="current-hash",
        banking_repo=repo,
    )
    assert result.duplicate_status == "CONFIRMED_DUPLICATE"


def test_same_account_different_cheque_same_amount_is_not_a_duplicate():
    """docs/19 S31's explicit false-positive example: same account,
    different cheque number, same amount (and implicitly same payee) must
    NOT automatically be classified as a duplicate."""
    repo = _FakeBankingRepo(image_hashes=[])  # no image evidence at all
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=250.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"},  # M4 already found no composite-key match
        current_perceptual_hash=None, current_file_hash="some-hash",
        banking_repo=repo,
    )
    assert result.duplicate_status == "NEW"


def test_rule_d4_flags_inconsistency_without_declaring_duplicate():
    from app.repositories.banking_repository import DuplicateMatch

    same_key = [DuplicateMatch(cheque_id="CHK-OLD", account_number="ACC1", cheque_number="000999",
                                payee_name="X", amount=999.0, cheque_date="2020-01-01")]
    repo = _FakeBankingRepo(same_key_records=same_key)
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=250.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"},
        current_perceptual_hash=None, current_file_hash="some-hash",
        banking_repo=repo,
    )
    assert result.d4_inconsistency is True
    assert result.d4_matched_cheque_id == "CHK-OLD"
    assert result.duplicate_status == "NEW"  # D4 is a separate signal, not an auto-duplicate


def test_duplicate_detector_fails_safe_when_banking_data_unavailable():
    repo = _FakeBankingRepo(unavailable=True)
    result = duplicate_detector.detect(
        account_number="ACC1", cheque_number="000999", amount=250.0, date_value="2026-08-01",
        validation_duplicate_check=None,
        current_perceptual_hash="abcd", current_file_hash="some-hash",
        banking_repo=repo,
    )
    assert result.analysis_status == "INSUFFICIENT_DATA"
    assert result.duplicate_status == "NEW"  # never silently treated as confirmed
