# Testing Strategy

# 31. Testing Strategy

## 1. Introduction

The **Testing Strategy** defines how the AI-Powered Cheque Scanning, Validation & Fraud Detection System will be tested to ensure that every major component works correctly, securely, and efficiently.

The system contains multiple processing stages:

```text
Cheque Image
     ↓
Image Preprocessing
     ↓
OCR
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
Decision Engine
     ↓
Approve / Review / Reject
     ↓
Audit Trail
```

Testing must therefore cover both **individual modules** and the **complete end-to-end workflow**.

The prototype will use **synthetic cheque images and mock banking data created specifically for this project**. This allows controlled testing without exposing real financial or customer information.

---

# 2. Testing Objectives

The main objectives of testing are to:

1. Verify that every module functions according to its requirements.
2. Ensure cheque images are correctly uploaded and processed.
3. Measure OCR extraction accuracy.
4. Verify validation rules against mock banking records.
5. Test fraud-detection rules and ML models.
6. Test signature-analysis functionality.
7. Verify duplicate-cheque detection.
8. Test anomaly detection.
9. Verify risk-score calculation.
10. Ensure the Decision Engine correctly produces Approve, Review, or Reject outcomes.
11. Verify manual-review workflows.
12. Test API and database functionality.
13. Verify role-based access control.
14. Verify audit-trail completeness.
15. Test system performance against the **<30-second processing target**.
16. Identify errors and edge cases before demonstration/deployment.

---

# 3. Testing Principles

The project follows these testing principles:

### Correctness

The system should produce the expected output for valid inputs.

### Reliability

Repeated processing of the same input should produce consistent results where deterministic behavior is expected.

### Security

Unauthorized users should not be able to access protected functionality.

### Performance

The system should process a cheque within the targeted processing time.

### Traceability

Important system actions and decisions should be recorded in the audit trail.

### Reproducibility

Testing should use controlled sample data so that results can be reproduced.

---

# 4. Testing Levels

Testing will be performed at multiple levels.

```text
                 Testing
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Unit          Integration   System
    Testing        Testing      Testing
       │            │            │
       └────────────┼────────────┘
                    ↓
              Acceptance
                 Testing
```

The major levels are:

1. Unit Testing
2. Integration Testing
3. System Testing
4. End-to-End Testing
5. Performance Testing
6. Security Testing
7. User Acceptance Testing

---

# 5. Unit Testing

Unit testing verifies individual functions or components independently.

Examples:

* Image preprocessing function
* OCR extraction function
* Date validation function
* Account-status validation
* Payee matching
* Duplicate detection
* Risk-score calculation
* Decision rules

Example:

```text
Input:
Cheque Date = Valid

Expected:
Date Validation = PASS
```

Another example:

```text
Input:
Account Status = CLOSED

Expected:
Account Validation = FAIL
```

---

# 6. Image Preprocessing Testing

The Image Preprocessing module should be tested with different image conditions.

### Test Conditions

* Clear cheque image
* Low-resolution image
* Rotated cheque
* Cropped cheque
* Dark image
* Bright image
* Noisy image
* Blurred image
* Skewed image
* Different image formats

Example:

| Test Case | Input            | Expected Result                   |
| --------- | ---------------- | --------------------------------- |
| IMG-001   | Clear JPEG       | Successfully processed            |
| IMG-002   | Rotated cheque   | Rotation corrected                |
| IMG-003   | Noisy image      | Noise reduced                     |
| IMG-004   | Blurred image    | Processed with reduced confidence |
| IMG-005   | Unsupported file | Rejected                          |

---

# 7. OCR Testing

OCR testing verifies whether the system correctly extracts information from cheque images.

The important fields are:

* Cheque number
* Account number
* Routing/transit number
* Payee
* Amount
* Date

Example:

```text
Cheque Image
     ↓
OCR
     ↓
Expected Data
     ↓
Compare
     ↓
Correct / Incorrect
```

---

# 8. OCR Test Dataset

We will create our own labeled test dataset.

For example:

```text
data/
└── sample_cheques/
    ├── cheque_001.png
    ├── cheque_002.png
    ├── cheque_003.png
    ├── cheque_004.png
    └── ...
```

Corresponding expected values can be stored in a structured file:

```text
data/
└── test_data/
    └── ocr_ground_truth.csv
```

Example:

| Image          | Cheque No | Account No | Payee    | Amount | Date       |
| -------------- | --------- | ---------- | -------- | -----: | ---------- |
| cheque_001.png | 100001    | 9000012345 | Sample A |   5000 | 2026-08-01 |
| cheque_002.png | 100002    | 9000012346 | Sample B |  12500 | 2026-08-03 |

This allows us to calculate actual OCR accuracy.

---

# 9. OCR Accuracy Measurement

OCR accuracy will be measured by comparing the extracted value with the known ground-truth value.

A simple field-level accuracy formula is:

```text
OCR Accuracy =
Correctly Extracted Fields
────────────────────────── × 100
Total Expected Fields
```

For example:

```text
Total fields = 600
Correct fields = 582

Accuracy = (582 / 600) × 100
         = 97%
```

The project target is:

> **OCR extraction accuracy ≥ 95%**

The final documentation should report the **actual measured accuracy**, not a predefined value.

---

# 10. Validation Engine Testing

The Validation Engine will be tested against controlled mock banking records.

Validation checks include:

* Cheque series
* Account status
* Date window
* Payee match
* Duplicate check
* Required fields
* Amount validity

Example:

```text
Cheque Account:
9000012345

Mock Banking Record:
9000012345 → ACTIVE

Expected:
Account Validation = PASS
```

---

# 11. Validation Test Cases

| ID      | Condition             | Expected Result |
| ------- | --------------------- | --------------- |
| VAL-001 | Active account        | PASS            |
| VAL-002 | Closed account        | FAIL            |
| VAL-003 | Valid cheque series   | PASS            |
| VAL-004 | Invalid cheque series | FAIL            |
| VAL-005 | Valid date            | PASS            |
| VAL-006 | Expired cheque        | FAIL            |
| VAL-007 | Matching payee        | PASS            |
| VAL-008 | Different payee       | FAIL            |
| VAL-009 | Valid amount          | PASS            |
| VAL-010 | Missing amount        | FAIL            |

---

# 12. Fraud Detection Testing

Fraud detection will be tested using both:

1. **Rule-based test cases**
2. **Labeled fraud/non-fraud test data**

The system should identify suspicious conditions such as:

* Image tampering
* Duplicate cheque
* Signature mismatch
* Unusual amount
* Account anomaly
* Payee mismatch
* Suspicious cheque characteristics

---

# 13. Fraud Test Dataset

We will create a controlled dataset containing:

```text
Normal Cheques
Fraudulent/Suspicious Cheques
```

Example:

```text
data/
└── test_data/
    └── fraud_labels.csv
```

Example:

| Cheque ID | Actual Class |
| --------- | ------------ |
| CHK-001   | NORMAL       |
| CHK-002   | NORMAL       |
| CHK-003   | FRAUD        |
| CHK-004   | NORMAL       |
| CHK-005   | FRAUD        |

This dataset will be used to evaluate the fraud-detection system.

---

# 14. Fraud Detection Metrics

The fraud model will be evaluated using:

### Accuracy

```text
Accuracy =
(TP + TN)
──────────────
(TP + TN + FP + FN)
```

### Precision

```text
Precision =
TP
────────
TP + FP
```

### Recall

```text
Recall =
TP
────────
TP + FN
```

### F1-Score

```text
F1 =
2 × Precision × Recall
──────────────────────
Precision + Recall
```

Where:

* **TP** = True Positive
* **TN** = True Negative
* **FP** = False Positive
* **FN** = False Negative

The project target is:

> **Fraud detection accuracy ≥ 90%**

The final measured value will be reported after testing.

---

# 15. Signature Analysis Testing

Signature analysis will be tested using sample cheque signatures.

Test cases should include:

```text
Genuine Signature
Modified Signature
Different Signature
Missing Signature
Low-quality Signature
```

Example:

| Test                   | Expected Result         |
| ---------------------- | ----------------------- |
| Genuine signature      | Match                   |
| Different signature    | Mismatch                |
| Modified signature     | Suspicious              |
| Missing signature      | Review                  |
| Poor-quality signature | Low confidence / Review |

The system should not automatically reject every low-confidence signature. Such cases may be routed to manual review depending on the configured decision rules.

---

# 16. Duplicate Detection Testing

Duplicate detection verifies whether the same cheque has already been processed.

The system can compare:

* Cheque number
* Account number
* Amount
* Date
* Image hash
* Other configured identifiers

Example:

```text
First Submission
       ↓
CHK-001
       ↓
Processed
       ↓
Second Submission
       ↓
Same Cheque
       ↓
DUPLICATE DETECTED
       ↓
REVIEW / REJECT
```

---

# 17. Duplicate Test Cases

| ID      | Scenario                           | Expected Result             |
| ------- | ---------------------------------- | --------------------------- |
| DUP-001 | New cheque                         | Not duplicate               |
| DUP-002 | Exact same image                   | Duplicate                   |
| DUP-003 | Same cheque number/account         | Duplicate indicator         |
| DUP-004 | Different cheque number            | Not duplicate               |
| DUP-005 | Similar image but different cheque | Not automatically duplicate |

---

# 18. Anomaly Detection Testing

Anomaly detection will identify unusual cheque behavior.

Examples:

* Unusually high amount
* Unusual transaction pattern
* Unusual cheque frequency
* Unusual account activity
* Unusual cheque characteristics

Example:

```text
Normal Amount Range:
₹500 – ₹25,000

Observed:
₹4,50,000

Result:
AMOUNT ANOMALY
```

The thresholds should be derived from the project's mock dataset and configured rules rather than arbitrarily claiming that an amount is fraudulent.

---

# 19. Risk Scoring Testing

The Risk Scoring module combines multiple indicators.

Example:

```text
Signature mismatch       +25
Duplicate detected       +30
Payee mismatch            +20
Amount anomaly            +15
Image tampering           +30
```

The final score is constrained to the configured range:

```text
0 – 100
```

Example:

```text
Duplicate             30
Signature mismatch    25
Amount anomaly        15
                     ───
Risk Score             70
```

Expected:

```text
Risk Level = HIGH
```

The exact scoring weights will be documented in the implementation/configuration.

---

# 20. Risk-Score Test Cases

| ID      | Risk Indicators         | Expected    |
| ------- | ----------------------- | ----------- |
| RSK-001 | No indicators           | Low         |
| RSK-002 | One minor indicator     | Low/Medium  |
| RSK-003 | Multiple indicators     | Medium/High |
| RSK-004 | Strong fraud indicators | High        |
| RSK-005 | Maximum configured risk | 100         |

The actual boundaries between Low, Medium, and High should match the project's configured risk thresholds.

---

# 21. Decision Engine Testing

The Decision Engine converts validation and fraud-analysis results into one of:

```text
APPROVE
REVIEW
REJECT
```

Example:

```text
Validation: PASS
Risk Score: 15
Fraud Indicators: None

Expected:
APPROVE
```

Another:

```text
Validation: PASS
Risk Score: 78
Signature: Mismatch

Expected:
REVIEW
```

Another:

```text
Validation: FAIL
Account: CLOSED

Expected:
REJECT
```

---

# 22. Decision Test Cases

| ID      | Scenario                                   | Expected Decision                          |
| ------- | ------------------------------------------ | ------------------------------------------ |
| DEC-001 | All validations pass + low risk            | APPROVE                                    |
| DEC-002 | High risk                                  | REVIEW                                     |
| DEC-003 | Account inactive                           | REJECT                                     |
| DEC-004 | Duplicate detected                         | REVIEW/REJECT according to configured rule |
| DEC-005 | Severe validation failure                  | REJECT                                     |
| DEC-006 | Low OCR confidence                         | REVIEW                                     |
| DEC-007 | Signature mismatch                         | REVIEW                                     |
| DEC-008 | Valid cheque with no suspicious indicators | APPROVE                                    |

The final decision must follow the rules documented in the Decision Engine module.

---

# 23. Manual Review Testing

Manual-review functionality will be tested by creating controlled review cases.

Workflow:

```text
Fraud/Validation Alert
        ↓
Decision Engine
        ↓
REVIEW
        ↓
Review Queue
        ↓
Reviewer
        ↓
Investigate
        ↓
Approve / Reject / Escalate
        ↓
Audit Trail
```

Testing should verify that:

* Review cases are created correctly.
* Only authorized reviewers can access them.
* Review comments are saved.
* Reviewer decisions are recorded.
* Final decisions update cheque status.
* Audit events are generated.

---

# 24. API Testing

All backend APIs should be tested independently.

Examples:

```http
POST /api/v1/cheques/upload
GET /api/v1/cheques/{id}
POST /api/v1/cheques/{id}/process
GET /api/v1/cheques/{id}/fraud
POST /api/v1/cheques/{id}/review
POST /api/v1/cheques/{id}/decision
GET /api/v1/dashboard/summary
GET /api/v1/audit
```

Testing should verify:

* HTTP status codes
* Request validation
* Response structure
* Authentication
* Authorization
* Error handling
* Database updates

---

# 25. API Test Examples

Example:

```text
POST /api/v1/cheques/upload
```

Valid file:

```text
Expected → 201 Created
```

Unsupported file:

```text
Expected → 400 Bad Request
```

Unauthenticated request:

```text
Expected → 401 Unauthorized
```

Unauthorized role:

```text
Expected → 403 Forbidden
```

---

# 26. Database Testing

Database testing ensures that information is stored and retrieved correctly.

Test areas include:

* Cheque records
* OCR results
* Validation results
* Fraud results
* Risk scores
* Decisions
* Review cases
* Users
* Audit events

Example:

```text
Cheque Processing
       ↓
Database Insert
       ↓
Retrieve Record
       ↓
Compare With Expected Data
```

---

# 27. Audit Trail Testing

Every important action should generate an audit event.

For example:

```text
Cheque Uploaded
      ↓
OCR Completed
      ↓
Validation Completed
      ↓
Fraud Analysis Completed
      ↓
Decision Generated
      ↓
Manual Review
      ↓
Final Decision
```

Testing should verify that each required event is recorded with:

* Event ID
* Timestamp
* Actor/system
* Action
* Cheque ID
* Result
* Relevant metadata

---

# 28. Security Testing

Security testing will verify:

### Authentication

* Valid login
* Invalid login
* Disabled account login

### Authorization

* Operator accessing reviewer function
* Reviewer accessing administrator function
* Auditor attempting to modify data

### File Security

* Unsupported files
* Oversized files
* Corrupted files
* Malicious filenames

### API Security

* Missing token
* Invalid token
* Insufficient permissions

### Data Security

* Sensitive information masking
* Secrets protection
* Unauthorized database access

---

# 29. Frontend Testing

The frontend should be tested for:

* Login interface
* File upload
* Dashboard
* Cheque details
* Review queue
* Decision interface
* Reports
* Error messages
* Role-based navigation

Example:

```text
Operator Login
      ↓
Operator Dashboard ✓
      ↓
Admin Page
      ↓
Access Denied ✓
```

---

# 30. Integration Testing

Integration testing verifies that multiple modules work together.

Examples:

### OCR + Validation

```text
Image
 ↓
OCR
 ↓
Extracted Account Number
 ↓
Validation Engine
 ↓
Mock Banking Database
```

### Fraud + Risk Scoring

```text
Fraud Indicators
       ↓
Risk Scoring
       ↓
Risk Level
```

### Risk + Decision

```text
Risk Score
    ↓
Decision Engine
    ↓
APPROVE / REVIEW / REJECT
```

---

# 31. End-to-End Testing

End-to-end testing verifies the complete system.

Example:

```text
Upload Cheque
      ↓
Preprocess Image
      ↓
OCR
      ↓
Extract Data
      ↓
Validate
      ↓
Fraud Detection
      ↓
Risk Score
      ↓
Decision
      ↓
Store Result
      ↓
Audit Event
      ↓
Dashboard Update
```

The final output must match the expected result for the test scenario.

---

# 32. End-to-End Test Scenarios

### Scenario 1 — Normal Cheque

```text
Valid Image
Valid OCR
Active Account
Matching Payee
No Fraud Indicators
Low Risk

Expected:
APPROVE
```

### Scenario 2 — Suspicious Cheque

```text
Valid Image
Valid Account
Signature Mismatch
High Risk

Expected:
REVIEW
```

### Scenario 3 — Invalid Account

```text
Valid Image
Account Closed

Expected:
REJECT
```

### Scenario 4 — Duplicate Cheque

```text
Cheque Already Processed

Expected:
Duplicate Indicator
REVIEW/REJECT
```

---

# 33. Performance Testing

Performance testing determines whether the system meets the target:

> **Processing time < 30 seconds per cheque**

Testing should measure:

* Image preprocessing time
* OCR time
* Validation time
* Fraud-analysis time
* Database time
* Total processing time

Example:

| Stage               |         Time |
| ------------------- | -----------: |
| Image Preprocessing |      2.1 sec |
| OCR                 |      6.5 sec |
| Validation          |      1.2 sec |
| Fraud Detection     |      5.8 sec |
| Database            |      1.1 sec |
| Other Processing    |      1.7 sec |
| **Total**           | **18.4 sec** |

These are example values only; actual measurements will be collected during testing.

---

# 34. Load Testing

Load testing evaluates system behavior when multiple cheques are processed.

Example test:

```text
10 Cheques
    ↓
50 Cheques
    ↓
100 Cheques
    ↓
500 Cheques
```

The system should be monitored for:

* Processing time
* CPU usage
* Memory usage
* Database performance
* API response time
* Failed requests

---

# 35. Stress Testing

Stress testing pushes the system beyond its expected normal workload.

Example:

```text
Normal Load
     ↓
Increasing Requests
     ↓
High Load
     ↓
System Limit
     ↓
Observe Failure Behavior
```

The purpose is not necessarily to prevent all failures, but to ensure the system fails safely and recovers appropriately.

---

# 36. Usability Testing

The system should be easy for Operators and Reviewers to understand.

Usability testing should evaluate:

* Ease of uploading a cheque
* Clarity of OCR results
* Clarity of fraud indicators
* Ease of reviewing flagged cases
* Visibility of final decision
* Ease of generating reports
* Error-message clarity

A reviewer should be able to understand **why a cheque was flagged** without examining raw system logs.

---

# 37. Regression Testing

Whenever code is changed, previously working functionality must be tested again.

Example:

```text
Modify OCR Module
       ↓
Run OCR Tests
       ↓
Run Validation Tests
       ↓
Run Fraud Tests
       ↓
Run End-to-End Tests
```

This prevents a change in one component from breaking another component.

---

# 38. Test Data Strategy

The project will create its own controlled test data.

The dataset should contain different categories:

```text
data/
├── sample_cheques/
│   ├── normal/
│   ├── suspicious/
│   └── invalid/
│
├── mock_banking_data/
│   ├── accounts.csv
│   ├── customers.csv
│   └── cheque_records.csv
│
└── test_data/
    ├── ocr_ground_truth.csv
    ├── fraud_labels.csv
    └── expected_decisions.csv
```

This structure will allow us to evaluate the complete system systematically.

---

# 39. Test Case Documentation

Each test case should contain:

| Field            | Description            |
| ---------------- | ---------------------- |
| Test ID          | Unique test identifier |
| Module           | Module being tested    |
| Test Description | What is being tested   |
| Input            | Test input             |
| Expected Result  | Expected output        |
| Actual Result    | Observed output        |
| Status           | PASS / FAIL            |
| Remarks          | Additional information |

Example:

| Test ID | Module     | Input                 | Expected                 | Status |
| ------- | ---------- | --------------------- | ------------------------ | ------ |
| OCR-001 | OCR        | cheque_001.png        | Correct amount extracted | PASS   |
| VAL-002 | Validation | Closed account        | Validation fails         | PASS   |
| FRA-003 | Fraud      | Duplicate cheque      | Duplicate detected       | PASS   |
| DEC-001 | Decision   | Low-risk valid cheque | APPROVE                  | PASS   |

---

# 40. Defect Management

When a test fails, the defect should be recorded.

Example:

```text
Defect ID: BUG-001
Module: OCR
Severity: Medium

Description:
Amount field incorrectly extracted.

Expected:
₹12,500

Actual:
₹12500

Status:
Open
```

Defect lifecycle:

```text
Detected
   ↓
Logged
   ↓
Assigned
   ↓
Fixed
   ↓
Retested
   ↓
Closed
```

---

# 41. Test Environment

The prototype testing environment can contain:

```text
Frontend
React / Vite

Backend
Python-based API

Database
PostgreSQL or configured development database

OCR
Tesseract / selected OCR engine

ML
Python + OpenCV + ML libraries

Testing
Pytest / API testing tools

Browser
Chrome / Edge
```

The exact tools will match the final implementation documented in the Technology Stack.

---

# 42. Test Automation

Where practical, repetitive tests should be automated.

Automated tests can cover:

* Unit tests
* API tests
* Validation rules
* Fraud rules
* Database operations
* Decision logic
* Regression tests

Example:

```text
Code Change
    ↓
Automated Test Suite
    ↓
Tests Pass?
 ┌───────┴───────┐
 YES             NO
 ↓                ↓
Continue       Fix Defect
```

---

# 43. Acceptance Criteria

The system will be considered ready for demonstration when:

* Core unit tests pass.
* Integration tests pass.
* End-to-end processing works.
* OCR performance is measured.
* Fraud-detection performance is measured.
* Validation rules work correctly.
* Duplicate detection works.
* Risk scoring works.
* Decision Engine produces expected outcomes.
* Manual-review workflow works.
* Audit events are generated.
* Role-based access is enforced.
* Security tests pass.
* Dashboard displays actual processing data.
* Reports can be generated.
* Processing performance is evaluated against the **<30-second target**.

---

# 44. Target Metrics

The testing process will evaluate the project's major targets.

| Metric                               |                                          Target |
| ------------------------------------ | ----------------------------------------------: |
| OCR Extraction Accuracy              |                                       **≥ 95%** |
| Fraud Detection Accuracy             |                                       **≥ 90%** |
| Processing Time                      |                         **< 30 seconds/cheque** |
| Manual Verification Effort Reduction |                                       **≥ 50%** |
| Audit Trail                          | **100% of required decisions/actions recorded** |

These are **project targets**, not assumed results.

The final project report should contain the actual measured values obtained from our test dataset.

---

# 45. Testing Workflow

The complete testing workflow is:

```text
Create Test Data
       ↓
Prepare Test Environment
       ↓
Unit Testing
       ↓
Integration Testing
       ↓
API Testing
       ↓
Security Testing
       ↓
End-to-End Testing
       ↓
Performance Testing
       ↓
Evaluate OCR
       ↓
Evaluate Fraud Detection
       ↓
Evaluate Decision Accuracy
       ↓
Fix Defects
       ↓
Regression Testing
       ↓
Final Acceptance Testing
```

---

# 46. Final Testing Report

At the end of development, the project should produce a testing report containing:

1. Number of test cases executed.
2. Number of tests passed.
3. Number of tests failed.
4. Number of defects identified.
5. Number of defects resolved.
6. OCR accuracy.
7. Fraud detection accuracy.
8. Precision, recall, and F1-score.
9. Average processing time.
10. Maximum processing time.
11. Manual-review rate.
12. Security-test results.
13. End-to-end test results.
14. Final acceptance status.

Example:

```text
TEST SUMMARY
──────────────────────────────
Total Test Cases       120
Passed                 114
Failed                   6

OCR Accuracy           [Measured]
Fraud Accuracy         [Measured]
Avg Processing Time    [Measured]

Security Tests         PASS
API Tests              PASS
E2E Tests              PASS
```

The values will be filled in **after we actually build and test the system**.

---

# 47. Summary

The **Testing Strategy** ensures that the Mass-Mutual cheque-processing system is tested from individual functions through the complete end-to-end workflow.

Testing will cover **image preprocessing, OCR, data extraction, validation, fraud detection, signature analysis, duplicate detection, anomaly detection, risk scoring, decision processing, manual review, database operations, APIs, security, dashboard functionality, and performance**.

A major part of the project will be the creation of our **own synthetic cheque dataset, mock banking database, OCR ground-truth data, fraud labels, and expected-decision dataset**. These datasets will allow us to calculate genuine project results rather than inserting assumed accuracy values.

The final testing process will specifically verify whether the system achieves its stated targets of **at least 95% OCR extraction accuracy, at least 90% fraud-detection accuracy, less than 30 seconds processing time per cheque, at least 50% reduction in manual verification cases, and a complete audit trail for required processing decisions and actions**.
