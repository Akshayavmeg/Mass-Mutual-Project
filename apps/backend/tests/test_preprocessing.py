"""Milestone 2 tests: image quality assessment and preprocessing pipeline.

Uses a real Milestone 1 synthetic cheque image as the clean baseline, and
programmatically derives degraded variants (blurred, rotated, dark,
noisy, low-resolution) since the Milestone 1 dataset's own categories
vary cheque *content* (fraud/validation scenarios), not image *quality* --
image-quality degradation is this milestone's own concern per
docs/13_Image_Preprocessing.md S28's documented test categories.
"""

from __future__ import annotations

import glob
import io
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageEnhance, ImageFilter

from app.main import app
from app.repositories.cheque_repository import get_cheque_repository

client = TestClient(app)

# Absolute, invocation-directory-independent path (works whether pytest is
# run from apps/backend/ or the repo root).
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SAMPLE_PATHS = glob.glob(str(_REPO_ROOT / "data" / "sample_cheques" / "valid" / "*.png"))


@pytest.fixture(autouse=True)
def _clean_repository():
    yield
    get_cheque_repository().clear_for_testing()


@pytest.fixture(scope="module")
def base_cheque_bytes() -> bytes:
    assert _SAMPLE_PATHS, "Milestone 1 sample cheques not found -- run scripts/generate_synthetic_data.py"
    with open(_SAMPLE_PATHS[0], "rb") as handle:
        return handle.read()


def _upload_and_get_quality(content: bytes, filename="cheque.png") -> dict:
    resp = client.post("/api/v1/cheques/upload", files={"file": (filename, content, "image/png")})
    assert resp.status_code == 201
    cheque_id = resp.json()["cheque_id"]
    detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
    return detail


class TestCleanImage:
    def test_clean_cheque_is_acceptable_quality(self, base_cheque_bytes):
        detail = _upload_and_get_quality(base_cheque_bytes)
        assert detail["preprocessing"]["quality"]["quality_status"] == "ACCEPTABLE"
        assert detail["preprocessing"]["preprocessing_status"] == "COMPLETED"

    def test_operations_recorded_for_clean_image(self, base_cheque_bytes):
        detail = _upload_and_get_quality(base_cheque_bytes)
        operations = detail["preprocessing"]["operations"]
        assert "grayscale" in operations
        # noise_reduction is applied conditionally (docs/13 S5: don't
        # apply operations blindly) -- a clean image's own noise factor
        # should read PASS, so denoising is correctly skipped for it.
        # (Milestone 3's real OCR evaluation showed unconditional median
        # denoising measurably hurt recognition accuracy on already-clean
        # synthetic cheque text, which is what motivated this milestone's
        # tightening of the trigger condition.)
        noise_factor = next(f for f in detail["preprocessing"]["quality"]["factors"] if f["name"] == "noise")
        assert ("noise_reduction" in operations) == (noise_factor["status"] == "WARNING")

    def test_processing_time_is_recorded_and_positive(self, base_cheque_bytes):
        detail = _upload_and_get_quality(base_cheque_bytes)
        assert detail["preprocessing"]["processing_time_ms"] > 0

    def test_processed_image_dimensions_present(self, base_cheque_bytes):
        detail = _upload_and_get_quality(base_cheque_bytes)
        assert detail["preprocessing"]["processed_width"] > 0
        assert detail["preprocessing"]["processed_height"] > 0


class TestBlurHandling:
    def test_blurred_image_is_flagged_poor_quality(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=4))
        buf = io.BytesIO()
        blurred.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "blurred.png")
        factors = {f["name"]: f for f in detail["preprocessing"]["quality"]["factors"]}
        assert factors["blur"]["status"] == "WARNING"
        assert detail["preprocessing"]["quality"]["quality_status"] in ("POOR", "UNSUITABLE")


class TestRotationAndSkewHandling:
    def test_rotated_image_skew_is_detected(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        rotated = img.rotate(8, expand=True, fillcolor=(250, 249, 244))
        buf = io.BytesIO()
        rotated.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "rotated.png")
        factors = {f["name"]: f for f in detail["preprocessing"]["quality"]["factors"]}
        assert factors["skew"]["status"] == "WARNING"
        assert abs(detail["preprocessing"]["quality"]["skew_angle_degrees"]) > 1

    def test_deskew_operation_applied_for_skewed_image(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        rotated = img.rotate(10, expand=True, fillcolor=(250, 249, 244))
        buf = io.BytesIO()
        rotated.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "rotated2.png")
        assert "deskew" in detail["preprocessing"]["operations"]

    def test_upright_image_does_not_trigger_deskew(self, base_cheque_bytes):
        detail = _upload_and_get_quality(base_cheque_bytes)
        assert "deskew" not in detail["preprocessing"]["operations"]


class TestBrightnessAndContrast:
    def test_dark_image_is_flagged(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        dark = ImageEnhance.Brightness(img).enhance(0.35)
        buf = io.BytesIO()
        dark.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "dark.png")
        factors = {f["name"]: f for f in detail["preprocessing"]["quality"]["factors"]}
        assert factors["brightness"]["status"] == "WARNING"

    def test_low_contrast_image_triggers_contrast_enhancement_operation(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        flat = ImageEnhance.Contrast(img).enhance(0.15)
        buf = io.BytesIO()
        flat.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "flat.png")
        assert "contrast_enhancement" in detail["preprocessing"]["operations"]


class TestNoiseHandling:
    def test_noisy_image_is_flagged(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes)).convert("RGB")
        arr = np.array(img).astype(np.int16)
        rng = np.random.default_rng(1)
        noise = rng.normal(0, 25, arr.shape).astype(np.int16)
        noisy_arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(noisy_arr).save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "noisy.png")
        factors = {f["name"]: f for f in detail["preprocessing"]["quality"]["factors"]}
        assert factors["noise"]["status"] == "WARNING"


class TestResolutionHandling:
    def test_low_resolution_image_is_flagged_and_still_processed(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        small = img.resize((300, 140))
        buf = io.BytesIO()
        small.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "lowres.png")
        factors = {f["name"]: f for f in detail["preprocessing"]["quality"]["factors"]}
        assert factors["resolution"]["status"] == "WARNING"
        # Still above the hard minimum, so it must be accepted and
        # processed (with a controlled upscale), not rejected outright.
        assert detail["preprocessing"]["preprocessing_status"] == "COMPLETED"
        assert "resize" in detail["preprocessing"]["operations"]

    def test_upscaling_is_capped_not_unlimited(self, base_cheque_bytes):
        img = Image.open(io.BytesIO(base_cheque_bytes))
        small = img.resize((200, 95))
        buf = io.BytesIO()
        small.save(buf, format="PNG")

        detail = _upload_and_get_quality(buf.getvalue(), "tiny_but_valid.png")
        # max_upscale_factor is 2.5x in config -- resulting long side
        # should not exceed 200 * 2.5 by more than rounding.
        assert detail["preprocessing"]["processed_width"] <= 200 * 2.5 + 5


class TestFraudAnalysisConsideration:
    def test_preprocessing_does_not_overwrite_original_color_information(self, base_cheque_bytes):
        """docs/13 S22: the fraud pipeline must not depend exclusively on
        a heavily thresholded OCR image -- verifies the original file on
        disk is untouched color/full-fidelity data, independent of
        whatever the OCR-oriented processed image looks like."""
        from app.services.cheque import storage

        resp = client.post(
            "/api/v1/cheques/upload", files={"file": ("cheque.png", base_cheque_bytes, "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        original_path = storage.original_file_path(cheque_id, ".png")
        with Image.open(original_path) as original_img:
            assert original_img.mode in ("RGB", "RGBA", "P")  # never binarized/thresholded
