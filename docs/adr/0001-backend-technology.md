# ADR-0001: Backend Technology Selection

## Status

Accepted

## Decision

The backend of the AI-Powered Cheque Scanning, Validation & Fraud Detection System will be implemented in **Python**, using **FastAPI** as the web framework.

## Context

Early project documentation (`03_Proposed_Solution.md`, `04_Requirements.md`) referenced **Python + Flask** as a candidate backend stack. The dedicated technology-selection documentation produced later (`11_Technology_Stack.md`, `08_System_Architecture.md`) instead names **Python + FastAPI** as the "Recommended Final Stack" / implementation baseline. These two sets of documents were never reconciled, leaving an open conflict between Flask and FastAPI.

The backend must support:

* A REST API consumed by a React-based frontend (see ADR-0007).
* An OCR pipeline built around Tesseract/PyTesseract and OpenCV (see ADR-0002).
* Structured request/response validation for cheque, validation, fraud, risk, and decision payloads.
* Auto-generated API documentation to support development and testing (`36_Development_Guidelines.md` and `26_API_Specification.md` both assume interactive API docs are available).
* Asynchronous I/O suitability for future scaling (`NFR-005` — stateless API services, background processing, worker queues).

## Alternatives Considered

* **Flask** — referenced in early proposal documents (03, 04). Mature, minimal, widely used, but requires additional libraries (e.g., Marshmallow/Flask-RESTX) to get equivalent request/response validation and OpenAPI documentation that FastAPI provides natively.
* **FastAPI** — named as the baseline in the dedicated technology stack and architecture documents (08, 11). Provides built-in Pydantic-based request/response validation, automatic OpenAPI/Swagger documentation, and native async support.
* **Django / Django REST Framework** — not mentioned anywhere in the project documentation; not considered.

No other backend language (Node.js, Java, .NET) is mentioned anywhere in the documentation; Python is the only language considered.

## Selected Approach

**Python + FastAPI**, per the explicit direction confirmed for this project. The Flask references in the earlier proposal documents (`03_Proposed_Solution.md` §13, `04_Requirements.md` §15) are treated as superseded by the dedicated technology and architecture documentation (`11_Technology_Stack.md`, `08_System_Architecture.md`) and have been corrected to reference FastAPI.

## Reason for Selection

* FastAPI is the technology named in the documents specifically dedicated to technology-stack and architecture decisions, which are more authoritative than the earlier general proposal narrative.
* Built-in Pydantic schema validation directly supports the project's requirement for structured, explainable request/response payloads (validation results, fraud indicators, risk scores, decisions) as documented across `16`, `17`, `21`, `22`, and `26`.
* Automatic OpenAPI documentation generation matches the interactive API docs (`/api/docs`, `/api/openapi.json`) implied by `26_API_Specification.md`.
* Native async support aligns with the scalability guidance in `NFR-005` (stateless API services, background processing, worker queues) without requiring a framework change later.

## Consequences

* All backend application code, dependency management (`requirements.txt`), and module structure guidance in `36_Development_Guidelines.md` should be read as targeting FastAPI conventions (e.g., routers instead of Flask blueprints, Pydantic schemas instead of Marshmallow).
* `03_Proposed_Solution.md` and `04_Requirements.md` have been updated to reference FastAPI instead of Flask so the documentation set no longer contradicts this decision.
* Any future change away from FastAPI must be recorded as a new ADR that explicitly supersedes this one.
