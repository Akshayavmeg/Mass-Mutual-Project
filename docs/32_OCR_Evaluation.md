# OCR Evaluation

# OCR Evaluation

## 1. Introduction

The **OCR Evaluation** module defines how the Optical Character Recognition (OCR) component of the AI-Powered Cheque Scanning, Validation & Fraud Detection System will be evaluated.

The purpose of OCR is to automatically extract important information from a cheque image and convert it into structured digital data that can be used by the subsequent validation and fraud-detection modules.

The primary fields evaluated are:

* Cheque number
* Account number
* Routing/transit number
* Payee name
* Amount
* Date

The target specified for this project is:

> **OCR extraction accuracy ≥ 95%**

This target will be verified experimentally using a **project-specific cheque image dataset and manually verified ground-truth data**.

---

# 2. OCR Evaluation Objectives

The objectives of OCR evaluation are to:

1. Measure the accuracy of extracted cheque information.
2. Identify which cheque fields are most frequently misread.
3. Evaluate OCR performance under different image conditions.
4. Measure field-level and overall extraction accuracy.
5. Identify low-confidence OCR results.
6. Determine whether preprocessing improves OCR performance.
7. Compare OCR output against manually verified ground-truth values.
8. Ensure incorrect OCR results are appropriately handled by the validation and manual-review workflow.

---

# 3. OCR Processing Pipeline

The evaluation follows the same pipeline used by the actual system.

```text
Cheque Image
     ↓
Image Quality Check
     ↓
Image Preprocessing
     ↓
Region Detection
     ↓
OCR Engine
     ↓
Text Extraction
     ↓
Field Identification
     ↓
Data Normalization
     ↓
Ground-Truth Comparison
     ↓
Accuracy Calculation
```

---

# 4. OCR Fields to be Evaluated

Each cheque will be evaluated for the following fields:

| Field                  | Example            |
| ---------------------- | ------------------ |
| Cheque Number          | 100001             |
| Account Number         | 9000012345         |
| Routing/Transit Number | 021000021          |
| Payee                  | Sample Corporation |
| Amount                 | 12500.00           |
| Date                   | 2026-08-01         |

The exact format of these fields will depend on the cheque format used in the project's synthetic dataset.

---

# 5. OCR Evaluation Dataset

Since the project should not depend on real customer banking information, the evaluation will use **synthetic/sample cheque images**.

The dataset will be maintained inside the project repository.

Recommended structure:

```text
data/
├── sample_cheques/
│   ├── normal/
│   ├── low_quality/
│   ├── rotated/
│   ├── noisy/
│   └── distorted/
│
└── test_data/
    └── ocr_ground_truth.csv
```

The `ocr_ground_truth.csv` file will contain the correct values corresponding to each cheque image.

Example:

```csv
image_id,cheque_number,account_number,routing_number,payee,amount,date
CHK001,100001,9000012345,021000021,Sample Corporation,12500.00,2026-08-01
CHK002,100002,9000012346,021000021,Demo Enterprises,7500.00,2026-08-03
```

The ground-truth file represents the **known correct values** against which OCR output will be compared.

---

# 6. Dataset Categories

The OCR system should be evaluated using different image conditions.

### Category 1 — Clear Images

High-quality, properly aligned cheque images.

```text
Expected OCR performance:
Highest accuracy
```

### Category 2 — Low-Quality Images

Images with reduced resolution or compression.

```text
Expected:
Some extraction errors may occur.
```

### Category 3 — Rotated Images

Cheques captured at different angles.

```text
Expected:
Preprocessing should correct the orientation.
```

### Category 4 — Noisy Images

Images containing scanning or camera noise.

### Category 5 — Blurred Images

Images with slight motion or focus blur.

### Category 6 — Uneven Lighting

Images containing shadows, brightness variation, or poor illumination.

### Category 7 — Distorted Images

Images with perspective distortion or skew.

This helps determine how robust the OCR pipeline is under realistic input conditions.

---

# 7. Ground-Truth Creation

Ground truth is the **manually verified correct information** corresponding to each cheque image.

For every sample cheque:

```text
Cheque Image
     ↓
Manual Verification
     ↓
Correct Field Values
     ↓
Ground-Truth Dataset
```

For example:

```text
Image:
CHK001.png

Ground Truth:

Cheque Number  → 100001
Account Number → 9000012345
Payee          → Sample Corporation
Amount         → 12500.00
Date           → 2026-08-01
```

The ground-truth values must be finalized before calculating OCR accuracy.

---

# 8. OCR Output

The OCR system will produce structured output.

Example:

```json
{
  "cheque_number": "100001",
  "account_number": "9000012345",
  "routing_number": "021000021",
  "payee": "Sample Corporation",
  "amount": "12500.00",
  "date": "2026-08-01"
}
```

This output will be compared with the ground-truth record.

---

# 9. Field-Level Accuracy

Each individual field will be evaluated separately.

For example:

```text
Expected Payee:
Sample Corporation

OCR Output:
Sample Corporation

Result:
CORRECT
```

Another example:

```text
Expected Amount:
12500.00

OCR Output:
12500.00

Result:
CORRECT
```

If the OCR output differs from the ground truth, the field will be classified as incorrect according to the project's comparison rules.

---

# 10. Field Accuracy Formula

For each field:

```text
Field Accuracy =
Correctly Extracted Values
────────────────────────── × 100
Total Values Tested
```

For example, if 100 cheque images are tested for the amount field and 97 are correctly extracted:

```text
Amount Accuracy = (97 / 100) × 100

                = 97%
```

---

# 11. Overall OCR Accuracy

The project will calculate overall field-level OCR accuracy across all evaluated fields.

```text
Overall OCR Accuracy =
Total Correctly Extracted Fields
──────────────────────────────── × 100
Total Fields Evaluated
```

For example:

```text
Number of cheques = 100
Fields per cheque = 6

Total fields = 100 × 6
             = 600

Correct fields = 582

Accuracy = (582 / 600) × 100
         = 97%
```

The numbers above are **illustrative only**. The actual project result will be calculated after the dataset is created and the OCR system is implemented.

---

# 12. Character-Level Evaluation

For fields where character-level errors matter, such as account numbers and cheque numbers, character-level comparison may also be performed.

For example:

```text
Expected:
9000012345

OCR:
9000012348
```

The difference occurs in the final digit.

This type of error is important because even a single incorrect digit can cause an incorrect banking-record match.

Character-level metrics such as **Character Error Rate (CER)** can therefore be used.

A common formula is:

```text
CER = (S + D + I) / N
```

Where:

* `S` = substitutions
* `D` = deletions
* `I` = insertions
* `N` = number of characters in the reference text

Lower CER indicates better OCR performance.

---

# 13. Field-Specific Evaluation

Different cheque fields have different importance and difficulty.

### Cheque Number

Expected to contain mostly numeric characters.

Testing should check:

* Digit recognition
* Missing digits
* Extra digits
* Confused digits

### Account Number

This is a critical field because it is used for banking-record validation.

A single digit error may result in:

```text
Incorrect Account Match
```

Therefore, account-number accuracy should be monitored separately.

### Routing/Transit Number

This field is also primarily numeric and should be validated carefully.

### Payee

Payee names contain alphabetic characters and spaces and may be more challenging for OCR.

### Amount

Amount may appear in:

* Numeric format
* Written words
* Currency format

The system should normalize the extracted amount before validation.

### Date

The system should normalize supported date formats into a standard representation.

Example:

```text
01/08/2026
```

may be converted internally to:

```text
2026-08-01
```

according to the project's configured date interpretation.

---

# 14. OCR Confidence

Where the selected OCR engine provides confidence information, the system should retain the confidence score for extracted fields.

Example:

```json
{
  "field": "account_number",
  "value": "9000012345",
  "confidence": 0.98
}
```

Confidence can be used to identify uncertain OCR results.

Example:

```text
Confidence ≥ configured threshold
        ↓
Continue processing

Confidence < configured threshold
        ↓
Flag for additional validation/review
```

The threshold should be determined through testing rather than arbitrarily assuming that one fixed value is universally optimal.

---

# 15. OCR Error Classification

OCR errors should be categorized to understand system weaknesses.

### Character Substitution

```text
Expected: 12500
OCR:      125OO
```

### Character Deletion

```text
Expected: 100001
OCR:      10001
```

### Character Insertion

```text
Expected: 100001
OCR:      1000001
```

### Missing Field

```text
Expected:
Payee = Sample Corporation

OCR:
Payee = ""
```

### Incorrect Field

```text
Expected:
Sample Corporation

OCR:
Sample Corparation
```

These error categories will help guide improvements to preprocessing and OCR configuration.

---

# 16. Preprocessing Impact Evaluation

The project will also evaluate whether image preprocessing improves OCR performance.

Two experiments can be performed:

```text
Original Image
      ↓
OCR
      ↓
Accuracy A
```

and:

```text
Original Image
      ↓
Preprocessing
      ↓
OCR
      ↓
Accuracy B
```

Then:

```text
Improvement =
Accuracy B − Accuracy A
```

For example, if:

```text
Without preprocessing = 88%
With preprocessing    = 96%
```

then:

```text
Improvement = 8 percentage points
```

These are example values only.

---

# 17. OCR Test Cases

| Test ID | Image Condition       | Expected Result                     |
| ------- | --------------------- | ----------------------------------- |
| OCR-001 | Clear cheque          | Correct extraction                  |
| OCR-002 | Low-resolution cheque | Extract or flag low confidence      |
| OCR-003 | Rotated cheque        | Orientation corrected and extracted |
| OCR-004 | Noisy cheque          | Noise reduced and extracted         |
| OCR-005 | Blurred cheque        | Extract or flag for review          |
| OCR-006 | Uneven lighting       | Preprocessing improves readability  |
| OCR-007 | Skewed cheque         | Perspective/skew corrected          |
| OCR-008 | Missing field         | Missing field detected              |
| OCR-009 | Unsupported image     | Input rejected                      |
| OCR-010 | Corrupted image       | Processing error handled safely     |

---

# 18. OCR Evaluation Procedure

The evaluation process will follow these steps:

### Step 1 — Prepare Dataset

Create a set of synthetic cheque images.

### Step 2 — Create Ground Truth

Manually record the correct information for every image.

### Step 3 — Process Images

Send the images through the complete OCR pipeline.

### Step 4 — Store OCR Results

Save extracted values and confidence information.

### Step 5 — Compare Results

Compare OCR output with ground-truth values.

### Step 6 — Calculate Metrics

Calculate:

* Field accuracy
* Overall accuracy
* CER where applicable
* Confidence statistics
* Error counts

### Step 7 — Analyze Errors

Identify the most common OCR errors.

### Step 8 — Improve Pipeline

Modify preprocessing/OCR configuration where necessary.

### Step 9 — Re-test

Run the same evaluation dataset again.

### Step 10 — Record Final Results

Document the final measured performance.

---

# 19. Evaluation Report

The final OCR evaluation report should contain a table similar to:

| Field          | Total Tested | Correct | Accuracy |
| -------------- | -----------: | ------: | -------: |
| Cheque Number  |            — |       — |        — |
| Account Number |            — |       — |        — |
| Routing Number |            — |       — |        — |
| Payee          |            — |       — |        — |
| Amount         |            — |       — |        — |
| Date           |            — |       — |        — |
| **Overall**    |        **—** |   **—** |    **—** |

The actual values will be populated after implementation and testing.

---

# 20. OCR Target

The project's target is:

> **Overall OCR extraction accuracy ≥ 95%**

However, this value must be **measured using the project's test dataset**.

The documentation must distinguish between:

```text
Target:
≥ 95%

Actual Result:
To be measured after implementation
```

We should **not claim 95% or higher until the system has actually been tested**.

---

# 21. OCR Evaluation and Validation Integration

OCR accuracy cannot be considered independently from the validation system.

For example:

```text
OCR:
Account Number = 9000012345
        ↓
Validation
        ↓
Mock Banking Database
        ↓
Account Found
```

If OCR produces:

```text
9000012348
```

the validation system may report:

```text
Account Not Found
```

Therefore, OCR errors can directly affect downstream validation and fraud decisions.

---

# 22. Low-Confidence OCR Handling

If a critical field has poor OCR confidence or fails validation, the system should avoid blindly approving the cheque.

Example:

```text
OCR Confidence
       ↓
Low
       ↓
Critical Field?
       ↓
Yes
       ↓
Additional Validation
       ↓
Manual Review if Required
```

This reduces the risk of an OCR error becoming an incorrect financial-processing decision.

---

# 23. OCR Evaluation Success Criteria

OCR evaluation will be considered successful when:

* The OCR pipeline successfully processes supported cheque images.
* Required fields are extracted into structured data.
* Ground-truth comparison is automated or reproducible.
* Field-level accuracy is measured.
* Overall OCR accuracy is measured.
* Critical numeric fields are carefully validated.
* OCR confidence is captured where supported.
* Low-confidence results can be routed to validation/manual review.
* Preprocessing effectiveness is evaluated.
* The final measured OCR accuracy is compared against the **≥95% project target**.

---

# 24. Final Evaluation Workflow

```text
Synthetic Cheque Dataset
          ↓
Ground-Truth Dataset
          ↓
Image Preprocessing
          ↓
OCR Engine
          ↓
Structured Extraction
          ↓
Field-Level Comparison
          ↓
┌───────────────────────────────┐
│ Accuracy                      │
│ Character Error Rate          │
│ Confidence                    │
│ Error Classification          │
└───────────────────────────────┘
          ↓
Preprocessing/OCR Improvements
          ↓
Re-testing
          ↓
Final OCR Evaluation Report
```

---

## 25. Expected Deliverables

The OCR evaluation phase will produce:

```text
data/test_data/
├── ocr_ground_truth.csv
├── ocr_predictions.csv
└── ocr_evaluation_results.csv
```

and documentation containing:

* Dataset description
* Ground-truth methodology
* OCR configuration
* Test cases
* Field-level accuracy
* Overall accuracy
* Character-level error analysis
* Confidence analysis
* Preprocessing comparison
* Error analysis
* Final measured performance
* Comparison against the **≥95% target**

This makes the OCR evaluation **measurable, reproducible, and directly connected to the actual cheque-processing system**, rather than simply stating that the OCR accuracy is 95%.
