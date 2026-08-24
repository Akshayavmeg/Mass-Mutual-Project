"""Cheque data extraction orchestrator (docs/15_Cheque_Data_Extraction.md).

Converts an OCRRawResult (raw text + word bounding boxes) into the
canonical structured cheque record (docs/15 S29), using spatial/
bounding-box region matching as the primary strategy and keyword/regex
parsing over the full text as a fallback (docs/15 S9: "Keywords,
Position, Expected data format, OCR bounding boxes, Cheque template,
Regular expressions, Cross-field validation").

Hard rule enforced throughout: a field that cannot be reliably read is
left null with its raw OCR evidence (if any) preserved -- never a
fabricated or guessed value (docs/15 S32).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field as dataclass_field
from typing import Any

import cv2
import numpy as np

from app.core.config import settings
from app.services.extraction import field_parsers, normalization
from app.services.ocr.engine import OCRRawResult, WordBox
from app.services.ocr.regions import REGIONS, TEMPLATE_NAME, region_text_and_confidence, words_in_region

REQUIRED_FIELDS = ("cheque_number", "account_number", "payee_name", "amount", "date")

_NORMALIZERS = {
    "cheque_number": normalization.normalize_cheque_number,
    "account_number": normalization.normalize_account_number,
    "routing_transit_number": normalization.normalize_routing_transit_number,
    "payee_name": normalization.normalize_payee_name,
    "date": normalization.normalize_date,
}


@dataclass
class FieldExtraction:
    value: Any
    raw_value: str | None
    confidence: float | None
    source: str | None  # "ocr_region" | "ocr_fallback" | None
    validation_status: str | None = None  # not populated until Milestone 4

    def as_dict(self) -> dict:
        return {
            "value": self.value,
            "raw_value": self.raw_value,
            "confidence": round(self.confidence, 2) if self.confidence is not None else None,
            "source": self.source,
            "validation_status": self.validation_status,
        }


@dataclass
class ChequeExtractionResult:
    cheque_id: str
    template: str
    fields: dict[str, FieldExtraction] = dataclass_field(default_factory=dict)
    signature_region_detected: bool = False
    signature_region_bbox: dict | None = None
    extraction_status: str = "PENDING"
    missing_fields: list[str] = dataclass_field(default_factory=list)
    ambiguous_fields: list[str] = dataclass_field(default_factory=list)
    processing_time_ms: float = 0.0

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "template": self.template,
            "extraction_status": self.extraction_status,
            "missing_fields": self.missing_fields,
            "ambiguous_fields": self.ambiguous_fields,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "signature_region_detected": self.signature_region_detected,
            "signature_region_bbox": self.signature_region_bbox,
            "fields": {name: f.as_dict() for name, f in self.fields.items()},
        }

    def canonical_schema(self) -> dict:
        """docs/15_Cheque_Data_Extraction.md S29 canonical output shape."""
        return {
            "cheque_id": self.cheque_id,
            "cheque_number": self.fields["cheque_number"].value,
            "account_number": self.fields["account_number"].value,
            "routing_transit_number": self.fields["routing_transit_number"].value,
            "payee_name": self.fields["payee_name"].value,
            "amount": self.fields["amount"].value,
            "amount_in_words": self.fields["amount_in_words"].value,
            "date": self.fields["date"].value,
            "bank_name": self.fields["bank_name"].value,
            "currency": self.fields["currency"].value,
            "signature_region_detected": self.signature_region_detected,
            "extraction_status": self.extraction_status,
        }


def _extract_one_field(field_name: str, words: list[WordBox], raw_text: str,
                        image_width: int, image_height: int) -> FieldExtraction:
    region = REGIONS.get(field_name)
    raw_value: str | None = None
    confidence: float | None = None
    source: str | None = None

    if region is not None:
        region_words = words_in_region(words, region, image_width, image_height)
        region_text, region_conf = region_text_and_confidence(region_words)
        if region_text:
            raw_value = field_parsers.strip_known_label(field_name, region_text)
            confidence, source = region_conf, "ocr_region"

    if raw_value is None:
        fallback_raw = field_parsers.parse_field_from_text(field_name, raw_text)
        if fallback_raw:
            raw_value, source = fallback_raw, "ocr_fallback"
            confidence = None  # fallback text isn't tied to a specific word's measured confidence

    normalizer = _NORMALIZERS.get(field_name)
    value = normalizer(raw_value) if normalizer else raw_value

    return FieldExtraction(value=value, raw_value=raw_value, confidence=confidence, source=source)


def _extract_amount_field(words: list[WordBox], raw_text: str, image_width: int, image_height: int) -> FieldExtraction:
    region = REGIONS["amount"]
    region_words = words_in_region(words, region, image_width, image_height)
    region_text, region_conf = region_text_and_confidence(region_words)

    raw_value, confidence, source = None, None, None
    if region_text:
        raw_value = field_parsers.strip_known_label("amount", region_text)
        confidence, source = region_conf, "ocr_region"
    else:
        fallback = field_parsers.parse_field_from_text("amount", raw_text)
        if fallback:
            raw_value, source = fallback, "ocr_fallback"

    value = normalization.normalize_amount(raw_value)
    return FieldExtraction(value=value, raw_value=raw_value, confidence=confidence, source=source)


def _extract_amount_in_words(words: list[WordBox], raw_text: str, image_width: int, image_height: int) -> FieldExtraction:
    region = REGIONS["amount_in_words"]
    region_words = words_in_region(words, region, image_width, image_height)
    region_text, region_conf = region_text_and_confidence(region_words)

    if region_text:
        cleaned = field_parsers.strip_known_label("amount_in_words", region_text)
        return FieldExtraction(value=cleaned, raw_value=cleaned, confidence=region_conf, source="ocr_region")

    fallback = field_parsers.parse_field_from_text("amount_in_words", raw_text)
    if fallback:
        return FieldExtraction(value=fallback, raw_value=fallback, confidence=None, source="ocr_fallback")
    return FieldExtraction(value=None, raw_value=None, confidence=None, source=None)


def _extract_bank_name(words: list[WordBox], raw_text: str, image_width: int, image_height: int) -> FieldExtraction:
    region = REGIONS["bank_name"]
    region_words = words_in_region(words, region, image_width, image_height)
    region_text, region_conf = region_text_and_confidence(region_words)
    if region_text:
        return FieldExtraction(value=region_text, raw_value=region_text, confidence=region_conf, source="ocr_region")
    fallback = field_parsers.parse_bank_name(raw_text)
    if fallback:
        return FieldExtraction(value=fallback, raw_value=fallback, confidence=None, source="ocr_fallback")
    return FieldExtraction(value=None, raw_value=None, confidence=None, source=None)


def _extract_currency(words: list[WordBox], raw_text: str, image_width: int, image_height: int) -> FieldExtraction:
    """Detects a currency symbol actually present in the OCR text near
    the amount -- never assumes a default currency (docs/15 S16: currency
    must be configured/detected per dataset, not assumed globally)."""
    region = REGIONS["amount"]
    region_words = words_in_region(words, region, image_width, image_height)
    region_text, _ = region_text_and_confidence(region_words)
    combined = f"{region_text} {raw_text}"
    if "$" in combined:
        return FieldExtraction(value="USD", raw_value="$", confidence=None, source="ocr_region")
    if "₹" in combined or "Rs" in combined or "Rs." in combined:
        return FieldExtraction(value="INR", raw_value="Rs", confidence=None, source="ocr_region")
    return FieldExtraction(value=None, raw_value=None, confidence=None, source=None)


def _detect_signature_region(image: np.ndarray, image_width: int, image_height: int) -> tuple[bool, dict]:
    """Detects whether the signature region contains meaningful ink
    content -- region *detection* only, no comparison/verification
    (that's Milestone 6's job)."""
    region = REGIONS["signature"]
    x0, y0 = int(region.x0 * image_width), int(region.y0 * image_height)
    x1, y1 = int(region.x1 * image_width), int(region.y1 * image_height)
    bbox = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    crop = gray[y0:y1, x0:x1]
    if crop.size == 0:
        return False, bbox

    _, thresh = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink_ratio = float(np.count_nonzero(thresh)) / thresh.size
    detected = ink_ratio >= settings.signature_region_ink_ratio_threshold
    return detected, bbox


def extract_cheque_data(cheque_id: str, ocr_result: OCRRawResult, image: np.ndarray) -> ChequeExtractionResult:
    start = time.perf_counter()

    if ocr_result.status == "FAILED":
        return ChequeExtractionResult(
            cheque_id=cheque_id, template=TEMPLATE_NAME, extraction_status="FAILED",
            missing_fields=list(REQUIRED_FIELDS), processing_time_ms=(time.perf_counter() - start) * 1000,
        )

    words = ocr_result.words
    raw_text = ocr_result.raw_text
    width, height = ocr_result.image_width, ocr_result.image_height

    fields: dict[str, FieldExtraction] = {}
    for name in ("cheque_number", "account_number", "routing_transit_number", "payee_name", "date"):
        fields[name] = _extract_one_field(name, words, raw_text, width, height)

    fields["amount"] = _extract_amount_field(words, raw_text, width, height)
    fields["amount_in_words"] = _extract_amount_in_words(words, raw_text, width, height)
    fields["bank_name"] = _extract_bank_name(words, raw_text, width, height)
    fields["currency"] = _extract_currency(words, raw_text, width, height)

    signature_detected, signature_bbox = _detect_signature_region(image, width, height)

    missing_fields = [name for name in REQUIRED_FIELDS if fields[name].value in (None, "")]
    ambiguous_fields: list[str] = []  # no multi-candidate disambiguation implemented in this milestone

    if missing_fields:
        extraction_status = "PARTIAL"
    else:
        extraction_status = "COMPLETED"

    return ChequeExtractionResult(
        cheque_id=cheque_id,
        template=TEMPLATE_NAME,
        fields=fields,
        signature_region_detected=signature_detected,
        signature_region_bbox=signature_bbox,
        extraction_status=extraction_status,
        missing_fields=missing_fields,
        ambiguous_fields=ambiguous_fields,
        processing_time_ms=(time.perf_counter() - start) * 1000,
    )
