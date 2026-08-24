"""PDF -> image conversion (docs/12_Cheque_Input_Module.md S8,
docs/13_Image_Preprocessing.md S6).

Per the documented MVP rule, a PDF is expected to contain one cheque per
processing request; only the first page is rendered and used. The
original PDF bytes are preserved separately and are never modified by
this step.
"""

from __future__ import annotations

import numpy as np
import pymupdf
from PIL import Image

from app.services.cheque.exceptions import InvalidPDFError

# 200 DPI keeps rendered cheque text legible for later OCR milestones
# without producing an unreasonably large working image.
_RENDER_DPI = 200


def render_first_page_to_image(pdf_content: bytes) -> tuple[np.ndarray, int]:
    """Returns (BGR image array, total_page_count)."""
    try:
        doc = pymupdf.open(stream=pdf_content, filetype="pdf")
        if doc.page_count < 1:
            raise InvalidPDFError()
        page = doc.load_page(0)
        zoom = _RENDER_DPI / 72
        matrix = pymupdf.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, colorspace=pymupdf.csRGB)
        page_count = doc.page_count
        doc.close()
    except InvalidPDFError:
        raise
    except Exception as exc:
        raise InvalidPDFError() from exc

    pil_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    rgb_array = np.array(pil_image)
    bgr_array = rgb_array[:, :, ::-1].copy()  # RGB -> BGR for OpenCV
    return bgr_array, page_count
