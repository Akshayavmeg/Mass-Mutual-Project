# Problem Statement

# 01. Problem Statement

## 1. Background

Cheque processing is an important banking operation that requires accurate extraction of cheque information, validation of banking details, and detection of potentially fraudulent activity. Traditional cheque processing workflows often involve a combination of manual verification, Optical Character Recognition (OCR), rule-based checks, and separate fraud investigation procedures.

Manual processing can be time-consuming and may introduce human errors, especially when dealing with a large number of cheques. Poor-quality cheque images, handwritten information, altered fields, duplicate submissions, signature inconsistencies, and unusual transaction patterns can further complicate the verification process.

Therefore, there is a need for an intelligent system that can automate the initial cheque verification process while providing clear evidence and explanations for cases that require human intervention.

## 2. Problem Definition

The proposed project aims to develop an **AI-Powered Cheque Scanning, Validation & Fraud Detection System** that can automatically process cheque images and assist banking personnel in determining whether a cheque should be approved, sent for manual review, or rejected.

The system will accept cheque images in formats such as **JPEG, PNG, and PDF**, captured through a camera, scanner, or file upload. It will use image processing and OCR techniques to extract important cheque information, including:

* Cheque number
* Account number
* Routing/transit or bank/branch identifier, where applicable
* Payee name
* Amount
* Date
* Signature region
* Other relevant cheque information visible in the image

The extracted information will then be validated against available **mock or approved banking records** and predefined business rules.

## 3. Fraud Detection Problem

The system will identify suspicious cheques by analyzing multiple fraud indicators rather than relying on a single rule.

Potential indicators include:

* Altered or tampered cheque regions
* Duplicate cheque submissions
* Duplicate cheque numbers or transaction combinations
* Signature mismatch or low signature similarity when a reference is available
* Invalid or suspicious cheque dates
* Account status inconsistencies
* Payee mismatches
* Unusual transaction amounts or patterns
* Inconsistent extracted information
* Low OCR confidence in important fields
* Multiple suspicious indicators occurring simultaneously

Each detected indicator will contribute to an overall **risk assessment**.

## 4. Proposed Decision

Based on validation results, fraud indicators, OCR confidence, and the calculated risk score, the system will classify each cheque into an appropriate workflow:

### Approve

The cheque has sufficient confidence, passes required validation checks, and does not contain significant fraud indicators.

### Manual Review

The cheque contains uncertainty, conflicting information, or moderate-risk indicators that require verification by an authorized banking analyst.

### Reject

The cheque contains critical validation failures or strong fraud indicators that meet the configured rejection criteria.

The system will provide the reasons behind a review or rejection decision so that users can understand **why the cheque was flagged**.

## 5. Key Problem Areas

The project addresses the following major problems:

| Problem                        | Proposed Solution                          |
| ------------------------------ | ------------------------------------------ |
| Manual cheque data entry       | Automated OCR-based extraction             |
| Poor-quality cheque images     | Image preprocessing and quality assessment |
| OCR extraction errors          | Confidence scoring and validation          |
| Invalid cheque information     | Rule-based validation engine               |
| Duplicate cheques              | Duplicate detection mechanisms             |
| Signature inconsistencies      | Signature-region analysis                  |
| Altered cheque information     | Image/tampering analysis                   |
| Unusual transaction behavior   | Anomaly detection                          |
| Fragmented fraud checks        | Unified fraud detection pipeline           |
| Difficult manual investigation | Explainable fraud indicators and evidence  |
| Lack of traceability           | Complete audit trail                       |

## 6. Target Outcomes

The system is designed to achieve the following target outcomes:

* **OCR extraction accuracy:** ≥ 95%
* **Fraud detection accuracy:** ≥ 90%
* **Processing time:** < 30 seconds per cheque under defined test conditions
* **Manual review reduction:** at least 50%
* **Manual verification effort reduction:** approximately 60–80%
* Faster cheque processing and turnaround
* Improved identification of suspicious transactions
* Reduced operational effort and potential financial losses
* Better customer experience through faster processing
* Complete auditability of validation and decision-making

These are **project targets to be evaluated during testing**, not guaranteed production performance figures.

## 7. Project Boundary

The system focuses on **automated cheque image processing, OCR, validation, fraud analysis, decision support, manual review, dashboarding, reporting, and audit logging**.

It is not intended to replace a bank's core banking system, payment settlement infrastructure, or real-time cheque-clearing network.

## 8. Problem Statement Summary

> **To design and develop an intelligent AI-powered cheque processing system that automatically scans cheque images, extracts key cheque information using OCR and computer vision, validates the extracted information against banking records and predefined rules, detects potential fraud using rule-based and AI/ML techniques, calculates a risk score, and routes each cheque to an appropriate Approve, Manual Review, or Reject workflow while maintaining a complete and explainable audit trail.**


