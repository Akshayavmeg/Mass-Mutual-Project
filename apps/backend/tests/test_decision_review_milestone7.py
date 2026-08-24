"""Milestone 7 integration tests: Decision Engine and Manual Review
Workflow running against real Milestone 1-6 pipeline output
(docs/22, docs/23).
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.banking_repository import reset_banking_repository_for_testing
from app.repositories.cheque_repository import get_cheque_repository
from app.repositories.review_repository import get_review_repository
from app.services.decision import decision_service
from app.services.decision.exceptions import RiskAssessmentNotAvailableError
from app.services.review import id_generator as review_id_generator

client = TestClient(app)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
GROUND_TRUTH_PATH = DATA_DIR / "test_data" / "cheques_ground_truth.csv"
REAL_BANKING_DATA_DIR = DATA_DIR / "mock_banking_data"

REVIEWER_HEADERS = {"X-User-Role": "REVIEWER"}
OPERATOR_HEADERS = {"X-User-Role": "OPERATOR"}


@pytest.fixture(autouse=True)
def _clean_repository():
    yield
    get_cheque_repository().clear_for_testing()
    get_review_repository().clear_for_testing()
    reset_banking_repository_for_testing(REAL_BANKING_DATA_DIR)
    review_id_generator.reset_counters_for_testing()


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
    for step in ("ocr", "validate", "fraud-analysis", "signature-analysis", "anomaly-analysis", "risk-score"):
        resp = client.post(f"/api/v1/cheques/{cheque_id}/{step}")
        assert resp.status_code == 200, f"{step}: {resp.text}"
    return cheque_id


def _decide(cheque_id: str) -> dict:
    resp = client.post(f"/api/v1/cheques/{cheque_id}/decision")
    assert resp.status_code == 200, resp.text
    return resp.json()


# ----------------------------------------------------------------------
# Full-pipeline decision scenarios
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_low_risk_cheque_approves():
    row = _sample("VALID")
    # Use the second VALID sample deterministically to avoid the first
    # one's known potential-duplicate calibration finding from Milestone 5/6.
    valid_rows = _GROUND_TRUTH_DF[_GROUND_TRUTH_DF["category"] == "VALID"]
    row = valid_rows.iloc[1].to_dict() if len(valid_rows) > 1 else row
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    result = _decide(cheque_id)
    assert result["decision"] in ("APPROVE", "REVIEW")  # never REJECT for a clean valid cheque
    if result["decision"] == "APPROVE":
        assert result["requires_manual_review"] is False
        assert result["risk_level"] == "LOW"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_invalid_account_hard_rejects():
    row = _sample("INVALID_ACCOUNT")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    result = _decide(cheque_id)
    assert result["decision"] == "REJECT"
    assert "ACCOUNT_INVALID_HARD_REJECT" in result["triggered_rules"]
    assert result["requires_manual_review"] is False


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_duplicate_category_confirmed_duplicate_hard_rejects():
    row = _sample("DUPLICATE")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    result = _decide(cheque_id)
    assert result["decision"] == "REJECT"
    assert "CONFIRMED_DUPLICATE_HARD_REJECT" in result["triggered_rules"]


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_stopped_cheque_produces_explainable_review_or_reject():
    row = _sample("STOPPED_CHEQUE")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    result = _decide(cheque_id)
    assert result["decision"] in ("REVIEW", "REJECT")
    assert result["reasons"]
    assert len(result["reasons"]) == len(result["triggered_rules"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_multiple_anomalies_category_produces_review_or_reject_with_multiple_reasons():
    row = _sample("MULTIPLE_ANOMALIES")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    result = _decide(cheque_id)
    assert result["decision"] in ("REVIEW", "REJECT")
    assert result["decision"] != "APPROVE"


def test_review_decision_creates_a_review_case():
    repo = get_cheque_repository()
    repo.save("CHK-REVIEW-TEST", {
        "cheque_id": "CHK-REVIEW-TEST",
        "extraction": {"fields": {"account_number": {"value": "9000010001"}, "cheque_number": {"value": "000100"}}},
        "validation": {"overall_validation_status": "PASS"},
        "ocr": {"average_confidence": 96.0},
        "fraud_analysis": {
            "risk_level": "LOW",
            "duplicate_analysis": {"duplicate_status": "POTENTIAL_DUPLICATE"},
            "image_analysis": {"image_tampering_score": 0.0},
            "indicators": [],
        },
        "signature_analysis": {"risk_level": "LOW", "similarity_score": 0.9},
        "anomaly_analysis": {"risk_level": "LOW"},
        "risk_assessment": {"overall_risk_score": 15.0, "risk_level": "LOW", "hard_rules_triggered": [], "unavailable_inputs": []},
    })
    result = decision_service.make_decision("CHK-REVIEW-TEST")
    assert result.decision == "REVIEW"

    resp = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS)
    assert resp.status_code == 200
    cases = resp.json()["cases"]
    matching = [c for c in cases if c["cheque_id"] == "CHK-REVIEW-TEST"]
    assert len(matching) == 1
    assert matching[0]["status"] == "QUEUED"
    assert matching[0]["automated_decision"]["decision"] == "REVIEW"


def test_approve_decision_does_not_create_a_review_case():
    repo = get_cheque_repository()
    repo.save("CHK-APPROVE-TEST", {
        "cheque_id": "CHK-APPROVE-TEST",
        "extraction": {"fields": {"account_number": {"value": "9000010001"}, "cheque_number": {"value": "000100"}}},
        "validation": {"overall_validation_status": "PASS"},
        "ocr": {"average_confidence": 98.0},
        "fraud_analysis": {
            "risk_level": "LOW", "duplicate_analysis": {"duplicate_status": "NEW"},
            "image_analysis": {"image_tampering_score": 0.0}, "indicators": [],
        },
        "signature_analysis": {"risk_level": "LOW", "similarity_score": 0.95},
        "anomaly_analysis": {"risk_level": "LOW"},
        "risk_assessment": {"overall_risk_score": 5.0, "risk_level": "LOW", "hard_rules_triggered": [], "unavailable_inputs": []},
    })
    result = decision_service.make_decision("CHK-APPROVE-TEST")
    assert result.decision == "APPROVE"
    resp = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS)
    matching = [c for c in resp.json()["cases"] if c["cheque_id"] == "CHK-APPROVE-TEST"]
    assert matching == []


# ----------------------------------------------------------------------
# Fail-safe / error paths
# ----------------------------------------------------------------------

def test_decision_raises_when_risk_not_run():
    get_cheque_repository().save("CHK-NO-RISK", {"cheque_id": "CHK-NO-RISK", "risk_assessment": None})
    with pytest.raises(RiskAssessmentNotAvailableError):
        decision_service.make_decision("CHK-NO-RISK")


def test_decision_endpoint_422_before_risk_score():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    resp = client.post(f"/api/v1/cheques/{cheque_id}/decision")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "RISK_ASSESSMENT_NOT_RUN"


def test_decision_endpoint_404_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/decision")
    assert resp.status_code == 404


def test_get_decision_404_before_post():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    resp = client.get(f"/api/v1/cheques/{cheque_id}/decision")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DECISION_NOT_RUN"


def test_post_then_get_decision_consistent():
    row = _sample("VALID") if _SAMPLES else None
    if row is None:
        pytest.skip("Milestone 1 dataset not found")
    cheque_id = _full_pipeline((DATA_DIR / row["image_path"]).read_bytes())
    post_result = client.post(f"/api/v1/cheques/{cheque_id}/decision").json()
    get_result = client.get(f"/api/v1/cheques/{cheque_id}/decision").json()
    assert post_result["decision"] == get_result["decision"]
    assert post_result["reasons"] == get_result["reasons"]


# ----------------------------------------------------------------------
# Review API contract + authorization
# ----------------------------------------------------------------------

def test_review_queue_requires_authentication():
    resp = client.get("/api/v1/reviews")
    assert resp.status_code == 401


def test_review_queue_rejects_unrecognized_role():
    resp = client.get("/api/v1/reviews", headers={"X-User-Role": "NOT_A_ROLE"})
    assert resp.status_code == 401


def test_operator_cannot_assign_review_case():
    """Reviewer-only operation must not be callable by an unauthorized role."""
    resp = client.post(
        "/api/v1/reviews/REV-2026-000001/assign", json={"reviewer_id": "USR-002"}, headers=OPERATOR_HEADERS,
    )
    assert resp.status_code == 403


def test_operator_cannot_complete_review_case():
    resp = client.post(
        "/api/v1/reviews/REV-2026-000001/complete", json={"decision": "APPROVE", "comment": "x"}, headers=OPERATOR_HEADERS,
    )
    assert resp.status_code == 403


def test_reviewer_can_view_queue():
    resp = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS)
    assert resp.status_code == 200
    assert "cases" in resp.json()


def test_assign_unknown_review_case_404():
    resp = client.post(
        "/api/v1/reviews/REV-DOES-NOT-EXIST/assign", json={"reviewer_id": "USR-002"}, headers=REVIEWER_HEADERS,
    )
    assert resp.status_code == 404


def test_complete_review_case_without_comment_returns_422():
    repo = get_cheque_repository()
    repo.save("CHK-EMPTY-COMMENT", {
        "cheque_id": "CHK-EMPTY-COMMENT",
        "extraction": {"fields": {}}, "validation": {"overall_validation_status": "PASS"}, "ocr": {"average_confidence": 96.0},
        "fraud_analysis": {"risk_level": "LOW", "duplicate_analysis": {"duplicate_status": "POTENTIAL_DUPLICATE"},
                            "image_analysis": {"image_tampering_score": 0.0}, "indicators": []},
        "signature_analysis": {"risk_level": "LOW", "similarity_score": 0.9},
        "anomaly_analysis": {"risk_level": "LOW"},
        "risk_assessment": {"overall_risk_score": 15.0, "risk_level": "LOW", "hard_rules_triggered": [], "unavailable_inputs": []},
    })
    decision_service.make_decision("CHK-EMPTY-COMMENT")
    case_id = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS).json()["cases"][0]["review_case_id"]
    resp = client.post(
        f"/api/v1/reviews/{case_id}/complete", json={"decision": "APPROVE", "comment": ""}, headers=REVIEWER_HEADERS,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "REVIEW_COMMENT_REQUIRED"


def test_full_review_lifecycle_via_api():
    repo = get_cheque_repository()
    repo.save("CHK-LIFECYCLE", {
        "cheque_id": "CHK-LIFECYCLE",
        "extraction": {"fields": {}}, "validation": {"overall_validation_status": "PASS"}, "ocr": {"average_confidence": 96.0},
        "fraud_analysis": {"risk_level": "LOW", "duplicate_analysis": {"duplicate_status": "POTENTIAL_DUPLICATE"},
                            "image_analysis": {"image_tampering_score": 0.0}, "indicators": []},
        "signature_analysis": {"risk_level": "LOW", "similarity_score": 0.9},
        "anomaly_analysis": {"risk_level": "LOW"},
        "risk_assessment": {"overall_risk_score": 15.0, "risk_level": "LOW", "hard_rules_triggered": [], "unavailable_inputs": []},
    })
    decision_service.make_decision("CHK-LIFECYCLE")
    case_id = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS).json()["cases"][0]["review_case_id"]

    assign_resp = client.post(f"/api/v1/reviews/{case_id}/assign", json={"reviewer_id": "USR-002"}, headers=REVIEWER_HEADERS)
    assert assign_resp.status_code == 200
    assert assign_resp.json()["status"] == "ASSIGNED"

    complete_resp = client.post(
        f"/api/v1/reviews/{case_id}/complete",
        json={"decision": "APPROVE", "comment": "Verified manually against reference."},
        headers={**REVIEWER_HEADERS, "X-User-Id": "USR-002"},
    )
    assert complete_resp.status_code == 200
    body = complete_resp.json()
    assert body["status"] == "CLOSED"
    assert body["reviewer_decision"] == "APPROVE"
    assert body["automated_decision"]["decision"] == "REVIEW"  # never overwritten


def test_duplicate_complete_action_returns_409():
    repo = get_cheque_repository()
    repo.save("CHK-DUP-ACTION", {
        "cheque_id": "CHK-DUP-ACTION",
        "extraction": {"fields": {}}, "validation": {"overall_validation_status": "PASS"}, "ocr": {"average_confidence": 96.0},
        "fraud_analysis": {"risk_level": "LOW", "duplicate_analysis": {"duplicate_status": "POTENTIAL_DUPLICATE"},
                            "image_analysis": {"image_tampering_score": 0.0}, "indicators": []},
        "signature_analysis": {"risk_level": "LOW", "similarity_score": 0.9},
        "anomaly_analysis": {"risk_level": "LOW"},
        "risk_assessment": {"overall_risk_score": 15.0, "risk_level": "LOW", "hard_rules_triggered": [], "unavailable_inputs": []},
    })
    decision_service.make_decision("CHK-DUP-ACTION")
    case_id = client.get("/api/v1/reviews", headers=REVIEWER_HEADERS).json()["cases"][0]["review_case_id"]
    client.post(f"/api/v1/reviews/{case_id}/complete", json={"decision": "APPROVE", "comment": "First."}, headers=REVIEWER_HEADERS)
    resp = client.post(f"/api/v1/reviews/{case_id}/complete", json={"decision": "REJECT", "comment": "Second."}, headers=REVIEWER_HEADERS)
    assert resp.status_code == 409


# ----------------------------------------------------------------------
# Ground-truth isolation
# ----------------------------------------------------------------------

_LEAKAGE_TOKENS = [
    "fraud_label", "ground_truth", "cheques_ground_truth", "fraud_labels.csv",
    "fraud_type", "expected_amount", "expected_payee_name", "expected_account_status",
    "expected_cheque_status", '"category"', "['category']", ".category",
]


def test_no_ground_truth_leakage_in_decision_and_review_modules():
    import app.services.decision.decision_rules as dr
    import app.services.decision.decision_service as ds
    import app.services.review.review_service as rs

    source = "".join(inspect.getsource(m) for m in (dr, ds, rs))
    for token in _LEAKAGE_TOKENS:
        assert token not in source, f"unexpected ground-truth reference: '{token}'"
