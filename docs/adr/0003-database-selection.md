# ADR-0003: Database Selection

## Status

Accepted

## Decision

The system will use **PostgreSQL** as its primary relational database.

## Context

The system must persist cheques, OCR results, validation results, fraud/signature/duplicate/anomaly results, risk assessments, decisions, manual review cases, users, and a complete, append-only audit trail (`24_Database_Architecture.md`, `25_Database_Schema.md`, `27_Audit_Trail.md`). It requires referential integrity between customers → bank accounts → cheques → per-cheque result tables, transactional consistency for multi-table updates (e.g., a reviewer decision updating a review case, the cheque status, and creating an audit event together), semi-structured storage for fraud indicators and audit metadata, and CHECK constraints enforcing score ranges (0–100) and enumerated decision values.

## Alternatives Considered

No alternative database engine (e.g., MySQL/MariaDB, MongoDB, SQLite) is discussed anywhere in the project documentation as having been evaluated and rejected — PostgreSQL is the only database named across `11_Technology_Stack.md`, `24_Database_Architecture.md`, `25_Database_Schema.md`, and `37_Deployment_Architecture.md`, all independently and consistently. This ADR records the rationale for that consistent choice rather than a comparison against alternatives that were never documented as candidates.

## Selected Approach

PostgreSQL, accessed from the FastAPI backend through an ORM/repository layer (SQLAlchemy, with Alembic for schema migrations per `24_Database_Architecture.md` §36), such that the frontend never connects to the database directly — all data access goes through the backend API/service layer.

## Reason for Selection

* Strong ACID transaction support, required for multi-table updates such as recording a reviewer decision alongside the cheque status and an audit event in a single transaction.
* Native foreign-key and CHECK constraint support, used throughout the schema (e.g., `decision IN ('APPROVE','REVIEW','REJECT')`, `overall_risk_score BETWEEN 0 AND 100`).
* Native JSONB support, used for semi-structured fields such as `fraud_results.indicators`, `anomaly_results.detected_patterns`, and `audit_logs.metadata`.
* Mature indexing support for the query patterns the dashboard and review queue require (status filters, risk-level filters, time-range queries).
* Well-supported from Python via SQLAlchemy/Alembic, consistent with the FastAPI backend selected in ADR-0001.
* Open source, with no licensing constraint on a prototype built from synthetic data.

## Consequences

* Cheque images themselves are not stored in PostgreSQL; only a file-path reference (`cheques.image_path`) is stored, with the actual image kept in `data/sample_cheques/` for the prototype (or object storage in a future deployment). Large binary storage in the relational database is intentionally avoided.
* Database credentials must be supplied via environment variables / secrets management and must never be committed to the repository (`NFR-010`, `28_Security_and_Privacy.md`).
* Schema changes must go through Alembic migrations, not manual edits to a live schema.
* The development database (`mass_mutual_db`) will contain only synthetic/mock data, consistent with ADR-0005.
