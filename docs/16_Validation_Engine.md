# Validation Engine

# 16. Validation Engine

## 1. Introduction

The **Validation Engine** is responsible for verifying whether the structured cheque information extracted by the OCR and Data Extraction modules is consistent with the available banking records and cheque-processing rules.

It acts as a **rule-based verification layer** between data extraction and fraud detection.

The Validation Engine does **not independently declare a cheque genuine or fraudulent**. Instead, it produces a set of validation results and indicators that are later consumed by the **Fraud Detection Engine** and **Decision Engine**.

```text
┌──────────────────────────────┐
│ 15. Cheque Data Extraction   │
└──────────────┬───────────────┘
               │
               ▼
       Structured Cheque Data
               │
               ▼
┌──────────────────────────────┐
│ 16. Validation Engine        │
│                              │
│ • Cheque series              │
│ • Account status             │
│ • Date window                │
│ • Payee match                │
│ • Duplicate check            │
│ • Field consistency          │
└──────────────┬───────────────┘
               │
               ▼
        Validation Results
               │
       ┌───────┴────────┐
       ▼                ▼
Fraud Detection    Decision Engine
```

---

# 2. Objectives

The main objectives of the Validation Engine are:

1. Verify extracted cheque information against banking records.
2. Validate whether the account exists.
3. Verify whether the account is active and eligible for cheque processing.
4. Validate the cheque number and cheque series.
5. Check whether the cheque date falls within the permitted processing window.
6. Compare the extracted payee with the expected banking information where such data is available.
7. Detect duplicate cheque submissions.
8. Verify basic consistency between extracted cheque fields.
9. Generate clear validation results for every check.
10. Provide evidence for fraud scoring and final decision-making.
11. Maintain a complete record of validation results for audit purposes.
12. Support both mock banking data and future integration with actual banking systems.

---

# 3. Validation Philosophy

The Validation Engine follows a **fail-safe validation approach**.

This means:

> If the system cannot confidently verify a critical field, it should not automatically approve the cheque.

For example:

```text
Account Number
      ↓
Account found?
      │
 ┌────┴─────┐
 ▼          ▼
YES         NO
 │          │
 ▼          ▼
Continue    Validation Failure
```

A validation failure does not automatically mean fraud.

It may mean:

* OCR error
* Incorrect cheque
* Missing banking record
* Invalid cheque
* Potential fraud

The Fraud Detection and Decision Engine will consider the complete set of indicators.

---

# 4. Input

The Validation Engine receives the structured cheque record from:

```text
15_Cheque_Data_Extraction.md
```

Example:

```json
{
  "cheque_id": "CHK-2026-000001",
  "cheque_number": "000123",
  "account_number": "1002345678",
  "routing_transit_number": "123456789",
  "payee_name": "John Doe",
  "amount": 25000.00,
  "amount_in_words": "Twenty Five Thousand Only",
  "date": "2026-08-15",
  "bank_name": "Demo Bank"
}
```

---

# 5. Banking Data Source

For the project MVP, the system will use **synthetic/mock banking data**.

This is important because the project is not intended to connect directly to a real bank's core banking system.

Example project data:

```text
data/
└── mock_banking_data/
    ├── accounts.csv
    ├── cheque_records.csv
    ├── customers.csv
    └── payees.csv
```

The exact files can be created as the implementation progresses.

---

# 6. Example Mock Banking Record

An example account record may look like:

```json
{
  "account_number": "1002345678",
  "customer_id": "CUS-00001",
  "account_status": "ACTIVE",
  "account_type": "CHECKING",
  "bank_code": "DEMO001",
  "routing_transit_number": "123456789"
}
```

Example cheque record:

```json
{
  "cheque_number": "000123",
  "account_number": "1002345678",
  "status": "ISSUED",
  "payee_name": "John Doe",
  "amount_limit": 50000.00
}
```

These are **synthetic records for demonstration only**.

---

# 7. Validation Pipeline

The complete validation workflow is:

```text
             Structured Cheque Data
                       │
                       ▼
             Required Field Check
                       │
                       ▼
              Account Validation
                       │
                       ▼
           Cheque Series Validation
                       │
                       ▼
             Date Window Validation
                       │
                       ▼
               Payee Validation
                       │
                       ▼
              Duplicate Detection
                       │
                       ▼
           Cross-Field Consistency
                       │
                       ▼
              Validation Summary
                       │
                       ▼
          Fraud Detection / Decision
```

---

# 8. Validation Categories

The module will perform the following major checks:

| Validation                 | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| Required Field Validation  | Ensures essential fields exist                          |
| Account Validation         | Checks account existence/status                         |
| Cheque Series Validation   | Verifies cheque number belongs to expected series       |
| Date Validation            | Checks cheque date                                      |
| Payee Validation           | Compares payee information                              |
| Routing/Transit Validation | Checks banking identifier                               |
| Duplicate Validation       | Detects repeated cheque submission                      |
| Amount Validation          | Checks amount consistency/rules                         |
| Cross-Field Validation     | Checks relationships between fields                     |
| Record Status Validation   | Checks whether cheque is already processed/stopped/etc. |

---

# 9. Required Field Validation

Before querying banking records, the system checks whether essential information has been extracted.

Required fields may include:

```text
Cheque Number
Account Number
Amount
Date
Payee
```

Example:

```text
✓ Cheque Number
✓ Account Number
✓ Amount
✓ Date
✗ Payee
```

Result:

```json
{
  "check": "REQUIRED_FIELDS",
  "status": "FAIL",
  "missing_fields": [
    "payee_name"
  ]
}
```

This should generally result in **manual review**, not automatic rejection, because the missing value may be caused by OCR failure.

---

# 10. Account Validation

The system checks whether the extracted account number exists in the banking dataset.

```text
Extracted Account Number
          ↓
Search accounts table
          ↓
Account exists?
      ┌───┴───┐
      ▼       ▼
     YES      NO
      │       │
      ▼       ▼
 Continue   FAIL
```

Example:

```json
{
  "check": "ACCOUNT_EXISTS",
  "status": "PASS",
  "account_number": "1002345678"
}
```

If the account does not exist:

```json
{
  "check": "ACCOUNT_EXISTS",
  "status": "FAIL",
  "reason": "Account not found"
}
```

---

# 11. Account Status Validation

Finding an account is not sufficient.

The system must also check its status.

Possible statuses:

```text
ACTIVE
INACTIVE
CLOSED
BLOCKED
FROZEN
```

Example:

```text
Account = 1002345678
Status = ACTIVE
```

Result:

```json
{
  "check": "ACCOUNT_STATUS",
  "status": "PASS"
}
```

If:

```text
Account Status = CLOSED
```

then:

```json
{
  "check": "ACCOUNT_STATUS",
  "status": "FAIL",
  "reason": "Account is closed"
}
```

---

# 12. Cheque Series Validation

The cheque number should belong to the expected cheque series associated with the account.

Example:

```text
Account: 1002345678

Expected cheque series:
000100 – 000199

Extracted cheque number:
000123
```

Result:

```text
000123 ∈ [000100, 000199]
```

Therefore:

```text
PASS
```

If the extracted cheque number is:

```text
000789
```

then:

```text
FAIL
```

This can indicate:

* Invalid cheque
* Wrong account
* OCR error
* Potential tampering

The result should therefore be passed to fraud analysis rather than automatically labeling the cheque fraudulent.

---

# 13. Cheque Status Validation

The system should verify whether the cheque has a valid status in the mock banking records.

Possible statuses:

```text
ISSUED
PRESENTED
PAID
STOPPED
CANCELLED
EXPIRED
```

Example:

```text
Cheque 000123
Status = ISSUED
```

Result:

```text
PASS
```

But if:

```text
Cheque 000123
Status = STOPPED
```

the validation should fail and create a high-priority indicator.

---

# 14. Date Validation

The cheque date must be checked against configured business rules.

The system should determine whether the date is:

* Valid
* Future-dated
* Too old
* Invalidly formatted
* Outside the configured processing window

Example:

```text
Cheque Date = 15/08/2026
Processing Date = 20/08/2026
```

If the configured validity window allows the cheque:

```text
PASS
```

If the cheque is beyond the allowed window:

```text
FAIL
```

---

# 15. Future-Dated Cheque

Example:

```text
Processing Date = 20/08/2026
Cheque Date     = 30/08/2026
```

The cheque is future-dated.

Result:

```json
{
  "check": "DATE_WINDOW",
  "status": "FAIL",
  "reason": "Cheque is future-dated"
}
```

The final Decision Engine may route it to:

```text
REVIEW
```

depending on the configured business rules.

---

# 16. Expired/Stale Cheque

The system should support a configurable cheque validity period.

For example:

```text
Current processing date
        -
Cheque date
        =
Cheque age
```

If:

```text
Cheque age > configured validity period
```

then:

```text
DATE_WINDOW = FAIL
```

The exact validity period should be stored in configuration rather than hard-coded into the application.

---

# 17. Payee Validation

The system compares the extracted payee with the expected payee information when such information exists in the mock banking records.

Example:

```text
Extracted Payee:
John Doe

Banking Record:
John Doe

        ↓

MATCH
```

Result:

```json
{
  "check": "PAYEE_MATCH",
  "status": "PASS"
}
```

---

# 18. Payee Mismatch

Example:

```text
Extracted:
John Doe

Banking Record:
Jane Doe
```

Result:

```json
{
  "check": "PAYEE_MATCH",
  "status": "FAIL",
  "reason": "Payee does not match banking record"
}
```

This becomes an input to fraud analysis.

However, the system should consider whether the cheque is actually expected to support payee verification. Some cheque types may legitimately permit variations.

---

# 19. Payee Normalization

Names may contain harmless formatting differences.

Example:

```text
JOHN DOE
```

and:

```text
John Doe
```

should generally be treated as equivalent after normalization.

Possible normalization:

```text
JOHN DOE
     ↓
john doe
```

The system can remove:

* Excess whitespace
* Case differences
* Certain formatting characters

But it should not perform aggressive fuzzy matching without carefully defined rules.

---

# 20. Routing/Transit Number Validation

The extracted routing/transit number should be checked against configured banking records.

Example:

```text
Extracted:
123456789

Banking Record:
123456789

Result:
PASS
```

Mismatch:

```text
Extracted:
123456780

Banking Record:
123456789

Result:
FAIL
```

This can indicate:

* OCR error
* Invalid cheque
* Incorrect banking information
* Potential tampering

---

# 21. Amount Validation

The amount can be checked against configured business rules and available banking information.

Examples:

```text
Amount > maximum permitted amount
```

or:

```text
Amount is zero/negative
```

or:

```text
Numeric amount ≠ amount in words
```

Example:

```text
Numeric:
25000.00

Words:
Twenty Five Thousand Only

Result:
PASS
```

---

# 22. Amount-in-Words Consistency

Where both values are available:

```text
Numeric Amount
       +
Amount in Words
       ↓
Convert/interpret
       ↓
Compare
```

Example:

```text
25,000.00
Twenty Five Thousand Only
        ↓
MATCH
```

Mismatch:

```text
25,000.00
Twenty Thousand Only
        ↓
MISMATCH
```

This should generate a validation failure and potentially increase fraud risk.

---

# 23. Duplicate Validation

The Validation Engine should determine whether the same cheque has already been processed or submitted.

A candidate duplicate can be identified using combinations such as:

```text
Account Number
+
Cheque Number
+
Amount
+
Date
```

Example:

```text
Account = 1002345678
Cheque No = 000123
Amount = 25000
Date = 2026-08-15
```

The system searches previously processed cheque records.

If a matching record exists:

```text
DUPLICATE = TRUE
```

The detailed duplicate-detection design will be documented in:

```text
19_Duplicate_Detection.md
```

---

# 24. Cross-Field Validation

The engine should also check relationships between extracted fields.

Examples:

```text
Account Number ↔ Routing/Transit Number
Cheque Number ↔ Account
Cheque Status ↔ Account
Amount ↔ Amount in Words
Cheque Date ↔ Processing Date
```

Example:

```text
Account Number = 1002345678
Routing Number = 999999999

Bank Record:
Routing Number = 123456789

        ↓

CROSS-FIELD VALIDATION = FAIL
```

---

# 25. Validation Result Structure

Each validation rule should produce a structured result.

Example:

```json
{
  "check": "ACCOUNT_EXISTS",
  "status": "PASS",
  "severity": "INFO",
  "message": "Account exists in banking records"
}
```

Another example:

```json
{
  "check": "PAYEE_MATCH",
  "status": "FAIL",
  "severity": "HIGH",
  "message": "Extracted payee does not match expected record"
}
```

---

# 26. Validation Statuses

The system should use standardized statuses:

```text
PASS
FAIL
WARNING
NOT_CHECKED
NOT_APPLICABLE
```

### PASS

The validation rule was successfully satisfied.

### FAIL

The validation rule was not satisfied.

### WARNING

The system detected something unusual but not necessarily invalid.

### NOT_CHECKED

The system could not perform the check because required information was unavailable.

### NOT_APPLICABLE

The validation rule does not apply to that cheque type.

---

# 27. Severity Levels

Validation failures should have severity.

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Example:

| Validation             | Severity |
| ---------------------- | -------- |
| Account exists         | INFO     |
| Minor formatting issue | LOW      |
| Date warning           | MEDIUM   |
| Payee mismatch         | HIGH     |
| Account does not exist | HIGH     |
| Stopped cheque         | CRITICAL |

Severity values should be configurable.

---

# 28. Validation Summary

After all checks are completed, the system generates a summary.

Example:

```json
{
  "cheque_id": "CHK-2026-000001",
  "overall_validation_status": "PASS",
  "checks": {
    "required_fields": "PASS",
    "account_exists": "PASS",
    "account_status": "PASS",
    "cheque_series": "PASS",
    "cheque_status": "PASS",
    "date_window": "PASS",
    "payee_match": "PASS",
    "routing_transit": "PASS",
    "duplicate_check": "PASS",
    "amount_consistency": "PASS"
  }
}
```

---

# 29. Example: Valid Cheque

Input:

```text
Account Number: 1002345678
Cheque Number: 000123
Payee: John Doe
Amount: 25,000
Date: 15/08/2026
```

Mock banking data:

```text
Account exists: YES
Account status: ACTIVE
Cheque status: ISSUED
Cheque series: VALID
Payee: John Doe
Routing: MATCH
Duplicate: NO
```

Result:

```text
Validation = PASS
```

The cheque can proceed to fraud scoring.

---

# 30. Example: Invalid Account

Input:

```text
Account Number: 9999999999
```

Banking records:

```text
Account found: NO
```

Result:

```text
ACCOUNT_EXISTS = FAIL
```

The system should generate a strong risk indicator.

The final result may become:

```text
REVIEW / REJECT
```

depending on the Decision Engine's configured rules.

---

# 31. Example: Stopped Cheque

Input:

```text
Cheque Number = 000125
```

Banking record:

```text
Status = STOPPED
```

Result:

```text
CHEQUE_STATUS = FAIL
Severity = CRITICAL
```

This should normally prevent automatic approval.

---

# 32. Example: Payee Mismatch

Extracted:

```text
Payee = John Doe
```

Banking record:

```text
Expected Payee = Jane Doe
```

Result:

```text
PAYEE_MATCH = FAIL
Severity = HIGH
```

The Fraud Detection Engine can use this as one of its risk indicators.

---

# 33. Validation Engine and Fraud Detection

The Validation Engine produces **evidence**.

The Fraud Detection Engine interprets that evidence together with additional signals.

```text
Validation Engine
      │
      ├── Account mismatch
      ├── Cheque series failure
      ├── Payee mismatch
      ├── Date anomaly
      ├── Duplicate
      └── Amount mismatch
             │
             ▼
      Fraud Detection
             │
             ▼
        Risk Score
```

This separation is important.

The Validation Engine should not contain all fraud logic.

---

# 34. Validation and Decision Separation

The system should maintain three distinct stages:

### Stage 1 — Validation

```text
Is the extracted information consistent with known records/rules?
```

### Stage 2 — Fraud Detection

```text
Does the cheque exhibit suspicious characteristics?
```

### Stage 3 — Decision

```text
Should the cheque be Approved, Reviewed, or Rejected?
```

Architecture:

```text
Validation
    ↓
Fraud Detection
    ↓
Risk Scoring
    ↓
Decision Engine
```

---

# 35. Mock Banking Database

For the prototype, the validation engine can query PostgreSQL or a local mock database.

Example tables:

```text
customers
accounts
cheques
payees
processed_cheques
```

Example:

```text
accounts
──────────────────────────────
account_number
customer_id
account_status
bank_code
routing_number
```

```text
cheques
──────────────────────────────
cheque_number
account_number
status
payee_name
amount_limit
```

---

# 36. Validation Service Design

The validation engine should be implemented as a separate backend service/module.

Possible structure:

```text
apps/
└── backend/
    ├── validation/
    │   ├── account_validator.py
    │   ├── cheque_validator.py
    │   ├── date_validator.py
    │   ├── payee_validator.py
    │   ├── duplicate_validator.py
    │   └── validation_service.py
```

This is a proposed implementation structure; it can be adjusted when we build the actual backend.

---

# 37. Validation API

A possible API endpoint is:

```http
POST /api/v1/validation/validate
```

Request:

```json
{
  "cheque_id": "CHK-2026-000001",
  "cheque_number": "000123",
  "account_number": "1002345678",
  "routing_transit_number": "123456789",
  "payee_name": "John Doe",
  "amount": 25000.00,
  "date": "2026-08-15"
}
```

Response:

```json
{
  "cheque_id": "CHK-2026-000001",
  "validation_status": "PASS",
  "failed_checks": [],
  "warnings": []
}
```

The complete API contract will be specified in:

```text
26_API_Specification.md
```

---

# 38. Audit Trail

Every validation operation should generate an audit record.

Example:

```json
{
  "cheque_id": "CHK-2026-000001",
  "check": "ACCOUNT_STATUS",
  "result": "PASS",
  "timestamp": "2026-08-20T10:15:22Z"
}
```

The audit trail should capture:

* Cheque ID
* Validation rule
* Result
* Timestamp
* System/user context where applicable
* Reason for failure/warning
* Relevant rule/version

Detailed audit requirements will be documented in:

```text
27_Audit_Trail.md
```

---

# 39. Security Requirements

The Validation Engine must:

1. Never expose complete sensitive account information unnecessarily.
2. Use parameterized database queries.
3. Protect database credentials.
4. Validate all API input.
5. Prevent unauthorized access to banking data.
6. Maintain audit logs.
7. Avoid storing sensitive information in application logs.
8. Follow the project's data-retention and privacy requirements.

---

# 40. Performance Requirements

The Validation Engine should be designed so that validation does not become a bottleneck.

The overall project target is:

> **Processing time < 30 seconds per cheque.**

The actual validation latency should be measured during performance testing.

Example:

```text
OCR                 → measured
Data Extraction     → measured
Validation          → measured
Fraud Detection     → measured
Decision             → measured
```

The final performance values will be reported in:

```text
34_Performance_Evaluation.md
```

---

# 41. Functional Requirements

The Validation Engine shall:

1. Receive structured cheque data.
2. Validate required fields.
3. Verify account existence.
4. Verify account status.
5. Validate cheque number/series.
6. Verify cheque status.
7. Validate cheque date.
8. Check the configured date window.
9. Validate routing/transit information where applicable.
10. Compare payee information where reference data exists.
11. Check for duplicate records.
12. Validate amount-related rules.
13. Compare numeric amount and amount-in-words when available.
14. Perform cross-field consistency checks.
15. Generate individual validation results.
16. Assign severity levels.
17. Generate an overall validation summary.
18. Record validation results in the audit trail.
19. Pass validation indicators to fraud detection and decision modules.

---

# 42. Non-Functional Requirements

### Accuracy

Validation rules must be deterministic and testable.

### Reliability

A database or validation failure should not result in an incorrect automatic approval.

For example:

```text
Banking Database Unavailable
          ↓
Cannot Verify Account
          ↓
NOT_CHECKED
          ↓
Manual Review
```

The system should **fail safely**.

### Performance

Validation must support the overall `<30 seconds per cheque` target.

### Maintainability

Rules should be modular and configurable.

### Auditability

Every validation result must be traceable.

---

# 43. Testing Strategy

The Validation Engine should be tested against the synthetic banking dataset.

### Test Case 1 — Valid Account

```text
Account exists = YES
Account status = ACTIVE
Expected = PASS
```

### Test Case 2 — Unknown Account

```text
Account exists = NO
Expected = FAIL
```

### Test Case 3 — Closed Account

```text
Account status = CLOSED
Expected = FAIL
```

### Test Case 4 — Valid Cheque Series

```text
Cheque number belongs to account series
Expected = PASS
```

### Test Case 5 — Invalid Cheque Series

```text
Cheque number outside expected series
Expected = FAIL
```

### Test Case 6 — Future-Dated Cheque

```text
Cheque date > processing date
Expected = FAIL/WARNING according to configured policy
```

### Test Case 7 — Payee Match

```text
Extracted = John Doe
Expected = John Doe
Expected = PASS
```

### Test Case 8 — Payee Mismatch

```text
Extracted = John Doe
Expected = Jane Doe
Expected = FAIL
```

### Test Case 9 — Duplicate

```text
Same cheque already processed
Expected = DUPLICATE
```

### Test Case 10 — Amount Mismatch

```text
Numeric amount ≠ amount in words
Expected = FAIL
```

---

# 44. Validation Matrix

For implementation and testing, the following matrix should be maintained:

| Check              | Input              | Reference             | Result    |
| ------------------ | ------------------ | --------------------- | --------- |
| Required Fields    | Extracted fields   | Required-field rules  | PASS/FAIL |
| Account Exists     | Account number     | Accounts table        | PASS/FAIL |
| Account Status     | Account number     | Account record        | PASS/FAIL |
| Cheque Series      | Cheque number      | Account cheque series | PASS/FAIL |
| Cheque Status      | Cheque number      | Cheque records        | PASS/FAIL |
| Date Window        | Cheque date        | Processing rules      | PASS/FAIL |
| Payee Match        | Payee              | Cheque/banking record | PASS/FAIL |
| Routing/Transit    | Routing number     | Banking record        | PASS/FAIL |
| Duplicate          | Cheque identifiers | Processed records     | PASS/FAIL |
| Amount             | Amount             | Business rules        | PASS/FAIL |
| Amount Consistency | Numeric + words    | Parsed values         | PASS/FAIL |

---

# 45. Example Complete Validation Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "validation_status": "PASS",

  "checks": [
    {
      "name": "required_fields",
      "status": "PASS"
    },
    {
      "name": "account_exists",
      "status": "PASS"
    },
    {
      "name": "account_status",
      "status": "PASS"
    },
    {
      "name": "cheque_series",
      "status": "PASS"
    },
    {
      "name": "cheque_status",
      "status": "PASS"
    },
    {
      "name": "date_window",
      "status": "PASS"
    },
    {
      "name": "payee_match",
      "status": "PASS"
    },
    {
      "name": "routing_transit",
      "status": "PASS"
    },
    {
      "name": "duplicate_check",
      "status": "PASS"
    },
    {
      "name": "amount_consistency",
      "status": "PASS"
    }
  ],

  "failed_checks": [],
  "warnings": []
}
```

---

# 46. Validation Failure Example

```json
{
  "cheque_id": "CHK-2026-000002",
  "validation_status": "FAIL",

  "checks": [
    {
      "name": "account_exists",
      "status": "PASS"
    },
    {
      "name": "account_status",
      "status": "PASS"
    },
    {
      "name": "cheque_series",
      "status": "PASS"
    },
    {
      "name": "payee_match",
      "status": "FAIL",
      "severity": "HIGH",
      "reason": "Payee mismatch"
    },
    {
      "name": "duplicate_check",
      "status": "PASS"
    }
  ],

  "failed_checks": [
    "payee_match"
  ]
}
```

The cheque should then proceed to the Fraud Detection Engine for risk assessment.

---

# 47. Module Boundary

## Responsible for

```text
✓ Required field validation
✓ Account existence
✓ Account status
✓ Cheque series
✓ Cheque status
✓ Date validation
✓ Payee matching
✓ Routing/transit validation
✓ Duplicate checking
✓ Amount consistency
✓ Cross-field checks
✓ Validation status
✓ Validation severity
✓ Validation audit records
```

## Not responsible for

```text
✗ Image processing
✗ OCR
✗ Raw field extraction
✗ Signature comparison
✗ Advanced anomaly detection
✗ Fraud model
✗ Final risk score
✗ Final approval/rejection
```

Those functions belong to the respective modules.

---

# 48. End-to-End Position in the Project

```text
┌──────────────────────────────┐
│ 12 Cheque Input Module       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 13 Image Preprocessing       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 14 OCR Engine                │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 15 Cheque Data Extraction    │
└──────────────┬───────────────┘
               ↓
┌══════════════════════════════╗
║ 16 VALIDATION ENGINE         ║
║                              ║
║ Account                      ║
║ Cheque Series                ║
║ Cheque Status                ║
║ Date                         ║
║ Payee                        ║
║ Routing/Transit              ║
║ Duplicate                    ║
║ Amount                       ║
║ Cross-field consistency      ║
╚══════════════════════════════╝
               ↓
┌──────────────────────────────┐
│ 17 Fraud Detection           │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 18 Signature Analysis        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 19 Duplicate Detection       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 20 Anomaly Detection         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 21 Risk Scoring              │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ 22 Decision Engine           │
│                              │
│ APPROVE / REVIEW / REJECT    │
└──────────────────────────────┘
```

## 49. Summary

The **Validation Engine** is the project's primary **banking-record and business-rule verification layer**. It takes the structured information produced by OCR/data extraction and compares it against the project's synthetic banking records and configured validation rules.

Its output is **not simply "fraud" or "not fraud."** Instead, it produces detailed, auditable results such as:

```text
Account        → PASS
Cheque Series  → PASS
Date           → PASS
Payee          → FAIL
Duplicate      → PASS
Amount         → PASS
```

These results are then passed to the **Fraud Detection, Risk Scoring, and Decision Engine** modules, which collectively determine whether the cheque should be **Approved, sent for Manual Review, or Rejected**.

For our actual implementation, the most important design principle is **fail-safe behavior**: if a critical banking record cannot be verified because the data is missing or the banking database is unavailable, the system must **not automatically approve the cheque**. It should return an appropriate `NOT_CHECKED`/`REVIEW` state and preserve the reason in the audit trail.
