"""
OCR text extraction using Tesseract.
Handles multiple image formats and returns extracted text with confidence.
"""

import logging
import io
import os
from typing import Union, Tuple, Dict, Any

import numpy as np
from PIL import Image

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes, convert_from_path
    _PDF2IMAGE_AVAILABLE = True
except ImportError:
    _PDF2IMAGE_AVAILABLE = False
    convert_from_bytes = None
    convert_from_path = None

from backend.config import settings
from backend.ocr.preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)

# Set Tesseract command path (only if pytesseract is available)
if _TESSERACT_AVAILABLE and os.path.exists(settings.TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class OCRExtractor:
    """Extract text from images using Tesseract OCR."""

    # Tesseract config for different document types
    CONFIGS = {
        "pan_card": "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/.- ",
        "salary_slip": "--oem 3 --psm 6",
        "general": "--oem 3 --psm 6",
        "single_line": "--oem 3 --psm 7",
        "number": "--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.",
    }

    @staticmethod
    def extract_from_image(
        image_input: Union[str, bytes, np.ndarray],
        doc_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract text from image with confidence scores.

        Args:
            image_input: File path, bytes, or numpy array
            doc_type: "pan_card", "salary_slip", or "general"

        Returns:
            Dict with extracted text, confidence, and word-level details
        """
        try:
            # Preprocess based on document type
            if doc_type == "pan_card":
                processed = ImagePreprocessor.preprocess_pan_card(image_input)
            elif doc_type == "salary_slip":
                processed = ImagePreprocessor.preprocess_salary_slip(image_input)
            else:
                processed = ImagePreprocessor.preprocess(image_input)

            # Convert to PIL Image for Tesseract
            pil_image = Image.fromarray(processed)

            # Get config
            config = OCRExtractor.CONFIGS.get(doc_type, OCRExtractor.CONFIGS["general"])

            # Extract text
            raw_text = pytesseract.image_to_string(pil_image, lang=settings.OCR_LANG, config=config)

            # Get detailed data with confidence scores
            ocr_data = pytesseract.image_to_data(
                pil_image,
                lang=settings.OCR_LANG,
                config=config,
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence
            confidences = [int(c) for c in ocr_data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Get word-level data
            words = []
            for i, word in enumerate(ocr_data['text']):
                if word.strip() and int(ocr_data['conf'][i]) > 30:
                    words.append({
                        "text": word.strip(),
                        "confidence": int(ocr_data['conf'][i]),
                        "x": ocr_data['left'][i],
                        "y": ocr_data['top'][i],
                        "width": ocr_data['width'][i],
                        "height": ocr_data['height'][i],
                    })

            return {
                "success": True,
                "raw_text": raw_text.strip(),
                "avg_confidence": round(avg_confidence, 2),
                "words": words,
                "word_count": len(words),
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "raw_text": "",
                "avg_confidence": 0.0,
                "words": [],
                "word_count": 0,
                "error": str(e),
            }

    @staticmethod
    def extract_from_pdf(
        pdf_input: Union[str, bytes],
        doc_type: str = "salary_slip"
    ) -> Dict[str, Any]:
        """
        Extract text from PDF file.

        Args:
            pdf_input: File path or bytes
            doc_type: Document type for OCR config

        Returns:
            Dict with extracted text from all pages
        """
        try:
            # Convert PDF to images
            if isinstance(pdf_input, bytes):
                pages = convert_from_bytes(pdf_input, dpi=300)
            else:
                pages = convert_from_path(pdf_input, dpi=300)

            all_text = []
            total_confidence = 0.0
            page_count = 0

            for page_num, page_image in enumerate(pages):
                # Convert PIL to numpy
                img_array = np.array(page_image)

                # Extract text from page
                result = OCRExtractor.extract_from_image(img_array, doc_type)

                if result["success"]:
                    all_text.append(f"--- Page {page_num + 1} ---\n{result['raw_text']}")
                    total_confidence += result["avg_confidence"]
                    page_count += 1

            avg_confidence = total_confidence / page_count if page_count > 0 else 0.0

            return {
                "success": True,
                "raw_text": "\n".join(all_text),
                "avg_confidence": round(avg_confidence, 2),
                "page_count": page_count,
            }

        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {e}")
            return {
                "success": False,
                "raw_text": "",
                "avg_confidence": 0.0,
                "page_count": 0,
                "error": str(e),
            }

    @staticmethod
    def extract_auto(
        file_input: Union[str, bytes],
        filename: str,
        doc_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Auto-detect file type and extract text.

        Args:
            file_input: File path or bytes
            filename: Original filename (used to detect type)
            doc_type: Document type hint

        Returns:
            Extraction result dict
        """
        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            return OCRExtractor.extract_from_pdf(file_input, doc_type)
        elif ext in ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp"]:
            return OCRExtractor.extract_from_image(file_input, doc_type)
        else:
            raise ValueError(f"Unsupported file format: {ext}")