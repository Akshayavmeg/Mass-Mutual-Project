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
    """docs/26_API_Specification.md S9 (Get Cheque Details).

    Milestone 9 extends this with the OCR-derived summary fields docs/26's
    own example shows (cheque_number, account_number, etc. -- now that
    Milestones 3-7 actually populate them) plus the full per-stage result
    dicts already persisted on the cheque record (ocr, extraction,
    validation, fraud_analysis, signature_analysis, anomaly_analysis,
    risk_assessment, decision, human_decision). This is the same
    "extend a canonical endpoint's response with the real, fuller data"
    precedent already used for every other Milestone 3-8 result endpoint
    (see e.g. ValidationResultResponse, FraudAnalysisResponse) rather than
    a new endpoint -- it lets a single GET reconstruct the complete
    processing state of a cheque for the frontend (Milestone 9's
    "every displayed cheque result must come from the backend API"
    requirement), each field staying null until that stage has actually
    run (never fabricated)."""

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

    # docs/26 S9 example summary fields, derived from the extracted fields.
    cheque_number: str | None = None
    account_number: str | None = None
    routing_transit_number: str | None = None
    payee_name: str | None = None
    amount: float | None = None
    cheque_date: str | None = None

    # Full per-stage results, already computed and persisted by
    # Milestones 3-7 -- null until that stage has run for this cheque.
    ocr: dict[str, Any] | None = None
    extraction: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    fraud_analysis: dict[str, Any] | None = None
    signature_analysis: dict[str, Any] | None = None
    anomaly_analysis: dict[str, Any] | None = None
    risk_assessment: dict[str, Any] | None = None
    decision: dict[str, Any] | None = None
    human_decision: dict[str, Any] | None = None


class ChequeSummaryResponse(BaseModel):
    """docs/26_API_Specification.md S10 (List Cheques) per-item shape."""

    cheque_id: str
    amount: float | None = None
    risk_level: str | None = None
    status: str
    payee_name: str | None = None
    cheque_date: str | None = None
    upload_timestamp: str
    decision: str | None = None


class ChequeListResponse(BaseModel):
    """docs/26_API_Specification.md S10 (List Cheques)."""

    page: int
    limit: int
    total: int
    cheques: list[ChequeSummaryResponse]


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
