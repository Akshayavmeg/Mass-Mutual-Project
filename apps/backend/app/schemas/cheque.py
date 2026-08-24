from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ChequeUploadResponse(BaseModel):
    """docs/12_Cheque_Input_Module.md S21 / docs/26_API_Specification.md S8."""

    success: bool
    cheque_id: str
    status: str
    message: str


class QualityFactorResponse(BaseModel):
    name: str
    value: float
    status: str
    message: str


class QualityResultResponse(BaseModel):
    quality_status: str
    skew_angle_degrees: float
    factors: list[QualityFactorResponse]


class PreprocessingMetadataResponse(BaseModel):
    """docs/13_Image_Preprocessing.md S24 processing-metadata shape."""

    preprocessing_status: str
    operations: list[str]
    processed_width: int | None = None
    processed_height: int | None = None
    processing_time_ms: float
    error_message: str | None = None
    quality: QualityResultResponse | None = None


class ChequeDetailResponse(BaseModel):
    """docs/26_API_Specification.md S9 (Get Cheque Details), restricted to
    the fields this milestone actually knows about -- OCR-derived fields
    (cheque_number, account_number, payee_name, amount, cheque_date) are
    intentionally absent until Milestone 3 populates them for real, per
    the "do not fabricate extracted cheque values" constraint."""

    cheque_id: str
    file_name: str
    file_type: str
    file_size: int
    input_source: str
    upload_timestamp: str
    file_hash: str
    original_width: int | None = None
    original_height: int | None = None
    pdf_page_count: int | None = None
    processing_status: str
    preprocessing: PreprocessingMetadataResponse | None = None
    error: dict[str, Any] | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
