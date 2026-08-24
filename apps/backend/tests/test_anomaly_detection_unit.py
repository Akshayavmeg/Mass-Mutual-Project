"""Unit tests for the Milestone 6 anomaly detectors
(docs/20_Anomaly_Detection.md), using crafted transaction fixtures so
every documented Z-score band and cold-start edge case is exercised
deterministically (independent of whatever the real Milestone 1 dataset
happens to contain for any given account).
"""

from __future__ import annotations

from datetime import date

from app.repositories.banking_repository import TransactionRecord
from app.services.anomaly.detectors import (
    amount_anomaly,
    frequency_anomaly,
    payee_anomaly,
    sequence_anomaly,
    transaction_pattern_anomaly,
)
from app.services.anomaly.models import AnomalyItem


def _txns(amounts, payee="Fatima Petrov", start_date="2026-07-01"):
    return [TransactionRecord(f"T{i}", "ACC1", start_date, "CHEQUE", amt, payee) for i, amt in enumerate(amounts)]


# --- Amount anomaly (recalibrated bands: MODERATE>=5, HIGH>=8, CRITICAL>=12) ---

def test_amount_anomaly_normal_not_flagged():
    txns = _txns([1000, 1050, 950, 1020, 980])
    assert amount_anomaly(1030.0, txns) is None


def test_amount_anomaly_moderate():
    txns = _txns([1000, 1010, 990, 1005, 995])  # tiny stdev ~ 7
    result = amount_anomaly(1040.0, txns)  # z ~ 5-6
    assert result is not None
    assert result.severity in ("MODERATE", "HIGH")
    assert result.type == "AMOUNT_ANOMALY"


def test_amount_anomaly_critical_for_extreme_deviation():
    txns = _txns([1000, 1010, 990, 1005, 995])
    result = amount_anomaly(50000.0, txns)
    assert result is not None
    assert result.severity == "CRITICAL"


def test_amount_anomaly_insufficient_history_not_flagged():
    txns = _txns([1000, 1010])  # below pattern_min_history_for_amount_baseline (3)
    assert amount_anomaly(999999.0, txns) is None


def test_amount_anomaly_zero_stdev_not_flagged():
    txns = _txns([1000, 1000, 1000, 1000])
    assert amount_anomaly(50000.0, txns) is None  # undefined Z-score, not "infinitely anomalous"


def test_amount_anomaly_none_when_amount_missing():
    txns = _txns([1000, 1010, 990])
    assert amount_anomaly(None, txns) is None


# --- Frequency anomaly ---

def test_frequency_anomaly_high_burst():
    baseline = _txns([1000] * 2, start_date="2026-07-01")
    burst = _txns([1000] * 10, start_date="2026-08-22")
    result = frequency_anomaly(baseline + burst, date(2026, 8, 23))
    assert result is not None
    assert result.type == "FREQUENCY_ANOMALY"


def test_frequency_anomaly_not_flagged_for_normal_activity():
    normal = _txns([1000] * 3, start_date="2026-08-20")
    assert frequency_anomaly(normal, date(2026, 8, 23)) is None


def test_frequency_anomaly_none_for_empty_history():
    assert frequency_anomaly([], date(2026, 8, 23)) is None


# --- Payee anomaly: deliberately disabled (measured 85.7% false-positive
# rate against the real dataset -- see Milestone 6 report) ---

def test_payee_anomaly_is_disabled_regardless_of_input():
    txns = _txns([1000, 1010, 990], payee="Known Payee")
    assert payee_anomaly("Completely Unknown Payee", txns) is None
    assert payee_anomaly(None, txns) is None
    assert payee_anomaly("Known Payee", txns) is None


# --- Sequence anomaly ---

def test_sequence_anomaly_large_gap():
    result = sequence_anomaly("099999", ["000100", "000101", "000102"])
    assert result is not None
    assert result.type == "CHEQUE_SEQUENCE_ANOMALY"


def test_sequence_anomaly_small_gap_not_flagged():
    result = sequence_anomaly("000105", ["000100", "000101", "000102"])
    assert result is None


def test_sequence_anomaly_insufficient_history_not_flagged():
    assert sequence_anomaly("099999", ["000100"]) is None


def test_sequence_anomaly_invalid_cheque_number_not_flagged():
    assert sequence_anomaly("ABCDEF", ["000100", "000101"]) is None


# --- Transaction pattern anomaly (co-occurrence) ---

def test_transaction_pattern_anomaly_requires_at_least_two_components():
    one = [AnomalyItem("AMOUNT_ANOMALY", "HIGH", "x", 30.0)]
    assert transaction_pattern_anomaly(one) is None

    two = [AnomalyItem("AMOUNT_ANOMALY", "HIGH", "x", 30.0), AnomalyItem("FREQUENCY_ANOMALY", "MODERATE", "y", 20.0)]
    result = transaction_pattern_anomaly(two)
    assert result is not None
    assert result.type == "TRANSACTION_PATTERN_ANOMALY"
    assert "AMOUNT_ANOMALY" in result.evidence["contributing_types"]
