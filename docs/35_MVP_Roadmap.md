# MVP Roadmap

# MVP Roadmap

## 1. Introduction

The **Minimum Viable Product (MVP) Roadmap** defines the development phases required to build, test, demonstrate, and evaluate the **AI-Powered Cheque Scanning, Validation & Fraud Detection System**.

The MVP will focus on implementing the core cheque-processing workflow:

```text
Cheque Upload
      ↓
Image Preprocessing
      ↓
OCR Extraction
      ↓
Cheque Data Structuring
      ↓
Validation
      ↓
Fraud Detection
      ↓
Risk Scoring
      ↓
Decision
      ↓
Audit Trail
      ↓
Dashboard
```

The MVP will use **synthetic/sample cheque images and mock banking records** rather than connecting to a live banking core system.

The roadmap is designed to deliver a functional end-to-end prototype first and then progressively improve accuracy, performance, security, reporting, and deployment readiness.

---

# 2. MVP Goals

The main goals of the MVP are to:

1. Accept cheque images in supported formats.
2. Preprocess cheque images for OCR.
3. Extract important cheque information using OCR.
4. Convert extracted information into structured data.
5. Validate cheque information against mock banking records.
6. Detect common fraud indicators.
7. Calculate a risk score.
8. Generate an **Approve / Review / Reject** decision.
9. Maintain a complete audit trail.
10. Provide a dashboard for monitoring processed cheques.
11. Evaluate OCR accuracy.
12. Evaluate fraud-detection performance.
13. Measure end-to-end processing time.
14. Demonstrate the complete workflow using synthetic data.

---

# 3. MVP Scope

The MVP will include the following core capabilities:

| Capability                     | MVP Status           |
| ------------------------------ | -------------------- |
| Cheque image upload            | Required             |
| JPEG/PNG/PDF support           | Required             |
| Image preprocessing            | Required             |
| OCR extraction                 | Required             |
| Cheque data structuring        | Required             |
| Mock banking database          | Required             |
| Account validation             | Required             |
| Cheque number validation       | Required             |
| Date validation                | Required             |
| Payee validation               | Required             |
| Duplicate detection            | Required             |
| Basic fraud rules              | Required             |
| Signature analysis             | Basic implementation |
| Anomaly detection              | Basic implementation |
| Risk scoring                   | Required             |
| Approve/Review/Reject workflow | Required             |
| Manual review workflow         | Required             |
| Audit trail                    | Required             |
| Dashboard                      | Required             |
| Reporting                      | Basic implementation |
| OCR evaluation                 | Required             |
| Fraud evaluation               | Required             |
| Performance evaluation         | Required             |

---

# 4. Development Phases

The MVP will be developed in the following phases:

```text
Phase 1 → Project Foundation
Phase 2 → Dataset & Mock Banking Data
Phase 3 → Cheque Input
Phase 4 → Image Preprocessing
Phase 5 → OCR
Phase 6 → Data Extraction
Phase 7 → Validation Engine
Phase 8 → Fraud Detection
Phase 9 → Risk Scoring & Decision Engine
Phase 10 → Database & Audit Trail
Phase 11 → Dashboard
Phase 12 → Testing & Evaluation
Phase 13 → Integration & Demo
Phase 14 → Deployment Preparation
```

---

# 4.1 Milestone Mapping (0–9 Implementation Plan)

Development execution for this project is tracked using an official **Milestone 0–9 plan**, agreed as the governing sequence for implementation. Each milestone maps onto one or more of the Phases defined in Section 4 / Sections 5–29 below, so the two numbering schemes describe the same work at different granularity. This mapping is the authoritative crosswalk between the two.

| Milestone | Name | Corresponding Phase(s) |
| --- | --- | --- |
| 0 | Repository & Development Foundation | Phase 1 — Project Foundation |
| 1 | Data Foundation | Phase 2 — Synthetic Dataset & Mock Banking Data |
| 2 | Cheque Upload & Image Processing | Phase 3 — Cheque Input Module; Phase 4 — Image Preprocessing |
| 3 | OCR & Cheque Data Extraction | Phase 5 — OCR Engine; Phase 6 — Cheque Data Extraction |
| 4 | Validation Engine | Phase 7 — Validation Engine |
| 5 | Fraud Detection | Phase 8 — Fraud Detection; Phase 10 — Duplicate Detection |
| 6 | Signature Analysis, Anomaly Detection & Risk Scoring | Phase 9 — Signature Analysis; Phase 11 — Anomaly Detection; Phase 12 — Risk Scoring |
| 7 | Decision Engine & Manual Review | Phase 13 — Decision Engine; Phase 14 — Manual Review Workflow |
| 8 | Database, API & Audit Trail | Phase 15 — Database Implementation; Phase 16 — Audit Trail; Phase 19 — API Integration |
| 9 | Frontend Dashboard & Complete Integration | Phase 17 — Dashboard; Phase 18 — Reporting; Phase 24 — End-to-End Integration |

Testing and evaluation (Phase 20 — Testing, Phase 21 — OCR Evaluation, Phase 22 — Fraud Model Evaluation, Phase 23 — Performance Evaluation) are not a separate milestone; per the project's development rules, relevant tests are created and run continuously within each milestone as its functionality is built. Phase 25 — MVP Demonstration is performed as final acceptance after Milestone 9 is complete, using the deliverables from all prior milestones.

Deployment-preparation activities referenced elsewhere in this roadmap (Phase 14 in the Section 4 summary, and `37_Deployment_Architecture.md`) remain out of scope for Milestones 0–9 and are deferred to a future phase, consistent with `40_Future_Roadmap.md`.

---

# 5. Phase 1 — Project Foundation

### Objective

Set up the project structure and development environment.

### Tasks

* Create Git repository.
* Configure project folders.
* Configure `.gitignore`.
* Create README.
* Set up backend.
* Set up frontend.
* Set up configuration files.
* Define development guidelines.
* Define initial architecture.

### Deliverables

```text
Mass-Mutual-Project/
├── apps/
├── config/
├── data/
├── docs/
├── models/
├── scripts/
└── tests/
```

### Completion Criteria

The project should build/run successfully with the basic frontend and backend structure.

---

# 6. Phase 2 — Synthetic Dataset & Mock Banking Data

### Objective

Create safe test data for development and evaluation.

Because real customer banking information must not be used, the MVP will use synthetic data.

### Data to create

#### Mock Accounts

```text
Account Number
Account Holder
Account Status
Account Type
Expected Signature Reference
Transaction History
```

#### Mock Cheques

```text
Cheque Number
Account Number
Payee
Amount
Date
Status
```

#### Fraud Samples

```text
Normal Cheques
Duplicate Cheques
Tampered Cheques
Signature-Mismatch Samples
Amount-Anomaly Samples
Payee-Mismatch Samples
```

### Deliverables

```text
data/
├── mock_banking_data/
├── sample_cheques/
└── test_data/
```

### Completion Criteria

The system has enough synthetic data to demonstrate the complete processing workflow.

---

# 7. Phase 3 — Cheque Input Module

### Objective

Allow users to submit cheque images.

### Supported inputs

* JPEG
* PNG
* PDF

### Features

* File upload
* File-type validation
* File-size validation
* Image preview
* Unique processing ID
* Input error handling

Example:

```text
User
 ↓
Upload Cheque
 ↓
Input Validation
 ↓
Processing ID Generated
 ↓
Processing Pipeline
```

### Completion Criteria

A valid cheque image can be successfully uploaded and passed to the preprocessing module.

---

# 8. Phase 4 — Image Preprocessing

### Objective

Improve cheque image quality before OCR.

### Processing operations

Depending on the input image:

* Resize
* Grayscale conversion
* Noise removal
* Contrast enhancement
* Thresholding
* Deskewing
* Perspective correction
* Cropping

Example:

```text
Original Image
      ↓
Grayscale
      ↓
Noise Reduction
      ↓
Contrast Enhancement
      ↓
Thresholding
      ↓
Deskew
      ↓
OCR-Ready Image
```

### Completion Criteria

The preprocessing pipeline produces an OCR-ready image and does not significantly increase the overall processing time.

---

# 9. Phase 5 — OCR Engine

### Objective

Extract text from the processed cheque image.

The MVP can use a suitable OCR engine such as:

> **Tesseract OCR**

The architecture should allow replacement with cloud OCR services such as Google Vision or Azure AI Vision if required later.

### Fields to extract

* Cheque number
* Account number
* Routing/transit number
* Payee
* Amount
* Date

### Completion Criteria

OCR successfully returns machine-readable text from the sample cheque dataset.

---

# 10. Phase 6 — Cheque Data Extraction

### Objective

Convert raw OCR output into structured cheque information.

Example raw OCR:

```text
CHEQUE NO: 100001
PAY TO: SAMPLE CORPORATION
AMOUNT: 12500.00
DATE: 01/08/2026
ACCOUNT: 9000012345
```

Structured output:

```json
{
  "cheque_number": "100001",
  "account_number": "9000012345",
  "payee_name": "Sample Corporation",
  "amount": 12500.00,
  "date": "2026-08-01"
}
```

### Tasks

* Field identification
* Text normalization
* Date normalization
* Amount normalization
* Numeric validation
* Missing-field detection

### Completion Criteria

OCR output is converted into a consistent structured format for downstream modules.

---

# 11. Phase 7 — Validation Engine

### Objective

Validate extracted cheque information against mock banking records.

### Validation rules

The MVP should check:

#### Account Status

```text
Active → Valid
Closed → Invalid
Blocked → Invalid/Review
```

#### Cheque Number

Check whether:

* Cheque number exists
* Cheque belongs to the account
* Cheque has already been processed

#### Date

Check:

* Valid date format
* Date window
* Future date
* Expired/stale cheque according to configured rules

#### Payee

Compare extracted payee with available banking/mock records where applicable.

#### Amount

Check:

* Valid numeric value
* Positive amount
* Configured limits

### Completion Criteria

The Validation Engine produces structured validation results.

Example:

```json
{
  "account_valid": true,
  "cheque_number_valid": true,
  "date_valid": true,
  "payee_match": true,
  "duplicate": false
}
```

---

# 12. Phase 8 — Fraud Detection

### Objective

Identify suspicious characteristics.

The MVP will initially use a combination of **rule-based detection and lightweight ML/AI components where appropriate**.

### Fraud checks

* Duplicate cheque detection
* Signature mismatch
* Image tampering
* Amount anomaly
* Payee mismatch
* Unusual cheque patterns
* OCR confidence issues
* Multiple validation failures

Example:

```text
Cheque
 ↓
Fraud Rules
 ↓
Fraud Indicators
 ↓
Fraud Score
```

### Completion Criteria

The system can identify the major fraud scenarios represented in the synthetic test dataset.

---

# 13. Phase 9 — Signature Analysis

### Objective

Provide a basic mechanism for identifying potential signature mismatches.

For the MVP, signature analysis can use synthetic/reference signature samples.

Possible approach:

```text
Cheque Signature
       ↓
Signature Region Detection
       ↓
Image Processing
       ↓
Feature Extraction
       ↓
Reference Comparison
       ↓
Similarity Score
```

Example:

```text
Similarity = 0.91
```

The similarity threshold will be established through testing.

### Important MVP limitation

Signature analysis in the MVP should be treated as a **risk indicator**, not as definitive proof of fraud.

---

# 14. Phase 10 — Duplicate Detection

### Objective

Identify cheques that have already been processed.

The system can compare:

* Cheque number
* Account number
* Amount
* Date
* Transaction/reference ID
* Image/hash information where implemented

Example:

```text
New Cheque
    ↓
Generate Identifier
    ↓
Search Previous Records
    ↓
Match Found?
   ↙      ↘
 YES      NO
 ↓         ↓
Duplicate  Continue
```

### Completion Criteria

Known duplicate test samples are correctly identified.

---

# 15. Phase 11 — Anomaly Detection

### Objective

Identify unusual cheque characteristics.

Potential indicators:

* Unusually high amount
* Unusual transaction frequency
* Unusual payee
* Unusual cheque sequence
* Abnormal OCR confidence
* Multiple validation failures

Example:

```text
Historical/Mock Pattern
        ↓
Expected Range
        ↓
Current Cheque
        ↓
Deviation
        ↓
Anomaly Score
```

### Completion Criteria

The MVP can identify predefined anomaly scenarios from the synthetic dataset.

---

# 16. Phase 12 — Risk Scoring

### Objective

Combine validation and fraud indicators into a single risk score.

Example scoring model:

```text
Risk Score = 
Validation Risk
+ Fraud Risk
+ Anomaly Risk
+ Image Risk
```

The actual weights will be documented and configured rather than hidden inside application code.

Example conceptual result:

```text
0 – 30   → Low Risk
31 – 70  → Medium Risk
71 – 100 → High Risk
```

These ranges are **initial configuration examples** and should be validated during testing.

---

# 17. Phase 13 — Decision Engine

### Objective

Convert validation and fraud results into an operational decision.

The MVP will support:

```text
APPROVE
REVIEW
REJECT
```

Example:

```text
                    Processing
                         ↓
                 Validation + Fraud
                         ↓
                    Risk Score
                         ↓
              ┌──────────┼──────────┐
              ↓          ↓          ↓
           LOW RISK   MEDIUM     HIGH RISK
              ↓          ↓          ↓
           APPROVE     REVIEW      REJECT
```

The exact decision rules will be configurable.

---

# 18. Phase 14 — Manual Review Workflow

### Objective

Provide a controlled process for suspicious cheques.

A reviewer should be able to see:

* Original cheque image
* Extracted information
* Validation results
* Fraud indicators
* Risk score
* Reasons for the alert
* Audit history

The reviewer can then select an appropriate action.

Example:

```text
Flagged Cheque
      ↓
Manual Review Queue
      ↓
Reviewer
      ↓
Review Evidence
      ↓
Approve / Reject / Escalate
```

### Completion Criteria

A flagged cheque can be reviewed and the review action is recorded.

---

# 19. Phase 15 — Database Implementation

### Objective

Store all required operational data.

The MVP database should contain entities such as:

```text
Users
Accounts
Cheques
Extracted Data
Validation Results
Fraud Results
Risk Scores
Decisions
Manual Reviews
Audit Logs
```

The final schema will follow:

```text
docs/25_Database_Schema.md
```

### Completion Criteria

The complete processing history of a cheque can be retrieved from the database.

---

# 20. Phase 16 — Audit Trail

### Objective

Maintain a complete record of system actions.

Example:

```text
Cheque Uploaded
      ↓
OCR Completed
      ↓
Validation Completed
      ↓
Fraud Analysis Completed
      ↓
Risk Score Generated
      ↓
Decision Generated
      ↓
Manual Review
      ↓
Final Decision
```

Each event should record information such as:

* Timestamp
* User/system actor
* Action
* Cheque ID
* Previous status
* New status
* Reason/result

### Completion Criteria

Every processed cheque has a traceable processing history.

---

# 21. Phase 17 — Dashboard

### Objective

Provide a visual interface for monitoring the cheque-processing system.

The MVP dashboard should display:

```text
Total Cheques
Approved
Under Review
Rejected
Fraud Alerts
Average Processing Time
OCR Accuracy
Fraud Detection Metrics
```

Possible dashboard sections:

```text
┌─────────────────────────────────────────┐
│ Total Cheques │ Approved │ Review │ Reject │
├─────────────────────────────────────────┤
│ Processing Statistics                   │
├─────────────────────────────────────────┤
│ Fraud Alerts                            │
├─────────────────────────────────────────┤
│ Recent Cheque Processing                │
├─────────────────────────────────────────┤
│ Performance Metrics                     │
└─────────────────────────────────────────┘
```

---

# 22. Phase 18 — Reporting

The MVP should provide basic reports.

### Operational Reports

* Processed cheques
* Approved cheques
* Rejected cheques
* Review cases

### Fraud Reports

* Fraud alerts
* Fraud categories
* High-risk cheques
* Duplicate cases

### Performance Reports

* Average processing time
* OCR performance
* Fraud-model performance

---

# 23. Phase 19 — API Integration

The backend should expose APIs for communication between the frontend and processing services.

Example:

```text
POST /api/cheques/upload
POST /api/cheques/process
GET  /api/cheques/{id}
GET  /api/cheques/{id}/result
GET  /api/reviews
POST /api/reviews/{id}/decision
GET  /api/dashboard
GET  /api/reports
```

The final API specification will be maintained in:

```text
docs/26_API_Specification.md
```

---

# 24. Phase 20 — Testing

Testing will cover:

### Unit Testing

Individual functions and modules.

### Integration Testing

Interaction between:

```text
OCR
 ↓
Validation
 ↓
Fraud Detection
 ↓
Risk Scoring
 ↓
Decision Engine
```

### System Testing

Complete end-to-end workflow.

### Security Testing

Authentication, authorization, input validation, and data protection.

### Performance Testing

Processing time and system resource usage.

### OCR Testing

Accuracy against ground truth.

### Fraud Testing

Accuracy against labeled synthetic fraud data.

---

# 25. Phase 21 — OCR Evaluation

The OCR module will be evaluated against the project's ground-truth dataset.

Target:

> **OCR extraction accuracy ≥ 95%**

Evaluation will include:

* Field-level accuracy
* Overall extraction accuracy
* Character-level errors
* OCR confidence
* Preprocessing impact

Actual results will be entered after testing.

---

# 26. Phase 22 — Fraud Model Evaluation

The fraud-detection component will be evaluated using labeled synthetic data.

Target:

> **Fraud detection accuracy ≥ 90%**

Evaluation metrics include:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix
* ROC-AUC where applicable
* False-positive analysis
* False-negative analysis

Actual results will be measured after implementation.

---

# 27. Phase 23 — Performance Evaluation

The complete system will be tested for processing speed.

Primary target:

> **Processing time < 30 seconds per cheque**

Testing will measure:

* End-to-end processing time
* OCR time
* Validation time
* Fraud detection time
* API response time
* Throughput
* CPU utilization
* Memory utilization

---

# 28. Phase 24 — End-to-End Integration

All components will be connected.

```text
                 Frontend
                    ↓
              Backend API
                    ↓
             Input Module
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
             Risk Scoring
                    ↓
           Decision Engine
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   Audit Trail             Dashboard
```

### Completion Criteria

A complete cheque can move from upload to final decision without manual intervention unless it is intentionally routed to review.

---

# 29. Phase 25 — MVP Demonstration

The MVP demonstration should use predefined synthetic scenarios.

### Scenario 1 — Valid Cheque

```text
Upload
 ↓
OCR
 ↓
Validation Pass
 ↓
Fraud Checks Pass
 ↓
Low Risk
 ↓
APPROVE
```

### Scenario 2 — Suspicious Cheque

```text
Upload
 ↓
OCR
 ↓
Validation
 ↓
Signature Mismatch
 ↓
Medium/High Risk
 ↓
REVIEW
```

### Scenario 3 — Duplicate Cheque

```text
Upload
 ↓
OCR
 ↓
Duplicate Detected
 ↓
High Risk
 ↓
REJECT/REVIEW
```

The exact final decision depends on the configured Decision Engine rules.

---

# 30. MVP Development Priority

The development order should prioritize the core processing pipeline.

### Priority 1 — Must Have

```text
Upload
OCR
Data Extraction
Validation
Fraud Detection
Risk Scoring
Decision Engine
Database
Audit Trail
```

### Priority 2 — Important

```text
Dashboard
Manual Review
Reporting
Signature Analysis
Duplicate Detection
Anomaly Detection
```

### Priority 3 — Enhancement

```text
Advanced ML Models
Cloud OCR
Advanced Analytics
Scalable Deployment
Advanced Explainability
```

This ensures that the project has a working end-to-end system even if advanced features require additional development time.

---

# 31. MVP Completion Criteria

The MVP will be considered complete when:

* A cheque image can be uploaded.
* The image can be preprocessed.
* OCR extracts the required cheque fields.
* Extracted data is structured.
* Data is validated against mock banking records.
* Duplicate checks are performed.
* Fraud indicators are evaluated.
* A risk score is generated.
* The system produces an Approve/Review/Reject decision.
* Suspicious cases can be sent to manual review.
* Processing events are recorded in the audit trail.
* Results are stored in the database.
* Dashboard displays processing information.
* Synthetic test data is available.
* OCR evaluation can be performed.
* Fraud evaluation can be performed.
* Performance evaluation can be performed.
* The complete workflow can be demonstrated.

---

# 32. MVP Target Metrics

| Metric                     |                        Target |
| -------------------------- | ----------------------------: |
| OCR extraction accuracy    |                     **≥ 95%** |
| Fraud detection accuracy   |                     **≥ 90%** |
| Processing time            |       **< 30 seconds/cheque** |
| Manual verification effort |    **≥ 50% reduction target** |
| Audit trail                | **100% of processed cheques** |
| Supported input            |          **JPEG / PNG / PDF** |
| Final decision             | **Approve / Review / Reject** |

The values represent **project targets**. Actual performance will be reported only after testing.

---

# 33. MVP Roadmap Summary

```text
┌───────────────────────────────────────────┐
│ 1. Project Foundation                     │
├───────────────────────────────────────────┤
│ 2. Synthetic Data & Mock Banking Records  │
├───────────────────────────────────────────┤
│ 3. Cheque Input                           │
├───────────────────────────────────────────┤
│ 4. Image Preprocessing                    │
├───────────────────────────────────────────┤
│ 5. OCR Engine                             │
├───────────────────────────────────────────┤
│ 6. Data Extraction                        │
├───────────────────────────────────────────┤
│ 7. Validation Engine                      │
├───────────────────────────────────────────┤
│ 8. Fraud Detection                        │
├───────────────────────────────────────────┤
│ 9. Risk Scoring & Decision Engine         │
├───────────────────────────────────────────┤
│ 10. Database & Audit Trail                │
├───────────────────────────────────────────┤
│ 11. Manual Review                         │
├───────────────────────────────────────────┤
│ 12. Dashboard & Reporting                 │
├───────────────────────────────────────────┤
│ 13. Testing                               │
├───────────────────────────────────────────┤
│ 14. OCR/Fraud/Performance Evaluation      │
├───────────────────────────────────────────┤
│ 15. End-to-End Integration                │
├───────────────────────────────────────────┤
│ 16. MVP Demonstration & Deployment        │
└───────────────────────────────────────────┘
```

---

# 34. Post-MVP Enhancements

After the MVP is successfully demonstrated, the following features can be considered for future versions:

* Advanced deep-learning fraud detection
* Improved signature verification
* Advanced image-forensics models
* Real banking-system integration
* Cloud-based OCR
* High-volume batch processing
* Distributed processing
* Advanced fraud analytics
* Model monitoring
* Automated model retraining
* Enterprise identity integration
* Production-grade deployment
* Real-time operational monitoring

These features are **not required for the initial MVP** and should not delay completion of the core cheque-processing workflow.

---

# 35. Final MVP Workflow

The final MVP should demonstrate this complete flow:

```text
                    USER
                      ↓
              Upload Cheque
                      ↓
             Input Validation
                      ↓
            Image Preprocessing
                      ↓
                     OCR
                      ↓
            Cheque Data Extraction
                      ↓
              Validation Engine
                      ↓
             Fraud Detection
                      ↓
               Risk Scoring
                      ↓
              Decision Engine
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    APPROVE         REVIEW         REJECT
                      ↓
               Manual Review
                      ↓
                Final Action
                      ↓
                 Audit Trail
                      ↓
              Dashboard/Reports
```

The MVP roadmap therefore ensures that **Mass-Mutual_Project is developed as a complete, demonstrable cheque-processing system rather than as separate OCR and fraud-detection components**. The later evaluation documents (`32_OCR_Evaluation.md`, `33_Fraud_Model_Evaluation.md`, and `34_Performance_Evaluation.md`) will provide the evidence for whether the MVP actually meets its stated accuracy and performance targets.

