# ADR-0006: Overall Architecture Style

## Status

Accepted

## Decision

The system will be built as a **layered, modular monolith** for the MVP/prototype: a single deployable backend application internally organized into clearly separated modules/domains, with a documented future path to independent services/microservices if scaling requirements justify it later.

## Context

`08_System_Architecture.md` §2 explicitly states: "The prototype will preferably follow a modular monolithic architecture, where the components are maintained within a single backend application but remain logically separated," organized into seven logical layers (Presentation, API/Application, Cheque Processing, AI/ML & Computer Vision, Data Access, Data Storage, Infrastructure & Security). `09_Component_Architecture.md` §1 independently states the same: "The prototype will preferably follow a modular monolithic architecture." `37_Deployment_Architecture.md` §21 confirms the MVP deployment topology keeps OCR, validation, fraud detection, and decision logic inside the single backend service.

## Alternatives Considered

* **Independent microservices per module** (e.g., separate OCR service, fraud-detection service, validation service, decision service) — described in `08_System_Architecture.md` §23 as a possible *future* production architecture behind an API Gateway and message/job queue, but explicitly qualified: "should only be introduced if actual scalability, operational, or organizational requirements justify it." Not adopted for the MVP because it introduces deployment, networking, and operational complexity disproportionate to a prototype demonstrating an end-to-end workflow on synthetic data.
* **Modular monolith (selected)** — a single backend application with internally separated modules (input, preprocessing, OCR, extraction, validation, fraud, risk, decision, review, audit, reporting), each with a defined responsibility and interface, but deployed and run as one unit.

## Selected Approach

One backend application (FastAPI, per ADR-0001), internally divided by architectural layer at the top level (`api/`, `core/`, `models/`, `repositories/`, `schemas/`, `services/`, `utils/` — per `36_Development_Guidelines.md` §4), with the processing-stage domains from `09_Component_Architecture.md` §33 (`cheque`, `preprocessing`, `ocr`, `extraction`, `validation`, `fraud` [`tampering`, `signature`, `duplicate`, `anomaly`], `risk`, `decision`, `review`, `audit`, `reporting`) nested inside `app/services/`. This reconciles the two structures previously proposed in `09` (stage-based) and `36` (layer-based) into one consistent layout. See the corresponding update to `09_Component_Architecture.md` §33.

## Reason for Selection

* Matches the explicit, independently-stated framing in two separate architecture documents (`08`, `09`).
* Minimizes deployment and operational complexity appropriate to a prototype built and evaluated on synthetic data within a fixed project timeline.
* Each module remains independently testable and — per the component design principles in `09_Component_Architecture.md` §32 — independently replaceable (e.g., the OCR module behind its adapter interface per ADR-0002), preserving a credible path to service extraction later without requiring it now.
* Keeps the processing pipeline (`input → preprocessing → OCR → extraction → validation → fraud → risk → decision → review → audit`) traceable through a single codebase and a single Processing ID, simplifying the audit-trail requirement (`NFR-008`).

## Consequences

* Milestone 0 will establish the reconciled backend structure described above rather than either of the two previously-conflicting proposals in isolation.
* Splitting any module out into an independent service later is a distinct, separately-justified architectural change requiring its own ADR — it is not assumed or partially implemented now.
* Because everything runs in one process for the MVP, the performance target (`NFR-001`, <30 seconds/cheque) must be met without relying on horizontal scaling; `NFR-005` (Scalability) is addressed only at the design level (stateless API, clear module boundaries) for this phase.
