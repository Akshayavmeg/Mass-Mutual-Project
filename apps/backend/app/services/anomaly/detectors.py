"""Rule-based/statistical anomaly detectors (docs/20_Anomaly_Detection.md
S7-S18).

Implements 4 of the 7 documented anomaly types against real evidence:
Amount (Z-score), Frequency (recent-vs-baseline ratio), Payee (unseen
payee), and Cheque Sequence (gap from recent usage) -- plus Transaction
Pattern (co-occurrence of >=2 of the above). Timing Anomaly and Account
Behavior Anomaly are explicitly NOT implemented (see anomaly_service.py's
module docstring for why) rather than approximated with an undocumented,
unjustified heuristic.

The underlying statistics mirror Milestone 5's fraud pattern_detector
(same Z-score/frequency-ratio/sequence-gap math, same config thresholds)
-- intentionally: this module is a separate, later-stage OWNER of the
combined weighted anomaly_score (docs/20 S20), and Milestone 5's own
docstring explicitly disclaims taking ownership of that score. A shared
helper module was not introduced to avoid touching Milestone 5's already
-tested code; the duplication is a few lines of well-understood
statistics, not business logic.
"""

from __future__ import annotations

import statistics
from datetime import date, datetime

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository
from app.services.anomaly.models import AnomalyItem


def _zscore_severity(z: float) -> str | None:
    """Uses settings.anomaly_amount_zscore_bands (recalibrated from
    docs/20 S11's illustrative 2/3/4 example against this project's own
    measured data -- see the Milestone 6 report and this module's
    docstring)."""
    az = abs(z)
    bands = settings.anomaly_amount_zscore_bands
    if az < bands["MODERATE"]:
        return None
    if az < bands["HIGH"]:
        return "MODERATE"
    if az < bands["CRITICAL"]:
        return "HIGH"
    return "CRITICAL"


def amount_anomaly(amount: float | None, transactions: list) -> AnomalyItem | None:
    if amount is None:
        return None
    amounts = [t.amount for t in transactions]
    if len(amounts) < settings.pattern_min_history_for_amount_baseline:
        return None  # docs/20 S38 cold-start: insufficient history, do not fabricate an anomaly
    mean = statistics.mean(amounts)
    stdev = statistics.pstdev(amounts)
    if stdev < 0.01:
        return None  # zero-variance history: a Z-score is undefined, not "infinitely anomalous"

    z = (amount - mean) / stdev
    severity = _zscore_severity(z)
    if severity is None:
        return None

    weight = settings.anomaly_weights["amount"]
    return AnomalyItem(
        type="AMOUNT_ANOMALY", severity=severity,
        reason=f"Cheque amount ({amount:,.2f}) deviates from the account's historical average ({mean:,.2f}) with Z-score {z:.2f}.",
        contribution=weight,
        evidence={"historical_average": round(mean, 2), "historical_stdev": round(stdev, 2), "zscore": round(z, 2), "sample_size": len(amounts)},
    )


def frequency_anomaly(transactions: list, processing_date: date) -> AnomalyItem | None:
    if not transactions:
        return None

    def _days_ago(txn_date_str: str) -> int | None:
        try:
            return (processing_date - datetime.strptime(txn_date_str, "%Y-%m-%d").date()).days
        except ValueError:
            return None

    baseline_count = sum(1 for t in transactions if (d := _days_ago(t.transaction_date)) is not None and 0 <= d <= settings.pattern_frequency_baseline_days)
    recent_count = sum(1 for t in transactions if (d := _days_ago(t.transaction_date)) is not None and 0 <= d <= settings.pattern_frequency_window_days)
    if recent_count < 3:
        return None

    expected = max(0.5, baseline_count * (settings.pattern_frequency_window_days / settings.pattern_frequency_baseline_days))
    ratio = recent_count / expected
    threshold = settings.pattern_frequency_ratio_threshold
    if ratio < threshold:
        return None
    severity = "CRITICAL" if ratio >= threshold * 4 else "HIGH" if ratio >= threshold * 2 else "MODERATE"

    weight = settings.anomaly_weights["frequency"]
    return AnomalyItem(
        type="FREQUENCY_ANOMALY", severity=severity,
        reason=(
            f"Account issued {recent_count} cheque(s) in the configured recent "
            f"{settings.pattern_frequency_window_days}-day window versus a historical baseline of "
            f"{baseline_count} over {settings.pattern_frequency_baseline_days} days."
        ),
        contribution=weight,
        evidence={"recent_count": recent_count, "baseline_count": baseline_count, "ratio": round(ratio, 2)},
    )


def payee_anomaly(payee_name: str | None, transactions: list) -> AnomalyItem | None:
    """Measured, documented limitation (Milestone 6 report): this
    project's synthetic transactions.csv assigns each account's
    transaction-history payees independently/randomly from its
    cheque_issuance.csv payees, rather than from a shared per-account
    identity pool. Measured directly against the real ground-truth
    dataset, comparing the actual cheque payee to that account's
    transaction-history payee set flagged 85.7% of cheques as "new
    payee" -- including the overwhelming majority of genuinely valid
    cheques. That is not a usable signal; shipping it as-is would
    systematically misclassify normal activity (violating this
    project's explicit false-positive-protection requirement).

    Per docs/38_Risk_Analysis.md R23 ("unrealistic mock data can produce
    misleading evaluation results"), this is treated the same way as
    Timing Anomaly: implemented, but not fired against this specific
    data source until the synthetic dataset's payee generation is
    corrected to draw transaction history from the same per-account
    payee identity as cheque issuance. Always returns None."""
    return None


def sequence_anomaly(cheque_number: str | None, historical_numbers_raw: list[str]) -> AnomalyItem | None:
    if not cheque_number:
        return None
    try:
        current = int(cheque_number)
    except ValueError:
        return None
    historical = []
    for c in historical_numbers_raw:
        try:
            historical.append(int(c))
        except ValueError:
            continue
    if len(historical) < 2:
        return None

    min_gap = min(abs(current - h) for h in historical)
    if min_gap <= settings.pattern_cheque_sequence_gap_threshold:
        return None

    weight = settings.anomaly_weights["sequence"]
    return AnomalyItem(
        type="CHEQUE_SEQUENCE_ANOMALY", severity="MODERATE",
        reason=f"Cheque number {cheque_number} is {min_gap} away from the nearest number this account has previously used.",
        contribution=weight,
        evidence={"min_gap": min_gap, "historical_sample_size": len(historical)},
    )


def transaction_pattern_anomaly(component_anomalies: list[AnomalyItem]) -> AnomalyItem | None:
    """docs/20 S18: individually weak signals become a stronger combined
    anomaly when several co-occur."""
    if len(component_anomalies) < 2:
        return None
    weight = settings.anomaly_weights["transaction_pattern"]
    types = [a.type for a in component_anomalies]
    return AnomalyItem(
        type="TRANSACTION_PATTERN_ANOMALY", severity="HIGH",
        reason=f"Multiple independent anomaly signals co-occurred: {', '.join(types)}.",
        contribution=weight,
        evidence={"contributing_types": types},
    )
