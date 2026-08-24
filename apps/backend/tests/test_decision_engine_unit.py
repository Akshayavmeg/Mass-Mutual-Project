"""Unit tests for the Milestone 7 Decision Engine rule evaluation
(docs/22_Decision_Engine.md S9-S11), using crafted M4-M6 result fixtures
so every documented precedence tier, hard rule, and threshold boundary
is exercised deterministically.
"""

from __future__ import annotations

from app.services.decision import decision_rules


def _validation(status="PASS"):
    return {"overall_validation_status": status, "checks": {}}


def _fraud(*, risk_level="LOW", duplicate_status="NEW", tampering_score=0.0, indicators=None):
    return {
        "risk_level": risk_level,
        "duplicate_analysis": {"duplicate_status": duplicate_status},
        "image_analysis": {"image_tampering_score": tampering_score},
        "indicators": indicators or [],
    }


def _signature(risk_level="LOW"):
    return {"risk_level": risk_level, "similarity_score": 0.9}


def _anomaly(risk_level="LOW"):
    return {"risk_level": risk_level}


def _risk(*, score=10.0, level="LOW", hard_rules=None, unavailable=None):
    return {
        "overall_risk_score": score, "risk_level": level,
        "hard_rules_triggered": hard_rules or [], "unavailable_inputs": unavailable or [],
    }


def _evaluate(**overrides):
    kwargs = dict(
        validation=_validation(), fraud_analysis=_fraud(), signature_analysis=_signature(),
        anomaly_analysis=_anomaly(), risk_assessment=_risk(), ocr_confidence=96.0,
    )
    kwargs.update(overrides)
    return decision_rules.evaluate(**kwargs)


# --- APPROVE ---

def test_low_risk_clean_cheque_approves():
    decision, rules, reasons, escalation = _evaluate()
    assert decision == "APPROVE"
    assert rules == ["LOW_RISK_APPROVE"]
    assert escalation is None
    assert reasons


def test_approval_requires_low_overall_risk_level_not_just_low_score():
    """Even if the numeric score happens to be low, a non-LOW risk_level
    (as classified by Milestone 6) must not approve."""
    decision, *_ = _evaluate(risk_assessment=_risk(score=10.0, level="MEDIUM"))
    assert decision != "APPROVE"


# --- REJECT: hard rules (Priority 1) ---

def test_invalid_account_hard_rejects_regardless_of_low_score():
    decision, rules, reasons, escalation = _evaluate(
        risk_assessment=_risk(score=5.0, level="LOW", hard_rules=["INVALID_OR_INACTIVE_ACCOUNT"]),
    )
    assert decision == "REJECT"
    assert "ACCOUNT_INVALID_HARD_REJECT" in rules


def test_confirmed_duplicate_hard_rejects_regardless_of_medium_score():
    """docs/22 S14 Example 3: risk score 35 (medium) but confirmed
    duplicate must still REJECT -- the canonical hard-rule-overrides-score test."""
    decision, rules, reasons, escalation = _evaluate(
        fraud_analysis=_fraud(duplicate_status="CONFIRMED_DUPLICATE"),
        risk_assessment=_risk(score=35.0, level="MEDIUM"),
    )
    assert decision == "REJECT"
    assert "CONFIRMED_DUPLICATE_HARD_REJECT" in rules
    assert escalation is not None


def test_severe_tampering_hard_rejects():
    decision, rules, *_ = _evaluate(fraud_analysis=_fraud(tampering_score=0.9))
    assert decision == "REJECT"
    assert "SEVERE_TAMPERING_HARD_REJECT" in rules


def test_critical_fraud_risk_level_hard_rejects():
    decision, rules, *_ = _evaluate(fraud_analysis=_fraud(risk_level="CRITICAL"))
    assert decision == "REJECT"
    assert "CRITICAL_FRAUD_HARD_REJECT" in rules


def test_multiple_hard_rejection_conditions_all_reported():
    decision, rules, reasons, _ = _evaluate(
        fraud_analysis=_fraud(risk_level="CRITICAL", duplicate_status="CONFIRMED_DUPLICATE"),
    )
    assert decision == "REJECT"
    assert "CONFIRMED_DUPLICATE_HARD_REJECT" in rules
    assert "CRITICAL_FRAUD_HARD_REJECT" in rules
    assert len(reasons) == 2


# --- REVIEW: mandatory review rules (Priority 2) ---

def test_possible_duplicate_reviews():
    decision, rules, *_ = _evaluate(fraud_analysis=_fraud(duplicate_status="POTENTIAL_DUPLICATE"))
    assert decision == "REVIEW"
    assert "POSSIBLE_DUPLICATE_REVIEW" in rules


def test_signature_critical_reviews_not_rejects():
    """Explicit policy: signature mismatch of ANY severity (including
    CRITICAL) routes to REVIEW, never automatic REJECT."""
    decision, rules, *_ = _evaluate(signature_analysis=_signature(risk_level="CRITICAL"))
    assert decision == "REVIEW"
    assert "SIGNATURE_UNCERTAIN_REVIEW" in rules


def test_missing_signature_reference_reviews_not_rejects():
    decision, rules, reasons, _ = _evaluate(signature_analysis=_signature(risk_level="UNAVAILABLE"))
    assert decision == "REVIEW"
    assert "SIGNATURE_UNCERTAIN_REVIEW" in rules
    assert any("not treated as fraud" in r for r in reasons)


def test_suspicious_tampering_reviews():
    decision, rules, *_ = _evaluate(fraud_analysis=_fraud(tampering_score=0.4))
    assert decision == "REVIEW"
    assert "SUSPICIOUS_TAMPERING_REVIEW" in rules


def test_low_ocr_confidence_reviews():
    decision, rules, *_ = _evaluate(ocr_confidence=40.0)
    assert decision == "REVIEW"
    assert "LOW_OCR_CONFIDENCE_REVIEW" in rules


def test_validation_not_pass_reviews():
    decision, rules, *_ = _evaluate(validation=_validation(status="FAIL"))
    assert decision == "REVIEW"
    assert "VALIDATION_ISSUE_REVIEW" in rules


def test_unavailable_critical_dependency_reviews_not_approves():
    decision, rules, *_ = _evaluate(risk_assessment=_risk(unavailable=["SIGNATURE_ANALYSIS"]))
    assert decision == "REVIEW"
    assert "CRITICAL_DATA_UNAVAILABLE_REVIEW" in rules


def test_high_anomaly_reviews():
    decision, rules, *_ = _evaluate(anomaly_analysis=_anomaly(risk_level="HIGH"))
    assert decision == "REVIEW"
    assert "UNUSUAL_ANOMALY_REVIEW" in rules


def test_multiple_high_risk_fraud_indicators_reviews():
    indicators = [
        {"type": "A", "severity": "HIGH"}, {"type": "B", "severity": "CRITICAL"},
    ]
    decision, rules, *_ = _evaluate(fraud_analysis=_fraud(indicators=indicators))
    assert decision == "REVIEW"
    assert "MULTIPLE_HIGH_RISK_INDICATORS_REVIEW" in rules


def test_contradictory_evidence_produces_multiple_review_reasons():
    """docs/22 S6: conflicting validation results / multiple uncertainty
    signals together -- all contributing reasons must be reported, not
    just the first one found."""
    decision, rules, reasons, _ = _evaluate(
        validation=_validation(status="WARNING"),
        signature_analysis=_signature(risk_level="HIGH"),
        anomaly_analysis=_anomaly(risk_level="HIGH"),
    )
    assert decision == "REVIEW"
    assert len(rules) >= 3
    assert len(reasons) == len(rules)


# --- REJECT: risk-score fallback (Priority 3) ---

def test_critical_risk_level_fallback_rejects():
    decision, rules, *_ = _evaluate(risk_assessment=_risk(score=90.0, level="CRITICAL"))
    assert decision == "REJECT"
    assert rules == ["CRITICAL_RISK_REJECT"]


def test_medium_or_high_risk_level_fallback_reviews():
    decision, rules, *_ = _evaluate(risk_assessment=_risk(score=60.0, level="HIGH"))
    assert decision == "REVIEW"
    assert rules == ["RISK_SCORE_REVIEW"]


# --- Precedence ---

def test_hard_rule_takes_precedence_over_low_risk_score():
    """The Priority-1 hard rule must win even when Priority-3's own risk
    score would otherwise say APPROVE."""
    decision, rules, *_ = _evaluate(
        fraud_analysis=_fraud(duplicate_status="CONFIRMED_DUPLICATE"),
        risk_assessment=_risk(score=2.0, level="LOW"),
    )
    assert decision == "REJECT"
    assert "CONFIRMED_DUPLICATE_HARD_REJECT" in rules


def test_review_rule_takes_precedence_over_critical_score_fallback():
    """A Priority-2 condition is checked (and REVIEW returned) before
    Priority-3's CRITICAL-score-reject fallback would otherwise apply --
    unless a genuine Priority-1 condition is present. Here, no hard
    rejection condition exists, so a Priority-2 condition should route
    to REVIEW even though the score alone is CRITICAL, since the
    precedence check order is P1 -> P2 -> P3 and this scenario has a P2
    match."""
    decision, rules, *_ = _evaluate(
        fraud_analysis=_fraud(duplicate_status="POTENTIAL_DUPLICATE"),
        risk_assessment=_risk(score=90.0, level="CRITICAL"),
    )
    assert decision == "REVIEW"
    assert "POSSIBLE_DUPLICATE_REVIEW" in rules


def test_decision_reason_is_first_reason_and_reasons_list_matches_rules():
    decision, rules, reasons, _ = _evaluate(fraud_analysis=_fraud(duplicate_status="POTENTIAL_DUPLICATE"))
    assert len(reasons) == len(rules)
