# Existing System

# 06. Existing System

## 1. Introduction

Cheque processing in traditional banking environments generally involves a combination of **physical cheque handling, image capture, OCR/MICR-based data extraction, rule-based validation, banking-system checks, and manual verification**.

The exact workflow varies between financial institutions. Therefore, this document describes the **general characteristics and limitations of a conventional cheque-processing workflow**, rather than claiming that every bank uses the same implementation.

The proposed AI-powered system is intended to improve this workflow by combining cheque digitization, automated validation, fraud analysis, risk scoring, and human review within a unified processing pipeline.

---

## 2. Conventional Cheque Processing Workflow

A typical cheque-processing workflow can be represented as:

```text
Physical / Digital Cheque
          ↓
Cheque Image Capture
          ↓
Image Quality Check
          ↓
MICR / OCR Data Extraction
          ↓
Banking Record Validation
          ↓
Business Rule Checks
          ↓
Fraud / Exception Checks
          ↓
Manual Verification
          ↓
Final Processing Decision
          ↓
Clearing / Settlement
```

The exact sequence and technologies can differ depending on the financial institution and cheque-clearing infrastructure.

---

# 3. Major Components of the Existing System

## 3.1 Cheque Collection and Image Capture

Traditional cheque processing begins with the collection of a physical cheque.

The cheque may be:

* Deposited at a bank branch
* Processed through a cheque scanning system
* Captured using specialized banking equipment

The cheque image is then made available to downstream processing systems.

---

## 3.2 MICR-Based Processing

Many conventional cheque-processing environments rely heavily on **Magnetic Ink Character Recognition (MICR)** information printed in the cheque's MICR line.

MICR can provide machine-readable information such as:

* Cheque number
* Bank/routing information
* Account-related information

MICR is particularly useful for structured machine-readable fields, but it does not by itself solve all cheque verification requirements.

---

## 3.3 OCR-Based Data Extraction

OCR may be used to extract information that is not available through structured MICR data.

Depending on the cheque format, OCR can be used for information such as:

* Payee
* Date
* Amount
* Other printed or handwritten information

However, OCR performance can be affected by:

* Image quality
* Handwriting
* Fonts
* Background patterns
* Skew
* Noise
* Different cheque layouts

---

## 3.4 Banking Record Validation

Extracted cheque information can be checked against available banking records.

Typical checks may include:

* Account existence
* Account status
* Cheque number
* Cheque series
* Transaction information
* Date validity
* Amount
* Other institution-specific business rules

This stage helps identify cheques that cannot be processed normally.

---

# 4. Traditional Fraud Detection

Conventional cheque fraud detection generally involves a combination of **predefined rules, transaction checks, image examination, and manual investigation**.

Potential fraud indicators can include:

* Duplicate cheque numbers
* Invalid account information
* Suspicious transaction amounts
* Signature discrepancies
* Altered cheque fields
* Unusual transaction behavior
* Repeated cheque submissions

Rules and thresholds may be configured by the financial institution.

---

# 5. Manual Verification

Cases that cannot be confidently processed automatically may be sent to banking personnel for manual verification.

The reviewer may inspect:

* Cheque image
* Extracted information
* Account information
* Signature
* Transaction history
* Validation failures
* Other available evidence

The reviewer then determines the appropriate action according to the institution's procedures.

---

# 6. Existing System Limitations

The following limitations represent common challenges in conventional or partially automated cheque-processing workflows.

## 6.1 Dependence on Manual Verification

Cases that fail automated checks often require human investigation.

When processing large volumes of cheques, this can result in:

* Increased workload
* Longer processing times
* Higher operational cost
* Potential human errors

---

## 6.2 Fragmented Processing

Different activities may be handled by separate systems or processes.

For example:

```text
OCR System
     ↓
Banking Validation
     ↓
Fraud System
     ↓
Manual Review System
     ↓
Reporting System
```

When these components are not integrated into a unified workflow, it can be difficult to obtain a single view of the cheque's complete processing history.

---

## 6.3 OCR Errors

OCR accuracy can decrease when cheque images contain:

* Poor lighting
* Blur
* Skew
* Noise
* Handwritten text
* Low-resolution characters
* Complex backgrounds

Incorrect OCR results can subsequently affect validation and fraud analysis.

---

## 6.4 Limited Context-Aware Fraud Detection

Purely rule-based fraud detection can identify known suspicious conditions effectively, but may have difficulty identifying previously unseen patterns.

For example, a simple rule such as:

```text
IF amount > threshold
THEN flag cheque
```

does not necessarily consider the customer's normal transaction behavior.

An AI/ML-assisted system can complement deterministic rules by analyzing multiple features and identifying unusual combinations.

---

## 6.5 False Positives

Aggressive fraud rules may flag legitimate transactions.

This can lead to:

* Increased manual review
* Reviewer workload
* Delayed processing
* Customer inconvenience

Therefore, the proposed system will use risk scoring and configurable thresholds rather than treating every individual anomaly as confirmed fraud.

---

## 6.6 Limited Explainability Across Multiple Checks

When multiple systems contribute to a decision, it can be difficult for a reviewer to understand exactly why a cheque was flagged.

A unified system can consolidate the relevant signals:

```text
Duplicate Candidate      → Yes
Signature Similarity     → 52%
Amount Anomaly           → Yes
OCR Confidence           → 71%
Account Validation       → Passed

                 ↓

          Risk Score: 78
                 ↓
           MANUAL REVIEW
```

This provides the reviewer with a clearer explanation of the decision.

---

## 6.7 Difficulty Handling Unseen Fraud Patterns

Traditional rule-based approaches depend heavily on predefined conditions.

If a fraudulent pattern does not match an existing rule, it may not be detected effectively.

Machine-learning and anomaly-detection techniques can complement rules by identifying unusual combinations or deviations from historical patterns.

---

## 6.8 Limited Automated Evidence Correlation

A suspicious cheque may have evidence across several areas:

* Image
* OCR
* Account information
* Transaction history
* Signature
* Duplicate records

If these signals are evaluated independently, investigators may need to manually correlate them.

The proposed solution addresses this by bringing the signals together into a unified risk assessment.

---

# 7. Existing System vs. Proposed System

| Area                   | Existing / Conventional Approach       | Proposed System                                      |
| ---------------------- | -------------------------------------- | ---------------------------------------------------- |
| Cheque input           | Scanning / capture                     | Upload, scanner, camera                              |
| Image processing       | Basic or system-specific preprocessing | Dedicated OpenCV preprocessing pipeline              |
| Data extraction        | MICR/OCR and manual correction         | OCR + structured extraction + confidence             |
| Validation             | Banking rules and system checks        | Centralized configurable validation engine           |
| Fraud detection        | Rules, checks, manual investigation    | Rules + CV + anomaly detection + ML where justified  |
| Signature verification | Manual/system-specific checks          | Automated similarity analysis where reference exists |
| Duplicate detection    | Transaction/record checks              | Record + hash + image similarity                     |
| Anomaly detection      | Limited or rule-based                  | Statistical/ML-assisted analysis                     |
| Risk assessment        | Rule/exception based                   | Centralized configurable risk scoring                |
| Decision               | Processing workflow                    | Approve / Review / Reject                            |
| Manual review          | Exception handling                     | Integrated review queue                              |
| Explainability         | May be distributed across systems      | Consolidated risk factors and evidence               |
| Audit trail            | Institution-specific                   | Centralized processing audit trail                   |
| Dashboard              | Existing operational reports           | Unified processing and fraud dashboard               |
| Model tracking         | Depends on system                      | Model/version traceability                           |
| Development data       | Production banking data                | Mock/synthetic data for prototype                    |

---

# 8. Problems Addressed by the Proposed System

The proposed system is specifically designed to address the following challenges:

### Problem 1 — Manual Effort

**Existing:** Human reviewers may need to investigate a large number of exceptions.

**Proposed:** Automatically process low-risk cheques and route only uncertain or suspicious cases for review.

---

### Problem 2 — Fragmented Information

**Existing:** OCR, validation, fraud detection, and review information may be distributed.

**Proposed:** Provide a unified processing pipeline and centralized record for each cheque.

---

### Problem 3 — Multiple Fraud Indicators

**Existing:** Individual rules may evaluate fraud indicators separately.

**Proposed:** Combine multiple signals into a risk score.

---

### Problem 4 — Unusual Transaction Patterns

**Existing:** Fixed rules may not detect every unusual behavior pattern.

**Proposed:** Add anomaly detection using available historical/mock transaction data.

---

### Problem 5 — Difficult Investigation

**Existing:** Reviewers may need to manually gather evidence from different systems.

**Proposed:** Present the cheque image, extracted fields, validation results, fraud indicators, risk score, and processing history together.

---

### Problem 6 — Lack of Consistent Auditability

**Existing:** Audit information depends on the underlying systems and processes.

**Proposed:** Maintain a centralized audit trail for the complete cheque-processing lifecycle.

---

# 9. Existing System Workflow

A simplified representation of the conventional workflow is:

```text
              CHEQUE
                 │
                 ▼
          Image Capture
                 │
                 ▼
          MICR / OCR
                 │
                 ▼
       Banking Validation
                 │
        ┌────────┴────────┐
        │                 │
      PASS              EXCEPTION
        │                 │
        ▼                 ▼
  Continue Process    Manual Review
                          │
                          ▼
                   Investigation
                          │
                          ▼
                    Final Action
```

The proposed system enhances this process by introducing a dedicated **fraud intelligence and risk-scoring layer**.

---

# 10. Need for the Proposed System

The limitations identified above demonstrate the need for a more integrated cheque-processing approach.

The proposed system addresses this need by combining:

```text
OCR
 +
Computer Vision
 +
Rule-Based Validation
 +
Duplicate Detection
 +
Signature Analysis
 +
Anomaly Detection
 +
Risk Scoring
 +
Human Review
 +
Audit Trail
```

into a single processing architecture.

The objective is **not to eliminate human involvement completely**, but to ensure that human expertise is focused on cases where it provides the most value.

---

# 11. Summary

> **The existing cheque-processing environment generally combines cheque image capture, MICR/OCR extraction, banking validation, predefined fraud checks, and manual exception handling. While these mechanisms provide essential cheque-processing capabilities, challenges can arise from manual verification effort, OCR errors, fragmented processing, false positives, limited detection of unfamiliar patterns, and difficulty correlating evidence across multiple checks. The proposed AI-powered system addresses these challenges by integrating OCR, computer vision, rule-based validation, duplicate detection, signature analysis, anomaly detection, risk scoring, manual review, dashboard reporting, and a centralized audit trail into a unified cheque-processing workflow.**
