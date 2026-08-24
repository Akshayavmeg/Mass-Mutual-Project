# Data Flow

# 10. Data Flow

## 1. Introduction

The **Data Flow** describes how cheque information moves through the AI-Powered Cheque Scanning, Validation & Fraud Detection System from the moment a cheque image is uploaded until the final decision is generated and recorded.

Since the project is a prototype, **sample/mock cheque data and mock banking records will be created specifically for development and testing**. No real customer banking information will be required.

The data flow is designed to demonstrate the complete processing pipeline:

```text
Cheque Image
     ↓
Image Validation
     ↓
Image Preprocessing
     ↓
OCR
     ↓
Data Extraction
     ↓
Data Normalization
     ↓
Banking Validation
     ↓
Fraud Detection
     ↓
Risk Scoring
     ↓
Decision
     ↓
Audit Trail
     ↓
Dashboard / Reports
```

---

# 2. Data Sources

The system will use the following data sources.

### 2.1 Sample Cheque Images

We will create/use sample cheque images representing different scenarios:

* Valid cheque
* Invalid account
* Expired cheque
* Duplicate cheque
* Amount mismatch
* Payee mismatch
* Suspicious/tampered cheque
* Low-quality cheque image
* Signature mismatch
* High-risk transaction

These images will be stored under:

```text
data/
└── sample_cheques/
```

---

### 2.2 Mock Banking Records

Since the prototype will not connect directly to a production banking system, mock banking data will be created.

Example:

```text
data/
└── mock_banking_data/
```

The mock data can contain:

```text
Accounts
Cheque Records
Customers
Payees
Transactions
Cheque Series
Reference Signatures
```

Example account record:

| Account Number | Account Holder | Status  | Balance | Branch |
| -------------- | -------------- | ------- | ------: | ------ |
| ACC100001      | Ravi Kumar     | ACTIVE  |   85000 | HYD001 |
| ACC100002      | Priya Sharma   | ACTIVE  |   42000 | HYD002 |
| ACC100003      | Arun Rao       | BLOCKED |   15000 | HYD001 |

**All such records will be synthetic and created only for project demonstration/testing.**

---

# 3. Sample Cheque Dataset

The project should contain a controlled test dataset.

For example:

| Cheque ID | Account   |  Amount | Payee           | Scenario           | Expected Result |
| --------- | --------- | ------: | --------------- | ------------------ | --------------- |
| CHK001    | ACC100001 | ₹25,000 | ABC Traders     | Valid              | APPROVE         |
| CHK002    | ACC100002 | ₹15,000 | XYZ Stores      | Valid              | APPROVE         |
| CHK003    | ACC100003 | ₹10,000 | ABC Traders     | Blocked account    | REJECT          |
| CHK004    | ACC100001 | ₹25,000 | ABC Traders     | Duplicate          | REVIEW          |
| CHK005    | ACC100002 | ₹90,000 | XYZ Stores      | Unusual amount     | REVIEW          |
| CHK006    | ACC100001 | ₹18,000 | DEF Enterprises | Payee mismatch     | REVIEW          |
| CHK007    | ACC100001 | ₹12,000 | ABC Traders     | Expired cheque     | REJECT          |
| CHK008    | ACC100002 | ₹20,000 | XYZ Stores      | Signature mismatch | REVIEW          |

These values are **illustrative synthetic data** and can be expanded during testing.

---

# 4. Complete Data Flow

## Step 1 — Cheque Upload

The user uploads a cheque image through the web application.

Supported formats:

```text
JPEG
JPG
PNG
PDF
```

Example:

```text
User
  │
  │ Upload CHK001.jpg
  ▼
Frontend
```

The frontend sends the file to the backend API.

---

# 5. Step 2 — File Validation

The backend first validates the uploaded file.

Checks include:

* File type
* File size
* File integrity
* Image dimensions
* Readability
* Duplicate upload ID

Example:

```json
{
  "file_name": "CHK001.jpg",
  "file_type": "image/jpeg",
  "valid": true
}
```

If the file is invalid:

```text
INVALID FILE
     ↓
Reject Upload
     ↓
Audit Event
```

---

# 6. Step 3 — Cheque Registration

After successful upload, the system creates a unique processing ID.

Example:

```text
Processing ID:
CHK-2026-000001
```

A database record is created:

```json
{
  "cheque_id": "CHK-2026-000001",
  "file_name": "CHK001.jpg",
  "status": "UPLOADED"
}
```

The original image is stored securely.

---

# 7. Step 4 — Image Preprocessing

The uploaded image is sent to the preprocessing component.

```text
Original Image
      ↓
Resize
      ↓
Grayscale
      ↓
Noise Removal
      ↓
Contrast Enhancement
      ↓
Thresholding
      ↓
Deskew
      ↓
Processed Image
```

The processed image is then passed to the OCR engine and relevant computer-vision modules.

---

# 8. Step 5 — OCR Processing

The OCR engine reads information from the processed cheque.

Example OCR output:

```text
MICR / Cheque Number: 102345
Account Number: ACC100001
Pay To: ABC TRADERS
Amount: 25,000
Date: 20/08/2026
```

The OCR engine also provides confidence information where supported.

Example:

```json
{
  "cheque_number": {
    "value": "102345",
    "confidence": 0.98
  },
  "payee_name": {
    "value": "ABC TRADERS",
    "confidence": 0.96
  },
  "amount": {
    "value": "25000",
    "confidence": 0.97
  }
}
```

---

# 9. Step 6 — Structured Data Extraction

The raw OCR output is converted into structured data.

Example:

```json
{
  "cheque_number": "102345",
  "account_number": "ACC100001",
  "routing_transit_number": "ROUT001",
  "payee_name": "ABC TRADERS",
  "amount": 25000.00,
  "date": "2026-08-20"
}
```

The extracted information is stored in the database.

---

# 10. Step 7 — Data Normalization

Before validation, the extracted data is normalized.

For example:

```text
OCR value:
" Rs. 25,000/- "

Normalized:
25000.00
```

Similarly:

```text
"abc traders"
       ↓
"ABC TRADERS"
```

Date formats are also standardized:

```text
20/08/2026
      ↓
2026-08-20
```

This ensures consistent comparison with banking records.

---

# 11. Step 8 — Banking Record Validation

The normalized cheque data is compared with the mock banking database.

For example:

### Extracted Data

```text
Account: ACC100001
Payee: ABC TRADERS
Amount: ₹25,000
Cheque: 102345
```

### Mock Banking Record

```text
Account: ACC100001
Status: ACTIVE
Registered Payee: ABC TRADERS
Cheque: 102345
```

The validation engine produces:

```text
Account Status       → PASS
Cheque Number        → PASS
Payee                → PASS
Cheque Date          → PASS
Cheque Series        → PASS
```

Overall:

```text
VALIDATION = PASS
```

---

# 12. Step 9 — Fraud Detection

The same cheque is passed through the fraud detection components.

```text
                    Cheque
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
  Tampering        Signature        Duplicate
  Detection         Analysis        Detection
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                Anomaly Detection
                       │
                       ▼
                 Fraud Indicators
```

For CHK001, the result could be:

```text
Tampering          → LOW
Signature          → MATCH
Duplicate          → NOT FOUND
Anomaly            → LOW
```

---

# 13. Step 10 — Risk Scoring

The validation and fraud results are combined.

Example:

```text
Validation Result       PASS
Tampering Score         LOW
Signature Result        MATCH
Duplicate Evidence     NONE
Anomaly Score           LOW
```

The risk engine produces a risk score.

Example:

```text
Risk Score = 12 / 100
Risk Level = LOW
```

**The actual scoring formula and thresholds will be finalized after testing and documented in `21_Risk_Scoring.md`.**

---

# 14. Step 11 — Decision Engine

The Decision Engine receives the final evidence.

For CHK001:

```text
Validation = PASS
Fraud Risk = LOW
Risk Score = 12
```

Therefore:

```text
                 DECISION
                    │
                    ▼
                 APPROVE
```

The result is stored in the database.

---

# 15. Example of a Rejected Cheque

Consider CHK003.

### Extracted information

```text
Account Number: ACC100003
Amount: ₹10,000
Payee: ABC TRADERS
```

### Banking record

```text
Account: ACC100003
Status: BLOCKED
```

Validation:

```text
Account Status → FAIL
```

Since account status is a critical validation failure:

```text
Validation Failure
       ↓
Decision Engine
       ↓
REJECT
```

The reason is recorded:

```text
REJECTION_REASON:
ACCOUNT_BLOCKED
```

---

# 16. Example of a Manual Review Case

Consider CHK004.

The system detects that a similar cheque has already been processed.

```text
Duplicate Detection
       ↓
Potential Duplicate
       ↓
Risk increases
       ↓
Decision Engine
       ↓
MANUAL REVIEW
```

The reviewer receives:

```text
Cheque Image
Cheque Details
Previous Cheque Reference
Similarity Score
Validation Results
Fraud Indicators
Risk Score
```

The reviewer can then make the final decision.

---

# 17. Data Flow for a Fraud Case

For a suspicious cheque:

```text
Cheque Image
     ↓
OCR
     ↓
Extracted Data
     ↓
Image Analysis
     ↓
Tampering Detected
     ↓
Fraud Indicator Generated
     ↓
Risk Score Increased
     ↓
Decision Engine
     ↓
MANUAL REVIEW / REJECT
```

The system should retain the evidence that contributed to the decision.

---

# 18. Data Flow Diagram — Level 0

At the highest level, the entire application can be represented as:

```text
                         ┌───────────────┐
                         │     USER      │
                         └───────┬───────┘
                                 │
                          Cheque Image
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ CHEQUE PROCESSING      │
                    │ SYSTEM                 │
                    └───────────┬────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
             OCR Data      Validation Data   Fraud Data
                │               │               │
                └───────────────┼───────────────┘
                                ▼
                         Risk / Decision
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
               APPROVE        REVIEW        REJECT
                  │             │             │
                  └─────────────┼─────────────┘
                                ▼
                          Audit Trail
```

---

# 19. Data Flow Diagram — Level 1

```text
                         USER
                           │
                           ▼
                  ┌────────────────┐
                  │ 1.0 CHEQUE     │
                  │ INPUT           │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ 2.0 IMAGE      │
                  │ PROCESSING     │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ 3.0 OCR &      │
                  │ EXTRACTION     │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ 4.0 VALIDATION │◄──────────┐
                  └───────┬────────┘           │
                          │                    │
                          ▼                    │
                  ┌────────────────┐           │
                  │ 5.0 FRAUD      │           │
                  │ DETECTION      │           │
                  └───────┬────────┘           │
                          │                    │
                          ▼                    │
                  ┌────────────────┐      ┌──────────────┐
                  │ 6.0 RISK       │      │ BANKING DATA │
                  │ SCORING        │      │ / MOCK DB    │
                  └───────┬────────┘      └──────────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │ 7.0 DECISION   │
                  │ ENGINE         │
                  └───────┬────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
           APPROVE      REVIEW      REJECT
              │           │           │
              └───────────┼───────────┘
                          ▼
                  ┌────────────────┐
                  │ 8.0 AUDIT &    │
                  │ REPORTING      │
                  └────────────────┘
```

---

# 20. Data Flow Diagram — Level 2: OCR Pipeline

```text
Cheque Image
     │
     ▼
Image Quality Check
     │
     ▼
Preprocessing
     │
     ▼
Region Detection
     │
     ├───────────────┐
     ▼               ▼
Text Regions     Signature Region
     │
     ▼
OCR Engine
     │
     ▼
Raw OCR Output
     │
     ▼
Field Extraction
     │
     ▼
Normalization
     │
     ▼
Structured Cheque Data
```

---

# 21. Data Flow Diagram — Level 2: Fraud Pipeline

```text
                    Cheque
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    Image Data    Transaction    Cheque Data
        │             Data          │
        ▼             ▼             ▼
   Tampering      Anomaly        Rule-Based
   Detection      Detection      Analysis
        │             │             │
        ▼             ▼             ▼
   Signature      Anomaly       Fraud Rules
   Analysis        Score          Result
        │             │             │
        └─────────────┼─────────────┘
                      ▼
               Fraud Evidence
                      │
                      ▼
                Risk Scoring
```

---

# 22. Data Storage Flow

The system will maintain different types of data separately.

```text
                     PROCESSING
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   Structured Data   Image Data     Audit Data
          │              │              │
          ▼              ▼              ▼
      PostgreSQL     File/Object      PostgreSQL
                      Storage
```

### Structured Data

Examples:

* Cheque ID
* Account number/reference
* Payee
* Amount
* Date
* OCR results
* Validation results
* Risk score
* Decision

### Image Data

Examples:

* Original cheque
* Processed cheque
* Relevant image regions

### Audit Data

Examples:

* Processing events
* User actions
* Decision changes
* Review actions

---

# 23. Data Lifecycle

Each cheque follows a defined lifecycle:

```text
UPLOADED
    ↓
VALIDATING
    ↓
PREPROCESSING
    ↓
OCR_PROCESSING
    ↓
DATA_EXTRACTED
    ↓
VALIDATING
    ↓
FRAUD_ANALYSIS
    ↓
RISK_ASSESSMENT
    ↓
DECISION_PENDING
    │
    ├───────────────┐
    ▼               ▼
 APPROVED         REVIEW
                    │
                    ▼
              FINAL DECISION
                    │
                    ▼
              APPROVED/REJECTED

OR

REJECTED
```

The exact status names can be standardized during backend implementation.

---

# 24. Sample Data Flow — Valid Cheque

```text
CHK001.jpg
    ↓
OCR
    ↓
{
  Account: ACC100001
  Payee: ABC TRADERS
  Amount: ₹25,000
  Date: 20-08-2026
}
    ↓
Banking Record Match
    ↓
All Validation Checks PASS
    ↓
Fraud Checks PASS
    ↓
Risk Score: LOW
    ↓
APPROVE
```

---

# 25. Sample Data Flow — Duplicate Cheque

```text
CHK004.jpg
    ↓
OCR
    ↓
Cheque Number: 102348
Account: ACC100001
Amount: ₹25,000
    ↓
Database Search
    ↓
Existing Matching Record Found
    ↓
Duplicate Indicator
    ↓
Risk Score Increased
    ↓
MANUAL REVIEW
    ↓
Reviewer Investigation
    ↓
Final Decision
```

---

# 26. Sample Data Flow — Invalid Account

```text
CHK003.jpg
    ↓
OCR
    ↓
Account: ACC100003
    ↓
Mock Banking Database
    ↓
Account Status = BLOCKED
    ↓
Critical Validation Failure
    ↓
REJECT
    ↓
Audit Event Recorded
```

---

# 27. Sample Data Flow — Suspicious/Tampered Cheque

```text
Suspicious Cheque
       ↓
Image Preprocessing
       ↓
Tampering Analysis
       ↓
Possible Alteration Detected
       ↓
Fraud Indicator
       ↓
Additional Fraud Checks
       ↓
Risk Score = HIGH
       ↓
MANUAL REVIEW / REJECT
       ↓
Audit Evidence Stored
```

---

# 28. Proposed Mock Data Files

To make the project fully demonstrable, the following synthetic data files should eventually be created under:

```text
data/
├── mock_banking_data/
│   ├── accounts.csv
│   ├── cheque_records.csv
│   ├── customers.csv
│   ├── payees.csv
│   ├── transactions.csv
│   └── reference_signatures/
│
├── sample_cheques/
│   ├── valid/
│   ├── duplicate/
│   ├── invalid/
│   ├── suspicious/
│   └── low_quality/
│
└── test_data/
    ├── expected_ocr_results.json
    ├── expected_validation_results.json
    ├── expected_fraud_results.json
    └── expected_decisions.json
```

These files will allow us to test the entire pipeline without using real banking/customer information.

---

# 29. Data Flow Traceability

Every cheque should have a unique identifier that connects all processing stages.

For example:

```text
Cheque ID:
CHK-2026-000001
```

The same ID should connect:

```text
Image
 ↓
OCR Result
 ↓
Extracted Data
 ↓
Validation Results
 ↓
Fraud Results
 ↓
Risk Assessment
 ↓
Decision
 ↓
Manual Review
 ↓
Audit Trail
```

This is critical for debugging, reporting, compliance, and auditability.

---

# 30. Data Flow Performance Requirement

The complete processing pipeline is targeted to complete within:

> **Less than 30 seconds per cheque under the defined prototype test environment and workload.**

The processing time should be measured separately for:

* Upload
* Preprocessing
* OCR
* Extraction
* Validation
* Fraud detection
* Risk scoring
* Decision generation

This will allow us to identify bottlenecks during performance evaluation.

---

# 31. Data Quality and Error Handling

The system must not blindly trust OCR output.

For example:

```text
OCR Confidence = LOW
        ↓
Data Reliability Concern
        ↓
Additional Processing / Manual Review
```

Similarly:

```text
Missing Account Number
        ↓
Validation Cannot Be Completed
        ↓
Do NOT Automatically Approve
        ↓
REVIEW / ERROR
```

This is especially important because OCR errors can otherwise propagate into validation and fraud decisions.

---

# 32. Privacy and Synthetic Data

For the prototype:

> **No real customer banking information should be used.**

All sample records should be synthetic.

Example:

```text
Customer:
Demo Customer 001

Account:
ACC100001

Payee:
ABC TRADERS

Cheque:
102345
```

If actual cheque images are used for testing, they must be handled according to the applicable privacy and organizational requirements, with sensitive information appropriately protected or anonymized.

---

# 33. Final End-to-End Data Flow

The complete system data flow is:

```text
                    ┌─────────────────┐
                    │ Sample / User   │
                    │ Cheque Image    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ File Validation │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Preprocessing   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ OCR Processing  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Data Extraction │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Normalization   │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌───────────────┐      ┌───────────────┐
          │  Validation   │      │ Fraud Analysis│
          │    Engine     │      │    Engine     │
          └───────┬───────┘      └───────┬───────┘
                  │                     │
                  │       ┌─────────────┤
                  │       │             │
                  │       ▼             ▼
                  │   Signature     Duplicate
                  │   Tampering     Anomaly
                  │
                  └──────────┬──────────┘
                             ▼
                    ┌─────────────────┐
                    │  Risk Scoring   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Decision Engine │
                    └───────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          APPROVE         REVIEW        REJECT
                            │
                            ▼
                     Manual Reviewer
                            │
                            ▼
                      Final Decision
                            │
                            ▼
                     ┌─────────────┐
                     │ Audit Trail │
                     └──────┬──────┘
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       PostgreSQL                    File/Object
        Database                       Storage
             │
             ▼
       Dashboard &
        Reporting
```

---

# 34. Summary

The proposed data flow establishes a complete and traceable path from **cheque image ingestion to final decision**. The system will use **synthetic sample cheque images and mock banking records** to demonstrate and validate the complete workflow.

The key principle is that every processing stage produces structured output that becomes the input for the next stage:

> **Image → OCR → Extraction → Normalization → Validation → Fraud Analysis → Risk Score → Decision → Audit**

This design supports the project's target outcomes of automated cheque digitization, high OCR accuracy, fraud detection, reduced manual verification effort, faster processing, and complete traceability of every validation decision.
