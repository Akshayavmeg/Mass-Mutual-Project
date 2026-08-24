# Decision Engine

# 22. Decision Engine

## 1. Introduction

The **Decision Engine** is the final rule-based processing component responsible for determining the appropriate action for a cheque after OCR extraction, validation, fraud detection, signature analysis, duplicate detection, anomaly detection, and risk scoring have been completed.

It evaluates all relevant results and assigns one of three primary decisions:

* **APPROVE** – the cheque satisfies the required checks and presents low risk.
* **MANUAL REVIEW** – the cheque contains one or more warning or uncertain conditions that require human verification.
* **REJECT** – the cheque fails a critical validation or fraud rule and should not proceed automatically.

The Decision Engine is therefore the bridge between the analytical modules and the final cheque-processing workflow.

---

# 2. Objectives

The Decision Engine is designed to:

1. Combine outputs from all cheque-processing modules.
2. Apply predefined business and fraud rules consistently.
3. Use the overall risk score to support the final decision.
4. Identify conditions requiring mandatory manual review.
5. Identify conditions requiring rejection.
6. Automatically approve eligible low-risk cheques.
7. Provide an explanation for every decision.
8. Record the decision in the audit trail.
9. Reduce unnecessary manual verification.
10. Ensure that critical fraud indicators cannot be overlooked because of a low overall score.

---

# 3. Position in the System

The Decision Engine operates after risk scoring.

```text
                 CHEQUE IMAGE
                       │
                       ▼
              Image Preprocessing
                       │
                       ▼
                  OCR Engine
                       │
                       ▼
             Data Extraction
                       │
                       ▼
              Validation Engine
                       │
                       ▼
             Fraud Detection
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Signature        Duplicate         Anomaly
 Analysis         Detection         Detection
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 Risk Scoring
                       │
                       ▼
               ┌───────────────┐
               │ Decision       │
               │ Engine         │
               └───────┬───────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       APPROVE       REVIEW       REJECT
          │            │            │
          └────────────┼────────────┘
                       ▼
                 Audit Trail
                       │
                       ▼
                  Dashboard
```

---

# 4. Decision Inputs

The Decision Engine receives outputs from multiple modules.

| Input                    | Source                 |
| ------------------------ | ---------------------- |
| OCR status               | OCR Engine             |
| Extracted cheque data    | Cheque Data Extraction |
| Account status           | Validation Engine      |
| Cheque number validation | Validation Engine      |
| Date validation          | Validation Engine      |
| Payee validation         | Validation Engine      |
| Cheque series validation | Validation Engine      |
| Tampering result         | Fraud Detection        |
| Signature result         | Signature Analysis     |
| Duplicate result         | Duplicate Detection    |
| Anomaly score            | Anomaly Detection      |
| Overall risk score       | Risk Scoring           |
| Risk level               | Risk Scoring           |

---

# 5. Three Primary Decisions

## 5.1 APPROVE

The cheque can be automatically approved when:

* Required fields are successfully extracted.
* OCR confidence is acceptable.
* Account is valid and active.
* Cheque number passes validation.
* Date is within the permitted window.
* Payee validation passes.
* No duplicate is detected.
* No significant tampering is detected.
* Signature verification passes within the configured threshold.
* Risk score is within the low-risk range.
* No mandatory rejection or review rule is triggered.

Example:

```text
Risk Score       = 12
Risk Level       = LOW
Account          = ACTIVE
Duplicate        = FALSE
Tampering        = FALSE
Signature        = MATCH
Validation       = PASS

Decision         = APPROVE
```

---

# 6. MANUAL REVIEW

A cheque should be sent to manual review when the system identifies uncertainty or moderate risk but does not have sufficient evidence for automatic rejection.

Examples:

* Medium/high risk score.
* Low OCR confidence.
* Possible image tampering.
* Signature similarity below the automatic approval threshold.
* Possible duplicate.
* Payee mismatch.
* Unusual transaction amount.
* Unusual transaction pattern.
* Missing or uncertain banking information.
* Conflicting validation results.

Example:

```text
Risk Score       = 47
Risk Level       = MEDIUM
Account          = ACTIVE
Duplicate        = FALSE
Tampering        = POSSIBLE
Signature        = UNCERTAIN

Decision         = MANUAL_REVIEW
```

---

# 7. REJECT

A cheque should be rejected when a configured **critical condition** is detected.

Examples include:

* Account is invalid or closed.
* Confirmed duplicate cheque.
* Invalid cheque number.
* Expired cheque where policy requires rejection.
* Strong evidence of image manipulation.
* Confirmed fraudulent signature.
* Critical fraud indicator.
* Required information cannot be validated and policy requires rejection.

Example:

```text
Risk Score       = 91
Risk Level       = CRITICAL
Duplicate        = TRUE
Tampering        = HIGH

Decision         = REJECT
```

---

# 8. Important Principle: Hard Rules Have Priority

The Decision Engine should **not depend only on the risk score**.

For example, suppose:

```text
Risk Score = 30
Risk Level = MEDIUM
```

but:

```text
Confirmed Duplicate = TRUE
```

The cheque should not be automatically approved merely because the numerical risk score is below the rejection threshold.

Therefore, the decision hierarchy is:

```text
Critical / Hard Rules
        ↓
Mandatory REJECT or REVIEW
        ↓
Risk Score
        ↓
Normal Decision Rules
        ↓
APPROVE / REVIEW
```

This is important for preventing critical fraud indicators from being hidden by an averaged score.

---

# 9. Decision Rule Hierarchy

The initial rule hierarchy for the project is:

### Priority 1 — Critical Rejection Rules

```text
IF account_invalid
OR confirmed_duplicate
OR severe_tampering
OR confirmed_fraud
THEN REJECT
```

### Priority 2 — Mandatory Review Rules

```text
IF possible_duplicate
OR signature_uncertain
OR suspicious_tampering
OR insufficient_OCR_confidence
OR critical_data_missing
THEN MANUAL_REVIEW
```

### Priority 3 — Risk Score Rules

```text
IF risk_score <= 24
THEN APPROVE

IF risk_score >= 25 AND risk_score <= 74
THEN MANUAL_REVIEW

IF risk_score >= 75
THEN REJECT
```

These are **initial prototype thresholds**. They should be calibrated using the synthetic test dataset and evaluation results.

---

# 10. Decision Matrix

| Condition                        | Decision                                 |
| -------------------------------- | ---------------------------------------- |
| All validation passed + low risk | APPROVE                                  |
| Medium risk                      | MANUAL REVIEW                            |
| High risk                        | MANUAL REVIEW                            |
| Critical risk                    | REJECT                                   |
| Confirmed duplicate              | REJECT                                   |
| Possible duplicate               | MANUAL REVIEW                            |
| Severe tampering                 | REJECT                                   |
| Possible tampering               | MANUAL REVIEW                            |
| Strong signature mismatch        | REJECT/REVIEW according to policy        |
| Uncertain signature              | MANUAL REVIEW                            |
| Invalid account                  | REJECT                                   |
| Missing critical data            | MANUAL REVIEW/REJECT according to policy |
| OCR confidence too low           | MANUAL REVIEW                            |

---

# 11. Decision Logic

The decision process can be represented as:

```text
START
  │
  ▼
Are required fields available?
  │
 ┌┴─────────────┐
NO              YES
 │               │
 ▼               ▼
REVIEW      Are critical validation
            rules failed?
                  │
             ┌────┴────┐
            YES        NO
             │          │
             ▼          ▼
          REJECT    Critical fraud?
                         │
                    ┌────┴────┐
                   YES        NO
                    │          │
                    ▼          ▼
                 REJECT    Review conditions?
                                  │
                             ┌────┴────┐
                            YES        NO
                             │          │
                             ▼          ▼
                          REVIEW     Risk Score
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                       LOW           MEDIUM/HIGH     CRITICAL
                         │              │              │
                         ▼              ▼              ▼
                      APPROVE        REVIEW         REJECT
```

---

# 12. Example 1 — Automatic Approval

### Input

```text
Cheque Number       → VALID
Account             → ACTIVE
Date                → VALID
Payee               → MATCH
Duplicate           → FALSE
Tampering           → FALSE
Signature           → MATCH
OCR Confidence      → 98%
Risk Score          → 12
Risk Level          → LOW
```

### Decision

```text
APPROVE
```

### Reason

```text
All mandatory validation checks passed.
No significant fraud indicators detected.
Risk score is within the low-risk range.
```

---

# 13. Example 2 — Manual Review

### Input

```text
Cheque Number       → VALID
Account             → ACTIVE
Date                → VALID
Payee               → MATCH
Duplicate           → FALSE
Tampering           → POSSIBLE
Signature           → UNCERTAIN
OCR Confidence      → 82%
Risk Score          → 43
Risk Level          → MEDIUM
```

### Decision

```text
MANUAL_REVIEW
```

### Reason

```text
Possible image tampering detected.
Signature verification is inconclusive.
OCR confidence is below the preferred threshold.
```

---

# 14. Example 3 — Rejection

### Input

```text
Cheque Number       → VALID
Account             → ACTIVE
Date                → VALID
Payee               → MATCH
Duplicate           → TRUE
Tampering           → FALSE
Signature           → MATCH
Risk Score          → 35
Risk Level          → MEDIUM
```

Although the risk score is only 35, the duplicate check identifies a critical condition.

### Decision

```text
REJECT
```

### Reason

```text
Confirmed duplicate cheque detected.
Critical duplicate rule overrides the numerical risk score.
```

---

# 15. Example 4 — Invalid Account

```text
Account Status = CLOSED
```

The system should not automatically approve the cheque even if other checks pass.

```text
Decision = REJECT
```

Reason:

```text
The associated account is not active.
```

---

# 16. Decision Explanation

Every decision must include a human-readable explanation.

Example:

```text
Decision: MANUAL REVIEW

Risk Score: 58/100
Risk Level: HIGH

Reasons:
1. Signature similarity is below the approval threshold.
2. Transaction amount is unusual for the account.
3. Possible image tampering detected.
4. No confirmed duplicate detected.

Recommended Action:
Manual verification by an authorized reviewer.
```

This improves transparency and supports the audit process.

---

# 17. Decision Output

The Decision Engine should generate a structured result.

Example:

```json
{
  "cheque_id": "CHK-2026-000153",
  "decision": "MANUAL_REVIEW",
  "risk_score": 58,
  "risk_level": "HIGH",
  "decision_reasons": [
    "Signature verification uncertain",
    "Unusual transaction amount",
    "Possible image tampering"
  ],
  "requires_manual_review": true,
  "decision_rule": "HIGH_RISK_REVIEW",
  "engine_version": "decision-v1.0"
}
```

---

# 18. Decision API

### Endpoint

Per ADR-0007, `docs/26_API_Specification.md` is the canonical endpoint contract; the decision endpoint is nested under the cheque resource:

```http
POST /api/v1/cheques/{cheque_id}/decision
```

### Request

```json
{
  "cheque_id": "CHK-2026-000153",
  "validation": {
    "account_status": "ACTIVE",
    "cheque_number_valid": true,
    "date_valid": true,
    "payee_match": true
  },
  "fraud": {
    "tampering": false,
    "duplicate": false
  },
  "signature": {
    "status": "MATCH"
  },
  "ocr": {
    "confidence": 97
  },
  "risk": {
    "score": 18,
    "level": "LOW"
  }
}
```

### Response

```json
{
  "cheque_id": "CHK-2026-000153",
  "decision": "APPROVE",
  "risk_score": 18,
  "risk_level": "LOW",
  "requires_manual_review": false,
  "reasons": [
    "All mandatory validations passed",
    "No duplicate detected",
    "No significant fraud indicators detected"
  ],
  "engine_version": "decision-v1.0"
}
```

---

# 19. Decision Service Architecture

The backend can implement the Decision Engine as a dedicated service.

Suggested structure:

```text
apps/
└── backend/
    └── decision_engine/
        ├── decision_service.py
        ├── decision_rules.py
        ├── decision_models.py
        ├── decision_repository.py
        └── decision_exceptions.py
```

### Responsibilities

| File                     | Responsibility                       |
| ------------------------ | ------------------------------------ |
| `decision_service.py`    | Main decision orchestration          |
| `decision_rules.py`      | Approval/review/rejection rules      |
| `decision_models.py`     | Decision request/response structures |
| `decision_repository.py` | Store decisions                      |
| `decision_exceptions.py` | Handle decision-related errors       |

---

# 20. Decision Configuration

Decision thresholds should be configurable rather than scattered throughout the code.

Example:

```json
{
  "risk_thresholds": {
    "low_max": 24,
    "medium_max": 49,
    "high_max": 74,
    "critical_min": 75
  },
  "mandatory_review": {
    "low_ocr_confidence": true,
    "possible_duplicate": true,
    "signature_uncertain": true,
    "possible_tampering": true
  },
  "mandatory_rejection": {
    "confirmed_duplicate": true,
    "invalid_account": true,
    "severe_tampering": true
  }
}
```

---

# 21. Database Storage

The decision result should be stored in the database.

Suggested `decisions` table:

| Field             | Description                       |
| ----------------- | --------------------------------- |
| `decision_id`     | Unique decision identifier        |
| `cheque_id`       | Associated cheque                 |
| `decision`        | APPROVE / REVIEW / REJECT         |
| `risk_score`      | Final risk score                  |
| `risk_level`      | Risk classification               |
| `decision_rule`   | Rule responsible for decision     |
| `reason`          | Human-readable explanation        |
| `review_required` | Whether manual review is required |
| `engine_version`  | Decision engine version           |
| `created_at`      | Decision timestamp                |

---

# 22. Integration With Manual Review

When the decision is:

```text
MANUAL_REVIEW
```

the system should create a review task.

Example:

```text
Cheque
  ↓
Decision Engine
  ↓
MANUAL_REVIEW
  ↓
Create Review Case
  ↓
Reviewer Dashboard
  ↓
Human Decision
  ├── Approve
  └── Reject
```

The reviewer's action must also be recorded in the audit trail.

---

# 23. Manual Review Case

A review case should contain:

```text
Review Case ID
Cheque ID
Risk Score
Risk Level
Detected Issues
Cheque Image
Extracted Data
Validation Results
Fraud Results
Signature Result
Decision Explanation
Assigned Reviewer
Review Status
Reviewer Decision
Review Timestamp
```

This allows the reviewer to make an informed decision without repeating the entire verification process.

---

# 24. Audit Trail

Every automated decision should generate an audit record.

Example:

```text
Cheque ID: CHK-2026-000153
Decision: MANUAL_REVIEW
Risk Score: 58
Decision Rule: HIGH_RISK_REVIEW
Engine Version: decision-v1.0
Timestamp: 2026-08-23 12:45:32
```

If a human later changes the decision:

```text
Automated Decision:
MANUAL_REVIEW

Reviewer:
Authorized User

Final Decision:
APPROVE

Reason:
Signature manually verified.
```

Both decisions should remain available in the audit history.

---

# 25. Decision States

The system can use the following workflow states:

```text
RECEIVED
   ↓
PROCESSING
   ↓
VALIDATED
   ↓
RISK_ASSESSED
   ↓
DECISION_PENDING
   │
   ├── APPROVED
   │
   ├── MANUAL_REVIEW
   │       ↓
   │   REVIEWED
   │       ├── APPROVED
   │       └── REJECTED
   │
   └── REJECTED
```

This gives every cheque a clear lifecycle.

---

# 26. Failure Handling

The Decision Engine should not approve a cheque when a critical processing component fails silently.

For example:

```text
OCR Engine Failure
       ↓
Required cheque data unavailable
       ↓
MANUAL_REVIEW
```

Similarly:

```text
Signature Service Unavailable
       ↓
Signature cannot be verified
       ↓
MANUAL_REVIEW
```

The system should avoid treating unavailable verification as successful verification.

---

# 27. Security Requirements

The Decision Engine should:

* Allow only authorized backend services to submit decisions.
* Prevent unauthorized modification of decision rules.
* Record all automated decisions.
* Record reviewer overrides.
* Protect sensitive cheque information.
* Maintain immutable or tamper-evident audit records where feasible.
* Validate all API inputs.
* Avoid exposing unnecessary account information in API responses.
* Maintain version information for decision logic.

---

# 28. Testing Strategy

The Decision Engine should be tested with synthetic cheque records covering normal, suspicious, and fraudulent scenarios.

### Test Case 1

```text
Low Risk
No Fraud Indicators
All Validation Passed

Expected → APPROVE
```

### Test Case 2

```text
Medium Risk
Possible Tampering

Expected → MANUAL_REVIEW
```

### Test Case 3

```text
Confirmed Duplicate

Expected → REJECT
```

### Test Case 4

```text
Closed Account

Expected → REJECT
```

### Test Case 5

```text
Low OCR Confidence

Expected → MANUAL_REVIEW
```

### Test Case 6

```text
Critical Risk Score

Expected → REJECT
```

### Test Case 7

```text
Low Risk Score
BUT Confirmed Duplicate

Expected → REJECT
```

This last test is particularly important because it verifies that **hard rules override the numerical risk score**.

---

# 29. Performance Requirement

The Decision Engine should execute quickly because the overall system requirement is:

```text
Complete cheque processing time < 30 seconds
```

The Decision Engine itself should add minimal processing overhead because it primarily evaluates rules and combines previously calculated results.

Actual performance should be measured during system testing.

---

# 30. Future Enhancements

Future versions can include:

* Dynamic decision thresholds.
* ML-based decision optimization.
* Human feedback incorporated into rule tuning.
* Explainable AI decision support.
* Policy-based rules for different cheque types.
* Bank-specific validation policies.
* Risk-based reviewer assignment.
* Automated escalation for high-risk cases.
* Decision analytics.
* Model-based decision calibration.

---

# 31. Complete Decision Engine Flow

```text
                  CHEQUE
                    │
                    ▼
            Processing Results
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
    Validation    Fraud       Risk Score
      Results    Results        Result
        │           │            │
        └───────────┼────────────┘
                    ▼
            Decision Engine
                    │
                    ▼
          Check Critical Rules
                    │
          ┌─────────┴─────────┐
          │                   │
       Critical            No Critical
        Issue                 Issue
          │                   │
          ▼                   ▼
       REJECT          Check Review Rules
                              │
                     ┌────────┴────────┐
                     │                 │
                   Review            No Review
                     │                 │
                     ▼                 ▼
                  REVIEW         Evaluate Risk
                                       │
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                       LOW          MEDIUM/HIGH   CRITICAL
                         │             │             │
                         ▼             ▼             ▼
                      APPROVE        REVIEW        REJECT
                         │             │             │
                         └─────────────┼─────────────┘
                                       ▼
                                 Audit Trail
                                       │
                                       ▼
                                  Dashboard
```

---

# 32. Summary

The **Decision Engine** is the final automated decision-making component of the cheque processing system.

It combines the results of:

```text
OCR
+
Validation
+
Fraud Detection
+
Signature Analysis
+
Duplicate Detection
+
Anomaly Detection
+
Risk Scoring
```

and produces:

```text
                 ┌───────────┐
                 │  DECISION │
                 └─────┬─────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       APPROVE        REVIEW       REJECT
```

The engine uses **hard rules first**, followed by risk-score-based rules. This ensures that critical conditions such as confirmed duplicates, invalid accounts, or severe tampering cannot be incorrectly approved merely because the overall numerical risk score is low.

Every decision will include a **decision reason, risk score, triggered rule, engine version, timestamp, and audit record**, making the system explainable, traceable, and suitable for the project's prototype banking environment.

