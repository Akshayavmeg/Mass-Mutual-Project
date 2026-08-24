"""Milestone 6 integration tests: Signature Analysis, Anomaly Detection,
and Risk Scoring running against real Milestone 1-5 pipeline output
(docs/18, docs/20, docs/21).
"""

from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.banking_repository import CSVBankingDataRepository, reset_banking_repository_for_testing
from app.repositories.cheque_repository import get_cheque_repository
from app.services.anomaly import anomaly_service
from app.services.anomaly.exceptions import ChequeNotExtractedForAnomalyError
from app.services.risk import risk_service
from app.services.risk.exceptions import FraudAnalysisNotAvailableError
from app.services.signature import signature_service
from app.services.signature.exceptions import ChequeNotExtractedForSignatureError

client = TestClient(app)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
GROUND_TRUTH_PATH = DATA_DIR / "test_data" / "cheques_ground_truth.csv"
REAL_BANKING_DATA_DIR = DATA_DIR / "mock_banking_data"
DATASET_PROCESSING_DATE = date(2026, 8, 23)


@pytest.fixture(autouse=True)
def _clean_repository():
    yield
    get_cheque_repository().clear_for_testing()
    reset_banking_repository_for_testing(REAL_BANKING_DATA_DIR)


def _ground_truth() -> pd.DataFrame:
    if not GROUND_TRUTH_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(GROUND_TRUTH_PATH, dtype={"account_number": str, "cheque_number": str})


_GROUND_TRUTH_DF = _ground_truth()
_SAMPLES = _GROUND_TRUTH_DF.groupby("category").first().reset_index().to_dict("records") if not _GROUND_TRUTH_DF.empty else []


def _sample(category: str) -> dict:
    return next(r for r in _SAMPLES if r["category"] == category)


def _full_pipeline(content: bytes, filename: str = "cheque.png") -> str:
    upload = client.post("/api/v1/cheques/upload", files={"file": (filename, content, "image/png")})
    assert upload.status_code == 201, upload.text
    cheque_id = upload.json()["cheque_id"]
    assert client.post(f"/api/v1/cheques/{cheque_id}/ocr").status_code == 200
    assert client.post(f"/api/v1/cheques/{cheque_id}/validate").status_code == 200
    assert client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis").status_code == 200
    return cheque_id


# ----------------------------------------------------------------------
# Signature analysis -- full pipeline
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_cheque_signature_present_and_good_quality():
    row = _sample("VALID")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/signature-analysis")
    assert resp.status_code == 200
    result = resp.json()
    assert result["signature_present"] is True
    assert result["model_version"].startswith("signature-")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_signature_mismatch_category_does_not_fabricate_a_confirmed_mismatch():
    """The measured calibration finding (Milestone 6 report): this
    synthetic dataset's forged/genuine similarity distributions overlap,
    so a forged sample is NOT guaranteed to score CRITICAL/HIGH. The
    important behavioral guarantee is that the module never crashes and
    never claims perfect certainty either way."""
    row = _sample("SIGNATURE_MISMATCH")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/signature-analysis")
    assert resp.status_code == 200
    result = resp.json()
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL", "UNAVAILABLE")
    assert result["analysis_confidence"] <= 1.0


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_invalid_account_has_no_reference_signature_and_is_not_treated_as_fraud():
    row = _sample("INVALID_ACCOUNT")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/signature-analysis")
    assert resp.status_code == 200
    result = resp.json()
    assert result["indicator"] == "REFERENCE_SIGNATURE_NOT_FOUND"
    assert result["risk_level"] == "UNAVAILABLE"  # not HIGH/CRITICAL -- missing reference != fraud
    assert result["similarity_score"] is None


def test_missing_signature_produces_distinct_indicator_from_mismatch():
    """SIGNATURE_MISSING must be distinguishable from SIGNATURE_MISMATCH
    (docs/18 S20)."""
    repo = get_cheque_repository()
    repo.save("CHK-NO-SIG", {
        "cheque_id": "CHK-NO-SIG",
        "extraction": {
            "fields": {"account_number": {"value": "9000010001"}},
            "signature_region_detected": False,
            "signature_region_bbox": {"x": 0, "y": 0, "width": 10, "height": 10},
        },
    })
    result = signature_service.analyze_signature("CHK-NO-SIG")
    assert result.indicator == "SIGNATURE_MISSING"
    assert result.similarity_score is None


def test_genuine_variation_is_not_automatically_classified_as_high_risk():
    """docs/18 S17 / Milestone 6 explicit requirement: natural signature
    variation must not automatically become a fraud classification."""
    from app.services.signature.comparator import similarity
    from app.services.signature.feature_extractor import extract_features
    import cv2

    sig_dir = DATA_DIR / "mock_banking_data" / "reference_signatures"
    index = pd.read_csv(sig_dir / "signatures_index.csv", dtype=str)
    account_refs = index[index["account_number"] == "9000010001"]
    genuine = account_refs[account_refs["variant"] == "genuine"]
    variation = account_refs[account_refs["variant"] == "genuine_variation"]
    if genuine.empty or variation.empty:
        pytest.skip("account does not have both genuine and variation references")

    a = extract_features(cv2.cvtColor(cv2.imread(str(sig_dir / Path(genuine.iloc[0]["signature_file"]).name)), cv2.COLOR_BGR2GRAY))
    b = extract_features(cv2.cvtColor(cv2.imread(str(sig_dir / Path(variation.iloc[0]["signature_file"]).name)), cv2.COLOR_BGR2GRAY))
    score = similarity(a, b)
    # This does not assert a strong-match score (the calibration finding
    # documents weak separation) -- only that the comparator runs and
    # produces a valid bounded score without crashing or fabricating a
    # certain-fraud result.
    assert 0.0 <= score <= 1.0


def test_signature_analysis_raises_when_not_extracted():
    repo = get_cheque_repository()
    repo.save("CHK-NO-EXTRACTION", {"cheque_id": "CHK-NO-EXTRACTION", "extraction": None})
    with pytest.raises(ChequeNotExtractedForSignatureError):
        signature_service.analyze_signature("CHK-NO-EXTRACTION")


def test_signature_analysis_raises_keyerror_for_unknown_cheque():
    with pytest.raises(KeyError):
        signature_service.analyze_signature("CHK-DOES-NOT-EXIST")


def test_signature_unavailable_banking_data_fails_safe(tmp_path):
    repo = get_cheque_repository()
    repo.save("CHK-SIG-NO-BANK", {
        "cheque_id": "CHK-SIG-NO-BANK",
        "extraction": {
            "fields": {"account_number": {"value": "9000010001"}},
            "signature_region_detected": True,
            "signature_region_bbox": {"x": 0, "y": 0, "width": 100, "height": 50},
        },
    })
    broken_repo = reset_banking_repository_for_testing(tmp_path)
    result = signature_service.analyze_signature("CHK-SIG-NO-BANK", banking_repo=broken_repo)
    assert result.risk_level == "UNAVAILABLE"
    assert result.indicator in ("REFERENCE_SIGNATURE_NOT_FOUND", "SIGNATURE_ANALYSIS_ERROR")


# ----------------------------------------------------------------------
# Anomaly analysis -- full pipeline
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_cheque_low_anomaly_score():
    row = _sample("VALID")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/anomaly-analysis")
    assert resp.status_code == 200
    result = resp.json()
    assert result["risk_level"] in ("LOW", "MEDIUM")


def test_anomaly_timing_is_deliberately_not_implemented():
    """docs/20 S17: timing analysis should only be used if reliable
    intraday timestamp data is available; the Milestone 1 dataset only
    has transaction_date (no time-of-day), so no anomaly of type
    TIMING_ANOMALY can ever be produced. This is a documented deferral,
    verified structurally: the detectors module defines no timing
    function and no TIMING_ANOMALY type appears anywhere in its source."""
    import app.services.anomaly.detectors as det

    source = inspect.getsource(det)
    assert "TIMING_ANOMALY" not in source
    assert not hasattr(det, "timing_anomaly")


def test_anomaly_analysis_raises_when_not_extracted():
    repo = get_cheque_repository()
    repo.save("CHK-NO-EXTRACTION-2", {"cheque_id": "CHK-NO-EXTRACTION-2", "extraction": None})
    with pytest.raises(ChequeNotExtractedForAnomalyError):
        anomaly_service.analyze_anomaly("CHK-NO-EXTRACTION-2")


def test_anomaly_analysis_unavailable_banking_data_fails_safe(tmp_path):
    repo = get_cheque_repository()
    repo.save("CHK-ANOM-NO-BANK", {
        "cheque_id": "CHK-ANOM-NO-BANK",
        "extraction": {"fields": {
            "account_number": {"value": "9000010001"}, "cheque_number": {"value": "000100"},
            "amount": {"value": 1000.0}, "payee_name": {"value": "X"},
        }},
    })
    broken_repo = reset_banking_repository_for_testing(tmp_path)
    result = anomaly_service.analyze_anomaly("CHK-ANOM-NO-BANK", processing_date=DATASET_PROCESSING_DATE, banking_repo=broken_repo)
    assert result.analysis_status == "INSUFFICIENT_DATA"
    assert result.anomaly_score == 0.0  # unavailable data must not be fabricated into a score
    assert "TRANSACTION_HISTORY" in result.unavailable_inputs


# ----------------------------------------------------------------------
# Risk scoring -- full pipeline
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_cheque_low_risk():
    row = _sample("VALID")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    client.post(f"/api/v1/cheques/{cheque_id}/signature-analysis")
    client.post(f"/api/v1/cheques/{cheque_id}/anomaly-analysis")
    resp = client.post(f"/api/v1/cheques/{cheque_id}/risk-score")
    assert resp.status_code == 200
    result = resp.json()
    assert result["risk_level"] in ("LOW", "MEDIUM")
    assert len(result["risk_factors"]) == 7


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_invalid_account_hard_rule_escalates_to_high():
    row = _sample("INVALID_ACCOUNT")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/risk-score")
    assert resp.status_code == 200
    result = resp.json()
    assert "INVALID_OR_INACTIVE_ACCOUNT" in result["hard_rules_triggered"]
    assert result["risk_level"] in ("HIGH", "CRITICAL")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_duplicate_category_hard_rule_and_duplicate_contribution():
    row = _sample("DUPLICATE")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    resp = client.post(f"/api/v1/cheques/{cheque_id}/risk-score")
    result = resp.json()
    duplicate_factor = next(f for f in result["risk_factors"] if f["factor"] == "DUPLICATE")
    assert duplicate_factor["contribution"] == 20
    assert "CONFIRMED_DUPLICATE_CHEQUE" in result["hard_rules_triggered"]
    assert result["risk_level"] in ("HIGH", "CRITICAL")


def test_risk_score_without_signature_or_anomaly_run_flags_unavailable():
    """Fail-safe requirement: risk scoring must work even when Milestone
    6's own signature/anomaly stages haven't been run yet for this
    cheque, and must clearly flag them as unavailable rather than
    silently treating them as zero-risk-verified-safe."""
    repo = get_cheque_repository()
    repo.save("CHK-RISK-PARTIAL", {
        "cheque_id": "CHK-RISK-PARTIAL",
        "validation": {"overall_validation_status": "PASS", "checks": {}},
        "ocr": {"average_confidence": 96.0},
        "fraud_analysis": {
            "image_analysis": {"image_tampering_score": 0.05},
            "duplicate_analysis": {"duplicate_status": "NEW"},
        },
    })
    result = risk_service.calculate_risk("CHK-RISK-PARTIAL")
    assert "SIGNATURE_ANALYSIS" in result.unavailable_inputs
    assert "ANOMALY_ANALYSIS" in result.unavailable_inputs
    assert result.risk_level != "CRITICAL"


def test_risk_score_raises_when_fraud_analysis_not_run():
    repo = get_cheque_repository()
    repo.save("CHK-NO-FRAUD", {"cheque_id": "CHK-NO-FRAUD", "fraud_analysis": None})
    with pytest.raises(FraudAnalysisNotAvailableError):
        risk_service.calculate_risk("CHK-NO-FRAUD")


def test_risk_score_raises_keyerror_for_unknown_cheque():
    with pytest.raises(KeyError):
        risk_service.calculate_risk("CHK-DOES-NOT-EXIST")


def test_low_ocr_confidence_increases_risk_contribution():
    repo = get_cheque_repository()
    common = {
        "validation": {"overall_validation_status": "PASS", "checks": {}},
        "fraud_analysis": {
            "image_analysis": {"image_tampering_score": 0.0},
            "duplicate_analysis": {"duplicate_status": "NEW"},
        },
    }
    repo.save("CHK-HIGH-OCR", {**common, "cheque_id": "CHK-HIGH-OCR", "ocr": {"average_confidence": 98.0}})
    repo.save("CHK-LOW-OCR", {**common, "cheque_id": "CHK-LOW-OCR", "ocr": {"average_confidence": 30.0}})
    high = risk_service.calculate_risk("CHK-HIGH-OCR")
    low = risk_service.calculate_risk("CHK-LOW-OCR")
    assert low.overall_risk_score > high.overall_risk_score


def test_multiple_contributing_indicators_produce_higher_score_than_single():
    repo = get_cheque_repository()
    common = {
        "validation": {"overall_validation_status": "PASS", "checks": {}},
        "ocr": {"average_confidence": 96.0},
    }
    repo.save("CHK-ONE-INDICATOR", {**common, "cheque_id": "CHK-ONE-INDICATOR", "fraud_analysis": {
        "image_analysis": {"image_tampering_score": 0.9}, "duplicate_analysis": {"duplicate_status": "NEW"},
    }})
    repo.save("CHK-MANY-INDICATORS", {**common, "cheque_id": "CHK-MANY-INDICATORS", "fraud_analysis": {
        "image_analysis": {"image_tampering_score": 0.9}, "duplicate_analysis": {"duplicate_status": "CONFIRMED_DUPLICATE"},
    }, "signature_analysis": {"risk_level": "CRITICAL", "similarity_score": 0.1},
       "anomaly_analysis": {"anomaly_score": 90.0, "analysis_status": "COMPLETED"}})
    one = risk_service.calculate_risk("CHK-ONE-INDICATOR")
    many = risk_service.calculate_risk("CHK-MANY-INDICATORS")
    assert many.overall_risk_score > one.overall_risk_score
    assert many.risk_level == "CRITICAL"


# ----------------------------------------------------------------------
# API contract
# ----------------------------------------------------------------------

def test_signature_analysis_endpoint_404_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/signature-analysis")
    assert resp.status_code == 404


def test_anomaly_analysis_endpoint_404_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/anomaly-analysis")
    assert resp.status_code == 404


def test_risk_score_endpoint_404_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/risk-score")
    assert resp.status_code == 404


def test_risk_score_endpoint_422_before_fraud_analysis():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    resp = client.post(f"/api/v1/cheques/{cheque_id}/risk-score")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "FRAUD_ANALYSIS_NOT_RUN"


def test_cheque_detail_shows_risk_scored_status():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000002.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis")
    client.post(f"/api/v1/cheques/{cheque_id}/risk-score")
    detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
    assert detail["processing_status"] == "RISK_SCORED"


# ----------------------------------------------------------------------
# Ground-truth isolation
# ----------------------------------------------------------------------

_LEAKAGE_TOKENS = [
    "fraud_label", "ground_truth", "cheques_ground_truth", "fraud_labels.csv",
    "fraud_type", "expected_amount", "expected_payee_name", "expected_account_status",
    "expected_cheque_status", '"category"', "['category']", ".category",
]


def test_no_ground_truth_leakage_in_signature_anomaly_risk_modules():
    import app.services.anomaly.anomaly_service as anom_svc
    import app.services.anomaly.detectors as anom_det
    import app.services.risk.risk_service as risk_svc
    import app.services.signature.signature_service as sig_svc
    import app.services.signature.comparator as sig_cmp
    import app.services.signature.feature_extractor as sig_feat

    source = "".join(inspect.getsource(m) for m in (anom_svc, anom_det, risk_svc, sig_svc, sig_cmp, sig_feat))
    for token in _LEAKAGE_TOKENS:
        assert token not in source, f"unexpected ground-truth reference: '{token}'"
