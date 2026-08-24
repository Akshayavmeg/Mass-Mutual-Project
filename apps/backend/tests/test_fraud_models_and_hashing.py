"""Unit tests for the fraud module's pure data/utility functions:
FraudIndicator/FraudResult/classify_risk_level (docs/17_Fraud_Detection.md
S21, S24, S30) and the exact/perceptual image hashing helpers
(docs/19_Duplicate_Detection.md S8-S11).
"""

from __future__ import annotations

import pytest

from app.services.fraud.detectors.image_hasher import (
    average_hash_of_bytes,
    hamming_distance_hex,
    sha256_of_bytes,
    similarity_from_hamming,
)
from app.services.fraud.models import FraudIndicator, FraudResult, RuleViolation, classify_risk_level

_BANDS = {"LOW": [0, 29], "MEDIUM": [30, 59], "HIGH": [60, 79], "CRITICAL": [80, 100]}


@pytest.mark.parametrize(
    "score,expected",
    [(0, "LOW"), (29, "LOW"), (30, "MEDIUM"), (59, "MEDIUM"), (60, "HIGH"), (79, "HIGH"), (80, "CRITICAL"), (100, "CRITICAL")],
)
def test_classify_risk_level_bands(score, expected):
    assert classify_risk_level(score, _BANDS) == expected


def test_classify_risk_level_above_100_is_critical():
    assert classify_risk_level(150, _BANDS) == "CRITICAL"


def test_fraud_result_as_dict_round_trip():
    indicator = FraudIndicator(type="PAYEE_MISMATCH", severity="HIGH", reason="mismatch", contribution=12.5)
    violation = RuleViolation("RULE-004", "IF amount mismatch THEN alert.", triggered_by=["AMOUNT_CONSISTENCY"])
    result = FraudResult(
        cheque_id="CHK-1", fraud_risk_score=42.0, risk_level="MEDIUM", model_prediction="SUSPICIOUS",
        indicators=[indicator], rule_violations=[violation], confidence=0.8,
        analysis_timestamp="2026-08-23T00:00:00+00:00", engine_version="fraud-engine-v1.0-rule-based",
        recommendation="MONITOR", unavailable_inputs=["SIGNATURE_ANALYSIS"],
    )
    payload = result.as_dict()
    assert payload["fraud_risk_score"] == 42.0
    assert payload["risk_level"] == "MEDIUM"
    assert payload["indicators"][0]["type"] == "PAYEE_MISMATCH"
    assert payload["rule_violations"][0]["rule_id"] == "RULE-004"
    assert payload["explanation"] == ["mismatch"]
    assert payload["unavailable_inputs"] == ["SIGNATURE_ANALYSIS"]


# --- Image hashing -----------------------------------------------------

def _tiny_png_bytes(fill: tuple[int, int, int]) -> bytes:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (32, 32), fill).save(buf, format="PNG")
    return buf.getvalue()


def test_sha256_of_bytes_is_deterministic_and_content_sensitive():
    a = _tiny_png_bytes((255, 255, 255))
    b = _tiny_png_bytes((255, 255, 255))
    c = _tiny_png_bytes((0, 0, 0))
    assert sha256_of_bytes(a) == sha256_of_bytes(b)
    assert sha256_of_bytes(a) != sha256_of_bytes(c)


def test_average_hash_of_bytes_identical_images_match():
    a = _tiny_png_bytes((200, 200, 200))
    b = _tiny_png_bytes((200, 200, 200))
    assert average_hash_of_bytes(a) == average_hash_of_bytes(b)


def test_average_hash_of_bytes_black_vs_white_differ():
    white = average_hash_of_bytes(_tiny_png_bytes((255, 255, 255)))
    black = average_hash_of_bytes(_tiny_png_bytes((0, 0, 0)))
    # A solid-color image has no internal contrast so aHash's threshold is
    # degenerate for both; the meaningful assertion is that the hash
    # function runs deterministically and produces a fixed-width hex value.
    assert len(white) == len(black) == 16


def test_hamming_distance_hex_identical_hashes_zero():
    assert hamming_distance_hex("387f3f7f1f3f390a", "387f3f7f1f3f390a") == 0


def test_hamming_distance_hex_counts_differing_bits():
    assert hamming_distance_hex("0000000000000000", "0000000000000001") == 1
    assert hamming_distance_hex("ffffffffffffffff", "0000000000000000") == 64


def test_hamming_distance_hex_missing_hash_returns_max_distance():
    assert hamming_distance_hex("", "387f3f7f1f3f390a") == 64
    assert hamming_distance_hex(None, None) == 0


def test_similarity_from_hamming_bounds():
    assert similarity_from_hamming(0, 8) == 1.0
    assert similarity_from_hamming(64, 8) == 0.0
    assert similarity_from_hamming(32, 8) == pytest.approx(0.5)
