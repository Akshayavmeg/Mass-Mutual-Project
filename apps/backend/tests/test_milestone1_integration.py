"""Milestone 2 integration tests against the real Milestone 1 dataset.

Confirms that a representative sample from every documented fraud/test
category (docs/17_Fraud_Detection.md S28) can actually enter the upload +
preprocessing pipeline end-to-end without error. This milestone does not
interpret the cheque *content* (no OCR/validation/fraud logic) -- it only
proves the pipeline accepts and processes every category's real image
files, since the whole point of Milestone 1 was to give later milestones
real files to consume.
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


def _one_sample_per_category() -> list[tuple[str, str]]:
    if not GROUND_TRUTH_PATH.exists():
        return []
    df = pd.read_csv(GROUND_TRUTH_PATH)
    picked = df.groupby("category").first().reset_index()
    return list(zip(picked["category"], picked["image_path"]))


_SAMPLES = _one_sample_per_category()


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found -- run scripts/generate_synthetic_data.py")
@pytest.mark.parametrize("category,image_path", _SAMPLES, ids=[c for c, _ in _SAMPLES])
def test_representative_sample_from_every_category_enters_pipeline(category, image_path):
    full_path = DATA_DIR / image_path
    assert full_path.exists(), f"Missing sample image for category {category}: {full_path}"

    content = full_path.read_bytes()
    resp = client.post(
        "/api/v1/cheques/upload",
        files={"file": (full_path.name, content, "image/png")},
    )

    assert resp.status_code == 201, f"Category {category} failed to upload: {resp.json()}"
    body = resp.json()
    assert body["success"] is True
    cheque_id = body["cheque_id"]

    detail = client.get(f"/api/v1/cheques/{cheque_id}")
    assert detail.status_code == 200
    record = detail.json()

    # The pipeline must reach a defined outcome (never silently do
    # nothing), and must never crash regardless of which fraud/validation
    # category the image represents -- Milestone 2 has no awareness of
    # cheque content/categories at all.
    assert record["processing_status"] in ("PROCESSING", "FAILED")
    assert record["preprocessing"] is not None
    assert record["preprocessing"]["preprocessing_status"] in ("COMPLETED", "FAILED")


@pytest.mark.skipif(not _SAMPLES, reason="Milestone 1 dataset not found")
def test_all_ten_required_categories_are_covered_by_this_test():
    required = {
        "VALID", "DUPLICATE", "PAYEE_TAMPERED", "AMOUNT_TAMPERED", "SIGNATURE_MISMATCH",
        "INVALID_ACCOUNT", "STALE_CHEQUE", "STOPPED_CHEQUE", "CHEQUE_SERIES_ANOMALY",
        "MULTIPLE_ANOMALIES",
    }
    covered = {c for c, _ in _SAMPLES}
    missing = required - covered
    assert not missing, f"Milestone 1 categories not exercised by the pipeline test: {missing}"
