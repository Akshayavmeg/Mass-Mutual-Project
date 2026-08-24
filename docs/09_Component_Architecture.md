# Component Architecture

# 09. Component Architecture

## 1. Introduction

The **Component Architecture** defines the major software components of the AI-Powered Cheque Scanning, Validation & Fraud Detection System and explains how these components interact with one another.

The system is divided into independent but interconnected components. Each component has a clearly defined responsibility, input, output, and interface.

The primary objective of this architecture is to ensure:

* Separation of responsibilities
* Low coupling between modules
* Reusability
* Maintainability
* Testability
* Scalability
* Clear data flow
* Easy replacement of individual technologies

The prototype will preferably follow a **modular monolithic architecture**, where the components are maintained within a single backend application but remain logically separated.

---

# 2. Component Architecture Overview

The major components are:

1. Frontend / Dashboard
2. API Gateway / REST API
3. Authentication & Authorization
4. Cheque Input Manager
5. Image Validation Component
6. Image Preprocessing Component
7. OCR Component
8. Cheque Data Extraction Component
9. Data Normalization Component
10. Validation Engine
11. Banking Data Repository
12. Fraud Detection Engine
13. Tampering Detection Component
14. Signature Analysis Component
15. Duplicate Detection Component
16. Anomaly Detection Component
17. Risk Scoring Engine
18. Decision Engine
19. Manual Review Component
20. Audit Trail Component
21. Reporting Component
22. Database Component
23. File/Object Storage Component
24. Model & Configuration Management Component

---

# 3. High-Level Component Diagram

```text
                         ┌───────────────────────┐
                         │        USER           │
                         │ Operator / Reviewer   │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    FRONTEND / UI      │
                         │ Dashboard / Upload /  │
                         │ Manual Review         │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       REST API        │
                         │ Request / Response    │
                         │ Validation            │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
      │ Authentication│      │ Cheque Input  │      │ Review /      │
      │ & Authorization│     │ Manager       │      │ Decision API  │
      └───────────────┘      └───────┬───────┘      └───────────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Image Validation   │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Image Preprocessing│
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │    OCR Component   │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Data Extraction    │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Data Normalization │
                           └─────────┬──────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
          ┌───────────────────┐             ┌───────────────────┐
          │ Validation Engine │             │ Fraud Detection   │
          └─────────┬─────────┘             │ Engine            │
                    │                       └─────────┬─────────┘
                    │                                 │
                    │                  ┌──────────────┼──────────────┐
                    │                  │              │              │
                    │                  ▼              ▼              ▼
                    │             Tampering      Signature      Duplicate
                    │             Detection      Analysis       Detection
                    │                  │              │              │
                    │                  └──────────────┼──────────────┘
                    │                                 │
                    │                                 ▼
                    │                         Anomaly Detection
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │   Risk Scoring     │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │   Decision Engine  │
                           └──────┬─────┬───────┘
                                  │     │
                         ┌────────┘     └────────┐
                         ▼                       ▼
                    ┌──────────┐          ┌──────────────┐
                    │ APPROVE  │          │ MANUAL REVIEW│
                    └────┬─────┘          └──────┬───────┘
                         │                       │
                         │                       ▼
                         │                ┌──────────────┐
                         │                │ Final Review │
                         │                └──────┬───────┘
                         │                       │
                         └───────────┬───────────┘
                                     ▼
                              ┌───────────────┐
                              │ Audit Trail   │
                              └───────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
             │ PostgreSQL  │  │ File/Object  │  │ Reporting / │
             │ Database    │  │ Storage      │  │ Dashboard   │
             └─────────────┘  └──────────────┘  └─────────────┘
```

---

# 4. Frontend / Dashboard Component

## Purpose

The Frontend provides the user interface through which authorized users interact with the system.

## Main Responsibilities

* User login
* Cheque upload
* Processing status display
* Cheque result visualization
* Fraud alert visualization
* Manual review
* Dashboard statistics
* Reports
* Audit history

## Inputs

* User actions
* Cheque files
* Review decisions
* Search/filter parameters

## Outputs

* API requests
* Processing status
* Decision information
* Reports and visualizations

## Proposed Technology

* React
* Vite
* HTML/CSS
* JavaScript/TypeScript as selected during implementation

---

# 5. REST API Component

The REST API acts as the communication interface between the frontend and backend.

## Responsibilities

* Receive requests
* Validate request structure
* Authenticate requests
* Invoke backend services
* Return structured responses
* Handle API errors

Example endpoints:

```text
POST /api/v1/cheques
GET  /api/v1/cheques/{id}
POST /api/v1/cheques/{id}/process
GET  /api/v1/cheques/{id}/results

GET  /api/v1/reviews
POST /api/v1/reviews/{id}/decision

GET  /api/v1/dashboard/summary
GET  /api/v1/audit/{cheque_id}
```

---

# 6. Authentication and Authorization Component

This component controls access to system functionality.

## Responsibilities

* User authentication
* Session/token management
* Role verification
* Permission enforcement
* Access logging

Example roles:

```text
ADMIN
OPERATOR
REVIEWER
AUDITOR
```

The component ensures that a user can access only the operations permitted by their assigned role.

---

# 7. Cheque Input Manager

The Cheque Input Manager is responsible for receiving cheque images.

## Supported Inputs

* JPEG
* JPG
* PNG
* PDF

## Responsibilities

1. Receive file
2. Validate file type
3. Validate file size
4. Generate processing ID
5. Store original image
6. Create cheque-processing record
7. Send the image to preprocessing

Example:

```text
Upload
   ↓
Generate ID
   ↓
CHK-2026-000001
   ↓
Store Image
   ↓
Start Processing
```

---

# 8. Image Validation Component

This component performs initial quality and integrity checks.

## Checks

* File integrity
* Image dimensions
* Resolution
* Blur
* Orientation
* Corruption
* Unsupported format

## Output

```json
{
  "valid": true,
  "quality_score": 0.91,
  "issues": []
}
```

If the image is not suitable for reliable processing, the system should route it to an appropriate error or review state.

---

# 9. Image Preprocessing Component

This component prepares images for OCR and fraud analysis.

## Operations

* Grayscale conversion
* Noise reduction
* Contrast enhancement
* Thresholding
* Resizing
* Deskewing
* Rotation correction
* Background normalization

## Proposed Technology

**OpenCV**

## Input

Original cheque image.

## Output

Processed cheque image.

---

# 10. OCR Component

The OCR component converts image information into text.

## Possible OCR Implementations

* Tesseract
* Google Vision
* Azure AI Vision

The architecture should use an OCR abstraction so that the OCR provider can be changed without modifying the entire processing pipeline.

## Output

```text
Raw Text
+
Bounding Boxes
+
OCR Confidence
```

where supported by the selected OCR engine.

---

# 11. Cheque Data Extraction Component

This component converts raw OCR output into structured cheque information.

## Extracted Fields

```text
Cheque Number
Account Number
Routing / Transit Number
Payee
Amount
Date
Currency
MICR Information
Signature Region
```

Example:

```json
{
  "cheque_number": "102345",
  "account_number": "XXXXXX7890",
  "payee_name": "ABC TRADERS",
  "amount": 25000.00,
  "date": "2026-08-20"
}
```

---

# 12. Data Normalization Component

OCR output can contain formatting inconsistencies.

The normalization component converts extracted information into a standardized format.

### Example

```text
OCR:
"25,000/-"

Normalized:
25000.00
```

Other normalization operations include:

* Date formatting
* Amount formatting
* Whitespace removal
* Case normalization
* Account-number normalization
* Payee-name normalization

This improves consistency during validation.

---

# 13. Validation Engine

The Validation Engine evaluates the extracted information against configured rules and banking records.

## Components

```text
Account Validator
Cheque Series Validator
Date Validator
Payee Validator
Amount Validator
Duplicate Validator
Cross-Field Validator
```

Each validator should return a structured result.

Example:

```json
{
  "rule": "ACCOUNT_STATUS",
  "result": "PASS",
  "message": "Account is active"
}
```

---

# 14. Banking Data Repository

The Banking Data Repository provides access to mock or approved banking records.

For the prototype, the repository may contain:

```text
Accounts
Cheque Records
Transactions
Payee Information
Cheque Series
Reference Signatures
```

The repository abstraction prevents the validation engine from being tightly coupled to a particular database implementation.

---

# 15. Fraud Detection Engine

The Fraud Detection Engine coordinates the different fraud-analysis components.

It collects:

* Tampering results
* Signature analysis
* Duplicate evidence
* Anomaly scores
* Rule-based fraud indicators

and converts them into a unified fraud assessment.

```text
Tampering ────────┐
Signature ────────┤
Duplicate ────────┼──→ Fraud Detection Engine
Anomaly ──────────┤
Rules ────────────┘
                         │
                         ▼
                  Fraud Indicators
```

---

# 16. Tampering Detection Component

This component analyzes the cheque image for possible alterations.

Potential regions include:

* Payee
* Amount
* Date
* Cheque number
* Signature area

Possible techniques include:

* Image comparison
* Region-level analysis
* Texture analysis
* Edge analysis
* Image-forensics techniques

The component should produce **evidence or a suspicion score**, not automatically declare fraud without sufficient evidence.

---

# 17. Signature Analysis Component

This component analyzes the signature region.

## Processing

```text
Cheque Image
     ↓
Signature Region
     ↓
Preprocessing
     ↓
Feature Extraction
     ↓
Reference Signature
     ↓
Similarity Analysis
     ↓
Signature Result
```

Possible outputs:

```text
MATCH
LOW_SIMILARITY
REVIEW
REFERENCE_NOT_AVAILABLE
```

Signature analysis is treated as one fraud signal among several.

---

# 18. Duplicate Detection Component

This component determines whether a cheque may have already been processed.

## Detection Methods

### Record Matching

Compare:

* Cheque number
* Account
* Amount
* Date
* Payee

### Image Hash

Generate a fingerprint of the image.

### Image Similarity

Compare the current image with previous cheque images where appropriate.

Output:

```json
{
  "duplicate_candidate": true,
  "similarity_score": 0.94,
  "matched_cheque_id": "CHK-2026-000021"
}
```

---

# 19. Anomaly Detection Component

The Anomaly Detection component identifies unusual transaction behavior.

Potential inputs include:

* Amount
* Transaction frequency
* Account activity
* Payee patterns
* Historical transaction behavior

The component may use statistical methods or machine-learning algorithms depending on dataset availability.

Output:

```text
Anomaly Score
+
Detected Features
+
Explanation
```

---

# 20. Fraud Rule Engine

The Rule Engine evaluates predefined fraud conditions.

Example:

```text
RULE-001:
If cheque has already been processed
→ DUPLICATE_ALERT

RULE-002:
If account is inactive
→ ACCOUNT_ALERT

RULE-003:
If critical cheque field is inconsistent
→ DATA_INCONSISTENCY_ALERT

RULE-004:
If configured high-risk condition is satisfied
→ HIGH_RISK_ALERT
```

Rules should be configurable and versioned.

---

# 21. Risk Scoring Component

The Risk Scoring Component combines signals from multiple modules.

Conceptually:

```text
Validation Results
       +
OCR Confidence
       +
Tampering Evidence
       +
Signature Result
       +
Duplicate Evidence
       +
Anomaly Score
       ↓
Risk Scoring
       ↓
Risk Score
       ↓
LOW / MEDIUM / HIGH
```

The scoring methodology should be documented and tested before being used for final decisions.

---

# 22. Decision Engine Component

The Decision Engine converts system evidence into a workflow state.

Possible outputs:

```text
APPROVE
REVIEW
REJECT
```

Example:

```text
IF critical validation failure
        → REJECT

ELSE IF high-risk fraud indicators
        → REVIEW / REJECT

ELSE IF insufficient evidence
        → REVIEW

ELSE
        → APPROVE
```

The exact thresholds will be configurable.

---

# 23. Manual Review Component

The Manual Review Component provides a human-in-the-loop workflow.

The reviewer can see:

```text
Original Cheque
Processed Image
Extracted Data
OCR Confidence
Validation Results
Fraud Indicators
Risk Score
Decision Recommendation
Audit History
```

The reviewer can then submit:

```text
FINAL APPROVAL
FINAL REJECTION
REQUEST ADDITIONAL REVIEW
```

along with a reason/comment.

---

# 24. Audit Trail Component

The Audit Trail Component records significant system activities.

## Events

* Upload
* Processing start
* Preprocessing
* OCR
* Extraction
* Validation
* Fraud analysis
* Risk scoring
* Decision
* Review assignment
* Review decision
* Final status

Example:

```json
{
  "event_type": "FRAUD_ANALYSIS_COMPLETED",
  "cheque_id": "CHK-2026-000001",
  "timestamp": "2026-08-20T12:00:12",
  "actor": "SYSTEM",
  "status": "COMPLETED"
}
```

---

# 25. Database Component

The database stores structured application data.

Major entities include:

```text
Users
Cheques
Cheque_Images
OCR_Results
Extracted_Fields
Validation_Results
Fraud_Indicators
Risk_Assessments
Decisions
Manual_Reviews
Audit_Events
Model_Versions
Configurations
```

PostgreSQL is the preferred database for the prototype.

---

# 26. File/Object Storage Component

Cheque images can be stored separately from structured database records.

The database stores metadata/reference information, while the file/object storage contains:

```text
Original Cheque Image
Processed Cheque Image
Derived Image Regions
Supporting Evidence
```

This separation prevents large binary files from unnecessarily increasing the size of relational database tables.

---

# 27. Reporting Component

The Reporting Component converts stored processing information into useful operational reports.

Examples:

* Daily cheque-processing report
* Approval/rejection report
* Fraud-alert report
* Manual-review report
* OCR performance report
* Processing-time report
* Risk-distribution report

---

# 28. Model Management Component

The Model Management Component maintains information about AI/ML models used by the system.

It should record:

* Model name
* Model version
* Training dataset/version
* Training date
* Evaluation metrics
* Deployment status

Example:

```text
Fraud Model
Version: 1.0
Accuracy: [Measured Value]
Precision: [Measured Value]
Recall: [Measured Value]
F1 Score: [Measured Value]
Status: Evaluation
```

Actual metrics should only be recorded after evaluation.

---

# 29. Configuration Management Component

Configuration values should be separated from application logic.

Examples:

```text
OCR confidence threshold
Risk thresholds
Duplicate similarity threshold
Allowed file formats
Maximum file size
Processing timeout
Fraud rule configuration
```

Example:

```yaml
risk:
  low_max: 30
  medium_max: 70
  high_min: 71
```

These values are examples and must be finalized through testing.

---

# 30. Component Interaction Sequence

A simplified sequence of component interactions is:

```text
User
 │
 ▼
Frontend
 │
 ▼
REST API
 │
 ▼
Cheque Input Manager
 │
 ▼
Image Validation
 │
 ▼
Image Preprocessing
 │
 ▼
OCR Component
 │
 ▼
Data Extraction
 │
 ▼
Normalization
 │
 ├───────────────┐
 ▼               ▼
Validation    Fraud Engine
 │               │
 │       ┌───────┼────────┐
 │       ▼       ▼        ▼
 │   Tampering Signature Duplicate
 │               │        │
 │               └───┬────┘
 │                   ▼
 │             Anomaly Detection
 │                   │
 └───────────┬───────┘
             ▼
        Risk Scoring
             │
             ▼
        Decision Engine
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    APPROVE REVIEW REJECT
             │
             ▼
       Manual Review
             │
             ▼
        Final Decision
             │
             ▼
         Audit Trail
             │
             ▼
        Database/Storage
```

---

# 31. Component Dependency Matrix

| Component           | Depends On                 | Provides                  |
| ------------------- | -------------------------- | ------------------------- |
| Frontend            | REST API                   | User interaction          |
| REST API            | Application services       | API interface             |
| Authentication      | User database              | Access control            |
| Cheque Input        | File storage, database     | Cheque record             |
| Image Validation    | Image processing libraries | Quality result            |
| Preprocessing       | OpenCV                     | Processed image           |
| OCR                 | Processed image            | OCR output                |
| Data Extraction     | OCR output                 | Structured fields         |
| Normalization       | Extracted fields           | Standardized data         |
| Validation          | Banking repository         | Validation results        |
| Fraud Engine        | Fraud components           | Fraud indicators          |
| Tampering Detection | Cheque image               | Tampering evidence        |
| Signature Analysis  | Signature/reference data   | Similarity result         |
| Duplicate Detection | Database/images            | Duplicate evidence        |
| Anomaly Detection   | Historical data            | Anomaly score             |
| Risk Scoring        | Validation + fraud results | Risk score                |
| Decision Engine     | Risk + validation          | Decision                  |
| Manual Review       | Decision + evidence        | Final review decision     |
| Audit Trail         | All major modules          | Audit records             |
| Reporting           | Database                   | Reports                   |
| Model Management    | Model metadata             | Model version information |
| Configuration       | Configuration store        | Runtime settings          |

---

# 32. Component Design Principles

Each component should follow these principles:

### Single Responsibility

Each component should have one clearly defined primary responsibility.

### Loose Coupling

Components should communicate through well-defined interfaces.

### High Cohesion

Related processing logic should remain within the same component.

### Testability

Each component should be independently testable where practical.

### Replaceability

An OCR provider or ML model should be replaceable without rewriting unrelated modules.

### Traceability

Important processing results should be linked to the cheque's unique Processing ID.

---

# 33. Proposed Backend Module Structure

Per ADR-0006 (Overall Architecture Style), the backend follows a **layer-based top-level structure** (consistent with `docs/36_Development_Guidelines.md` §4), with the processing-stage domains described in this document nested inside `app/services/`:

```text
apps/
└── backend/
    ├── app/
    │   ├── api/
    │   ├── core/
    │   ├── models/
    │   ├── repositories/
    │   ├── schemas/
    │   ├── services/
    │   │   ├── auth/
    │   │   ├── cheque/
    │   │   ├── preprocessing/
    │   │   ├── ocr/
    │   │   ├── extraction/
    │   │   ├── validation/
    │   │   ├── fraud/
    │   │   │   ├── tampering/
    │   │   │   ├── signature/
    │   │   │   ├── duplicate/
    │   │   │   └── anomaly/
    │   │   ├── risk/
    │   │   ├── decision/
    │   │   ├── review/
    │   │   ├── audit/
    │   │   └── reporting/
    │   └── utils/
    │
    ├── tests/
    └── main.py
```

This reconciles the stage-based grouping shown above with the layer-based top-level structure in `36_Development_Guidelines.md` §4: `api/`, `core/`, `models/`, `repositories/`, and `schemas/` hold the cross-cutting layers (routing, configuration/logging, ORM models, data-access, and request/response schemas respectively), while each processing-stage component described earlier in this document (Cheque Input Manager, Image Preprocessing, OCR, Extraction, Validation Engine, Fraud Detection Engine and its sub-components, Risk Scoring, Decision Engine, Manual Review, Audit Trail, Reporting) becomes a subpackage under `app/services/`. This is a **logical structure**; minor implementation adjustments are expected during development, but the top-level layering should not diverge from ADR-0006 without a corresponding ADR update.

---

# 34. End-to-End Component Responsibility

The complete responsibility chain is:

```text
Frontend
   ↓
Accepts user input

API
   ↓
Controls communication

Cheque Input
   ↓
Registers cheque

Image Validation
   ↓
Checks image suitability

Preprocessing
   ↓
Improves image

OCR
   ↓
Reads text

Extraction
   ↓
Identifies cheque fields

Normalization
   ↓
Standardizes values

Validation
   ↓
Checks banking/business rules

Fraud Components
   ↓
Identify suspicious indicators

Risk Scoring
   ↓
Combines evidence

Decision Engine
   ↓
Determines workflow

Manual Review
   ↓
Handles uncertain cases

Audit
   ↓
Records processing history

Database/Storage
   ↓
Persists system information

Dashboard/Reporting
   ↓
Provides operational visibility
```

---

# 35. Component Architecture Summary

> **The Component Architecture divides the AI-Powered Cheque Scanning, Validation & Fraud Detection System into specialized components responsible for user interaction, API communication, cheque intake, image processing, OCR, data extraction, validation, fraud analysis, risk scoring, decision management, manual review, auditing, storage, and reporting. The components are logically separated and communicate through defined interfaces. The prototype will follow a modular design within a unified backend application, allowing each component to be independently tested and replaced where necessary. This architecture provides a clear foundation for implementing the complete cheque-processing pipeline while maintaining scalability, traceability, security, and future extensibility.**
