"""Milestone 3 integration tests against the real Milestone 1 dataset.

Runs the actual upload -> preprocess -> OCR -> extract pipeline against a
representative real cheque image from every documented category and
compares the extracted fields to the Milestone 1 ground truth. This is a
functional correctness check (does extraction actually work on our real
data), not the full accuracy evaluation -- that is
scripts/run_ocr_evaluation.py, which measures accuracy across the whole
dataset and writes the results docs/32_OCR_Evaluation.md requires.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.cheque_repository import get_cheque_repository

client = TestClient(app)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
GROUND_TRUTH_PATH = DATA_DIR / "test_data" / "cheques_ground_truth.csv"


@pytest.fixture(autouse=True)
def _clean_repository():
    yield
    get_cheque_repository().clear_for_testing()


def _one_sample_per_category() -> list[dict]:
    if not GROUND_TRUTH_PATH.exists():
        return []
    df = pd.read_csv(GROUND_TRUTH_PATH, dtype={"account_number": str, "cheque_number": str})
    picked = df.groupby("category").first().reset_index()
    return picked.to_dict("records")


_SAMPLES = _one_sample_per_category()


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
@pytest.mark.parametrize("row", _SAMPLES, ids=[r["category"] for r in _SAMPLES])
def test_ocr_extraction_runs_for_every_category_without_crashing(row):
    """Milestone 3 has no awareness of fraud/validation categories -- it
    must simply extract whatever text is actually printed on the cheque
    image for every one of them without crashing."""
    full_path = DATA_DIR / row["image_path"]
    content = full_path.read_bytes()

    upload = client.post("/api/v1/cheques/upload", files={"file": (full_path.name, content, "image/png")})
    assert upload.status_code == 201
    cheque_id = upload.json()["cheque_id"]

    ocr_start = client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    assert ocr_start.status_code == 200

    result = client.get(f"/api/v1/cheques/{cheque_id}/ocr").json()
    assert result["ocr_status"] in ("COMPLETED", "LOW_CONFIDENCE", "PARTIAL", "FAILED")
    assert result["extraction_status"] in ("COMPLETED", "PARTIAL", "FAILED", "AMBIGUOUS")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_extracted_fields_match_ground_truth_for_a_clean_valid_cheque():
    """A VALID-category cheque (no tampering, clean rendering) should
    have its printed fields read back correctly -- this is what "printed
    on the cheque" ground truth means, as distinct from the *bank
    record* ground truth (expected_*) that Milestone 4's validation will
    check against."""
    row = next(r for r in _SAMPLES if r["category"] == "VALID")
    full_path = DATA_DIR / row["image_path"]
    content = full_path.read_bytes()

    upload = client.post("/api/v1/cheques/upload", files={"file": (full_path.name, content, "image/png")})
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    result = client.get(f"/api/v1/cheques/{cheque_id}/ocr").json()

    extracted = result["extracted_data"]
    assert extracted["cheque_number"]["value"] == str(row["cheque_number"]).zfill(6)
    assert extracted["account_number"]["value"] == str(row["account_number"])
    assert extracted["routing_transit_number"]["value"] == str(row["routing_transit_number"])
    assert extracted["payee_name"]["value"] == row["payee_name"]
    assert extracted["amount"]["value"] == pytest.approx(float(row["amount"]), abs=0.01)
    assert extracted["date"]["value"] == row["cheque_date"]


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_amount_tampered_cheque_ocr_reads_the_printed_tampered_amount():
    """For an AMOUNT_TAMPERED sample, OCR has no way to know the "true"
    bank-record amount -- it can only read what's actually printed on
    the image. Extraction must reflect the printed (tampered) value, not
    the bank's expected_amount; reconciling the two is Milestone 4's job."""
    row = next(r for r in _SAMPLES if r["category"] == "AMOUNT_TAMPERED")
    full_path = DATA_DIR / row["image_path"]
    content = full_path.read_bytes()

    upload = client.post("/api/v1/cheques/upload", files={"file": (full_path.name, content, "image/png")})
    cheque_id = upload.json()["cheque_id"]
    client.post(f"/api/v1/cheques/{cheque_id}/ocr")
    result = client.get(f"/api/v1/cheques/{cheque_id}/ocr").json()

    extracted_amount = result["extracted_data"]["amount"]["value"]
    assert extracted_amount == pytest.approx(float(row["amount"]), abs=0.01)
    # The printed amount and the bank's expected amount genuinely differ
    # for this category -- confirming the test fixture actually exercises
    # a mismatch, not a coincidentally-equal case.
    assert float(row["amount"]) != float(row["expected_amount"])
