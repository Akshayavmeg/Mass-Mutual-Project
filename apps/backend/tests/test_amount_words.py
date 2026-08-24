"""Unit tests for words_to_amount() (docs/16_Validation_Engine.md S22),
the inverse of scripts/generate_synthetic_data.py's amount_to_words().

Covers whole-dollar amounts, the "and NN/100" cents fraction, and the
no-fabrication requirement that unrecognized input returns None rather
than a guessed partial amount.
"""

from __future__ import annotations

import pytest

from app.services.validation.amount_words import words_to_amount


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Seventeen Thousand Three Hundred Thirty Four and 23/100 Only", 17334.23),
        ("Nineteen Thousand Two Hundred Ninety Three and 83/100 Only", 19293.83),
        ("Three Thousand Four Hundred Eleven Only", 3411.0),
        ("Zero Only", 0.0),
        ("Zero and 23/100 Only", 0.23),
        ("One Hundred Only", 100.0),
        ("Twenty Five Only", 25.0),
        ("One Million Only", 1_000_000.0),
        ("One Million Two Hundred Thousand and 05/100 Only", 1_200_000.05),
        ("Five and 09/100 Only", 5.09),
    ],
)
def test_words_to_amount_parses_expected_value(text, expected):
    assert words_to_amount(text) == pytest.approx(expected, abs=0.001)


def test_words_to_amount_ignores_rs_and_rupees_and_and_tokens():
    assert words_to_amount("Rs. One Hundred and Twenty Five Only") == pytest.approx(125.0)


@pytest.mark.parametrize("text", [None, "", "   "])
def test_words_to_amount_returns_none_for_empty_input(text):
    assert words_to_amount(text) is None


def test_words_to_amount_returns_none_for_unrecognized_word():
    # "gibberish" is not a recognized number word -- must not guess.
    assert words_to_amount("Seventeen Thousand Gibberish Only") is None


def test_words_to_amount_returns_none_for_pure_punctuation():
    assert words_to_amount("*** ??? ///100") is None


def test_words_to_amount_cents_fraction_removed_before_word_tokenization():
    # The digits in "23/100" must not leak into the letters-only tokenizer
    # and must not be silently dropped either.
    result = words_to_amount("Ten and 23/100 Only")
    assert result == pytest.approx(10.23)
