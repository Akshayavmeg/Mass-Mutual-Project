# Signature Analysis

# 18. Signature Analysis

## 1. Introduction

The **Signature Analysis Module** is responsible for analyzing the signature present on a cheque and determining whether it is sufficiently similar to the **reference signature associated with the account**.

Signature analysis is an important component of the cheque fraud detection pipeline because unauthorized cheques may contain:

* A completely different signature
* A modified signature
* A forged signature
* A copied signature
* A signature with unusual characteristics

The module does **not independently declare a signature as legally forged**. Instead, it produces a **signature similarity score and risk indicator**, which are combined with other fraud indicators by the Fraud Detection Engine.

```text
Cheque Image
     │
     ▼
Signature Region Detection
     │
     ▼
Signature Extraction
     │
     ▼
Image Preprocessing
     │
     ▼
Feature Extraction
     │
     ▼
Signature Comparison
     │
     ▼
Similarity Score
     │
     ▼
Signature Risk Level
     │
     ▼
Fraud Detection Engine
```

---

# 2. Objectives

The objectives of the Signature Analysis Module are:

1. Identify the signature region on the cheque.
2. Extract the signature image from the cheque.
3. Preprocess the signature image for analysis.
4. Compare the extracted signature with the reference signature.
5. Generate a signature similarity score.
6. Identify potentially suspicious signature differences.
7. Provide an interpretable signature risk indicator.
8. Pass the analysis result to the Fraud Detection Engine.
9. Maintain signature-analysis results for audit purposes.
10. Support future ML-based signature verification.

---

# 3. Signature Analysis in the Overall System

Signature analysis is one of several fraud indicators.

```text
                    Cheque
                       │
                       ▼
                Image Processing
                       │
                       ▼
               Signature Region
                       │
                       ▼
              Signature Analysis
                       │
                       ▼
              Similarity Score
                       │
                       ▼
             Fraud Detection Engine
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Signature       Duplicate        Tampering
     Risk             Risk             Risk
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  Risk Score
```

This prevents the system from relying on the signature alone.

---

# 4. Input to the Module

The module receives:

### From the Cheque Image

* Original cheque image
* Image quality information
* Signature region coordinates, if already detected

### From Banking Records

* Account number
* Reference signature
* Signature image or signature template
* Account status

### From OCR/Data Extraction

* Extracted account number
* Cheque identifier

Example:

```json
{
  "cheque_id": "CHK-2026-000125",
  "account_number": "1002345678",
  "signature_region": {
    "x": 820,
    "y": 430,
    "width": 300,
    "height": 100
  },
  "reference_signature_id": "SIG-1002345678"
}
```

---

# 5. Signature Region Identification

The first step is to identify the signature area.

A cheque normally contains a designated signature section.

The system can use:

* Fixed cheque layout coordinates
* Template-based detection
* Computer vision
* Object detection
* Region-of-interest detection

For the MVP, **template-based signature-region extraction** can be used if all sample cheques follow a controlled layout.

For variable cheque layouts, a computer-vision/object-detection approach can be added later.

---

# 6. Signature Region Extraction

After locating the signature area, the system crops the region.

```text
Original Cheque
┌──────────────────────────────────────┐
│                                      │
│     Payee: John Doe                  │
│                                      │
│     Amount: ₹25,000                  │
│                                      │
│                         __________   │
│                        / Signature/  │
│                       /____________  │
│                                      │
└──────────────────────────────────────┘
                              │
                              ▼
                     Signature Crop
```

The extracted region is passed to preprocessing.

---

# 7. Image Preprocessing

The signature image may contain:

* Background noise
* Printed lines
* Stamps
* Scanning artifacts
* Low contrast
* Shadows
* Compression artifacts

Therefore, preprocessing is required.

Typical operations include:

1. Grayscale conversion
2. Noise removal
3. Contrast enhancement
4. Thresholding
5. Background removal
6. Resizing
7. Normalization

Example:

```text
Original Signature
       ↓
Grayscale
       ↓
Noise Removal
       ↓
Thresholding
       ↓
Background Removal
       ↓
Normalized Signature
```

---

# 8. Signature Segmentation

The objective of segmentation is to separate the actual handwritten signature from the background.

Example:

```text
Before:

┌──────────────────────┐
│      background      │
│    ///////           │
│       JohnSignature  │
│      //////          │
└──────────────────────┘

After:

┌──────────────────────┐
│                      │
│      Signature       │
│                      │
└──────────────────────┘
```

This improves comparison accuracy.

---

# 9. Reference Signature

A reference signature is required for comparison.

For the project's prototype, reference signatures will be stored in the **mock banking dataset**.

Example:

```text
data/
└── mock_banking_data/
    └── reference_signatures/
        ├── SIG-100001.png
        ├── SIG-100002.png
        └── SIG-100003.png
```

Each reference signature should be linked to a synthetic account.

Example:

```json
{
  "account_number": "1002345678",
  "signature_id": "SIG-1002345678",
  "signature_file": "SIG-1002345678.png"
}
```

**No real customer signatures should be used in the project dataset.**

---

# 10. Signature Comparison

The extracted cheque signature is compared with the reference signature.

```text
                 ┌─────────────────┐
                 │ Cheque Signature│
                 └────────┬────────┘
                          │
                          ▼
                  Feature Extraction
                          │
                          ▼
                  Signature Features
                          │
                          │
                          ▼
                 Similarity Algorithm
                          ▲
                          │
                  Reference Features
                          ▲
                          │
                 ┌────────┴────────┐
                 │Reference        │
                 │Signature        │
                 └─────────────────┘
```

---

# 11. Signature Features

Depending on the selected implementation, the system may analyze:

* Shape
* Stroke structure
* Orientation
* Width and height
* Aspect ratio
* Contour
* Edge characteristics
* Pixel distribution
* Texture
* Key points
* Embeddings

For an advanced implementation, a deep-learning model can generate a **signature embedding**.

---

# 12. Comparison Methods

The project can support different comparison approaches.

### Method 1 — Image Similarity

Compare processed signature images directly.

Possible techniques:

* Structural similarity
* Template matching
* Feature matching

### Method 2 — Feature-Based Comparison

Extract features and calculate the distance between them.

### Method 3 — Deep Learning

Generate embeddings using a neural network and compare the embeddings.

For example:

```text
Cheque Signature
       ↓
Embedding Model
       ↓
Vector A

Reference Signature
       ↓
Embedding Model
       ↓
Vector B

Vector A ↔ Vector B
       ↓
Similarity Score
```

For the MVP, a simpler feature-based approach can be implemented first, while keeping the architecture ready for a deep-learning model.

---

# 13. Similarity Score

The module produces a normalized similarity score.

```text
0.00 ───────────────────────── 1.00
 │                               │
Very different              Very similar
```

Example:

```text
0.92 → Very similar
0.81 → Similar
0.65 → Moderate similarity
0.42 → Low similarity
0.18 → Very low similarity
```

The actual threshold must be established through testing using the project's synthetic signature dataset.

---

# 14. Signature Risk Classification

The similarity score can be converted into a risk level.

Initial prototype thresholds may be:

| Similarity | Risk     | Interpretation         |
| ---------: | -------- | ---------------------- |
|     ≥ 0.85 | Low      | Strong similarity      |
|  0.70–0.84 | Medium   | Moderate concern       |
|  0.50–0.69 | High     | Significant difference |
|     < 0.50 | Critical | Very low similarity    |

These values are **prototype thresholds only**. They must be calibrated using the test dataset and should not be presented as industry-standard banking thresholds.

---

# 15. Example — Valid Signature

Reference signature:

```text
SIG-1002345678.png
```

Cheque signature:

```text
Extracted from cheque
```

Comparison:

```text
Similarity Score = 0.93
```

Result:

```text
Signature Risk = LOW
```

The result is passed to the Fraud Detection Engine.

---

# 16. Example — Suspicious Signature

Suppose:

```text
Similarity Score = 0.47
```

The system produces:

```text
Signature Risk = CRITICAL
Indicator = LOW_SIGNATURE_SIMILARITY
```

The Fraud Detection Engine then combines this with other signals.

For example:

```text
Signature Risk       → HIGH
Payee Match           → PASS
Account Validation    → PASS
Duplicate             → NO
Image Tampering       → LOW
```

The cheque may be routed to manual review rather than automatically rejected.

---

# 17. Important Design Principle

A signature mismatch should **not automatically mean fraud**.

There can be legitimate reasons for differences:

* Natural variation in handwriting
* Different writing speed
* Scanning quality
* Image rotation
* Ink differences
* Partial signature capture
* Poor image resolution

Therefore:

```text
Signature mismatch
       ≠
Confirmed fraud
```

Instead:

```text
Signature mismatch
       ↓
Fraud Risk Indicator
       ↓
Combined with other evidence
       ↓
Final Decision
```

---

# 18. Confidence Score

The module can provide both:

* Similarity score
* Analysis confidence

Example:

```json
{
  "similarity_score": 0.81,
  "confidence": 0.89,
  "risk_level": "MEDIUM"
}
```

Confidence represents how reliable the analysis is based on factors such as:

* Image quality
* Signature size
* Segmentation quality
* Reference quality
* Model confidence

It should not be confused with the probability that a signature is genuinely forged.

---

# 19. Image Quality Check

Before performing signature comparison, the system should verify whether the signature image is suitable.

Possible checks:

```text
Image Resolution
       ↓
Blur Detection
       ↓
Contrast Check
       ↓
Signature Visibility
       ↓
Background Noise
```

If the image quality is insufficient:

```text
SIGNATURE_ANALYSIS_UNRELIABLE
```

The cheque should be routed for manual review instead of being automatically approved.

---

# 20. Missing Signature

The system must detect whether a signature is present.

Example:

```text
Signature Region
       ↓
No signature detected
       ↓
SIGNATURE_MISSING
       ↓
High Risk Indicator
```

This should be recorded separately from signature mismatch.

```text
SIGNATURE_MISSING
```

is not the same as:

```text
SIGNATURE_MISMATCH
```

---

# 21. Partial Signature

Sometimes only part of a signature may be captured.

Example:

```text
Full reference signature
████████████████████

Captured signature
████████
```

The system should recognize this as a **low-quality comparison case** rather than immediately treating it as fraud.

Output:

```text
Analysis Status = INSUFFICIENT_IMAGE
```

Recommendation:

```text
MANUAL_REVIEW
```

---

# 22. Signature Tampering Indicators

The system may detect suspicious characteristics such as:

* Copy-paste artifacts
* Unusual edges
* Pixel inconsistencies
* Different background characteristics
* Signature region modification
* Unusual compression patterns

These indicators can be generated by image-processing algorithms.

Example:

```json
{
  "signature_tampering_score": 0.73
}
```

This score should be treated as an indicator rather than definitive proof of forgery.

---

# 23. Signature Analysis Output

The module should produce a structured result.

Example:

```json
{
  "cheque_id": "CHK-2026-000125",
  "account_number": "1002345678",
  "signature_present": true,
  "image_quality": "GOOD",
  "similarity_score": 0.47,
  "analysis_confidence": 0.91,
  "signature_tampering_score": 0.68,
  "risk_level": "HIGH",
  "indicator": "SIGNATURE_MISMATCH",
  "recommendation": "MANUAL_REVIEW"
}
```

---

# 24. Integration with Fraud Detection

The Signature Analysis Module passes its result to the Fraud Detection Engine.

```text
Signature Analysis
       │
       ├── Similarity Score
       ├── Confidence
       ├── Tampering Score
       └── Signature Status
                │
                ▼
       Fraud Detection Engine
                │
                ▼
          Fraud Risk Score
```

Example:

```text
Signature Similarity = 0.47
             ↓
Signature Risk = HIGH
             ↓
Fraud Risk Score increases
```

---

# 25. Integration with Decision Engine

The Signature Analysis module does **not** make the final cheque decision.

```text
Signature Analysis
        │
        ▼
Fraud Detection
        │
        ▼
Risk Score
        │
        ▼
Decision Engine
        │
   ┌────┼─────┐
   ▼    ▼     ▼
APPROVE REVIEW REJECT
```

This separation is important because a cheque may have a suspicious signature but still require human verification rather than automatic rejection.

---

# 26. Synthetic Signature Dataset

Since the project uses mock banking data, a synthetic signature dataset should be created.

Suggested structure:

```text
data/
└── test_data/
    └── signatures/
        ├── genuine/
        ├── altered/
        ├── low_quality/
        ├── missing/
        └── partial/
```

Each synthetic account can have multiple reference signatures.

Example:

```text
Account: 1002345678

Reference signatures:
SIG_001.png
SIG_002.png
SIG_003.png
```

This is useful because genuine signatures naturally vary.

---

# 27. Signature Test Categories

The test dataset should contain:

| Category          | Description                         |
| ----------------- | ----------------------------------- |
| Genuine           | Signature matches account reference |
| Genuine Variation | Same signer with natural variation  |
| Forged            | Different synthetic signature       |
| Altered           | Modified signature                  |
| Missing           | No signature                        |
| Partial           | Incomplete signature                |
| Low Quality       | Blurred/noisy signature             |
| Tampered          | Digitally modified signature        |

This allows proper evaluation of the module.

---

# 28. Multiple Reference Signatures

Using only one reference signature may cause false positives because genuine signatures naturally vary.

Therefore, the prototype can store multiple reference signatures.

```text
Account
  │
  ├── Reference Signature 1
  ├── Reference Signature 2
  └── Reference Signature 3
```

The submitted signature can be compared against all references.

Example:

```text
Similarity:

Reference 1 → 0.82
Reference 2 → 0.91
Reference 3 → 0.86
```

The system may use the highest or an appropriately aggregated similarity score, depending on the chosen algorithm.

---

# 29. Proposed Processing Algorithm

```text
START
  │
  ▼
Receive Cheque Image
  │
  ▼
Locate Signature Region
  │
  ▼
Is Signature Present?
  │
 ┌┴─────────────┐
NO              YES
 │                │
 ▼                ▼
Missing       Preprocess
Risk             │
 │                ▼
 │          Check Image Quality
 │                │
 │                ▼
 │         Extract Signature Features
 │                │
 │                ▼
 │         Load Reference Signature
 │                │
 │                ▼
 │          Compare Signatures
 │                │
 │                ▼
 │         Calculate Similarity
 │                │
 └───────┬────────┘
         ▼
Generate Risk Indicator
         │
         ▼
Send Result to Fraud Engine
         │
         ▼
       END
```

---

# 30. Proposed Python Implementation

For the project, Python is suitable for the signature-analysis component because it provides libraries for computer vision and machine learning.

Potential libraries:

```text
OpenCV
NumPy
scikit-image
scikit-learn
TensorFlow / PyTorch
```

Possible implementation:

```text
OpenCV
   ↓
Image preprocessing
   ↓
Feature extraction
   ↓
Similarity calculation
   ↓
Risk classification
```

A deep-learning implementation can be added after the baseline system is working.

---

# 31. Suggested Module Structure

The backend can be organized as:

```text
apps/
└── backend/
    └── signature_analysis/
        ├── preprocessing.py
        ├── region_detector.py
        ├── feature_extractor.py
        ├── comparator.py
        ├── quality_checker.py
        ├── risk_classifier.py
        └── signature_service.py
```

Responsibilities:

| File                   | Responsibility               |
| ---------------------- | ---------------------------- |
| `preprocessing.py`     | Clean signature image        |
| `region_detector.py`   | Locate signature region      |
| `feature_extractor.py` | Extract signature features   |
| `comparator.py`        | Compare signatures           |
| `quality_checker.py`   | Evaluate image quality       |
| `risk_classifier.py`   | Convert results into risk    |
| `signature_service.py` | Coordinate complete workflow |

---

# 32. API Example

The module can expose an internal API:

### Request

```http
POST /api/v1/signature/analyze
```

Request:

```json
{
  "cheque_id": "CHK-2026-000125",
  "account_number": "1002345678",
  "image_path": "sample_cheque_001.png"
}
```

### Response

```json
{
  "cheque_id": "CHK-2026-000125",
  "signature_present": true,
  "similarity_score": 0.89,
  "confidence": 0.93,
  "risk_level": "LOW",
  "indicator": null,
  "recommendation": "PASS"
}
```

---

# 33. Error Handling

The module should handle:

### No signature

```text
SIGNATURE_MISSING
```

### Poor image

```text
SIGNATURE_IMAGE_LOW_QUALITY
```

### Reference unavailable

```text
REFERENCE_SIGNATURE_NOT_FOUND
```

### Processing failure

```text
SIGNATURE_ANALYSIS_ERROR
```

### Unsupported image

```text
UNSUPPORTED_SIGNATURE_IMAGE
```

These errors should be logged and should **not result in automatic approval**.

---

# 34. Security and Privacy

Signature images are sensitive information.

The system should:

1. Use synthetic signatures for development.
2. Avoid storing unnecessary copies.
3. Restrict access to authorized users.
4. Encrypt sensitive data at rest where applicable.
5. Use secure communication.
6. Avoid exposing signatures in application logs.
7. Mask account information in logs and dashboards.
8. Maintain access records.
9. Apply enterprise data-retention policies.
10. Ensure test data contains no real customer signatures.

---

# 35. Performance Requirements

The signature analysis component should operate efficiently enough to satisfy the project's overall requirement:

> **Complete cheque processing time < 30 seconds per cheque.**

The following should be measured:

```text
Signature region detection time
Preprocessing time
Feature extraction time
Comparison time
Risk classification time
```

The actual measured performance will be documented in:

```text
docs/34_Performance_Evaluation.md
```

---

# 36. Testing Strategy

### Test Case 1 — Genuine Signature

```text
Input:
Genuine synthetic signature

Expected:
High similarity
LOW risk
```

### Test Case 2 — Different Signature

```text
Input:
Different synthetic signature

Expected:
Low similarity
HIGH risk indicator
```

### Test Case 3 — Missing Signature

```text
Input:
Blank signature area

Expected:
SIGNATURE_MISSING
Manual Review
```

### Test Case 4 — Blurred Signature

```text
Input:
Low-quality signature

Expected:
Low analysis confidence
Manual Review
```

### Test Case 5 — Genuine Variation

```text
Input:
Same synthetic signer with natural variation

Expected:
Should not be incorrectly classified as fraud
```

### Test Case 6 — Partial Signature

```text
Input:
Incomplete signature

Expected:
Insufficient comparison
Manual Review
```

---

# 37. Evaluation Metrics

The module should be evaluated using:

### Genuine Acceptance Rate

Percentage of genuine signatures correctly identified as acceptable.

### False Acceptance Rate

Percentage of different/forged signatures incorrectly accepted.

### False Rejection Rate

Percentage of genuine signatures incorrectly classified as suspicious.

### Precision

Measures how many signatures classified as suspicious were actually suspicious within the defined test ground truth.

### Recall

Measures how many suspicious signatures were successfully detected.

### F1 Score

Balances precision and recall.

The project should document these measurements using the synthetic test dataset.

---

# 38. Important Accuracy Target

The overall project specifies:

> **Fraud detection accuracy ≥ 90%.**

This should be treated as a **project target**, not as an already achieved signature-analysis accuracy.

Signature analysis should therefore be evaluated independently and then assessed as one component of the overall fraud detection pipeline.

---

# 39. Audit Trail

Each signature-analysis operation should produce an audit record.

Example:

```json
{
  "cheque_id": "CHK-2026-000125",
  "timestamp": "2026-08-20T10:18:42Z",
  "similarity_score": 0.47,
  "risk_level": "HIGH",
  "analysis_status": "COMPLETED",
  "engine_version": "signature-engine-v1.0"
}
```

The system should record **what result was generated and which engine version generated it**, without unnecessarily storing sensitive signature images in logs.

---

# 40. Module Boundaries

## Signature Analysis is responsible for:

```text
✓ Signature region detection
✓ Signature extraction
✓ Image preprocessing
✓ Image quality analysis
✓ Feature extraction
✓ Signature comparison
✓ Similarity score
✓ Signature risk indicator
✓ Signature analysis status
```

## Signature Analysis is NOT responsible for:

```text
✗ OCR of cheque fields
✗ Account validation
✗ Duplicate detection
✗ Final fraud decision
✗ Final approve/reject decision
✗ Payment settlement
```

---

# 41. End-to-End Example

Consider a synthetic cheque:

```text
Cheque ID       : CHK-2026-000125
Account Number  : 1002345678
```

Reference signature:

```text
SIG-1002345678.png
```

Extracted cheque signature:

```text
signature_crop.png
```

After preprocessing:

```text
Image Quality = GOOD
```

Comparison:

```text
Similarity Score = 0.47
```

Result:

```text
Signature Present       = TRUE
Similarity              = 0.47
Analysis Confidence     = 0.91
Signature Risk          = HIGH
Indicator               = SIGNATURE_MISMATCH
Recommendation          = MANUAL_REVIEW
```

Fraud Detection Engine receives:

```text
SIGNATURE_MISMATCH
       +
Similarity Score
       +
Confidence
```

and combines it with:

```text
Payee Match
Amount Anomaly
Duplicate Status
Image Tampering
Account Validation
Cheque Validation
```

to calculate the overall fraud risk.

---

# 42. Final Architecture

```text
                    CHEQUE IMAGE
                         │
                         ▼
              ┌─────────────────────┐
              │ Signature Region     │
              │ Detection            │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Image Preprocessing │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Quality Assessment  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Feature Extraction  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Reference Signature │
              │ Comparison           │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Similarity Score    │
              │ + Confidence        │
              │ + Risk Indicator    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Fraud Detection     │
              │ Engine              │
              └──────────┬──────────┘
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

## Summary

The **Signature Analysis Module** provides a structured mechanism for comparing the signature on a cheque against a synthetic reference signature associated with the account. It performs **signature-region extraction, preprocessing, quality assessment, feature extraction, comparison, similarity scoring, and risk classification**.

The module is intentionally designed as an **evidence-generating component**, not as an independent fraud judge. Its results are combined with duplicate detection, image-tampering analysis, cheque validation, account validation, and anomaly detection by the **Fraud Detection Engine** before the final decision is made.

For this project, the initial implementation should use **synthetic signature/reference data**, with thresholds and performance metrics established experimentally through the project's test dataset.

