from __future__ import annotations


class ReviewCaseNotFoundError(Exception):
    pass


class ReviewCaseAlreadyClosedError(Exception):
    """docs/23_Manual_Review_Workflow.md S31 Test Case 3/duplicate-action
    prevention: a closed case must not accept further reviewer actions."""


class ReviewCommentRequiredError(Exception):
    """docs/23 S15 mandatory-comment rule."""


class InvalidReviewDecisionError(Exception):
    """docs/23 S13: the only two reviewer final outcomes are APPROVE and REJECT."""
