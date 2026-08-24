"""Anomaly Detection orchestrator (docs/20_Anomaly_Detection.md S4, S42
final architecture).

Implements the explainable hybrid (rule-based + statistical) baseline
docs/20 S27-S28 recommends for the MVP. No ML layer (Isolation Forest,
docs/20 S24-S26) is implemented: the synthetic dataset has only a
handful of transactions per account, far too little to train and
honestly evaluate an unsupervised model without overfitting/fabricating
a result (mirrors ADR-0004's reasoning for deferring a trained fraud
model). This is a deliberate, documented deferral, not an oversight --
see the Milestone 6 report.

Timing Anomaly (docs/20 S17) and Account Behavior Anomaly (docs/20 S7,
never given its own algorithm in the source document beyond the
already-covered amount/frequency/payee/sequence signals) are likewise
NOT implemented: docs/20 S17 itself says timing analysis should only be
used "if reliable transaction timestamp data is available" -- the
Milestone 1 dataset's transactions.csv has only a transaction_date, no
intraday timestamp, so there is no real evidence to analyze.

Module boundary (docs/20 S1, S31-S32): produces an anomaly score/
evidence for the Fraud Detection Engine and Risk Scoring -- never an
independent fraud verdict.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError, get_banking_repository
from app.repositories.cheque_repository import get_cheque_repository
from app.services.audit import audit_service
from app.services.anomaly.detectors import amount_anomaly, frequency_anomaly, payee_anomaly, sequence_anomaly, transaction_pattern_anomaly
from app.services.anomaly.exceptions import ChequeNotExtractedForAnomalyError
from app.services.anomaly.models import AnomalyItem, AnomalyResult

_MODEL_NAME = "anomaly-rule-statistical"


def _field_value(fields: dict, name: str):
    return fields.get(name, {}).get("value")


def _classify_risk(score: float) -> str:
    for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        low, high = settings.anomaly_risk_bands[level]
        if low <= score <= high:
            return level
    return "CRITICAL"


def analyze_anomaly(
    cheque_id: str, *, processing_date: date | None = None, banking_repo: BankingDataRepository | None = None,
) -> AnomalyResult:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    extraction = record.get("extraction")
    if extraction is None:
        raise ChequeNotExtractedForAnomalyError(
            "Cheque has not completed OCR/extraction yet; anomaly analysis cannot run."
        )

    banking_repo = banking_repo or get_banking_repository()
    processing_date = processing_date or datetime.now(timezone.utc).date()
    fields = extraction.get("fields", {})
    account_number = _field_value(fields, "account_number")
    cheque_number = _field_value(fields, "cheque_number")
    amount = _field_value(fields, "amount")
    payee_name = _field_value(fields, "payee_name")

    unavailable_inputs: list[str] = []
    transactions: list = []
    cheque_number_history: list[str] = []
    if account_number:
        try:
            transactions = banking_repo.get_account_transactions(account_number)
            cheque_number_history = banking_repo.get_account_cheque_number_history(account_number)
        except BankingDataUnavailableError:
            unavailable_inputs.append("TRANSACTION_HISTORY")
    else:
        unavailable_inputs.append("ACCOUNT_NUMBER")

    component_anomalies: list[AnomalyItem] = []
    for item in (
        amount_anomaly(amount, transactions),
        frequency_anomaly(transactions, processing_date),
        payee_anomaly(payee_name, transactions),
        sequence_anomaly(cheque_number, cheque_number_history),
    ):
        if item is not None:
            component_anomalies.append(item)

    pattern_item = transaction_pattern_anomaly(component_anomalies)
    all_anomalies = component_anomalies + ([pattern_item] if pattern_item else [])

    anomaly_score = min(100.0, sum(a.contribution for a in all_anomalies))
    risk_level = _classify_risk(anomaly_score)

    result = AnomalyResult(
        cheque_id=cheque_id, account_number=account_number, anomaly_score=anomaly_score,
        risk_level=risk_level, anomalies=all_anomalies, model_name=_MODEL_NAME,
        model_version=settings.anomaly_engine_version,
        analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        analysis_status="INSUFFICIENT_DATA" if "TRANSACTION_HISTORY" in unavailable_inputs else "COMPLETED",
        unavailable_inputs=unavailable_inputs,
    )

    repo.update(cheque_id, {"anomaly_analysis": result.as_dict(), "processing_status": "ANOMALY_ANALYZED"})
    audit_service.record(
        event_type="ANOMALY_ANALYSIS_COMPLETED", cheque_id=cheque_id, source="SYSTEM",
        new_status="ANOMALY_ANALYZED", action="RUN_ANOMALY_ANALYSIS", result=risk_level,
        metadata={"anomaly_score": anomaly_score},
    )
    return result


def get_anomaly_result(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("anomaly_analysis")
