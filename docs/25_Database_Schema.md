# Database Schema
# 25. Database Schema

## 1. Introduction

The **Database Schema** defines the logical and physical structure of the PostgreSQL database used by the **AI-Powered Cheque Scanning, Validation & Fraud Detection System**.

The schema defines:

* Tables
* Columns
* Data types
* Primary keys
* Foreign keys
* Constraints
* Relationships
* Indexes
* Enumerated values
* Audit information

The database is designed around the **cheque-processing lifecycle**, beginning with cheque upload and OCR extraction and continuing through validation, fraud analysis, risk assessment, decision-making, manual review, and auditing.

The MVP will use **synthetic/mock banking data**. No real customer or banking information should be stored in the development database.

---

# 2. Database Schema Overview

The proposed PostgreSQL database is named:

```text
mass_mutual_db
```

The major tables are:

```text
customers
bank_accounts
cheques
ocr_results
validation_results
fraud_results
signature_results
duplicate_results
anomaly_results
risk_assessments
decisions
users
manual_review_cases
audit_logs
```

The central entity is the `cheques` table.

```text
CUSTOMERS
    │
    ▼
BANK_ACCOUNTS
    │
    ▼
CHEQUES
    │
    ├── OCR_RESULTS
    ├── VALIDATION_RESULTS
    ├── FRAUD_RESULTS
    ├── SIGNATURE_RESULTS
    ├── DUPLICATE_RESULTS
    ├── ANOMALY_RESULTS
    ├── RISK_ASSESSMENTS
    ├── DECISIONS
    ├── MANUAL_REVIEW_CASES
    └── AUDIT_LOGS
```

---

# 3. Design Principles

The database follows these principles:

1. **Relational design** for structured banking and cheque data.
2. **Normalization** to reduce unnecessary duplication.
3. **Referential integrity** using foreign keys.
4. **Traceability** through audit records.
5. **Security** through role-based access and controlled database access.
6. **Extensibility** so additional fraud models and validation rules can be added later.
7. **Explainability** by storing individual validation and fraud results instead of only the final decision.
8. **Synthetic data protection** for the MVP.

---

# 4. Entity Relationship Structure

The primary relationships are:

```text
CUSTOMER
   │
   │ 1:N
   ▼
BANK_ACCOUNT
   │
   │ 1:N
   ▼
CHEQUE
   │
   ├──────── 1:1 ──────── OCR_RESULT
   ├──────── 1:1 ──────── VALIDATION_RESULT
   ├──────── 1:1 ──────── FRAUD_RESULT
   ├──────── 1:1 ──────── SIGNATURE_RESULT
   ├──────── 1:1 ──────── DUPLICATE_RESULT
   ├──────── 1:1 ──────── ANOMALY_RESULT
   ├──────── 1:N ──────── RISK_ASSESSMENT
   ├──────── 1:N ──────── DECISION
   ├──────── 1:N ──────── MANUAL_REVIEW_CASE
   └──────── 1:N ──────── AUDIT_LOG

USER
   │
   ├──────── 1:N ──────── MANUAL_REVIEW_CASE
   └──────── 1:N ──────── AUDIT_LOG
```

---

# 5. `customers` Table

Stores synthetic customer information used by the mock banking system.

| Column          | Data Type    | Constraints | Description                |
| --------------- | ------------ | ----------- | -------------------------- |
| `customer_id`   | UUID         | PK          | Unique customer identifier |
| `customer_name` | VARCHAR(150) | NOT NULL    | Synthetic customer name    |
| `email`         | VARCHAR(255) | NULL        | Synthetic email            |
| `phone`         | VARCHAR(20)  | NULL        | Synthetic phone            |
| `status`        | VARCHAR(20)  | NOT NULL    | ACTIVE/INACTIVE            |
| `created_at`    | TIMESTAMP    | NOT NULL    | Record creation time       |
| `updated_at`    | TIMESTAMP    | NOT NULL    | Last update time           |

### Primary Key

```text
customer_id
```

### Example

```text
customer_id: 550e8400-e29b-41d4-a716-446655440000
customer_name: Ravi Kumar
status: ACTIVE
```

---

# 6. `bank_accounts` Table

Stores synthetic banking account information.

| Column           | Data Type     | Constraints      | Description                 |
| ---------------- | ------------- | ---------------- | --------------------------- |
| `account_id`     | UUID          | PK               | Unique account identifier   |
| `customer_id`    | UUID          | FK               | References customers        |
| `account_number` | VARCHAR(30)   | UNIQUE, NOT NULL | Mock account number         |
| `routing_number` | VARCHAR(20)   | NOT NULL         | Mock routing/transit number |
| `account_type`   | VARCHAR(30)   | NOT NULL         | Account type                |
| `account_status` | VARCHAR(20)   | NOT NULL         | ACTIVE/CLOSED/BLOCKED       |
| `balance`        | NUMERIC(15,2) | NOT NULL         | Mock account balance        |
| `created_at`     | TIMESTAMP     | NOT NULL         | Creation timestamp          |
| `updated_at`     | TIMESTAMP     | NOT NULL         | Last update                 |

### Foreign Key

```text
customer_id → customers.customer_id
```

### Relationship

```text
customers 1 ───────── N bank_accounts
```

---

# 7. `cheques` Table

The `cheques` table is the **central table** of the application.

It stores information about each cheque submitted for processing.

| Column              | Data Type     | Constraints  | Description                      |
| ------------------- | ------------- | ------------ | -------------------------------- |
| `cheque_id`         | UUID          | PK           | Unique cheque identifier         |
| `account_id`        | UUID          | FK, NOT NULL | Associated bank account          |
| `cheque_number`     | VARCHAR(30)   | NOT NULL     | Cheque number                    |
| `cheque_series`     | VARCHAR(30)   | NULL         | Cheque series                    |
| `routing_transit_number` | VARCHAR(20) | NULL     | Extracted routing/transit number |
| `payee_name`        | VARCHAR(255)  | NULL         | Extracted payee                  |
| `amount`            | NUMERIC(15,2) | NULL         | Cheque amount                    |
| `cheque_date`       | DATE          | NULL         | Date written on cheque           |
| `image_path`        | TEXT          | NOT NULL     | Image/file reference             |
| `file_type`         | VARCHAR(20)   | NOT NULL     | JPEG/PNG/PDF                     |
| `processing_status` | VARCHAR(30)   | NOT NULL     | Current processing state         |
| `uploaded_at`       | TIMESTAMP     | NOT NULL     | Upload timestamp                 |
| `processed_at`      | TIMESTAMP     | NULL         | Processing completion            |
| `created_at`        | TIMESTAMP     | NOT NULL     | Record creation                  |
| `updated_at`        | TIMESTAMP     | NOT NULL     | Last update                      |

### Foreign Key

```text
account_id → bank_accounts.account_id
```

### Example processing statuses

```text
UPLOADED
PROCESSING
OCR_COMPLETED
VALIDATED
FRAUD_ANALYZED
APPROVED
UNDER_REVIEW
REJECTED
FAILED
```

---

# 8. `ocr_results` Table

Stores OCR processing results for a cheque.

| Column               | Data Type    | Constraints | Description                |
| -------------------- | ------------ | ----------- | -------------------------- |
| `ocr_id`             | UUID         | PK          | Unique OCR result          |
| `cheque_id`          | UUID         | FK, UNIQUE  | Associated cheque          |
| `engine_name`        | VARCHAR(50)  | NOT NULL    | OCR engine                 |
| `engine_version`     | VARCHAR(50)  | NULL        | Engine version             |
| `raw_text`           | TEXT         | NULL        | Raw OCR output             |
| `confidence_score`   | NUMERIC(5,2) | NULL        | OCR confidence percentage  |
| `processing_time_ms` | INTEGER      | NULL        | OCR processing time        |
| `status`             | VARCHAR(20)  | NOT NULL    | SUCCESS/FAILED             |
| `error_message`      | TEXT         | NULL        | Error if processing failed |
| `created_at`         | TIMESTAMP    | NOT NULL    | Processing timestamp       |

### Relationship

```text
cheques 1 ───────── 1 ocr_results
```

---

# 9. `validation_results` Table

Stores individual validation results generated by the Validation Engine.

| Column                 | Data Type   | Constraints | Description               |
| ---------------------- | ----------- | ----------- | ------------------------- |
| `validation_id`        | UUID        | PK          | Unique validation record  |
| `cheque_id`            | UUID        | FK, UNIQUE  | Associated cheque         |
| `account_valid`        | BOOLEAN     | NOT NULL    | Account validation        |
| `cheque_number_valid`  | BOOLEAN     | NOT NULL    | Cheque number validation  |
| `series_valid`         | BOOLEAN     | NOT NULL    | Cheque series validation  |
| `routing_transit_number_valid` | BOOLEAN | NOT NULL | Routing/transit number validation |
| `date_valid`           | BOOLEAN     | NOT NULL    | Date validation           |
| `payee_match`          | BOOLEAN     | NULL        | Payee verification result |
| `amount_valid`         | BOOLEAN     | NULL        | Amount validation         |
| `overall_status`       | VARCHAR(20) | NOT NULL    | PASS/FAIL/WARNING         |
| `validation_message`   | TEXT        | NULL        | Explanation               |
| `created_at`           | TIMESTAMP   | NOT NULL    | Validation timestamp      |

---

# 10. `fraud_results` Table

Stores the results generated by the Fraud Detection module.

| Column               | Data Type    | Constraints | Description               |
| -------------------- | ------------ | ----------- | ------------------------- |
| `fraud_result_id`    | UUID         | PK          | Unique result             |
| `cheque_id`          | UUID         | FK, UNIQUE  | Associated cheque         |
| `tampering_detected` | BOOLEAN      | NOT NULL    | Image tampering indicator |
| `tampering_score`    | NUMERIC(5,2) | NULL        | Tampering confidence      |
| `fraud_score`        | NUMERIC(5,2) | NOT NULL    | Overall fraud score       |
| `fraud_level`        | VARCHAR(20)  | NOT NULL    | LOW/MEDIUM/HIGH/CRITICAL  |
| `indicators`         | JSONB        | NULL        | Detected fraud indicators |
| `model_name`         | VARCHAR(100) | NULL        | Fraud model               |
| `model_version`      | VARCHAR(50)  | NULL        | Model version             |
| `created_at`         | TIMESTAMP    | NOT NULL    | Detection timestamp       |

### Example `indicators`

```json
{
  "tampering": false,
  "amount_anomaly": true,
  "duplicate_pattern": false
}
```

---

# 11. `signature_results` Table

Stores signature analysis results.

| Column                | Data Type    | Constraints | Description              |
| --------------------- | ------------ | ----------- | ------------------------ |
| `signature_result_id` | UUID         | PK          | Unique result            |
| `cheque_id`           | UUID         | FK, UNIQUE  | Associated cheque        |
| `similarity_score`    | NUMERIC(5,2) | NULL        | Signature similarity     |
| `status`              | VARCHAR(20)  | NOT NULL    | MATCH/UNCERTAIN/MISMATCH |
| `model_name`          | VARCHAR(100) | NULL        | Signature model          |
| `model_version`       | VARCHAR(50)  | NULL        | Model version            |
| `created_at`          | TIMESTAMP    | NOT NULL    | Analysis timestamp       |

---

# 12. `duplicate_results` Table

Stores duplicate cheque detection results.

| Column                | Data Type    | Constraints | Description               |
| --------------------- | ------------ | ----------- | ------------------------- |
| `duplicate_result_id` | UUID         | PK          | Unique result             |
| `cheque_id`           | UUID         | FK, UNIQUE  | Current cheque            |
| `duplicate_detected`  | BOOLEAN      | NOT NULL    | Duplicate indicator       |
| `matched_cheque_id`   | UUID         | FK, NULL    | Previously matched cheque |
| `similarity_score`    | NUMERIC(5,2) | NULL        | Similarity score          |
| `comparison_method`   | VARCHAR(50)  | NULL        | Comparison method         |
| `created_at`          | TIMESTAMP    | NOT NULL    | Detection timestamp       |

### Relationship

```text
cheques 1 ───── N duplicate_results
                    │
                    └──── matched_cheque_id → cheques.cheque_id
```

The self-reference allows the system to identify the earlier cheque that caused the duplicate match.

---

# 13. `anomaly_results` Table

Stores unusual behavioral or transactional patterns.

| Column              | Data Type    | Constraints | Description           |
| ------------------- | ------------ | ----------- | --------------------- |
| `anomaly_id`        | UUID         | PK          | Unique anomaly result |
| `cheque_id`         | UUID         | FK, UNIQUE  | Associated cheque     |
| `anomaly_score`     | NUMERIC(5,2) | NOT NULL    | Anomaly score         |
| `anomaly_level`     | VARCHAR(20)  | NOT NULL    | LOW/MEDIUM/HIGH       |
| `detected_patterns` | JSONB        | NULL        | Detected patterns     |
| `model_name`        | VARCHAR(100) | NULL        | Anomaly model         |
| `model_version`     | VARCHAR(50)  | NULL        | Model version         |
| `created_at`        | TIMESTAMP    | NOT NULL    | Detection timestamp   |

---

# 14. `risk_assessments` Table

Stores the combined risk assessment generated from multiple fraud and validation signals.

| Column               | Data Type    | Constraints | Description              |
| -------------------- | ------------ | ----------- | ------------------------ |
| `risk_id`            | UUID         | PK          | Unique risk assessment   |
| `cheque_id`          | UUID         | FK          | Associated cheque        |
| `fraud_score`        | NUMERIC(5,2) | NULL        | Fraud contribution       |
| `validation_score`   | NUMERIC(5,2) | NULL        | Validation contribution  |
| `signature_score`    | NUMERIC(5,2) | NULL        | Signature contribution   |
| `duplicate_score`    | NUMERIC(5,2) | NULL        | Duplicate contribution   |
| `anomaly_score`      | NUMERIC(5,2) | NULL        | Anomaly contribution     |
| `overall_risk_score` | NUMERIC(5,2) | NOT NULL    | Combined risk score      |
| `risk_level`         | VARCHAR(20)  | NOT NULL    | LOW/MEDIUM/HIGH/CRITICAL |
| `model_version`      | VARCHAR(50)  | NULL        | Risk model version       |
| `created_at`         | TIMESTAMP    | NOT NULL    | Assessment timestamp     |

### Risk range

```text
0–24    → LOW
25–49   → MEDIUM
50–74   → HIGH
75–100  → CRITICAL
```

These thresholds are configurable and will be evaluated during testing rather than treated as universal banking rules.

---

# 15. `decisions` Table

Stores the final automated decision.

| Column            | Data Type    | Constraints | Description                     |
| ----------------- | ------------ | ----------- | ------------------------------- |
| `decision_id`     | UUID         | PK          | Unique decision                 |
| `cheque_id`       | UUID         | FK          | Associated cheque               |
| `decision`        | VARCHAR(20)  | NOT NULL    | APPROVE/REVIEW/REJECT           |
| `risk_score`      | NUMERIC(5,2) | NOT NULL    | Score used                      |
| `risk_level`      | VARCHAR(20)  | NOT NULL    | Risk classification             |
| `decision_rule`   | VARCHAR(100) | NULL        | Rule that triggered decision    |
| `reason`          | TEXT         | NOT NULL    | Explanation                     |
| `review_required` | BOOLEAN      | NOT NULL    | Whether manual review is needed |
| `engine_version`  | VARCHAR(50)  | NULL        | Decision engine version         |
| `created_at`      | TIMESTAMP    | NOT NULL    | Decision timestamp              |

---

# 16. `users` Table

Stores authorized application users.

| Column          | Data Type    | Constraints      | Description     |
| --------------- | ------------ | ---------------- | --------------- |
| `user_id`       | UUID         | PK               | Unique user     |
| `username`      | VARCHAR(100) | UNIQUE, NOT NULL | Username        |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL | User email      |
| `password_hash` | TEXT         | NOT NULL         | Hashed password |
| `role`          | VARCHAR(30)  | NOT NULL         | User role       |
| `status`        | VARCHAR(20)  | NOT NULL         | ACTIVE/INACTIVE |
| `created_at`    | TIMESTAMP    | NOT NULL         | Creation time   |
| `updated_at`    | TIMESTAMP    | NOT NULL         | Last update     |

### Supported roles

```text
ADMIN
REVIEWER
SUPERVISOR
ANALYST
```

---

# 17. `manual_review_cases` Table

Stores cheques requiring human intervention.

| Column                 | Data Type   | Constraints | Description              |
| ---------------------- | ----------- | ----------- | ------------------------ |
| `review_case_id`       | UUID        | PK          | Unique case              |
| `cheque_id`            | UUID        | FK          | Associated cheque        |
| `priority`             | VARCHAR(20) | NOT NULL    | LOW/MEDIUM/HIGH/CRITICAL |
| `trigger_reason`       | TEXT        | NOT NULL    | Why review was triggered |
| `status`               | VARCHAR(30) | NOT NULL    | Current review status    |
| `assigned_reviewer_id` | UUID        | FK, NULL    | Assigned reviewer        |
| `reviewer_decision`    | VARCHAR(20) | NULL        | APPROVE/REJECT           |
| `reviewer_comment`     | TEXT        | NULL        | Reviewer's comments      |
| `created_at`           | TIMESTAMP   | NOT NULL    | Case creation            |
| `assigned_at`          | TIMESTAMP   | NULL        | Assignment time          |
| `reviewed_at`          | TIMESTAMP   | NULL        | Review completion        |
| `closed_at`            | TIMESTAMP   | NULL        | Case closure             |

### Review statuses

```text
QUEUED
ASSIGNED
UNDER_REVIEW
APPROVED
REJECTED
CLOSED
```

---

# 18. `audit_logs` Table

Stores the complete audit history of the system. This table's canonical schema is defined in `docs/27_Audit_Trail.md` §13; it is reproduced here for completeness.

| Column             | Data Type    | Constraints | Description                       |
| ------------------ | ------------ | ----------- | ---------------------------------- |
| `audit_id`         | UUID         | PK          | Unique audit event                 |
| `cheque_id`        | UUID         | NULL        | Related cheque                     |
| `event_type`       | VARCHAR(100) | NOT NULL    | Event category                     |
| `event_timestamp`  | TIMESTAMP    | NOT NULL    | Event time                         |
| `user_id`          | UUID         | NULL        | User responsible, if applicable    |
| `user_role`        | VARCHAR(50)  | NULL        | Role of the responsible user       |
| `source`           | VARCHAR(30)  | NOT NULL    | SYSTEM / USER / API                |
| `previous_status`  | VARCHAR(50)  | NULL        | Status before the action           |
| `new_status`       | VARCHAR(50)  | NULL        | Status after the action            |
| `action`           | VARCHAR(100) | NULL        | Action performed                   |
| `result`           | VARCHAR(50)  | NULL        | Result of the action               |
| `reason`           | TEXT         | NULL        | Explanation for the result         |
| `request_id`       | VARCHAR(100) | NULL        | Unique API request identifier      |
| `ip_address`       | VARCHAR(45)  | NULL        | Source IP where applicable         |
| `metadata`         | JSONB        | NULL        | Additional structured information  |

### Example events

```text
CHEQUE_UPLOADED
PREPROCESSING_COMPLETED
OCR_COMPLETED
VALIDATION_COMPLETED
FRAUD_ANALYSIS_COMPLETED
RISK_SCORE_GENERATED
DECISION_GENERATED
REVIEW_CREATED
REVIEW_ASSIGNED
REVIEW_COMPLETED
FINAL_DECISION_GENERATED
```

See `docs/27_Audit_Trail.md` §4 for the complete list of audited event types.

---

# 19. Primary Key Summary

| Table                 | Primary Key           |
| --------------------- | --------------------- |
| `customers`           | `customer_id`         |
| `bank_accounts`       | `account_id`          |
| `cheques`             | `cheque_id`           |
| `ocr_results`         | `ocr_id`              |
| `validation_results`  | `validation_id`       |
| `fraud_results`       | `fraud_result_id`     |
| `signature_results`   | `signature_result_id` |
| `duplicate_results`   | `duplicate_result_id` |
| `anomaly_results`     | `anomaly_id`          |
| `risk_assessments`    | `risk_id`             |
| `decisions`           | `decision_id`         |
| `users`               | `user_id`             |
| `manual_review_cases` | `review_case_id`      |
| `audit_logs`          | `audit_id`            |

---

# 20. Foreign Key Relationships

| Child Table           | Foreign Key            | Parent Table               |
| --------------------- | ---------------------- | -------------------------- |
| `bank_accounts`       | `customer_id`          | `customers.customer_id`    |
| `cheques`             | `account_id`           | `bank_accounts.account_id` |
| `ocr_results`         | `cheque_id`            | `cheques.cheque_id`        |
| `validation_results`  | `cheque_id`            | `cheques.cheque_id`        |
| `fraud_results`       | `cheque_id`            | `cheques.cheque_id`        |
| `signature_results`   | `cheque_id`            | `cheques.cheque_id`        |
| `duplicate_results`   | `cheque_id`            | `cheques.cheque_id`        |
| `duplicate_results`   | `matched_cheque_id`    | `cheques.cheque_id`        |
| `anomaly_results`     | `cheque_id`            | `cheques.cheque_id`        |
| `risk_assessments`    | `cheque_id`            | `cheques.cheque_id`        |
| `decisions`           | `cheque_id`            | `cheques.cheque_id`        |
| `manual_review_cases` | `cheque_id`            | `cheques.cheque_id`        |
| `manual_review_cases` | `assigned_reviewer_id` | `users.user_id`            |
| `audit_logs`          | `cheque_id`            | `cheques.cheque_id`        |
| `audit_logs`          | `user_id`              | `users.user_id`            |

---

# 21. Important Constraints

The following constraints should be implemented:

### Risk score

```text
overall_risk_score >= 0
AND
overall_risk_score <= 100
```

### Fraud score

```text
fraud_score >= 0
AND
fraud_score <= 100
```

### OCR confidence

```text
confidence_score >= 0
AND
confidence_score <= 100
```

### Signature similarity

```text
similarity_score >= 0
AND
similarity_score <= 100
```

### Decision

```text
APPROVE
REVIEW
REJECT
```

Only these values should be accepted by the database for automated decisions.

---

# 22. Indexes

The following indexes are recommended:

```text
idx_cheques_account_id
idx_cheques_cheque_number
idx_cheques_processing_status
idx_cheques_uploaded_at

idx_fraud_results_fraud_level
idx_fraud_results_fraud_score

idx_risk_assessments_risk_level
idx_risk_assessments_overall_score

idx_decisions_decision

idx_review_cases_status
idx_review_cases_priority
idx_review_cases_reviewer

idx_audit_logs_cheque_id
idx_audit_logs_event_timestamp
```

These indexes improve performance for frequently used operations such as:

* Searching a cheque.
* Retrieving pending review cases.
* Filtering high-risk cheques.
* Generating dashboard statistics.
* Viewing cheque history.
* Generating audit reports.

---

# 23. Example End-to-End Database Record

Consider a synthetic cheque:

```text
Cheque Number: 004521
Amount: ₹25,000
Payee: ABC Supplies
```

The database could contain:

```text
CHEQUES
   │
   └── CHK-001
         │
         ├── OCR_RESULT
         │      Confidence: 97.2%
         │
         ├── VALIDATION_RESULT
         │      Status: PASS
         │
         ├── FRAUD_RESULT
         │      Fraud Score: 12
         │
         ├── SIGNATURE_RESULT
         │      Status: MATCH
         │
         ├── DUPLICATE_RESULT
         │      Duplicate: FALSE
         │
         ├── ANOMALY_RESULT
         │      Score: 10
         │
         ├── RISK_ASSESSMENT
         │      Risk Score: 15
         │      Risk Level: LOW
         │
         └── DECISION
                Decision: APPROVE
```

The corresponding audit events would record the processing stages.

---

# 24. Sample SQL Table Definition

The following is an example of how the central `cheques` table can be implemented in PostgreSQL:

```sql
CREATE TABLE cheques (
    cheque_id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    cheque_number VARCHAR(30) NOT NULL,
    cheque_series VARCHAR(30),
    routing_transit_number VARCHAR(20),
    payee_name VARCHAR(255),
    amount NUMERIC(15,2),
    cheque_date DATE,
    image_path TEXT NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    processing_status VARCHAR(30) NOT NULL DEFAULT 'UPLOADED',
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cheque_account
        FOREIGN KEY (account_id)
        REFERENCES bank_accounts(account_id),

    CONSTRAINT chk_cheque_amount
        CHECK (amount IS NULL OR amount >= 0)
);
```

This is a **schema implementation example**. The complete SQL schema will be developed in the backend implementation phase.

---

# 25. Normalization

The schema follows relational normalization principles.

For example, customer information is not repeatedly stored inside every cheque record.

Instead:

```text
CUSTOMER
   ↓
BANK_ACCOUNT
   ↓
CHEQUE
```

Similarly, OCR, fraud, validation, signature, and anomaly results are stored in dedicated tables.

This reduces:

* Data duplication.
* Update anomalies.
* Inconsistent records.
* Unnecessary storage.

It also makes individual processing results easier to retrieve and audit.

---

# 26. Data Lifecycle

The database follows this lifecycle:

```text
UPLOAD
   ↓
CHEQUE RECORD CREATED
   ↓
OCR RESULT STORED
   ↓
VALIDATION RESULT STORED
   ↓
FRAUD ANALYSIS STORED
   ↓
RISK ASSESSMENT STORED
   ↓
DECISION STORED
   ↓
┌───────────┬────────────┬───────────┐
│  APPROVE  │   REVIEW   │  REJECT   │
└───────────┴──────┬─────┴───────────┘
                   │
                   ▼
            MANUAL REVIEW
                   │
                   ▼
             FINAL DECISION
                   │
                   ▼
             AUDIT EVENT
```

Every major processing stage creates a persistent record, allowing the system to reconstruct the history of a cheque.

---

# 27. Data Integrity and Traceability

The schema ensures that every final decision can be traced back to the information used to make it.

For example:

```text
Decision
   ↓
Risk Assessment
   ↓
Fraud Result
   ↓
Validation Result
   ↓
OCR Result
   ↓
Cheque
   ↓
Bank Account
   ↓
Customer
```

This traceability is important because the project requires a **complete audit trail for every validation decision**.

---

# 28. Database Schema Summary

The final schema provides a structured data foundation for the complete cheque-processing system.

```text
                    CUSTOMERS
                        │
                        ▼
                  BANK_ACCOUNTS
                        │
                        ▼
                     CHEQUES
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
       ▼                ▼                 ▼
      OCR          VALIDATION           FRAUD
       │                │                 │
       └────────────────┼─────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
         SIGNATURE             DUPLICATE
              │                   │
              └─────────┬─────────┘
                        ▼
                    ANOMALY
                        │
                        ▼
                 RISK_ASSESSMENT
                        │
                        ▼
                    DECISION
                    /      \
               APPROVE     REVIEW
                            │
                            ▼
                     MANUAL_REVIEW
                            │
                            ▼
                          USER

All major activities
        │
        ▼
   AUDIT_LOGS
```

This schema is designed specifically for the **Mass-Mutual_Project** MVP and provides the database foundation required for OCR extraction, validation, fraud detection, risk scoring, automated decision-making, manual review, dashboard reporting, and complete auditability.

