# ADR-0007: API Architecture

## Status

Accepted

## Decision

The system exposes a **REST API** under URL-path versioning (`/api/v1/`), using **JSON** request/response bodies and **JWT bearer authentication** for protected endpoints. **`docs/26_API_Specification.md` is the canonical endpoint contract** — where other documents describe an endpoint differently, `26_API_Specification.md` governs.

## Context

Every document that describes the API — `03_Proposed_Solution.md`, `04_Requirements.md`, `08_System_Architecture.md`, `09_Component_Architecture.md`, `11_Technology_Stack.md`, and especially the dedicated `26_API_Specification.md` — describes REST with JSON exclusively; no alternative paradigm (GraphQL, gRPC, SOAP) is mentioned or considered anywhere in the documentation. `26_API_Specification.md` documents a base URL of `http://localhost:8000/api/v1` (development), a standard error envelope (`{"error": {"code", "message", "request_id"}}`), a standard set of HTTP status codes, and `Authorization: Bearer <JWT_TOKEN>` for protected routes — consistent with `FR-039` (Authentication) and `FR-040` (Role-Based Access Control).

Three module-level documents, however, defined endpoint paths for the same operations that do not match `26_API_Specification.md`'s nested, per-cheque path structure:

| Operation | Path in module doc | Canonical path (`26`) |
|---|---|---|
| Calculate risk score | `POST /api/v1/risk-score/calculate` (`21_Risk_Scoring.md` §20) | `POST /api/v1/cheques/{cheque_id}/risk-score` |
| Evaluate decision | `POST /api/v1/decisions/evaluate` (`22_Decision_Engine.md` §18) | `POST /api/v1/cheques/{cheque_id}/decision` |
| Submit review decision | `POST /api/v1/reviews/{review_case_id}/decision` (`23_Manual_Review_Workflow.md` §22) | `POST /api/v1/reviews/{review_case_id}/complete` |

## Alternatives Considered

* **GraphQL** — not mentioned anywhere in the documentation; not considered.
* **gRPC / RPC-style internal APIs** — not mentioned anywhere in the documentation; not considered.
* **Flat, top-level endpoints** (e.g., `/risk-score/calculate`, `/decisions/evaluate`) as used in `21` and `22` — inconsistent with the resource-oriented, per-cheque nesting used everywhere else in `26_API_Specification.md` (e.g., `/cheques/{id}/ocr`, `/cheques/{id}/validation`, `/cheques/{id}/fraud-analysis`).
* **Nested, resource-oriented paths under `/cheques/{cheque_id}/...` and `/reviews/{review_case_id}/...`** (selected, per `26`) — consistent with the rest of the API surface and with REST resource-modeling conventions.

## Selected Approach

REST, JSON, `/api/v1/` versioning, JWT bearer auth, and the exact endpoint list, request/response shapes, status codes, and error envelope defined in `26_API_Specification.md`. `21_Risk_Scoring.md`, `22_Decision_Engine.md`, and `23_Manual_Review_Workflow.md` have been updated to reference the canonical paths shown above instead of their previously divergent ones.

## Reason for Selection

* REST with JSON is the only paradigm ever discussed in the documentation — this ADR formalizes an existing, unanimous choice rather than introducing a new one.
* `26_API_Specification.md` is the document specifically dedicated to the API contract (endpoints, request/response schemas, status codes, error format, auth, role-based access matrix); it is the natural authority when other documents disagree with it on a specific path.
* Nested, per-cheque paths keep the entire processing pipeline's API surface consistent and predictable (`/cheques/{id}/ocr`, `/cheques/{id}/validation`, `/cheques/{id}/fraud-analysis`, `/cheques/{id}/risk-score`, `/cheques/{id}/decision`), which matters for a system whose core design principle is per-cheque traceability via a single Processing ID.

## Consequences

* `21_Risk_Scoring.md`, `22_Decision_Engine.md`, and `23_Manual_Review_Workflow.md` have been corrected to reference the canonical endpoint paths.
* Milestone 8 (Database, API & Audit Trail) implements exactly the endpoint list in `26_API_Specification.md`; any future addition or change to an endpoint should be made in `26` first, with module-level docs updated to match rather than drifting independently again.
