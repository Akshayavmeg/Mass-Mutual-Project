"""Banking-domain ORM models (docs/25_Database_Schema.md S5-S6).

Synthetic/mock data only (ADR-0005) -- never real customer or account
information.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    bank_accounts: Mapped[list["BankAccount"]] = relationship(back_populates="customer")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False)
    account_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    routing_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_type: Mapped[str] = mapped_column(String(30), nullable=False)
    account_status: Mapped[str] = mapped_column(String(20), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    cheque_series_start: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cheque_series_end: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="bank_accounts")
    cheques: Mapped[list["Cheque"]] = relationship(back_populates="account")


class Payee(Base):
    """docs/24 S6 Banking Domain / docs/19 duplicate-detection evidence --
    the canonical `payees.csv` reference list, not documented as a table
    in docs/25's own table list but present in docs/24's banking domain
    and needed to seed the synthetic payee reference data."""

    __tablename__ = "payees"

    payee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payee_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ChequeIssuance(Base):
    """The bank's own issued-cheque registry (docs/16_Validation_Engine.md
    S12-S13 CHEQUE_SERIES/CHEQUE_STATUS checks source this); not itself
    one of docs/25's per-cheque *result* tables, but required banking
    reference data for validation to run against."""

    __tablename__ = "cheque_issuance"
    __table_args__ = ()

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=False)
    cheque_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_limit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)


class Transaction(Base):
    """Historical transaction data feeding anomaly/pattern detection
    (docs/20_Anomaly_Detection.md S6)."""

    __tablename__ = "transactions"

    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=False, index=True)
    transaction_date: Mapped[str] = mapped_column(String(10), nullable=False)  # ISO date string, matches CSV source
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    payee_name: Mapped[str] = mapped_column(String(255), nullable=False)


class ReferenceSignature(Base):
    """docs/18_Signature_Analysis.md S9 reference-signature registry."""

    __tablename__ = "reference_signatures"

    signature_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=False, index=True)
    signature_file: Mapped[str] = mapped_column(String(500), nullable=False)
    variant: Mapped[str] = mapped_column(String(30), nullable=False)


class ProcessedChequeHistory(Base):
    """docs/19_Duplicate_Detection.md S32 `processed_cheques` reference
    table -- historical cheques used as Level 1/2/3 duplicate-comparison
    candidates (distinct from `duplicate_results`, which stores the
    per-cheque duplicate-check OUTCOME, not the historical candidates
    compared against)."""

    __tablename__ = "processed_cheque_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_cheque_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=False, index=True)
    cheque_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    payee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    cheque_date: Mapped[str] = mapped_column(String(10), nullable=False)
    image_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    perceptual_hash: Mapped[str | None] = mapped_column(String(32), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False)
    processed_at: Mapped[str] = mapped_column(String(10), nullable=False)
