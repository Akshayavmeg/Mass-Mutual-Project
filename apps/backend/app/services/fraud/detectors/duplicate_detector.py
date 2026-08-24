"""Multi-level duplicate detection (docs/19_Duplicate_Detection.md
S13-S16, S23 rules D1-D4).

Level 1 (exact composite data match) deliberately REUSES Milestone 4's
already-computed DUPLICATE_CHECK result rather than re-querying banking
history a second time (docs/16/17 module-boundary guidance: the fraud
engine consumes validation results instead of duplicating validation
logic). Levels 2 (exact SHA-256 image match) and 3 (perceptual near-
duplicate match) are new capability this milestone adds on top of that.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError
from app.services.fraud.detectors.image_hasher import hamming_distance_hex, similarity_from_hamming

STATUSES = ("NEW", "POTENTIAL_DUPLICATE", "CONFIRMED_DUPLICATE")


@dataclass
class DuplicateDetectionResult:
    duplicate_status: str
    data_match: bool
    image_match: bool
    perceptual_similarity: float | None
    hamming_distance: int | None
    matched_cheque_id: str | None
    reason: str
    d4_inconsistency: bool = False
    d4_matched_cheque_id: str | None = None
    analysis_status: str = "COMPLETED"

    def as_dict(self) -> dict:
        return {
            "duplicate_status": self.duplicate_status,
            "data_match": self.data_match,
            "image_match": self.image_match,
            "perceptual_similarity": self.perceptual_similarity,
            "hamming_distance": self.hamming_distance,
            "matched_cheque_id": self.matched_cheque_id,
            "reason": self.reason,
            "d4_inconsistency": self.d4_inconsistency,
            "d4_matched_cheque_id": self.d4_matched_cheque_id,
            "analysis_status": self.analysis_status,
        }


_STATUS_PRECEDENCE = {"NEW": 0, "POTENTIAL_DUPLICATE": 1, "CONFIRMED_DUPLICATE": 2}


def detect(
    *,
    account_number: str | None,
    cheque_number: str | None,
    amount: float | None,
    date_value: str | None,
    validation_duplicate_check: dict | None,
    current_perceptual_hash: str | None,
    current_file_hash: str | None,
    banking_repo: BankingDataRepository,
) -> DuplicateDetectionResult:
    status = "NEW"
    data_match = False
    image_match = False
    perceptual_similarity: float | None = None
    hamming_distance: int | None = None
    matched_cheque_id: str | None = None
    reasons: list[str] = []

    # --- Level 1: exact composite data match (reused from Milestone 4) ---
    if validation_duplicate_check is not None:
        if validation_duplicate_check.get("status") == "FAIL":
            data_match = True
            status = "CONFIRMED_DUPLICATE"
            details = validation_duplicate_check.get("details") or {}
            matched_cheque_id = details.get("matched_cheque_id")
            reasons.append("Composite cheque details (account, cheque number, amount, date) match a previously processed cheque.")
        elif validation_duplicate_check.get("status") == "NOT_CHECKED":
            reasons.append("Exact data match could not be verified (insufficient extracted data).")

    # --- Level 2: exact image hash match ---
    try:
        hash_index = banking_repo.get_image_hash_index()
        data_unavailable = False
    except BankingDataUnavailableError:
        hash_index = []
        data_unavailable = True
        reasons.append("Image-hash history unavailable; exact/near-image matching could not be performed.")

    if current_file_hash and not data_unavailable:
        for record in hash_index:
            if record.image_hash == current_file_hash:
                image_match = True
                status = "CONFIRMED_DUPLICATE"
                matched_cheque_id = matched_cheque_id or record.cheque_id
                reasons.append(f"Exact image hash match with previously processed cheque {record.cheque_id}.")
                break

    # --- Level 3: near-duplicate via perceptual hash + Hamming distance ---
    #
    # A short (hash_size=8, 64-bit) average hash was measured against this
    # project's own synthetic dataset (see the Milestone 5 report) to have
    # limited discriminative power on its own: because every cheque shares
    # the same bank template, genuinely UNRELATED cheques were observed at
    # perceptual similarity up to 1.00 (mean ~0.96), which would make a
    # similarity-only threshold produce excessive false "confirmed
    # duplicate" results. Per docs/19_Duplicate_Detection.md Rule D3
    # ("High perceptual similarity + matching account/cheque information"),
    # a Level 3 match is only escalated to CONFIRMED when corroborated by a
    # matching account NUMBER AND cheque NUMBER together -- docs/19 S31's
    # own false-positive example is "same account, different cheque
    # number, same amount, same payee -> NOT a duplicate", so account
    # alone is not sufficient corroboration (an account's other genuine
    # cheques share its visual template too). An image-only match (no
    # such corroboration) is capped at POTENTIAL_DUPLICATE. This is a
    # multi-signal-correlation fix, not an arbitrary threshold change --
    # the documented 0.95/0.80 thresholds are unchanged.
    if not image_match and current_perceptual_hash and not data_unavailable:
        best_similarity = -1.0
        best_distance = None
        best_cheque_id = None
        best_key_match = False
        for record in hash_index:
            if not record.perceptual_hash:
                continue
            distance = hamming_distance_hex(current_perceptual_hash, record.perceptual_hash)
            similarity = similarity_from_hamming(distance, settings.duplicate_perceptual_hash_size)
            if similarity > best_similarity:
                best_similarity, best_distance, best_cheque_id = similarity, distance, record.cheque_id
                best_key_match = bool(
                    account_number and cheque_number
                    and record.account_number == account_number
                    and record.cheque_number == cheque_number
                )

        if best_similarity >= 0:
            perceptual_similarity = best_similarity
            hamming_distance = best_distance
            if best_similarity >= settings.duplicate_confirmed_similarity_threshold and best_key_match:
                status = "CONFIRMED_DUPLICATE"
                matched_cheque_id = matched_cheque_id or best_cheque_id
                reasons.append(
                    f"Perceptual image similarity {best_similarity:.2f} with cheque {best_cheque_id}, "
                    "corroborated by a matching account number and cheque number (confirmed-duplicate threshold)."
                )
            elif best_similarity >= settings.duplicate_potential_similarity_threshold:
                if _STATUS_PRECEDENCE[status] < _STATUS_PRECEDENCE["POTENTIAL_DUPLICATE"]:
                    status = "POTENTIAL_DUPLICATE"
                matched_cheque_id = matched_cheque_id or best_cheque_id
                reasons.append(f"Perceptual image similarity {best_similarity:.2f} with cheque {best_cheque_id} (potential-duplicate range).")

    if status == "NEW" and not reasons:
        reasons.append("No significant historical match found.")

    # --- Rule D4: same account + same cheque number, different amount/date ---
    d4_inconsistency = False
    d4_matched_cheque_id = None
    if account_number and cheque_number and not data_unavailable:
        try:
            same_key_records = banking_repo.find_by_account_and_cheque_number(account_number, cheque_number)
        except BankingDataUnavailableError:
            same_key_records = []
        for record in same_key_records:
            amounts_differ = amount is None or abs(record.amount - amount) >= 0.01
            dates_differ = date_value is None or record.cheque_date != date_value
            if amounts_differ or dates_differ:
                d4_inconsistency = True
                d4_matched_cheque_id = record.cheque_id
                break

    return DuplicateDetectionResult(
        duplicate_status=status,
        data_match=data_match,
        image_match=image_match,
        perceptual_similarity=perceptual_similarity,
        hamming_distance=hamming_distance,
        matched_cheque_id=matched_cheque_id,
        reason=" ".join(reasons),
        d4_inconsistency=d4_inconsistency,
        d4_matched_cheque_id=d4_matched_cheque_id,
        analysis_status="INSUFFICIENT_DATA" if data_unavailable else "COMPLETED",
    )
