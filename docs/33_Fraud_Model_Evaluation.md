# Fraud Model Evaluation

# Fraud Model Evaluation

## 1. Introduction

The **Fraud Model Evaluation** module defines how the fraud-detection component of the AI-Powered Cheque Scanning, Validation & Fraud Detection System will be tested and evaluated.

The purpose of the fraud-detection system is to identify cheques that may contain fraudulent or suspicious characteristics and classify them appropriately for further processing.

The system may use a combination of:

* Rule-based fraud detection
* Image-based analysis
* Signature analysis
* Duplicate detection
* Anomaly detection
* Statistical/ML-based fraud classification
* Risk scoring

The primary project target is:

> **Fraud detection accuracy ≥ 90%**

This is a **target**, not an assumed result. The actual performance will be calculated using the project's own labeled synthetic test dataset.

---

# 2. Evaluation Objectives

The objectives of fraud-model evaluation are to:

1. Determine how accurately the system identifies fraudulent and legitimate cheques.
2. Measure false positives and false negatives.
3. Evaluate the effectiveness of individual fraud indicators.
4. Measure precision, recall, and F1-score.
5. Evaluate the model using a controlled test dataset.
6. Test the model on different types of suspicious cheque conditions.
7. Verify that fraud scores are correctly generated.
8. Verify that fraud results are correctly passed to the Risk Scoring module.
9. Verify that fraud results influence the Decision Engine correctly.
10. Ensure that suspicious cases can be routed to manual review.

---

# 3. Fraud Detection Architecture

The fraud evaluation follows the project's fraud-processing pipeline:

```text
Cheque Image
      ↓
OCR + Extracted Data
      ↓
Validation Results
      ↓
Fraud Indicators
 ┌────┼────┬────┬────┬────┐
 ↓    ↓    ↓    ↓    ↓
Tampering
Signature
Duplicate
Anomaly
Pattern Analysis
 └────┴────┴────┴────┴────┘
             ↓
       Fraud Model / Rules
             ↓
       Fraud Probability
             ↓
        Risk Score
             ↓
     Decision Engine
             ↓
 APPROVE / REVIEW / REJECT
```

---

# 4. Fraud Categories

The test dataset should contain multiple fraud/suspicion categories.

### Category 1 — Normal Cheque

A valid cheque with:

* Valid account
* Valid cheque number
* Matching payee
* Valid date
* Valid signature
* No duplicate
* No unusual characteristics

Expected:

```text
FRAUD = NO
```

---

### Category 2 — Duplicate Cheque

A cheque that has already been processed.

Expected:

```text
Duplicate = TRUE
```

The final decision may be:

```text
REVIEW / REJECT
```

depending on the configured Decision Engine rules.

---

### Category 3 — Signature Mismatch

The cheque contains a signature that does not sufficiently match the expected signature pattern.

Expected:

```text
Signature Risk = HIGH
```

This would normally result in:

```text
REVIEW
```

rather than automatic approval.

---

### Category 4 — Image Tampering

The cheque image contains suspicious modifications.

Examples:

* Altered amount
* Modified payee
* Modified cheque number
* Edited image region
* Copy-paste artifacts

Expected:

```text
Tampering Indicator = TRUE
```

---

### Category 5 — Amount Anomaly

The cheque amount is significantly unusual compared with the account's historical/mock transaction pattern.

Example:

```text
Typical range:
₹500 – ₹25,000

Observed:
₹4,50,000
```

Expected:

```text
Amount Anomaly = TRUE
```

The threshold will be determined using the project's mock data/configuration.

---

### Category 6 — Payee Mismatch

The extracted payee does not match the expected banking record or configured validation rule.

Expected:

```text
Payee Match = FAIL
```

This should contribute to the overall risk assessment.

---

# 5. Fraud Dataset

The project will create its own controlled dataset.

Recommended structure:

```text
data/
├── sample_cheques/
│   ├── normal/
│   ├── suspicious/
│   └── fraudulent/
│
└── test_data/
    ├── fraud_labels.csv
    ├── fraud_predictions.csv
    └── fraud_evaluation_results.csv
```

The dataset must contain both legitimate and suspicious/fraudulent examples.

---

# 6. Fraud Ground-Truth Dataset

Each test cheque will have a known classification.

Example:

```csv
cheque_id,label,fraud_type
CHK001,0,NONE
CHK002,0,NONE
CHK003,1,DUPLICATE
CHK004,1,SIGNATURE_MISMATCH
CHK005,0,NONE
CHK006,1,IMAGE_TAMPERING
```

Where:

```text
0 = Legitimate
1 = Fraudulent/Suspicious
```

The exact labeling policy should be defined before evaluation.

For cases that are genuinely ambiguous, the dataset should distinguish between:

```text
LEGITIMATE
SUSPICIOUS
CONFIRMED_FRAUD
```

if the implementation supports a three-class model.

---

# 7. Dataset Split

If an ML model is used, the dataset should be divided into:

```text
Dataset
   │
   ├── Training Set
   │
   ├── Validation Set
   │
   └── Test Set
```

A possible split is:

```text
70% Training
15% Validation
15% Testing
```

The exact split may be changed depending on the final dataset size.

The **test dataset must not be used for model training**.

This prevents the evaluation from being artificially inflated.

---

# 8. Data Leakage Prevention

Fraud detection evaluation must avoid data leakage.

For example, if the same cheque image or near-identical version appears in both training and testing datasets, the measured performance may not represent real-world performance.

Therefore:

* Duplicate images should not cross dataset splits.
* Synthetic variants of the same cheque should be carefully controlled.
* Ground-truth labels should not be included as model input.
* Test data should remain isolated until final evaluation.

---

# 9. Fraud Detection Inputs

The fraud model may receive features from several system modules.

Possible inputs include:

```text
OCR Fields
    ↓
Validation Results
    ↓
Signature Features
    ↓
Duplicate Indicators
    ↓
Image/Tampering Features
    ↓
Transaction/Account Features
    ↓
Anomaly Indicators
```

Example feature set:

| Feature         | Example |
| --------------- | ------- |
| Account Active  | TRUE    |
| Payee Match     | TRUE    |
| Duplicate       | FALSE   |
| Signature Match | TRUE    |
| Amount Anomaly  | FALSE   |
| Image Tampering | FALSE   |
| OCR Confidence  | 0.98    |
| Cheque Age      | Valid   |

These features can be used by the rule engine and/or ML model.

---

# 10. Rule-Based Fraud Evaluation

Before evaluating an ML model, individual fraud rules should be tested independently.

Example:

```text
IF duplicate = TRUE
THEN duplicate_risk = HIGH
```

Another:

```text
IF signature_match = FALSE
THEN signature_risk = HIGH
```

Another:

```text
IF image_tampering = TRUE
THEN tampering_risk = HIGH
```

This allows the project team to identify whether an error originates from:

* Input data
* Individual rule
* ML model
* Risk scoring
* Decision Engine

---

# 11. Fraud Model Output

The fraud model should produce a standardized output.

Example:

```json
{
  "cheque_id": "CHK003",
  "fraud_probability": 0.87,
  "fraud_prediction": 1,
  "risk_level": "HIGH"
}
```

Where:

```text
fraud_probability
        ↓
Risk Scoring
        ↓
Decision Engine
```

The probability should be treated as a model output and not automatically interpreted as a guaranteed percentage chance of actual fraud unless the model has been properly calibrated.

---

# 12. Confusion Matrix

The primary evaluation tool will be the **confusion matrix**.

```text
                         Actual
                    Legitimate  Fraud
                 ┌────────────┬──────────┐
Predicted        │            │          │
Legitimate       │    TN      │    FN    │
                 ├────────────┼──────────┤
Fraud            │    FP      │    TP    │
                 └────────────┴──────────┘
```

Where:

### True Positive — TP

Fraudulent cheque correctly identified as fraud.

### True Negative — TN

Legitimate cheque correctly identified as legitimate.

### False Positive — FP

Legitimate cheque incorrectly flagged as fraud.

### False Negative — FN

Fraudulent cheque incorrectly classified as legitimate.

For cheque fraud detection, **false negatives are particularly important** because they represent potentially fraudulent cheques that were not detected.

---

# 13. Accuracy

Accuracy measures the overall percentage of correctly classified cheques.

```text
Accuracy =
(TP + TN)
────────────────────── × 100
TP + TN + FP + FN
```

Example:

```text
TP = 40
TN = 50
FP = 5
FN = 5

Accuracy =
(40 + 50) / 100

= 90%
```

The example is illustrative only.

The project target is:

> **Fraud detection accuracy ≥ 90%**

---

# 14. Precision

Precision measures how many cheques flagged as fraudulent were actually fraudulent.

```text
Precision =
TP
────────── × 100
TP + FP
```

High precision reduces unnecessary manual-review cases.

Example:

If the system flags 50 cheques as fraudulent and 45 are actually fraudulent:

```text
Precision = 45 / 50 × 100
          = 90%
```

---

# 15. Recall

Recall measures how many actual fraudulent cheques were successfully detected.

```text
Recall =
TP
────────── × 100
TP + FN
```

Recall is especially important in fraud detection because a low recall means the system is allowing fraudulent cheques to pass undetected.

Example:

```text
Actual fraudulent cheques = 50
Detected fraudulent cheques = 45

Recall = 45 / 50 × 100
       = 90%
```

---

# 16. F1-Score

F1-score combines precision and recall.

```text
F1 =
2 × Precision × Recall
────────────────────────
Precision + Recall
```

A higher F1-score indicates a better balance between detecting fraud and avoiding unnecessary false alerts.

---

# 17. ROC-AUC

If the fraud model produces probabilities, **ROC-AUC** can be used to evaluate its ability to distinguish between legitimate and fraudulent samples across different decision thresholds.

The ROC curve plots:

```text
True Positive Rate
        vs.
False Positive Rate
```

AUC represents the area under this curve.

This metric is useful when the model's classification threshold may be adjusted depending on the desired balance between fraud detection and false alerts.

---

# 18. Precision-Recall Analysis

Because fraud datasets can become imbalanced, precision-recall analysis should also be considered.

For example:

```text
Normal cheques = 950
Fraudulent cheques = 50
```

A model could achieve high accuracy simply by predicting most cheques as legitimate.

Therefore, accuracy alone should **not** be used to judge the fraud model.

The evaluation should consider:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion Matrix
* ROC-AUC where applicable
* Precision-Recall behavior

---

# 19. Class Imbalance

Fraud cases are typically fewer than legitimate cases.

The project's synthetic dataset should therefore be monitored for class imbalance.

Example:

```text
Legitimate = 80%
Suspicious/Fraud = 20%
```

If the dataset becomes highly imbalanced, suitable techniques may be evaluated, such as:

* Class weighting
* Oversampling
* Undersampling
* Threshold adjustment

The selected approach should be documented based on the actual dataset.

---

# 20. Fraud Test Cases

| Test ID | Scenario                     | Expected Result    |
| ------- | ---------------------------- | ------------------ |
| FRA-001 | Normal cheque                | Legitimate         |
| FRA-002 | Duplicate cheque             | Fraud indicator    |
| FRA-003 | Signature mismatch           | Suspicious         |
| FRA-004 | Image tampering              | Suspicious/Fraud   |
| FRA-005 | Unusual amount               | Anomaly            |
| FRA-006 | Payee mismatch               | Suspicious         |
| FRA-007 | Closed account               | Validation failure |
| FRA-008 | Multiple fraud indicators    | High risk          |
| FRA-009 | Clear legitimate cheque      | Low risk           |
| FRA-010 | Low-confidence OCR + anomaly | Review             |

---

# 21. Fraud Indicator Evaluation

Each fraud indicator should also be evaluated individually.

Example:

| Indicator          | Correctly Detected | Missed | False Alerts |
| ------------------ | -----------------: | -----: | -----------: |
| Duplicate          |                  — |      — |            — |
| Signature mismatch |                  — |      — |            — |
| Image tampering    |                  — |      — |            — |
| Amount anomaly     |                  — |      — |            — |
| Payee mismatch     |                  — |      — |            — |

The actual values will be populated after the test dataset is processed.

---

# 22. Risk Score Evaluation

Fraud-model output will be passed to the Risk Scoring module.

Example:

```text
Fraud Probability
       +
Validation Results
       +
Fraud Indicators
       ↓
Risk Scoring
       ↓
0 – 100 Risk Score
```

The evaluation must verify that higher-risk cases receive appropriately higher risk scores according to the configured scoring rules.

Example:

```text
Normal cheque:
Risk Score → Low

One suspicious indicator:
Risk Score → Medium

Multiple strong indicators:
Risk Score → High
```

---

# 23. Decision Engine Evaluation

The fraud model should not operate independently from the final decision.

Example:

```text
Fraud Model
    ↓
High Risk
    ↓
Decision Engine
    ↓
REVIEW
```

A severe validation failure may instead result in:

```text
Validation Failure
       ↓
Decision Engine
       ↓
REJECT
```

The test must verify that fraud results are correctly interpreted by the Decision Engine.

---

# 24. False Positive Analysis

False positives occur when legitimate cheques are flagged as suspicious.

Example:

```text
Actual:
LEGITIMATE

System:
FRAUD

Result:
FALSE POSITIVE
```

A high false-positive rate can increase manual verification effort.

Therefore, false positives should be tracked because the project has a goal of reducing manual verification effort by at least **50%**.

---

# 25. False Negative Analysis

False negatives occur when fraudulent cheques are classified as legitimate.

Example:

```text
Actual:
FRAUD

System:
LEGITIMATE

Result:
FALSE NEGATIVE
```

False negatives are particularly important because they represent potentially undetected fraud.

Each false negative should be investigated to determine the cause.

Possible causes:

* Poor image quality
* OCR error
* Weak fraud feature
* Incorrect threshold
* Missing training examples
* Model limitation
* Rule configuration issue

---

# 26. Threshold Evaluation

If the model generates a fraud probability, different thresholds can be tested.

Example:

```text
Probability < T1
      ↓
Legitimate

T1 ≤ Probability < T2
      ↓
Review

Probability ≥ T2
      ↓
High Risk
```

The thresholds should be selected based on testing results and the project's desired balance between:

* Fraud detection
* False positives
* Manual review workload

The chosen thresholds must be documented in the final configuration.

---

# 27. Explainability

The system should provide understandable reasons when a cheque is flagged.

Example:

```text
Decision: REVIEW

Reasons:
• Signature mismatch detected
• Amount anomaly detected
• OCR confidence below configured threshold

Risk Score: 72
```

This is important because a reviewer should be able to understand **why the system considers the cheque suspicious**.

---

# 28. Model Robustness Testing

The fraud model should be tested against variations in cheque images and input data.

Examples:

* Different image resolutions
* Slight rotation
* Different lighting
* Compression
* Background noise
* Minor distortions
* Different cheque layouts

The purpose is to determine whether performance remains acceptable when input conditions change.

---

# 29. Model Comparison

If multiple fraud approaches are implemented, they can be compared.

For example:

| Model/Approach       | Accuracy | Precision | Recall | F1 |
| -------------------- | -------: | --------: | -----: | -: |
| Rule-Based           |        — |         — |      — |  — |
| Logistic Regression  |        — |         — |      — |  — |
| Random Forest        |        — |         — |      — |  — |
| Other Selected Model |        — |         — |      — |  — |

Only models actually implemented should appear in the final evaluation.

The best model should not be selected based on accuracy alone.

---

# 30. Evaluation Procedure

The complete fraud-model evaluation will follow these steps:

### Step 1 — Create Synthetic Dataset

Generate normal and suspicious/fraudulent cheque samples.

### Step 2 — Assign Ground Truth

Label every sample according to predefined rules.

### Step 3 — Prepare Features

Generate OCR, validation, image, signature, duplicate, and anomaly features as applicable.

### Step 4 — Train Model

If an ML model is used, train it using the training dataset.

### Step 5 — Tune/Validate

Use the validation dataset to select appropriate model parameters and decision thresholds.

### Step 6 — Freeze the Model

Finalize the selected model and configuration before testing.

### Step 7 — Run Test Dataset

Evaluate the frozen model on unseen test data.

### Step 8 — Generate Predictions

Store predicted class and fraud probability where applicable.

### Step 9 — Calculate Metrics

Calculate:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix
* ROC-AUC where applicable

### Step 10 — Analyze Errors

Investigate false positives and false negatives.

### Step 11 — Evaluate Downstream Decisions

Verify Risk Scoring and Decision Engine behavior.

### Step 12 — Record Results

Store final evaluation results in the project documentation.

---

# 31. Evaluation Results File

The project can maintain:

```text
data/test_data/
├── fraud_labels.csv
├── fraud_predictions.csv
└── fraud_evaluation_results.csv
```

Example `fraud_predictions.csv`:

```csv
cheque_id,actual_label,predicted_label,fraud_probability
CHK001,0,0,0.08
CHK002,1,1,0.91
CHK003,0,1,0.67
CHK004,1,1,0.84
```

This makes the evaluation reproducible.

---

# 32. Final Evaluation Report

The final report should contain:

### Dataset

* Number of legitimate samples
* Number of suspicious/fraud samples
* Number of test samples
* Dataset split

### Model

* Selected model/approach
* Features used
* Configuration
* Decision threshold

### Metrics

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix
* ROC-AUC where applicable

### Error Analysis

* False positives
* False negatives
* Common failure conditions

### Performance

* Fraud-analysis processing time
* End-to-end processing time

---

# 33. Target vs Actual Result

The documentation must clearly distinguish between project requirements and measured results.

| Metric                   |                    Project Target |  Actual Result |
| ------------------------ | --------------------------------: | -------------: |
| Fraud Detection Accuracy |                             ≥ 90% | To be measured |
| Precision                | To be established through testing | To be measured |
| Recall                   | To be established through testing | To be measured |
| F1-Score                 | To be established through testing | To be measured |
| False Positive Rate      |                   To be minimized | To be measured |
| False Negative Rate      |                   To be minimized | To be measured |

We should **not enter fabricated values** into this table.

---

# 34. Fraud Model Success Criteria

The fraud-detection evaluation will be considered successful when:

* The fraud dataset contains clearly defined ground-truth labels.
* Training and testing data are properly separated when ML is used.
* No significant data leakage is present.
* Fraud predictions can be reproduced.
* Confusion matrix is generated.
* Accuracy is measured.
* Precision, recall, and F1-score are measured.
* False positives and false negatives are analyzed.
* Fraud indicators are tested individually.
* Risk scores are generated correctly.
* Decision Engine integration works correctly.
* The actual fraud-detection accuracy is compared against the **≥90% project target**.
* Results are documented using the actual test data.

---

# 35. Complete Fraud Evaluation Workflow

```text
                 Synthetic Cheque Dataset
                           ↓
                    Ground-Truth Labels
                           ↓
                    Feature Generation
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       Rule-Based Checks           ML Fraud Model
              ↓                         ↓
              └────────────┬────────────┘
                           ↓
                    Fraud Prediction
                           ↓
                Probability / Indicators
                           ↓
                    Risk Scoring
                           ↓
                    Decision Engine
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           APPROVE       REVIEW       REJECT
                           ↓
                    Manual Review
                           ↓
                     Audit Trail
                           ↓
                   Evaluation Report
```

---

# 36. Summary

The **Fraud Model Evaluation** module provides a measurable framework for determining whether the cheque fraud-detection system performs effectively.

The evaluation will use **synthetic cheque images, mock banking records, and labeled fraud test data created specifically for this project**. The model will be evaluated using a combination of **confusion matrix, accuracy, precision, recall, F1-score, and ROC-AUC where applicable**.

Special attention will be given to **false negatives**, because undetected fraudulent cheques represent a significant risk, while **false positives** will also be monitored because excessive false alerts increase manual-review workload.

The final fraud-detection result will be compared against the project's target of **≥90% accuracy**, but the actual value will only be reported after the model has been implemented and evaluated on unseen test data.

