"""ORM models (Milestone 8; docs/25_Database_Schema.md).

Importing this package registers every table on `app.core.database.Base`
-- required both for Alembic's autogenerate support and so relationship()
string references between modules (e.g. Cheque.ocr_result -> "OCRResult")
resolve correctly.
"""

from __future__ import annotations

from app.models.audit import AuditLog
from app.models.banking import (
    BankAccount,
    ChequeIssuance,
    Customer,
    Payee,
    ProcessedChequeHistory,
    ReferenceSignature,
    Transaction,
)
from app.models.cheque import Cheque
from app.models.processing_results import (
    AnomalyResult,
    Decision,
    DuplicateResult,
    FraudResult,
    OCRResult,
    RiskAssessment,
    SignatureResult,
    ValidationResult,
)
from app.models.review import ManualReviewCase, User

__all__ = [
    "AuditLog",
    "BankAccount",
    "ChequeIssuance",
    "Customer",
    "Payee",
    "ProcessedChequeHistory",
    "ReferenceSignature",
    "Transaction",
    "Cheque",
    "AnomalyResult",
    "Decision",
    "DuplicateResult",
    "FraudResult",
    "OCRResult",
    "RiskAssessment",
    "SignatureResult",
    "ValidationResult",
    "ManualReviewCase",
    "User",
]
