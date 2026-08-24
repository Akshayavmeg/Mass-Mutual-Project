"""Milestone 3 tests: field normalization (docs/15_Cheque_Data_Extraction.md
S11-S22). Pure-function unit tests -- no OCR engine involved."""

from __future__ import annotations

from app.services.extraction import normalization


class TestNormalizeAmount:
    def test_currency_symbol_and_commas_stripped(self):
        assert normalization.normalize_amount("$17,334.23") == 17334.23

    def test_rupee_style_amount(self):
        assert normalization.normalize_amount("Rs. 25,000/-") == 25000.0

    def test_plain_number(self):
        assert normalization.normalize_amount("450.00") == 450.0

    def test_label_prefix_does_not_break_parsing(self):
        assert normalization.normalize_amount("Amount: $1,234.56") == 1234.56

    def test_empty_or_none_returns_none(self):
        assert normalization.normalize_amount(None) is None
        assert normalization.normalize_amount("") is None

    def test_garbage_text_returns_none_not_a_guess(self):
        assert normalization.normalize_amount("not a number") is None

    def test_negative_amount_rejected(self):
        assert normalization.normalize_amount("-500.00") is None

    def test_multiple_decimal_points_rejected(self):
        assert normalization.normalize_amount("12.34.56") is None


class TestNormalizeDate:
    def test_dd_mm_yyyy_to_iso(self):
        assert normalization.normalize_date("11/08/2026") == "2026-08-11"

    def test_date_with_label_prefix(self):
        assert normalization.normalize_date("Date: 15/08/2026") == "2026-08-15"

    def test_date_with_dashes(self):
        assert normalization.normalize_date("15-08-2026") == "2026-08-15"

    def test_already_iso_format(self):
        assert normalization.normalize_date("2026-08-15") == "2026-08-15"

    def test_unparseable_text_returns_none(self):
        assert normalization.normalize_date("not a date") is None

    def test_none_returns_none(self):
        assert normalization.normalize_date(None) is None

    def test_impossible_date_returns_none(self):
        # Day 32 is not valid in any month -- must not be silently accepted.
        assert normalization.normalize_date("32/13/2026") is None


class TestNormalizeChequeNumber:
    def test_leading_zeros_preserved(self):
        assert normalization.normalize_cheque_number("000123") == "000123"

    def test_label_prefix_stripped_via_digit_extraction(self):
        assert normalization.normalize_cheque_number("Cheque No 000123") == "000123"

    def test_non_digit_text_returns_none(self):
        assert normalization.normalize_cheque_number("Cheque No") is None

    def test_none_returns_none(self):
        assert normalization.normalize_cheque_number(None) is None


class TestNormalizeAccountNumber:
    def test_digits_extracted(self):
        assert normalization.normalize_account_number("Account No 9000010020") == "9000010020"

    def test_none_returns_none(self):
        assert normalization.normalize_account_number(None) is None


class TestNormalizeRoutingTransitNumber:
    def test_digits_extracted(self):
        assert normalization.normalize_routing_transit_number("121000358") == "121000358"

    def test_label_and_slash_do_not_corrupt_result(self):
        assert normalization.normalize_routing_transit_number("Routing/Transit No: 121000358") == "121000358"


class TestNormalizePayeeName:
    def test_whitespace_collapsed(self):
        assert normalization.normalize_payee_name("Bluepeak   Distributors") == "Bluepeak Distributors"

    def test_leading_trailing_whitespace_trimmed(self):
        assert normalization.normalize_payee_name("  John Doe  ") == "John Doe"

    def test_none_returns_none(self):
        assert normalization.normalize_payee_name(None) is None

    def test_no_fuzzy_matching_or_correction(self):
        # Normalization must not "correct" spelling -- that would be
        # inventing a value the OCR engine did not actually produce.
        assert normalization.normalize_payee_name("Bluepeek Distributers") == "Bluepeek Distributers"
