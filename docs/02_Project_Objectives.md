# Project Objectives

# 02. Project Objectives

## 1. Primary Objective

The primary objective of this project is to develop an **AI-Powered Cheque Scanning, Validation & Fraud Detection System** that automates the cheque processing workflow by combining **OCR, image processing, rule-based validation, AI/ML-based fraud detection, risk scoring, and human-in-the-loop decision making**.

The system is designed to reduce manual verification effort, improve processing speed, identify suspicious cheques, and provide an explainable and auditable decision for every processed cheque.

---

## 2. Specific Objectives

### 2.1 Automated Cheque Image Processing

To develop a cheque input module that can accept cheque images in supported formats such as **JPEG, PNG, and PDF** through file upload, camera, or scanner input.

The system should validate the uploaded file and create a unique processing record for every cheque.

### 2.2 Image Preprocessing

To improve the quality of cheque images before OCR and fraud analysis by applying computer vision techniques such as:

* Noise removal
* Grayscale conversion
* Contrast enhancement
* Image resizing
* Skew correction
* Rotation correction
* Thresholding
* Cropping and region detection

This improves the reliability of subsequent OCR and image-analysis operations.

### 2.3 Automated OCR-Based Data Extraction

To automatically extract important cheque information using OCR technology.

The system should identify fields such as:

* Cheque number
* Account number
* Routing/transit or bank/branch identifier
* Payee name
* Amount
* Date
* Other relevant visible cheque information

The system should also store **OCR confidence scores** for extracted fields.

### 2.4 Structured Cheque Data Generation

To convert raw OCR output into a structured and standardized cheque data format.

Each extracted field should contain information such as:

* Raw extracted value
* Normalized value
* Confidence score
* Source image region
* Extraction status

This allows downstream validation and fraud detection modules to work with consistent data.

### 2.5 Automated Validation

To develop a validation engine that verifies extracted cheque information against predefined business rules and available mock/approved banking records.

The validation engine should perform checks such as:

* Cheque number validation
* Account existence and status
* Cheque series validation
* Date validity
* Date-window verification
* Payee matching
* Amount validation
* Required-field validation
* Cross-field consistency
* Duplicate cheque checks

### 2.6 Fraud Detection

To develop an intelligent fraud detection module capable of identifying suspicious cheque characteristics using a combination of **rules, computer vision, statistical analysis, and machine learning techniques**.

The system should consider indicators such as:

* Image tampering
* Altered cheque fields
* Duplicate cheque presentation
* Signature mismatch
* Unusual transaction amounts
* Unusual transaction patterns
* Account-related anomalies
* Inconsistent cheque information
* Multiple simultaneous risk indicators

### 2.7 Signature Analysis

To analyze the signature region of a cheque and compare it with an available reference signature where applicable.

The system should generate a similarity/confidence value and flag cases where the similarity falls below a configurable threshold.

If a valid reference signature is unavailable, the system should report that signature verification could not be performed rather than automatically treating the cheque as fraudulent.

### 2.8 Duplicate Detection

To identify possible duplicate cheque submissions using combinations of:

* Cheque number
* Account information
* Amount
* Date
* Image hash
* Image similarity
* Available transaction history

The system should identify duplicate candidates and provide the related evidence for review.

### 2.9 Anomaly Detection

To identify unusual cheque behavior by comparing the current cheque against available historical or mock banking data.

Examples include:

* Unusually high transaction amount
* Unusual frequency of cheque usage
* Unusual payee
* Unexpected transaction pattern
* Abnormal account activity

### 2.10 Risk Scoring

To combine validation results, OCR confidence, fraud indicators, anomaly results, duplicate evidence, and other relevant features into an overall **risk score**.

The system should categorize the result into configurable risk levels such as:

* **Low Risk**
* **Medium Risk**
* **High Risk**

Each risk score should be explainable through the individual signals that contributed to it.

### 2.11 Automated Decision Workflow

To develop a decision engine that routes each cheque into an appropriate workflow based on the validation and fraud-analysis results.

The primary decision states are:

```text
APPROVE
   ↓
REVIEW
   ↓
REJECT
```

The decision engine should use configurable thresholds and business rules rather than hard-coded decisions distributed across multiple modules.

### 2.12 Human-in-the-Loop Manual Review

To provide a manual review workflow for cases where the system has insufficient confidence or identifies suspicious activity.

Reviewers should be able to view:

* Original cheque image
* Extracted information
* OCR confidence
* Validation failures
* Fraud indicators
* Risk score
* Supporting evidence
* Previous processing/review history

The reviewer should be able to record the final disposition and comments.

### 2.13 Dashboard and Reporting

To develop a dashboard that provides an overview of cheque-processing activity.

The dashboard should display information such as:

* Total cheques processed
* Approved cheques
* Cheques requiring review
* Rejected cheques
* Fraud alerts
* Risk distribution
* OCR performance
* Processing time
* Review workload
* Common validation failures
* Fraud detection trends

### 2.14 Complete Audit Trail

To maintain a complete audit trail for every cheque-processing decision.

The audit trail should record important events such as:

* Upload
* Image preprocessing
* OCR execution
* Data extraction
* Validation
* Fraud analysis
* Risk scoring
* Decision
* Manual review
* Final disposition

Each important decision should be traceable to the relevant processing, model, rule, and configuration versions.

### 2.15 Security and Privacy

To protect cheque images and financial information throughout the processing lifecycle.

The system should:

* Use role-based access control
* Protect sensitive information
* Avoid exposing PII in application logs
* Keep credentials and API keys outside source code
* Use mock/synthetic banking data during development
* Maintain controlled access to cheque images
* Provide auditable user actions

### 2.16 Performance Improvement

To reduce the time required for cheque verification and target:

* **Processing time below 30 seconds per cheque** under defined test conditions
* **At least 50% reduction in manual review cases**
* **60–80% reduction in manual verification effort**

These targets will be measured during system evaluation.

---

## 3. AI/ML Objectives

The project will use AI/ML where it provides measurable value rather than replacing deterministic banking rules.

The AI/ML objectives are to:

1. Improve cheque image understanding.
2. Improve OCR-based information extraction.
3. Detect suspicious image alterations.
4. Analyze signature similarity where reference data exists.
5. Detect unusual transaction patterns.
6. Combine multiple fraud indicators into a meaningful risk assessment.
7. Provide confidence scores for uncertain predictions.
8. Support explainable fraud decisions.
9. Evaluate models using appropriate performance metrics.
10. Maintain model/version traceability.

---

## 4. Target Performance Objectives

| Objective                               |                       Target |
| --------------------------------------- | ---------------------------: |
| OCR extraction accuracy                 |                        ≥ 95% |
| Fraud detection accuracy                |                        ≥ 90% |
| Processing time                         |          < 30 seconds/cheque |
| Reduction in manual review cases        |                        ≥ 50% |
| Reduction in manual verification effort |                       60–80% |
| Audit coverage                          | 100% of processing decisions |

The targets above are **evaluation goals for the project** and will be validated using a defined test dataset and evaluation methodology.

---

## 5. Overall Objective

The overall objective can be summarized as:

> **To develop a secure, modular, explainable, and AI-assisted cheque processing system that automates cheque image scanning, OCR-based data extraction, validation, fraud detection, risk scoring, and decision routing while reducing manual verification effort and maintaining a complete audit trail for every processing decision.**

