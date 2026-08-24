# ADR-0008: AI/ML Model Versioning

## Status

Accepted (requirements-level scope; tooling/mechanism deferred)

## Decision

Every AI/ML-influenced result (fraud, signature, anomaly, and any future risk/decision model) must record a `model_name` and `model_version` alongside its output. Versions are explicit, human-assigned strings such as `v1.0`, `v2.0` (not automatically generated). No model-registry or experiment-tracking tool (e.g., MLflow, DVC) is introduced at this stage. Selection of such tooling is explicitly deferred and will be revisited once a real (trained, non-rule-based) model is actually built and needs to be versioned.

## Context

The requirement that model versioning must exist is well and consistently documented:

* `NFR-012` (Reproducibility): a processing decision should be reproducible from the stored model version, ruleset version, configuration version, processing data, and risk thresholds.
* `09_Component_Architecture.md` §28 (Model Management Component): must record model name, version, training dataset/version, training date, evaluation metrics, and deployment status.
* `36_Development_Guidelines.md` §28–29: models are developed under `models/ocr/` and `models/fraud_detection/`; every production-ready model should have a version (example: `fraud_model_v1`, `fraud_model_v2`); the audit trail should record which model version produced a given decision.
* `17_Fraud_Detection.md` §34: "fraud rules and ML models should be versioned independently."
* `21_Risk_Scoring.md` §31: scoring-configuration versions are recorded per calculation (example: `risk-v1.0`, incrementing to `risk-v1.1` on a weight change, `risk-ml-v1.0` if an ML model is introduced).
* `25_Database_Schema.md`: `fraud_results`, `signature_results`, and `anomaly_results` all carry `model_name`/`model_version` columns.

What is **not** documented anywhere is *how* versioning is technically implemented: no experiment-tracking or model-registry tool is named; `36_Development_Guidelines.md` §28 says only that large model files "should not be committed to Git" and that "appropriate model storage/versioning" should be used "when required," without naming what that is; no formal versioning scheme (semantic versioning vs. informal incrementing numbers) is mandated as a rule — `v1`/`v2` appears only as an example.

## Alternatives Considered

* **Adopt a model-registry/experiment-tracking tool now** (e.g., MLflow, DVC) — rejected for this stage. The current fraud/risk architecture (ADR-0004) is rule-based and statistical, not a trained model; introducing model-registry tooling before there is an actual trained artifact to manage would add infrastructure with nothing yet to track, contradicting the project's guidance against unnecessary complexity (`36_Development_Guidelines.md` §2, "Configuration over hard-coding" / avoid premature infrastructure).
* **Informal versioning only, recorded in application code/config** (selected) — every model-influenced result stores `model_name` + `model_version` (e.g., `"fraud_model"`, `"v1.0"`) as plain fields on the corresponding result record and in the audit trail, matching the pattern already shown in `36_Development_Guidelines.md` §29 and the `risk-v1.0` / `risk-v1.1` / `risk-ml-v1.0` pattern in `21_Risk_Scoring.md` §31.
* **No versioning at all** — rejected outright; directly contradicts `NFR-012` and the Model Management Component requirement in `09_Component_Architecture.md` §28.

## Selected Approach

Model/ruleset version is a required field wherever a fraud, signature, anomaly, or risk result is produced (rule-based versions included, e.g., `fraud-rules-v1.0`, not only trained-model versions), stored on the corresponding database record (`model_name`, `model_version` per `25_Database_Schema.md`) and surfaced in the audit trail (`27_Audit_Trail.md`). Version numbers are bumped manually by whoever changes the rules/weights/model, following the `vMAJOR.MINOR` convention already used in the documentation (`v1.0`, `v1.1`, `v2.0`). Model-registry/experiment-tracking tooling is out of scope until Milestone 5/6 actually trains a supervised model per ADR-0004's ML-ready path — at that point, this ADR should be revisited (or superseded) to select a concrete mechanism.

## Reason for Selection

* Matches every example already given in the documentation (`fraud_model_v1`, `risk-v1.0`) without inventing a new scheme.
* Keeps Milestone 0–8 scope proportionate: there is no trained model artifact to register or track yet, since fraud/risk detection is rule-based and statistical for the MVP (ADR-0004).
* Fully satisfies the *requirement* (`NFR-012`, reproducibility and traceability of every decision to a model/ruleset version) without committing to unnecessary infrastructure.

## Consequences

* Every fraud, signature, anomaly, and risk-scoring result produced by Milestones 5–7 must include `model_name`/`model_version` fields, even while the "model" is a documented, versioned rule set rather than a trained classifier.
* When a real trained model is introduced (post-MVP or later in the roadmap per `40_Future_Roadmap.md`), model-artifact storage and versioning tooling must be selected explicitly and recorded in a follow-up ADR — it is not silently assumed by this one.
* Large model artifacts (if any are produced, e.g., a future trained fraud classifier) must not be committed directly to Git, per `36_Development_Guidelines.md` §28, pending that follow-up decision.
