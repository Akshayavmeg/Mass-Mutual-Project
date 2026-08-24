"""Original/processed file storage (docs/13_Image_Preprocessing.md S23).

Originals and processed working copies are kept in separate directories
under data/runtime/ so the original is never at risk of being overwritten
by preprocessing (docs/13 S4: "The original cheque image must remain
unchanged"). This runtime directory is gitignored -- it holds copies of
whatever a caller uploads, and per docs/12 S19 real cheque data must never
be committed to the repository.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.core.config import settings


def _ensure_dirs() -> None:
    settings.runtime_original_dir.mkdir(parents=True, exist_ok=True)
    settings.runtime_processed_dir.mkdir(parents=True, exist_ok=True)


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def original_file_path(cheque_id: str, extension: str) -> Path:
    """Filename is derived entirely from the generated Processing ID, not
    from the user-supplied filename, which prevents path traversal and
    filename-injection issues (docs/36 S22)."""
    return settings.runtime_original_dir / f"{cheque_id}{extension}"


def processed_file_path(cheque_id: str) -> Path:
    return settings.runtime_processed_dir / f"{cheque_id}.png"


def save_original(cheque_id: str, extension: str, content: bytes) -> Path:
    _ensure_dirs()
    path = original_file_path(cheque_id, extension)
    path.write_bytes(content)
    return path


def original_bytes_unchanged(cheque_id: str, extension: str, original_content: bytes) -> bool:
    """Verifies the stored original still matches what was uploaded --
    used by tests to confirm preprocessing never mutates it in place."""
    path = original_file_path(cheque_id, extension)
    if not path.exists():
        return False
    return path.read_bytes() == original_content
