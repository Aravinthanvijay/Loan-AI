"""
Agent 2: Document Processing Agent
Runs OCR on PAN card and salary slip, extracts data, validates against form.
"""

import logging
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.ocr.extractor import OCRExtractor
from backend.ocr.pan_parser import PANParser
from backend.ocr.salary_parser import SalaryParser
from backend.ocr.validator import OCRValidator


class DocumentAgent(BaseAgent):
    """
    Agent 2 responsibilities:
    1. Load uploaded PAN card image/PDF
    2. Load uploaded salary slip image/PDF
    3. Run OCR extraction on both documents
    4. Parse structured data from raw OCR text
    5. Cross-validate extracted data vs form-submitted data
    6. Flag mismatches and fraud indicators
    """

    def __init__(self):
        super().__init__("DocumentAgent", 2)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process documents via OCR and validate against form data."""

        application_data = state.get("application_data", {})
        pan_doc = application_data.get("pan_document", {})
        salary_doc = application_data.get("salary_document", {})

        pan_path = pan_doc.get("file_path", "")
        salary_path = salary_doc.get("file_path", "")
        pan_filename = pan_doc.get("filename", "document.jpg")
        salary_filename = salary_doc.get("filename", "document.jpg")

        issues = []

        # ── Step 1: OCR on PAN card ──────────────────────────────────────
        self.logger.info(f"Running OCR on PAN card: {pan_path}")
        pan_ocr_result = {"success": False, "raw_text": "", "avg_confidence": 0}

        try:
            pan_ocr_result = OCRExtractor.extract_auto(
                pan_path, pan_filename, doc_type="pan_card"
            )
        except Exception as e:
            self.logger.error(f"PAN OCR failed: {e}")
            issues.append(f"PAN card OCR failed: {str(e)}")

        # ── Step 2: Parse PAN card data ──────────────────────────────────
        pan_extracted = {}
        if pan_ocr_result.get("success"):
            pan_extracted = PANParser.parse(pan_ocr_result)
        else:
            issues.append("Could not extract text from PAN card image")

        # ── Step 3: OCR on salary slip ───────────────────────────────────
        self.logger.info(f"Running OCR on salary slip: {salary_path}")
        salary_ocr_result = {"success": False, "raw_text": "", "avg_confidence": 0}

        try:
            salary_ocr_result = OCRExtractor.extract_auto(
                salary_path, salary_filename, doc_type="salary_slip"
            )
        except Exception as e:
            self.logger.error(f"Salary OCR failed: {e}")
            issues.append(f"Salary slip OCR failed: {str(e)}")

        # ── Step 4: Parse salary slip data ──────────────────────────────
        salary_extracted = {}
        if salary_ocr_result.get("success"):
            salary_extracted = SalaryParser.parse(salary_ocr_result)
        else:
            issues.append("Could not extract text from salary slip")

        # ── Step 5: Cross-validate PAN card data ─────────────────────────
        pan_validation = {}
        if pan_extracted:
            pan_validation = OCRValidator.validate_pan_extraction(
                pan_extracted,
                {
                    "pan_number": application_data.get("pan_number", ""),
                    "full_name": application_data.get("full_name", ""),
                    "date_of_birth": application_data.get("date_of_birth"),
                }
            )
            if not pan_validation.get("is_valid"):
                for issue in pan_validation.get("issues", []):
                    issues.append(f"PAN validation: {issue}")

        # ── Step 6: Cross-validate salary slip data ──────────────────────
        salary_validation = {}
        if salary_extracted:
            salary_validation = OCRValidator.validate_salary_extraction(
                salary_extracted,
                {
                    "monthly_income": application_data.get("monthly_income", 0),
                    "employer_name": application_data.get("employer_name", ""),
                    "pan_number": application_data.get("pan_number", ""),
                }
            )
            if not salary_validation.get("is_valid"):
                for issue in salary_validation.get("issues", []):
                    issues.append(f"Salary validation: {issue}")

        # ── Step 7: Check OCR confidence ────────────────────────────────
        pan_confidence = pan_ocr_result.get("avg_confidence", 0)
        salary_confidence = salary_ocr_result.get("avg_confidence", 0)
        avg_confidence = (pan_confidence + salary_confidence) / 2

        if pan_confidence < 40:
            issues.append(f"PAN card image quality poor (OCR confidence: {pan_confidence:.0f}%)")
        if salary_confidence < 40:
            issues.append(f"Salary slip image quality poor (OCR confidence: {salary_confidence:.0f}%)")

        # ── Determine pass/fail ──────────────────────────────────────────
        # Allow pass if critical documents extracted successfully
        critical_pass = (
            pan_extracted.get("pan_number") is not None
            and (salary_extracted.get("gross_salary") is not None
                 or salary_extracted.get("net_salary") is not None)
        )

        passed = critical_pass and len([i for i in issues if "mismatch" in i.lower()]) == 0

        return {
            "status": "pass" if passed else "fail",
            "pan_extracted": pan_extracted,
            "salary_extracted": salary_extracted,
            "pan_validation": pan_validation,
            "salary_validation": salary_validation,
            "cross_validation": {
                "pan_valid": pan_validation.get("is_valid", False),
                "salary_valid": salary_validation.get("is_valid", False),
            },
            "ocr_confidence": {
                "pan_card": round(pan_confidence, 2),
                "salary_slip": round(salary_confidence, 2),
                "average": round(avg_confidence, 2),
            },
            "issues": issues,
            "passed": passed,
        }