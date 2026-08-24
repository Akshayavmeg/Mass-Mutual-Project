# API Specification

# 26. API Specification

## 1. Introduction

The **API Specification** defines the REST APIs through which the frontend, backend services, OCR engine, validation engine, fraud detection modules, decision engine, database, and dashboard communicate.

The API acts as the communication layer between the user interface and the cheque-processing backend.

The proposed API architecture follows a **RESTful design** and uses **JSON** for request and response data, except for cheque image/file upload APIs, which use `multipart/form-data`.

The APIs are designed for the MVP and can later be extended for integration with authorized banking systems.

---

# 2. API Architecture

The overall API communication flow is:

```text
┌─────────────────────┐
│      Frontend       │
│   React Dashboard   │
└──────────┬──────────┘
           │
           │ HTTPS / REST API
           ▼
┌─────────────────────────────┐
│       Backend API            │
│      Python / FastAPI        │
└──────────────┬──────────────┘
               │
      ┌────────┼────────┐
      │        │        │
      ▼        ▼        ▼
     OCR   Validation  Fraud
      │        │        │
      └────────┼────────┘
               ▼
        Decision Engine
               │
               ▼
          PostgreSQL
```

The frontend should **never connect directly to PostgreSQL**.

---

# 3. API Base URL

For local development:

```text
http://localhost:8000/api/v1
```

For example:

```text
GET http://localhost:8000/api/v1/cheques
```

For production, the base URL will depend on the selected cloud deployment.

---

# 4. API Versioning

The API will use URL-based versioning:

```text
/api/v1/
```

Example:

```text
/api/v1/cheques
/api/v1/validation
/api/v1/fraud
```

Versioning allows future API changes without breaking existing clients.

---

# 5. API Communication Standards

| Item               | Standard             |
| ------------------ | -------------------- |
| Architecture       | REST                 |
| Data Format        | JSON                 |
| File Upload        | Multipart Form Data  |
| Transport          | HTTPS                |
| Authentication     | JWT / secure session |
| API Version        | v1                   |
| Database           | PostgreSQL           |
| Character Encoding | UTF-8                |
| HTTP Status Codes  | Standard HTTP codes  |

---

# 6. Main API Modules

The API will contain the following major modules:

```text
Authentication API
Cheque API
OCR API
Validation API
Fraud Detection API
Signature API
Duplicate Detection API
Risk API
Decision API
Manual Review API
Dashboard API
Audit API
User API
Health API
```

---

# 7. Authentication API

Authentication APIs manage user login and access tokens.

## 7.1 Login

### Endpoint

```http
POST /api/v1/auth/login
```

### Purpose

Authenticates an authorized system user.

### Request

```json
{
  "username": "reviewer01",
  "password": "********"
}
```

### Response

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "USR-001",
    "username": "reviewer01",
    "role": "REVIEWER"
  }
}
```

### Status Codes

```text
200 OK
401 Unauthorized
422 Unprocessable Entity
```

---

# 8. Cheque Upload API

## 8.1 Upload Cheque

### Endpoint

```http
POST /api/v1/cheques/upload
```

### Purpose

Uploads a cheque image or PDF for processing.

### Supported formats

```text
JPEG
PNG
PDF
```

### Request

Content-Type:

```text
multipart/form-data
```

Example:

```text
file: cheque_001.png
```

Optional metadata:

```text
account_id: ACC-001
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "status": "UPLOADED",
  "message": "Cheque uploaded successfully."
}
```

### Status Codes

```text
201 Created
400 Bad Request
413 Payload Too Large
415 Unsupported Media Type
500 Internal Server Error
```

---

# 9. Get Cheque Details

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}
```

### Purpose

Retrieves complete information about a specific cheque.

### Example

```http
GET /api/v1/cheques/CHK-2026-000001
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "cheque_number": "004521",
  "account_number": "XXXXXX4521",
  "routing_transit_number": "110000001",
  "payee_name": "ABC Supplies",
  "amount": 25000.00,
  "cheque_date": "2026-08-12",
  "processing_status": "COMPLETED"
}
```

---

# 10. List Cheques API

### Endpoint

```http
GET /api/v1/cheques
```

### Purpose

Returns a list of processed or pending cheques.

### Query parameters

```text
?page=1
&limit=20
&status=UNDER_REVIEW
&risk_level=HIGH
```

Example:

```http
GET /api/v1/cheques?page=1&limit=20&status=UNDER_REVIEW
```

### Response

```json
{
  "page": 1,
  "limit": 20,
  "total": 2,
  "cheques": [
    {
      "cheque_id": "CHK-001",
      "amount": 25000,
      "risk_level": "HIGH",
      "status": "UNDER_REVIEW"
    }
  ]
}
```

---

# 11. OCR API

## 11.1 Start OCR Processing

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/ocr
```

### Purpose

Runs OCR on the uploaded cheque image.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "status": "COMPLETED",
  "ocr_confidence": 96.8
}
```

---

# 12. OCR Result API

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/ocr
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "engine": "Tesseract",
  "confidence_score": 96.8,
  "extracted_data": {
    "cheque_number": "004521",
    "account_number": "XXXXXX4521",
    "routing_transit_number": "110000001",
    "payee_name": "ABC Supplies",
    "amount": "25000.00",
    "date": "2026-08-12"
  },
  "status": "SUCCESS"
}
```

---

# 13. Validation API

## 13.1 Run Validation

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/validate
```

### Purpose

Validates the extracted cheque information against mock banking records.

The validation engine checks:

* Account status.
* Cheque number.
* Cheque series.
* Routing/transit number.
* Date validity.
* Payee match.
* Amount validity.
* Duplicate history.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "overall_status": "PASS",
  "checks": {
    "account_valid": true,
    "cheque_number_valid": true,
    "series_valid": true,
    "routing_number_valid": true,
    "date_valid": true,
    "payee_match": true,
    "amount_valid": true
  }
}
```

---

# 14. Get Validation Result

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/validation
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "overall_status": "PASS",
  "validation_message": "All validation checks passed.",
  "checks": {
    "account_valid": true,
    "cheque_number_valid": true,
    "series_valid": true,
    "date_valid": true,
    "payee_match": true
  }
}
```

---

# 15. Fraud Detection API

## 15.1 Run Fraud Detection

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/fraud-analysis
```

### Purpose

Runs the fraud detection pipeline.

The system evaluates:

```text
Image Tampering
Signature Mismatch
Duplicate Patterns
Amount Anomalies
Transaction Anomalies
Suspicious Cheque Characteristics
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "fraud_score": 18.5,
  "fraud_level": "LOW",
  "tampering_detected": false,
  "indicators": []
}
```

---

# 16. Get Fraud Analysis

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/fraud-analysis
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "fraud_score": 18.5,
  "fraud_level": "LOW",
  "tampering_detected": false,
  "indicators": {
    "tampering": false,
    "duplicate": false,
    "amount_anomaly": false,
    "signature_mismatch": false
  },
  "model_version": "fraud-v1"
}
```

---

# 17. Signature Analysis API

## 17.1 Analyze Signature

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/signature-analysis
```

### Purpose

Analyzes the signature region of the cheque and compares it against an authorized reference signature where such reference data is available in the mock dataset.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "similarity_score": 91.4,
  "status": "MATCH"
}
```

Possible statuses:

```text
MATCH
UNCERTAIN
MISMATCH
NOT_AVAILABLE
```

---

# 18. Duplicate Detection API

## 18.1 Check Duplicate

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/duplicate-check
```

### Purpose

Checks whether the submitted cheque has already been processed or closely matches a previous cheque.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "duplicate_detected": false,
  "matched_cheque_id": null,
  "similarity_score": 4.2
}
```

---

# 19. Anomaly Detection API

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/anomaly-analysis
```

### Purpose

Identifies unusual patterns associated with the cheque.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "anomaly_score": 12.5,
  "anomaly_level": "LOW",
  "detected_patterns": []
}
```

---

# 20. Risk Scoring API

## 20.1 Calculate Risk

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/risk-score
```

### Purpose

Combines outputs from validation, fraud detection, signature analysis, duplicate detection, and anomaly detection.

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "overall_risk_score": 18.0,
  "risk_level": "LOW",
  "components": {
    "fraud_score": 18.5,
    "validation_score": 0,
    "signature_score": 8.6,
    "duplicate_score": 0,
    "anomaly_score": 12.5
  }
}
```

The exact scoring formula will be documented and implemented consistently in the Risk Scoring module.

---

# 21. Decision Engine API

## 21.1 Generate Decision

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/decision
```

### Purpose

Generates the final automated decision.

Possible outputs:

```text
APPROVE
REVIEW
REJECT
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "decision": "APPROVE",
  "risk_score": 18.0,
  "risk_level": "LOW",
  "review_required": false,
  "reason": "All validation and fraud checks passed."
}
```

---

# 22. Get Decision API

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/decision
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "decision": "REVIEW",
  "risk_score": 61.5,
  "risk_level": "HIGH",
  "review_required": true,
  "reason": "High fraud score and signature mismatch detected."
}
```

---

# 23. Complete Processing API

For the MVP, a single endpoint can also trigger the complete processing pipeline.

### Endpoint

```http
POST /api/v1/cheques/{cheque_id}/process
```

### Processing sequence

```text
Upload
   ↓
Preprocessing
   ↓
OCR
   ↓
Data Extraction
   ↓
Validation
   ↓
Fraud Detection
   ↓
Signature Analysis
   ↓
Duplicate Detection
   ↓
Anomaly Detection
   ↓
Risk Scoring
   ↓
Decision
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "status": "COMPLETED",
  "decision": "REVIEW",
  "risk_score": 57.8,
  "risk_level": "HIGH"
}
```

For the prototype, this endpoint can simplify the demonstration workflow.

---

# 24. Manual Review API

## 24.1 Get Review Queue

### Endpoint

```http
GET /api/v1/reviews
```

### Query parameters

```text
?status=QUEUED
&priority=HIGH
```

### Response

```json
{
  "total": 3,
  "cases": [
    {
      "review_case_id": "REV-001",
      "cheque_id": "CHK-001",
      "priority": "HIGH",
      "status": "QUEUED",
      "trigger_reason": "Signature mismatch"
    }
  ]
}
```

---

# 25. Assign Review Case

### Endpoint

```http
POST /api/v1/reviews/{review_case_id}/assign
```

### Request

```json
{
  "reviewer_id": "USR-002"
}
```

### Response

```json
{
  "review_case_id": "REV-001",
  "status": "ASSIGNED",
  "assigned_reviewer_id": "USR-002"
}
```

---

# 26. Complete Manual Review

### Endpoint

```http
POST /api/v1/reviews/{review_case_id}/complete
```

### Request

```json
{
  "decision": "APPROVE",
  "comment": "Signature verified manually and cheque information confirmed."
}
```

### Response

```json
{
  "review_case_id": "REV-001",
  "status": "CLOSED",
  "final_decision": "APPROVE"
}
```

Every manual-review action should create an audit event.

---

# 27. Dashboard API

The dashboard requires aggregated statistics rather than individual cheque records only.

## 27.1 Dashboard Summary

### Endpoint

```http
GET /api/v1/dashboard/summary
```

### Response

```json
{
  "total_cheques": 1250,
  "approved": 1050,
  "under_review": 125,
  "rejected": 75,
  "fraud_detected": 82,
  "average_processing_time_seconds": 18.7,
  "average_ocr_confidence": 96.2
}
```

---

# 28. Dashboard Fraud Statistics

### Endpoint

```http
GET /api/v1/dashboard/fraud-statistics
```

### Response

```json
{
  "low_risk": 1050,
  "medium_risk": 120,
  "high_risk": 60,
  "critical_risk": 20
}
```

These values are calculated from the database and displayed graphically in the frontend.

---

# 29. Processing Statistics API

### Endpoint

```http
GET /api/v1/dashboard/processing-statistics
```

### Response

```json
{
  "average_processing_time": 18.7,
  "ocr_success_rate": 97.1,
  "validation_success_rate": 94.8,
  "manual_review_rate": 10.0
}
```

This API supports evaluation against the project's performance targets.

---

# 30. Audit API

## 30.1 Get Cheque Audit History

### Endpoint

```http
GET /api/v1/cheques/{cheque_id}/audit
```

### Response

```json
{
  "cheque_id": "CHK-2026-000001",
  "events": [
    {
      "event_type": "CHEQUE_UPLOADED",
      "timestamp": "2026-08-12T10:00:00Z"
    },
    {
      "event_type": "OCR_COMPLETED",
      "timestamp": "2026-08-12T10:00:04Z"
    },
    {
      "event_type": "VALIDATION_COMPLETED",
      "timestamp": "2026-08-12T10:00:07Z"
    },
    {
      "event_type": "DECISION_GENERATED",
      "timestamp": "2026-08-12T10:00:15Z"
    }
  ]
}
```

---

# 31. User API

## Get Current User

### Endpoint

```http
GET /api/v1/users/me
```

### Response

```json
{
  "user_id": "USR-002",
  "username": "reviewer01",
  "role": "REVIEWER",
  "status": "ACTIVE"
}
```

---

# 32. Health Check API

### Endpoint

```http
GET /api/v1/health
```

### Purpose

Checks whether the backend service is operational.

### Response

```json
{
  "status": "healthy",
  "service": "cheque-processing-api",
  "database": "connected"
}
```

If the database is unavailable:

```json
{
  "status": "unhealthy",
  "service": "cheque-processing-api",
  "database": "disconnected"
}
```

---

# 33. HTTP Status Codes

The API will use standard HTTP status codes.

| Code  | Meaning                | Usage                          |
| ----- | ---------------------- | ------------------------------ |
| `200` | OK                     | Successful request             |
| `201` | Created                | Resource created               |
| `202` | Accepted               | Processing started             |
| `400` | Bad Request            | Invalid request                |
| `401` | Unauthorized           | Authentication required        |
| `403` | Forbidden              | Insufficient permission        |
| `404` | Not Found              | Resource unavailable           |
| `409` | Conflict               | Duplicate/conflicting resource |
| `413` | Payload Too Large      | File exceeds allowed size      |
| `415` | Unsupported Media Type | Invalid file type              |
| `422` | Unprocessable Entity   | Validation failure             |
| `429` | Too Many Requests      | Rate limit exceeded            |
| `500` | Internal Server Error  | Server-side failure            |
| `503` | Service Unavailable    | Dependency unavailable         |

---

# 34. Authentication

Protected APIs will require authentication.

Example:

```http
Authorization: Bearer <JWT_TOKEN>
```

Authentication should be required for:

```text
Cheque processing
Fraud results
Risk results
Decision results
Manual review
Audit records
Dashboard
User management
```

The public health endpoint may remain accessible depending on deployment requirements.

---

# 35. Role-Based API Access

Different users will have different API permissions.

| API Area        | Admin | Reviewer | Analyst | Supervisor |
| --------------- | ----: | -------: | ------: | ---------: |
| Upload Cheque   |     ✓ |        ✓ |       ✓ |          ✓ |
| Process Cheque  |     ✓ |        ✓ |       ✓ |          ✓ |
| View Results    |     ✓ |        ✓ |       ✓ |          ✓ |
| Manual Review   |     ✓ |        ✓ |    View |          ✓ |
| Complete Review |     ✓ |        ✓ |       ✗ |          ✓ |
| Dashboard       |     ✓ |        ✓ |       ✓ |          ✓ |
| Audit Logs      |     ✓ |  Limited | Limited |          ✓ |
| User Management |     ✓ |        ✗ |       ✗ |          ✗ |

Actual authorization rules will be implemented in the backend.

---

# 36. API Error Response Format

All API errors should follow a consistent structure.

Example:

```json
{
  "error": {
    "code": "CHEQUE_NOT_FOUND",
    "message": "The requested cheque does not exist.",
    "request_id": "REQ-2026-000145"
  }
}
```

Another example:

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only JPEG, PNG and PDF files are supported.",
    "request_id": "REQ-2026-000146"
  }
}
```

This makes errors easier to understand and debug.

---

# 37. API Request Validation

The backend should validate incoming requests before processing.

Examples:

### File validation

```text
File type
File size
File integrity
Image readability
```

### Cheque data validation

```text
Amount > 0
Valid date format
Valid cheque number format
Valid account identifier
```

### Review validation

```text
Decision must be APPROVE or REJECT
Reviewer must be authorized
Case must be in a reviewable state
```

---

# 38. API Processing Flow

The complete API-level workflow is:

```text
                    USER
                     │
                     ▼
              Upload Cheque
                     │
                     ▼
              POST /upload
                     │
                     ▼
                Create Record
                     │
                     ▼
              POST /process
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
      OCR API              Validation API
        │                         │
        └────────────┬────────────┘
                     ▼
                Fraud API
                     │
                     ▼
              Signature API
                     │
                     ▼
             Duplicate API
                     │
                     ▼
              Anomaly API
                     │
                     ▼
                Risk API
                     │
                     ▼
              Decision API
                     │
             ┌───────┼────────┐
             ▼       ▼        ▼
          APPROVE   REVIEW   REJECT
                      │
                      ▼
                 Review API
                      │
                      ▼
                 Final Decision
                      │
                      ▼
                  Audit API
```

---

# 39. API Security Requirements

The API must implement:

* HTTPS in deployed environments.
* Authentication.
* Role-based authorization.
* Input validation.
* File type validation.
* File size restrictions.
* Secure error handling.
* Rate limiting where appropriate.
* Request logging.
* Audit logging.
* Secure credential management.
* No passwords or secrets in API responses.
* No sensitive information in application logs.

Cheque images and extracted financial information should only be exposed to authorized users.

---

# 40. API Performance Requirements

The API design should support the project's target of:

```text
Processing time < 30 seconds per cheque
```

The API should measure:

```text
Upload time
Preprocessing time
OCR time
Validation time
Fraud detection time
Risk calculation time
Decision time
Total processing time
```

These metrics will later be used by the **Performance Evaluation** module.

---

# 41. API Documentation

The backend should provide automatically generated API documentation.

If FastAPI is used, the project can expose:

```text
/api/docs
```

for interactive API documentation and:

```text
/api/openapi.json
```

for the OpenAPI specification.

This allows developers and evaluators to test endpoints without manually constructing every HTTP request.

---

# 42. API Endpoint Summary

| Method | Endpoint                           | Purpose               |
| ------ | ---------------------------------- | --------------------- |
| POST   | `/auth/login`                      | Authenticate user     |
| POST   | `/cheques/upload`                  | Upload cheque         |
| GET    | `/cheques`                         | List cheques          |
| GET    | `/cheques/{id}`                    | Get cheque            |
| POST   | `/cheques/{id}/ocr`                | Run OCR               |
| GET    | `/cheques/{id}/ocr`                | Get OCR result        |
| POST   | `/cheques/{id}/validate`           | Run validation        |
| GET    | `/cheques/{id}/validation`         | Get validation        |
| POST   | `/cheques/{id}/fraud-analysis`     | Run fraud analysis    |
| GET    | `/cheques/{id}/fraud-analysis`     | Get fraud result      |
| POST   | `/cheques/{id}/signature-analysis` | Analyze signature     |
| POST   | `/cheques/{id}/duplicate-check`    | Check duplicate       |
| POST   | `/cheques/{id}/anomaly-analysis`   | Analyze anomaly       |
| POST   | `/cheques/{id}/risk-score`         | Calculate risk        |
| POST   | `/cheques/{id}/decision`           | Generate decision     |
| GET    | `/cheques/{id}/decision`           | Get decision          |
| POST   | `/cheques/{id}/process`            | Run complete pipeline |
| GET    | `/reviews`                         | Get review queue      |
| POST   | `/reviews/{id}/assign`             | Assign reviewer       |
| POST   | `/reviews/{id}/complete`           | Complete review       |
| GET    | `/dashboard/summary`               | Dashboard summary     |
| GET    | `/dashboard/fraud-statistics`      | Fraud statistics      |
| GET    | `/dashboard/processing-statistics` | Processing statistics |
| GET    | `/cheques/{id}/audit`              | Get audit history     |
| GET    | `/users/me`                        | Current user          |
| GET    | `/health`                          | Health check          |

---

# 43. API Design Summary

The API layer provides a controlled interface between the frontend and the cheque-processing backend.

The complete API workflow is:

```text
Cheque Upload
      ↓
OCR
      ↓
Validation
      ↓
Fraud Detection
      ↓
Signature Analysis
      ↓
Duplicate Detection
      ↓
Anomaly Detection
      ↓
Risk Scoring
      ↓
Decision Engine
      ↓
Approve / Review / Reject
      ↓
Audit Trail
```

The API design is intentionally modular so that each processing component can be developed and tested independently while also supporting a **single end-to-end cheque processing API** for the final demonstration.

For the **Mass-Mutual_Project MVP**, the APIs will operate against the project's **synthetic PostgreSQL banking dataset**. Actual banking-system integration is outside the current scope and can be introduced later through secure, authorized APIs without changing the overall API structure.
