"""OCR adapter interface (docs/14_OCR_Engine.md, FR-008).

FR-008: "The OCR engine shall be implemented through an adapter/interface
so that the underlying OCR provider can be replaced without redesigning
the complete system." Everything downstream of OCR (extraction,
normalization, and later validation/fraud modules) depends only on
`OCREngine` / `WordBox` / `OCRRawResult` defined here -- never on
PyTesseract or any other library directly. A future Google Vision/Azure
AI Vision/AWS Textract adapter would implement the same `OCREngine`
protocol and could be substituted without touching any other module
(ADR-0002).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class WordBox:
    """A single recognized word with its position and confidence, in the
    coordinate space of the image that was passed to the engine.

    block_num/par_num/line_num/word_num are the engine's own reading-order
    indices (Tesseract numbers every word this way). They are used to sort
    words within a region in genuine reading order, which is materially
    more reliable than re-deriving row order from raw pixel Y-coordinates
    -- two words on the same printed line can still differ by several
    pixels in measured top/height depending on ascenders/descenders."""

    text: str
    left: int
    top: int
    width: int
    height: int
    confidence: float  # engine-native confidence scale (Tesseract: 0-100; -1 if unavailable)
    block_num: int = 0
    par_num: int = 0
    line_num: int = 0
    word_num: int = 0

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> tuple[float, float]:
        return (self.left + self.width / 2, self.top + self.height / 2)


@dataclass
class OCRRawResult:
    """Everything the OCR adapter itself is responsible for producing --
    no field extraction or interpretation happens here (docs/14 S30:
    OCR is NOT responsible for extraction/validation/scoring)."""

    engine_name: str
    engine_version: str
    raw_text: str
    words: list[WordBox] = field(default_factory=list)
    average_confidence: float = 0.0  # mean of word confidences with conf >= 0 (Tesseract uses -1 for non-text)
    image_width: int = 0
    image_height: int = 0
    processing_time_ms: float = 0.0
    status: str = "COMPLETED"  # PENDING | PROCESSING | COMPLETED | LOW_CONFIDENCE | PARTIAL | FAILED
    error_message: str | None = None


class OCREngine(Protocol):
    """The adapter interface every OCR provider implementation must
    satisfy. `run` receives an already-preprocessed image (a BGR/gray
    numpy array, as produced by Milestone 2) and returns a fully-formed
    OCRRawResult -- it must never raise for a "just poor recognition"
    case; only genuine engine failures should raise OCREngineError."""

    def run(self, image: np.ndarray, *, config: str | None = None) -> OCRRawResult: ...

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...
