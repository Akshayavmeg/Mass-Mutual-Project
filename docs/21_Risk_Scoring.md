# Risk Scoring

# 21. Risk Scoring

## 1. Introduction

The **Risk Scoring Module** combines the results produced by the validation, fraud detection, signature analysis, duplicate detection, tampering detection, and anomaly detection modules to calculate an overall **risk score for each cheque**.

The purpose of risk scoring is to convert multiple individual risk indicators into one standardized score that can be used by the **Decision Engine**.

The risk score helps the system determine whether a cheque should be:

* **Approved**
* **Sent for Manual Review**
* **Rejected**

> **Important:** The risk score is a decision-support mechanism for the prototype. It does not independently prove that a cheque is fraudulent.

---

# 2. Objectives

The Risk Scoring Module aims to:

1. Combine multiple fraud and validation indicators.
2. Assign appropriate weights to different risk factors.
3. Generate a standardized risk score from **0 to 100**.
4. Classify the cheque into a risk category.
5. Provide clear reasons contributing to the score.
6. Support the final decision-making process.
7. Reduce unnecessary manual verification.
8. Maintain consistency in cheque processing.
9. Store the calculated score in the audit trail.
10. Support future replacement of rule-based scoring with a trained ML model.

---

# 3. Position in the System

The Risk Scoring Module sits between the fraud detection modules and the Decision Engine.

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
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Signature        Duplicate         Anomaly
 Analysis         Detection         Detection
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                Risk Scoring
                       │
                       ▼
               Overall Risk Score
                       │
                       ▼
               Decision Engine
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         APPROVE     REVIEW     REJECT
```

---

# 4. Why Risk Scoring Is Required

Individual fraud checks provide separate results.

For example:

```text
Signature Match       → PASS
Duplicate Check       → PASS
Amount Anomaly        → HIGH
Payee Validation      → WARNING
Image Tampering       → LOW
```

Looking at these results individually makes it difficult to determine the overall risk.

Risk scoring combines them:

```text
Multiple Risk Signals
        ↓
Weighted Risk Calculation
        ↓
Overall Risk Score
        ↓
Risk Category
        ↓
Final Decision
```

---

# 5. Risk Score Range

The project will use a standardized score between:

```text
0 ─────────────────────────────── 100
Low Risk                         High Risk
```

Where:

|  Score | Risk Level |
| -----: | ---------- |
|   0–24 | LOW        |
|  25–49 | MEDIUM     |
|  50–74 | HIGH       |
| 75–100 | CRITICAL   |

These thresholds are **initial prototype thresholds** and should be calibrated using the project's synthetic cheque dataset and evaluation results.

---

# 6. Risk Factors

The risk score will consider the following major factors:

1. Validation result
2. Image tampering
3. Signature mismatch
4. Duplicate cheque detection
5. Amount anomaly
6. Payee anomaly
7. Transaction frequency anomaly
8. Cheque sequence anomaly
9. Account status
10. Date-related risk
11. OCR confidence
12. Other suspicious patterns

---

# 7. Risk Factor Weighting

An initial scoring configuration can be defined as follows:

| Risk Factor                 | Maximum Contribution |
| --------------------------- | -------------------: |
| Image Tampering             |                   20 |
| Signature Risk              |                   20 |
| Duplicate Detection         |                   20 |
| Anomaly Detection           |                   20 |
| Validation Risk             |                   10 |
| OCR/Data Confidence         |                    5 |
| Other Suspicious Indicators |                    5 |
| **Total**                   |              **100** |

The weights are configurable and should be validated experimentally rather than treated as real banking thresholds.

---

# 8. Image Tampering Risk

The image-processing and fraud modules analyze the cheque image for possible manipulation.

Examples:

* Altered amount
* Modified payee
* Edited date
* Copy-paste artifacts
* Image inconsistencies
* Suspicious regions
* Digital manipulation indicators

Example scoring:

| Tampering Result   | Risk Contribution |
| ------------------ | ----------------: |
| No indication      |                 0 |
| Low suspicion      |                 5 |
| Moderate suspicion |                10 |
| High suspicion     |                15 |
| Strong evidence    |                20 |

Example:

```text
Tampering Risk = HIGH

Contribution = 15
```

---

# 9. Signature Risk

The Signature Analysis Module compares the extracted signature region with the available reference signature.

Example:

```text
Signature similarity = 96%
```

Possible interpretation:

```text
LOW RISK
```

Another example:

```text
Signature similarity = 42%
```

Possible interpretation:

```text
HIGH RISK
```

For the prototype:

| Signature Result     | Contribution |
| -------------------- | -----------: |
| Strong match         |            0 |
| Minor concern        |            5 |
| Moderate mismatch    |           10 |
| Significant mismatch |           15 |
| Severe mismatch      |           20 |

The exact thresholds should be determined during model evaluation.

---

# 10. Duplicate Risk

The Duplicate Detection Module checks whether the same cheque or substantially identical cheque has already been processed.

Signals may include:

* Cheque number
* Account number
* Amount
* Date
* Payee
* Image hash

Example:

```text
Cheque already processed
        ↓
Duplicate detected
        ↓
Duplicate Risk = HIGH
```

Suggested contribution:

| Duplicate Result       | Contribution |
| ---------------------- | -----------: |
| No duplicate           |            0 |
| Possible duplicate     |           10 |
| Strong duplicate match |           20 |

A confirmed duplicate should normally cause the Decision Engine to reject or escalate the cheque according to the project's configured policy.

---

# 11. Anomaly Risk

The Anomaly Detection Module produces an anomaly score.

Example:

```text
Anomaly Score = 82/100
```

This score can be converted into a risk contribution.

| Anomaly Level | Contribution |
| ------------- | -----------: |
| Low           |          0–5 |
| Medium        |         6–10 |
| High          |        11–15 |
| Critical      |        16–20 |

Example:

```text
Anomaly Score = 82

Anomaly Contribution = 18
```

---

# 12. Validation Risk

The Validation Engine checks whether the cheque satisfies expected banking rules.

Examples:

* Account exists
* Account is active
* Cheque number is valid
* Cheque date is acceptable
* Amount is valid
* Payee information is valid
* Cheque series is valid

Example:

```text
Account Status → ACTIVE
Cheque Number → VALID
Date → VALID
Payee → MATCH
```

Validation contribution:

```text
0
```

If a validation problem occurs:

```text
Account → CLOSED
```

the risk contribution may be significantly higher.

---

# 13. OCR Confidence Risk

OCR quality affects the reliability of downstream processing.

For example:

```text
OCR Confidence = 98%
```

means the extracted information is relatively reliable.

However:

```text
OCR Confidence = 61%
```

means the extracted values may need additional verification.

Suggested interpretation:

| OCR Confidence | Risk Contribution |
| -------------: | ----------------: |
|          ≥ 95% |                 0 |
|         85–94% |                 1 |
|         70–84% |                 3 |
|          < 70% |                 5 |

The threshold values can be adjusted during testing.

---

# 14. Overall Risk Score Formula

The basic weighted score can be represented as:

[
R = R_t + R_s + R_d + R_a + R_v + R_o + R_p
]

Where:

* (R_t) = tampering risk
* (R_s) = signature risk
* (R_d) = duplicate risk
* (R_a) = anomaly risk
* (R_v) = validation risk
* (R_o) = OCR/data confidence risk
* (R_p) = other pattern risk

The maximum score is normalized to:

[
0 \leq R \leq 100
]

---

# 15. Example Risk Calculation

Suppose a cheque produces:

```text
Tampering Risk       = 10
Signature Risk       = 5
Duplicate Risk       = 0
Anomaly Risk         = 15
Validation Risk      = 3
OCR Risk             = 2
Other Risk           = 2
```

Therefore:

[
R = 10 + 5 + 0 + 15 + 3 + 2 + 2
]

[
R = 37
]

Final result:

```text
Risk Score = 37/100
Risk Level = MEDIUM
```

The Decision Engine may send the cheque for manual review depending on the configured decision rules.

---

# 16. Risk Classification

The initial classification is:

```text
0–24
   ↓
LOW

25–49
   ↓
MEDIUM

50–74
   ↓
HIGH

75–100
   ↓
CRITICAL
```

### LOW

The cheque appears consistent with expected patterns.

Possible decision:

```text
APPROVE
```

### MEDIUM

Some unusual indicators exist.

Possible decision:

```text
MANUAL REVIEW
```

### HIGH

Multiple significant risk indicators are present.

Possible decision:

```text
MANUAL REVIEW
```

or rejection depending on the specific rule triggered.

### CRITICAL

Strong fraud indicators or confirmed issues are present.

Possible decision:

```text
REJECT
```

or mandatory manual review depending on policy.

---

# 17. Risk Score Does Not Replace Hard Rules

Some conditions should be treated as **hard decision rules** rather than simply adding points.

For example:

```text
Confirmed duplicate
        ↓
Mandatory Review / Reject
```

or:

```text
Account is closed
        ↓
Reject
```

Therefore, the Decision Engine should evaluate:

```text
Hard Rules
    +
Risk Score
    +
Fraud Indicators
```

rather than relying only on the numerical score.

---

# 18. Hard Rules vs Risk Score

| Type        | Example               | Effect           |
| ----------- | --------------------- | ---------------- |
| Risk signal | Unusual amount        | Adds risk points |
| Risk signal | New payee             | Adds risk points |
| Risk signal | Low OCR confidence    | Adds risk points |
| Hard rule   | Confirmed duplicate   | Mandatory action |
| Hard rule   | Invalid account       | Reject           |
| Hard rule   | Invalid cheque number | Reject/Review    |
| Hard rule   | Severe tampering      | Reject/Review    |

This prevents a dangerous situation where many low-risk indicators could mathematically offset a critical condition.

---

# 19. Risk Score Explainability

The system should never display only:

```text
Risk Score: 78
```

Instead, it should explain why.

Example:

```text
Risk Score: 78/100
Risk Level: CRITICAL

Contributing Factors:

✓ Amount anomaly             +18
✓ New payee                  +12
✓ Signature mismatch        +15
✓ Image tampering            +20
✓ OCR confidence concern      +3
✓ Duplicate check             +0
✓ Validation                  +0
```

This makes the system easier for a manual reviewer to understand.

---

# 20. Risk Score API

### Endpoint

```http
POST /api/v1/risk-score/calculate
```

### Request

```json
{
  "cheque_id": "CHK-2026-000153",
  "validation_result": {
    "status": "PASS",
    "risk": 3
  },
  "tampering_risk": 10,
  "signature_risk": 5,
  "duplicate_risk": 0,
  "anomaly_risk": 15,
  "ocr_risk": 2
}
```

### Response

```json
{
  "cheque_id": "CHK-2026-000153",
  "risk_score": 35,
  "risk_level": "MEDIUM",
  "decision_recommendation": "MANUAL_REVIEW",
  "risk_factors": [
    {
      "factor": "ANOMALY",
      "contribution": 15
    },
    {
      "factor": "TAMPERING",
      "contribution": 10
    },
    {
      "factor": "SIGNATURE",
      "contribution": 5
    },
    {
      "factor": "OCR",
      "contribution": 2
    },
    {
      "factor": "VALIDATION",
      "contribution": 3
    }
  ]
}
```

---

# 21. Risk Scoring Service

The backend can implement the scoring logic through a dedicated service.

Suggested structure:

```text
apps/
└── backend/
    └── risk_scoring/
        ├── risk_service.py
        ├── risk_rules.py
        ├── risk_weights.py
        ├── risk_calculator.py
        └── risk_repository.py
```

### Responsibilities

| File                 | Responsibility                 |
| -------------------- | ------------------------------ |
| `risk_service.py`    | Coordinates risk scoring       |
| `risk_rules.py`      | Defines scoring and hard rules |
| `risk_weights.py`    | Stores configurable weights    |
| `risk_calculator.py` | Calculates final score         |
| `risk_repository.py` | Stores risk results            |

---

# 22. Configurable Risk Weights

Risk weights should **not be hard-coded throughout the application**.

For example:

```json
{
  "tampering": 20,
  "signature": 20,
  "duplicate": 20,
  "anomaly": 20,
  "validation": 10,
  "ocr": 5,
  "other": 5
}
```

This allows the project team to modify scoring during evaluation without changing the core application logic.

---

# 23. Database Design

A dedicated `risk_scores` table can store each calculation.

Suggested fields:

| Field              | Description              |
| ------------------ | ------------------------ |
| `risk_id`          | Unique risk record       |
| `cheque_id`        | Associated cheque        |
| `risk_score`       | Score from 0–100         |
| `risk_level`       | LOW/MEDIUM/HIGH/CRITICAL |
| `tampering_score`  | Tampering contribution   |
| `signature_score`  | Signature contribution   |
| `duplicate_score`  | Duplicate contribution   |
| `anomaly_score`    | Anomaly contribution     |
| `validation_score` | Validation contribution  |
| `ocr_score`        | OCR contribution         |
| `model_version`    | Version of scoring logic |
| `created_at`       | Timestamp                |

---

# 24. Audit Trail

Every risk calculation should be recorded.

Example:

```text
Cheque ID:
CHK-2026-000153

Risk Score:
78

Risk Level:
CRITICAL

Calculated At:
2026-08-23 12:30:45

Scoring Version:
risk-v1.0

Decision:
MANUAL_REVIEW
```

This supports the project's requirement for a **complete audit trail for every validation decision**.

---

# 25. Dashboard Integration

The dashboard should display:

```text
┌─────────────────────────────────────┐
│ CHEQUE RISK ANALYSIS                │
├─────────────────────────────────────┤
│ Cheque ID: CHK-000153               │
│                                     │
│ Risk Score: 78 / 100                │
│ Risk Level: CRITICAL                │
│                                     │
│ ███████████████░░░                  │
│                                     │
│ Main Risk Factors:                  │
│ • Image Tampering                   │
│ • Signature Mismatch                │
│ • High Amount Anomaly               │
│                                     │
│ Recommended Action:                 │
│ MANUAL REVIEW                       │
└─────────────────────────────────────┘
```

This makes the result easy for reviewers to understand.

---

# 26. Example — Low-Risk Cheque

```text
Validation       = PASS
Tampering        = 0
Signature        = 1
Duplicate        = 0
Anomaly          = 3
OCR              = 0
Other            = 1
```

Total:

```text
Risk Score = 5/100
Risk Level = LOW
```

Possible decision:

```text
APPROVE
```

---

# 27. Example — Medium-Risk Cheque

```text
Validation       = 3
Tampering        = 5
Signature        = 5
Duplicate        = 0
Anomaly          = 15
OCR              = 2
Other            = 3
```

Total:

```text
Risk Score = 33/100
Risk Level = MEDIUM
```

Possible decision:

```text
MANUAL REVIEW
```

---

# 28. Example — High-Risk Cheque

```text
Validation       = 5
Tampering        = 10
Signature        = 15
Duplicate        = 0
Anomaly          = 18
OCR              = 3
Other            = 4
```

Total:

```text
Risk Score = 55/100
Risk Level = HIGH
```

Possible decision:

```text
MANUAL REVIEW
```

---

# 29. Example — Critical-Risk Cheque

```text
Validation       = 8
Tampering        = 20
Signature        = 18
Duplicate        = 20
Anomaly          = 18
OCR              = 3
Other            = 5
```

Total:

```text
Risk Score = 92/100
Risk Level = CRITICAL
```

Additionally:

```text
Confirmed Duplicate = TRUE
```

The Decision Engine should apply the corresponding hard rule, such as:

```text
REJECT
```

or mandatory manual review, depending on the configured policy.

---

# 30. Risk Scoring and Fraud Detection Relationship

The two modules have different responsibilities.

### Fraud Detection

Answers:

> **"What suspicious indicators were detected?"**

Example:

```text
Signature mismatch
Amount anomaly
Possible tampering
Duplicate detected
```

### Risk Scoring

Answers:

> **"How much overall risk do these indicators represent?"**

Example:

```text
Risk Score = 78/100
Risk Level = CRITICAL
```

Therefore:

```text
Fraud Detection
       ↓
Risk Signals
       ↓
Risk Scoring
       ↓
Overall Risk
       ↓
Decision Engine
```

---

# 31. Model and Rule Versioning

Every risk calculation should record the version of the scoring configuration.

Example:

```text
risk-v1.0
```

If the weights are changed:

```text
risk-v1.1
```

If an ML model is introduced:

```text
risk-ml-v1.0
```

This ensures that historical decisions can be reproduced and audited.

---

# 32. Testing Strategy

The Risk Scoring Module should be tested using synthetic test cases.

### Test Case 1 — Normal Cheque

Expected:

```text
Score → LOW
```

### Test Case 2 — High Amount

Expected:

```text
Score increases
```

### Test Case 3 — Signature Mismatch

Expected:

```text
Score increases significantly
```

### Test Case 4 — Duplicate

Expected:

```text
High risk / hard-rule action
```

### Test Case 5 — Multiple Suspicious Signals

Expected:

```text
CRITICAL
```

### Test Case 6 — Missing Historical Data

Expected:

```text
No unjustified high anomaly score
```

---

# 33. Evaluation Metrics

The risk scoring system should be evaluated using:

* Accuracy of risk classification
* Precision
* Recall
* F1-score
* False-positive rate
* False-negative rate
* Manual-review rate
* Processing time
* Decision consistency

The evaluation should be performed against the **synthetic ground-truth dataset** created for this project.

---

# 34. Performance Requirement

The risk scoring calculation should be lightweight.

The complete cheque processing pipeline has the project requirement:

```text
Processing time < 30 seconds per cheque
```

Risk scoring itself should therefore add only a small fraction of the total processing time.

The actual processing time should be measured during performance testing rather than assumed.

---

# 35. Security Considerations

The risk scoring module must:

* Avoid exposing sensitive account information unnecessarily.
* Use authorized backend access.
* Log scoring operations.
* Protect stored risk results.
* Avoid storing unnecessary PII.
* Maintain model/rule version information.
* Prevent unauthorized modification of scoring configuration.

---

# 36. Future ML-Based Risk Scoring

The initial MVP can use a weighted rule-based system.

Later, a supervised ML model can be trained using labeled synthetic/historical transactions.

Possible models:

* Logistic Regression
* Random Forest
* XGBoost
* Gradient Boosting
* Neural Network

The future model could learn:

```text
Cheque Features
      +
Fraud Indicators
      +
Historical Behavior
      ↓
ML Risk Probability
      ↓
Calibrated Risk Score
```

However, the ML model should be introduced only after sufficient labeled data and evaluation are available.

---

# 37. Final Risk Scoring Architecture

```text
                    CHEQUE
                       │
                       ▼
              ┌─────────────────┐
              │ Validation      │
              │ Results         │
              └────────┬────────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
  Tampering        Signature         Duplicate
    Risk              Risk              Risk
       │               │                │
       └───────────────┼────────────────┘
                       │
                       ▼
                Anomaly Results
                       │
                       ▼
                 OCR Confidence
                       │
                       ▼
              Risk Scoring Engine
                       │
                       ▼
              Weighted Calculation
                       │
                       ▼
              Score: 0 – 100
                       │
                       ▼
             Risk Classification
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
      LOW           MEDIUM/HIGH      CRITICAL
       │               │                │
       ▼               ▼                ▼
    APPROVE          REVIEW           REJECT
                       │
                       ▼
                 Audit Trail
```

---

## 38. Summary

The **Risk Scoring Module** provides a unified method for evaluating the overall risk associated with a cheque.

It combines:

```text
Validation
+
Tampering Detection
+
Signature Analysis
+
Duplicate Detection
+
Anomaly Detection
+
OCR Confidence
+
Other Fraud Indicators
        ↓
Weighted Risk Score
        ↓
0–100
        ↓
LOW / MEDIUM / HIGH / CRITICAL
        ↓
Decision Engine
        ↓
APPROVE / REVIEW / REJECT
```

The initial implementation will use an **explainable, configurable weighted scoring system** supported by the synthetic banking and cheque datasets created for the project. The scoring system will maintain detailed reasons and version information so that every decision can be explained and audited. Future versions can incorporate a machine-learning risk model after sufficient labeled data is generated and evaluated.

