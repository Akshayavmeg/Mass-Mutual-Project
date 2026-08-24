"""Milestone 4 integration tests: the Validation Engine running against
real Milestone 1 synthetic banking data and real Milestone 3
upload->OCR->extraction pipeline output (docs/16_Validation_Engine.md).

Includes the 10 mandatory baseline test cases documented in
data/test_data/validation_test_cases.csv (docs/16 S43), one end-to-end
smoke test per Milestone 1 fraud/test category, the fail-safe
NOT_CHECKED behavior when banking data is unavailable, and the
POST/GET /cheques/{id}/validate(ion) API contract.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.banking_repository import (
    CSVBankingDataRepository,
    reset_banking_repository_for_testing,
)
from app.repositories.cheque_repository import get_cheque_repository
from app.services.validation import validation_service
from app.services.validation.exceptions import ChequeNotExtractedError

client = TestClient(app)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
GROUND_TRUTH_PATH = DATA_DIR / "test_data" / "cheques_ground_truth.csv"
VALIDATION_TEST_CASES_PATH = DATA_DIR / "test_data" / "validation_test_cases.csv"
REAL_BANKING_DATA_DIR = DATA_DIR / "mock_banking_data"

# The dataset was generated with this as its processing date (see
# generation_summary.json); pinning tests to it keeps DATE_WINDOW/staleness
# assertions deterministic regardless of the real wall-clock date a future
# test run happens to execute on.
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


def _one_sample_per_category() -> list[dict]:
    df = _ground_truth()
    if df.empty:
        return []
    return df.groupby("category").first().reset_index().to_dict("records")


_GROUND_TRUTH_DF = _ground_truth()
_SAMPLES = _one_sample_per_category()


def _upload_and_extract(image_relative_path: str) -> str:
    """Runs the real upload -> OCR -> extraction pipeline (Milestones 2-3)
    for a real Milestone 1 sample image and returns the resulting
    cheque_id."""
    full_path = DATA_DIR / image_relative_path
    content = full_path.read_bytes()
    upload = client.post("/api/v1/cheques/upload", files={"file": (full_path.name, content, "image/png")})
    assert upload.status_code == 201
    cheque_id = upload.json()["cheque_id"]
    ocr = client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    assert ocr.status_code == 200
    return cheque_id


def _validate(cheque_id: str, processing_date: date = DATASET_PROCESSING_DATE) -> dict:
    summary = validation_service.validate_cheque(cheque_id, processing_date=processing_date)
    return summary.as_dict()


def _row_for(cheque_id: str) -> dict:
    return _GROUND_TRUTH_DF[_GROUND_TRUTH_DF["cheque_id"] == cheque_id].iloc[0].to_dict()


# ----------------------------------------------------------------------
# 10 mandatory baseline test cases (docs/16 S43,
# data/test_data/validation_test_cases.csv) -- each maps to one specific
# check, verified by running the real pipeline against the exact cheque
# named in that CSV row.
# ----------------------------------------------------------------------

_BASELINE_CHECK_MAP = {
    "VAL-001": "ACCOUNT_EXISTS",
    "VAL-002": "ACCOUNT_EXISTS",
    "VAL-003": "ACCOUNT_STATUS",
    "VAL-004": "CHEQUE_SERIES",
    "VAL-005": "CHEQUE_SERIES",
    "VAL-006": "DATE_WINDOW",
    "VAL-007": "PAYEE_MATCH",
    "VAL-008": "PAYEE_MATCH",
    "VAL-009": "DUPLICATE_CHECK",
    "VAL-010": "AMOUNT_CONSISTENCY",
}


def _baseline_cases() -> list[dict]:
    if not VALIDATION_TEST_CASES_PATH.exists() or _GROUND_TRUTH_DF.empty:
        return []
    return pd.read_csv(VALIDATION_TEST_CASES_PATH, dtype=str).to_dict("records")


_BASELINE_CASES = _baseline_cases()


@pytest.mark.skipif(not _BASELINE_CASES, reason="Milestone 1 dataset not found")
@pytest.mark.parametrize("case", _BASELINE_CASES, ids=[c["test_id"] for c in _BASELINE_CASES])
def test_docs16_mandatory_baseline_case(case):
    cheque_id = case["cheque_id"]
    row = _row_for(cheque_id)
    check_name = _BASELINE_CHECK_MAP[case["test_id"]]

    live_cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(live_cheque_id)

    assert result["checks"][check_name]["status"] == case["expected"], (
        f"{case['test_id']} ({case['name']}): expected {check_name}={case['expected']}, "
        f"got {result['checks'][check_name]}"
    )


# ----------------------------------------------------------------------
# One end-to-end smoke test per Milestone 1 category
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_category_cheque_passes_all_checks():
    row = next(r for r in _SAMPLES if r["category"] == "VALID")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["overall_validation_status"] == "PASS"
    assert result["failed_checks"] == []


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_invalid_account_category_fails_account_checks():
    row = next(r for r in _SAMPLES if r["category"] == "INVALID_ACCOUNT")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["overall_validation_status"] == "FAIL"
    assert "ACCOUNT_EXISTS" in result["failed_checks"] or "ACCOUNT_STATUS" in result["failed_checks"]


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_stopped_cheque_category_fails_with_critical_severity():
    row = next(r for r in _SAMPLES if r["category"] == "STOPPED_CHEQUE")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["overall_validation_status"] == "FAIL"
    assert result["checks"]["CHEQUE_STATUS"]["status"] == "FAIL"
    assert result["checks"]["CHEQUE_STATUS"]["severity"] == "CRITICAL"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_stale_cheque_category_fails_date_window():
    row = next(r for r in _SAMPLES if r["category"] == "STALE_CHEQUE")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["DATE_WINDOW"]["status"] == "FAIL"
    assert "FAIL" in result["overall_validation_status"]


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_future_dated_category_fails_date_window():
    row = next(r for r in _SAMPLES if r["category"] == "FUTURE_DATED")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["DATE_WINDOW"]["status"] == "FAIL"
    assert "future-dated" in result["checks"]["DATE_WINDOW"]["message"]


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_payee_tampered_category_fails_payee_match():
    row = next(r for r in _SAMPLES if r["category"] == "PAYEE_TAMPERED")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["PAYEE_MATCH"]["status"] == "FAIL"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_amount_tampered_category_fails_amount_consistency():
    row = next(r for r in _SAMPLES if r["category"] == "AMOUNT_TAMPERED")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["AMOUNT_CONSISTENCY"]["status"] == "FAIL"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_cheque_series_anomaly_category_fails_cheque_series():
    row = next(r for r in _SAMPLES if r["category"] == "CHEQUE_SERIES_ANOMALY")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["CHEQUE_SERIES"]["status"] == "FAIL"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_duplicate_category_fails_duplicate_check():
    row = next(r for r in _SAMPLES if r["category"] == "DUPLICATE")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["checks"]["DUPLICATE_CHECK"]["status"] == "FAIL"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_multiple_anomalies_category_fails_more_than_one_check():
    row = next(r for r in _SAMPLES if r["category"] == "MULTIPLE_ANOMALIES")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert len(result["failed_checks"]) >= 2


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_signature_mismatch_category_is_out_of_scope_for_validation_engine():
    """Module boundary check (docs/16 S47): the Validation Engine does not
    do signature comparison, so a cheque whose ONLY defect is a forged
    signature must not fail any of the 12 validation checks here -- that
    detection is Milestone 5/7's job."""
    row = next(r for r in _SAMPLES if r["category"] == "SIGNATURE_MISMATCH")
    cheque_id = _upload_and_extract(row["image_path"])
    result = _validate(cheque_id)
    assert result["overall_validation_status"] == "PASS"
    assert result["failed_checks"] == []


# ----------------------------------------------------------------------
# Fail-safe behavior: unavailable banking data must never look like PASS
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_unavailable_banking_data_routes_to_not_checked_not_pass(tmp_path):
    row = next(r for r in _SAMPLES if r["category"] == "VALID")
    cheque_id = _upload_and_extract(row["image_path"])

    broken_repo = reset_banking_repository_for_testing(tmp_path)  # empty dir -> no CSVs
    result = validation_service.validate_cheque(
        cheque_id, processing_date=DATASET_PROCESSING_DATE, banking_repo=broken_repo,
    ).as_dict()

    assert result["overall_validation_status"] != "PASS"
    assert "ACCOUNT_EXISTS" in result["not_checked"]
    assert result["checks"]["ACCOUNT_EXISTS"]["status"] == "NOT_CHECKED"
    assert result["checks"]["CHEQUE_STATUS"]["status"] == "NOT_CHECKED"
    assert result["checks"]["DUPLICATE_CHECK"]["status"] == "NOT_CHECKED"


# ----------------------------------------------------------------------
# Required-field / missing-data fail-safe (crafted record, no real image
# needed -- this exercises a case the real dataset doesn't produce)
# ----------------------------------------------------------------------

def test_missing_required_field_fails_but_does_not_crash():
    repo = get_cheque_repository()
    repo.save("CHK-TEST-MISSING", {
        "cheque_id": "CHK-TEST-MISSING",
        "extraction": {
            "fields": {
                "cheque_number": {"value": "000100"},
                "account_number": {"value": "9000010001"},
                # amount, date, payee_name all missing
            },
        },
    })
    result = validation_service.validate_cheque(
        "CHK-TEST-MISSING", processing_date=DATASET_PROCESSING_DATE,
    ).as_dict()
    assert result["checks"]["REQUIRED_FIELDS"]["status"] == "FAIL"
    assert result["overall_validation_status"] == "FAIL"


def test_validate_cheque_raises_when_extraction_not_run():
    repo = get_cheque_repository()
    repo.save("CHK-TEST-NO-EXTRACTION", {"cheque_id": "CHK-TEST-NO-EXTRACTION", "extraction": None})
    with pytest.raises(ChequeNotExtractedError):
        validation_service.validate_cheque("CHK-TEST-NO-EXTRACTION")


def test_validate_cheque_raises_keyerror_for_unknown_cheque():
    with pytest.raises(KeyError):
        validation_service.validate_cheque("CHK-DOES-NOT-EXIST")


# ----------------------------------------------------------------------
# Live-session duplicate detection (two cheques processed in the same
# run, neither present in the historical CSV)
# ----------------------------------------------------------------------

def _crafted_extraction(*, account_number, cheque_number, amount, cheque_date, payee_name):
    return {
        "fields": {
            "cheque_number": {"value": cheque_number},
            "account_number": {"value": account_number},
            "amount": {"value": amount},
            "date": {"value": cheque_date},
            "payee_name": {"value": payee_name},
            "routing_transit_number": {"value": "121000358"},
            "amount_in_words": {"value": None},
        },
    }


def test_live_session_duplicate_is_detected_between_two_cheques_processed_this_run():
    repo = get_cheque_repository()
    common = dict(account_number="9000010001", cheque_number="000110", amount=250.0,
                  cheque_date="2026-08-01", payee_name="Fatima Petrov")
    repo.save("CHK-LIVE-1", {"cheque_id": "CHK-LIVE-1", "extraction": _crafted_extraction(**common)})
    repo.save("CHK-LIVE-2", {"cheque_id": "CHK-LIVE-2", "extraction": _crafted_extraction(**common)})

    validation_service.validate_cheque("CHK-LIVE-1", processing_date=DATASET_PROCESSING_DATE)
    result2 = validation_service.validate_cheque(
        "CHK-LIVE-2", processing_date=DATASET_PROCESSING_DATE,
    ).as_dict()

    assert result2["checks"]["DUPLICATE_CHECK"]["status"] == "FAIL"
    assert result2["checks"]["DUPLICATE_CHECK"]["details"]["matched_cheque_id"] == "CHK-LIVE-1"


# ----------------------------------------------------------------------
# API contract: POST/GET /cheques/{id}/validate(ion)
# ----------------------------------------------------------------------

def test_validate_endpoint_returns_404_for_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/validate")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CHEQUE_NOT_FOUND"


def test_validate_endpoint_returns_422_when_ocr_not_run():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("blank.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    resp = client.post(f"/api/v1/cheques/{cheque_id}/validate")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "CHEQUE_NOT_EXTRACTED"


def test_get_validation_endpoint_returns_404_before_validate_has_run():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")

    resp = client.get(f"/api/v1/cheques/{cheque_id}/validation")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "VALIDATION_NOT_RUN"


def test_validate_then_get_validation_returns_consistent_result():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")

    post_result = client.post(f"/api/v1/cheques/{cheque_id}/validate").json()
    get_result = client.get(f"/api/v1/cheques/{cheque_id}/validation").json()

    assert post_result["overall_validation_status"] == get_result["overall_validation_status"]
    assert post_result["checks"] == get_result["checks"]


def test_get_cheque_detail_shows_validated_processing_status():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")

    detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
    assert detail["processing_status"] == "VALIDATED"
