# Audit Trail

# 27. Audit Trail

## 1. Introduction

The **Audit Trail** module maintains a complete, chronological, and tamper-evident record of every important activity performed during the cheque processing lifecycle.

For the **Mass-Mutual_Project**, every cheque must have an associated audit history showing:

* Who performed the action.
* What action was performed.
* When the action occurred.
* Which cheque was affected.
* What the system detected.
* What decision was generated.
* Whether the action was performed automatically or manually.
* What changes were made during manual review.

The audit trail is essential for **fraud investigation, accountability, compliance, debugging, dispute resolution, and system monitoring**.

---

# 2. Objectives

The main objectives of the Audit Trail module are:

1. Maintain a complete history of cheque processing activities.
2. Track every major system-generated event.
3. Track all manual reviewer actions.
4. Record validation and fraud-detection results.
5. Record the final decision and the reason behind it.
6. Provide traceability from cheque upload to final decision.
7. Prevent unauthorized modification of audit records.
8. Support fraud investigations and operational analysis.
9. Provide evidence for compliance and internal audits.
10. Ensure that no important processing event is lost.

---

# 3. Audit Trail Scope

The audit trail covers the complete cheque lifecycle:

```text
Cheque Upload
      ↓
Image Preprocessing
      ↓
OCR Processing
      ↓
Data Extraction
      ↓
Validation
      ↓
Fraud Detection
      ↓
Signature Analysis
      ↓
Duplicate Detection
      ↓
Anomaly Detection
      ↓
Risk Scoring
      ↓
Decision
      ↓
Manual Review (if required)
      ↓
Final Decision
```

Every important stage generates an audit event.

---

# 4. Events That Must Be Audited

The following events will be recorded.

| Event                          | Description                     |
| ------------------------------ | ------------------------------- |
| `CHEQUE_UPLOADED`              | Cheque image/PDF uploaded       |
| `PREPROCESSING_STARTED`        | Image preprocessing started     |
| `PREPROCESSING_COMPLETED`      | Image preprocessing completed   |
| `OCR_STARTED`                  | OCR processing started          |
| `OCR_COMPLETED`                | OCR extraction completed        |
| `OCR_FAILED`                   | OCR processing failed           |
| `VALIDATION_STARTED`           | Validation started              |
| `VALIDATION_COMPLETED`         | Validation completed            |
| `VALIDATION_FAILED`            | Validation failed               |
| `FRAUD_ANALYSIS_STARTED`       | Fraud analysis started          |
| `FRAUD_ANALYSIS_COMPLETED`     | Fraud analysis completed        |
| `SIGNATURE_ANALYSIS_COMPLETED` | Signature analysis completed    |
| `DUPLICATE_CHECK_COMPLETED`    | Duplicate detection completed   |
| `ANOMALY_ANALYSIS_COMPLETED`   | Anomaly detection completed     |
| `RISK_SCORE_GENERATED`         | Risk score calculated           |
| `DECISION_GENERATED`           | Automated decision generated    |
| `REVIEW_CREATED`               | Manual review case created      |
| `REVIEW_ASSIGNED`              | Case assigned to reviewer       |
| `REVIEW_STARTED`               | Reviewer opened case            |
| `REVIEW_UPDATED`               | Reviewer updated case           |
| `REVIEW_COMPLETED`             | Manual review completed         |
| `FINAL_DECISION_GENERATED`     | Final decision recorded         |
| `USER_LOGIN`                   | User logged into system         |
| `USER_LOGOUT`                  | User logged out                 |
| `ACCESS_DENIED`                | Unauthorized access attempted   |
| `SYSTEM_ERROR`                 | Important system error occurred |

---

# 5. Information Stored in an Audit Event

Each audit event should contain sufficient information to reconstruct what happened.

Example structure:

```text
Audit Event
│
├── Event ID
├── Cheque ID
├── Event Type
├── Event Timestamp
├── User ID
├── User Role
├── Source
├── Previous Status
├── New Status
├── Action Details
├── Result
├── Risk Information
├── IP Address
├── Request ID
└── Metadata
```

---

# 6. Audit Event Data Model

A typical audit record can contain:

| Field             | Description                       |
| ----------------- | --------------------------------- |
| `audit_id`        | Unique identifier for audit event |
| `cheque_id`       | Associated cheque                 |
| `event_type`      | Type of event                     |
| `event_timestamp` | Date and time of event            |
| `user_id`         | User who performed action         |
| `user_role`       | Role of user                      |
| `source`          | SYSTEM, USER, API, etc.           |
| `previous_status` | Status before action              |
| `new_status`      | Status after action               |
| `action`          | Action performed                  |
| `result`          | Result of action                  |
| `reason`          | Explanation for result            |
| `request_id`      | Unique API request identifier     |
| `ip_address`      | Source IP where applicable        |
| `metadata`        | Additional structured information |

---

# 7. Example Audit Record

For a successfully processed cheque:

```json
{
  "audit_id": "AUD-000001",
  "cheque_id": "CHK-2026-000001",
  "event_type": "CHEQUE_UPLOADED",
  "event_timestamp": "2026-08-20T10:15:22Z",
  "user_id": "USR-001",
  "user_role": "OPERATOR",
  "source": "USER",
  "previous_status": null,
  "new_status": "UPLOADED",
  "action": "UPLOAD_CHEQUE",
  "result": "SUCCESS",
  "reason": "Cheque image uploaded successfully.",
  "request_id": "REQ-2026-000101"
}
```

---

# 8. Complete Audit History Example

For one cheque, the audit history may look like:

```text
10:15:22  CHEQUE_UPLOADED
10:15:23  PREPROCESSING_STARTED
10:15:25  PREPROCESSING_COMPLETED
10:15:25  OCR_STARTED
10:15:29  OCR_COMPLETED
10:15:30  VALIDATION_COMPLETED
10:15:34  FRAUD_ANALYSIS_COMPLETED
10:15:36  SIGNATURE_ANALYSIS_COMPLETED
10:15:37  DUPLICATE_CHECK_COMPLETED
10:15:38  ANOMALY_ANALYSIS_COMPLETED
10:15:39  RISK_SCORE_GENERATED
10:15:40  DECISION_GENERATED
```

Example:

```text
CHEQUE ID: CHK-2026-000001

Decision: APPROVE
Risk Score: 18.4

Audit Status:
✓ Uploaded
✓ Preprocessed
✓ OCR Completed
✓ Validation Passed
✓ Fraud Analysis Passed
✓ Signature Matched
✓ Duplicate Check Passed
✓ Anomaly Check Passed
✓ Risk Score Generated
✓ Approved
```

---

# 9. Manual Review Audit Trail

Manual review requires additional auditing because a human reviewer can change the outcome.

Example:

```text
10:15:40  DECISION_GENERATED
          Decision: REVIEW

10:16:10  REVIEW_CREATED
          Reason: Signature mismatch

10:18:25  REVIEW_ASSIGNED
          Reviewer: USR-007

10:20:02  REVIEW_STARTED

10:24:15  REVIEW_UPDATED
          Comment: Signature manually verified

10:25:10  REVIEW_COMPLETED
          Decision: APPROVE

10:25:11  FINAL_DECISION_GENERATED
          Final Decision: APPROVE
```

This allows the organization to determine exactly **why an automated decision was overridden**.

---

# 10. Audit Trail for Fraud Detection

Fraud-related events should contain additional information.

Example:

```json
{
  "audit_id": "AUD-000145",
  "cheque_id": "CHK-2026-000087",
  "event_type": "FRAUD_ANALYSIS_COMPLETED",
  "event_timestamp": "2026-08-20T11:25:31Z",
  "source": "SYSTEM",
  "result": "SUSPICIOUS",
  "fraud_score": 82.5,
  "risk_level": "HIGH",
  "indicators": [
    "SIGNATURE_MISMATCH",
    "AMOUNT_ANOMALY"
  ],
  "model_version": "fraud-v1"
}
```

This is particularly useful during fraud investigations.

---

# 11. Audit Trail for Validation

Validation events should record which checks passed or failed.

Example:

```json
{
  "event_type": "VALIDATION_COMPLETED",
  "cheque_id": "CHK-2026-000092",
  "result": "FAILED",
  "checks": {
    "account_valid": true,
    "cheque_number_valid": true,
    "series_valid": true,
    "date_valid": true,
    "payee_match": false,
    "duplicate_check": true
  },
  "reason": "Payee does not match authorized banking record."
}
```

This makes the system's decision explainable.

---

# 12. Decision Audit

The final decision must always be recorded.

Example:

```json
{
  "event_type": "DECISION_GENERATED",
  "cheque_id": "CHK-2026-000100",
  "decision": "REVIEW",
  "risk_score": 67.4,
  "risk_level": "HIGH",
  "reason": [
    "Signature mismatch",
    "Unusual transaction amount"
  ]
}
```

The system must not record only:

```text
REVIEW
```

It should also record **why** the cheque was sent for review.

---

# 13. Audit Trail Database Table

A dedicated table will be maintained in PostgreSQL.

### Table: `audit_logs`

```sql
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY,
    cheque_id UUID,
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID,
    user_role VARCHAR(50),
    source VARCHAR(30) NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    action VARCHAR(100),
    result VARCHAR(50),
    reason TEXT,
    request_id VARCHAR(100),
    ip_address VARCHAR(45),
    metadata JSONB
);
```

The exact database implementation may be adjusted during development, but the logical structure should remain consistent with this design.

---

# 14. Audit Log Relationships

The relationship is:

```text
USER
 │
 │ performs action
 ▼
AUDIT_LOG
 │
 │ associated with
 ▼
CHEQUE
```

One cheque can have many audit records:

```text
CHEQUE
   │
   ├── Audit Event 1
   ├── Audit Event 2
   ├── Audit Event 3
   ├── Audit Event 4
   ├── Audit Event 5
   └── ...
```

Therefore:

```text
One Cheque → Many Audit Events
```

---

# 15. Audit Trail API

The backend will provide an API to retrieve audit history.

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/audit
```

Example:

```http
GET /api/v1/cheques/CHK-2026-000001/audit
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "total_events": 8,
  "events": [
    {
      "event_type": "CHEQUE_UPLOADED",
      "timestamp": "2026-08-20T10:15:22Z",
      "source": "USER",
      "result": "SUCCESS"
    },
    {
      "event_type": "OCR_COMPLETED",
      "timestamp": "2026-08-20T10:15:29Z",
      "source": "SYSTEM",
      "result": "SUCCESS"
    },
    {
      "event_type": "VALIDATION_COMPLETED",
      "timestamp": "2026-08-20T10:15:30Z",
      "source": "SYSTEM",
      "result": "PASS"
    },
    {
      "event_type": "DECISION_GENERATED",
      "timestamp": "2026-08-20T10:15:40Z",
      "source": "SYSTEM",
      "result": "APPROVE"
    }
  ]
}
```

---

# 16. Audit Trail in Dashboard

The dashboard should provide an **Audit History** section.

Example:

```text
┌────────────────────────────────────────────────────────────┐
│ Audit History - CHK-2026-000001                            │
├────────────┬───────────────────────┬───────────┬───────────┤
│ Time       │ Event                 │ Source    │ Result    │
├────────────┼───────────────────────┼───────────┼───────────┤
│ 10:15:22   │ Cheque Uploaded       │ User      │ Success   │
│ 10:15:29   │ OCR Completed         │ System    │ Success   │
│ 10:15:30   │ Validation Completed  │ System    │ Pass      │
│ 10:15:34   │ Fraud Analysis        │ System    │ Pass      │
│ 10:15:36   │ Signature Analysis    │ System    │ Match     │
│ 10:15:37   │ Duplicate Check       │ System    │ Pass      │
│ 10:15:39   │ Risk Score Generated  │ System    │ Low       │
│ 10:15:40   │ Decision Generated    │ System    │ Approve   │
└────────────┴───────────────────────┴───────────┴───────────┘
```

---

# 17. Audit Record Immutability

Audit records should be treated as **append-only records**.

Once an audit event has been created:

```text
CREATE  ✓
READ    ✓
UPDATE  ✗
DELETE  ✗
```

Normal application users should not be able to modify or delete historical audit events.

If a correction is required, a **new audit event** should be created instead of changing the previous record.

Example:

```text
Incorrect/old event:
REVIEW → APPROVE

New corrective event:
AUDIT_CORRECTION → Reason documented
```

This preserves the original history.

---

# 18. Audit Security

The audit system must protect audit records from unauthorized access and modification.

Security controls include:

* Role-based access control.
* Authentication before viewing audit records.
* Restricted database permissions.
* Append-only audit design.
* Encryption in transit.
* Encryption at rest where supported.
* Secure logging practices.
* No sensitive credentials in audit logs.
* Controlled access to cheque images.
* Monitoring of unauthorized access attempts.

---

# 19. Protection of Sensitive Information

The project uses cheque-related financial information, so audit records must avoid unnecessarily exposing sensitive data.

For example, instead of storing:

```text
Account Number: 123456789012
```

the system can display:

```text
Account Number: ******9012
```

where full account information is not required.

Similarly, passwords, authentication tokens, API keys, and other secrets must **never** be written into audit logs.

---

# 20. Request ID and Traceability

Each API request should have a unique `request_id`.

Example:

```text
REQ-2026-000145
```

This allows developers and investigators to trace an action across multiple backend services.

Example:

```text
Request ID: REQ-2026-000145

Upload API
     ↓
OCR Service
     ↓
Validation Service
     ↓
Fraud Service
     ↓
Decision Engine
```

All related audit records can reference the same request ID.

---

# 21. Audit Trail and Compliance

The audit trail supports the project's compliance and governance requirements by providing evidence of:

* User activity.
* Automated processing.
* Validation decisions.
* Fraud detection results.
* Manual overrides.
* Final decisions.
* System errors.
* Unauthorized access attempts.

The project will use synthetic/mock banking data for development and demonstration, but the audit architecture is designed to support enterprise governance requirements when real banking data is introduced in a controlled environment.

---

# 22. Audit Trail and Fraud Investigation

When a suspicious cheque is identified, investigators can use the audit trail to reconstruct the complete processing history.

Example:

```text
Cheque: CHK-2026-000087

          ↓
Uploaded
          ↓
OCR extracted amount = ₹85,000
          ↓
Validation passed
          ↓
Signature mismatch detected
          ↓
Amount anomaly detected
          ↓
Fraud score = 82.5
          ↓
Risk Level = HIGH
          ↓
Decision = REVIEW
          ↓
Reviewer investigated
          ↓
Final Decision = REJECT
```

This provides a complete evidence trail for the decision.

---

# 23. Audit Retention

For the prototype, audit records will be retained for the lifetime of the project dataset.

For an enterprise deployment, retention duration should be defined according to the organization's legal, regulatory, security, and data-governance requirements.

The system should support configurable retention policies without allowing ordinary users to delete audit records.

---

# 24. Audit Monitoring Metrics

The dashboard can calculate:

```text
Total audit events
Events per cheque
Failed processing events
Fraud-related events
Manual review events
Decision overrides
Unauthorized access attempts
System errors
Average processing duration
```

These metrics help administrators monitor the health and security of the cheque-processing system.

---

# 25. Audit Trail Success Criteria

The Audit Trail module will be considered successfully implemented when:

* Every processed cheque has an audit history.
* Major processing stages generate audit events.
* Manual reviewer actions are recorded.
* Automated decisions are recorded.
* Decision reasons are captured.
* Fraud indicators are traceable.
* Audit records contain timestamps.
* Audit records identify the responsible user or system component.
* Audit records cannot be modified by normal users.
* Audit history can be retrieved through the API.
* Audit history can be displayed through the dashboard.
* Sensitive credentials are never stored in logs.
* The complete processing lifecycle can be reconstructed from the audit history.

---

# 26. Example End-to-End Audit Record

```text
CHEQUE ID: CHK-2026-000001

------------------------------------------------------------
TIME        EVENT                     SOURCE       RESULT
------------------------------------------------------------
10:15:22    CHEQUE_UPLOADED           USER         SUCCESS
10:15:23    PREPROCESSING_STARTED     SYSTEM       STARTED
10:15:25    PREPROCESSING_COMPLETED   SYSTEM       SUCCESS
10:15:25    OCR_STARTED               SYSTEM       STARTED
10:15:29    OCR_COMPLETED             SYSTEM       SUCCESS
10:15:30    VALIDATION_COMPLETED      SYSTEM       PASS
10:15:34    FRAUD_ANALYSIS_COMPLETED  SYSTEM       PASS
10:15:36    SIGNATURE_ANALYSIS        SYSTEM       MATCH
10:15:37    DUPLICATE_CHECK           SYSTEM       PASS
10:15:38    ANOMALY_ANALYSIS          SYSTEM       LOW
10:15:39    RISK_SCORE_GENERATED      SYSTEM       18.4
10:15:40    DECISION_GENERATED        SYSTEM       APPROVE
------------------------------------------------------------

FINAL DECISION: APPROVE
RISK LEVEL: LOW
AUDIT STATUS: COMPLETE
```

---

# 27. Summary

The **Audit Trail module** provides complete traceability for the AI-powered cheque processing system. It records the lifecycle of every cheque from **upload through OCR, validation, fraud detection, risk scoring, decision generation, and manual review**.

The module ensures that every significant action is attributable to a user or system component and is associated with a timestamp, result, and relevant processing information.

This provides the project with **accountability, transparency, explainability, fraud-investigation capability, and a complete history of every validation decision**, satisfying the requirement for a complete audit trail for every cheque processed.

