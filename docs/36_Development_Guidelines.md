# Development Guidelines

# Development Guidelines

## 1. Introduction

This document defines the development standards, coding practices, repository conventions, testing practices, security requirements, and collaboration guidelines for the **AI-Powered Cheque Scanning, Validation & Fraud Detection System**.

The purpose of these guidelines is to ensure that the project is:

* Structured
* Maintainable
* Secure
* Testable
* Scalable
* Consistent
* Easy to understand
* Suitable for demonstration and future enhancement

All development should follow these guidelines throughout the project lifecycle.

---

# 2. Development Principles

The project should follow these core principles:

1. **Modularity** – Each major functionality should be implemented as an independent module.
2. **Separation of concerns** – OCR, validation, fraud detection, database, API, and UI logic should remain separated.
3. **Reusability** – Common functionality should not be duplicated.
4. **Testability** – Important functions should be independently testable.
5. **Security by design** – Sensitive cheque and banking information must be protected.
6. **Traceability** – Important processing and decision-making activities must be recorded.
7. **Explainability** – Fraud and rejection decisions should provide understandable reasons.
8. **Configuration over hard-coding** – Thresholds and environment-specific values should be configurable.
9. **Data privacy** – Only synthetic/mock banking data should be used for development and testing.
10. **Performance awareness** – Processing time must be considered when implementing every major component.

---

# 3. Repository Structure

The project should follow the established repository structure:

```text
Mass-Mutual-Project/
│
├── apps/
│   ├── backend/
│   └── frontend/
│
├── config/
│
├── data/
│   ├── mock_banking_data/
│   ├── sample_cheques/
│   └── test_data/
│
├── docs/
│   ├── adr/
│   └── *.md
│
├── models/
│   ├── fraud_detection/
│   └── ocr/
│
├── scripts/
│
├── tests/
│
├── .gitignore
└── README.md
```

Each directory should have a clearly defined purpose.

---

# 4. Backend Development Guidelines

The backend is responsible for:

* API endpoints
* Cheque processing
* OCR integration
* Validation
* Fraud detection
* Risk scoring
* Decision generation
* Database interaction
* Audit logging

Backend code should be organized into logical modules rather than placing all functionality in a single file.

Recommended structure:

```text
apps/backend/
│
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── utils/
│   └── core/
│
├── tests/
├── requirements.txt
└── main.py
```

The exact structure may be adjusted according to the selected backend framework.

---

# 5. Frontend Development Guidelines

The frontend should be responsible primarily for:

* File upload
* Cheque preview
* Processing status
* Extracted-data display
* Validation results
* Fraud alerts
* Risk score display
* Decision display
* Manual review interface
* Dashboard
* Reports

Business logic should not be unnecessarily duplicated in the frontend.

For example:

```text
Frontend
   ↓
Backend API
   ↓
Validation Engine
```

The frontend should display the backend's authoritative validation and decision results.

---

# 6. Coding Standards

Code should follow the official conventions of the selected programming language.

For Python:

* Follow PEP 8.
* Use meaningful variable names.
* Use functions for reusable logic.
* Use classes where object-oriented design provides value.
* Add type hints where practical.
* Avoid unnecessarily long functions.
* Avoid global mutable state.

Example:

```python
def validate_account(account_number: str) -> bool:
    """
    Validate whether an account exists and is active.
    """
    ...
```

Avoid unclear code such as:

```python
def check(x):
    ...
```

Prefer descriptive names such as:

```python
def validate_account_status(account_number):
    ...
```

---

# 7. Naming Conventions

Consistent naming should be used throughout the project.

### Python

```text
snake_case
```

Example:

```python
cheque_number
account_status
fraud_score
```

### Classes

```text
PascalCase
```

Example:

```python
FraudDetectionService
ValidationEngine
DecisionEngine
```

### Constants

```text
UPPER_SNAKE_CASE
```

Example:

```python
MAX_FILE_SIZE
DEFAULT_RISK_THRESHOLD
```

### Files

Use descriptive names:

```text
ocr_service.py
validation_engine.py
fraud_detector.py
decision_engine.py
audit_service.py
```

---

# 8. Function Guidelines

Functions should ideally perform one clearly defined task.

Good:

```text
preprocess_image()
extract_ocr_text()
extract_cheque_fields()
validate_account()
detect_duplicate()
calculate_risk_score()
generate_decision()
```

Avoid creating one large function that performs the entire cheque-processing pipeline.

Instead:

```text
process_cheque()
    ↓
preprocess_image()
    ↓
run_ocr()
    ↓
extract_fields()
    ↓
validate_cheque()
    ↓
detect_fraud()
    ↓
calculate_risk()
    ↓
generate_decision()
```

---

# 9. Configuration Management

Configuration values should not be hard-coded throughout the source code.

Examples of configurable values:

* OCR settings
* Database connection
* File-size limits
* Risk thresholds
* Fraud thresholds
* Processing limits
* API configuration
* Environment settings

Use configuration files or environment variables.

Example:

```text
config/
├── settings.yaml
├── development.yaml
└── testing.yaml
```

Sensitive configuration such as credentials should be stored using environment variables and must not be committed to Git.

---

# 10. Environment Variables

A `.env` file may be used for local development.

Example:

```text
DATABASE_URL=
OCR_ENGINE=
API_KEY=
SECRET_KEY=
```

The actual `.env` file must be included in `.gitignore`.

A safe example file may be provided:

```text
.env.example
```

Example:

```text
DATABASE_URL=your_database_url
OCR_ENGINE=tesseract
API_KEY=your_api_key
```

No real credentials should be stored in the repository.

---

# 11. OCR Development Guidelines

The OCR module should be implemented as an independent service/component.

Example:

```text
OCR Service
    ↓
Input Image
    ↓
Preprocessing
    ↓
OCR Engine
    ↓
Raw OCR Output
```

The OCR implementation should:

* Handle invalid images gracefully.
* Record OCR confidence where available.
* Preserve raw OCR output for debugging where appropriate.
* Normalize extracted text.
* Avoid silently changing extracted values.
* Identify missing fields.
* Support future replacement of the OCR engine.

The OCR engine should not directly make approval or rejection decisions.

---

# 12. Cheque Data Extraction Guidelines

OCR output should be converted into a standardized structure.

Example:

```json
{
  "cheque_number": "100001",
  "account_number": "9000012345",
  "payee": "Sample Corporation",
  "amount": 12500.00,
  "date": "2026-08-01"
}
```

The extraction layer should clearly distinguish between:

```text
OCR Raw Data
      ↓
Extracted Data
      ↓
Validated Data
```

This distinction is important for debugging and auditability.

---

# 13. Validation Engine Guidelines

Validation rules should be modular.

Example:

```text
validation/
├── account_validator.py
├── cheque_validator.py
├── date_validator.py
├── payee_validator.py
└── duplicate_validator.py
```

Each validation rule should produce a clear result.

Example:

```json
{
  "rule": "account_status",
  "passed": true,
  "reason": "Account is active"
}
```

Validation failures should not automatically be treated as fraud unless the configured fraud rules explicitly classify them as such.

---

# 14. Fraud Detection Guidelines

Fraud detection should be designed as a combination of independent indicators.

Potential indicators include:

```text
Duplicate
Signature mismatch
Image tampering
Payee mismatch
Unusual amount
Unusual pattern
Invalid account
Multiple validation failures
```

Each indicator should provide:

* Indicator name
* Result
* Severity
* Evidence/reason
* Score contribution

Example:

```json
{
  "indicator": "duplicate_cheque",
  "detected": true,
  "severity": "high",
  "reason": "Matching cheque already exists"
}
```

This improves explainability.

---

# 15. Risk Scoring Guidelines

Risk scores should be calculated using documented rules or models.

Example:

```text
Validation Risk
       +
Fraud Risk
       +
Anomaly Risk
       +
Image Risk
       ↓
Overall Risk Score
```

Risk thresholds should be stored in configuration rather than scattered throughout the code.

Example:

```text
LOW_RISK_THRESHOLD
MEDIUM_RISK_THRESHOLD
HIGH_RISK_THRESHOLD
```

The scoring logic should be documented so that developers and reviewers can understand how a score was generated.

---

# 16. Decision Engine Guidelines

The Decision Engine should be independent from the UI.

It should receive validated information and produce a structured decision.

Example:

```json
{
  "decision": "REVIEW",
  "risk_score": 67,
  "reasons": [
    "Signature similarity below threshold",
    "Unusual transaction amount"
  ]
}
```

Supported decisions:

```text
APPROVE
REVIEW
REJECT
```

Every non-approval decision should have clearly recorded reasons.

---

# 17. Manual Review Guidelines

Manual review cases should provide sufficient information for the reviewer.

The reviewer should be able to see:

* Original cheque
* Extracted data
* Validation results
* Fraud indicators
* Risk score
* Decision reason
* Processing history

The reviewer action should be recorded in the audit trail.

---

# 18. Database Development Guidelines

Database access should be separated from business logic.

Recommended flow:

```text
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

Avoid placing raw database queries throughout the application.

Database operations should:

* Use parameterized queries/ORM mechanisms.
* Validate inputs.
* Handle database errors.
* Use appropriate indexes.
* Avoid unnecessary queries.
* Maintain referential integrity.

---

# 19. Database Migration Guidelines

Database schema changes should be version-controlled.

When the selected database framework supports migrations, use them rather than manually modifying production schemas.

Each schema change should have a clear migration.

Example:

```text
001_initial_schema
002_add_audit_logs
003_add_risk_score
```

---

# 20. API Development Guidelines

APIs should follow consistent naming and response formats.

Example:

```text
POST /api/cheques/upload
GET  /api/cheques/{cheque_id}
POST /api/cheques/{cheque_id}/process
GET  /api/cheques/{cheque_id}/result
GET  /api/reviews
POST /api/reviews/{review_id}/decision
```

API responses should use appropriate HTTP status codes.

Examples:

```text
200 → Successful request
201 → Resource created
400 → Invalid request
401 → Unauthorized
403 → Forbidden
404 → Resource not found
500 → Internal server error
```

---

# 21. API Error Handling

Errors should return structured responses.

Example:

```json
{
  "error": {
    "code": "INVALID_CHEQUE_IMAGE",
    "message": "The uploaded file is not a supported cheque image."
  }
}
```

Do not expose:

* Database credentials
* Internal stack traces
* Secret keys
* Sensitive infrastructure details

to end users.

---

# 22. File Upload Security

Cheque images must be treated as untrusted input.

The application should:

* Validate file extension.
* Validate MIME type.
* Enforce file-size limits.
* Generate safe internal filenames.
* Prevent path traversal.
* Reject unsupported file formats.
* Store uploaded files securely.
* Avoid executing uploaded files.

Example:

```text
User File
   ↓
Type Validation
   ↓
Size Validation
   ↓
Security Check
   ↓
Safe Storage
   ↓
Processing
```

---

# 23. Logging Guidelines

Application logs should provide enough information to diagnose failures without exposing sensitive data.

Log examples:

```text
INFO  - Cheque processing started
INFO  - OCR completed
INFO  - Validation completed
WARN  - Cheque flagged for review
ERROR - OCR processing failed
```

Do not log complete:

* Account numbers
* Personal information
* Authentication credentials
* API keys
* Sensitive cheque images

unless explicitly required and appropriately protected.

---

# 24. Audit Logging

Audit logs are different from normal application logs.

Audit logs should capture important business events such as:

```text
Cheque uploaded
OCR completed
Validation completed
Fraud alert generated
Decision generated
Manual review started
Manual review completed
Final decision changed
```

Audit records should be persistent and protected from unauthorized modification.

---

# 25. Security Guidelines

The system should follow basic security principles including:

* Authentication
* Authorization
* Input validation
* Secure file handling
* Secure API design
* Password protection
* Secret management
* Access control
* Audit logging
* Data encryption where applicable

The system should follow least-privilege access.

Users should only have access to the functionality required for their role.

---

# 26. Data Privacy Guidelines

The project should use **synthetic/mock banking data** during development and testing.

Do not commit real:

* Customer names
* Account numbers
* Banking records
* Signatures
* Cheque images
* Personal information

to the repository.

If real enterprise data is ever introduced, it must follow the organization's approved data-governance and privacy requirements.

---

# 27. Synthetic Data Guidelines

Synthetic cheque data should clearly be identified as test data.

Example:

```text
data/mock_banking_data/
data/sample_cheques/
data/test_data/
```

Synthetic account numbers should not correspond to real customer accounts.

Test cases should include:

```text
Normal
Invalid Account
Duplicate
Payee Mismatch
Expired
Signature Mismatch
High Amount
Tampered Image
Multiple Risk Indicators
```

---

# 28. Machine Learning Development Guidelines

ML models should be developed separately from application code.

Recommended structure:

```text
models/
├── ocr/
└── fraud_detection/
```

The following should be documented for each model:

* Model purpose
* Dataset
* Features
* Training process
* Evaluation metrics
* Model version
* Thresholds
* Limitations

Model files should not be committed to Git if they are large.

Use appropriate model storage/versioning when required.

---

# 29. Model Versioning

Every production-ready model should have a version.

Example:

```text
fraud_model_v1
fraud_model_v2
```

The audit trail should record which model version was used for a fraud decision when applicable.

Example:

```json
{
  "model": "fraud_model",
  "version": "v1.0"
}
```

This allows a decision to be traced back to the model that generated it.

---

# 30. Testing Guidelines

Every major module should have tests.

Recommended structure:

```text
tests/
├── unit/
├── integration/
├── system/
├── performance/
└── test_data/
```

Tests should cover:

* Normal cases
* Invalid inputs
* Edge cases
* Error conditions
* Fraud cases
* Duplicate cases
* OCR extraction cases

A new feature should ideally include corresponding tests.

---

# 31. Test Data Guidelines

Test data should not depend on production data.

Use controlled synthetic data.

Example:

```text
VALID_CHEQUE_001
INVALID_ACCOUNT_001
DUPLICATE_CHEQUE_001
FRAUD_SIGNATURE_001
ANOMALOUS_AMOUNT_001
```

Each test case should have an expected result.

---

# 32. Code Review Guidelines

Before merging significant changes, code should be reviewed.

Reviewers should check:

* Correctness
* Security
* Readability
* Performance
* Testing
* Error handling
* Documentation
* Maintainability

Avoid merging code that contains:

* Hard-coded secrets
* Unnecessary duplicate code
* Debug statements
* Disabled security checks
* Unexplained business rules

---

# 33. Git Guidelines

Git should be used for version control throughout development.

Recommended workflow:

```text
main
  ↑
feature branch
```

For example:

```text
feature/ocr-engine
feature/validation-engine
feature/fraud-detection
feature/dashboard
```

Changes should be committed regularly.

---

# 34. Commit Message Guidelines

Use descriptive commit messages.

Recommended format:

```text
type: description
```

Examples:

```text
feat: add cheque upload module
feat: implement OCR extraction
feat: add validation engine
feat: implement duplicate detection
fix: handle invalid cheque images
test: add OCR evaluation tests
docs: update fraud detection documentation
refactor: improve validation service
chore: update project dependencies
```

Avoid vague commits such as:

```text
update
changes
final
new code
```

---

# 35. Branching Guidelines

The `main` branch should contain stable code.

Feature development should preferably occur in separate branches.

Example:

```text
main
│
├── feature/cheque-upload
├── feature/ocr
├── feature/validation
├── feature/fraud-detection
└── feature/dashboard
```

After testing and review, changes can be merged into `main`.

---

# 36. Documentation Guidelines

Every major module should have corresponding documentation.

The project's `docs/` directory contains the detailed architecture and technical documentation.

When implementation changes significantly, the relevant documentation should also be updated.

For example:

```text
Implementation Change
        ↓
Code Updated
        ↓
Tests Updated
        ↓
Documentation Updated
```

Documentation should describe the **actual implemented system**, not only the originally proposed design.

---

# 37. Architecture Decision Records

Important technical decisions should be recorded in:

```text
docs/adr/
```

Examples already defined in this project include:

```text
0001-backend-technology.md
0002-ocr-engine-selection.md
0003-database-selection.md
0004-fraud-detection-architecture.md
```

An ADR should explain:

* Decision
* Context
* Alternatives considered
* Selected approach
* Reason for selection
* Consequences

---

# 38. Dependency Management

All project dependencies should be explicitly documented.

For Python:

```text
requirements.txt
```

or an appropriate modern Python dependency-management configuration should be used.

Dependencies should:

* Have known versions where appropriate.
* Be reviewed periodically.
* Not contain unnecessary packages.
* Be updated carefully.
* Be checked for known vulnerabilities where possible.

---

# 39. Performance Guidelines

The project's main performance requirement is:

> **End-to-end processing time < 30 seconds per cheque.**

Developers should avoid unnecessary processing.

Examples:

* Do not repeatedly preprocess the same image.
* Do not perform unnecessary database queries.
* Avoid loading large datasets into memory unnecessarily.
* Avoid repeated OCR operations.
* Use efficient image-processing techniques.

Performance should be measured rather than assumed.

---

# 40. Error Handling Guidelines

Every major module should handle expected failures gracefully.

Examples:

### OCR Failure

```text
OCR Failure
    ↓
Record Error
    ↓
Mark Processing Failed/Review
    ↓
Inform User
```

### Database Failure

```text
Database Failure
    ↓
Log Error
    ↓
Do Not Produce Unverified Decision
```

### Invalid Image

```text
Invalid File
    ↓
Reject Upload
    ↓
Return Clear Error
```

The system must not generate an **Approve** decision when required validation steps have failed or produced unreliable results.

---

# 41. Explainability Guidelines

Fraud decisions should not simply display:

```text
FRAUD DETECTED
```

Instead, the system should provide reasons.

Example:

```text
Decision: REVIEW

Reasons:
• Signature similarity below configured threshold
• Duplicate cheque indicator detected
• Amount significantly differs from expected pattern
```

This makes the system easier to review and demonstrate.

---

# 42. Development Workflow

The recommended development workflow is:

```text
Requirement
    ↓
Design
    ↓
Implementation
    ↓
Unit Testing
    ↓
Integration Testing
    ↓
Code Review
    ↓
Documentation
    ↓
Git Commit
    ↓
Merge
    ↓
Performance/Security Validation
```

No major feature should be considered complete merely because the code runs.

---

# 43. Definition of Done

A feature is considered **Done** when:

* The feature is implemented.
* Code follows project standards.
* Input validation is included.
* Error handling is included.
* Unit tests are added.
* Integration impact is checked.
* Documentation is updated.
* No secrets are committed.
* The feature works with synthetic test data.
* Relevant performance impact is evaluated.
* Changes are committed to Git.

---

# 44. Development Checklist

Before considering a module complete, verify:

```text
[ ] Requirement understood
[ ] Design completed
[ ] Code implemented
[ ] Input validation added
[ ] Error handling added
[ ] Unit tests added
[ ] Integration tested
[ ] Security checked
[ ] Performance checked
[ ] Documentation updated
[ ] Git commit created
```

---

# 45. Final Development Principles

The **Mass-Mutual_Project** should be developed as a modular, testable, secure, and explainable system.

The development team should maintain a clear separation between:

```text
Input
  ↓
Processing
  ↓
OCR
  ↓
Validation
  ↓
Fraud Detection
  ↓
Risk Scoring
  ↓
Decision
  ↓
Audit
  ↓
Presentation
```

The system should use **synthetic banking data during development**, maintain a complete audit trail, provide reasons for fraud-related decisions, and avoid making unsupported claims about accuracy or performance before actual evaluation.

Most importantly, **the implementation and documentation must remain synchronized**. As the project evolves, any change to the architecture, technology stack, database, APIs, OCR engine, fraud methodology, or decision rules should be reflected in the corresponding documentation and ADR files.

