"""
OCR result validation.
Cross-validates extracted OCR data against user-submitted form data.
"""

from typing import Dict, Any, List, Tuple
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OCRValidator:
    """Validate and cross-check OCR extracted data with form data."""

    @staticmethod
    def validate_pan_extraction(
        extracted: Dict[str, Any],
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cross-validate PAN card data against form submission.

        Args:
            extracted: PANParser.parse() result
            form_data: User submitted form data (name, pan_number, dob)

        Returns:
            Validation result with match scores
        """
        issues = []
        matches = {}

        # Validate PAN number
        extracted_pan = extracted.get("pan_number")
        form_pan = form_data.get("pan_number", "").upper()

        if extracted_pan:
            pan_match = extracted_pan.upper() == form_pan
            matches["pan_number"] = pan_match
            if not pan_match:
                issues.append(f"PAN mismatch: OCR={extracted_pan}, Form={form_pan}")
        else:
            matches["pan_number"] = False
            issues.append("Could not extract PAN number from document")

        # Validate name (fuzzy match)
        extracted_name = extracted.get("name")
        form_name = form_data.get("full_name", "").upper()

        if extracted_name and form_name:
            name_similarity = OCRValidator._name_similarity(extracted_name, form_name)
            matches["name"] = name_similarity > 0.7
            if name_similarity <= 0.7:
                issues.append(f"Name mismatch: OCR={extracted_name}, Form={form_name} (similarity={name_similarity:.2f})")
        else:
            matches["name"] = False
            if not extracted_name:
                issues.append("Could not extract name from PAN card")

        # Validate DOB if provided
        extracted_dob = extracted.get("date_of_birth")
        form_dob = form_data.get("date_of_birth")

        if extracted_dob and form_dob:
            dob_match = OCRValidator._normalize_date(extracted_dob) == OCRValidator._normalize_date(str(form_dob))
            matches["date_of_birth"] = dob_match
            if not dob_match:
                issues.append(f"DOB mismatch: OCR={extracted_dob}, Form={form_dob}")
        else:
            matches["date_of_birth"] = None  # Not validated

        return {
            "is_valid": len(issues) == 0,
            "matches": matches,
            "issues": issues,
            "ocr_confidence": extracted.get("ocr_confidence", 0),
        }

    @staticmethod
    def validate_salary_extraction(
        extracted: Dict[str, Any],
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cross-validate salary slip data against form submission.

        Args:
            extracted: SalaryParser.parse() result
            form_data: User submitted form data (monthly_income, employer_name)

        Returns:
            Validation result
        """
        issues = []
        matches = {}

        # Validate salary amount (within 20% tolerance)
        extracted_gross = extracted.get("gross_salary")
        extracted_net = extracted.get("net_salary")
        form_income = float(form_data.get("monthly_income", 0))

        if extracted_gross or extracted_net:
            best_salary = extracted_net or extracted_gross
            if form_income > 0 and best_salary:
                tolerance = 0.20
                lower = form_income * (1 - tolerance)
                upper = form_income * (1 + tolerance)
                salary_match = lower <= best_salary <= upper
                matches["monthly_income"] = salary_match
                if not salary_match:
                    issues.append(
                        f"Income mismatch: OCR={best_salary:.0f}, Form={form_income:.0f} "
                        f"(tolerance=±20%)"
                    )
        else:
            matches["monthly_income"] = False
            issues.append("Could not extract salary from document")

        # Validate employer name (fuzzy)
        extracted_employer = extracted.get("employer_name")
        form_employer = form_data.get("employer_name", "")

        if extracted_employer and form_employer:
            emp_similarity = OCRValidator._name_similarity(
                extracted_employer.upper(),
                form_employer.upper()
            )
            matches["employer_name"] = emp_similarity > 0.5
        else:
            matches["employer_name"] = None

        # Cross-check PAN from salary slip
        salary_pan = extracted.get("pan_number")
        form_pan = form_data.get("pan_number", "").upper()

        if salary_pan and form_pan:
            matches["pan_number"] = salary_pan.upper() == form_pan
            if not matches["pan_number"]:
                issues.append(f"PAN in salary slip ({salary_pan}) doesn't match form ({form_pan})")

        return {
            "is_valid": len(issues) == 0,
            "matches": matches,
            "issues": issues,
            "ocr_confidence": extracted.get("ocr_confidence", 0),
        }

    @staticmethod
    def _name_similarity(name1: str, name2: str) -> float:
        """Calculate similarity between two names using token overlap."""
        tokens1 = set(name1.upper().split())
        tokens2 = set(name2.upper().split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Normalize date to DD/MM/YYYY format."""
        date_str = date_str.replace('-', '/')
        parts = date_str.split('/')
        if len(parts) == 3:
            return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
        return date_str