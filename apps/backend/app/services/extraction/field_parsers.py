"""Keyword/regex fallback field parsing (docs/15_Cheque_Data_Extraction.md
S9-S10).

Used only when region-based extraction (app/services/ocr/regions.py)
finds nothing for a field -- e.g. because the cheque was cropped
unusually or a region fell just outside its expected bounding box. This
mirrors docs/15's documented keyword table (Date -> "Date"/"Dated",
Payee -> "Pay"/"Pay to"/"Payee", Amount -> "Amount"/"Rs"/"$",
Account -> "Account"/"A/C"/"A/C No", Cheque Number ->
"Cheque No"/"Check No"/"Chq No").

Every pattern only ever *extracts* text that is already present in the
OCR output -- it never invents a value.
"""

from __future__ import annotations

import re

_PATTERNS: dict[str, re.Pattern] = {
    "date": re.compile(r"(?:Date|Dated)\s*[:\-]?\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})", re.IGNORECASE),
    "cheque_number": re.compile(r"(?:Cheque|Check|Chq)\s*No\.?\s*[:\-]?\s*([A-Za-z0-9]+)", re.IGNORECASE),
    "account_number": re.compile(r"Account\s*No\.?\s*[:\-]?\s*([A-Za-z0-9]+)", re.IGNORECASE),
    "routing_transit_number": re.compile(
        r"Routing\s*/?\s*Transit\s*No\.?\s*[:\-]?\s*([A-Za-z0-9]+)", re.IGNORECASE,
    ),
    "amount": re.compile(r"[$₹]\s*([\d,]+\.\d{2})"),
    "amount_in_words": re.compile(
        r"Amount\s*in\s*words\s*[:\-]?\s*\n?\s*(.+)", re.IGNORECASE,
    ),
    "payee_name": re.compile(
        r"Pay\s*to\s*the\s*order\s*of\s*[:\-]?\s*\n?\s*(.+)", re.IGNORECASE,
    ),
}


def parse_field_from_text(field_name: str, raw_text: str) -> str | None:
    pattern = _PATTERNS.get(field_name)
    if pattern is None or not raw_text:
        return None
    match = pattern.search(raw_text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def strip_known_label(field_name: str, text: str) -> str:
    """If `text` still contains this field's label (e.g. a region crop
    that includes both the printed label and the value, such as "Pay to
    the order of: Bluepeak Distributors"), returns just the captured
    value portion. If the label isn't present, returns `text` unchanged
    -- this never removes anything from text that wasn't a recognized
    label, so it cannot turn a real value into a guess."""
    pattern = _PATTERNS.get(field_name)
    if pattern is None or not text:
        return text
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return text


def parse_bank_name(raw_text: str) -> str | None:
    """The bank name is printed as the first non-empty line of the
    cheque, with no distinguishing keyword -- handled as a special case
    rather than forced into the generic keyword table."""
    if not raw_text:
        return None
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None
