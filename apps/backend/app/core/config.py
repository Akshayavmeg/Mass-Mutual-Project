"""Application configuration.

Loads non-secret defaults from the shared/environment YAML files under
``config/`` and layers environment-variable-based overrides (via
``pydantic-settings``) on top for anything sensitive (database URL, secret
key). Secrets must never be committed to the repository; they are supplied
through a local ``.env`` file (see ``.env.example``) or real environment
variables.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/backend/app/core/config.py -> repo root is four levels up
REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = REPO_ROOT / "config"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_yaml_config(environment: str) -> dict[str, Any]:
    """Merge config/settings.yaml with the environment-specific override file."""
    base = _load_yaml(CONFIG_DIR / "settings.yaml")
    override = _load_yaml(CONFIG_DIR / f"{environment}.yaml")
    return _deep_merge(base, override)


class Settings(BaseSettings):
    """Environment-variable-backed settings. Never hard-code secrets here."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    app_name: str = "Mass Mutual Cheque Fraud Detection System"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/mass_mutual_db"
    secret_key: str = "changeme-local-development-only"

    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]

    max_upload_size_mb: int = 10

    # --- Milestone 2: Cheque Input & Image Preprocessing --------------
    # These are intentionally configuration fields (not hard-coded inside
    # the processing logic), per docs/36_Development_Guidelines.md S9 and
    # docs/12_Cheque_Input_Module.md S6 -- all are explicitly documented as
    # "example prototype rules" to be calibrated later, not fixed banking
    # standards.
    allowed_upload_extensions: list[str] = [".jpg", ".jpeg", ".png", ".pdf"]

    # Below this size an image is treated as unreadable/invalid (hard
    # rejection). Below the "soft" size the image is accepted but flagged
    # as poor quality (docs/12 S7: "reject / request better image").
    min_hard_width_px: int = 80
    min_hard_height_px: int = 40
    min_soft_width_px: int = 500
    min_soft_height_px: int = 220

    # Laplacian-variance sharpness threshold; below this the image is
    # flagged as blurred (docs/13 S17). Calibratable per docs' own caveat.
    # Calibrated against the Milestone 1 synthetic cheque images (clean
    # samples measure ~2500); a threshold two orders of magnitude below
    # that comfortably separates genuinely blurred test images.
    blur_variance_threshold: float = 150.0

    # Mean pixel intensity (0-255) bounds for "too dark"/"too bright".
    # Calibrated against the Milestone 1 synthetic cheque images: their
    # light cream background measures ~mean 240-250, which is normal for
    # a document photo/scan and must not be flagged as "washed out".
    brightness_dark_threshold: float = 90.0
    brightness_bright_threshold: float = 251.0

    # Standard-deviation-of-intensity threshold below which contrast
    # enhancement (CLAHE) is applied. Calibrated so the Milestone 1
    # synthetic cheques (mostly white background, sparse text -> std
    # dev ~28-30) read as acceptable, while a genuinely low-contrast
    # (e.g. faded) image still triggers enhancement.
    contrast_enhancement_threshold: float = 22.0

    # Skew angle (degrees) beyond which deskew rotation is applied.
    skew_correction_threshold_degrees: float = 1.0

    # Simple noise proxy (mean abs diff vs. median-blurred version);
    # above this the image is flagged as noisy.
    noise_threshold: float = 6.0

    # Controlled upscaling target when an image is smaller than this on
    # its longer side but still above the hard-minimum resolution.
    target_working_long_side_px: int = 1600
    max_upscale_factor: float = 2.5

    # --- Milestone 3: OCR & Cheque Data Extraction ---------------------
    # Per ADR-0002, Tesseract via PyTesseract, invoked only through the
    # OCR adapter interface (app/services/ocr/engine.py). The binary path
    # is configurable since Tesseract is a native executable, not a pure
    # Python package -- pytesseract only calls out to it.
    tesseract_cmd_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Below this average confidence (Tesseract's own 0-100 scale) the OCR
    # result is treated as LOW_CONFIDENCE and a retry with an alternate
    # image representation is attempted (docs/14 S16-S17). Explicitly a
    # calibratable prototype default, not a proven accuracy threshold.
    ocr_low_confidence_threshold: float = 55.0

    # Below this per-field confidence, an individual extracted field is
    # flagged low-confidence even if the overall OCR run succeeded.
    ocr_field_low_confidence_threshold: float = 40.0

    # Minimum fraction of non-background pixels in the signature region
    # for it to be reported as "signature detected" (docs/15 S21). This is
    # region *detection* only -- not comparison/verification.
    signature_region_ink_ratio_threshold: float = 0.01

    # --- Milestone 4: Validation Engine ---------------------------------
    # Business thresholds, per docs/16_Validation_Engine.md's repeated
    # instruction that these must be configuration, not hard-coded inside
    # validation functions (S16 date validity; S21 amount limits).
    mock_banking_data_dir: str = "data/mock_banking_data"

    # A cheque older than this many days (relative to the processing
    # date) is treated as stale/expired (docs/16 S16). Matches the
    # assumption documented in scripts/generate_synthetic_data.py so the
    # Milestone 1 STALE_CHEQUE category is evaluated consistently.
    cheque_validity_period_days: int = 180

    # Whether a cheque dated after the processing date should be allowed
    # to PASS date validation (docs/16 S15). Default false: future-dated
    # cheques fail DATE_WINDOW.
    allow_future_dated_cheques: bool = False

    # Maximum permitted cheque amount (docs/16 S21). Matches the
    # `amount_limit` used in the Milestone 1 mock cheque-issuance registry.
    max_permitted_cheque_amount: float = 500000.00

    # Per-check severities (docs/16 S27: "Severity values should be
    # configurable"). Defaults follow docs/16 S27's own example table
    # where it gives one explicitly (e.g. stopped cheque = CRITICAL,
    # payee mismatch = HIGH); checks the table doesn't cover are assigned
    # a documented, reasonable default severity (see Milestone 4 report).
    validation_severities: dict[str, str] = {
        "REQUIRED_FIELDS": "HIGH",
        "ACCOUNT_EXISTS": "HIGH",
        "ACCOUNT_STATUS": "HIGH",
        "CHEQUE_SERIES": "MEDIUM",
        "CHEQUE_STATUS": "HIGH",
        "CHEQUE_STATUS_STOPPED": "CRITICAL",
        "DATE_WINDOW": "MEDIUM",
        "PAYEE_MATCH": "HIGH",
        "ROUTING_TRANSIT": "MEDIUM",
        "AMOUNT": "HIGH",
        "AMOUNT_CONSISTENCY": "HIGH",
        "DUPLICATE_CHECK": "HIGH",
        "CROSS_FIELD": "MEDIUM",
    }

    # --- Milestone 5: Fraud Detection Engine ----------------------------
    # docs/17_Fraud_Detection.md S21 documents the fraud engine's own
    # internal risk composition (image/validation/duplicate/anomaly/
    # transaction risk) as distinct from the later, separate Risk Scoring
    # Module (docs/21, Milestone 6/7) that additionally folds in
    # signature and OCR-confidence risk -- these weights are the fraud
    # engine's own prototype configuration, not the final risk formula.
    fraud_score_weights: dict[str, float] = {
        "tampering": 30.0,
        "validation_signal": 25.0,
        "duplicate": 30.0,
        "pattern": 15.0,
    }

    # 0-100 fraud_risk_score bands (docs/17 S21, initial project
    # thresholds -- not proven banking thresholds).
    fraud_risk_bands: dict[str, list[int]] = {
        "LOW": [0, 29],
        "MEDIUM": [30, 59],
        "HIGH": [60, 79],
        "CRITICAL": [80, 100],
    }

    # RULE-005: number of HIGH+CRITICAL-severity fraud indicators that
    # triggers a mandatory manual-review escalation regardless of the
    # numeric score (docs/17 S19).
    fraud_multi_indicator_review_threshold: int = 2

    # Image tampering detector (docs/17 S7-S9): per-region statistics are
    # compared against the cheque's own background reference rather than
    # any external/trained baseline. Thresholds are explicitly prototype
    # values pending calibration against a larger dataset.
    tampering_regions: list[str] = ["amount", "payee_name", "date", "cheque_number"]
    tampering_noise_zscore_threshold: float = 2.5
    tampering_edge_zscore_threshold: float = 2.5
    tampering_score_review_threshold: float = 0.5

    # Multi-level duplicate detection (docs/19 S12-S16): prototype
    # similarity thresholds, explicitly calibratable.
    duplicate_perceptual_hash_size: int = 8
    duplicate_confirmed_similarity_threshold: float = 0.95
    duplicate_potential_similarity_threshold: float = 0.80

    # Pattern/behavioral indicators (docs/20 S9-S13): initial statistical
    # thresholds, not banking-industry norms.
    pattern_amount_zscore_threshold: float = 3.0
    pattern_min_history_for_amount_baseline: int = 3
    pattern_frequency_window_days: int = 2
    pattern_frequency_baseline_days: int = 30
    pattern_frequency_ratio_threshold: float = 3.0
    pattern_cheque_sequence_gap_threshold: int = 50

    fraud_engine_version: str = "fraud-engine-v1.0-rule-based"

    # Number of FAILed Milestone 4 validation checks that constitutes
    # "multiple validation failures" as its own fraud indicator (docs/17
    # S18/S1 indicator #12).
    validation_multiple_failures_threshold: int = 2

    def yaml_config(self) -> dict[str, Any]:
        return load_yaml_config(self.environment)

    @property
    def runtime_data_dir(self) -> Path:
        return REPO_ROOT / "data" / "runtime"

    @property
    def runtime_original_dir(self) -> Path:
        return self.runtime_data_dir / "original"

    @property
    def runtime_processed_dir(self) -> Path:
        return self.runtime_data_dir / "processed"

    @property
    def mock_banking_data_path(self) -> Path:
        return REPO_ROOT / self.mock_banking_data_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
