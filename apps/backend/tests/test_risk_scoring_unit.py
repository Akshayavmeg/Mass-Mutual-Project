"""Unit tests for the Milestone 6 Risk Scoring factor-mapping functions
(docs/21_Risk_Scoring.md S7-S13), in isolation from the full
cheque-record orchestration (covered in
test_signature_anomaly_risk_milestone6.py).
"""

from __future__ import annotations

from app.services.risk import risk_service


def test_tampering_factor_bands():
    none_case = risk_service._tampering_factor({"image_analysis": {"image_tampering_score": 0.05}})
    strong_case = risk_service._tampering_factor({"image_analysis": {"image_tampering_score": 0.9}})
    assert none_case.contribution == 0
    assert strong_case.contribution == 20


def test_tampering_factor_unavailable_when_no_score():
    factor = risk_service._tampering_factor({"image_analysis": {"image_tampering_score": None}})
    assert factor.contribution == 0
    assert "unavailable" in factor.reason.lower()


def test_signature_factor_maps_risk_levels():
    low, unavailable_low = risk_service._signature_factor({"risk_level": "LOW", "similarity_score": 0.9})
    critical, unavailable_critical = risk_service._signature_factor({"risk_level": "CRITICAL", "similarity_score": 0.1})
    assert low.contribution == 0
    assert critical.contribution == 20
    assert unavailable_low is False
    assert unavailable_critical is False


def test_signature_factor_missing_reference_is_unavailable_not_risky():
    """Fail-safe requirement: a missing reference signature must
    contribute ZERO risk points (not be treated as evidence of fraud),
    while still being flagged as an unavailable input."""
    factor, unavailable = risk_service._signature_factor({"risk_level": "UNAVAILABLE", "similarity_score": None})
    assert factor.contribution == 0
    assert unavailable is True


def test_signature_factor_not_run_is_unavailable():
    factor, unavailable = risk_service._signature_factor(None)
    assert factor.contribution == 0
    assert unavailable is True


def test_duplicate_factor_maps_status():
    new = risk_service._duplicate_factor({"duplicate_analysis": {"duplicate_status": "NEW"}})
    potential = risk_service._duplicate_factor({"duplicate_analysis": {"duplicate_status": "POTENTIAL_DUPLICATE"}})
    confirmed = risk_service._duplicate_factor({"duplicate_analysis": {"duplicate_status": "CONFIRMED_DUPLICATE"}})
    assert new.contribution == 0
    assert potential.contribution == 10
    assert confirmed.contribution == 20


def test_anomaly_factor_scales_into_20_point_budget():
    factor, unavailable = risk_service._anomaly_factor({"anomaly_score": 50.0, "analysis_status": "COMPLETED"})
    assert factor.contribution == 10.0  # 50/100 * 20
    assert unavailable is False


def test_anomaly_factor_not_run_is_unavailable():
    factor, unavailable = risk_service._anomaly_factor(None)
    assert factor.contribution == 0
    assert unavailable is True


def test_anomaly_factor_insufficient_data_flagged_unavailable():
    factor, unavailable = risk_service._anomaly_factor({"anomaly_score": 0.0, "analysis_status": "INSUFFICIENT_DATA"})
    assert unavailable is True


def test_validation_factor_maps_status():
    passed = risk_service._validation_factor({"overall_validation_status": "PASS", "checks": {}})
    failed = risk_service._validation_factor({"overall_validation_status": "FAIL", "checks": {}})
    assert passed.contribution == 0
    assert failed.contribution == 10


def test_validation_factor_not_run_is_max_contribution():
    factor = risk_service._validation_factor(None)
    assert factor.contribution == factor.max_contribution


def test_ocr_factor_bands():
    high_conf = risk_service._ocr_factor({"average_confidence": 98.0})
    low_conf = risk_service._ocr_factor({"average_confidence": 40.0})
    assert high_conf.contribution == 0
    assert low_conf.contribution == 5


def test_classify_bands():
    assert risk_service._classify(0) == "LOW"
    assert risk_service._classify(24) == "LOW"
    assert risk_service._classify(25) == "MEDIUM"
    assert risk_service._classify(50) == "HIGH"
    assert risk_service._classify(75) == "CRITICAL"
    assert risk_service._classify(100) == "CRITICAL"
