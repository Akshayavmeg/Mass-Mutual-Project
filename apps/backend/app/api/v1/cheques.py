"""Cheque upload, detail, OCR, and validation endpoints.

Implements exactly the endpoints these milestones need from the canonical
contract (docs/26_API_Specification.md SS8-9, S11-S14): upload, get
details, run OCR, get OCR result, run validation, get validation result.
No fraud/decision endpoints are added here -- those belong to later
milestones.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.anomaly import AnomalyAnalysisResponse
from app.schemas.cheque import ChequeDetailResponse, ChequeUploadResponse
from app.schemas.decision import DecisionResponse
from app.schemas.fraud import FraudAnalysisResponse
from app.schemas.ocr import OCRResultResponse, OCRStartResponse
from app.schemas.risk import RiskScoreResponse
from app.schemas.signature import SignatureAnalysisResponse
from app.schemas.validation import ValidationResultResponse
from app.services.anomaly import anomaly_service
from app.services.anomaly.exceptions import ChequeNotExtractedForAnomalyError
from app.services.cheque import input_service
from app.services.cheque.exceptions import ChequeInputError
from app.services.decision import decision_service
from app.services.decision.exceptions import RiskAssessmentNotAvailableError
from app.services.fraud import fraud_service
from app.services.fraud.exceptions import ChequeNotValidatedError
from app.services.ocr import pipeline as ocr_pipeline
from app.services.ocr.exceptions import ChequeNotPreprocessedError
from app.services.risk import risk_service
from app.services.risk.exceptions import FraudAnalysisNotAvailableError
from app.services.signature import signature_service
from app.services.signature.exceptions import ChequeNotExtractedForSignatureError
from app.services.validation import validation_service
from app.services.validation.exceptions import ChequeNotExtractedError

router = APIRouter(prefix="/cheques", tags=["cheques"])


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """docs/26_API_Specification.md S36 error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": f"REQ-{uuid.uuid4().hex[:12]}"}},
    )


_ERROR_STATUS_CODES = {
    "EMPTY_UPLOAD": 400,
    "INVALID_FILE_TYPE": 415,
    "FILE_TOO_LARGE": 413,
    "CORRUPTED_FILE": 400,
    "INVALID_PDF": 400,
    "IMAGE_UNREADABLE": 400,
}


@router.post("/upload", status_code=201, response_model=ChequeUploadResponse)
async def upload_cheque(file: UploadFile = File(...)):
    content = await file.read()

    try:
        record = input_service.handle_upload(file.filename, content)
    except ChequeInputError as exc:
        status_code = _ERROR_STATUS_CODES.get(exc.code, 400)
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": exc.message, "status": "REJECTED"},
        )

    return ChequeUploadResponse(
        success=True,
        cheque_id=record["cheque_id"],
        status="UPLOADED",
        message="Cheque uploaded successfully.",
    )


@router.get("/{cheque_id}", response_model=ChequeDetailResponse)
async def get_cheque(cheque_id: str):
    record = input_service.get_cheque_record(cheque_id)
    if record is None:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    return ChequeDetailResponse(**record)


def _build_ocr_result_response(cheque_id: str, ocr: dict, extraction: dict) -> OCRResultResponse:
    outer_status = "FAILED" if ocr["ocr_status"] == "FAILED" else "SUCCESS"
    return OCRResultResponse(
        cheque_id=cheque_id,
        engine=ocr["engine_name"],
        engine_version=ocr["engine_version"],
        ocr_status=ocr["ocr_status"],
        confidence_score=ocr["average_confidence"],
        raw_text=ocr["raw_text"],
        ocr_processing_time_ms=ocr["processing_time_ms"],
        extraction_status=extraction["extraction_status"],
        extraction_processing_time_ms=extraction["processing_time_ms"],
        missing_fields=extraction["missing_fields"],
        ambiguous_fields=extraction["ambiguous_fields"],
        template=extraction["template"],
        signature_region_detected=extraction["signature_region_detected"],
        signature_region_bbox=extraction["signature_region_bbox"],
        extracted_data=extraction["fields"],
        status=outer_status,
        error_message=ocr.get("error_message"),
    )


@router.post("/{cheque_id}/ocr", response_model=OCRStartResponse)
async def run_ocr(cheque_id: str):
    try:
        result = ocr_pipeline.run_ocr_and_extraction(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except ChequeNotPreprocessedError as exc:
        return _error_response(422, "CHEQUE_NOT_PREPROCESSED", str(exc))

    return OCRStartResponse(
        cheque_id=cheque_id,
        status=result["ocr"]["ocr_status"],
        ocr_confidence=result["ocr"]["average_confidence"],
    )


@router.get("/{cheque_id}/ocr", response_model=OCRResultResponse)
async def get_ocr_result(cheque_id: str):
    result = ocr_pipeline.get_ocr_and_extraction(cheque_id)
    if result is None:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    if result["ocr"] is None:
        return _error_response(404, "OCR_NOT_RUN", "OCR has not been run for this cheque yet.")

    return _build_ocr_result_response(cheque_id, result["ocr"], result["extraction"])


@router.post("/{cheque_id}/validate", response_model=ValidationResultResponse)
async def run_validation(cheque_id: str):
    try:
        summary = validation_service.validate_cheque(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except ChequeNotExtractedError as exc:
        return _error_response(422, "CHEQUE_NOT_EXTRACTED", str(exc))

    return ValidationResultResponse(**summary.as_dict())


@router.get("/{cheque_id}/validation", response_model=ValidationResultResponse)
async def get_validation_result(cheque_id: str):
    record = input_service.get_cheque_record(cheque_id)
    if record is None:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")

    validation = validation_service.get_validation_result(cheque_id)
    if validation is None:
        return _error_response(404, "VALIDATION_NOT_RUN", "Validation has not been run for this cheque yet.")

    return ValidationResultResponse(**validation)


def _build_fraud_analysis_response(payload: dict) -> FraudAnalysisResponse:
    tampering_detected = bool(payload.get("image_analysis", {}).get("image_tampering_score") or 0) and any(
        ind["type"] == "IMAGE_TAMPERING" for ind in payload.get("indicators", [])
    )
    return FraudAnalysisResponse(tampering_detected=tampering_detected, **payload)


@router.post("/{cheque_id}/fraud-analysis", response_model=FraudAnalysisResponse)
async def run_fraud_analysis(cheque_id: str):
    try:
        result = fraud_service.analyze_fraud(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except ChequeNotValidatedError as exc:
        return _error_response(422, "CHEQUE_NOT_VALIDATED", str(exc))

    payload = fraud_service.get_fraud_result(cheque_id)
    return _build_fraud_analysis_response(payload)


@router.get("/{cheque_id}/fraud-analysis", response_model=FraudAnalysisResponse)
async def get_fraud_analysis(cheque_id: str):
    record = input_service.get_cheque_record(cheque_id)
    if record is None:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")

    payload = fraud_service.get_fraud_result(cheque_id)
    if payload is None:
        return _error_response(404, "FRAUD_ANALYSIS_NOT_RUN", "Fraud analysis has not been run for this cheque yet.")

    return _build_fraud_analysis_response(payload)


@router.post("/{cheque_id}/signature-analysis", response_model=SignatureAnalysisResponse)
async def run_signature_analysis(cheque_id: str):
    try:
        result = signature_service.analyze_signature(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except ChequeNotExtractedForSignatureError as exc:
        return _error_response(422, "CHEQUE_NOT_EXTRACTED", str(exc))

    return SignatureAnalysisResponse(**result.as_dict())


@router.post("/{cheque_id}/anomaly-analysis", response_model=AnomalyAnalysisResponse)
async def run_anomaly_analysis(cheque_id: str):
    try:
        result = anomaly_service.analyze_anomaly(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except ChequeNotExtractedForAnomalyError as exc:
        return _error_response(422, "CHEQUE_NOT_EXTRACTED", str(exc))

    return AnomalyAnalysisResponse(**result.as_dict())


@router.post("/{cheque_id}/risk-score", response_model=RiskScoreResponse)
async def run_risk_score(cheque_id: str):
    try:
        result = risk_service.calculate_risk(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except FraudAnalysisNotAvailableError as exc:
        return _error_response(422, "FRAUD_ANALYSIS_NOT_RUN", str(exc))

    return RiskScoreResponse(**result.as_dict())


@router.post("/{cheque_id}/decision", response_model=DecisionResponse)
async def run_decision(cheque_id: str):
    try:
        result = decision_service.make_decision(cheque_id)
    except KeyError:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")
    except RiskAssessmentNotAvailableError as exc:
        return _error_response(422, "RISK_ASSESSMENT_NOT_RUN", str(exc))

    return DecisionResponse(**result.as_dict())


@router.get("/{cheque_id}/decision", response_model=DecisionResponse)
async def get_decision(cheque_id: str):
    record = input_service.get_cheque_record(cheque_id)
    if record is None:
        return _error_response(404, "CHEQUE_NOT_FOUND", "The requested cheque does not exist.")

    payload = decision_service.get_decision(cheque_id)
    if payload is None:
        return _error_response(404, "DECISION_NOT_RUN", "A decision has not been made for this cheque yet.")

    return DecisionResponse(**payload)
