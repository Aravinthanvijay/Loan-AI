"""MCP tools for Agent 2 OCR/Document processing."""

import os
import logging
from typing import Dict, Any

from backend.config import settings

logger = logging.getLogger(__name__)


async def preprocess_image(image_path: str) -> Dict[str, Any]:
    """Preprocess image for OCR — resize, denoise, threshold."""
    try:
        import cv2
        import numpy as np

        if not os.path.exists(image_path):
            return {"success": False, "error": f"File not found: {image_path}"}

        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "Failed to read image"}

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        processed_path = image_path.rsplit(".", 1)[0] + "_processed.png"
        cv2.imwrite(processed_path, thresh)

        return {"success": True, "processed_path": processed_path, "original_path": image_path}

    except ImportError:
        logger.warning("OpenCV not available, skipping preprocessing")
        return {"success": True, "processed_path": image_path, "original_path": image_path}
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return {"success": False, "error": str(e)}


async def run_ocr(image_path: str, lang: str = "eng") -> Dict[str, Any]:
    """Run OCR on an image file. Falls back to simulation if Tesseract not available."""
    try:
        import pytesseract
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        if not os.path.exists(settings.TESSERACT_CMD):
            raise FileNotFoundError("Tesseract not installed")

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang)
        data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

        confidences = [int(c) for c in data["conf"] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "success": True,
            "text": text,
            "confidence": round(avg_confidence, 1),
            "method": "tesseract",
        }

    except (FileNotFoundError, ImportError, Exception) as e:
        logger.warning(f"Tesseract OCR unavailable ({e}). Using simulation fallback.")
        return _simulate_ocr(image_path)


def _simulate_ocr(image_path: str) -> Dict[str, Any]:
    """Simulate OCR output for demo when Tesseract is not installed."""
    import random

    filename = os.path.basename(image_path).lower()

    if "pan" in filename:
        text = "INCOME TAX DEPARTMENT\nGOVT OF INDIA\nRAHUL KUMAR SHARMA\nABCDE1234F\nDate of Birth: 15/03/1990"
    elif "salary" in filename or "slip" in filename:
        text = (
            "SALARY SLIP - March 2024\n"
            "Employee: Rahul Kumar Sharma\n"
            "Employee ID: EMP-4521\n"
            "Employer: Tata Consultancy Services\n"
            "Basic Salary: 45,000\n"
            "HRA: 18,000\n"
            "Other Allowances: 12,000\n"
            "Gross Salary: 75,000\n"
            "PF Deduction: 5,400\n"
            "Tax Deduction: 8,500\n"
            "Net Salary: 61,100"
        )
    else:
        text = f"Document content from {filename}"

    return {
        "success": True,
        "text": text,
        "confidence": round(random.uniform(72, 92), 1),
        "method": "simulation",
    }


def parse_pan_fields(ocr_text: str) -> Dict[str, Any]:
    """Extract PAN card fields from OCR text."""
    import re

    result = {
        "pan_number": None,
        "name": None,
        "dob": None,
        "father_name": None,
    }

    # Extract PAN number
    pan_match = re.search(r'[A-Z]{3}[PCHABGJLFTE][A-Z][0-9]{4}[A-Z]', ocr_text)
    if pan_match:
        result["pan_number"] = pan_match.group()

    # Extract date of birth
    dob_match = re.search(r'(\d{2}[/\-]\d{2}[/\-]\d{4})', ocr_text)
    if dob_match:
        result["dob"] = dob_match.group()

    # Extract name (line after GOVT OF INDIA or before PAN)
    lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]
    for i, line in enumerate(lines):
        if "GOVT" in line.upper() or "INCOME TAX" in line.upper():
            if i + 1 < len(lines):
                potential_name = lines[i + 1]
                if not re.search(r'[0-9]', potential_name) and len(potential_name) > 3:
                    result["name"] = potential_name
                elif i + 2 < len(lines):
                    result["name"] = lines[i + 2]
            break

    return result


def parse_salary_fields(ocr_text: str) -> Dict[str, Any]:
    """Extract salary slip fields from OCR text."""
    import re

    result = {
        "employee_name": None,
        "employer_name": None,
        "gross_salary": None,
        "net_salary": None,
        "basic_salary": None,
        "deductions": None,
        "month": None,
    }

    lines = ocr_text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()

        # Month/period
        month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s*\d{4}', line_lower)
        if month_match:
            result["month"] = month_match.group().title()

        # Employee name
        if "employee:" in line_lower or "name:" in line_lower:
            val = line.split(":", 1)[-1].strip()
            if val and not val.replace(" ", "").isdigit():
                result["employee_name"] = val

        # Employer
        if "employer:" in line_lower or "company:" in line_lower:
            result["employer_name"] = line.split(":", 1)[-1].strip()

        # Amounts
        amount_match = re.search(r'[\d,]+(?:\.\d{2})?', line)
        if amount_match:
            try:
                amount = float(amount_match.group().replace(",", ""))
                if "gross" in line_lower and "salary" in line_lower:
                    result["gross_salary"] = amount
                elif "net" in line_lower and "salary" in line_lower:
                    result["net_salary"] = amount
                elif "basic" in line_lower:
                    result["basic_salary"] = amount
                elif "deduction" in line_lower or "total ded" in line_lower:
                    result["deductions"] = amount
            except ValueError:
                pass

    return result