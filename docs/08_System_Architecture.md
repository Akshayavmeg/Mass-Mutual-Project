# System Architecture

# 08. System Architecture

## 1. Introduction

The **AI-Powered Cheque Scanning, Validation & Fraud Detection System** follows a modular, layered architecture designed to process cheque images from initial submission through OCR extraction, validation, fraud analysis, risk assessment, decision-making, and audit logging.

The architecture separates the **presentation, API, processing, AI/ML, data, and infrastructure concerns** so that individual components can be developed, tested, replaced, and scaled independently.

The primary architectural objective is to create a system that is:

* Modular
* Scalable
* Secure
* Auditable
* Explainable
* Maintainable
* Extensible
* Suitable for human-in-the-loop processing

---

# 2. Architectural Style

The proposed system uses a **layered modular architecture with service-oriented components**.

The main logical layers are:

1. **Presentation Layer**
2. **API and Application Layer**
3. **Cheque Processing Layer**
4. **AI/ML and Computer Vision Layer**
5. **Data Access Layer**
6. **Data Storage Layer**
7. **Infrastructure and Security Layer**

For the initial prototype, these components may be implemented as a **modular monolithic application** rather than deploying every component as an independent microservice.

This approach reduces unnecessary deployment complexity while keeping the internal modules sufficiently separated for future service extraction.

---

# 3. High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                              │
│   Web Dashboard     Cheque Upload     Manual Review UI       │
│   Reports           Risk Visualization                       │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTPS / REST API
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    API / APPLICATION LAYER                   │
│                                                              │
│ Authentication │ Authorization │ Request Validation          │
│ Cheque API     │ Review API    │ Reporting API              │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  CHEQUE PROCESSING LAYER                     │
│                                                              │
│ Input Validation → Preprocessing → OCR → Extraction          │
│                         │                                    │
│                         ▼                                    │
│             Validation + Fraud Analysis                      │
│                         │                                    │
│                         ▼                                    │
│                Risk Scoring → Decision                       │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ▼                      ▼
┌────────────────────────┐   ┌────────────────────────────────┐
│ AI / ML & COMPUTER     │   │       VALIDATION SERVICES       │
│ VISION LAYER           │   │                                │
│                        │   │ Mock Banking Records           │
│ OCR                    │   │ Account Validation             │
│ OpenCV                 │   │ Cheque Validation              │
│ Tampering Detection    │   │ Payee Validation               │
│ Signature Analysis     │   │ Duplicate Validation            │
│ Anomaly Detection      │   │ Business Rules                 │
│ Fraud Models           │   │                                │
└────────────┬───────────┘   └──────────────┬─────────────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                     DATA ACCESS LAYER                        │
│                                                              │
│ Repositories │ ORM/Data Access │ Transaction Management      │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│                                                              │
│ PostgreSQL / SQL Database                                    │
│                                                              │
│ Cheques │ OCR Results │ Validation │ Fraud │ Decisions       │
│ Reviews │ Users │ Audit Logs │ Model Metadata                │
│                                                              │
│ Object/File Storage → Original & Processed Cheque Images     │
└──────────────────────────────────────────────────────────────┘
```

---

# 4. Presentation Layer

The Presentation Layer provides interfaces for system users.

## 4.1 Dashboard

The dashboard provides an overview of system activity.

It displays:

* Total cheques processed
* Approved cheques
* Review cases
* Rejected cheques
* Fraud alerts
* Risk distribution
* Processing time
* OCR performance
* Validation statistics

---

## 4.2 Cheque Upload Interface

Authorized users can submit cheque images through the web interface.

Supported formats:

* JPEG/JPG
* PNG
* PDF

The interface should provide basic feedback regarding:

* Upload status
* File validation
* Processing status
* Processing ID
* Final decision

---

## 4.3 Manual Review Interface

Reviewers can inspect cases requiring human intervention.

The interface should display:

```text
Original Image
      +
Extracted Fields
      +
OCR Confidence
      +
Validation Results
      +
Fraud Indicators
      +
Risk Score
      +
Decision Recommendation
      +
Review History
```

The reviewer can then record the final decision and comments.

---

# 5. API and Application Layer

The API Layer acts as the communication boundary between the frontend and backend.

A REST-based API is proposed for the prototype.

## Responsibilities

* Receive client requests
* Validate request parameters
* Authenticate users
* Authorize operations
* Invoke application services
* Return structured responses
* Handle errors
* Record relevant audit events

Example API categories:

```text
POST   /api/v1/cheques
GET    /api/v1/cheques/{id}
POST   /api/v1/cheques/{id}/process
GET    /api/v1/cheques/{id}/results

GET    /api/v1/reviews
POST   /api/v1/reviews/{id}/decision

GET    /api/v1/dashboard/summary
GET    /api/v1/reports

GET    /api/v1/audit/{cheque_id}
```

The complete API contract will be documented separately in:

`26_API_Specification.md`

---

# 6. Cheque Processing Layer

The Cheque Processing Layer contains the core business workflow.

The processing sequence is:

```text
Cheque Upload
      ↓
File Validation
      ↓
Image Preprocessing
      ↓
OCR
      ↓
Data Extraction
      ↓
Validation
      ↓
Fraud Detection
      ↓
Risk Scoring
      ↓
Decision Engine
      ↓
Approve / Review / Reject
```

Each processing stage should have a clearly defined input and output.

---

# 7. Image Processing Architecture

The image-processing pipeline is responsible for preparing cheque images for downstream analysis.

```text
Original Cheque
      │
      ▼
Format Validation
      │
      ▼
Image Quality Check
      │
      ▼
Grayscale
      │
      ▼
Noise Reduction
      │
      ▼
Contrast Enhancement
      │
      ▼
Thresholding
      │
      ▼
Deskew / Rotation
      │
      ▼
Region Detection
      │
      ▼
Processed Image
```

OpenCV can be used for these operations.

The detailed implementation will be described in:

`13_Image_Preprocessing.md`

---

# 8. OCR Architecture

The OCR subsystem converts cheque images into machine-readable information.

```text
Processed Cheque Image
          │
          ▼
     OCR Engine
          │
          ├───────────────┐
          ▼               ▼
      Text Data      Text Coordinates
          │               │
          └───────┬───────┘
                  ▼
          OCR Confidence
                  │
                  ▼
          Extraction Module
```

The system should support an abstraction layer around the OCR provider.

This allows the implementation to use an engine such as:

* Tesseract
* Google Vision
* Azure AI Vision

without coupling the rest of the application directly to a single OCR implementation.

---

# 9. Data Extraction Architecture

Raw OCR results are converted into a standardized cheque representation.

Example:

```json
{
  "cheque_number": "102345",
  "account_number": "XXXXXX7890",
  "payee_name": "ABC TRADERS",
  "amount": 25000.00,
  "date": "2026-08-20",
  "currency": "INR",
  "ocr_confidence": 0.96
}
```

The extraction layer should also preserve sufficient information to identify which OCR output contributed to each extracted field.

This is important for troubleshooting and manual review.

---

# 10. Validation Architecture

The Validation Engine receives structured cheque data and compares it against configured rules and banking records.

```text
                 Extracted Cheque Data
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
        Account Check  Cheque Check  Date Check
             │            │            │
             ├────────────┼────────────┤
             ▼            ▼            ▼
        Payee Check   Amount Check  Duplicate Check
             │            │            │
             └────────────┼────────────┘
                          ▼
                 Validation Result
```

Each check should produce a structured result such as:

```text
PASS
FAIL
WARNING
NOT_AVAILABLE
```

This allows the decision engine to distinguish between different types of validation outcomes.

---

# 11. Fraud Detection Architecture

The Fraud Detection subsystem combines multiple fraud-analysis techniques.

```text
                       Cheque
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Image Analysis    Transaction Data    Extracted Data
        │                │                │
        ▼                ▼                ▼
  Tampering       Anomaly Detection   Rule Checks
        │                │                │
        ▼                ▼                ▼
 Signature         Behavioral Risk    Data Inconsistency
 Analysis
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                 Fraud Indicators
                         │
                         ▼
                  Risk Scoring
```

The system should not treat a single weak signal as definitive proof of fraud unless a specific business rule requires it.

---

# 12. Duplicate Detection Architecture

Duplicate detection can use multiple levels of comparison.

### Level 1 — Record-Based Detection

Compare:

* Cheque number
* Account number
* Amount
* Date
* Payee

### Level 2 — Image-Based Detection

Generate an image fingerprint/hash and compare it against previously processed cheque images.

### Level 3 — Similarity-Based Detection

Where appropriate, image similarity techniques can identify visually similar submissions even when minor image differences exist.

```text
New Cheque
    │
    ▼
Generate Metadata
    │
    ▼
Record Comparison
    │
    ▼
Image Hash Comparison
    │
    ▼
Similarity Analysis
    │
    ▼
Duplicate Evidence
```

---

# 13. Signature Analysis Architecture

Signature analysis is treated as a supporting fraud signal rather than an absolute fraud decision.

```text
Cheque Image
     │
     ▼
Signature Region
     │
     ▼
Image Processing
     │
     ▼
Feature Extraction
     │
     ▼
Reference Signature
     │
     ▼
Similarity Calculation
     │
     ▼
Signature Result
```

If no valid reference signature is available, the system should return:

```text
REFERENCE_NOT_AVAILABLE
```

rather than automatically treating the cheque as fraudulent.

---

# 14. Anomaly Detection Architecture

The anomaly detection subsystem analyzes transaction characteristics using available historical or mock data.

Potential features include:

* Transaction amount
* Transaction frequency
* Account activity
* Payee patterns
* Time-related patterns
* Historical transaction behavior

A simplified architecture is:

```text
Historical Transactions
          │
          ▼
Feature Preparation
          │
          ▼
Baseline / Model
          │
          ▼
New Cheque
          │
          ▼
Anomaly Score
          │
          ▼
Fraud Risk Engine
```

The exact ML algorithm will depend on the availability and quality of the dataset.

---

# 15. Risk Scoring Architecture

The Risk Scoring Engine aggregates evidence from validation and fraud-analysis modules.

Example conceptual model:

```text
OCR Confidence
       │
Validation Results
       │
Duplicate Evidence
       │
Signature Result
       │
Tampering Score
       │
Anomaly Score
       │
       ▼
┌─────────────────────┐
│   Risk Scoring      │
│      Engine         │
└──────────┬──────────┘
           ▼
     Risk Score
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
    LOW  MEDIUM  HIGH
```

The final scoring formula and thresholds will be defined and evaluated separately.

---

# 16. Decision Architecture

The Decision Engine consumes:

* Validation results
* Fraud indicators
* Risk score
* Processing exceptions
* Configured business rules

and generates a workflow outcome.

```text
             Risk + Validation Evidence
                       │
                       ▼
                Decision Engine
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       APPROVE       REVIEW       REJECT
```

### Example Conceptual Rules

```text
IF critical validation failure
    → REJECT

ELSE IF high fraud risk
    → REJECT or REVIEW
       depending on configured policy

ELSE IF uncertainty / insufficient evidence
    → REVIEW

ELSE
    → APPROVE
```

The exact decision policy should remain configurable rather than being permanently embedded in application code.

---

# 17. Data Architecture

The system uses a relational database for structured processing information.

A PostgreSQL-based implementation is proposed for the prototype.

The database stores:

```text
Users
Cheques
Cheque Metadata
OCR Results
Extracted Fields
Validation Results
Fraud Indicators
Risk Assessments
Decisions
Manual Reviews
Audit Events
Model Metadata
Configuration
```

Cheque images themselves may be stored in controlled file/object storage, with their metadata and references stored in the database.

---

# 18. Audit Architecture

Every major processing stage generates an auditable event.

```text
Upload
  ↓
Preprocessing
  ↓
OCR
  ↓
Extraction
  ↓
Validation
  ↓
Fraud Analysis
  ↓
Risk Scoring
  ↓
Decision
  ↓
Manual Review
  ↓
Final Decision
```

Each event should contain information such as:

* Event ID
* Processing/Cheque ID
* Event type
* Timestamp
* User/system actor
* Status
* Relevant metadata
* Model/configuration version where applicable

Sensitive information should not be unnecessarily duplicated in audit logs.

---

# 19. Security Architecture

Security controls are applied across multiple layers.

```text
                Authentication
                       │
                       ▼
                Authorization
                       │
                       ▼
             API Input Validation
                       │
                       ▼
               Business Services
                       │
                       ▼
              Database Access Control
                       │
                       ▼
              Secure Data Storage
```

Key principles include:

* Least privilege
* Role-based access
* Secure credential management
* Input validation
* Protected file access
* Encryption in transit
* Appropriate encryption at rest
* Audit logging
* PII minimization

---

# 20. User Roles

The architecture supports role-based access.

Example roles include:

### Administrator

Can manage:

* Users
* Roles
* Configuration
* System settings

### Operations User

Can:

* Upload cheques
* View processing status
* View results

### Fraud Analyst / Reviewer

Can:

* View flagged cheques
* Investigate fraud indicators
* Review evidence
* Record final decisions

### Auditor

Can:

* View audit records
* View reports
* Trace processing history

Access permissions will be implemented according to the actual application requirements.

---

# 21. Error and Failure Architecture

The system must handle failures without producing unsafe decisions.

For example:

```text
OCR Failure
    │
    ▼
Retry / Alternative OCR
    │
    ├── Success → Continue
    │
    └── Failure → Manual Review
```

Similarly:

```text
Banking Data Unavailable
          │
          ▼
Cannot Complete Validation
          │
          ▼
Do NOT Automatically Approve
          │
          ▼
Review / Retry
```

This ensures that missing critical verification information does not result in an unjustified approval.

---

# 22. Deployment Architecture

For the prototype, the recommended deployment structure is:

```text
                  User Browser
                       │
                       ▼
              Frontend Application
                       │
                    HTTPS
                       │
                       ▼
                Backend API
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   OCR Service     ML/CV Engine   Database
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 File Storage
```

The system can initially run locally and later be deployed to AWS, Azure, or GCP.

---

# 23. Prototype Architecture vs. Future Architecture

## Prototype

The initial implementation can use:

```text
Frontend
    ↓
Backend Application
    ↓
Processing Modules
    ↓
OCR / ML / OpenCV
    ↓
PostgreSQL
    ↓
Local/Object File Storage
```

This keeps development and debugging manageable.

## Future Production Architecture

A future production implementation could separate high-load components:

```text
Frontend
    ↓
API Gateway
    ↓
Application Services
    ├── Cheque Processing Service
    ├── OCR Service
    ├── Fraud Detection Service
    ├── Validation Service
    ├── Decision Service
    └── Review Service
             │
             ▼
       Message / Job Queue
             │
       ┌─────┴─────┐
       ▼           ▼
   Database    Object Storage
```

This separation should only be introduced if actual scalability, operational, or organizational requirements justify it.

---

# 24. Technology Mapping

| Architecture Component | Proposed Technology                                         |
| ---------------------- | ----------------------------------------------------------- |
| Frontend               | React / Vite                                                |
| Backend                | Python                                                      |
| API                    | REST                                                        |
| Image Processing       | OpenCV                                                      |
| OCR                    | Tesseract / Cloud OCR                                       |
| AI/ML                  | Python / Scikit-learn / TensorFlow where required           |
| Database               | PostgreSQL                                                  |
| Data Processing        | Pandas / NumPy where appropriate                            |
| Authentication         | Application-level authentication                            |
| File Storage           | Local storage for prototype / Object storage for deployment |
| Testing                | Pytest / API testing tools                                  |
| Containerization       | Docker, if required                                         |
| Cloud                  | AWS / Azure / GCP                                           |

The final technology choices should be recorded in the relevant Architecture Decision Records under:

`docs/adr/`

---

# 25. Architectural Principles

The following principles govern the design:

### 25.1 Separation of Concerns

OCR, validation, fraud detection, decision-making, and presentation should remain logically separate.

### 25.2 Modular Design

Modules should communicate through defined interfaces rather than tightly coupled internal implementations.

### 25.3 Explainability

Every risk-based decision should have identifiable contributing factors.

### 25.4 Auditability

Important system events must be traceable.

### 25.5 Human-in-the-Loop

Cases with uncertainty should be routed to authorized human reviewers.

### 25.6 Fail-Safe Processing

Critical service failures should not result in automatic approval.

### 25.7 Configurability

Business rules and decision thresholds should be configurable.

### 25.8 Extensibility

OCR engines, fraud models, and external data sources should be replaceable without redesigning the complete system.

---

# 26. End-to-End Architecture Flow

The complete architecture can be summarized as:

```text
┌─────────────────────────────────────────────────────┐
│                    USER / OPERATOR                  │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                WEB DASHBOARD / UI                   │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    REST API                         │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              CHEQUE PROCESSING ORCHESTRATOR         │
└─────────────────────────┬───────────────────────────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     Preprocessing       OCR          Data Extraction
          │               │                │
          └───────────────┼────────────────┘
                          ▼
              ┌─────────────────────┐
              │ Validation Engine   │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │ Fraud Detection     │
              │ Engine              │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │ Risk Scoring        │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │ Decision Engine     │
              └──────┬────┬────┬────┘
                     │    │    │
                     ▼    ▼    ▼
                  APPROVE REVIEW REJECT
                     │    │    │
                     └────┼────┘
                          ▼
                 ┌─────────────────┐
                 │   Audit Trail   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    Database     │
                 └─────────────────┘
```

---

# 27. Architecture Summary

> **The proposed system uses a layered, modular architecture in which the presentation layer communicates with backend application services through REST APIs. The backend orchestrates cheque input, image preprocessing, OCR, data extraction, banking validation, fraud analysis, risk scoring, and decision processing. AI/ML and computer-vision components provide specialized analysis, while a relational database stores structured cheque-processing information and audit records. Original and processed cheque images are maintained through controlled file/object storage. The architecture supports Approve, Manual Review, and Reject workflows and is designed to fail safely when critical verification services are unavailable. The prototype can be implemented as a modular monolith for simplicity, while the architecture allows selected components to be separated into independent services in a future production deployment if required.**

