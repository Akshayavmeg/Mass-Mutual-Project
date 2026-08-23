# Image Preprocessing

# 13. Image Preprocessing

## 1. Introduction

The **Image Preprocessing Module** is responsible for converting an uploaded cheque image into a clean, standardized, and OCR-ready image.

Cheque images may contain problems such as:

* Noise
* Low contrast
* Blur
* Uneven lighting
* Rotation
* Skew
* Shadows
* Background patterns
* Poor image quality
* Unnecessary borders or margins

These issues can reduce OCR accuracy and may also affect later fraud-detection and signature-analysis operations.

Therefore, the preprocessing module is placed between the **Cheque Input Module** and the **OCR Engine**.

```text
Cheque Input
     ↓
Image Preprocessing
     ↓
OCR Engine
     ↓
Cheque Data Extraction
     ↓
Validation & Fraud Detection
```

---

# 2. Objectives

The main objectives of the Image Preprocessing Module are:

1. Validate the readability of the cheque image.
2. Convert the image into a standardized format.
3. Remove unwanted noise.
4. Improve image contrast.
5. Correct image rotation and skew.
6. Detect and crop unnecessary background areas.
7. Improve the visibility of cheque text.
8. Prepare the image for OCR.
9. Preserve important cheque information.
10. Generate a consistent image representation for downstream processing.
11. Preserve the original image separately for audit and fraud analysis.

---

# 3. Input to the Module

The module receives a validated cheque from the **Cheque Input Module**.

Example input:

```json
{
  "cheque_id": "CHK-2026-000001",
  "file_path": "secure-storage/CHK-2026-000001.jpg",
  "file_type": "image/jpeg",
  "status": "READY_FOR_PREPROCESSING"
}
```

For a PDF input, the PDF page containing the cheque is first rendered into an image before image-processing operations are performed.

---

# 4. Output of the Module

After preprocessing, the module produces an OCR-ready image.

Example:

```json
{
  "cheque_id": "CHK-2026-000001",
  "preprocessed_image": "processed/CHK-2026-000001.png",
  "status": "READY_FOR_OCR"
}
```

The original cheque image must remain unchanged.

```text
Original Image
      │
      ├──────────────► Secure Original Storage
      │
      ▼
Preprocessing
      │
      ▼
Processed Image
      │
      ▼
OCR
```

This is important because the original image may later be required for:

* Fraud investigation
* Manual review
* Audit
* Signature comparison
* Evidence/reference

---

# 5. Preprocessing Pipeline

The proposed preprocessing pipeline is:

```text
                  Input Cheque
                       │
                       ▼
              Format Normalization
                       │
                       ▼
                Image Validation
                       │
                       ▼
                  Grayscale
                       │
                       ▼
                Noise Reduction
                       │
                       ▼
              Contrast Enhancement
                       │
                       ▼
                  Thresholding
                       │
                       ▼
              Deskew / Rotation
                       │
                       ▼
              Border / Crop Check
                       │
                       ▼
               Resolution Check
                       │
                       ▼
              Quality Assessment
                       │
                       ▼
              OCR-Ready Image
```

Not every operation must be applied aggressively to every cheque. The pipeline should select preprocessing operations based on the image characteristics so that useful information is not accidentally removed.

---

# 6. Format Normalization

The first step is to convert supported input formats into a standard internal image representation.

For example:

```text
JPEG ──┐
PNG  ──┼──► Standard Image ──► Preprocessing
PDF  ──┘
```

A standard format such as PNG can be used internally for the processed image.

The system should retain the original uploaded file separately.

---

# 7. Image Validation

Before processing, the system checks whether the image can be processed successfully.

Checks include:

* Image can be opened.
* Image contains valid pixel data.
* Image dimensions are valid.
* Image is not completely blank.
* Image is not excessively damaged.
* Image contains sufficient visual information.

Example:

```text
Image
  ↓
Can image be opened?
  │
 ┌┴──────────────┐
 ▼               ▼
YES              NO
 │               │
 ▼               ▼
Continue        Error
```

---

# 8. Grayscale Conversion

A cheque is generally processed more efficiently by converting its image from RGB/color representation into grayscale.

Example:

```text
Color Image
    ↓
Grayscale Conversion
    ↓
Gray Image
```

Instead of processing three color channels:

```text
Red
Green
Blue
```

the system works with a single intensity channel.

This reduces computational complexity and can make text processing easier.

---

# 9. Noise Reduction

Cheque images may contain unwanted noise caused by:

* Scanner imperfections
* Camera sensors
* Paper texture
* Compression
* Dust
* Background patterns

Noise reduction can be performed using OpenCV filters.

Possible techniques include:

* Gaussian blur
* Median filtering
* Bilateral filtering

For example:

```text
Noisy Image
     ↓
Median Filter
     ↓
Cleaner Image
```

The filter should be selected carefully because excessive smoothing can remove thin characters or cheque details.

---

# 10. Contrast Enhancement

Poor contrast can make cheque text difficult to recognize.

The system can improve contrast using techniques such as:

* Histogram equalization
* CLAHE (Contrast Limited Adaptive Histogram Equalization)

Example:

```text
Low Contrast
     ↓
Contrast Enhancement
     ↓
Clearer Text
```

This is particularly useful when the cheque has uneven lighting or faded text.

---

# 11. Thresholding

Thresholding converts a grayscale image into a representation where foreground text can be separated from the background.

Basic concept:

```text
Grayscale Image
      ↓
Thresholding
      ↓
Foreground + Background
```

Possible methods include:

* Global thresholding
* Otsu thresholding
* Adaptive thresholding

Adaptive thresholding can be useful when lighting is not uniform across the cheque.

However, thresholding should not always be applied blindly because cheque backgrounds, security patterns, and signatures can be affected.

---

# 12. Deskewing

A cheque may be scanned or photographed at an angle.

Example:

```text
Before:

 ┌──────────────────────
  \  CHEQUE INFORMATION
   \____________________

After:

 ┌──────────────────────┐
 │  CHEQUE INFORMATION  │
 └──────────────────────┘
```

The system should estimate the skew angle and rotate the image accordingly.

Typical steps:

```text
Image
  ↓
Detect dominant lines/edges
  ↓
Estimate skew angle
  ↓
Rotate image
  ↓
Corrected image
```

OpenCV can be used for this operation.

---

# 13. Rotation Correction

The system should identify whether the cheque is:

* Correctly oriented
* Rotated 90°
* Rotated 180°
* Rotated 270°

If necessary, the image can be rotated before OCR.

Example:

```text
Incorrect Orientation
        ↓
Orientation Detection
        ↓
Rotation
        ↓
Correct Orientation
```

For the MVP, orientation handling should focus on common image-capture cases rather than attempting to solve every possible orientation automatically.

---

# 14. Cropping and Border Removal

Uploaded images may contain unnecessary areas around the cheque.

Example:

```text
┌─────────────────────────────┐
│                             │
│    ┌───────────────────┐    │
│    │      CHEQUE       │    │
│    │                   │    │
│    └───────────────────┘    │
│                             │
└─────────────────────────────┘
```

The system can detect the cheque boundary and crop unnecessary background.

Expected result:

```text
┌───────────────────────┐
│       CHEQUE          │
│                       │
│   Relevant Content    │
│                       │
└───────────────────────┘
```

This can improve OCR performance by reducing irrelevant visual information.

---

# 15. Resolution Enhancement

OCR performance depends heavily on image quality.

If the image is too small, the system may perform controlled resizing before OCR.

```text
Low Resolution
      ↓
Quality Check
      ↓
Controlled Resize
      ↓
OCR Processing
```

Upscaling cannot recreate information that was never captured. Therefore, extremely low-quality images should be flagged rather than relying on enlargement alone.

---

# 16. Image Quality Assessment

The module should calculate basic image-quality indicators.

Possible indicators include:

| Quality Factor | Purpose                                          |
| -------------- | ------------------------------------------------ |
| Resolution     | Determines whether sufficient detail exists      |
| Brightness     | Detects overly dark/light images                 |
| Contrast       | Measures separation between text/background      |
| Blur           | Detects out-of-focus images                      |
| Skew           | Determines alignment                             |
| Noise          | Estimates unwanted image interference            |
| Cropping       | Determines whether cheque boundaries are visible |

Example:

```text
Image Quality Score
        ↓
 ┌──────┴──────┐
 ▼             ▼
Accept       Poor Quality
 ▼             ▼
OCR          Re-upload /
             Manual Review
```

The exact thresholds should be established experimentally using the project's sample cheque dataset.

---

# 17. Blur Detection

Blur can significantly reduce OCR accuracy.

One possible approach is to calculate a sharpness measure based on the **Laplacian variance**.

Conceptually:

```text
Sharp Image
    ↓
Higher sharpness measure
    ↓
Suitable
```

```text
Blurred Image
    ↓
Lower sharpness measure
    ↓
Quality warning
```

The threshold should be calibrated using sample images rather than assuming one universal value.

---

# 18. Image Preprocessing Using OpenCV

The primary computer-vision library for this project will be **OpenCV**.

Possible processing sequence:

```python
image
  ↓
cv2.imread()
  ↓
grayscale
  ↓
noise reduction
  ↓
contrast enhancement
  ↓
thresholding
  ↓
deskew
  ↓
crop/resize
  ↓
OCR-ready image
```

OpenCV provides the necessary image-processing operations for the MVP.

---

# 19. Multiple Preprocessing Variants

A single preprocessing method may not work equally well for every cheque image.

Therefore, the system can maintain multiple preprocessing strategies.

Example:

```text
                    Input Image
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Variant A       Variant B      Variant C
      Grayscale       CLAHE          Adaptive
      + Threshold     + Threshold    Threshold
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    OCR Evaluation
```

The system can compare OCR confidence/results and select the most suitable representation when necessary.

For the initial MVP, a simpler deterministic pipeline is preferable. More advanced multi-variant processing can be added after measuring baseline OCR performance.

---

# 20. Region Preservation

A critical requirement is that preprocessing must **not destroy information needed by later modules**.

Important regions include:

```text
┌──────────────────────────────────────────┐
│                CHEQUE                    │
│                                          │
│ Payee: _________________________________ │
│                                          │
│ Date: __________                         │
│                                          │
│ Amount: ________________________________ │
│                                          │
│ Account Information                      │
│                                          │
│ Signature Area                           │
│                                          │
│ Cheque Number / MICR Information         │
└──────────────────────────────────────────┘
```

The preprocessing stage must preserve:

* Text
* Signature
* Cheque number
* Account information
* Routing/transit information
* Security features that may be relevant to fraud analysis

Therefore, the original image must always be retained.

---

# 21. OCR-Specific Preprocessing

The OCR engine requires a clean representation of text.

The preprocessing module should optimize the image for:

```text
Cheque
  ↓
Text visibility
  ↓
Character separation
  ↓
OCR
```

The preprocessing process should be evaluated based on its effect on the project's OCR target of:

> **OCR extraction accuracy ≥ 95%**

The 95% value is a project target, not a guaranteed result. It must be demonstrated through evaluation on the project's test dataset.

---

# 22. Fraud-Detection Consideration

Preprocessing has two different purposes:

### OCR processing

The system may use:

```text
Grayscale
Noise removal
Thresholding
Contrast enhancement
```

### Fraud analysis

The system may need:

```text
Original image
High-resolution image
Color information
Security patterns
Signature region
Tampering indicators
```

Therefore:

```text
                    Original Image
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       OCR Preprocessing        Fraud Analysis
             │                       │
             ▼                       ▼
         OCR Image              Original/
                                 Analysis Image
```

**The fraud-detection pipeline must not depend exclusively on a heavily thresholded OCR image.**

---

# 23. Storage of Processed Images

The project can maintain separate references for:

```text
Original:
data/runtime/original/

Processed:
data/runtime/processed/

Debug:
data/runtime/debug/
```

For the Git repository, actual sensitive runtime cheque images should not be committed.

Synthetic sample data can be stored separately under:

```text
data/sample_cheques/
```

---

# 24. Processing Metadata

The preprocessing stage should record metadata such as:

```json
{
  "cheque_id": "CHK-2026-000001",
  "original_format": "image/jpeg",
  "processed_format": "image/png",
  "original_width": 1800,
  "original_height": 900,
  "preprocessing_status": "COMPLETED",
  "operations": [
    "grayscale",
    "noise_reduction",
    "contrast_enhancement",
    "deskew"
  ]
}
```

This information helps with debugging, evaluation, and auditability.

---

# 25. Error Handling

Possible errors include:

| Error                    | Action                                  |
| ------------------------ | --------------------------------------- |
| Image cannot be opened   | Reject processing                       |
| Corrupted image          | Request re-upload                       |
| Extremely low resolution | Flag for re-upload/manual review        |
| Excessive blur           | Flag image quality issue                |
| Missing cheque boundary  | Attempt correction or request re-upload |
| Processing failure       | Record error and stop pipeline          |
| Unsupported format       | Reject input                            |

The original image should remain available for investigation when permitted.

---

# 26. Functional Requirements

The Image Preprocessing Module shall:

1. Accept validated cheque images from the input module.
2. Normalize supported image formats.
3. Convert images to grayscale where appropriate.
4. Reduce image noise.
5. Improve image contrast.
6. Apply thresholding where beneficial.
7. Correct skew and orientation where possible.
8. Remove unnecessary borders/background.
9. Assess basic image quality.
10. Generate an OCR-ready image.
11. Preserve the original cheque image.
12. Record preprocessing metadata.
13. Handle preprocessing errors safely.
14. Pass successfully processed images to the OCR engine.

---

# 27. Non-Functional Requirements

### Performance

Preprocessing should be optimized so that it does not significantly contribute to exceeding the project's overall target of:

```text
< 30 seconds per cheque
```

### Reliability

The module should handle common image-quality problems without crashing the processing pipeline.

### Maintainability

Individual preprocessing operations should be implemented as modular functions.

Example:

```text
preprocess_image()
├── normalize_image()
├── convert_to_grayscale()
├── reduce_noise()
├── enhance_contrast()
├── correct_skew()
├── crop_image()
└── assess_quality()
```

### Traceability

Each processed image must remain associated with its:

```text
cheque_id
```

---

# 28. Testing Requirements

The module should be tested using the project's own synthetic/sample cheque dataset.

Test categories should include:

```text
1. Clear cheque
2. Blurred cheque
3. Rotated cheque
4. Low-contrast cheque
5. Noisy cheque
6. Dark image
7. Bright image
8. Low-resolution image
9. Cropped cheque
10. PDF cheque
```

For every test image, the system should record:

```text
Input quality
Preprocessing operations
Processing time
OCR result
OCR confidence
Final quality status
```

This allows us to determine whether preprocessing actually improves OCR performance.

---

# 29. Example Processing Scenario

### Input

A user uploads:

```text
sample_blurred_cheque.jpg
```

The system performs:

```text
1. Load image
       ↓
2. Check dimensions
       ↓
3. Detect blur
       ↓
4. Convert to grayscale
       ↓
5. Reduce noise
       ↓
6. Enhance contrast
       ↓
7. Correct skew
       ↓
8. Generate processed image
       ↓
9. Send to OCR
```

Output:

```json
{
  "cheque_id": "CHK-2026-000015",
  "preprocessing_status": "COMPLETED",
  "quality_status": "ACCEPTABLE",
  "status": "READY_FOR_OCR"
}
```

---

# 30. Module Boundary

The Image Preprocessing Module is responsible for:

```text
✓ Image normalization
✓ Image enhancement
✓ Noise reduction
✓ Contrast improvement
✓ Deskewing
✓ Orientation correction
✓ Basic quality assessment
✓ OCR image preparation
✓ Preprocessing metadata
```

It is **not responsible for**:

```text
✗ OCR text extraction
✗ Account validation
✗ Payee validation
✗ Duplicate detection
✗ Fraud scoring
✗ Final decision
✗ Cheque approval/rejection
```

Those operations belong to later modules.

---

# 31. Relationship With Other Modules

```text
┌───────────────────────────┐
│ 12 Cheque Input Module    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 13 Image Preprocessing    │
│                           │
│ Normalize                 │
│ Grayscale                 │
│ Denoise                   │
│ Enhance                   │
│ Deskew                    │
│ Quality Check             │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 14 OCR Engine             │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 15 Cheque Data Extraction │
└───────────────────────────┘
```

---

# 32. Expected Output

The final output of this module is an **OCR-ready cheque image plus preprocessing metadata**.

```json
{
  "cheque_id": "CHK-2026-000001",
  "processed_image": "processed/CHK-2026-000001.png",
  "quality_status": "ACCEPTABLE",
  "preprocessing_status": "COMPLETED",
  "status": "READY_FOR_OCR"
}
```

This output becomes the input to:

```text
14_OCR_Engine.md
```

The key design principle is that **preprocessing improves OCR without destroying information required for fraud detection, signature analysis, or later manual review**.
