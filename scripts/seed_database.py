"""Loads the Milestone 1 synthetic banking dataset (data/mock_banking_data/)
into PostgreSQL (Milestone 8; docs/25_Database_Schema.md, ADR-0005).

Synthetic/mock data only -- never real customer or banking information
(per ADR-0005, unchanged by this milestone). Deterministic and safely
repeatable: every row's UUID primary key is derived via uuid5 from its
CSV natural key (e.g. "CUST-0001", an account number, a cheque_id), so
re-running this script re-derives the SAME UUIDs and upserts rather than
duplicating rows.

This script is intentionally NOT run automatically at application
startup (per this milestone's explicit instruction) -- invoke it
manually:

    apps/backend/.venv/Scripts/python.exe scripts/seed_database.py

Requires a reachable PostgreSQL server (DATABASE_URL); if none is
configured/reachable, this script reports that clearly and exits
without partially seeding anything.
"""

from __future__ import annotations

import csv
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "backend"))

DATA_DIR = REPO_ROOT / "data" / "mock_banking_data"
NAMESPACE = uuid.NAMESPACE_URL


def deterministic_uuid(*parts: str) -> uuid.UUID:
    """Same natural key always maps to the same UUID -- this is what
    makes re-running the seed script idempotent (upsert, not duplicate)."""
    return uuid.uuid5(NAMESPACE, "|".join(parts))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    from app.core.database import SessionLocal, check_database_connection
    from app.models.banking import (
        BankAccount, ChequeIssuance, Customer, Payee, ProcessedChequeHistory,
        ReferenceSignature, Transaction,
    )

    if not check_database_connection():
        print(
            "ERROR: No reachable PostgreSQL database is configured "
            "(see DATABASE_URL / app.core.config.settings.database_url). "
            "Seeding was NOT performed -- nothing was partially written.",
            file=sys.stderr,
        )
        return 1

    session = SessionLocal()
    try:
        customer_uuid: dict[str, uuid.UUID] = {}
        account_uuid: dict[str, uuid.UUID] = {}

        customers = read_csv(DATA_DIR / "customers.csv")
        for row in customers:
            cid = deterministic_uuid("customer", row["customer_id"])
            customer_uuid[row["customer_id"]] = cid
            session.merge(Customer(
                customer_id=cid, customer_name=row["customer_name"],
                email=row.get("email") or None, phone=row.get("phone") or None,
                status=row["status"],
            ))
        print(f"customers: {len(customers)} rows")

        # accounts.csv links to customers.csv by customer_id (e.g. "CUST-0001")
        accounts = read_csv(DATA_DIR / "accounts.csv")
        for row in accounts:
            aid = deterministic_uuid("account", row["account_number"])
            account_uuid[row["account_number"]] = aid
            cust_id = customer_uuid.get(row["customer_id"])
            if cust_id is None:
                continue  # orphaned reference in source data -- skip rather than fabricate a customer
            session.merge(BankAccount(
                account_id=aid, customer_id=cust_id, account_number=row["account_number"],
                routing_number=row["routing_number"], account_type=row["account_type"],
                account_status=row["account_status"], balance=float(row["balance"]),
                cheque_series_start=row.get("cheque_series_start") or None,
                cheque_series_end=row.get("cheque_series_end") or None,
            ))
        print(f"bank_accounts: {len(accounts)} rows")
        session.flush()

        payees = read_csv(DATA_DIR / "payees.csv")
        for row in payees:
            session.merge(Payee(
                payee_id=deterministic_uuid("payee", row["payee_id"]),
                payee_name=row["payee_name"], payee_type=row.get("payee_type") or None,
            ))
        print(f"payees: {len(payees)} rows")

        issuance_rows = read_csv(DATA_DIR / "cheque_issuance.csv")
        skipped_issuance = 0
        for row in issuance_rows:
            aid = account_uuid.get(row["account_number"])
            if aid is None:
                skipped_issuance += 1
                continue
            session.merge(ChequeIssuance(
                id=deterministic_uuid("issuance", row["account_number"], row["cheque_number"]),
                account_id=aid, cheque_number=row["cheque_number"], status=row["status"],
                payee_name=row["payee_name"], amount_limit=float(row["amount_limit"]),
            ))
        print(f"cheque_issuance: {len(issuance_rows) - skipped_issuance}/{len(issuance_rows)} rows")

        transactions = read_csv(DATA_DIR / "transactions.csv")
        skipped_txn = 0
        for row in transactions:
            aid = account_uuid.get(row["account_number"])
            if aid is None:
                skipped_txn += 1
                continue
            session.merge(Transaction(
                transaction_id=deterministic_uuid("transaction", row["transaction_id"]),
                account_id=aid, transaction_date=row["transaction_date"],
                transaction_type=row["transaction_type"], amount=float(row["amount"]),
                payee_name=row["payee_name"],
            ))
        print(f"transactions: {len(transactions) - skipped_txn}/{len(transactions)} rows")

        sig_index = read_csv(DATA_DIR / "reference_signatures" / "signatures_index.csv")
        skipped_sig = 0
        for row in sig_index:
            aid = account_uuid.get(row["account_number"])
            if aid is None:
                skipped_sig += 1
                continue
            session.merge(ReferenceSignature(
                signature_id=row["signature_id"], account_id=aid,
                signature_file=row["signature_file"], variant=row["variant"],
            ))
        print(f"reference_signatures: {len(sig_index) - skipped_sig}/{len(sig_index)} rows")

        history_rows = read_csv(DATA_DIR / "processed_cheques_history.csv")
        skipped_history = 0
        inserted_history = 0
        for row in history_rows:
            if not row.get("cheque_number"):
                continue  # historical transactions with no associated cheque number (matches banking_repository.py's own CSV-loading rule)
            aid = account_uuid.get(row["account_number"])
            if aid is None:
                skipped_history += 1
                continue
            session.merge(ProcessedChequeHistory(
                id=deterministic_uuid("history", row["cheque_id"]),
                source_cheque_id=row["cheque_id"], account_id=aid, cheque_number=row["cheque_number"],
                payee_name=row["payee_name"], amount=float(row["amount"]), cheque_date=row["cheque_date"],
                image_hash=row.get("image_hash") or None, perceptual_hash=row.get("perceptual_hash") or None,
                processing_status=row["processing_status"], processed_at=row["processed_at"],
            ))
            inserted_history += 1
        print(f"processed_cheque_history: {inserted_history}/{len(history_rows)} rows")

        session.commit()
        print("\nSeed completed successfully (synthetic/mock data only, per ADR-0005).")
        return 0
    except Exception as exc:  # noqa: BLE001 - report and roll back rather than leave a partial seed
        session.rollback()
        print(f"ERROR during seeding, rolled back: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
