# ADR-0004: Fraud Detection Architecture

## Status

Accepted

## Decision

Fraud detection will use a **hybrid architecture**: explainable **rule-based detection** is prioritized for the MVP, combined with **image-based (tampering) analysis** and **anomaly/pattern detection**, with the architecture kept **ML-ready** so a trained model can be introduced later once sufficient labeled synthetic data is available.

## Context

`17_Fraud_Detection.md` §3–4 documents this exact hybrid approach independently of `11_Technology_Stack.md` §14, which states the same framing ("a hybrid approach combining rule-based validation, image analysis, and machine-learning techniques where sufficient data is available"). `FR-019`–`FR-024` require fraud-signal generation, tampering detection, signature analysis, duplicate detection, anomaly detection, and correlation of multiple signals rather than reliance on any single indicator. `NFR-007` (Explainability) requires that fraud and risk decisions provide understandable reasons, and `NFR-003` sets a ≥90% fraud-detection accuracy target to be measured, not assumed.

## Alternatives Considered

* **Pure rule-based detection** — fully explainable and requires no training data, but cannot generalize to fraud patterns not anticipated by a fixed rule set, and doesn't improve as more data becomes available.
* **Pure ML-based detection** — can potentially generalize better, but is harder to explain to a reviewer (conflicting with `NFR-007`), and requires a labeled dataset large enough to train and evaluate reliably — which does not yet exist at the start of the project (data is created in Milestone 1).
* **Hybrid (selected)** — rule-based detection provides immediate, explainable, deterministic coverage for known fraud patterns (duplicate, tampering, signature mismatch, invalid account, etc.) from day one; anomaly/pattern detection adds statistical coverage for unusual-but-not-explicitly-ruled-for behavior; the architecture stays open to a supervised ML model (candidates: Random Forest, XGBoost, Isolation Forest for anomaly detection) once the synthetic dataset from Milestone 1 is large enough to support training and honest evaluation.

## Selected Approach

For the MVP: rule-based fraud indicators (`17_Fraud_Detection.md` §19 rules RULE-001–RULE-005) combined with image-tampering evidence and anomaly/pattern signals, all feeding into the Risk Scoring module (ADR-independent, see `21_Risk_Scoring.md`) with configurable, documented weights — not a trained classifier. The Fraud Detection Engine and its sub-components (tampering, signature, duplicate, anomaly) are structured so a supervised ML model can later be substituted or added as an additional signal without changing the Decision Engine's contract.

## Reason for Selection

* Matches the explicit, independently-stated framing in two separate project documents (`17`, `11`), so this ADR formalizes an already-converged decision rather than introducing a new one.
* Satisfies `NFR-007` (Explainability) immediately, since rule-based indicators each carry a name, severity, and evidence/reason by construction.
* Avoids the risk of training an ML fraud model on a dataset too small to produce a trustworthy, non-overfit result, which would undermine `NFR-003`'s accuracy target and the project's stated principle of never reporting unverified metrics as achieved (`33_Fraud_Model_Evaluation.md` §33).
* Keeps a documented path to ML (Random Forest/XGBoost for classification, Isolation Forest for anomaly detection) once Milestone 1's synthetic dataset and Milestone 5/6 evaluation results justify it.

## Consequences

* Milestone 5 (Fraud Detection) and Milestone 6 (Signature Analysis, Anomaly Detection & Risk Scoring) will implement rule-based and statistical detection first; introducing a trained ML fraud model is out of scope until a labeled dataset and evaluation methodology exist.
* All rule thresholds and risk weights must live in configuration (not hard-coded), per `17_Fraud_Detection.md` §21–22 and `36_Development_Guidelines.md` §9, and must be presented as calibratable prototype values, not proven banking thresholds, until validated through testing.
* Any future introduction of a trained ML model must record its `model_name`/`model_version` alongside every prediction (see ADR-0008) so decisions remain reproducible and auditable.
