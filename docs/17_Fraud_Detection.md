# Fraud Detection

# 17. Fraud Detection

## 1. Introduction

The **Fraud Detection Engine** is a core security component of the AI-Powered Cheque Scanning, Validation & Fraud Detection System.

Its purpose is to identify **suspicious or potentially fraudulent cheques** by analyzing information obtained from OCR, image processing, the Validation Engine, signature analysis, duplicate detection, and anomaly detection.

The Fraud Detection Engine does **not rely on a single rule** to determine fraud. Instead, it combines multiple indicators and produces a **fraud risk score** that is passed to the Decision Engine.

```text
Cheque Image
     │
     ▼
OCR + Image Analysis
     │
     ▼
Cheque Data Extraction
     │
     ▼
Validation Engine
     │
     ├── Account mismatch
     ├── Cheque mismatch
     ├── Payee mismatch
     ├── Date anomaly
     └── Amount inconsistency
             │
             ▼
┌──────────────────────────────┐
│     FRAUD DETECTION ENGINE   │
│                              │
│ • Tampering Detection        │
│ • Duplicate Indicators       │
│ • Signature Indicators       │
│ • Amount Anomalies           │
│ • Behavioural Patterns       │
│ • Rule-Based Detection       │
│ • ML-Based Detection         │
└──────────────┬───────────────┘
               │
               ▼
         Fraud Risk Score
               │
               ▼
       Risk / Decision Engine
```

---

# 2. Objectives

The objectives of the Fraud Detection Engine are:

1. Detect suspicious cheque characteristics.
2. Identify possible image tampering.
3. Detect duplicate cheque submissions.
4. Identify suspicious account and cheque patterns.
5. Detect inconsistencies between cheque fields.
6. Incorporate signature-analysis results.
7. Detect unusual transaction amounts.
8. Detect abnormal cheque usage patterns.
9. Combine multiple fraud indicators into a single risk score.
10. Reduce false positives by using multiple independent signals.
11. Support automatic approval, manual review, and rejection decisions.
12. Provide an explainable reason for every fraud alert.
13. Maintain an audit trail of fraud-detection decisions.
14. Support future machine-learning-based fraud detection.

---

# 3. Fraud Detection Approach

The project will use a **hybrid fraud detection architecture**.

It combines:

### 1. Rule-Based Detection

Explicit banking and fraud rules.

### 2. Image-Based Detection

Analysis of the cheque image for possible alteration or tampering.

### 3. Pattern/Anomaly Detection

Identification of unusual transaction characteristics.

### 4. ML-Based Detection

A machine-learning model can be added to identify patterns that are difficult to capture through manually defined rules.

The MVP should prioritize **explainable rule-based detection**, while the architecture should remain ready for ML integration.

---

# 4. Why a Hybrid Approach?

A purely rule-based system can miss previously unseen fraud patterns.

A purely ML-based system can be difficult to explain and may require a large amount of labeled banking data.

Therefore:

```text
                 Fraud Detection
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Rules          Image          ML/Anomaly
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Risk Aggregation
                       │
                       ▼
                  Risk Score
```

This gives the system both:

* **Explainability**
* **Flexibility**

---

# 5. Fraud Detection Inputs

The Fraud Detection Engine receives information from multiple modules.

| Source                 | Information                     |
| ---------------------- | ------------------------------- |
| Image Preprocessing    | Image quality and image regions |
| OCR Engine             | Extracted text                  |
| Cheque Data Extraction | Structured cheque fields        |
| Validation Engine      | Validation failures/warnings    |
| Signature Analysis     | Signature similarity result     |
| Duplicate Detection    | Duplicate indicators            |
| Anomaly Detection      | Unusual transaction patterns    |
| Mock Banking Data      | Account and cheque history      |

Example input:

```json
{
  "cheque_id": "CHK-2026-000002",
  "account_number": "1002345678",
  "cheque_number": "000125",
  "payee_name": "John Doe",
  "amount": 75000.00,
  "date": "2026-08-20",
  "validation_failures": [
    "PAYEE_MATCH"
  ],
  "duplicate_detected": false,
  "signature_similarity": 0.62,
  "image_tampering_score": 0.78
}
```

---

# 6. Fraud Indicators

The system evaluates several fraud indicators.

### Primary indicators

```text
1. Image tampering
2. Signature mismatch
3. Duplicate cheque
4. Account mismatch
5. Cheque-series mismatch
6. Payee mismatch
7. Amount inconsistency
8. Date anomaly
9. Unusual transaction amount
10. Unusual cheque frequency
11. Suspicious cheque number
12. Multiple validation failures
```

Each indicator contributes to the overall fraud risk.

---

# 7. Image Tampering Detection

Cheque images may be manipulated digitally before being submitted.

The system should look for suspicious visual characteristics such as:

* Altered amount
* Altered payee
* Altered date
* Modified cheque number
* Different font characteristics
* Inconsistent spacing
* Copy-paste artifacts
* Suspicious regions
* Image composition inconsistencies

Example:

```text
Original-looking region
        +
Suspiciously modified region
        ↓
Image Tampering Indicator
```

The system should not claim that an image is fraudulent solely because an image artifact is detected.

It should generate a **tampering risk indicator**.

---

# 8. Image Tampering Score

A normalized score can be used:

```text
0.00 ─────────────────────── 1.00
 │                            │
Low tampering              High tampering
```

Example:

```text
Tampering Score = 0.12
```

→ Low concern.

```text
Tampering Score = 0.82
```

→ High concern.

This score can be combined with other fraud indicators.

---

# 9. Amount Tampering

The amount area is a particularly important cheque region.

The system can compare:

```text
Numeric Amount
      +
Amount in Words
      +
OCR result
      +
Image characteristics
```

Example:

```text
Numeric amount:
₹25,000

Amount in words:
Twenty Five Thousand Only

Result:
CONSISTENT
```

Suspicious case:

```text
Numeric amount:
₹75,000

Amount in words:
Twenty Five Thousand Only

Result:
MISMATCH
```

This produces a high-priority fraud indicator.

---

# 10. Payee Tampering

The payee field should be analyzed for inconsistencies.

Example:

```text
Extracted Payee:
John Doe

Expected Payee:
Jane Doe
```

Result:

```text
PAYEE_MISMATCH = TRUE
```

The system should consider this alongside:

* cheque type
* banking record
* image analysis
* account history

before making a final decision.

---

# 11. Signature Mismatch

The signature area can be analyzed using the Signature Analysis module.

The Fraud Detection Engine receives the result rather than performing all signature processing itself.

Example:

```text
Signature Similarity = 0.94
```

→ Low concern.

```text
Signature Similarity = 0.42
```

→ High concern.

A low similarity score should increase fraud risk but should not automatically prove fraud.

Detailed signature processing belongs to:

```text
18_Signature_Analysis.md
```

---

# 12. Duplicate Cheque Detection

Fraudsters may attempt to submit the same cheque multiple times.

The system should compare the current cheque with historical processing records.

Possible matching attributes:

```text
Account Number
Cheque Number
Amount
Date
Payee
Image fingerprint
```

Example:

```text
Current cheque:
Account = 1002345678
Cheque = 000123
Amount = 25,000

Previous record:
Account = 1002345678
Cheque = 000123
Amount = 25,000
```

Result:

```text
DUPLICATE RISK = HIGH
```

Detailed duplicate detection is documented separately in:

```text
19_Duplicate_Detection.md
```

---

# 13. Account-Based Fraud Indicators

The system can identify suspicious account-related characteristics.

Examples:

* Account does not exist
* Account is closed
* Account is blocked
* Account is frozen
* Cheque does not belong to the account
* Routing/transit number mismatch
* Unusual cheque activity

Example:

```text
Account Status = CLOSED
```

This is a strong fraud/risk indicator.

---

# 14. Cheque-Series Fraud Indicator

The system compares the cheque number with the expected cheque series.

Example:

```text
Expected:
000100 – 000199

Submitted:
000523
```

Result:

```text
CHEQUE_SERIES_ANOMALY = TRUE
```

Possible causes:

* OCR error
* Incorrect cheque
* Account mismatch
* Counterfeit cheque
* Tampering

Therefore, the system should combine this indicator with other signals.

---

# 15. Date-Based Fraud Indicators

The system should detect suspicious dates.

Examples:

### Future-dated cheque

```text
Cheque Date > Processing Date
```

### Stale cheque

```text
Cheque Date significantly older than allowed window
```

### Invalid date

```text
Date cannot be interpreted correctly
```

### Unusual date pattern

A cheque may also be suspicious if its date conflicts with known transaction records.

---

# 16. Amount-Based Anomaly Detection

The system can compare the current cheque amount with historical transaction behavior.

Example:

```text
Historical average cheque amount:
₹15,000

Current cheque:
₹2,50,000
```

This is potentially unusual.

However:

> An unusually large cheque is not automatically fraudulent.

It should generate an anomaly indicator.

---

# 17. Frequency-Based Detection

The system can analyze cheque frequency.

Example:

```text
Normal:
2 cheques per month

Current activity:
15 cheques in one day
```

This may indicate suspicious activity.

The system can calculate:

```text
Cheque Frequency
=
Number of cheques
/
Defined time period
```

The threshold should be configurable.

---

# 18. Multiple Validation Failures

A single validation failure may be caused by OCR error.

However, multiple independent failures are more concerning.

Example:

```text
Account          → PASS
Cheque Series    → FAIL
Payee            → FAIL
Amount           → FAIL
Signature        → FAIL
Duplicate        → PASS
```

This combination represents a significantly higher risk than one isolated failure.

---

# 19. Fraud Rule Engine

The project should maintain fraud rules separately from application logic where practical.

Example:

```text
RULE-001:
IF account does not exist
THEN increase risk significantly

RULE-002:
IF cheque is already processed
THEN mark duplicate risk as high

RULE-003:
IF payee mismatch AND signature mismatch
THEN increase risk significantly

RULE-004:
IF amount mismatch
THEN create high-priority alert

RULE-005:
IF multiple high-risk indicators exist
THEN route to manual review
```

The actual thresholds should be configurable.

---

# 20. Rule Severity

Each fraud rule should have a severity.

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Example:

| Indicator                    | Severity |
| ---------------------------- | -------- |
| Minor image anomaly          | LOW      |
| Unusual amount               | MEDIUM   |
| Payee mismatch               | HIGH     |
| Duplicate cheque             | HIGH     |
| Stopped cheque               | CRITICAL |
| Multiple critical indicators | CRITICAL |

---

# 21. Risk Scoring

Each fraud indicator contributes to a total risk score.

Example conceptual model:

```text
Fraud Risk Score =
    Image Risk
  + Validation Risk
  + Signature Risk
  + Duplicate Risk
  + Anomaly Risk
  + Transaction Risk
```

The score should be normalized between:

```text
0 – 100
```

Example:

```text
0–29   → Low Risk
30–59  → Medium Risk
60–79  → High Risk
80–100 → Critical Risk
```

These are **initial project thresholds** and should be calibrated during testing rather than presented as proven banking thresholds.

---

# 22. Example Risk Calculation

Consider:

```text
Image Tampering       = High
Payee Mismatch        = Yes
Signature Similarity  = Low
Duplicate             = No
Account Validation    = Pass
Amount Anomaly        = Medium
```

The system may produce:

```text
Image Risk            = 25
Payee Risk            = 20
Signature Risk        = 25
Duplicate Risk        = 0
Account Risk          = 0
Amount Risk           = 10
                     ─────
Total                 = 80
```

Result:

```text
Risk Score = 80/100
Risk Level = CRITICAL
```

The exact weights should be configurable and evaluated using the project's test dataset.

---

# 23. Explainable Fraud Detection

Every fraud decision must have an explanation.

Instead of:

```text
Fraud = TRUE
```

the system should produce:

```text
Risk Score: 82

Reasons:
1. Payee mismatch
2. Signature similarity below configured threshold
3. Possible image tampering detected
4. Amount significantly differs from historical pattern
```

This is important for:

* Manual reviewers
* Auditors
* Demonstrations
* Debugging
* Model evaluation
* Regulatory/compliance considerations

---

# 24. Fraud Alert Structure

Example:

```json
{
  "cheque_id": "CHK-2026-000002",
  "risk_score": 82,
  "risk_level": "CRITICAL",
  "alerts": [
    {
      "type": "PAYEE_MISMATCH",
      "severity": "HIGH"
    },
    {
      "type": "SIGNATURE_MISMATCH",
      "severity": "HIGH"
    },
    {
      "type": "IMAGE_TAMPERING",
      "severity": "HIGH"
    }
  ]
}
```

---

# 25. Fraud Detection Workflow

```text
                Cheque Data
                    │
                    ▼
          Collect Fraud Indicators
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
     Image       Validation    History
     Analysis      Results      Analysis
        │           │            │
        └───────────┼────────────┘
                    ▼
             Rule Evaluation
                    │
                    ▼
            Anomaly Detection
                    │
                    ▼
             Risk Aggregation
                    │
                    ▼
             Fraud Risk Score
                    │
                    ▼
              Decision Engine
```

---

# 26. ML-Based Fraud Detection

The architecture should support a future machine-learning model.

Potential algorithms include:

* Random Forest
* XGBoost
* Logistic Regression
* Isolation Forest
* Neural Networks

For the MVP, a simpler explainable model such as **Random Forest/XGBoost** can be evaluated if sufficient labeled synthetic data is available.

For unsupervised anomaly detection:

```text
Isolation Forest
```

can be considered for identifying unusual transaction patterns.

---

# 27. ML Input Features

Potential model features include:

```text
amount
cheque_age
account_age
cheque_frequency
average_historical_amount
amount_deviation
payee_match
account_status
cheque_series_match
duplicate_indicator
signature_similarity
image_tampering_score
ocr_confidence
validation_failure_count
```

Example:

```json
{
  "amount": 75000,
  "amount_deviation": 3.4,
  "payee_match": 0,
  "duplicate_indicator": 0,
  "signature_similarity": 0.61,
  "image_tampering_score": 0.74,
  "validation_failure_count": 2
}
```

---

# 28. Synthetic Fraud Dataset

Because real banking data cannot be assumed to be available, this project will create a **synthetic dataset** for development and evaluation.

Example:

```text
data/
├── mock_banking_data/
├── sample_cheques/
└── test_data/
```

The dataset can contain categories such as:

```text
VALID
DUPLICATE
PAYEE_TAMPERED
AMOUNT_TAMPERED
SIGNATURE_MISMATCH
INVALID_ACCOUNT
STALE_CHEQUE
STOPPED_CHEQUE
CHEQUE_SERIES_ANOMALY
MULTIPLE_ANOMALIES
```

This dataset will be used to test the fraud detection pipeline.

---

# 29. Synthetic Data Generation

Each synthetic cheque should have:

```text
Cheque Image
Cheque Number
Account Number
Routing/Transit Number
Payee
Amount
Amount in Words
Date
Signature Region
Ground Truth Label
```

Example:

```json
{
  "cheque_id": "SYN-00001",
  "label": "VALID",
  "amount": 25000,
  "payee_name": "John Doe"
}
```

Fraudulent example:

```json
{
  "cheque_id": "SYN-00002",
  "label": "AMOUNT_TAMPERED",
  "original_amount": 25000,
  "modified_amount": 75000
}
```

All such records should be clearly marked as **synthetic** and should never contain real customer information.

---

# 30. Fraud Detection Output

The Fraud Detection Engine should produce:

```text
Fraud Risk Score
Risk Level
Detected Indicators
Rule Violations
Model Prediction
Explanation
Confidence/Model Probability where applicable
```

Example:

```json
{
  "cheque_id": "CHK-2026-000002",
  "fraud_risk_score": 82,
  "risk_level": "CRITICAL",
  "prediction": "SUSPICIOUS",
  "indicators": [
    "PAYEE_MISMATCH",
    "SIGNATURE_MISMATCH",
    "IMAGE_TAMPERING"
  ],
  "recommendation": "MANUAL_REVIEW"
}
```

---

# 31. Relationship with Decision Engine

The Fraud Detection Engine should **not directly approve or reject** the cheque.

Instead:

```text
Fraud Detection
       ↓
Risk Score
       ↓
Decision Engine
       ↓
┌─────────┬────────┬────────┐
│ APPROVE │ REVIEW │ REJECT │
└─────────┴────────┴────────┘
```

This separation keeps the architecture clean.

---

# 32. Example Decision Scenarios

### Scenario 1 — Low Risk

```text
Risk Score = 12
```

All important validation checks pass.

Possible result:

```text
APPROVE
```

### Scenario 2 — Medium Risk

```text
Risk Score = 48
```

One or more unusual indicators exist.

Possible result:

```text
REVIEW
```

### Scenario 3 — High Risk

```text
Risk Score = 75
```

Multiple suspicious indicators exist.

Possible result:

```text
REVIEW / REJECT
```

### Scenario 4 — Critical Risk

```text
Risk Score = 92
```

Critical indicators such as duplicate/stopped cheque combined with other suspicious signals.

Possible result:

```text
REJECT
```

The exact final decision rules belong to `22_Decision_Engine.md`.

---

# 33. Audit Trail

Every fraud detection operation must be recorded.

Example:

```json
{
  "cheque_id": "CHK-2026-000002",
  "timestamp": "2026-08-20T10:18:42Z",
  "risk_score": 82,
  "risk_level": "CRITICAL",
  "rules_triggered": [
    "PAYEE_MISMATCH",
    "SIGNATURE_MISMATCH",
    "IMAGE_TAMPERING"
  ],
  "engine_version": "fraud-engine-v1.0"
}
```

The audit record allows the organization to determine:

* What happened?
* Which rules triggered?
* What score was generated?
* Which model/rule version was used?
* When was the decision generated?

---

# 34. Security Requirements

The Fraud Detection Engine must:

1. Protect cheque and account information.
2. Avoid exposing sensitive information in logs.
3. Use secure database connections.
4. Validate all incoming data.
5. Restrict access to fraud-related information.
6. Maintain immutable/auditable decision records where supported.
7. Protect model files and configuration.
8. Version fraud rules and ML models.
9. Prevent unauthorized modification of fraud thresholds.
10. Ensure synthetic data is clearly separated from real banking data.

---

# 35. Performance Requirements

The Fraud Detection Engine should support the overall project requirement:

> **Complete cheque processing time < 30 seconds per cheque.**

Fraud detection should therefore be optimized to execute within the overall processing pipeline.

Performance measurements should include:

```text
Image analysis time
Rule evaluation time
Feature generation time
ML inference time
Risk calculation time
Database lookup time
```

Final measured results should be documented in:

```text
34_Performance_Evaluation.md
```

---

# 36. Functional Requirements

The Fraud Detection Engine shall:

1. Receive structured cheque information.
2. Receive validation results.
3. Receive image-analysis indicators.
4. Receive signature-analysis results.
5. Receive duplicate-detection results.
6. Evaluate predefined fraud rules.
7. Identify suspicious patterns.
8. Generate fraud indicators.
9. Calculate a fraud risk score.
10. Assign a risk level.
11. Generate explainable fraud alerts.
12. Support configurable thresholds.
13. Support future ML-based fraud detection.
14. Record fraud detection results.
15. Pass the risk assessment to the Decision Engine.

---

# 37. Non-Functional Requirements

### Accuracy

The project target is:

> **Fraud detection accuracy ≥ 90%.**

This target must be measured against a defined test dataset and evaluation methodology. It should not be claimed as achieved until testing confirms it.

### Performance

Fraud analysis should fit within the overall `<30 seconds per cheque` target.

### Explainability

Each alert should contain understandable reasons.

### Reliability

Failures in fraud analysis should not result in automatic approval.

Example:

```text
Fraud Engine unavailable
        ↓
Risk cannot be calculated
        ↓
Manual Review
```

### Maintainability

Fraud rules and models should be versioned independently.

---

# 38. Testing Strategy

The Fraud Detection Engine should be tested using synthetic test cases.

### Test Case 1 — Valid Cheque

```text
No suspicious indicators
Expected:
LOW RISK
```

### Test Case 2 — Duplicate Cheque

```text
Duplicate = TRUE
Expected:
HIGH/CRITICAL RISK
```

### Test Case 3 — Payee Tampering

```text
Payee mismatch
Expected:
Risk increases
```

### Test Case 4 — Amount Tampering

```text
Numeric amount ≠ words
Expected:
HIGH RISK INDICATOR
```

### Test Case 5 — Signature Mismatch

```text
Low signature similarity
Expected:
Risk increases
```

### Test Case 6 — Image Tampering

```text
High image tampering score
Expected:
Risk increases
```

### Test Case 7 — Multiple Indicators

```text
Payee mismatch
+
Signature mismatch
+
Image tampering
```

Expected:

```text
HIGH/CRITICAL RISK
```

### Test Case 8 — Normal High-Value Cheque

```text
High amount
BUT
all other indicators normal
```

Expected:

```text
Possible anomaly/review
NOT automatically fraud
```

This is important for reducing false positives.

---

# 39. Evaluation Metrics

The fraud detection system should not be evaluated using accuracy alone.

The following metrics should be measured:

### Accuracy

```text
(TP + TN) / (TP + TN + FP + FN)
```

### Precision

```text
TP / (TP + FP)
```

### Recall

```text
TP / (TP + FN)
```

### F1 Score

```text
2 × Precision × Recall
----------------------
Precision + Recall
```

### False Positive Rate

```text
FP / (FP + TN)
```

### False Negative Rate

```text
FN / (FN + TP)
```

For a fraud-detection system, **false negatives are particularly important**, because failing to detect a fraudulent cheque can result in financial loss.

Detailed evaluation will be documented in:

```text
33_Fraud_Model_Evaluation.md
```

---

# 40. Fraud Detection Module Structure

The proposed backend structure is:

```text
apps/
└── backend/
    ├── fraud_detection/
    │   ├── rules/
    │   │   ├── account_rules.py
    │   │   ├── cheque_rules.py
    │   │   ├── amount_rules.py
    │   │   └── image_rules.py
    │   │
    │   ├── features/
    │   │   └── feature_engineering.py
    │   │
    │   ├── models/
    │   │   └── fraud_model.py
    │   │
    │   ├── scoring/
    │   │   └── risk_scorer.py
    │   │
    │   └── fraud_service.py
```

This is an implementation proposal and can be adjusted during actual development.

---

# 41. Example End-to-End Fraud Analysis

Consider the following cheque:

```text
Cheque Number: 000125
Account: 1002345678
Payee: John Doe
Amount: ₹75,000
Date: 20/08/2026
```

The system finds:

```text
Account                 → PASS
Cheque Series           → PASS
Cheque Status           → PASS
Payee Match             → FAIL
Amount Anomaly          → HIGH
Duplicate               → PASS
Signature Similarity    → LOW
Image Tampering         → MEDIUM
```

Fraud Engine:

```text
Payee mismatch          +20
Amount anomaly          +15
Signature risk          +25
Image tampering         +10
Duplicate               +0
                         ───
Risk Score              70
```

Output:

```text
Risk Score: 70/100
Risk Level: HIGH

Reasons:
• Payee mismatch
• Unusual transaction amount
• Low signature similarity
• Image tampering indicator

Recommendation:
MANUAL REVIEW
```

The Decision Engine will make the final workflow decision.

---

# 42. Module Boundary

## Responsible for

```text
✓ Fraud rules
✓ Fraud indicators
✓ Tampering indicators
✓ Suspicious patterns
✓ Risk aggregation
✓ Risk scoring
✓ Fraud alerts
✓ Explainability
✓ ML inference where implemented
✓ Fraud audit records
```

## Not responsible for

```text
✗ Image upload
✗ OCR
✗ Raw cheque data extraction
✗ Basic banking validation
✗ Signature image processing
✗ Final approval/rejection
✗ Manual reviewer actions
✗ Payment settlement
```

---

# 43. End-to-End Position

```text
┌──────────────────────────────┐
│ Cheque Image                 │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ OCR + Data Extraction        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Validation Engine            │
└──────────────┬───────────────┘
               ↓
╔══════════════════════════════╗
║      FRAUD DETECTION         ║
║                              ║
║ • Rules                      ║
║ • Tampering                  ║
║ • Signature indicators       ║
║ • Duplicate indicators      ║
║ • Anomaly indicators         ║
║ • ML model                   ║
║ • Risk scoring               ║
╚══════════════╤═══════════════╝
               ↓
┌──────────────────────────────┐
│ Risk Score / Risk Level      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Decision Engine              │
└──────────────┬───────────────┘
               ↓
       ┌───────┼────────┐
       ▼       ▼        ▼
    APPROVE  REVIEW   REJECT
```

---

# 44. Summary

The **Fraud Detection Engine** is responsible for identifying suspicious cheque activity by combining information from **validation results, image analysis, signature analysis, duplicate detection, transaction patterns, and optional machine-learning models**.

The system follows a **risk-based approach** rather than treating every anomaly as fraud.

Its output is an explainable risk assessment:

```text
Fraud Risk Score
       +
Risk Level
       +
Triggered Indicators
       +
Explanation
```

This information is passed to the **Decision Engine**, which determines whether the cheque should be:

```text
APPROVE
   │
   ├── REVIEW
   │
   └── REJECT
```

The project will initially use **synthetic/mock banking data and synthetic fraud scenarios** so that the complete pipeline can be developed and evaluated without using real customer banking information. The target of **≥90% fraud-detection accuracy** will be treated as an evaluation goal and verified experimentally using the project's test dataset.

