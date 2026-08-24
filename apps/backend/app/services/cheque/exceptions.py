"""Cheque input errors.

Each carries the user-facing message and error code documented in
docs/12_Cheque_Input_Module.md S18 -- the API layer maps these to HTTP
status codes without exposing internal details (docs/12 S18: "The system
should avoid exposing internal technical details to the end user").
"""

from __future__ import annotations


class ChequeInputError(Exception):
    code = "PROCESSING_ERROR"
    message = "Cheque could not be processed. Please retry."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message


class EmptyUploadError(ChequeInputError):
    code = "EMPTY_UPLOAD"
    message = "Please select a cheque file."


class UnsupportedFileTypeError(ChequeInputError):
    code = "INVALID_FILE_TYPE"
    message = "Unsupported file format."


class FileTooLargeError(ChequeInputError):
    code = "FILE_TOO_LARGE"
    message = "File exceeds the maximum allowed size."


class CorruptedFileError(ChequeInputError):
    code = "CORRUPTED_FILE"
    message = "Unable to read the uploaded file."


class InvalidPDFError(ChequeInputError):
    code = "INVALID_PDF"
    message = "Unable to extract a valid cheque image from PDF."


class ImageUnreadableError(ChequeInputError):
    code = "IMAGE_UNREADABLE"
    message = "Image quality is insufficient for processing."
