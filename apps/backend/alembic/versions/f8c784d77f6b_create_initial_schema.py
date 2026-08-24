"""create initial schema

Revision ID: f8c784d77f6b
Revises:
Create Date: 2026-08-24 12:40:04.995135

Hand-written rather than `alembic revision --autogenerate` (Milestone 8
report): autogenerate requires a live database connection to diff
against, and no PostgreSQL server was reachable in this environment.
This migration was written directly from app/models/ (docs/25_Database_Schema.md,
docs/27_Audit_Trail.md S13) instead, table-for-table and column-for-column.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f8c784d77f6b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. Table order follows the dependency graph
    (docs/25 S4: CUSTOMER -> BANK_ACCOUNT -> CHEQUE -> per-cheque
    result tables) so every foreign key already has its target."""

    op.create_table(
        "customers",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(20)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "bank_accounts",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.customer_id"), nullable=False),
        sa.Column("account_number", sa.String(30), nullable=False, unique=True),
        sa.Column("routing_number", sa.String(20), nullable=False),
        sa.Column("account_type", sa.String(30), nullable=False),
        sa.Column("account_status", sa.String(20), nullable=False),
        sa.Column("balance", sa.Numeric(15, 2), nullable=False),
        sa.Column("cheque_series_start", sa.String(30)),
        sa.Column("cheque_series_end", sa.String(30)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_bank_accounts_account_number", "bank_accounts", ["account_number"])

    op.create_table(
        "payees",
        sa.Column("payee_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("payee_name", sa.String(255), nullable=False),
        sa.Column("payee_type", sa.String(30)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "cheque_issuance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.account_id"), nullable=False),
        sa.Column("cheque_number", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("payee_name", sa.String(255), nullable=False),
        sa.Column("amount_limit", sa.Numeric(15, 2), nullable=False),
    )
    op.create_index("idx_cheque_issuance_cheque_number", "cheque_issuance", ["cheque_number"])

    op.create_table(
        "transactions",
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.account_id"), nullable=False),
        sa.Column("transaction_date", sa.String(10), nullable=False),
        sa.Column("transaction_type", sa.String(30), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("payee_name", sa.String(255), nullable=False),
    )
    op.create_index("idx_transactions_account_id", "transactions", ["account_id"])

    op.create_table(
        "reference_signatures",
        sa.Column("signature_id", sa.String(50), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.account_id"), nullable=False),
        sa.Column("signature_file", sa.String(500), nullable=False),
        sa.Column("variant", sa.String(30), nullable=False),
    )
    op.create_index("idx_reference_signatures_account_id", "reference_signatures", ["account_id"])

    op.create_table(
        "processed_cheque_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_cheque_id", sa.String(50), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.account_id"), nullable=False),
        sa.Column("cheque_number", sa.String(30), nullable=False),
        sa.Column("payee_name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("cheque_date", sa.String(10), nullable=False),
        sa.Column("image_hash", sa.String(64)),
        sa.Column("perceptual_hash", sa.String(32)),
        sa.Column("processing_status", sa.String(30), nullable=False),
        sa.Column("processed_at", sa.String(10), nullable=False),
    )
    op.create_index("idx_processed_history_source_cheque_id", "processed_cheque_history", ["source_cheque_id"])
    op.create_index("idx_processed_history_account_id", "processed_cheque_history", ["account_id"])
    op.create_index("idx_processed_history_cheque_number", "processed_cheque_history", ["cheque_number"])
    op.create_index("idx_processed_history_image_hash", "processed_cheque_history", ["image_hash"])

    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "cheques",
        sa.Column("cheque_id", sa.String(50), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.account_id"), nullable=True),
        sa.Column("cheque_number", sa.String(30)),
        sa.Column("cheque_series", sa.String(30)),
        sa.Column("routing_transit_number", sa.String(20)),
        sa.Column("payee_name", sa.String(255)),
        sa.Column("amount", sa.Numeric(15, 2)),
        sa.Column("cheque_date", sa.Date()),
        sa.Column("image_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_hash", sa.String(64)),
        sa.Column("processing_status", sa.String(30), nullable=False, server_default="UPLOADED"),
        sa.Column("upload_metadata", postgresql.JSONB()),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("amount IS NULL OR amount >= 0", name="chk_cheque_amount_non_negative"),
    )
    op.create_index("idx_cheques_cheque_number", "cheques", ["cheque_number"])
    op.create_index("idx_cheques_account_id", "cheques", ["account_id"])
    op.create_index("idx_cheques_processing_status", "cheques", ["processing_status"])
    op.create_index("idx_cheques_uploaded_at", "cheques", ["uploaded_at"])

    op.create_table(
        "ocr_results",
        sa.Column("ocr_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("engine_name", sa.String(50), nullable=False),
        sa.Column("engine_version", sa.String(50)),
        sa.Column("raw_text", sa.Text()),
        sa.Column("confidence_score", sa.Numeric(5, 2)),
        sa.Column("processing_time_ms", sa.Integer()),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("extracted_fields", postgresql.JSONB()),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "validation_results",
        sa.Column("validation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("account_valid", sa.Boolean(), nullable=False),
        sa.Column("cheque_number_valid", sa.Boolean(), nullable=False),
        sa.Column("series_valid", sa.Boolean(), nullable=False),
        sa.Column("routing_transit_number_valid", sa.Boolean(), nullable=False),
        sa.Column("date_valid", sa.Boolean(), nullable=False),
        sa.Column("payee_match", sa.Boolean()),
        sa.Column("amount_valid", sa.Boolean()),
        sa.Column("overall_status", sa.String(20), nullable=False),
        sa.Column("validation_message", sa.Text()),
        sa.Column("checks", postgresql.JSONB()),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("overall_status IN ('PASS','FAIL','WARNING')", name="chk_validation_overall_status"),
    )

    op.create_table(
        "fraud_results",
        sa.Column("fraud_result_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("tampering_detected", sa.Boolean(), nullable=False),
        sa.Column("tampering_score", sa.Numeric(5, 2)),
        sa.Column("fraud_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("fraud_level", sa.String(20), nullable=False),
        sa.Column("indicators", postgresql.JSONB()),
        sa.Column("model_name", sa.String(100)),
        sa.Column("model_version", sa.String(50)),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("fraud_score >= 0 AND fraud_score <= 100", name="chk_fraud_score_range"),
    )
    op.create_index("idx_fraud_results_fraud_level", "fraud_results", ["fraud_level"])
    op.create_index("idx_fraud_results_fraud_score", "fraud_results", ["fraud_score"])

    op.create_table(
        "signature_results",
        sa.Column("signature_result_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("similarity_score", sa.Numeric(5, 2)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("model_name", sa.String(100)),
        sa.Column("model_version", sa.String(50)),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "similarity_score IS NULL OR (similarity_score >= 0 AND similarity_score <= 100)",
            name="chk_signature_similarity_range",
        ),
    )

    op.create_table(
        "duplicate_results",
        sa.Column("duplicate_result_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False),
        sa.Column("duplicate_detected", sa.Boolean(), nullable=False),
        sa.Column("matched_cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id")),
        sa.Column("similarity_score", sa.Numeric(5, 2)),
        sa.Column("comparison_method", sa.String(50)),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_duplicate_results_cheque_id", "duplicate_results", ["cheque_id"])

    op.create_table(
        "anomaly_results",
        sa.Column("anomaly_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("anomaly_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("anomaly_level", sa.String(20), nullable=False),
        sa.Column("detected_patterns", postgresql.JSONB()),
        sa.Column("model_name", sa.String(100)),
        sa.Column("model_version", sa.String(50)),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("risk_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("fraud_score", sa.Numeric(5, 2)),
        sa.Column("validation_score", sa.Numeric(5, 2)),
        sa.Column("signature_score", sa.Numeric(5, 2)),
        sa.Column("duplicate_score", sa.Numeric(5, 2)),
        sa.Column("anomaly_score", sa.Numeric(5, 2)),
        sa.Column("overall_risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("risk_factors", postgresql.JSONB()),
        sa.Column("model_version", sa.String(50)),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("overall_risk_score >= 0 AND overall_risk_score <= 100", name="chk_risk_score_range"),
    )
    op.create_index("idx_risk_assessments_risk_level", "risk_assessments", ["risk_level"])
    op.create_index("idx_risk_assessments_overall_score", "risk_assessments", ["overall_risk_score"])

    op.create_table(
        "decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False, unique=True),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("decision_rule", sa.String(100)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("review_required", sa.Boolean(), nullable=False),
        sa.Column("engine_version", sa.String(50)),
        sa.Column("triggered_rules", postgresql.JSONB()),
        sa.Column("reasons", postgresql.JSONB()),
        sa.Column("full_result", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("decision IN ('APPROVE','REVIEW','REJECT')", name="chk_decision_value"),
    )
    op.create_index("idx_decisions_decision", "decisions", ["decision"])

    op.create_table(
        "manual_review_cases",
        sa.Column("review_case_id", sa.String(50), primary_key=True),
        sa.Column("cheque_id", sa.String(50), sa.ForeignKey("cheques.cheque_id"), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("trigger_reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("assigned_reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id")),
        sa.Column("reviewer_decision", sa.String(20)),
        sa.Column("reviewer_comment", sa.Text()),
        sa.Column("comments", postgresql.JSONB()),
        sa.Column("automated_decision", postgresql.JSONB()),
        sa.Column("risk_score", sa.Numeric(5, 2)),
        sa.Column("escalation_reason", sa.Text()),
        sa.Column("full_case", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("assigned_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "reviewer_decision IS NULL OR reviewer_decision IN ('APPROVE','REJECT')",
            name="chk_reviewer_decision_value",
        ),
    )
    op.create_index("idx_review_cases_status", "manual_review_cases", ["status"])
    op.create_index("idx_review_cases_priority", "manual_review_cases", ["priority"])
    op.create_index("idx_review_cases_reviewer", "manual_review_cases", ["assigned_reviewer_id"])
    op.create_index("idx_review_cases_cheque_id", "manual_review_cases", ["cheque_id"])

    op.create_table(
        "audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cheque_id", sa.String(50)),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.String(100)),
        sa.Column("user_role", sa.String(50)),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("previous_status", sa.String(50)),
        sa.Column("new_status", sa.String(50)),
        sa.Column("action", sa.String(100)),
        sa.Column("result", sa.String(50)),
        sa.Column("reason", sa.Text()),
        sa.Column("request_id", sa.String(100)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("metadata", postgresql.JSONB()),
    )
    op.create_index("idx_audit_logs_cheque_id", "audit_logs", ["cheque_id"])
    op.create_index("idx_audit_logs_event_timestamp", "audit_logs", ["event_timestamp"])


def downgrade() -> None:
    """Downgrade schema -- reverse dependency order."""
    op.drop_table("audit_logs")
    op.drop_table("manual_review_cases")
    op.drop_table("decisions")
    op.drop_table("risk_assessments")
    op.drop_table("anomaly_results")
    op.drop_table("duplicate_results")
    op.drop_table("signature_results")
    op.drop_table("fraud_results")
    op.drop_table("validation_results")
    op.drop_table("ocr_results")
    op.drop_table("cheques")
    op.drop_table("users")
    op.drop_table("processed_cheque_history")
    op.drop_table("reference_signatures")
    op.drop_table("transactions")
    op.drop_table("cheque_issuance")
    op.drop_table("payees")
    op.drop_table("bank_accounts")
    op.drop_table("customers")
