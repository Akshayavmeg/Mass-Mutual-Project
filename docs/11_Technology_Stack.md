# Technology Stack

# 11. Technology Stack

## 1. Introduction

The **AI-Powered Cheque Scanning, Validation & Fraud Detection System** will use a combination of web technologies, OCR, image processing, artificial intelligence, database technologies, and cloud/deployment tools.

The technology stack is selected to support the complete cheque-processing pipeline:

```text
Cheque Image
     ↓
Frontend
     ↓
Backend API
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
Database
     ↓
Dashboard & Reports
```

---

# 2. Technology Stack Overview

| Layer             | Technology                | Purpose                                        |
| ----------------- | ------------------------- | ---------------------------------------------- |
| Frontend          | React.js                  | User interface and dashboard                   |
| Styling           | HTML5, CSS3, Tailwind CSS | UI structure and styling                       |
| Backend           | Python + FastAPI          | REST APIs and application logic                |
| OCR               | Tesseract OCR             | Extract text from cheque images                |
| Image Processing  | OpenCV                    | Image enhancement and cheque analysis          |
| AI/ML             | Python, Scikit-learn      | Fraud detection and anomaly detection          |
| Deep Learning     | TensorFlow/PyTorch        | Advanced fraud/signature models if required    |
| Database          | PostgreSQL                | Store cheque, validation, fraud and audit data |
| Data Processing   | Pandas, NumPy             | Dataset preparation and analysis               |
| API Testing       | Postman / REST Assured    | API testing                                    |
| Automated Testing | PyTest                    | Backend and ML testing                         |
| Browser Testing   | Playwright                | Frontend workflow testing                      |
| Version Control   | Git + GitHub              | Source-code management                         |
| Containerization  | Docker                    | Consistent application deployment              |
| Cloud             | AWS / Azure / GCP         | Optional deployment environment                |

---

# 3. Frontend Technology

## 3.1 React.js

**React.js** will be used to build the web-based user interface.

The frontend will provide:

* Cheque upload
* Processing status
* Extracted cheque information
* Validation results
* Fraud indicators
* Risk score
* Approve / Review / Reject status
* Manual review interface
* Dashboard
* Reports
* Audit history

Example workflow:

```text
User
 ↓
Upload Cheque
 ↓
Processing Screen
 ↓
Cheque Details
 ↓
Fraud Analysis
 ↓
Decision
```

---

## 3.2 HTML5

HTML5 provides the basic structure of the web application.

It will be used for:

* Forms
* File upload controls
* Tables
* Dashboard components
* Buttons
* Navigation elements

---

## 3.3 CSS3

CSS3 will be used for:

* Layout
* Spacing
* Responsive design
* Tables
* Forms
* Cards
* Status indicators

---

## 3.4 Tailwind CSS

Tailwind CSS can be used to create a consistent and responsive dashboard.

Example UI elements:

```text
┌────────────────────────────────────┐
│ Cheque Processing Dashboard        │
├────────────────────────────────────┤
│ Total      Approved     Review     │
│  250          180          45      │
│                                    │
│ Rejected    Fraud Cases            │
│    25           12                 │
└────────────────────────────────────┘
```

---

# 4. Backend Technology

## 4.1 Python

Python will be the primary backend and AI/ML programming language.

Python is suitable because the project requires:

* OCR integration
* Computer vision
* Machine learning
* Data processing
* Fraud detection
* API development

Major Python libraries include:

```text
OpenCV
Pandas
NumPy
Scikit-learn
PyTesseract
FastAPI
SQLAlchemy
PyTest
```

---

# 5. FastAPI

**FastAPI** will be used to build the backend REST API.

The backend will handle:

* File uploads
* OCR processing
* Data extraction
* Validation
* Fraud analysis
* Risk scoring
* Decision generation
* Database operations
* Audit logging

Example API structure:

```text
POST   /api/cheques/upload
GET    /api/cheques/{cheque_id}
POST   /api/cheques/{cheque_id}/validate
POST   /api/cheques/{cheque_id}/fraud-check
GET    /api/cheques/{cheque_id}/decision
GET    /api/dashboard/summary
GET    /api/audit/{cheque_id}
```

The final API specification will be documented in:

```text
docs/26_API_Specification.md
```

---

# 6. OCR Technology

## 6.1 Tesseract OCR

For the initial prototype, **Tesseract OCR** will be used as the primary OCR engine.

It will extract information such as:

* Cheque number
* Account number
* Routing/transit number
* Payee
* Amount
* Date
* Other printed text

The OCR pipeline will be:

```text
Cheque Image
     ↓
OpenCV Preprocessing
     ↓
Tesseract OCR
     ↓
Raw Text
     ↓
Field Extraction
     ↓
Structured Cheque Data
```

---

## 6.2 Alternative OCR Engines

The architecture will be designed so that other OCR engines can be integrated later.

Possible alternatives include:

* Google Cloud Vision
* Azure AI Vision
* AWS Textract

These alternatives can be evaluated if Tesseract does not provide the required accuracy for particular cheque layouts or image conditions.

---

# 7. Computer Vision

## 7.1 OpenCV

OpenCV will be used for cheque image processing.

Main operations include:

```text
Image resizing
Grayscale conversion
Noise removal
Contrast enhancement
Thresholding
Deskewing
Edge detection
Region detection
Image quality analysis
```

Example:

```text
Original Image
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
OCR-ready Image
```

OpenCV can also support tampering-related image analysis.

---

# 8. Artificial Intelligence and Machine Learning

## 8.1 Scikit-learn

Scikit-learn will be used for traditional machine-learning components where appropriate.

Potential applications include:

* Anomaly detection
* Transaction pattern analysis
* Risk classification
* Fraud classification
* Model evaluation

Possible algorithms include:

```text
Logistic Regression
Random Forest
Decision Tree
Isolation Forest
Support Vector Machine
```

The final algorithm will be selected based on the available synthetic dataset and evaluation results rather than assuming a particular model in advance.

---

# 9. Deep Learning

TensorFlow or PyTorch may be used for advanced AI components when sufficient training data is available.

Potential applications include:

* Signature similarity analysis
* Image tampering detection
* Advanced fraud classification
* Visual anomaly detection

For the initial MVP, these components may use rule-based or classical computer-vision approaches if the available dataset is too small for reliable deep-learning training.

This prevents the project from claiming an AI model that cannot be properly trained and evaluated.

---

# 10. Data Processing

## 10.1 Pandas

Pandas will be used for:

* Creating mock banking datasets
* Cleaning datasets
* Processing cheque records
* Preparing ML datasets
* Generating evaluation reports

Example:

```text
accounts.csv
cheque_records.csv
transactions.csv
fraud_test_cases.csv
```

---

## 10.2 NumPy

NumPy will support:

* Numerical calculations
* Feature processing
* Image/data operations
* ML preprocessing

---

# 11. Database

## 11.1 PostgreSQL

**PostgreSQL** will be the primary relational database for the project.

It will store:

### Cheque information

```text
cheque_id
cheque_number
account_reference
payee
amount
date
```

### OCR results

```text
ocr_text
field_confidence
extraction_status
```

### Validation results

```text
account_status
payee_match
date_validity
duplicate_status
validation_result
```

### Fraud results

```text
tampering_score
signature_score
duplicate_score
anomaly_score
fraud_score
```

### Decision

```text
risk_score
risk_level
decision
decision_reason
```

### Audit information

```text
event_id
user_id
action
timestamp
previous_status
new_status
```

---

# 12. Database ORM

## SQLAlchemy

SQLAlchemy will be used as the database ORM layer between Python and PostgreSQL.

Architecture:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

This allows the backend to interact with database tables using Python models while maintaining structured database operations.

---

# 13. Mock Banking Data

Because the project is a prototype, synthetic banking records will be created.

The dataset may include:

```text
accounts.csv
customers.csv
cheque_records.csv
payees.csv
transactions.csv
```

Example:

```csv
account_number,account_status,account_holder
ACC100001,ACTIVE,Demo Customer 001
ACC100002,ACTIVE,Demo Customer 002
ACC100003,BLOCKED,Demo Customer 003
```

No real customer banking information should be included.

---

# 14. Fraud Detection Technology

Fraud detection will use a **hybrid approach** combining rule-based validation, image analysis, and machine-learning techniques where sufficient data is available.

```text
                  Fraud Detection
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
 Rule-Based          Computer Vision      ML Model
 Detection            Analysis           Analysis
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                  Fraud Indicators
                         │
                         ▼
                    Risk Score
```

Potential fraud indicators:

* Duplicate cheque
* Account mismatch
* Payee mismatch
* Unusual amount
* Invalid date
* Signature mismatch
* Image tampering
* Abnormal transaction pattern

---

# 15. API Testing

## Postman

Postman will be used to manually test REST APIs during development.

Example:

```text
POST /api/cheques/upload
```

Input:

```text
Cheque Image
```

Expected response:

```json
{
  "cheque_id": "CHK-2026-000001",
  "status": "PROCESSING"
}
```

---

# 16. Automated API Testing

## REST Assured / PyTest

The project can use automated API tests to verify:

* Upload API
* OCR API
* Validation API
* Fraud API
* Decision API
* Dashboard API

Since the backend is planned in Python, **PyTest will be the primary automated backend testing framework**. REST Assured can be used if a Java-based API test suite is later required.

---

# 17. Frontend Automation

## Playwright

Playwright can be used for end-to-end browser testing.

Example workflow:

```text
Open Application
      ↓
Login
      ↓
Upload Cheque
      ↓
Wait for Processing
      ↓
View Extracted Data
      ↓
View Fraud Result
      ↓
Verify Decision
```

This verifies the complete user workflow rather than testing individual APIs only.

---

# 18. Version Control

## Git

Git will be used for source-code version control.

Example:

```text
git add .
git commit -m "feat: add OCR processing"
git push
```

---

## GitHub

GitHub will host the project repository:

```text
Mass-Mutual-Project
```

The repository will contain:

```text
apps/
config/
data/
docs/
models/
scripts/
tests/
README.md
```

GitHub will also provide:

* Version history
* Collaboration
* Issue tracking
* Branch management
* Project documentation

---

# 19. Containerization

## Docker

Docker can be used to package the application and its dependencies.

Possible containers:

```text
┌─────────────────────┐
│ Frontend Container  │
└─────────────────────┘

┌─────────────────────┐
│ Backend Container   │
└─────────────────────┘

┌─────────────────────┐
│ PostgreSQL Container│
└─────────────────────┘
```

This provides a consistent development and deployment environment.

---

# 20. Cloud Deployment

The system can be deployed to a cloud platform such as:

* AWS
* Microsoft Azure
* Google Cloud Platform

A possible deployment architecture is:

```text
                    Internet
                       │
                       ▼
                 Load Balancer
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Frontend            Backend
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
              OCR/AI       PostgreSQL     Storage
```

Cloud deployment is primarily considered for the later MVP/deployment stage.

---

# 21. Recommended Final Stack

For the **first working version (MVP)**, the recommended stack is:

```text
Frontend
→ React.js + Tailwind CSS

Backend
→ Python + FastAPI

OCR
→ Tesseract OCR

Image Processing
→ OpenCV

AI/ML
→ Scikit-learn + Python

Data Processing
→ Pandas + NumPy

Database
→ PostgreSQL

ORM
→ SQLAlchemy

API Testing
→ Postman + PyTest

End-to-End Testing
→ Playwright

Version Control
→ Git + GitHub

Containerization
→ Docker

Cloud
→ AWS / Azure / GCP (deployment phase)
```

---

# 22. Technology Selection Rationale

| Technology       | Reason for Selection                                                |
| ---------------- | ------------------------------------------------------------------- |
| **React.js**     | Suitable for interactive dashboards and processing interfaces       |
| **Tailwind CSS** | Fast and consistent UI development                                  |
| **Python**       | Strong ecosystem for OCR, computer vision, ML and data processing   |
| **FastAPI**      | Lightweight, fast and suitable for REST APIs                        |
| **Tesseract**    | Open-source OCR suitable for the initial prototype                  |
| **OpenCV**       | Strong image-processing and computer-vision capabilities            |
| **Scikit-learn** | Suitable for fraud/anomaly models and evaluation                    |
| **PostgreSQL**   | Reliable relational database for structured banking/processing data |
| **SQLAlchemy**   | Provides clean database integration with Python                     |
| **PyTest**       | Suitable for automated Python testing                               |
| **Playwright**   | Supports complete browser-based workflow testing                    |
| **Git/GitHub**   | Version control and project collaboration                           |
| **Docker**       | Reproducible development and deployment environment                 |

---

# 23. Technology Stack and Project Requirements Mapping

| Requirement              | Technology                              |
| ------------------------ | --------------------------------------- |
| Cheque upload            | React + FastAPI                         |
| JPEG/PNG/PDF support     | Python + image/PDF processing libraries |
| OCR extraction           | Tesseract OCR                           |
| Image enhancement        | OpenCV                                  |
| Cheque field extraction  | Python + OCR + rule-based parsing       |
| Account validation       | FastAPI + PostgreSQL                    |
| Cheque series validation | Python + PostgreSQL                     |
| Duplicate detection      | PostgreSQL + Python                     |
| Signature analysis       | OpenCV + ML/DL where applicable         |
| Tampering detection      | OpenCV + ML/DL where applicable         |
| Anomaly detection        | Scikit-learn / Python                   |
| Risk scoring             | Python                                  |
| Approve/Review/Reject    | FastAPI decision engine                 |
| Manual review            | React dashboard                         |
| Audit trail              | PostgreSQL                              |
| Reporting                | React dashboard + backend analytics     |
| Testing                  | PyTest + Playwright + Postman           |
| Version control          | Git + GitHub                            |
| Deployment               | Docker + Cloud                          |

---

# 24. Important Implementation Principle

The project will follow a **modular architecture**, so individual technologies can be replaced without redesigning the entire system.

For example:

```text
                 OCR Interface
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Tesseract    Google       Azure
        OCR        Vision      AI Vision
```

Similarly, the fraud-detection module can evolve from:

```text
Rule-Based Detection
        ↓
Classical ML
        ↓
Advanced ML / Deep Learning
```

This makes the prototype easier to develop while keeping the architecture suitable for future enterprise-level expansion.

---

## 25. Final Technology Architecture

```text
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│          React.js + Tailwind CSS                    │
└───────────────────────┬─────────────────────────────┘
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│               Python + FastAPI                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Cheque Input → OCR → Validation → Fraud → Decision │
│                                                     │
└───────┬───────────────┬──────────────┬──────────────┘
        │               │              │
        ▼               ▼              ▼
   OpenCV           Tesseract      ML/AI Models
        │               │              │
        └───────────────┼──────────────┘
                        ▼
                 SQLAlchemy ORM
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   PostgreSQL                        │
│ Cheques | Accounts | Validation | Fraud | Audit    │
└─────────────────────────────────────────────────────┘

Supporting Technologies:
Git + GitHub | Docker | PyTest | Playwright | Postman
```

**This is the technology stack we should use as the baseline for the actual implementation of `Mass-Mutual-Project`.** We should avoid claiming Google Vision, Azure Vision, TensorFlow, or cloud services are being used in the MVP unless we actually implement and test them.

