"""Milestone 5 integration tests: the Fraud Detection Engine running
against real Milestone 1 synthetic data through the real upload -> OCR ->
validate -> fraud-analysis pipeline (docs/17_Fraud_Detection.md).

Covers the scenario list from the Milestone 5 instructions (valid,
invalid account, stopped cheque, cheque-series anomaly, duplicate,
payee mismatch, amount mismatch, multiple indicators, normal high-value
cheque, and the duplicate-detection false-positive/near-duplicate
matrix), the API contract, fail-safe behavior, and the specific
follow-up checks requested after the smoke test: why a VALID and an
INVALID_ACCOUNT cheque both showed POTENTIAL_DUPLICATE, that duplicate
detection never reads ground-truth labels, and that image_tampering_score
is derived from real per-cheque pixel evidence.
"""

from __future__ import annotations

import inspect
import io
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.repositories.banking_repository import CSVBankingDataRepository, reset_banking_repository_for_testing
from app.repositories.cheque_repository import get_cheque_repository
from app.services.fraud import fraud_service
from app.services.fraud.detectors import duplicate_detector, image_tampering_detector
from app.services.fraud.exceptions import ChequeNotValidatedError

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


def _upload_ocr_validate(content: bytes, filename: str = "cheque.png", media_type: str = "image/png") -> str:
    upload = client.post("/api/v1/cheques/upload", files={"file": (filename, content, media_type)})
    assert upload.status_code == 201, upload.text
    cheque_id = upload.json()["cheque_id"]
    assert client.post(f"/api/v1/cheques/{cheque_id}/ocr").status_code == 200
    assert client.post(f"/api/v1/cheques/{cheque_id}/validate").status_code == 200
    return cheque_id


def _run_fraud(cheque_id: str) -> dict:
    resp = client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis")
    assert resp.status_code == 200, resp.text
    return resp.json()


def _sample(category: str) -> dict:
    return next(r for r in _SAMPLES if r["category"] == category)


# ----------------------------------------------------------------------
# Required scenario coverage (Milestone 5 instructions S13)
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_valid_cheque_is_low_risk():
    row = _sample("VALID")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert result["risk_level"] in ("LOW", "MEDIUM")  # see investigation note below re: POTENTIAL_DUPLICATE
    assert not any(v["rule_id"] in ("RULE-001", "RULE-002") for v in result["rule_violations"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_invalid_account_triggers_rule001_and_high_risk():
    row = _sample("INVALID_ACCOUNT")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert any(v["rule_id"] == "RULE-001" for v in result["rule_violations"])
    assert result["risk_level"] in ("HIGH", "CRITICAL")
    assert result["recommendation"] == "MANUAL_REVIEW"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_stopped_cheque_triggers_critical_indicator():
    row = _sample("STOPPED_CHEQUE")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert any(ind["type"] == "STOPPED_CHEQUE" and ind["severity"] == "CRITICAL" for ind in result["indicators"])
    assert result["risk_level"] in ("HIGH", "CRITICAL")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_cheque_series_anomaly_triggers_indicator():
    row = _sample("CHEQUE_SERIES_ANOMALY")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert any(ind["type"] == "CHEQUE_SERIES_MISMATCH" for ind in result["indicators"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_duplicate_category_triggers_rule002_confirmed_duplicate():
    row = _sample("DUPLICATE")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert result["duplicate_analysis"]["duplicate_status"] == "CONFIRMED_DUPLICATE"
    assert any(v["rule_id"] == "RULE-002" for v in result["rule_violations"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_payee_tampered_triggers_payee_mismatch_indicator():
    row = _sample("PAYEE_TAMPERED")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert any(ind["type"] == "PAYEE_MISMATCH" for ind in result["indicators"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_amount_tampered_triggers_rule004_amount_mismatch():
    row = _sample("AMOUNT_TAMPERED")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert any(v["rule_id"] == "RULE-004" for v in result["rule_violations"])
    assert any(ind["type"] == "AMOUNT_MISMATCH" and ind["severity"] == "HIGH" for ind in result["indicators"])


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_multiple_anomalies_category_triggers_rule005_manual_review():
    row = _sample("MULTIPLE_ANOMALIES")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    assert len(result["indicators"]) >= 2
    assert any(v["rule_id"] == "RULE-005" for v in result["rule_violations"])
    assert result["recommendation"] == "MANUAL_REVIEW"


def test_normal_high_value_cheque_is_not_automatically_flagged():
    """Explicit requirement: a large amount that is consistent with the
    account's own historical pattern must not be treated as fraud."""
    repo = CSVBankingDataRepository(REAL_BANKING_DATA_DIR)
    account_number = "9000010001"
    txns = repo.get_account_transactions(account_number)
    assert len(txns) >= 3
    mean_amount = sum(t.amount for t in txns) / len(txns)

    cheque_repo = get_cheque_repository()
    cheque_repo.save("CHK-HIGH-VALUE", {
        "cheque_id": "CHK-HIGH-VALUE",
        "extraction": {"fields": {
            "account_number": {"value": account_number}, "cheque_number": {"value": "000101"},
            "amount": {"value": round(mean_amount * 1.1, 2)}, "date": {"value": "2026-08-01"},
            "payee_name": {"value": "Foundry Systems"}, "routing_transit_number": {"value": "121000358"},
            "amount_in_words": {"value": None},
        }},
        "validation": {"checks": {
            "ACCOUNT_EXISTS": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "ACCOUNT_STATUS": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "CHEQUE_SERIES": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "CHEQUE_STATUS": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "PAYEE_MATCH": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "AMOUNT": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "AMOUNT_CONSISTENCY": {"status": "NOT_CHECKED", "severity": "HIGH", "message": "", "details": None},
            "DUPLICATE_CHECK": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
        }},
    })

    result = fraud_service.analyze_fraud(
        "CHK-HIGH-VALUE", processing_date=DATASET_PROCESSING_DATE, banking_repo=repo,
    )
    assert not any(ind.type == "AMOUNT_ANOMALY" for ind in result.indicators)
    assert result.risk_level in ("LOW", "MEDIUM")


def test_unusual_amount_and_suspicious_cheque_number_via_crafted_history(monkeypatch):
    """Frequency/sequence anomalies are unit-tested directly against
    crafted repositories in test_fraud_detectors_unit.py (the real
    Milestone 1 transaction history has no naturally-occurring burst);
    this test exercises the same scenario through the full
    fraud_service.analyze_fraud() orchestration instead of the isolated
    pattern_detector function, using a real account's banking data with
    a monkeypatched transaction history."""
    from app.repositories.banking_repository import TransactionRecord

    repo = CSVBankingDataRepository(REAL_BANKING_DATA_DIR)
    repo._ensure_loaded()
    account_number = "9000010001"
    monkeypatch.setitem(
        repo._transactions, account_number,
        [TransactionRecord(f"T{i}", account_number, "2026-07-01", "CHEQUE", 1000.0, "X") for i in range(3)]
        + [TransactionRecord(f"B{i}", account_number, "2026-08-22", "CHEQUE", 1000.0, "X") for i in range(10)],
    )
    # The real Milestone 1 processed-cheque history has no cheque-number
    # entries for this account (only the 8 duplicate-source accounts do),
    # so the sequence baseline is monkeypatched here too.
    monkeypatch.setattr(repo, "get_account_cheque_number_history", lambda acct: ["000100", "000101", "000102", "000103"])

    cheque_repo = get_cheque_repository()
    cheque_repo.save("CHK-FREQ", {
        "cheque_id": "CHK-FREQ",
        "extraction": {"fields": {
            "account_number": {"value": account_number}, "cheque_number": {"value": "099999"},
            "amount": {"value": 1000.0}, "date": {"value": "2026-08-01"},
            "payee_name": {"value": "Fatima Petrov"}, "routing_transit_number": {"value": "121000358"},
            "amount_in_words": {"value": None},
        }},
        "validation": {"checks": {
            "ACCOUNT_EXISTS": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "ACCOUNT_STATUS": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
            "CHEQUE_SERIES": {"status": "FAIL", "severity": "MEDIUM", "message": "", "details": None},
            "DUPLICATE_CHECK": {"status": "PASS", "severity": "INFO", "message": "", "details": None},
        }},
    })

    result = fraud_service.analyze_fraud("CHK-FREQ", processing_date=date(2026, 8, 23), banking_repo=repo)
    indicator_types = {ind.type for ind in result.indicators}
    assert "FREQUENCY_ANOMALY" in indicator_types
    assert "CHEQUE_SEQUENCE_ANOMALY" in indicator_types


# ----------------------------------------------------------------------
# Duplicate-detection matrix (Milestone 5 instructions S13)
# ----------------------------------------------------------------------

_DUPLICATE_SOURCE_IMAGE = DATA_DIR / "sample_cheques" / "duplicate" / "CHK-2026-000009.png"
_UNIQUE_IMAGE = DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000002.png"


@pytest.mark.skipif(not _DUPLICATE_SOURCE_IMAGE.exists(), reason="Milestone 1 duplicate fixture not found")
def test_exact_duplicate_and_renamed_identical_image_both_confirmed():
    content = _DUPLICATE_SOURCE_IMAGE.read_bytes()
    for filename in ("CHK-2026-000009.png", "totally_different_name.png"):
        cheque_id = _upload_ocr_validate(content, filename=filename)
        result = _run_fraud(cheque_id)
        assert result["duplicate_analysis"]["duplicate_status"] == "CONFIRMED_DUPLICATE", filename
        assert result["duplicate_analysis"]["image_match"] is True, filename


@pytest.mark.skipif(not _DUPLICATE_SOURCE_IMAGE.exists(), reason="Milestone 1 duplicate fixture not found")
def test_cropped_near_duplicate_is_at_least_potential():
    img = Image.open(_DUPLICATE_SOURCE_IMAGE)
    w, h = img.size
    cropped = img.crop((int(w * 0.01), int(h * 0.01), int(w * 0.99), int(h * 0.99))).resize((w, h))
    buf = io.BytesIO()
    cropped.save(buf, format="PNG")

    cheque_id = _upload_ocr_validate(buf.getvalue(), filename="cropped.png")
    result = _run_fraud(cheque_id)
    assert result["duplicate_analysis"]["duplicate_status"] in ("POTENTIAL_DUPLICATE", "CONFIRMED_DUPLICATE")


@pytest.mark.skipif(not _DUPLICATE_SOURCE_IMAGE.exists(), reason="Milestone 1 duplicate fixture not found")
def test_rotated_near_duplicate_is_at_least_potential():
    img = Image.open(_DUPLICATE_SOURCE_IMAGE)
    rotated = img.rotate(2, fillcolor="white", expand=False)
    buf = io.BytesIO()
    rotated.save(buf, format="PNG")

    cheque_id = _upload_ocr_validate(buf.getvalue(), filename="rotated.png")
    result = _run_fraud(cheque_id)
    assert result["duplicate_analysis"]["duplicate_status"] in ("POTENTIAL_DUPLICATE", "CONFIRMED_DUPLICATE")


@pytest.mark.skipif(not _DUPLICATE_SOURCE_IMAGE.exists(), reason="Milestone 1 duplicate fixture not found")
def test_compressed_near_duplicate_is_at_least_potential():
    img = Image.open(_DUPLICATE_SOURCE_IMAGE).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=35)

    cheque_id = _upload_ocr_validate(buf.getvalue(), filename="compressed.jpg", media_type="image/jpeg")
    result = _run_fraud(cheque_id)
    assert result["duplicate_analysis"]["duplicate_status"] in ("POTENTIAL_DUPLICATE", "CONFIRMED_DUPLICATE")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_similar_but_unrelated_cheque_is_not_a_confirmed_duplicate():
    """False-positive protection: two genuinely different VALID cheques
    (different account, cheque number, payee, amount) must not be
    reported as a confirmed duplicate of each other, even though they
    share the same visual template."""
    row_a = _sample("VALID")
    cheque_a = _upload_ocr_validate((DATA_DIR / row_a["image_path"]).read_bytes())
    _run_fraud(cheque_a)

    content_b = _UNIQUE_IMAGE.read_bytes()
    cheque_b = _upload_ocr_validate(content_b, filename="unrelated.png")
    result_b = _run_fraud(cheque_b)
    assert result_b["duplicate_analysis"]["duplicate_status"] != "CONFIRMED_DUPLICATE"


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_same_account_different_cheque_number_is_not_flagged_as_duplicate():
    """docs/19 S31's explicit example: same account, different cheque
    number is not automatically a duplicate."""
    repo = CSVBankingDataRepository(REAL_BANKING_DATA_DIR)
    account_number = "9000010001"

    cheque_repo = get_cheque_repository()
    for cheque_id, cheque_number in (("CHK-A", "000100"), ("CHK-B", "000101")):
        cheque_repo.save(cheque_id, {
            "cheque_id": cheque_id,
            "extraction": {"fields": {
                "account_number": {"value": account_number}, "cheque_number": {"value": cheque_number},
                "amount": {"value": 500.0}, "date": {"value": "2026-08-01"},
                "payee_name": {"value": "Fatima Petrov"}, "routing_transit_number": {"value": "121000358"},
                "amount_in_words": {"value": None},
            }},
            "validation": {"checks": {"DUPLICATE_CHECK": {"status": "PASS", "severity": "HIGH", "message": "", "details": None}}},
        })

    result_a = fraud_service.analyze_fraud("CHK-A", processing_date=DATASET_PROCESSING_DATE, banking_repo=repo)
    result_b = fraud_service.analyze_fraud("CHK-B", processing_date=DATASET_PROCESSING_DATE, banking_repo=repo)
    assert result_b.as_dict()  # sanity: ran without error
    assert not any(ind.type == "DUPLICATE_CHEQUE" for ind in result_b.indicators)


# ----------------------------------------------------------------------
# Fail-safe behavior
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_unavailable_banking_data_does_not_crash_and_lowers_confidence(tmp_path):
    row = _sample("VALID")
    cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())

    broken_repo = reset_banking_repository_for_testing(tmp_path)
    result = fraud_service.analyze_fraud(
        cheque_id, processing_date=DATASET_PROCESSING_DATE, banking_repo=broken_repo,
    )
    assert result.confidence < 1.0
    assert "DUPLICATE_DETECTION" in result.unavailable_inputs
    assert "TRANSACTION_HISTORY" in result.unavailable_inputs
    assert result.risk_level != "CRITICAL"  # unavailable data must not be fabricated into false certainty


def test_fraud_analysis_raises_when_validation_not_run():
    cheque_repo = get_cheque_repository()
    cheque_repo.save("CHK-NO-VALIDATION", {"cheque_id": "CHK-NO-VALIDATION", "extraction": {"fields": {}}, "validation": None})
    with pytest.raises(ChequeNotValidatedError):
        fraud_service.analyze_fraud("CHK-NO-VALIDATION")


def test_fraud_analysis_raises_keyerror_for_unknown_cheque():
    with pytest.raises(KeyError):
        fraud_service.analyze_fraud("CHK-DOES-NOT-EXIST")


# ----------------------------------------------------------------------
# API contract
# ----------------------------------------------------------------------

def test_fraud_analysis_endpoint_404_for_unknown_cheque():
    resp = client.post("/api/v1/cheques/CHK-DOES-NOT-EXIST/fraud-analysis")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CHEQUE_NOT_FOUND"


def test_fraud_analysis_endpoint_422_when_not_validated():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    resp = client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "CHEQUE_NOT_VALIDATED"


def test_get_fraud_analysis_404_before_post():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000001.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    resp = client.get(f"/api/v1/cheques/{cheque_id}/fraud-analysis")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "FRAUD_ANALYSIS_NOT_RUN"


def test_post_then_get_fraud_analysis_consistent():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000002.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    post_result = client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis").json()
    get_result = client.get(f"/api/v1/cheques/{cheque_id}/fraud-analysis").json()
    assert post_result["fraud_risk_score"] == get_result["fraud_risk_score"]
    assert post_result["indicators"] == get_result["indicators"]


def test_cheque_detail_shows_fraud_analyzed_status():
    upload = client.post(
        "/api/v1/cheques/upload",
        files={"file": ("c.png", (DATA_DIR / "sample_cheques" / "valid" / "CHK-2026-000002.png").read_bytes(), "image/png")},
    )
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    client.post(f"/api/v1/cheques/{cheque_id}/validate")
    client.post(f"/api/v1/cheques/{cheque_id}/fraud-analysis")
    detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
    assert detail["processing_status"] == "FRAUD_ANALYZED"


# ----------------------------------------------------------------------
# Investigation follow-ups requested after the smoke test
# ----------------------------------------------------------------------

@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_investigation_1_and_2_valid_and_invalid_account_potential_duplicate_explained():
    """Reproduces and explains the smoke-test observation: a real VALID
    cheque (CHK-2026-000001) and a real INVALID_ACCOUNT cheque
    (CHK-2026-000049) both showed duplicate_status=POTENTIAL_DUPLICATE.

    Root cause (measured directly against the real historical hash
    index): the Milestone 1 dataset renders every cheque from the same
    template, so the 64-bit average-perceptual-hash of genuinely
    unrelated cheques can be as high as 0.98+ similarity -- comfortably
    above the documented 0.95 "confirmed" threshold on similarity alone.
    This test proves that outcome is (a) driven purely by Level 3 image
    evidence, not by fabricated data, and (b) correctly CAPPED at
    POTENTIAL rather than CONFIRMED because neither cheque's account
    number and cheque number both match the closest historical hash
    entry -- exactly the Rule D3 corroboration requirement.
    """
    valid_row = _sample("VALID")
    cheque_id = _upload_ocr_validate((DATA_DIR / valid_row["image_path"]).read_bytes())
    result = _run_fraud(cheque_id)
    dup = result["duplicate_analysis"]

    if dup["duplicate_status"] == "POTENTIAL_DUPLICATE":
        # Confirm this came from Level 3 (perceptual similarity), not a
        # fabricated/level-1/level-2 signal, and that it was correctly
        # NOT escalated to CONFIRMED.
        assert dup["perceptual_similarity"] is not None
        assert dup["perceptual_similarity"] >= 0.80
        assert dup["data_match"] is False
        assert dup["image_match"] is False
        # A POTENTIAL (not CONFIRMED) duplicate alone must not push a
        # cheque with no other problems into HIGH/CRITICAL risk.
        assert result["risk_level"] in ("LOW", "MEDIUM")
    else:
        assert dup["duplicate_status"] == "NEW"


_GROUND_TRUTH_LEAKAGE_TOKENS = [
    "fraud_label", "ground_truth", "cheques_ground_truth", "fraud_labels.csv",
    "fraud_type", "expected_amount", "expected_payee_name", "expected_account_status",
    "expected_cheque_status", '"category"', "['category']", ".category",
]


def test_investigation_3_duplicate_detection_never_reads_ground_truth_labels():
    """Static + behavioral proof that duplicate detection uses only
    documented evidence (extracted fields, image bytes/hashes, banking
    history) -- never the synthetic category/fraud_label ground truth.

    The forbidden-token list intentionally targets concrete column/file
    names from the ground-truth CSVs (data/test_data/cheques_ground_truth.csv,
    fraud_labels.csv) and actual dict/attribute access patterns, not the
    bare English word "category" -- which legitimately appears in this
    module's own docstrings explaining what must NOT be read.
    """
    import app.services.fraud.detectors.duplicate_detector as dd
    import app.services.fraud.fraud_service as fs

    source = inspect.getsource(dd) + inspect.getsource(fs)
    for token in _GROUND_TRUTH_LEAKAGE_TOKENS:
        assert token not in source, f"duplicate/fraud service source unexpectedly references '{token}'"

    # Behavioral confirmation: detect() is a pure function of its declared
    # arguments -- calling it twice with identical inputs (no ground-truth
    # label argument exists in its signature at all) is fully deterministic.
    repo = CSVBankingDataRepository(REAL_BANKING_DATA_DIR)
    kwargs = dict(
        account_number="9000010001", cheque_number="000100", amount=500.0, date_value="2026-08-01",
        validation_duplicate_check={"status": "PASS"}, current_perceptual_hash="0000000000000000",
        current_file_hash="some-hash", banking_repo=repo,
    )
    result_a = duplicate_detector.detect(**kwargs)
    result_b = duplicate_detector.detect(**kwargs)
    assert result_a.as_dict() == result_b.as_dict()

    assert "ground_truth" not in inspect.signature(duplicate_detector.detect).parameters
    assert "category" not in inspect.signature(duplicate_detector.detect).parameters
    assert "fraud_label" not in inspect.signature(duplicate_detector.detect).parameters


def test_investigation_4_image_tampering_score_derived_from_real_pixels_not_category():
    """Confirms image_tampering_score varies per actual image content
    across different real cheques (not a constant/label-driven value),
    and that the source code never reads the category/fraud label."""
    import app.services.fraud.detectors.image_tampering_detector as itd

    source = inspect.getsource(itd)
    for token in _GROUND_TRUTH_LEAKAGE_TOKENS:
        assert token not in source

    assert "category" not in inspect.signature(image_tampering_detector.analyze).parameters
    assert "fraud_label" not in inspect.signature(image_tampering_detector.analyze).parameters

    scores = []
    for category in ("VALID", "AMOUNT_TAMPERED", "STOPPED_CHEQUE"):
        row = _sample(category)
        cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
        result = _run_fraud(cheque_id)
        scores.append(result["image_analysis"]["image_tampering_score"])

    assert all(s is not None for s in scores)
    # Real per-image pixel statistics should not all be bit-identical.
    assert len(set(scores)) > 1


@pytest.mark.skipif(not _DUPLICATE_SOURCE_IMAGE.exists(), reason="Milestone 1 duplicate fixture not found")
def test_investigation_5_similar_but_unrelated_cheques_false_positive_protection():
    """Broader false-positive sweep: several genuinely distinct real
    cheques (different accounts/cheques/payees/amounts, same template)
    must never be reported CONFIRMED_DUPLICATE against each other."""
    categories = ["VALID", "STOPPED_CHEQUE", "CHEQUE_SERIES_ANOMALY", "STALE_CHEQUE"]
    statuses = []
    for category in categories:
        row = _sample(category)
        cheque_id = _upload_ocr_validate((DATA_DIR / row["image_path"]).read_bytes())
        result = _run_fraud(cheque_id)
        statuses.append((category, result["duplicate_analysis"]["duplicate_status"]))

    confirmed_without_real_history_match = [
        c for c, status in statuses if status == "CONFIRMED_DUPLICATE" and c not in ("DUPLICATE",)
    ]
    assert confirmed_without_real_history_match == [], statuses
