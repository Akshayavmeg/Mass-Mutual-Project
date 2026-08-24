# ADR-0005: Use of Mock/Synthetic Banking Data

## Status

Accepted

## Decision

Development, testing, and demonstration of this system will use **only synthetic/mock banking and cheque data**. No real customer banking information, real account records, or real signatures will be used or committed to this repository.

## Context

This is the most consistently and repeatedly documented constraint in the entire project. It is stated, independently and in near-identical language, in at least eight separate documents, including:

* `04_Requirements.md` — NFR-011 (Privacy): "Development and testing shall use mock/synthetic banking data unless real data has been explicitly authorized and appropriately protected." Also FR-041: "Use synthetic/mock data during development."
* `05_Scope_and_Assumptions.md` — A-002: "No real customer banking information is required for the prototype." A-010: real/PII data, if ever introduced, must follow organizational privacy requirements; development should preferably use synthetic or anonymized data.
* `02_Project_Objectives.md` §2.15 — "Use mock/synthetic banking data during development."
* `06_Existing_System.md` — proposed development data source is explicitly "Mock/synthetic data for prototype."
* `42_Executive_Summary.md` §8, §12 — the MVP's data strategy is built entirely on synthetic cheque images, artificial customer records, mock account information, synthetic transaction history, and controlled fraudulent/suspicious examples, specifically so the workflow can be demonstrated "without exposing real customer financial information."
* `24_Database_Architecture.md`, `25_Database_Schema.md`, `28_Security_and_Privacy.md`, `36_Development_Guidelines.md` — all state the same constraint for their respective layers (database, schema, security, and general development practice).

## Alternatives Considered

* **Real banking data under a data-sharing/authorization agreement** — explicitly out of scope for this prototype per `05_Scope_and_Assumptions.md` and the project's stated exclusion of production banking integration; would require regulatory approval, security assessment, and organizational authorization not available to this project.
* **Anonymized real data** — considered as a theoretical future path in `05_Scope_and_Assumptions.md` A-010 ("if real data is introduced... development should preferably use synthetic or anonymized data") but not adopted for the MVP; anonymization does not eliminate the compliance burden of having handled real records in the first place.
* **Fully synthetic/mock data (selected)** — no real PII or financial data ever enters the system, eliminating the associated compliance, privacy, and security burden while still allowing every validation, fraud-detection, and decision pathway to be exercised realistically.

## Selected Approach

All customers, accounts, cheques, transactions, and reference signatures used anywhere in this project — in `data/mock_banking_data/`, `data/sample_cheques/`, and `data/test_data/` — are synthetically generated for this project. Synthetic account numbers, names, and signatures must not correspond to real people or real accounts.

## Reason for Selection

* Eliminates the risk of exposing real financial or personal information in a public repository.
* Allows every documented fraud, duplicate, and validation scenario (valid, duplicate, tampered, signature-mismatch, invalid-account, stale, stopped, anomalous, etc.) to be constructed deliberately and labeled with known ground truth — something not reliably possible with real data.
* Matches the project's explicit framing as a decision-support prototype, not a production banking system (`05_Scope_and_Assumptions.md`).

## Consequences

* Milestone 1 (Data Foundation) is responsible for generating a complete, internally consistent synthetic dataset (customers → accounts → cheques → transactions) covering the full set of test-case categories documented across `16`, `17`, `18`, `19`, `20`, and `33`.
* No milestone may introduce real customer or banking data at any point, including for demos.
* Any future integration with real banking data is explicitly deferred to a future phase requiring separate authorization, security review, and its own ADR — it is not part of this project's scope.
