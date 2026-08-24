"""PostgreSQL-backed implementation of BankingDataRepository (Milestone
8), implementing the exact same interface as
app.repositories.banking_repository.CSVBankingDataRepository so
Milestones 4-6's validation/fraud/anomaly/signature services do not
change at all.
"""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import SessionLocal
from app.models.banking import (
    BankAccount,
    ChequeIssuance,
    ProcessedChequeHistory,
    ReferenceSignature,
    Transaction,
)
from app.repositories.banking_repository import (
    AccountRecord,
    ChequeIssuanceRecord,
    DuplicateMatch,
    ImageHashRecord,
    ReferenceSignatureRecord,
    TransactionRecord,
)


def _account_record(row: BankAccount) -> AccountRecord:
    return AccountRecord(
        account_number=row.account_number, customer_id=str(row.customer_id),
        account_status=row.account_status, account_type=row.account_type,
        balance=float(row.balance), routing_number=row.routing_number,
        bank_code="DEMO001", cheque_series_start=row.cheque_series_start or "",
        cheque_series_end=row.cheque_series_end or "",
    )


class PostgresBankingDataRepository:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    def get_account(self, account_number: str) -> AccountRecord | None:
        with self._session_factory() as session:
            row = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            return _account_record(row) if row else None

    def get_cheque_issuance(self, account_number: str, cheque_number: str) -> ChequeIssuanceRecord | None:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return None
            row = session.query(ChequeIssuance).filter_by(account_id=account.account_id, cheque_number=cheque_number).one_or_none()
            if row is None:
                return None
            return ChequeIssuanceRecord(
                cheque_number=row.cheque_number, account_number=account_number,
                status=row.status, payee_name=row.payee_name, amount_limit=float(row.amount_limit),
            )

    def find_duplicate(self, account_number: str, cheque_number: str, amount: float, cheque_date: str) -> DuplicateMatch | None:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return None
            candidates = session.query(ProcessedChequeHistory).filter_by(
                account_id=account.account_id, cheque_number=cheque_number, cheque_date=cheque_date,
            ).all()
            for row in candidates:
                if abs(float(row.amount) - amount) < 0.01:
                    return DuplicateMatch(
                        cheque_id=row.source_cheque_id, account_number=account_number,
                        cheque_number=cheque_number, payee_name=row.payee_name,
                        amount=float(row.amount), cheque_date=row.cheque_date,
                    )
            return None

    def get_account_transactions(self, account_number: str) -> list[TransactionRecord]:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return []
            rows = session.query(Transaction).filter_by(account_id=account.account_id).order_by(Transaction.transaction_date).all()
            return [
                TransactionRecord(
                    transaction_id=str(r.transaction_id), account_number=account_number,
                    transaction_date=r.transaction_date, transaction_type=r.transaction_type,
                    amount=float(r.amount), payee_name=r.payee_name,
                )
                for r in rows
            ]

    def get_image_hash_index(self) -> list[ImageHashRecord]:
        with self._session_factory() as session:
            rows = session.query(ProcessedChequeHistory).filter(ProcessedChequeHistory.image_hash.isnot(None)).all()
            result = []
            for r in rows:
                account = session.get(BankAccount, r.account_id)
                result.append(ImageHashRecord(
                    cheque_id=r.source_cheque_id, account_number=account.account_number if account else "",
                    cheque_number=r.cheque_number, image_hash=r.image_hash or "", perceptual_hash=r.perceptual_hash or "",
                ))
            return result

    def find_by_account_and_cheque_number(self, account_number: str, cheque_number: str) -> list[DuplicateMatch]:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return []
            rows = session.query(ProcessedChequeHistory).filter_by(account_id=account.account_id, cheque_number=cheque_number).all()
            return [
                DuplicateMatch(
                    cheque_id=r.source_cheque_id, account_number=account_number, cheque_number=cheque_number,
                    payee_name=r.payee_name, amount=float(r.amount), cheque_date=r.cheque_date,
                )
                for r in rows
            ]

    def get_account_cheque_number_history(self, account_number: str) -> list[str]:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return []
            rows = session.query(ProcessedChequeHistory).filter_by(account_id=account.account_id).all()
            return [r.cheque_number for r in rows]

    def get_reference_signatures(self, account_number: str) -> list[ReferenceSignatureRecord]:
        with self._session_factory() as session:
            account = session.query(BankAccount).filter_by(account_number=account_number).one_or_none()
            if account is None:
                return []
            rows = session.query(ReferenceSignature).filter_by(account_id=account.account_id).all()
            return [
                ReferenceSignatureRecord(
                    signature_id=r.signature_id, account_number=account_number,
                    signature_file=r.signature_file, variant=r.variant,
                )
                for r in rows
            ]
