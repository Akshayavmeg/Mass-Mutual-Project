# Manual Review Workflow

# 23. Manual Review Workflow

## 1. Introduction

The **Manual Review Workflow** handles cheques that cannot be safely approved or rejected automatically by the Decision Engine.

A cheque is sent for manual review when the automated system detects **uncertainty, moderate/high risk, conflicting validation results, insufficient OCR confidence, or other conditions requiring human verification**.

The purpose of manual review is not to repeat the entire cheque-processing process. Instead, the reviewer receives the cheque image, extracted information, validation results, fraud indicators, risk score, and reasons for the review in one place and makes the final decision.

The workflow supports two possible reviewer outcomes:

* **Approve**
* **Reject**

Every review action must be recorded in the audit trail.

---

# 2. Objectives

The Manual Review Workflow aims to:

1. Route uncertain or suspicious cheques to authorized reviewers.
2. Provide reviewers with all relevant cheque information.
3. Clearly display the reasons that triggered manual review.
4. Allow reviewers to inspect the original cheque image.
5. Allow reviewers to verify OCR-extracted information.
6. Allow reviewers to compare validation and fraud results.
7. Allow reviewers to approve or reject the cheque.
8. Record reviewer comments and evidence.
9. Maintain a complete audit trail.
10. Reduce unnecessary manual verification by allowing automation to handle low-risk cheques.

---

# 3. Position in the System

The Manual Review Workflow is triggered by the **Decision Engine**.

```text
                    CHEQUE
                       │
                       ▼
                OCR + Extraction
                       │
                       ▼
              Validation Engine
                       │
                       ▼
              Fraud Detection
                       │
                       ▼
                Risk Scoring
                       │
                       ▼
                Decision Engine
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       APPROVE       REVIEW       REJECT
                       │
                       ▼
              Manual Review Queue
                       │
                       ▼
               Authorized Reviewer
                       │
              ┌────────┴────────┐
              ▼                 ▼
           APPROVE            REJECT
              │                 │
              └────────┬────────┘
                       ▼
                  Audit Trail
```

---

# 4. When Manual Review Is Triggered

The system should create a manual review case when one or more configured conditions are detected.

### Common triggers

* Medium or high risk score.
* Possible cheque image tampering.
* Signature verification is uncertain.
* Possible duplicate cheque.
* OCR confidence below the configured threshold.
* Payee information does not match expected records.
* Unusual transaction amount.
* Unusual transaction frequency.
* Conflicting validation results.
* Missing critical information.
* Verification service failure.
* Decision Engine explicitly returns `MANUAL_REVIEW`.

Example:

```text
Risk Score = 52
Risk Level = HIGH
Signature = UNCERTAIN
Tampering = POSSIBLE

        ↓

MANUAL_REVIEW
```

---

# 5. Manual Review Lifecycle

Each review case follows a defined lifecycle.

```text
REVIEW_CASE_CREATED
        │
        ▼
      QUEUED
        │
        ▼
     ASSIGNED
        │
        ▼
   UNDER_REVIEW
        │
    ┌───┴────┐
    ▼        ▼
 APPROVE   REJECT
    │        │
    └───┬────┘
        ▼
      CLOSED
```

If a case cannot be processed immediately:

```text
UNDER_REVIEW
      │
      ▼
ON_HOLD
      │
      ▼
UNDER_REVIEW
```

---

# 6. Manual Review Case

A **Review Case** is created for every cheque requiring human intervention.

Example:

```text
Review Case ID: REV-2026-000045
Cheque ID: CHK-2026-000153
Status: QUEUED
Priority: HIGH
Risk Score: 67
Risk Level: HIGH
Created At: 2026-08-23 13:10:22
```

The review case links the cheque to all relevant processing results.

---

# 7. Review Case Information

The reviewer should be able to see:

### Cheque Information

* Cheque number
* Account number — masked where appropriate
* Routing/transit number
* Payee
* Amount
* Date
* Bank/branch information

### Processing Information

* OCR confidence
* Validation results
* Fraud results
* Signature result
* Duplicate result
* Anomaly score
* Risk score
* Risk level
* Automated decision
* Review trigger

### Evidence

* Original cheque image
* Preprocessed cheque image
* OCR regions
* Extracted fields
* Suspicious image regions
* Signature region
* Duplicate comparison information

---

# 8. Reviewer Dashboard

The reviewer dashboard should provide a centralized view.

Example:

```text
┌──────────────────────────────────────────────┐
│              MANUAL REVIEW QUEUE             │
├──────────────────────────────────────────────┤
│ Case ID       Cheque ID       Risk   Status  │
│ REV-001       CHK-153         82     QUEUED  │
│ REV-002       CHK-154         61     QUEUED  │
│ REV-003       CHK-155         47     REVIEW  │
└──────────────────────────────────────────────┘
```

The reviewer can select a case to open the detailed review screen.

---

# 9. Review Queue Prioritization

Cases should be prioritized based on risk and configured business rules.

Example:

| Priority | Example                 |
| -------- | ----------------------- |
| CRITICAL | Strong fraud indicators |
| HIGH     | High risk score         |
| MEDIUM   | Moderate risk           |
| LOW      | Minor uncertainty       |

Example:

```text
CRITICAL
   ↓
HIGH
   ↓
MEDIUM
   ↓
LOW
```

This allows reviewers to process the most important cases first.

---

# 10. Review Case Assignment

A case can be:

* Unassigned
* Assigned to a reviewer
* Reassigned by an authorized supervisor
* Completed

Example:

```text
REV-2026-000045

Status:
ASSIGNED

Reviewer:
Reviewer-001

Assigned At:
2026-08-23 13:15:10
```

Only authorized users should be allowed to assign or reassign cases.

---

# 11. Reviewer Verification Process

The reviewer should follow a structured process.

### Step 1 — Open the Case

The reviewer selects a case from the queue.

### Step 2 — Inspect Original Image

The reviewer views the original cheque image.

### Step 3 — Verify Extracted Data

The reviewer checks:

```text
Cheque Number
Account Number
Routing/Transit Number
Payee
Amount
Date
```

against the image.

### Step 4 — Review Validation Results

The reviewer checks the automated validation results.

### Step 5 — Review Fraud Indicators

The reviewer examines:

* Tampering indicators
* Signature result
* Duplicate result
* Anomaly indicators
* Risk factors

### Step 6 — Make Decision

The reviewer selects:

```text
APPROVE
```

or

```text
REJECT
```

### Step 7 — Enter Reason

A reason/comment is required.

### Step 8 — Submit

The system records the final decision and closes the case.

---

# 12. Review Screen

A detailed review screen can be structured as:

```text
┌─────────────────────────────────────────────────────┐
│                 CHEQUE REVIEW                       │
├─────────────────────────────────────────────────────┤
│ Case ID: REV-2026-000045                            │
│ Risk Score: 67 / 100       Risk: HIGH               │
├───────────────────────┬─────────────────────────────┤
│                       │ Extracted Data              │
│                       │                             │
│   CHEQUE IMAGE        │ Cheque No: 001245           │
│                       │ Account: ******4582          │
│                       │ Payee: ABC Stores            │
│                       │ Amount: ₹25,000              │
│                       │ Date: 20/08/2026             │
│                       │                             │
├───────────────────────┴─────────────────────────────┤
│ Validation Results                                  │
│ ✓ Account Active                                    │
│ ✓ Cheque Number Valid                               │
│ ✓ Date Valid                                        │
│ ⚠ Payee Verification Uncertain                     │
├─────────────────────────────────────────────────────┤
│ Fraud Indicators                                    │
│ ⚠ Possible Tampering                                │
│ ⚠ Signature Uncertain                               │
│ ✓ No Duplicate Detected                             │
├─────────────────────────────────────────────────────┤
│ Reviewer Comments:                                  │
│ [_______________________________________________]   │
│                                                     │
│       [ APPROVE ]              [ REJECT ]           │
└─────────────────────────────────────────────────────┘
```

---

# 13. Reviewer Decision

The reviewer has two primary final outcomes.

## APPROVE

Used when the reviewer determines that the cheque is legitimate despite the automated warning.

Example:

```text
Automated Decision:
MANUAL_REVIEW

Reviewer Decision:
APPROVE

Reason:
Signature manually verified against the reference.
```

## REJECT

Used when the reviewer determines that the cheque should not be processed.

Example:

```text
Automated Decision:
MANUAL_REVIEW

Reviewer Decision:
REJECT

Reason:
Cheque image contains evidence of alteration.
```

---

# 14. Reviewer Comments

A reviewer should provide a meaningful reason for the final decision.

Example:

```text
Reviewer Comment:

"Amount field was visually verified against the
original image. Signature matches the available
reference. No duplicate was identified.
Cheque approved."
```

For rejection:

```text
Reviewer Comment:

"Signature differs significantly from the reference
and image contains suspicious alteration around the
amount field. Cheque rejected."
```

---

# 15. Mandatory Comment Rule

For traceability, the system should require a reviewer comment before completing a case.

```text
IF decision = APPROVE
AND comment is empty
        ↓
Do not submit
        ↓
Display:
"Please provide a review reason."
```

The same applies to rejection.

This prevents unexplained human decisions.

---

# 16. Reviewer Override

The reviewer may override the automated decision when permitted by system policy.

Example:

```text
Automated Decision:
REVIEW

Reviewer:
APPROVE

Reason:
"False positive. Original cheque verified manually."
```

The automated decision must **never be overwritten or deleted**.

Instead, both should be stored:

```text
Automated Decision → REVIEW
Reviewer Decision  → APPROVE
```

---

# 17. Automated vs Human Decision

The system should distinguish between:

| Decision Type | Example |
| ------------- | ------- |
| Automated     | APPROVE |
| Automated     | REVIEW  |
| Automated     | REJECT  |
| Human         | APPROVE |
| Human         | REJECT  |

This distinction is important for auditing and performance evaluation.

---

# 18. Review Statuses

The following statuses can be used:

| Status         | Description                     |
| -------------- | ------------------------------- |
| `QUEUED`       | Waiting for reviewer            |
| `ASSIGNED`     | Assigned to reviewer            |
| `UNDER_REVIEW` | Reviewer is currently examining |
| `ON_HOLD`      | Review temporarily paused       |
| `APPROVED`     | Reviewer approved               |
| `REJECTED`     | Reviewer rejected               |
| `CLOSED`       | Review process completed        |

---

# 19. Manual Review API

### Create Review Case

```http
POST /api/v1/reviews
```

Example request:

```json
{
  "cheque_id": "CHK-2026-000153",
  "risk_score": 67,
  "risk_level": "HIGH",
  "trigger": [
    "POSSIBLE_TAMPERING",
    "SIGNATURE_UNCERTAIN"
  ]
}
```

Example response:

```json
{
  "review_case_id": "REV-2026-000045",
  "cheque_id": "CHK-2026-000153",
  "status": "QUEUED",
  "priority": "HIGH"
}
```

---

# 20. Get Review Queue

```http
GET /api/v1/reviews?status=QUEUED
```

Example response:

```json
{
  "cases": [
    {
      "review_case_id": "REV-2026-000045",
      "cheque_id": "CHK-2026-000153",
      "risk_score": 67,
      "risk_level": "HIGH",
      "priority": "HIGH",
      "status": "QUEUED"
    }
  ]
}
```

---

# 21. Assign Review Case

```http
POST /api/v1/reviews/{review_case_id}/assign
```

Example:

```json
{
  "reviewer_id": "REV-001"
}
```

Response:

```json
{
  "review_case_id": "REV-2026-000045",
  "reviewer_id": "REV-001",
  "status": "ASSIGNED"
}
```

---

# 22. Submit Review Decision

```http
POST /api/v1/reviews/{review_case_id}/decision
```

Example:

```json
{
  "decision": "APPROVE",
  "comment": "Signature manually verified and cheque details confirmed."
}
```

Response:

```json
{
  "review_case_id": "REV-2026-000045",
  "decision": "APPROVE",
  "status": "CLOSED"
}
```

---

# 23. Database Design

A `manual_review_cases` table can be used.

| Field                  | Description            |
| ---------------------- | ---------------------- |
| `review_case_id`       | Unique review case     |
| `cheque_id`            | Associated cheque      |
| `risk_score`           | Automated risk score   |
| `risk_level`           | Risk classification    |
| `trigger_reason`       | Reason for review      |
| `priority`             | Review priority        |
| `status`               | Current case status    |
| `assigned_reviewer_id` | Assigned reviewer      |
| `reviewer_decision`    | APPROVE/REJECT         |
| `reviewer_comment`     | Review explanation     |
| `created_at`           | Case creation time     |
| `assigned_at`          | Assignment timestamp   |
| `reviewed_at`          | Review completion time |
| `closed_at`            | Case closure time      |

---

# 24. Review History

The system should preserve the complete history of a case.

Example:

```text
13:10:22
Case Created

13:12:05
Assigned to Reviewer-001

13:15:30
Reviewer Opened Case

13:18:45
Reviewer Added Comment

13:19:10
Reviewer Approved

13:19:11
Case Closed
```

This provides a complete timeline for auditing.

---

# 25. Security and Access Control

Only authorized users should be able to perform manual reviews.

Suggested roles:

### Reviewer

Can:

* View assigned cases.
* Inspect cheque information.
* Approve cases.
* Reject cases.
* Add comments.

### Senior Reviewer / Supervisor

Can additionally:

* View all cases.
* Assign/reassign cases.
* Review escalated cases.
* Override certain decisions according to policy.

### Administrator

Can:

* Configure workflow.
* Manage users and roles.
* Configure rules.
* View audit logs.

---

# 26. Data Privacy

Cheque information may contain sensitive financial information.

Therefore:

* Account numbers should be masked where possible.
* Access should be role-based.
* Images should be securely stored.
* Sensitive information should not be unnecessarily displayed.
* API responses should expose only required fields.
* Review actions should be logged.
* Test datasets should use synthetic or appropriately anonymized information.

For this project, **synthetic banking data should be preferred for development and demonstration**.

---

# 27. Handling Review Queue Overload

If many cases enter manual review, the dashboard should show:

```text
Total Pending Reviews: 25
Critical: 3
High: 8
Medium: 14
```

The system can prioritize:

```text
CRITICAL → HIGH → MEDIUM → LOW
```

This helps ensure that the most suspicious cases are handled first.

---

# 28. Review Performance Metrics

The dashboard can track:

* Number of cases received.
* Number of cases reviewed.
* Pending cases.
* Average review time.
* Approval rate.
* Rejection rate.
* Escalation rate.
* Reviewer workload.
* Automated-to-manual ratio.
* False-positive rate.

Example:

```text
Total Cheques:             1,000
Automatically Approved:      720
Manual Reviews:              230
Rejected Automatically:       50

Manual Review Rate:          23%
```

These metrics can be used to evaluate the project's goal of reducing manual verification effort.

---

# 29. Manual Review Reduction

The project aims to reduce manual verification by at least **50%**.

The system achieves this by automatically processing low-risk cheques.

Example:

### Traditional Process

```text
1,000 cheques
      ↓
Manual Verification
      ↓
1,000 reviews
```

### Proposed System

```text
1,000 cheques
      ↓
Automated Validation + Fraud Detection
      │
      ├── 720 → APPROVE
      ├── 230 → MANUAL REVIEW
      └── 50  → REJECT
```

The actual reduction percentage must be measured using the project's test dataset rather than assumed.

---

# 30. Error Handling

The workflow should handle situations such as:

### Missing Cheque Image

```text
Image unavailable
     ↓
Cannot complete review
     ↓
ON_HOLD
```

### Reviewer Session Failure

The case should remain available and should not be incorrectly marked as completed.

### Service Failure

If a required verification service is unavailable:

```text
Verification unavailable
       ↓
MANUAL_REVIEW / ON_HOLD
```

depending on the configured policy.

---

# 31. Testing Strategy

The Manual Review Workflow should be tested with different scenarios.

### Test Case 1 — Normal Review

```text
Case Created
→ Assigned
→ Reviewed
→ Approved
→ Closed
```

Expected: Successful completion.

### Test Case 2 — Fraudulent Cheque

```text
Case Created
→ Assigned
→ Reviewed
→ Rejected
→ Closed
```

Expected: Rejection recorded.

### Test Case 3 — Missing Comment

```text
Reviewer selects APPROVE
+
Comment = EMPTY
```

Expected:

```text
Submission blocked
```

### Test Case 4 — Unauthorized Reviewer

```text
Unauthorized user attempts decision
```

Expected:

```text
ACCESS DENIED
```

### Test Case 5 — Reviewer Override

```text
Automated Decision = REVIEW
Reviewer Decision = APPROVE
```

Expected:

```text
Both decisions retained in audit trail
```

---

# 32. Suggested Backend Structure

```text
apps/
└── backend/
    └── manual_review/
        ├── review_service.py
        ├── review_routes.py
        ├── review_models.py
        ├── review_repository.py
        ├── review_rules.py
        └── review_exceptions.py
```

### Responsibilities

| File                   | Responsibility                        |
| ---------------------- | ------------------------------------- |
| `review_service.py`    | Main review workflow                  |
| `review_routes.py`     | Review APIs                           |
| `review_models.py`     | Review data structures                |
| `review_repository.py` | Database operations                   |
| `review_rules.py`      | Review eligibility and workflow rules |
| `review_exceptions.py` | Error handling                        |

---

# 33. Integration With Dashboard

The frontend should contain a dedicated **Manual Review Queue**.

Suggested sections:

```text
Dashboard
│
├── Overview
├── Cheque Processing
├── Fraud Detection
├── Risk Analysis
├── Manual Review
│   ├── Pending
│   ├── Assigned
│   ├── In Review
│   └── Completed
├── Reports
└── Audit Trail
```

---

# 34. Example End-to-End Scenario

Consider a synthetic cheque:

```text
Cheque ID:
CHK-2026-000153

Amount:
₹25,000

Account:
******4582

Payee:
ABC Stores
```

The system produces:

```text
OCR Confidence       = 94%
Account              = ACTIVE
Cheque Number        = VALID
Payee                 = MATCH
Duplicate             = FALSE
Tampering             = POSSIBLE
Signature             = UNCERTAIN
Anomaly Score         = 72
Risk Score            = 61
Risk Level            = HIGH
```

Decision Engine:

```text
MANUAL_REVIEW
```

The system creates:

```text
Review Case:
REV-2026-000045
Priority:
HIGH
Status:
QUEUED
```

Reviewer opens the case and verifies:

* Original cheque image.
* Signature.
* Amount.
* Payee.
* Date.
* Other suspicious regions.

The reviewer determines:

```text
Signature verified.
No actual tampering.
```

Reviewer enters:

```text
"Signature manually verified against reference.
Amount and payee confirmed."
```

Final decision:

```text
APPROVE
```

The system records:

```text
Automated Decision → MANUAL_REVIEW
Human Decision     → APPROVE
Reviewer           → Reviewer-001
Timestamp          → Recorded
Reason             → Stored
```

The case then becomes:

```text
CLOSED
```

---

# 35. Complete Workflow

```text
              DECISION ENGINE
                     │
                     ▼
              MANUAL_REVIEW
                     │
                     ▼
            Create Review Case
                     │
                     ▼
              Add to Queue
                     │
                     ▼
             Assign Reviewer
                     │
                     ▼
              Reviewer Opens
                     │
                     ▼
        ┌────────────────────────┐
        │ Examine Cheque Image   │
        │ Verify OCR Data         │
        │ Check Validation        │
        │ Examine Fraud Signals  │
        │ Check Signature        │
        │ Review Risk Score      │
        └───────────┬────────────┘
                    │
                    ▼
             Reviewer Decision
                    │
              ┌─────┴─────┐
              ▼           ▼
           APPROVE       REJECT
              │           │
              └─────┬─────┘
                    ▼
             Store Comments
                    │
                    ▼
              Update Status
                    │
                    ▼
              Audit Trail
                    │
                    ▼
                  CLOSED
```

---

# 36. Summary

The **Manual Review Workflow** provides a controlled human-verification layer for cheques that cannot be safely processed automatically.

The workflow is:

```text
Automated Processing
        ↓
Decision Engine
        ↓
MANUAL_REVIEW
        ↓
Review Queue
        ↓
Authorized Reviewer
        ↓
Cheque + OCR + Validation + Fraud + Risk
        ↓
Human Verification
        ↓
APPROVE / REJECT
        ↓
Audit Trail
        ↓
Case Closed
```

The design ensures that **automation handles low-risk cheques while human reviewers focus on uncertain and suspicious cases**. Every automated decision, reviewer action, comment, override, timestamp, and final outcome is retained for traceability.

For the MVP, the workflow will operate using the project's **synthetic cheque images and mock banking records**, allowing the complete process to be demonstrated without connecting to a live core banking or payment-settlement system.

