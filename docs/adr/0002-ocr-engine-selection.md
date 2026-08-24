# ADR-0002: OCR Engine Selection

## Status

Accepted

## Decision

The system will use **Tesseract OCR**, invoked from the Python backend through the **PyTesseract** wrapper, accessed exclusively through a **replaceable OCR adapter/interface** so the underlying OCR provider can be swapped without redesigning the processing pipeline.

## Context

`FR-008` requires that "the OCR engine shall be implemented through an adapter/interface so that the underlying OCR provider can be replaced without redesigning the complete system." `14_OCR_Engine.md` documents Tesseract as the selected engine for the MVP, with cloud OCR services identified only as future, non-committed alternatives. The project is a prototype built and evaluated against synthetic cheque data, and must not claim the use of a paid or cloud OCR service unless it has actually been implemented and evaluated (`11_Technology_Stack.md` §25).

## Alternatives Considered

* **Google Cloud Vision** — higher potential accuracy, but a paid cloud service requiring external credentials and network dependency; not appropriate for an MVP built and evaluated on synthetic data without incurring cost or cloud coupling.
* **Azure AI Vision** — same trade-offs as Google Cloud Vision.
* **AWS Textract** — same trade-offs as Google Cloud Vision; also introduces AWS-specific coupling inconsistent with the project's cloud-agnostic stance (`AWS / Azure / GCP` all listed only as optional future deployment targets, not commitments).
* **Tesseract OCR (selected)** — open source, integrates directly with Python and OpenCV, requires no external service or credentials, and is well suited to prototyping against a synthetic dataset.

## Selected Approach

Tesseract OCR via PyTesseract, wrapped behind an OCR adapter interface (e.g., an `OCREngine` abstraction in `app/services/ocr/`) so that Google Vision, Azure AI Vision, AWS Textract, or another engine could later be substituted by implementing the same interface, without changes to preprocessing, extraction, validation, or any downstream module.

## Reason for Selection

* Avoids introducing a paid or cloud-dependent service into a prototype whose primary goal is to demonstrate the end-to-end workflow against synthetic data.
* Integrates natively with the OpenCV-based preprocessing pipeline (ADR — image processing, `13_Image_Preprocessing.md`).
* Provides recognized text, per-element bounding boxes, and confidence scores, which are the inputs the Cheque Data Extraction and Validation modules require (`15_Cheque_Data_Extraction.md`, `16_Validation_Engine.md`).
* Satisfies `FR-008`'s adapter/interface requirement by design, keeping the door open to a cloud OCR evaluation later without an architectural rewrite.

## Consequences

* The measured OCR accuracy achieved with Tesseract against the project's synthetic dataset is what will be reported — the ≥95% target (`NFR-002`) is not assumed to be met simply by selecting Tesseract, and must be demonstrated through the evaluation described in `32_OCR_Evaluation.md`.
* If Tesseract's measured accuracy is insufficient, the adapter interface allows a cloud OCR engine to be evaluated as a follow-up without redesigning the OCR-Engine, Data-Extraction, or Validation modules.
* `requirements.txt` must include `pytesseract`, and the deployment environment must have the native Tesseract binary installed separately (it is not a pure Python package).
