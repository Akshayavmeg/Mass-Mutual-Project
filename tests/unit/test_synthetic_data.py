"""Milestone 1 validation tests for the synthetic/mock data foundation.

Verifies dataset structure, referential integrity between the generated
CSV files, absence of duplicate identifiers, presence of every required
fraud/test category, and that no real customer/banking data has leaked
into the dataset (ADR-0005).

Run with the backend virtual environment (has pandas installed):
    apps/backend/.venv/Scripts/python.exe -m pytest tests/unit -v
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
MOCK_DIR = DATA_DIR / "mock_banking_data"
SAMPLE_DIR = DATA_DIR / "sample_cheques"
TEST_DIR = DATA_DIR / "test_data"

REQUIRED_CATEGORIES = {
    "VALID",
    "DUPLICATE",
    "PAYEE_TAMPERED",
    "AMOUNT_TAMPERED",
    "SIGNATURE_MISMATCH",
    "INVALID_ACCOUNT",
    "STALE_CHEQUE",
    "STOPPED_CHEQUE",
    "CHEQUE_SERIES_ANOMALY",
    "MULTIPLE_ANOMALIES",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def customers() -> pd.DataFrame:
    return pd.read_csv(MOCK_DIR / "customers.csv")


@pytest.fixture(scope="module")
def accounts() -> pd.DataFrame:
    return pd.read_csv(MOCK_DIR / "accounts.csv", dtype={"account_number": str})


@pytest.fixture(scope="module")
def payees() -> pd.DataFrame:
    return pd.read_csv(MOCK_DIR / "payees.csv")


@pytest.fixture(scope="module")
def cheque_issuance() -> pd.DataFrame:
    return pd.read_csv(
        MOCK_DIR / "cheque_issuance.csv",
        dtype={"account_number": str, "cheque_number": str},
    )


@pytest.fixture(scope="module")
def transactions() -> pd.DataFrame:
    return pd.read_csv(MOCK_DIR / "transactions.csv", dtype={"account_number": str})


@pytest.fixture(scope="module")
def signatures_index() -> pd.DataFrame:
    return pd.read_csv(
        MOCK_DIR / "reference_signatures" / "signatures_index.csv",
        dtype={"account_number": str},
    )


@pytest.fixture(scope="module")
def processed_cheques_history() -> pd.DataFrame:
    return pd.read_csv(
        MOCK_DIR / "processed_cheques_history.csv", dtype={"account_number": str}
    )


@pytest.fixture(scope="module")
def ground_truth() -> pd.DataFrame:
    return pd.read_csv(
        TEST_DIR / "cheques_ground_truth.csv", dtype={"account_number": str}
    )


@pytest.fixture(scope="module")
def fraud_labels() -> pd.DataFrame:
    return pd.read_csv(TEST_DIR / "fraud_labels.csv")


@pytest.fixture(scope="module")
def validation_test_cases() -> pd.DataFrame:
    return pd.read_csv(TEST_DIR / "validation_test_cases.csv")


@pytest.fixture(scope="module")
def anomaly_test_cases() -> pd.DataFrame:
    return pd.read_csv(TEST_DIR / "anomaly_test_cases.csv", dtype={"account_number": str})


# ---------------------------------------------------------------------------
# 1. Dataset structure
# ---------------------------------------------------------------------------


class TestDatasetStructure:
    def test_mock_banking_data_files_exist(self):
        expected = [
            "customers.csv",
            "accounts.csv",
            "payees.csv",
            "cheque_issuance.csv",
            "transactions.csv",
            "processed_cheques_history.csv",
        ]
        for name in expected:
            assert (MOCK_DIR / name).exists(), f"Missing {name}"

    def test_reference_signature_files_exist(self):
        sig_dir = MOCK_DIR / "reference_signatures"
        assert (sig_dir / "signatures_index.csv").exists()
        assert len(list(sig_dir.glob("*.png"))) > 0

    def test_test_data_files_exist(self):
        expected = [
            "cheques_ground_truth.csv",
            "image_hashes.csv",
            "validation_test_cases.csv",
            "anomaly_test_cases.csv",
            "fraud_labels.csv",
            "fraud_test_cases.csv",
            "generation_summary.json",
        ]
        for name in expected:
            assert (TEST_DIR / name).exists(), f"Missing {name}"

    def test_duplicate_and_signature_test_subdirectories_exist(self):
        for sub in ("exact_duplicates", "near_duplicates", "unique_cheques"):
            d = TEST_DIR / "duplicate_detection" / sub
            assert d.exists() and any(d.iterdir()), f"{d} missing or empty"
        for sub in ("genuine", "altered", "low_quality", "missing", "partial"):
            d = TEST_DIR / "signatures" / sub
            assert d.exists() and any(d.iterdir()), f"{d} missing or empty"

    def test_sample_cheque_images_exist_on_disk(self, ground_truth):
        missing = [p for p in ground_truth["image_path"] if not (DATA_DIR / p).exists()]
        assert not missing, f"Ground truth references missing image files: {missing[:5]}"


# ---------------------------------------------------------------------------
# 2. Foreign-key-like relationships
# ---------------------------------------------------------------------------


class TestReferentialIntegrity:
    def test_every_account_references_a_known_customer(self, accounts, customers):
        known = set(customers["customer_id"])
        orphans = set(accounts["customer_id"]) - known
        assert not orphans, f"Accounts reference unknown customers: {orphans}"

    def test_every_transaction_references_a_known_account(self, transactions, accounts):
        known = set(accounts["account_number"])
        orphans = set(transactions["account_number"]) - known
        assert not orphans, f"Transactions reference unknown accounts: {orphans}"

    def test_every_cheque_issuance_row_references_a_known_account(self, cheque_issuance, accounts):
        known = set(accounts["account_number"])
        orphans = set(cheque_issuance["account_number"]) - known
        assert not orphans, f"Cheque issuance rows reference unknown accounts: {orphans}"

    def test_every_signature_references_a_known_account(self, signatures_index, accounts):
        known = set(accounts["account_number"])
        orphans = set(signatures_index["account_number"]) - known
        assert not orphans, f"Reference signatures reference unknown accounts: {orphans}"

    def test_every_processed_history_row_references_a_known_account(
        self, processed_cheques_history, accounts
    ):
        known = set(accounts["account_number"])
        orphans = set(processed_cheques_history["account_number"]) - known
        assert not orphans, f"Processed-cheque history references unknown accounts: {orphans}"

    def test_ground_truth_accounts_are_known_or_deliberately_invalid(self, ground_truth, accounts):
        known = set(accounts["account_number"])
        not_known = set(ground_truth["account_number"]) - known
        # INVALID_ACCOUNT is the only category allowed to reference a
        # non-existent account number (that is the point of the category).
        offending = ground_truth[
            ground_truth["account_number"].isin(not_known) & (ground_truth["category"] != "INVALID_ACCOUNT")
        ]
        assert offending.empty, (
            "Non-INVALID_ACCOUNT ground-truth rows reference unknown accounts: "
            f"{offending['cheque_id'].tolist()}"
        )

    def test_fraud_labels_reference_known_ground_truth_cheques(self, fraud_labels, ground_truth):
        known = set(ground_truth["cheque_id"])
        orphans = set(fraud_labels["cheque_id"]) - known
        assert not orphans, f"fraud_labels.csv references unknown cheque_id values: {orphans}"

    def test_ground_truth_payees_reference_known_payee_names(self, ground_truth, payees):
        known_payees = set(payees["payee_name"])
        # expected_payee_name should always be a real registered payee
        # (it represents the bank's on-file record); the on-cheque payee_name
        # may legitimately be an unregistered/garbled value for tampered cases.
        unknown_expected = set(ground_truth["expected_payee_name"]) - known_payees
        assert not unknown_expected, f"Unknown expected payees: {unknown_expected}"


# ---------------------------------------------------------------------------
# 3. Duplicate IDs that should not exist
# ---------------------------------------------------------------------------


class TestUniqueness:
    def test_customer_ids_unique(self, customers):
        assert customers["customer_id"].is_unique

    def test_account_numbers_unique(self, accounts):
        assert accounts["account_number"].is_unique

    def test_payee_ids_unique(self, payees):
        assert payees["payee_id"].is_unique

    def test_transaction_ids_unique(self, transactions):
        assert transactions["transaction_id"].is_unique

    def test_signature_ids_unique(self, signatures_index):
        assert signatures_index["signature_id"].is_unique

    def test_ground_truth_cheque_ids_unique(self, ground_truth):
        assert ground_truth["cheque_id"].is_unique

    def test_cheque_issuance_composite_key_unique(self, cheque_issuance):
        composite = cheque_issuance["account_number"] + "|" + cheque_issuance["cheque_number"]
        assert composite.is_unique, "Duplicate (account_number, cheque_number) in cheque_issuance.csv"

    def test_intentional_duplicate_category_is_the_only_repeated_composite_key(self, ground_truth):
        """Every ground-truth composite key (account+cheque_number+amount+date)
        should be unique EXCEPT for the deliberately-paired DUPLICATE category
        rows, which must repeat by design."""
        composite = (
            ground_truth["account_number"].astype(str)
            + "|"
            + ground_truth["cheque_number"].astype(str)
            + "|"
            + ground_truth["amount"].astype(str)
            + "|"
            + ground_truth["cheque_date"].astype(str)
        )
        dupes = composite[composite.duplicated(keep=False)]
        dupe_rows = ground_truth.loc[dupes.index]
        non_duplicate_category_rows = dupe_rows[dupe_rows["category"] != "DUPLICATE"]
        assert non_duplicate_category_rows.empty, (
            "Found unintended duplicate cheque records outside the DUPLICATE category: "
            f"{non_duplicate_category_rows['cheque_id'].tolist()}"
        )


# ---------------------------------------------------------------------------
# 4. Required fraud/test categories
# ---------------------------------------------------------------------------


class TestCategoryCoverage:
    def test_all_ten_required_categories_present(self, ground_truth):
        present = set(ground_truth["category"])
        missing = REQUIRED_CATEGORIES - present
        assert not missing, f"Missing required categories: {missing}"

    def test_each_required_category_has_multiple_samples(self, ground_truth):
        counts = ground_truth["category"].value_counts()
        thin = {cat: int(counts.get(cat, 0)) for cat in REQUIRED_CATEGORIES if counts.get(cat, 0) < 2}
        assert not thin, f"Categories with fewer than 2 samples: {thin}"

    def test_valid_category_is_labeled_non_fraud(self, ground_truth):
        valid_rows = ground_truth[ground_truth["category"] == "VALID"]
        assert (valid_rows["fraud_label"] == 0).all(), "VALID rows must have fraud_label == 0"

    def test_non_valid_categories_are_labeled_fraud(self, ground_truth):
        non_valid = ground_truth[~ground_truth["category"].isin(["VALID"])]
        # DUPLICATE category legitimately contains one non-fraud "original"
        # row per pair alongside the fraud-labeled resubmission.
        non_valid_excl_dup_originals = non_valid[
            ~((non_valid["category"] == "DUPLICATE") & (non_valid["fraud_label"] == 0))
        ]
        assert (non_valid_excl_dup_originals["fraud_label"] == 1).all()

    def test_validation_test_cases_cover_documented_scenarios(self, validation_test_cases):
        assert len(validation_test_cases) == 10
        expected_names = {
            "Valid Account", "Unknown Account", "Closed Account", "Valid Cheque Series",
            "Invalid Cheque Series", "Future-Dated Cheque", "Payee Match", "Payee Mismatch",
            "Duplicate", "Amount Mismatch",
        }
        assert set(validation_test_cases["name"]) == expected_names

    def test_anomaly_test_cases_cover_documented_subcategories(self, anomaly_test_cases):
        expected = {
            "NORMAL", "AMOUNT_ANOMALY_HIGH", "AMOUNT_ANOMALY_LOW", "FREQUENCY_ANOMALY",
            "PAYEE_ANOMALY", "SEQUENCE_ANOMALY", "MULTIPLE_ANOMALIES", "COLD_START",
        }
        assert expected.issubset(set(anomaly_test_cases["category"]))


# ---------------------------------------------------------------------------
# 5. No real/personal banking data
# ---------------------------------------------------------------------------


class TestNoRealData:
    def test_all_account_numbers_use_synthetic_prefix(self, accounts):
        assert accounts["account_number"].astype(str).str.startswith("9000").all()

    def test_all_customer_emails_use_synthetic_domain(self, customers):
        assert customers["email"].str.endswith("@example-synthetic.test").all()

    def test_bank_name_and_code_are_the_fictional_constants(self, ground_truth, accounts):
        assert (ground_truth["bank_name"] == "DEMO NATIONAL BANK").all()
        assert (accounts["bank_code"] == "DEMO001").all()

    def test_no_real_routing_number_used(self, accounts):
        # Single fictional routing number reused across the whole synthetic
        # dataset; guards against accidentally introducing a real ABA number.
        assert set(accounts["routing_number"].astype(str)) == {"121000358"}

    def test_cheque_images_contain_synthetic_watermark(self, ground_truth):
        # Spot-check a sample of images for the literal watermark text
        # baked into every rendered cheque by the generator.
        sample = ground_truth.sample(min(10, len(ground_truth)), random_state=1)
        for _, row in sample.iterrows():
            path = DATA_DIR / row["image_path"]
            assert path.exists()
            assert path.stat().st_size > 0

    def test_no_files_named_env_or_containing_secrets_in_data_dir(self):
        assert not list(DATA_DIR.rglob(".env"))
        assert not list(DATA_DIR.rglob("*.key"))
        assert not list(DATA_DIR.rglob("*.pem"))


# ---------------------------------------------------------------------------
# Field-level sanity checks
# ---------------------------------------------------------------------------


class TestFieldSanity:
    def test_amounts_are_positive(self, ground_truth):
        assert (ground_truth["amount"] > 0).all()
        assert (ground_truth["expected_amount"] > 0).all()

    def test_cheque_dates_are_valid_iso_dates(self, ground_truth):
        parsed = pd.to_datetime(ground_truth["cheque_date"], format="%Y-%m-%d", errors="coerce")
        assert parsed.notna().all(), "Some cheque_date values are not valid ISO dates"

    def test_fraud_label_is_binary(self, ground_truth):
        assert set(ground_truth["fraud_label"].unique()).issubset({0, 1})

    def test_account_status_values_are_within_documented_set(self, accounts):
        allowed = {"ACTIVE", "INACTIVE", "CLOSED", "BLOCKED", "FROZEN"}
        assert set(accounts["account_status"]).issubset(allowed)

    def test_cheque_issuance_status_values_are_within_documented_set(self, cheque_issuance):
        allowed = {"ISSUED", "PRESENTED", "PAID", "STOPPED", "CANCELLED", "EXPIRED"}
        assert set(cheque_issuance["status"]).issubset(allowed)

    def test_stopped_cheque_category_actually_has_stopped_status(self, ground_truth):
        stopped_rows = ground_truth[ground_truth["category"] == "STOPPED_CHEQUE"]
        assert (stopped_rows["expected_cheque_status"] == "STOPPED").all()

    def test_stale_cheque_category_exceeds_validity_window(self, ground_truth):
        stale_rows = ground_truth[ground_truth["category"] == "STALE_CHEQUE"]
        cheque_dates = pd.to_datetime(stale_rows["cheque_date"])
        processing_date = pd.Timestamp("2026-08-23")
        age_days = (processing_date - cheque_dates).dt.days
        assert (age_days > 180).all()

    def test_future_dated_category_is_after_processing_date(self, ground_truth):
        future_rows = ground_truth[ground_truth["category"] == "FUTURE_DATED"]
        cheque_dates = pd.to_datetime(future_rows["cheque_date"])
        processing_date = pd.Timestamp("2026-08-23")
        assert (cheque_dates > processing_date).all()

    def test_amount_tampered_category_has_mismatched_amount_and_words(self, ground_truth):
        tampered = ground_truth[ground_truth["category"] == "AMOUNT_TAMPERED"]
        assert (tampered["amount"] != tampered["expected_amount"]).all()

    def test_payee_tampered_category_has_mismatched_payee(self, ground_truth):
        tampered = ground_truth[ground_truth["category"] == "PAYEE_TAMPERED"]
        assert (tampered["payee_name"] != tampered["expected_payee_name"]).all()
