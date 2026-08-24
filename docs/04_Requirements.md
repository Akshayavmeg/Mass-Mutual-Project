# Requirements

# 04. Requirements

## 1. Introduction

This document defines the functional and non-functional requirements for the **AI-Powered Cheque Scanning, Validation & Fraud Detection System**.

The requirements describe what the system must do, how it should perform, what data it should process, and the security, reliability, usability, and auditability standards it should maintain.

The system is intended as a prototype/decision-support solution and will use **mock or approved banking data** for validation during development.

---

# 2. Functional Requirements

Functional requirements define the capabilities that the system must provide.

## FR-001 — Cheque Image Upload

The system shall allow authorized users to upload cheque images in supported formats.

**Supported formats:**

* JPEG/JPG
* PNG
* PDF

The system shall reject unsupported file formats and display an appropriate error message.

---

## FR-002 — Image Capture

The system should support cheque image acquisition from:

* Scanner
* Camera
* File upload

The captured image shall be passed through the same validation and processing pipeline as an uploaded image.

---

## FR-003 — File Validation

Before processing, the system shall validate:

* File format
* File size
* Image readability
* Image dimensions
* File integrity

Invalid or corrupted files shall not be passed to the OCR or fraud detection modules.

---

## FR-004 — Processing ID Generation

The system shall generate a unique **Processing ID** for every cheque submitted.

Example:

```text
CHK-2026-000001
```

The Processing ID shall be used to associate:

* Image
* OCR results
* Extracted fields
* Validation results
* Fraud results
* Risk score
* Decision
* Audit events

---

## FR-005 — Original Image Preservation

The system shall preserve the original cheque image or a protected reference to it.

Image preprocessing shall operate on a separate working copy.

The original image shall not be overwritten by preprocessing operations.

---

# 3. Image Processing Requirements

## FR-006 — Image Quality Assessment

The system shall assess the quality of the uploaded cheque image before OCR processing.

The assessment should consider:

* Resolution
* Blur
* Brightness
* Contrast
* Skew
* Rotation
* Noise
* Image readability

The system shall identify images that are unsuitable for reliable processing.

---

## FR-007 — Image Preprocessing

The system shall preprocess cheque images using computer vision techniques where required.

Possible operations include:

* Grayscale conversion
* Noise removal
* Contrast enhancement
* Thresholding
* Resizing
* Deskewing
* Rotation correction
* Cropping
* Background normalization

The preprocessing steps applied to an image shall be recorded.

---

# 4. OCR Requirements

## FR-008 — OCR Processing

The system shall use an OCR engine to extract textual information from cheque images.

Possible OCR technologies include:

* Tesseract
* Google Vision
* Azure AI Vision

The OCR engine shall be implemented through an adapter/interface so that the underlying OCR provider can be replaced without redesigning the complete system.

---

## FR-009 — Cheque Field Extraction

The system shall extract relevant cheque information, including where visible:

* Cheque number
* Account number
* Routing/transit number
* Bank/branch identifier
* Payee
* Amount
* Date
* Currency
* MICR-related information
* Signature region

The system shall not fabricate values when a field cannot be reliably extracted.

---

## FR-010 — OCR Confidence

The system shall generate and store a confidence score for extracted fields whenever supported by the OCR/extraction implementation.

Example:

```text
Cheque Number : 123456
Confidence    : 98%

Amount        : ₹25,000
Confidence    : 96%

Payee         : ABC Enterprises
Confidence    : 89%
```

Low-confidence fields shall be considered during validation and decision-making.

---

## FR-011 — Data Normalization

The system shall normalize extracted values into a standard internal representation.

Examples:

```text
"Rs. 25,000/-" → 25000.00

"12/08/2026" → 2026-08-12
```

The original OCR value shall be retained separately from the normalized value.

---

# 5. Validation Requirements

## FR-012 — Cheque Number Validation

The system shall validate the cheque number against the configured cheque-number format and available cheque series information.

---

## FR-013 — Account Validation

The system shall validate the extracted account information against mock or approved banking records.

The system may check:

* Account existence
* Account status
* Account eligibility
* Associated cheque series

---

## FR-014 — Date Validation

The system shall validate the cheque date.

The validation should identify:

* Invalid date formats
* Impossible dates
* Future dates where not permitted
* Expired/stale cheques
* Dates outside the configured processing window

---

## FR-015 — Payee Validation

Where reference information is available, the system shall compare the extracted payee with the corresponding banking/reference record.

Potential mismatches shall generate a validation or fraud signal.

---

## FR-016 — Amount Validation

The system shall validate the cheque amount.

The system should check:

* Numeric amount
* Written amount where available
* Numeric/written amount consistency
* Valid amount range
* Currency consistency

---

## FR-017 — Cross-Field Validation

The system shall perform consistency checks between extracted fields.

For example:

```text
Numeric Amount = ₹25,000
Written Amount = Twenty Five Thousand
                 ↓
             MATCH
```

If the values conflict, the system shall generate a validation failure or review signal.

---

## FR-018 — Duplicate Validation

The system shall check whether the cheque may have already been processed.

Duplicate detection may use:

* Cheque number
* Account number
* Amount
* Date
* Transaction identifiers
* Image hash
* Image similarity

---

# 6. Fraud Detection Requirements

## FR-019 — Fraud Signal Generation

The system shall generate fraud indicators based on available cheque information, image analysis, transaction information, and historical/mock data.

---

## FR-020 — Tampering Detection

The system shall analyze relevant cheque regions for potential alterations or tampering.

Potential regions include:

* Amount
* Payee
* Date
* Cheque number
* Signature

The system may use OpenCV and machine-learning techniques for this analysis.

---

## FR-021 — Signature Analysis

Where a valid reference signature is available, the system shall compare the cheque signature with the reference signature.

The system shall generate a similarity score.

Example:

```text
Signature Similarity: 92%
Status: MATCH
```

If the similarity falls below the configured threshold, the cheque shall receive a signature-related risk signal.

If no reference signature exists, the system shall mark signature verification as unavailable.

---

## FR-022 — Duplicate Fraud Detection

The system shall identify possible duplicate cheque submissions using image and transaction-level evidence.

A duplicate candidate shall include references to the previously matched record where available.

---

## FR-023 — Anomaly Detection

The system shall identify unusual cheque patterns using available historical or mock transaction data.

Potential anomalies include:

* Unusually high amount
* Unusual transaction frequency
* Unusual payee
* Unusual account activity
* Significant deviation from historical behavior

---

## FR-024 — Multiple Signal Correlation

The system shall combine multiple fraud indicators rather than relying exclusively on a single indicator.

For example:

```text
Duplicate Candidate       → High
Signature Similarity      → Low
Unusual Amount            → Medium
OCR Confidence            → Low

                ↓

        Combined Risk
                ↓
          MANUAL REVIEW
```

---

# 7. Risk Scoring Requirements

## FR-025 — Risk Score Generation

The system shall calculate a risk score using relevant:

* Validation results
* Fraud signals
* OCR confidence
* Anomaly scores
* Duplicate evidence
* Signature analysis
* Image-analysis results

---

## FR-026 — Risk Classification

The system shall classify the calculated risk into configurable categories.

Example:

| Risk Score | Risk Level |
| ---------: | ---------- |
|       0–30 | Low        |
|      31–70 | Medium     |
|     71–100 | High       |

**Note:** These values are initial example thresholds and must be calibrated during testing.

---

## FR-027 — Explainable Risk Score

The system shall provide the major factors contributing to the risk score.

Example:

```text
Risk Score: 78

Contributing Factors:
✓ Duplicate candidate       +30
✓ Signature mismatch        +25
✓ Unusual amount            +15
✓ Low OCR confidence        +8
```

---

# 8. Decision Workflow Requirements

## FR-028 — Automated Decision

The system shall generate a workflow recommendation based on validation results, fraud signals, risk score, and configured business rules.

The supported decisions shall be:

```text
APPROVE
REVIEW
REJECT
```

---

## FR-029 — Approve Decision

The system may recommend **APPROVE** when:

* Required information is available.
* Critical validation checks pass.
* No significant fraud indicators are detected.
* Risk is within the configured low-risk range.

---

## FR-030 — Manual Review Decision

The system shall route a cheque to **MANUAL REVIEW** when:

* Important fields have low confidence.
* Validation results conflict.
* Fraud indicators require investigation.
* Risk falls within the configured review range.
* Required reference information is unavailable for an important check.

---

## FR-031 — Reject Decision

The system may recommend **REJECT** when critical validation failures or high-risk conditions satisfy the configured rejection policy.

The rejection reason shall be recorded.

---

# 9. Manual Review Requirements

## FR-032 — Review Queue

The system shall provide a queue containing cheques requiring manual investigation.

The queue should display:

* Processing ID
* Date/time
* Risk level
* Risk score
* Reason for review
* Current status
* Assigned reviewer

---

## FR-033 — Review Evidence

Reviewers shall be able to access:

* Original cheque image
* Extracted cheque data
* OCR confidence
* Validation results
* Fraud signals
* Risk score
* Relevant evidence
* Processing history

---

## FR-034 — Reviewer Decision

An authorized reviewer shall be able to record the final outcome.

The reviewer should provide a reason/comment for material decisions.

---

# 10. Dashboard Requirements

## FR-035 — Processing Dashboard

The system shall provide a dashboard showing cheque-processing statistics.

The dashboard should include:

* Total cheques processed
* Approved cheques
* Review cases
* Rejected cheques
* Fraud alerts
* Risk distribution
* Processing time
* OCR confidence
* Validation failures

---

## FR-036 — Reporting

The system shall provide reports that help authorized users analyze:

* Processing volume
* Fraud trends
* Review workload
* Decision distribution
* Validation failures
* System performance
* OCR performance

---

# 11. Audit Requirements

## FR-037 — Audit Trail

The system shall maintain an audit trail for every important processing event.

Events shall include, where applicable:

```text
Upload
Image Validation
Preprocessing
OCR
Extraction
Validation
Fraud Analysis
Risk Scoring
Decision
Manual Review
Final Disposition
```

---

## FR-038 — Decision Traceability

Every final decision shall be traceable to:

* Processing ID
* Extracted data
* Validation results
* Fraud signals
* Risk score
* Decision policy
* Model version where applicable
* Configuration version
* Reviewer action where applicable

---

# 12. Security Requirements

## FR-039 — Authentication

The production-oriented system shall require authenticated access to protected functionality.

---

## FR-040 — Role-Based Access Control

The system shall support role-based permissions.

Example roles:

| Role          | Access                              |
| ------------- | ----------------------------------- |
| Admin         | Configuration and system management |
| Analyst       | Processing and review               |
| Fraud Analyst | Fraud investigation                 |
| Supervisor    | Review, reporting and oversight     |
| Viewer        | Read-only reporting                 |

---

## FR-041 — Sensitive Data Protection

The system shall protect sensitive cheque and financial information.

It shall:

* Restrict access to cheque images.
* Avoid unnecessary storage of PII.
* Mask sensitive values in logs.
* Keep secrets outside source code.
* Use synthetic/mock data during development.

---

# 13. Non-Functional Requirements

## NFR-001 — Performance

The system shall target a processing time of **less than 30 seconds per cheque** under defined test conditions.

Performance shall be measured separately for:

* Image preprocessing
* OCR
* Extraction
* Validation
* Fraud analysis
* Risk scoring
* Total processing time

---

## NFR-002 — OCR Accuracy

The system shall target an OCR/extraction accuracy of **at least 95%** on the defined evaluation dataset.

Accuracy shall be measured at field level and documented in the OCR evaluation report.

---

## NFR-003 — Fraud Detection Accuracy

The fraud detection system shall target **at least 90% accuracy** on the defined evaluation dataset.

Additional metrics such as:

* Precision
* Recall
* F1-score
* False-positive rate
* False-negative rate
* ROC-AUC where appropriate

shall also be evaluated.

---

## NFR-004 — Reliability

The system shall handle invalid inputs and component failures gracefully without corrupting cheque records or audit information.

---

## NFR-005 — Scalability

The architecture should support future scaling through:

* Stateless API services
* Background processing
* Worker queues
* Independent OCR/fraud services
* Database optimization

---

## NFR-006 — Maintainability

The system shall use modular components so that OCR engines, fraud models, validation rules, and database implementations can be modified independently.

---

## NFR-007 — Explainability

Fraud and risk decisions shall provide understandable reasons and supporting indicators to authorized reviewers.

---

## NFR-008 — Auditability

All important processing and decision events shall be recorded with sufficient information to reconstruct the processing history.

---

## NFR-009 — Usability

The dashboard and review interface should allow authorized users to understand a cheque's status and risk information without requiring technical knowledge of the underlying ML models.

---

## NFR-010 — Security

The system shall follow secure development practices including:

* Authentication
* Authorization
* Input validation
* Secure API design
* Secret management
* Secure logging
* Data protection
* Least-privilege access

---

## NFR-011 — Privacy

Development and testing shall use **mock/synthetic banking data** unless real data has been explicitly authorized and appropriately protected.

---

## NFR-012 — Reproducibility

A processing decision should be reproducible using the stored:

* Model version
* Ruleset version
* Configuration version
* Processing data
* Risk thresholds

---

# 14. Target Performance Requirements

| Metric                               |                       Target |
| ------------------------------------ | ---------------------------: |
| OCR extraction accuracy              |                        ≥ 95% |
| Fraud detection accuracy             |                        ≥ 90% |
| Processing time                      |          < 30 seconds/cheque |
| Manual review reduction              |                        ≥ 50% |
| Manual verification effort reduction |                       60–80% |
| Audit coverage                       | 100% of processing decisions |

These are **project evaluation targets**, not guaranteed production SLAs.

---

# 15. Technology Requirements

The proposed system may use the following technologies:

| Category           | Proposed Technology                         |
| ------------------ | ------------------------------------------- |
| Frontend           | React + Vite                                |
| Backend            | Python + FastAPI                            |
| OCR                | Tesseract / Google Vision / Azure AI Vision |
| Image Processing   | OpenCV                                      |
| AI/ML              | Python, TensorFlow / scikit-learn           |
| Database           | PostgreSQL                                  |
| API                | REST                                        |
| Testing            | Pytest, REST Assured                        |
| Browser Automation | Playwright / Selenium                       |
| Cloud              | AWS / Azure / GCP                           |
| Version Control    | Git + GitHub                                |

Technology choices are finalized through the project's Architecture Decision Records (`docs/adr/`); see ADR-0001 for the backend technology decision.

---

# 16. Requirement Traceability

The major requirements map to the system modules as follows:

```text
FR-001 – FR-005
        ↓
Cheque Input Module

FR-006 – FR-007
        ↓
Image Processing Module

FR-008 – FR-011
        ↓
OCR + Data Extraction

FR-012 – FR-018
        ↓
Validation Engine

FR-019 – FR-024
        ↓
Fraud Detection

FR-025 – FR-027
        ↓
Risk Scoring

FR-028 – FR-031
        ↓
Decision Engine

FR-032 – FR-034
        ↓
Manual Review

FR-035 – FR-036
        ↓
Dashboard & Reporting

FR-037 – FR-038
        ↓
Audit Trail

FR-039 – FR-041
        ↓
Security & Access Control
```

## 17. Requirements Acceptance Criteria

The requirements document is considered satisfied when the implemented system can demonstrate the complete lifecycle:

```text
Cheque Upload
      ↓
Image Processing
      ↓
OCR Extraction
      ↓
Validation
      ↓
Fraud Detection
      ↓
Risk Scoring
      ↓
Approve / Review / Reject
      ↓
Audit Trail
      ↓
Dashboard / Reporting
```

Every major stage must have a defined input, output, error-handling mechanism, test case, and traceable result.

