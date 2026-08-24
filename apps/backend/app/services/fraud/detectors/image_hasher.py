"""Exact and perceptual image hashing (docs/19_Duplicate_Detection.md
S8-S11, Level 2/3 duplicate evidence).

The average-hash (aHash) algorithm here is deliberately identical to
scripts/generate_synthetic_data.py's `average_hash()`, which precomputed
`perceptual_hash` values into data/mock_banking_data/processed_cheques_history.csv
and data/test_data/image_hashes.csv "purely as a reference value for
later milestones to consume" -- using the same algorithm and hash_size
here means this milestone's computed hashes are directly comparable
(via Hamming distance) against those precomputed reference values.
"""

from __future__ import annotations

import hashlib
import io

from PIL import Image


def sha256_of_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def average_hash_of_bytes(content: bytes, hash_size: int = 8) -> str:
    with Image.open(io.BytesIO(content)) as img:
        gray = img.convert("L").resize((hash_size, hash_size))
        pixels = list(gray.tobytes())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p > avg else "0" for p in pixels)
    return f"{int(bits, 2):0{hash_size * hash_size // 4}x}"


def hamming_distance_hex(hash_a: str, hash_b: str) -> int:
    if not hash_a or not hash_b:
        return max(len(hash_a or ""), len(hash_b or "")) * 4
    a, b = int(hash_a, 16), int(hash_b, 16)
    return bin(a ^ b).count("1")


def similarity_from_hamming(distance: int, hash_size: int = 8) -> float:
    """Converts a Hamming distance over `hash_size**2` bits into a
    0.00-1.00 similarity score (docs/19 S12)."""
    total_bits = hash_size * hash_size
    return max(0.0, 1.0 - (distance / total_bits))
