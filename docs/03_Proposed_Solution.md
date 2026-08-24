# Proposed Solution

# 03. Proposed Solution

## 1. Solution Overview

The proposed solution is an **AI-Powered Cheque Scanning, Validation & Fraud Detection System** designed to automate and simplify the cheque verification process.

The system will process a cheque image through a sequence of automated stages including **image capture, image preprocessing, OCR-based data extraction, validation, fraud detection, risk scoring, and decision making**.

Instead of relying entirely on manual verification, the system will combine **OCR, Computer Vision, rule-based validation, and AI/ML techniques** to identify suspicious cheques and prioritize cases that require human intervention.

The system will provide three primary outcomes:

* **Approve** – cheque satisfies the required validation and risk criteria.
* **Manual Review** – cheque contains uncertainty or suspicious indicators requiring human verification.
* **Reject** – cheque contains critical validation failures or high-risk fraud indicators.

---

## 2. Proposed End-to-End Workflow

The proposed system will follow the workflow below:

```text
Cheque Image
     ↓
Image Upload / Capture
     ↓
File & Image Validation
     ↓
Image Quality Assessment
     ↓
Image Preprocessing
     ↓
OCR Processing
     ↓
Cheque Data Extraction
     ↓
Data Validation
     ↓
Fraud Detection
     ↓
Risk Scoring
     ↓
Decision Engine
     ↓
 ┌──────────┬──────────────┬──────────┐
 │ APPROVE  │ MANUAL REVIEW│  REJECT  │
 └──────────┴──────────────┴──────────┘
              ↓
        Audit Trail
              ↓
       Dashboard & Reports
```

---

## 3. Cheque Input and Image Capture

The system will provide an input module for uploading cheque images.

Supported input formats will include:

* JPEG
* PNG
* PDF

The cheque can be obtained through:

* Scanner
* Camera
* File upload

Before processing, the system will validate:

* File format
* File size
* Image readability
* Image dimensions
* Image integrity

A unique **Processing ID** will be generated for every cheque submitted to the system.

---

## 4. Image Preprocessing

Cheque images may contain noise, skew, shadows, poor lighting, rotation, or low contrast.

The system will therefore use **OpenCV-based image preprocessing** to improve the image before OCR and fraud analysis.

Possible preprocessing operations include:

* Grayscale conversion
* Noise removal
* Contrast enhancement
* Image resizing
* Deskewing
* Rotation correction
* Thresholding
* Cropping
* Background removal
* Region-of-interest detection

The original cheque image will be preserved separately, while preprocessing will operate on a working copy.

---

## 5. OCR-Based Data Extraction

After preprocessing, the system will pass the image to an OCR engine such as **Tesseract, Google Vision, or Azure AI Vision**.

The OCR module will extract text and positional information from the cheque.

The system will attempt to identify:

* Cheque number
* Account number
* Routing/transit/bank identifier where applicable
* Payee name
* Date
* Amount
* Currency
* Relevant MICR-like information
* Signature region

Each extracted field will contain a **confidence score**.

For example:

```json
{
  "field": "amount",
  "raw_value": "Rs. 25,000/-",
  "normalized_value": 25000,
  "confidence": 0.96
}
```

Low-confidence fields will be highlighted for validation or manual review.

---

## 6. Validation Engine

The extracted cheque information will be passed to a validation engine.

The validation engine will perform deterministic checks against **mock banking records or approved banking data sources**.

Validation checks will include:

### Cheque Number Validation

Checks whether the cheque number follows the expected format and series.

### Account Validation

Checks whether the account exists and whether its status permits cheque processing.

### Date Validation

Checks:

* Date format
* Future date
* Expired/stale cheque
* Configured date window

### Payee Validation

Compares the extracted payee with available banking/reference records where applicable.

### Amount Validation

Checks whether the amount is valid and whether different representations of the amount are consistent.

### Duplicate Validation

Checks whether the cheque or transaction has already been processed.

### Cross-Field Validation

Checks for inconsistencies between extracted fields.

---

## 7. Fraud Detection Engine

The fraud detection layer will combine multiple techniques to identify suspicious activity.

### 7.1 Image Tampering Detection

Computer vision techniques will analyze cheque regions for possible:

* Alteration
* Erasure
* Overwriting
* Inconsistent backgrounds
* Suspicious image artifacts
* Region-level modifications

Important regions such as the **amount, payee, date, and signature** can be analyzed separately.

### 7.2 Duplicate Detection

The system will compare the current cheque against previously processed cheques using:

* Cheque number
* Account information
* Amount
* Date
* Image hash
* Image similarity

A high similarity or matching transaction combination will generate a duplicate-related fraud signal.

### 7.3 Signature Analysis

Where a valid reference signature is available, the system will compare the cheque signature against the reference using image-processing or ML-based similarity techniques.

The output may be represented as:

```text
Signature Similarity: 92%
Status: MATCH
```

or:

```text
Signature Similarity: 48%
Status: REVIEW
```

If no reference signature is available, the system will mark signature verification as unavailable rather than automatically treating it as fraud.

### 7.4 Anomaly Detection

The system will analyze available historical/mock transaction information to identify unusual patterns such as:

* Unusually high cheque amount
* Unusual transaction frequency
* Unusual payee
* Unusual account behavior
* Sudden deviation from historical patterns

---

## 8. Risk Scoring

The outputs from validation and fraud detection will be combined by a centralized **Risk Scoring Engine**.

A conceptual risk calculation is:

```text
Risk Score =
    Fraud Indicators
  + Validation Severity
  + Anomaly Score
  + Duplicate Evidence
  + Image/Signature Evidence
  + Uncertainty Penalties
```

The exact weighting will be configurable and evaluated using test data.

The system will classify the resulting score into risk levels such as:

| Risk Level | Description                                  |
| ---------- | -------------------------------------------- |
| Low        | No significant suspicious indicators         |
| Medium     | Some uncertainty or moderate-risk indicators |
| High       | Multiple or critical fraud indicators        |

The system will also store the individual signals contributing to the score.

---

## 9. Decision Engine

The Decision Engine will convert the risk assessment and validation results into an operational workflow decision.

### Approve

A cheque may be classified as an approval candidate when:

* Required fields are successfully extracted.
* Validation rules pass.
* OCR confidence is sufficient.
* No critical fraud indicators are present.
* Risk score is within the configured low-risk range.

### Manual Review

A cheque will be routed to manual review when:

* Important OCR fields have low confidence.
* Validation rules conflict.
* Signature verification is uncertain.
* Duplicate evidence requires investigation.
* Moderate fraud indicators are detected.
* Risk score falls within the review range.

### Reject

A cheque may be rejected when:

* Critical validation conditions fail.
* Strong fraud indicators are detected.
* The configured high-risk policy is triggered.

The rejection decision will be explainable and recorded in the audit trail.

---

## 10. Human-in-the-Loop Review

The system will not attempt to automate every decision.

Cases with uncertainty or suspicious activity will be placed in a **Manual Review Queue**.

The reviewer will be able to view:

* Original cheque image
* Extracted cheque information
* OCR confidence
* Validation results
* Fraud indicators
* Risk score
* Evidence
* Previous processing history

The reviewer can then record:

* Approve
* Reject
* Request further investigation
* Reviewer comments

Every reviewer action will be recorded.

---

## 11. Dashboard and Reporting

A web-based dashboard will provide an overview of the cheque-processing system.

The dashboard will display:

* Total cheques processed
* Approved cheques
* Review cases
* Rejected cheques
* Fraud alerts
* Risk distribution
* OCR confidence
* Processing time
* Validation failures
* Fraud patterns
* Manual review workload

This will help supervisors and analysts understand the overall performance of the system.

---

## 12. Audit Trail

Every major processing event will be recorded.

The audit trail will include:

```text
Upload
  ↓
Image Processing
  ↓
OCR
  ↓
Extraction
  ↓
Validation
  ↓
Fraud Detection
  ↓
Risk Scoring
  ↓
Decision
  ↓
Manual Review (if applicable)
  ↓
Final Disposition
```

The system will maintain references to:

* Processing ID
* Timestamp
* User/service responsible
* Processing stage
* Result
* Model version
* Rule/configuration version
* Decision
* Review action

This provides complete traceability for each cheque.

---

## 13. Proposed Technology Architecture

The proposed implementation will use:

| Layer            | Technology                                    |
| ---------------- | --------------------------------------------- |
| Frontend         | React + Vite                                  |
| Backend          | Python + FastAPI                              |
| OCR              | Tesseract / Google Vision / Azure AI Vision   |
| Image Processing | OpenCV                                        |
| AI/ML            | Python, scikit-learn / TensorFlow as required |
| Database         | PostgreSQL                                    |
| API              | REST API                                      |
| Testing          | Pytest, REST Assured where applicable         |
| Automation       | Playwright / Selenium where required          |
| Cloud            | AWS / Azure / GCP                             |
| Version Control  | Git + GitHub                                  |

The exact technology choices are documented in the Technology Stack (`11_Technology_Stack.md`) and Architecture Decision Records (`docs/adr/`); see ADR-0001 for the backend technology decision.

---

## 14. Key Advantages of the Proposed Solution

The proposed solution provides:

1. **Automated cheque digitization**
2. **Faster data extraction**
3. **Reduced manual verification**
4. **Multi-layer fraud detection**
5. **Explainable risk scoring**
6. **Human-in-the-loop review**
7. **Complete auditability**
8. **Modular and scalable architecture**
9. **Improved operational efficiency**
10. **Foundation for future banking integration**

---

## 15. Proposed Solution Summary

> **The proposed system provides an end-to-end intelligent cheque processing pipeline that combines computer vision, OCR, deterministic validation, fraud detection, anomaly analysis, risk scoring, and human review. By bringing these capabilities into a unified workflow, the system aims to reduce manual verification effort, accelerate cheque processing, improve fraud identification, and provide an explainable and fully auditable decision for every cheque processed.**

