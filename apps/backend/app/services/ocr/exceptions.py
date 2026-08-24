from __future__ import annotations


class OCREngineError(Exception):
    """Base class for OCR-engine-level failures. Callers must catch this
    and route the cheque to a FAILED/manual-review-eligible state rather
    than crash (docs/14_OCR_Engine.md S16: "The system should not
    automatically assume that an OCR result is correct" / must fail
    safely on engine problems)."""


class OCREngineUnavailableError(OCREngineError):
    """The underlying OCR engine (e.g. the Tesseract binary) could not be
    invoked at all -- distinct from the engine running and producing a
    poor/empty result."""


class ChequeNotPreprocessedError(Exception):
    """Raised when OCR is requested for a cheque that hasn't successfully
    completed Milestone 2 preprocessing yet."""
