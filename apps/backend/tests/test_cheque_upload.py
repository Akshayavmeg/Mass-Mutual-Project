"""Milestone 2 tests: cheque upload / input handling.

Covers docs/12_Cheque_Input_Module.md's documented behaviors: supported
formats, file validation (extension/size/integrity), Processing ID
generation, original-file preservation, and safe failure for invalid
input.
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.repositories.cheque_repository import get_cheque_repository
from app.services.cheque import storage

client = TestClient(app)


def _make_png_bytes(size=(600, 300), color=(250, 249, 244)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_jpeg_bytes(size=(600, 300), color=(250, 249, 244)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_pdf_bytes(size=(600, 300)) -> bytes:
    img = Image.new("RGB", size, (250, 249, 244))
    buf = io.BytesIO()
    img.save(buf, format="PDF")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _clean_repository():
    yield
    get_cheque_repository().clear_for_testing()


class TestValidUploads:
    def test_valid_png_upload_returns_201_and_cheque_id(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.png", _make_png_bytes(), "image/png")},
        )
        body = resp.json()
        assert resp.status_code == 201
        assert body["success"] is True
        assert body["status"] == "UPLOADED"
        assert body["cheque_id"].startswith("CHK-")

    def test_valid_jpeg_upload_returns_201(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        assert resp.status_code == 201
        assert resp.json()["success"] is True

    def test_valid_jpeg_extension_variant_accepted(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.jpeg", _make_jpeg_bytes(), "image/jpeg")},
        )
        assert resp.status_code == 201

    def test_valid_pdf_upload_returns_201(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.pdf", _make_pdf_bytes(), "application/pdf")},
        )
        assert resp.status_code == 201
        assert resp.json()["success"] is True


class TestInvalidUploads:
    def test_unsupported_file_extension_is_rejected(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.gif", b"GIF89a" + b"\x00" * 20, "image/gif")},
        )
        assert resp.status_code == 415
        body = resp.json()
        assert body["success"] is False
        assert body["status"] == "REJECTED"

    def test_disguised_executable_with_image_extension_is_rejected(self):
        """A file renamed to .png but not actually PNG content must be
        caught by content validation, not just the extension."""
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("fake.png", b"MZ\x90\x00this is not a real png", "image/png")},
        )
        assert resp.status_code == 415

    def test_truncated_png_with_valid_signature_is_rejected_as_corrupted(self):
        """Valid PNG magic bytes but truncated/invalid body -- must be
        caught by actual image decoding, not just the signature check."""
        real_png = _make_png_bytes()
        truncated = real_png[:20]  # keep the PNG signature, drop the rest
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("truncated.png", truncated, "image/png")},
        )
        assert resp.status_code in (400, 415)
        assert resp.json()["success"] is False

    def test_oversized_file_is_rejected(self):
        base = _make_png_bytes()
        oversized = base + (b"\x00" * (11 * 1024 * 1024))
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("huge.png", oversized, "image/png")},
        )
        assert resp.status_code == 413
        assert resp.json()["status"] == "REJECTED"

    def test_empty_upload_is_rejected(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("empty.png", b"", "image/png")},
        )
        assert resp.status_code in (400, 415)
        assert resp.json()["success"] is False

    def test_extremely_low_resolution_image_is_rejected(self):
        """Below the hard minimum resolution the image is unreadable for
        any practical purpose and must be rejected outright, per
        docs/12 S7."""
        tiny = _make_png_bytes(size=(10, 5))
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("tiny.png", tiny, "image/png")},
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False

    def test_invalid_pdf_content_is_rejected(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("bad.pdf", b"%PDF-1.4\nnot actually a valid pdf structure", "application/pdf")},
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False

    def test_rejected_upload_does_not_get_a_processing_id(self):
        """docs/12 S16: the REJECTED response does not include a
        cheque_id -- Processing IDs are only issued after validation
        passes."""
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.gif", b"GIF89a" + b"\x00" * 20, "image/gif")},
        )
        assert "cheque_id" not in resp.json()


class TestProcessingIdAndTraceability:
    def test_processing_id_format(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.png", _make_png_bytes(), "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        import re
        assert re.match(r"^CHK-\d{4}-\d{6}$", cheque_id)

    def test_processing_ids_are_unique_across_uploads(self):
        ids = set()
        for _ in range(5):
            resp = client.post(
                "/api/v1/cheques/upload",
                files={"file": ("cheque.png", _make_png_bytes(), "image/png")},
            )
            ids.add(resp.json()["cheque_id"])
        assert len(ids) == 5

    def test_cheque_is_retrievable_by_its_processing_id(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.png", _make_png_bytes(), "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        detail = client.get(f"/api/v1/cheques/{cheque_id}")
        assert detail.status_code == 200
        assert detail.json()["cheque_id"] == cheque_id

    def test_unknown_cheque_id_returns_404_with_error_envelope(self):
        resp = client.get("/api/v1/cheques/CHK-2026-999999")
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["code"] == "CHEQUE_NOT_FOUND"
        assert "request_id" in body["error"]

    def test_metadata_fields_recorded_on_upload(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("my_cheque.png", _make_png_bytes(), "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
        assert detail["file_name"] == "my_cheque.png"
        assert detail["file_type"] == "image/png"
        assert detail["file_size"] > 0
        assert detail["input_source"] == "UPLOAD"
        assert detail["upload_timestamp"]
        assert len(detail["file_hash"]) == 64  # sha256 hex digest


class TestOriginalImagePreservation:
    def test_original_file_stored_unchanged_on_disk(self):
        content = _make_png_bytes()
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.png", content, "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        assert storage.original_bytes_unchanged(cheque_id, ".png", content)

    def test_processed_output_is_a_separate_file_from_the_original(self):
        content = _make_png_bytes()
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("cheque.png", content, "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        original_path = storage.original_file_path(cheque_id, ".png")
        processed_path = storage.processed_file_path(cheque_id)
        assert original_path != processed_path
        assert original_path.exists()
        assert processed_path.exists()
        # The original bytes must be identical to what was uploaded --
        # i.e. preprocessing operated on a copy, never in place.
        assert original_path.read_bytes() == content


class TestSecurity:
    def test_path_traversal_filename_is_sanitized(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("../../etc/passwd.png", _make_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        cheque_id = resp.json()["cheque_id"]
        detail = client.get(f"/api/v1/cheques/{cheque_id}").json()
        assert "/" not in detail["file_name"]
        assert ".." not in detail["file_name"]

    def test_original_file_path_is_derived_from_processing_id_not_filename(self):
        resp = client.post(
            "/api/v1/cheques/upload",
            files={"file": ("../../weird name!!.png", _make_png_bytes(), "image/png")},
        )
        cheque_id = resp.json()["cheque_id"]
        path = storage.original_file_path(cheque_id, ".png")
        assert path.name == f"{cheque_id}.png"
        assert path.exists()
