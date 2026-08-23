# Duplicate Detection

# 19. Duplicate Detection

## 1. Introduction

The **Duplicate Detection Module** identifies whether the same cheque, or a substantially similar cheque, has already been processed by the system.

Duplicate cheque submission can be an important fraud indicator. For example, a cheque image may be submitted multiple times intentionally, or the same cheque may appear with minor modifications such as cropping, rotation, compression, or changes to the image quality.

The module compares the current cheque against previously processed cheque records and determines whether it is:

* **New**
* **Potential Duplicate**
* **Confirmed Duplicate**

The module does **not independently declare a cheque as fraudulent**. Its result is passed to the **Fraud Detection Engine**, where it is combined with other indicators such as signature mismatch, tampering, unusual amount, and account validation failures.

---

# 2. Objectives

The objectives of the Duplicate Detection Module are:

1. Detect repeated submissions of the same cheque.
2. Compare newly submitted cheque data with historical records.
3. Identify exact duplicate cheque submissions.
4. Detect visually similar cheque images even when minor image changes are present.
5. Identify duplicate cheque numbers associated with the same account.
6. Detect repeated combinations of important cheque attributes.
7. Generate a duplicate similarity score.
8. Classify the cheque as new, potential duplicate, or confirmed duplicate.
9. Pass duplicate information to the Fraud Detection Engine.
10. Maintain duplicate-detection results in the audit trail.

---

# 3. Why Duplicate Detection Is Required

Without duplicate detection, the same cheque could potentially be submitted multiple times.

Example:

```text
Original Cheque
     │
     ▼
Submitted → Processed
     │
     ▼
Same cheque submitted again
     │
     ▼
System detects duplicate
     │
     ▼
Manual Review / Reject
```

Duplicate detection helps prevent repeated processing and provides an additional fraud indicator.

---

# 4. Duplicate Detection in the Overall System

```text
                    New Cheque
                        │
                        ▼
                 OCR + Extraction
                        │
                        ▼
              Extracted Cheque Data
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Historical Data        Image Database
             │                     │
             └──────────┬──────────┘
                        ▼
               Duplicate Detection
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
           NEW      POTENTIAL   CONFIRMED
                    DUPLICATE    DUPLICATE
                        │
                        ▼
               Fraud Detection
                        │
                        ▼
                  Risk Scoring
                        │
                        ▼
                 Decision Engine
```

---

# 5. Types of Duplicate Detection

The system should use multiple methods rather than depending on only one comparison.

### 5.1 Exact Data Duplicate

Checks whether important cheque fields are exactly the same.

Example:

```text
Account Number  = 1002345678
Cheque Number   = 000125
Amount          = ₹25,000
Date            = 2026-08-20
```

If an already processed cheque has the same combination, it may be a duplicate.

---

### 5.2 Cheque Number Duplicate

The system checks whether the same cheque number has already been processed for the same account.

```text
Account       Cheque Number
1002345678    000125
```

If the same cheque number appears again:

```text
Duplicate Indicator = TRUE
```

However, cheque number alone should not always be treated as sufficient evidence because cheque numbering conventions can vary.

---

### 5.3 Image Duplicate

The system compares the current cheque image against previously stored cheque images.

This can detect the same image being uploaded again.

---

### 5.4 Near-Duplicate Image

The same cheque may be uploaded again after:

* Cropping
* Rotation
* Resizing
* Compression
* Brightness adjustment
* Minor image modifications

Therefore, the system should support **near-duplicate detection**.

---

# 6. Exact Duplicate Detection

The first level uses extracted cheque information.

Important fields include:

* Account number
* Cheque number
* Amount
* Cheque date
* Payee
* Bank/routing information

Example:

```text
Current Cheque

Account      : 1002345678
Cheque No.   : 000125
Amount       : 25000
Date         : 2026-08-20
Payee        : ABC Stores
```

Historical record:

```text
Account      : 1002345678
Cheque No.   : 000125
Amount       : 25000
Date         : 2026-08-20
Payee        : ABC Stores
```

Result:

```text
CONFIRMED DUPLICATE
```

---

# 7. Duplicate Key

A composite duplicate key can be created using important cheque attributes.

Example:

```text
Duplicate Key =
Account Number
+
Cheque Number
+
Amount
+
Cheque Date
```

Example:

```text
1002345678|000125|25000|2026-08-20
```

The system can hash this value.

```text
Composite Key
      │
      ▼
Hash Function
      │
      ▼
Duplicate Hash
```

Example:

```text
duplicate_hash =
SHA256(account + cheque_number + amount + date)
```

The hash can then be stored in the database.

---

# 8. Image Hashing

Image hashing can be used to identify repeated cheque images.

A cryptographic hash such as SHA-256 can identify an **exactly identical file**.

```text
Cheque Image
     │
     ▼
SHA-256
     │
     ▼
Image Hash
```

Example:

```text
Image Hash:
a73f9b...e82d
```

If the same file is uploaded again:

```text
Same Image Hash
      ↓
Exact Duplicate
```

---

# 9. Limitation of SHA-256 for Images

SHA-256 is useful for exact duplicates, but it will not identify visually identical images if even a small change is made.

For example:

```text
Original Image
      │
      ▼
Crop / Resize
      │
      ▼
Different File
      │
      ▼
Different SHA-256
```

Therefore, the project should use **perceptual image hashing** for near-duplicate detection.

---

# 10. Perceptual Hashing

Perceptual hashing generates a hash based on the visual characteristics of an image.

Possible techniques include:

* pHash
* dHash
* aHash

Example:

```text
Original Cheque
      │
      ▼
Perceptual Hash
      │
      ▼
101100101001...
```

A slightly modified version of the same cheque:

```text
Modified Cheque
      │
      ▼
Perceptual Hash
      │
      ▼
101100101011...
```

The hashes remain relatively similar.

---

# 11. Hamming Distance

The difference between perceptual hashes can be measured using **Hamming distance**.

Example:

```text
Hash A:
10110010

Hash B:
10110011
```

Only one bit differs.

```text
Hamming Distance = 1
```

A small distance indicates that the images may be visually similar.

The exact threshold should be calibrated using the project's synthetic cheque dataset.

---

# 12. Duplicate Similarity Score

The system can produce a similarity score.

Example:

```text
0.00 ───────────────────────── 1.00
 │                               │
Different                    Identical
```

Example classification:

| Similarity | Initial Classification |
| ---------: | ---------------------- |
|     ≥ 0.95 | Confirmed Duplicate    |
|  0.80–0.94 | Potential Duplicate    |
|     < 0.80 | Likely New             |

These are **initial prototype thresholds**. They must be validated against the project's test dataset before being used as final thresholds.

---

# 13. Multi-Level Duplicate Detection

The recommended architecture uses three levels.

```text
Level 1
Exact Data Match
       │
       ▼
Level 2
Exact Image Match
       │
       ▼
Level 3
Near-Image Match
```

This provides stronger duplicate detection than relying on a single method.

---

# 14. Level 1 — Data Matching

Compare:

```text
Account Number
Cheque Number
Amount
Date
Payee
```

Example:

```text
Account Number → MATCH
Cheque Number  → MATCH
Amount         → MATCH
Date           → MATCH
Payee          → MATCH
```

Result:

```text
CONFIRMED DUPLICATE
```

---

# 15. Level 2 — Exact Image Matching

If the extracted fields are not sufficient, compare image hashes.

```text
Current Image
      │
      ▼
SHA-256 Hash
      │
      ▼
Search Historical Images
      │
      ▼
Exact Match?
```

If yes:

```text
Duplicate Status = CONFIRMED
```

---

# 16. Level 3 — Near-Duplicate Detection

If the exact image does not match:

```text
Current Image
      │
      ▼
Perceptual Hash
      │
      ▼
Compare Historical Images
      │
      ▼
Calculate Hamming Distance
      │
      ▼
Similarity Score
```

This can identify visually similar cheque images.

---

# 17. Duplicate Detection Algorithm

```text
START
  │
  ▼
Receive New Cheque
  │
  ▼
Extract Cheque Fields
  │
  ▼
Generate Composite Duplicate Key
  │
  ▼
Search Historical Records
  │
  ├── Match Found ──────► CONFIRMED DUPLICATE
  │
  ▼
Generate Exact Image Hash
  │
  ▼
Search Image Hash
  │
  ├── Match Found ──────► CONFIRMED DUPLICATE
  │
  ▼
Generate Perceptual Hash
  │
  ▼
Compare Similar Images
  │
  ▼
Calculate Similarity
  │
  ├── High ─────────────► POTENTIAL/CONFIRMED DUPLICATE
  │
  ▼
No Significant Match
  │
  ▼
NEW CHEQUE
```

---

# 18. Duplicate Detection Using Historical Data

The project will create a **synthetic historical cheque dataset**.

Suggested structure:

```text
data/
├── mock_banking_data/
│   ├── accounts.csv
│   ├── cheques.csv
│   └── transactions.csv
│
├── sample_cheques/
│   ├── original/
│   ├── duplicate/
│   └── modified/
│
└── test_data/
    └── duplicate_detection/
        ├── exact_duplicates/
        ├── near_duplicates/
        └── unique_cheques/
```

No real customer cheque information should be used.

---

# 19. Sample Historical Data

Example `cheques.csv`:

```csv
cheque_id,account_number,cheque_number,payee,amount,cheque_date,status
CHK001,1002345678,000125,ABC Stores,25000,2026-08-20,PROCESSED
CHK002,1003456789,000126,XYZ Traders,15000,2026-08-19,PROCESSED
CHK003,1002345678,000127,DEF Services,18000,2026-08-18,PROCESSED
```

New cheque:

```text
Account Number = 1002345678
Cheque Number  = 000125
```

The system finds:

```text
CHK001
```

Therefore:

```text
Duplicate Status = CONFIRMED
```

---

# 20. Duplicate Detection with Payee and Amount

Suppose the cheque number is incorrectly extracted.

The system can still compare other attributes.

Example:

```text
Account Number = 1002345678
Payee          = ABC Stores
Amount         = 25000
Date           = 2026-08-20
```

Historical record:

```text
Account Number = 1002345678
Payee          = ABC Stores
Amount         = 25000
Date           = 2026-08-20
```

This creates a **potential duplicate indicator** even if the cheque number does not match.

This is particularly useful when OCR has minor extraction errors.

---

# 21. OCR Error Handling

OCR may produce errors such as:

```text
000125 → 000I25
```

or:

```text
ABC Stores → ABC St0res
```

Therefore, duplicate detection should not depend exclusively on exact string matching.

The system can use:

* Normalization
* Fuzzy matching
* Numeric validation
* Multiple field comparison
* Image comparison

---

# 22. Data Normalization

Before comparison, fields should be normalized.

Example:

```text
"ABC STORES"
"ABC Stores"
"abc stores"
```

can be normalized to:

```text
abc stores
```

Similarly:

```text
₹25,000
25,000
25000
```

can be normalized to:

```text
25000
```

This reduces false negatives caused by formatting differences.

---

# 23. Duplicate Detection Rules

The initial rule set can be:

### Rule D1 — Exact Composite Match

```text
Same account
+
Same cheque number
+
Same amount
+
Same cheque date
```

→ **Confirmed Duplicate**

### Rule D2 — Exact Image Match

```text
Same image hash
```

→ **Confirmed Duplicate**

### Rule D3 — Strong Visual Similarity

```text
High perceptual similarity
+
Matching account/cheque information
```

→ **Potential/Confirmed Duplicate**

### Rule D4 — Partial Match

```text
Same account
+
Same cheque number
+
Different amount/date
```

→ **High-risk inconsistency → Manual Review**

This should not automatically be called a duplicate because it could represent legitimate data or OCR errors.

---

# 24. Duplicate Status

The module should return one of the following statuses:

```text
NEW
POTENTIAL_DUPLICATE
CONFIRMED_DUPLICATE
```

Additionally, an analysis status can indicate:

```text
COMPLETED
INSUFFICIENT_DATA
ERROR
```

---

# 25. Example — New Cheque

```json
{
  "cheque_id": "CHK-2026-000150",
  "duplicate_status": "NEW",
  "similarity_score": 0.21,
  "matched_cheque_id": null,
  "reason": "No significant historical match found"
}
```

---

# 26. Example — Confirmed Duplicate

```json
{
  "cheque_id": "CHK-2026-000151",
  "duplicate_status": "CONFIRMED_DUPLICATE",
  "similarity_score": 1.0,
  "matched_cheque_id": "CHK-2026-000125",
  "reason": "Composite cheque details and image match"
}
```

---

# 27. Example — Potential Duplicate

```json
{
  "cheque_id": "CHK-2026-000152",
  "duplicate_status": "POTENTIAL_DUPLICATE",
  "similarity_score": 0.88,
  "matched_cheque_id": "CHK-2026-000125",
  "reason": "High visual similarity with historical cheque"
}
```

---

# 28. Duplicate Detection Output

A complete output can be:

```json
{
  "cheque_id": "CHK-2026-000152",
  "duplicate_status": "POTENTIAL_DUPLICATE",
  "matched_cheque_id": "CHK-2026-000125",
  "data_match": true,
  "image_match": false,
  "perceptual_similarity": 0.88,
  "hamming_distance": 8,
  "confidence": 0.91,
  "reason": "High similarity with previously processed cheque",
  "recommendation": "MANUAL_REVIEW"
}
```

---

# 29. Integration with Fraud Detection

Duplicate detection produces a fraud indicator.

```text
Duplicate Detection
        │
        ├── Duplicate Status
        ├── Similarity Score
        ├── Matched Cheque ID
        └── Reason
                │
                ▼
       Fraud Detection Engine
```

Example:

```text
Confirmed Duplicate
        │
        ▼
High Fraud Risk Indicator
```

But:

```text
Potential Duplicate
        │
        ▼
Review Indicator
```

This distinction is important.

---

# 30. Integration with Decision Engine

The Duplicate Detection Module does not directly decide whether the cheque should be approved.

Instead:

```text
Duplicate Detection
        │
        ▼
Fraud Detection
        │
        ▼
Risk Scoring
        │
        ▼
Decision Engine
```

Example:

```text
Duplicate = CONFIRMED
Signature = MISMATCH
Tampering = HIGH
Amount Anomaly = HIGH
```

The combined risk may result in:

```text
REJECT
```

Whereas:

```text
Duplicate = POTENTIAL
Signature = MATCH
Tampering = LOW
Account = VALID
```

may result in:

```text
MANUAL REVIEW
```

---

# 31. Preventing False Positives

Duplicate detection must avoid incorrectly identifying legitimate cheques as duplicates.

For example:

```text
Same Account
Different Cheque Number
Same Amount
Same Payee
```

This does **not automatically mean duplicate**.

A customer may legitimately issue:

```text
Cheque 00125 → ₹25,000
Cheque 00126 → ₹25,000
```

Therefore, multiple attributes should be evaluated together.

---

# 32. Duplicate Detection Database

The database should maintain information required for comparison.

Example table:

### `processed_cheques`

| Field               | Description                |
| ------------------- | -------------------------- |
| `cheque_id`         | Internal cheque identifier |
| `account_number`    | Synthetic account number   |
| `cheque_number`     | Cheque number              |
| `payee`             | Payee name                 |
| `amount`            | Cheque amount              |
| `cheque_date`       | Date on cheque             |
| `image_hash`        | Exact image hash           |
| `perceptual_hash`   | Visual similarity hash     |
| `processing_status` | Processing result          |
| `processed_at`      | Processing timestamp       |

---

# 33. Suggested Database Indexes

To improve performance, indexes can be created on:

```text
account_number
cheque_number
duplicate_key
image_hash
perceptual_hash
```

This allows the system to search historical records efficiently.

---

# 34. Suggested Backend Structure

The module can be implemented as:

```text
apps/
└── backend/
    └── duplicate_detection/
        ├── duplicate_service.py
        ├── data_matcher.py
        ├── image_hasher.py
        ├── perceptual_matcher.py
        ├── similarity_calculator.py
        ├── duplicate_rules.py
        └── duplicate_repository.py
```

### Responsibilities

| File                       | Responsibility                      |
| -------------------------- | ----------------------------------- |
| `duplicate_service.py`     | Coordinates duplicate detection     |
| `data_matcher.py`          | Compares cheque fields              |
| `image_hasher.py`          | Generates exact image hash          |
| `perceptual_matcher.py`    | Performs visual similarity matching |
| `similarity_calculator.py` | Calculates similarity               |
| `duplicate_rules.py`       | Applies duplicate rules             |
| `duplicate_repository.py`  | Retrieves historical records        |

---

# 35. API Specification

### Endpoint

```http
POST /api/v1/duplicate/check
```

### Request

```json
{
  "cheque_id": "CHK-2026-000152",
  "account_number": "1002345678",
  "cheque_number": "000125",
  "amount": 25000,
  "cheque_date": "2026-08-20",
  "image_path": "sample_cheque_152.png"
}
```

### Response

```json
{
  "cheque_id": "CHK-2026-000152",
  "duplicate_status": "CONFIRMED_DUPLICATE",
  "matched_cheque_id": "CHK-2026-000125",
  "similarity_score": 1.0,
  "confidence": 0.98,
  "recommendation": "REVIEW"
}
```

---

# 36. Audit Trail

Every duplicate check should be recorded.

Example:

```json
{
  "event_type": "DUPLICATE_CHECK",
  "cheque_id": "CHK-2026-000152",
  "timestamp": "2026-08-20T10:30:15Z",
  "duplicate_status": "CONFIRMED_DUPLICATE",
  "matched_cheque_id": "CHK-2026-000125",
  "engine_version": "duplicate-engine-v1.0"
}
```

The audit record helps answer:

> **Why was this cheque flagged as a duplicate?**

---

# 37. Performance Requirement

Duplicate detection must contribute to the overall project requirement:

> **Total processing time should be less than 30 seconds per cheque.**

Performance should be measured for:

```text
Database lookup
+
Exact hash comparison
+
Perceptual hash comparison
+
Similarity calculation
```

The actual measured results should be documented in:

```text
docs/34_Performance_Evaluation.md
```

---

# 38. Testing Strategy

The project should create a synthetic dataset containing known duplicate relationships.

### Test Categories

| Category                       | Expected Result                       |
| ------------------------------ | ------------------------------------- |
| Completely new cheque          | NEW                                   |
| Exact same cheque              | CONFIRMED_DUPLICATE                   |
| Same image renamed             | CONFIRMED_DUPLICATE                   |
| Cropped same cheque            | POTENTIAL/CONFIRMED                   |
| Rotated same cheque            | POTENTIAL_DUPLICATE                   |
| Compressed same cheque         | POTENTIAL_DUPLICATE                   |
| Different cheque               | NEW                                   |
| Same account, different cheque | NEW                                   |
| OCR formatting difference      | Should still detect where appropriate |
| Similar but unrelated cheque   | NEW                                   |

---

# 39. Evaluation Metrics

The module should be evaluated using:

### Duplicate Detection Precision

How many detected duplicates are actually duplicates?

### Duplicate Detection Recall

How many actual duplicates are detected?

### False Positive Rate

How many legitimate cheques are incorrectly flagged?

### False Negative Rate

How many duplicates are missed?

### Processing Time

Average time required to complete duplicate analysis.

---

# 40. Example End-to-End Scenario

Suppose the system receives:

```text
Cheque ID       : CHK-2026-000152
Account Number  : 1002345678
Cheque Number   : 000125
Amount          : ₹25,000
Date            : 20-Aug-2026
Payee           : ABC Stores
```

The system searches historical records.

It finds:

```text
CHK-2026-000125
```

with:

```text
Account Number  → MATCH
Cheque Number   → MATCH
Amount          → MATCH
Date            → MATCH
Payee           → MATCH
Image Hash      → MATCH
```

Result:

```text
Duplicate Status = CONFIRMED_DUPLICATE
```

The Fraud Detection Engine receives:

```text
DUPLICATE_CHEQUE
```

The Decision Engine then considers all other fraud signals before producing:

```text
APPROVE / REVIEW / REJECT
```

---

# 41. Module Boundaries

## Duplicate Detection is responsible for:

```text
✓ Historical cheque lookup
✓ Duplicate-key generation
✓ Exact data comparison
✓ Exact image comparison
✓ Perceptual image comparison
✓ Similarity calculation
✓ Duplicate classification
✓ Duplicate reason generation
✓ Duplicate audit record
```

## Duplicate Detection is NOT responsible for:

```text
✗ OCR extraction
✗ Signature verification
✗ Account validation
✗ Final fraud decision
✗ Final approval/rejection
✗ Payment settlement
```

---

# 42. Final Architecture

```text
                     NEW CHEQUE
                          │
                          ▼
                 Extracted Cheque Data
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       Historical Data            Image Data
             │                         │
             ▼                         ▼
       Data Matching             Image Hashing
             │                         │
             │                    Exact Match?
             │                         │
             │                         ▼
             │                  Perceptual Hash
             │                         │
             └────────────┬────────────┘
                          ▼
                 Similarity Analysis
                          │
                          ▼
                Duplicate Classification
                          │
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
            NEW       POTENTIAL      CONFIRMED
                     DUPLICATE       DUPLICATE
             │            │             │
             └────────────┼─────────────┘
                          ▼
                Fraud Detection Engine
                          │
                          ▼
                    Risk Scoring
                          │
                          ▼
                   Decision Engine
                          │
                 ┌────────┼────────┐
                 ▼        ▼        ▼
              APPROVE   REVIEW   REJECT
```

## Summary

The **Duplicate Detection Module** provides a multi-layer mechanism for identifying previously processed or highly similar cheques. It combines **structured data matching, exact image hashing, perceptual image hashing, similarity analysis, and rule-based classification**.

For our project, duplicate detection will operate against the **synthetic/mock banking and cheque dataset** that we create under `data/mock_banking_data/` and `data/test_data/`. This will allow us to demonstrate exact duplicates, modified/near-duplicates, unique cheques, and OCR-variation cases during testing.

The module's output will be passed to the **Fraud Detection Engine**, rather than directly determining fraud. This keeps the architecture modular and allows duplicate evidence to be combined with **signature analysis, tampering detection, anomaly detection, account validation, and risk scoring** before the final **Approve / Review / Reject** decision.

