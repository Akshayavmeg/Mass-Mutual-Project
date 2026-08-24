# Anomaly Detection

# 20. Anomaly Detection

## 1. Introduction

The **Anomaly Detection Module** identifies cheque transactions that differ significantly from the normal transaction behavior associated with an account, cheque history, or defined banking rules.

An anomaly does **not automatically mean fraud**. It indicates that a cheque is unusual and may require additional investigation.

For this project, anomaly detection will analyze factors such as:

* Unusually high cheque amount
* Unusual transaction frequency
* Unusual cheque timing
* Unusual payee
* Unusual account activity
* Unusual cheque sequence
* Unusual geographic or channel information, if available
* Repeated unusual transaction patterns

The module generates anomaly indicators that are passed to the **Fraud Detection Engine**.

---

# 2. Objectives

The objectives of the Anomaly Detection Module are:

1. Establish normal transaction behavior using historical synthetic banking data.
2. Identify transactions that deviate significantly from normal behavior.
3. Detect unusually high or low cheque amounts.
4. Detect unusual cheque frequency.
5. Identify unusual payees.
6. Detect unusual cheque-number sequences.
7. Identify unusual transaction patterns.
8. Generate an anomaly score.
9. Classify the anomaly risk.
10. Provide understandable reasons for detected anomalies.
11. Pass anomaly indicators to the Fraud Detection Engine.
12. Maintain anomaly results in the audit trail.

---

# 3. Why Anomaly Detection Is Required

Traditional validation checks whether a cheque is structurally valid.

For example:

```text
Account exists?
Cheque number valid?
Date valid?
Amount valid?
```

However, a cheque can pass all these checks and still be suspicious.

Example:

```text
Account:
Normal cheque amount → ₹5,000 – ₹20,000

New cheque:
Amount → ₹4,50,000
```

The cheque may be technically valid, but the amount is highly unusual for that account.

Therefore:

```text
VALID CHEQUE
      ≠
NORMAL CHEQUE
```

Anomaly detection identifies these unusual patterns.

---

# 4. Position in Overall System

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
             Anomaly Detection
                      │
       ┌──────────────┼───────────────┐
       ▼              ▼               ▼
 Amount Anomaly   Payee Anomaly   Frequency Anomaly
       │              │               │
       └──────────────┼───────────────┘
                      ▼
                Anomaly Score
                      │
                      ▼
             Fraud Detection Engine
                      │
                      ▼
                Risk Scoring
                      │
                      ▼
              Decision Engine
```

---

# 5. Input Data

The module requires the current cheque information and historical transaction information.

### Current Cheque

* Account number
* Cheque number
* Amount
* Date
* Payee
* Transaction channel, if available

### Historical Data

* Previous cheque amounts
* Previous cheque dates
* Previous payees
* Previous cheque numbers
* Transaction frequency
* Account activity
* Historical transaction status

For this project, this information will be generated using **synthetic/mock banking data**.

---

# 6. Synthetic Banking Dataset

We need to create our own dataset for anomaly detection.

Suggested structure:

```text
data/
└── mock_banking_data/
    ├── accounts.csv
    ├── customers.csv
    ├── cheques.csv
    ├── transactions.csv
    └── payees.csv
```

Example `transactions.csv`:

```csv
transaction_id,account_number,transaction_date,transaction_type,amount,payee
TXN001,1002345678,2026-07-01,CHEQUE,8500,ABC Stores
TXN002,1002345678,2026-07-05,CHEQUE,12000,XYZ Traders
TXN003,1002345678,2026-07-12,CHEQUE,9500,ABC Stores
TXN004,1002345678,2026-07-20,CHEQUE,11000,DEF Services
TXN005,1002345678,2026-07-28,CHEQUE,13500,ABC Stores
```

Then a new cheque:

```text
Amount = ₹4,50,000
```

would be highly unusual compared with the account's historical behavior.

---

# 7. Types of Anomalies

The system will initially support the following anomaly categories:

1. **Amount Anomaly**
2. **Frequency Anomaly**
3. **Payee Anomaly**
4. **Cheque Sequence Anomaly**
5. **Timing Anomaly**
6. **Transaction Pattern Anomaly**
7. **Account Behavior Anomaly**

---

# 8. Amount Anomaly

Amount anomaly identifies cheques whose amounts are significantly different from the account's historical cheque amounts.

Example:

```text
Historical amounts:

₹8,500
₹12,000
₹9,500
₹11,000
₹13,500
```

Average:

```text
₹10,900
```

New cheque:

```text
₹4,50,000
```

This is significantly higher than the historical pattern.

Therefore:

```text
Amount Anomaly = HIGH
```

---

# 9. Mean and Standard Deviation Approach

For the initial prototype, statistical analysis can be used.

Calculate:

### Mean

[
\mu = \frac{\sum x_i}{n}
]

where:

* (x_i) = historical cheque amount
* (n) = number of historical transactions

### Standard Deviation

[
\sigma = \sqrt{\frac{\sum(x_i-\mu)^2}{n}}
]

The current cheque can then be compared with the historical distribution.

---

# 10. Z-Score

A simple anomaly score can be generated using the Z-score.

[
Z = \frac{x-\mu}{\sigma}
]

Where:

* (x) = current cheque amount
* (\mu) = historical mean
* (\sigma) = historical standard deviation

Example:

```text
Historical Mean = ₹10,900
Standard Deviation = ₹2,000
Current Amount = ₹50,000
```

[
Z = \frac{50000-10900}{2000}
]

[
Z = 19.55
]

This would represent an extreme deviation.

---

# 11. Initial Amount Anomaly Thresholds

For the prototype, a starting rule can be:

| Absolute Z-Score | Classification   |
| ---------------: | ---------------- |
|              < 2 | Normal           |
|              2–3 | Moderate Anomaly |
|              3–4 | High Anomaly     |
|              > 4 | Critical Anomaly |

These are **initial statistical thresholds**, not banking-industry fraud thresholds. They must be evaluated and adjusted using our synthetic dataset.

---

# 12. Frequency Anomaly

Frequency anomaly identifies unusually frequent cheque activity.

Example historical behavior:

```text
Normal:
2–5 cheques per month
```

Current activity:

```text
15 cheques in 2 days
```

This may indicate unusual account activity.

Result:

```text
Frequency Anomaly = HIGH
```

---

# 13. Frequency Calculation

The system can calculate:

```text
Cheques per day
Cheques per week
Cheques per month
```

Example:

```text
Previous 30 days:
4 cheques

Current 2 days:
10 cheques
```

This is significantly different from the historical pattern.

---

# 14. Payee Anomaly

The system can identify whether a cheque is being issued to an unusual payee.

Example historical payees:

```text
ABC Stores
XYZ Traders
DEF Services
ABC Stores
XYZ Traders
```

New payee:

```text
UNKNOWN INTERNATIONAL LLC
```

The system can generate:

```text
PAYEE_ANOMALY
```

This does not mean the payee is fraudulent.

It simply indicates that the payee is outside the account's normal historical pattern.

---

# 15. Payee Frequency

The system can calculate how frequently an account has interacted with a particular payee.

Example:

```text
ABC Stores → 15 transactions
XYZ Traders → 10 transactions
DEF Services → 8 transactions
Unknown LLC → 1 transaction
```

The new payee has little historical association with the account.

Therefore:

```text
Payee Familiarity = LOW
```

This may contribute to the anomaly score.

---

# 16. Cheque Sequence Anomaly

Cheque numbers normally follow a sequence, depending on the account's cheque book structure.

Example:

```text
00120
00121
00122
00123
00124
```

Suddenly:

```text
00987
```

may be unusual.

The system can flag:

```text
CHEQUE_SEQUENCE_ANOMALY
```

However, sequence analysis should be treated carefully because cheque numbers may not always be strictly sequential in real-world processing.

---

# 17. Timing Anomaly

If transaction timestamp information is available, the system can analyze unusual timing patterns.

Example:

```text
Normal:
Cheque activity → business hours

New:
Unusual transaction time
```

The system can generate:

```text
TIMING_ANOMALY
```

For the MVP, timing analysis should only be used if reliable transaction timestamp data is available in the synthetic dataset.

---

# 18. Transaction Pattern Anomaly

The system can analyze combinations of features rather than individual values.

Example:

```text
New Payee
+
Very High Amount
+
Unusual Frequency
+
Unusual Cheque Sequence
```

Individually, each signal may not prove fraud.

Together, they represent a stronger anomaly.

```text
Multiple anomalies
        │
        ▼
Higher anomaly score
```

---

# 19. Rule-Based Anomaly Detection

The initial implementation should use understandable rules.

Example:

### Rule A1 — High Amount

```text
IF cheque_amount > historical_threshold
THEN amount_anomaly = TRUE
```

### Rule A2 — Unusual Frequency

```text
IF recent_transaction_count > historical_threshold
THEN frequency_anomaly = TRUE
```

### Rule A3 — New Payee

```text
IF payee NOT IN known_payees
THEN payee_anomaly = TRUE
```

### Rule A4 — Sequence Anomaly

```text
IF cheque_number deviates significantly
FROM expected sequence
THEN sequence_anomaly = TRUE
```

---

# 20. Anomaly Score

Each detected anomaly can contribute to an overall score.

Example:

| Indicator           |  Weight |
| ------------------- | ------: |
| Amount anomaly      |      30 |
| Frequency anomaly   |      20 |
| Payee anomaly       |      20 |
| Sequence anomaly    |      10 |
| Timing anomaly      |      10 |
| Transaction pattern |      10 |
| **Maximum**         | **100** |

Example:

```text
Amount Anomaly     → 30
Payee Anomaly      → 20
Frequency Anomaly  → 20
Sequence Anomaly   → 10
```

Total:

```text
Anomaly Score = 80/100
```

The weights are configurable and must be validated experimentally.

---

# 21. Anomaly Risk Classification

Initial prototype classification:

|  Score | Risk     |
| -----: | -------- |
|   0–24 | LOW      |
|  25–49 | MEDIUM   |
|  50–74 | HIGH     |
| 75–100 | CRITICAL |

These are project-level prototype thresholds and should be calibrated during testing.

---

# 22. Example — Normal Transaction

Historical behavior:

```text
Average amount: ₹10,000
Typical range: ₹5,000–₹20,000
Known payee: ABC Stores
Frequency: 3 cheques/month
```

New cheque:

```text
Amount: ₹12,000
Payee: ABC Stores
Frequency: Normal
```

Result:

```text
Amount Anomaly     = NO
Payee Anomaly      = NO
Frequency Anomaly  = NO
Sequence Anomaly   = NO

Anomaly Score      = LOW
```

---

# 23. Example — Suspicious Transaction

Historical:

```text
Average amount = ₹12,000
Typical frequency = 3/month
Known payees = ABC Stores, XYZ Traders
```

New cheque:

```text
Amount = ₹4,00,000
Payee = Unknown Company
Recent cheques = 10
```

Possible output:

```text
Amount Anomaly     = HIGH
Payee Anomaly      = HIGH
Frequency Anomaly  = HIGH

Anomaly Score      = 85
Risk Level         = CRITICAL
```

The system should then pass the result to the Fraud Detection Engine.

---

# 24. Machine Learning-Based Anomaly Detection

After implementing the rule-based baseline, the system can support ML-based anomaly detection.

Potential algorithms include:

* Isolation Forest
* Local Outlier Factor
* One-Class SVM
* Autoencoder

For this project, **Isolation Forest** is a suitable candidate for an initial ML implementation because it is designed for identifying unusual observations in datasets.

---

# 25. Isolation Forest

Isolation Forest works by attempting to isolate unusual observations.

Conceptually:

```text
Normal transactions
      │
      ├── Similar behavior
      ├── Similar amounts
      └── Similar frequency

Anomalous transaction
      │
      └── Easily isolated
```

Example feature set:

```text
amount
transaction_frequency
days_since_previous_cheque
payee_frequency
cheque_sequence_difference
```

The model generates an anomaly score.

---

# 26. ML Feature Vector

For each cheque:

```text
X = [
    amount,
    normalized_amount,
    transaction_frequency,
    payee_frequency,
    days_since_previous_cheque,
    cheque_sequence_difference
]
```

Example:

```text
X =
[
  450000,
  18.4,
  12,
  1,
  0,
  862
]
```

The anomaly model evaluates this vector.

---

# 27. Hybrid Approach

The recommended design for this project is:

```text
          Historical Data
                 │
        ┌────────┴────────┐
        ▼                 ▼
   Rule Engine       ML Model
        │                 │
        ▼                 ▼
 Rule Anomaly Score   ML Score
        │                 │
        └────────┬────────┘
                 ▼
          Combined Score
                 │
                 ▼
          Anomaly Risk
```

This gives the system both:

* Explainability from rules
* Pattern detection from ML

---

# 28. Why Hybrid Detection Is Preferred

A purely ML-based approach can be difficult to explain.

For example:

```text
"Model says this transaction is anomalous."
```

does not clearly explain why.

A rule-based system can say:

```text
Amount is 6.2× the account's historical average.
Payee has not appeared previously.
12 cheques were issued within 48 hours.
```

This is much more useful for manual reviewers and demonstrations.

Therefore, the MVP should prioritize **explainable anomaly rules**, with ML as an additional layer.

---

# 29. Explainable Anomaly Reasons

Every anomaly should have a reason.

Example:

```json
{
  "anomaly_type": "AMOUNT_ANOMALY",
  "severity": "HIGH",
  "reason": "Cheque amount is significantly higher than the account's historical average.",
  "historical_average": 12500,
  "current_amount": 450000
}
```

Multiple reasons can be returned.

```json
{
  "anomalies": [
    "AMOUNT_ANOMALY",
    "NEW_PAYEE",
    "HIGH_TRANSACTION_FREQUENCY"
  ]
}
```

---

# 30. Complete Anomaly Detection Output

Example:

```json
{
  "cheque_id": "CHK-2026-000153",
  "account_number": "1002345678",
  "anomaly_score": 82,
  "risk_level": "CRITICAL",
  "anomalies": [
    {
      "type": "AMOUNT_ANOMALY",
      "severity": "HIGH"
    },
    {
      "type": "NEW_PAYEE",
      "severity": "MEDIUM"
    },
    {
      "type": "FREQUENCY_ANOMALY",
      "severity": "HIGH"
    }
  ],
  "recommendation": "MANUAL_REVIEW"
}
```

---

# 31. Integration with Fraud Detection

Anomaly detection is one component of the larger fraud detection system.

```text
                    Fraud Detection Engine
                              ▲
                              │
          ┌───────────────────┼──────────────────┐
          │                   │                  │
          │                   │                  │
   Signature Analysis   Duplicate Detection   Anomaly Detection
          │                   │                  │
          │                   │                  │
     Signature Risk      Duplicate Risk      Anomaly Risk
```

The engine combines these signals.

---

# 32. Example Combined Fraud Analysis

Suppose:

```text
Signature Risk       = LOW
Duplicate Risk       = NONE
Anomaly Risk         = HIGH
Tampering Risk       = LOW
Account Validation   = PASS
```

The final fraud risk may be:

```text
MEDIUM
```

and the cheque may be sent to:

```text
MANUAL REVIEW
```

This demonstrates why anomaly detection should not independently reject a cheque.

---

# 33. Integration with Decision Engine

The flow is:

```text
Anomaly Detection
       │
       ▼
Anomaly Score
       │
       ▼
Fraud Detection Engine
       │
       ▼
Overall Fraud Risk
       │
       ▼
Decision Engine
       │
 ┌─────┼──────┐
 ▼     ▼      ▼
APPROVE REVIEW REJECT
```

---

# 34. Database Requirements

The system should maintain historical data required for anomaly analysis.

Suggested tables:

```text
accounts
customers
cheques
transactions
payees
anomaly_results
```

### `anomaly_results`

| Field            | Description                 |
| ---------------- | --------------------------- |
| `anomaly_id`     | Unique anomaly record       |
| `cheque_id`      | Related cheque              |
| `account_number` | Related account             |
| `anomaly_score`  | Overall anomaly score       |
| `risk_level`     | Risk classification         |
| `anomaly_types`  | Detected anomaly categories |
| `reasons`        | Explanation                 |
| `model_version`  | Model used                  |
| `created_at`     | Detection timestamp         |

---

# 35. Suggested Backend Structure

```text
apps/
└── backend/
    └── anomaly_detection/
        ├── anomaly_service.py
        ├── feature_engineering.py
        ├── rule_engine.py
        ├── statistical_detector.py
        ├── ml_detector.py
        ├── anomaly_scorer.py
        └── anomaly_repository.py
```

### Responsibilities

| File                      | Responsibility                   |
| ------------------------- | -------------------------------- |
| `anomaly_service.py`      | Coordinates anomaly detection    |
| `feature_engineering.py`  | Creates model features           |
| `rule_engine.py`          | Applies business rules           |
| `statistical_detector.py` | Performs statistical analysis    |
| `ml_detector.py`          | Runs ML anomaly model            |
| `anomaly_scorer.py`       | Combines anomaly signals         |
| `anomaly_repository.py`   | Stores/retrieves anomaly results |

---

# 36. API Specification

### Endpoint

```http
POST /api/v1/anomaly/analyze
```

### Request

```json
{
  "cheque_id": "CHK-2026-000153",
  "account_number": "1002345678",
  "amount": 450000,
  "cheque_date": "2026-08-20",
  "payee_name": "Unknown Company"
}
```

### Response

```json
{
  "cheque_id": "CHK-2026-000153",
  "anomaly_score": 82,
  "risk_level": "CRITICAL",
  "anomalies": [
    "AMOUNT_ANOMALY",
    "NEW_PAYEE",
    "FREQUENCY_ANOMALY"
  ],
  "recommendation": "MANUAL_REVIEW"
}
```

---

# 37. Error Handling

The module should handle:

### Insufficient History

```text
INSUFFICIENT_HISTORICAL_DATA
```

For a newly created account, there may not be enough historical transactions to establish a reliable baseline.

The system should avoid incorrectly declaring an anomaly.

---

### Missing Amount

```text
AMOUNT_DATA_UNAVAILABLE
```

---

### Missing Payee

```text
PAYEE_DATA_UNAVAILABLE
```

---

### Model Failure

```text
ANOMALY_MODEL_ERROR
```

---

### Invalid Transaction Data

```text
INVALID_TRANSACTION_DATA
```

These cases should be logged and handled safely.

---

# 38. Cold-Start Problem

A new account may have little or no transaction history.

Example:

```text
Account created yesterday
       │
       ▼
No historical cheque data
       │
       ▼
Cannot establish normal behavior
```

The system should therefore use:

* Rule-based validation
* Population-level baseline where appropriate
* Minimum-history requirements
* Manual review when necessary

It should **not automatically classify every transaction as anomalous**.

---

# 39. Testing Dataset

We should create synthetic data containing:

### Normal transactions

```text
Normal amounts
Normal payees
Normal frequency
Normal cheque sequence
```

### Amount anomalies

```text
Extremely high amounts
Extremely low amounts
```

### Frequency anomalies

```text
Many transactions within a short period
```

### Payee anomalies

```text
Previously unseen payees
```

### Sequence anomalies

```text
Unexpected cheque number gaps
```

### Combined anomalies

```text
High amount
+
New payee
+
High frequency
```

This will allow us to demonstrate anomaly detection properly.

---

# 40. Example Synthetic Dataset

```csv
transaction_id,account_number,amount,payee,days_since_previous_cheque
TXN001,1002345678,8500,ABC Stores,4
TXN002,1002345678,12000,XYZ Traders,6
TXN003,1002345678,9500,ABC Stores,7
TXN004,1002345678,11000,DEF Services,5
TXN005,1002345678,13500,ABC Stores,8
TXN006,1002345678,450000,Unknown Company,0
```

The final transaction should be detected as anomalous.

---

# 41. Evaluation Metrics

The module should be evaluated using:

### Detection Precision

Percentage of detected anomalies that are actually anomalies according to the synthetic ground truth.

### Detection Recall

Percentage of actual anomalies successfully detected.

### F1 Score

Balance between precision and recall.

### False Positive Rate

Percentage of normal transactions incorrectly flagged.

### False Negative Rate

Percentage of anomalous transactions missed.

### Processing Time

Time required to calculate anomaly indicators.

---

# 42. Final Architecture

```text
                         NEW CHEQUE
                              │
                              ▼
                     Extracted Data
                              │
                              ▼
                    Historical Account Data
                              │
                              ▼
                    Feature Engineering
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
       Rule-Based Analysis              Statistical / ML
              │                                │
              │                         Isolation Forest
              │                                │
              └───────────────┬────────────────┘
                              ▼
                     Anomaly Score
                              │
                              ▼
                   Risk Classification
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
                LOW        MEDIUM       HIGH/CRITICAL
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                    Fraud Detection Engine
                              │
                              ▼
                       Overall Risk Score
                              │
                              ▼
                       Decision Engine
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              APPROVE       REVIEW       REJECT
```

## Summary

The **Anomaly Detection Module** identifies cheque transactions that deviate from the normal behavior established using the project's **synthetic/mock banking data**. It analyzes amount, transaction frequency, payee behavior, cheque sequence, timing, and combined transaction patterns.

For the **MVP**, the recommended implementation is an **explainable hybrid approach**:

```text
Rule-Based Detection
        +
Statistical Detection
        +
Optional ML Detection
        ↓
Combined Anomaly Score
```

The module will **not independently declare a cheque fraudulent**. It generates evidence and an anomaly score that are passed to the **Fraud Detection Engine**, where they are combined with **signature analysis, duplicate detection, tampering analysis, validation results, and other fraud indicators** before the final **Approve / Review / Reject** decision.

All anomaly results should be recorded in the audit trail with the relevant reason, score, timestamp, and model/rule version.
