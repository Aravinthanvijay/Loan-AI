"""
Salary slip specific parser.
Extracts employer name, gross salary, net salary, employee name, and month.
"""

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SalaryParser:
    """Parse salary slip OCR output to extract structured data."""

    # Amount pattern — matches Indian currency amounts
    AMOUNT_PATTERN = r'(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)'

    # Month pattern
    MONTH_PATTERN = r'\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b'

    @staticmethod
    def parse(ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse salary slip OCR result.

        Args:
            ocr_result: Result from OCRExtractor

        Returns:
            Structured salary data
        """
        raw_text = ocr_result.get("raw_text", "")
        confidence = ocr_result.get("avg_confidence", 0.0)

        text = SalaryParser._normalize_text(raw_text)

        # Extract fields
        employer_name = SalaryParser._extract_employer(text)
        employee_name = SalaryParser._extract_employee_name(text)
        gross_salary = SalaryParser._extract_gross_salary(text)
        net_salary = SalaryParser._extract_net_salary(text)
        basic_salary = SalaryParser._extract_basic_salary(text)
        salary_month = SalaryParser._extract_month(text)
        pan_number = SalaryParser._extract_pan(text)
        pf_number = SalaryParser._extract_pf(text)

        result = {
            "employer_name": employer_name,
            "employee_name": employee_name,
            "gross_salary": gross_salary,
            "net_salary": net_salary,
            "basic_salary": basic_salary,
            "salary_month": salary_month,
            "pan_number": pan_number,
            "pf_number": pf_number,
            "raw_text": raw_text,
            "ocr_confidence": confidence,
            "extraction_successful": gross_salary is not None or net_salary is not None,
            "fields_extracted": sum([
                employer_name is not None,
                employee_name is not None,
                gross_salary is not None,
                net_salary is not None,
                basic_salary is not None,
            ]),
        }

        logger.info(f"Salary parsed: Employer={employer_name}, Gross={gross_salary}, Net={net_salary}")
        return result

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize OCR text."""
        text = re.sub(r'\s+', ' ', text)
        return text.upper().strip()

    @staticmethod
    def _extract_amount(text: str) -> Optional[float]:
        """Extract numeric amount from text."""
        # Remove commas from numbers
        matches = re.findall(r'[\d,]+(?:\.\d{2})?', text)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 1000 <= amount <= 10000000:  # Valid salary range
                    return amount
            except ValueError:
                continue
        return None

    @staticmethod
    def _extract_employer(text: str) -> Optional[str]:
        """Extract employer/company name."""
        # Look for company name indicators
        patterns = [
            r'(?:COMPANY|EMPLOYER|ORGANIZATION|ORG|LTD|LIMITED|PVT|PRIVATE|INC|CORP|TECHNOLOGIES|SERVICES|SOLUTIONS)\s*:?\s*([A-Z][A-Z\s&.,]+)',
            r'^([A-Z][A-Z\s&.,]{5,50}(?:LTD|LIMITED|PVT|INC|CORP|TECHNOLOGIES|SERVICES))',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()[:100]
        return None

    @staticmethod
    def _extract_employee_name(text: str) -> Optional[str]:
        """Extract employee name from salary slip."""
        patterns = [
            r'(?:EMPLOYEE\s*NAME|NAME\s*OF\s*EMPLOYEE|EMP\s*NAME)\s*:?\s*([A-Z][A-Z\s]{4,40})',
            r'(?:NAME)\s*:?\s*([A-Z][A-Z\s]{4,40})',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                name = matches[0].strip()
                # Filter out common non-name matches
                if not any(word in name for word in ['SALARY', 'SLIP', 'MONTH', 'YEAR']):
                    return name
        return None

    @staticmethod
    def _extract_gross_salary(text: str) -> Optional[float]:
        """Extract gross salary."""
        patterns = [
            r'GROSS\s*(?:SALARY|PAY|EARNINGS|CTCO?)\s*:?\s*([\d,]+(?:\.\d{2})?)',
            r'TOTAL\s*GROSS\s*:?\s*([\d,]+(?:\.\d{2})?)',
            r'GROSS\s*:?\s*([\d,]+(?:\.\d{2})?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 5000 <= amount <= 10000000:
                        return amount
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_net_salary(text: str) -> Optional[float]:
        """Extract net take-home salary."""
        patterns = [
            r'NET\s*(?:SALARY|PAY|TAKE\s*HOME|PAYABLE)\s*:?\s*([\d,]+(?:\.\d{2})?)',
            r'TAKE\s*HOME\s*:?\s*([\d,]+(?:\.\d{2})?)',
            r'NET\s*:?\s*([\d,]+(?:\.\d{2})?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 5000 <= amount <= 10000000:
                        return amount
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_basic_salary(text: str) -> Optional[float]:
        """Extract basic salary."""
        patterns = [
            r'BASIC\s*(?:SALARY|PAY)?\s*:?\s*([\d,]+(?:\.\d{2})?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 2000 <= amount <= 10000000:
                        return amount
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_month(text: str) -> Optional[str]:
        """Extract salary month."""
        matches = re.findall(SalaryParser.MONTH_PATTERN, text)
        if matches:
            return matches[0]

        # Try MM/YYYY or MONTH YEAR pattern
        year_matches = re.findall(r'((?:0?[1-9]|1[0-2])[/-]\d{4})', text)
        if year_matches:
            return year_matches[0]
        return None

    @staticmethod
    def _extract_pan(text: str) -> Optional[str]:
        """Extract PAN number from salary slip."""
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
        matches = re.findall(pan_pattern, text)
        return matches[0] if matches else None

    @staticmethod
    def _extract_pf(text: str) -> Optional[str]:
        """Extract PF/EPF account number."""
        pf_pattern = r'(?:PF|EPF|PROVIDENT\s*FUND)\s*(?:NO|NUMBER|A/C)?\s*:?\s*([A-Z0-9/]{10,25})'
        matches = re.findall(pf_pattern, text)
        return matches[0] if matches else None