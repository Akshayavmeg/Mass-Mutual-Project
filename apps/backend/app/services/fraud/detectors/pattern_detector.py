"""Transaction/behavioral pattern indicators (docs/20_Anomaly_Detection.md
S8-S16; docs/17_Fraud_Detection.md S16-S17). This is deliberately the
*fraud-indicator* subset only -- amount, frequency, and cheque-sequence
signals derived from the Milestone 1 synthetic transaction history -- not
the full Milestone 6 anomaly-scoring system (payee-familiarity scoring,
timing anomalies, ML/Isolation-Forest detection, a dedicated anomaly
score/audit table). Consistent with docs/20 S38's cold-start guidance,
an account with too little history is never automatically flagged.
"""

from __future__ import annotations

import statistics
from datetime import date, datetime

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError
from app.services.fraud.models import FraudIndicator


def _severity_for_zscore(z: float) -> str:
    az = abs(z)
    if az >= 4:
        return "CRITICAL"
    if az >= 3:
        return "HIGH"
    return "MEDIUM"


def _amount_anomaly(account_number: str, amount: float | None, banking_repo: BankingDataRepository) -> FraudIndicator | None:
    if amount is None:
        return None
    try:
        transactions = banking_repo.get_account_transactions(account_number)
    except BankingDataUnavailableError:
        return None

    amounts = [t.amount for t in transactions]
    if len(amounts) < settings.pattern_min_history_for_amount_baseline:
        return None  # cold start -- insufficient history to judge normality

    mean = statistics.mean(amounts)
    stdev = statistics.pstdev(amounts)
    if stdev < 0.01:
        return None

    z = (amount - mean) / stdev
    if abs(z) <= settings.pattern_amount_zscore_threshold:
        return None

    weight = settings.fraud_score_weights["pattern"]
    return FraudIndicator(
        type="AMOUNT_ANOMALY", severity=_severity_for_zscore(z),
        reason=(
            f"Cheque amount ({amount:,.2f}) deviates significantly from the account's historical "
            f"average ({mean:,.2f}, z-score={z:.2f})."
        ),
        contribution=weight * min(1.0, abs(z) / (settings.pattern_amount_zscore_threshold * 2)),
        evidence={"historical_mean": round(mean, 2), "historical_stdev": round(stdev, 2), "zscore": round(z, 2), "sample_size": len(amounts)},
    )


def _frequency_anomaly(
    account_number: str, processing_date: date, banking_repo: BankingDataRepository,
) -> FraudIndicator | None:
    try:
        transactions = banking_repo.get_account_transactions(account_number)
    except BankingDataUnavailableError:
        return None
    if not transactions:
        return None

    def _days_ago(txn_date_str: str) -> int | None:
        try:
            txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
        return (processing_date - txn_date).days

    baseline_count = sum(
        1 for t in transactions
        if (d := _days_ago(t.transaction_date)) is not None and 0 <= d <= settings.pattern_frequency_baseline_days
    )
    recent_count = sum(
        1 for t in transactions
        if (d := _days_ago(t.transaction_date)) is not None and 0 <= d <= settings.pattern_frequency_window_days
    )

    if recent_count < 3:
        return None  # too few recent cheques to be meaningful regardless of ratio

    expected_in_window = (
        baseline_count * (settings.pattern_frequency_window_days / settings.pattern_frequency_baseline_days)
    )
    if expected_in_window < 0.5:
        expected_in_window = 0.5  # avoid division blow-up for near-zero baselines

    ratio = recent_count / expected_in_window
    if ratio < settings.pattern_frequency_ratio_threshold:
        return None

    weight = settings.fraud_score_weights["pattern"]
    return FraudIndicator(
        type="FREQUENCY_ANOMALY", severity="HIGH" if ratio >= settings.pattern_frequency_ratio_threshold * 2 else "MEDIUM",
        reason=(
            f"{recent_count} cheques were processed for this account in the last "
            f"{settings.pattern_frequency_window_days} day(s), {ratio:.1f}x the expected rate "
            f"based on the last {settings.pattern_frequency_baseline_days} days of history."
        ),
        contribution=weight * min(1.0, ratio / (settings.pattern_frequency_ratio_threshold * 3)),
        evidence={"recent_count": recent_count, "baseline_count": baseline_count, "ratio": round(ratio, 2)},
    )


def _sequence_anomaly(
    account_number: str, cheque_number: str | None, banking_repo: BankingDataRepository,
) -> FraudIndicator | None:
    if not cheque_number:
        return None
    try:
        current = int(cheque_number)
    except ValueError:
        return None
    try:
        history = banking_repo.get_account_cheque_number_history(account_number)
    except BankingDataUnavailableError:
        return None

    historical_numbers = []
    for c in history:
        try:
            historical_numbers.append(int(c))
        except ValueError:
            continue
    if len(historical_numbers) < 2:
        return None

    min_gap = min(abs(current - h) for h in historical_numbers)
    if min_gap <= settings.pattern_cheque_sequence_gap_threshold:
        return None

    weight = settings.fraud_score_weights["pattern"]
    return FraudIndicator(
        type="CHEQUE_SEQUENCE_ANOMALY", severity="MEDIUM",
        reason=(
            f"Cheque number {cheque_number} is {min_gap} away from the nearest cheque number this "
            f"account has previously used, a larger gap than its recent usage pattern."
        ),
        contribution=weight * 0.5,
        evidence={"min_gap": min_gap, "historical_sample_size": len(historical_numbers)},
    )


def analyze(
    *,
    account_number: str | None,
    cheque_number: str | None,
    amount: float | None,
    processing_date: date,
    banking_repo: BankingDataRepository,
) -> list[FraudIndicator]:
    if not account_number:
        return []

    indicators: list[FraudIndicator] = []
    for detector in (
        lambda: _amount_anomaly(account_number, amount, banking_repo),
        lambda: _frequency_anomaly(account_number, processing_date, banking_repo),
        lambda: _sequence_anomaly(account_number, cheque_number, banking_repo),
    ):
        result = detector()
        if result is not None:
            indicators.append(result)
    return indicators
