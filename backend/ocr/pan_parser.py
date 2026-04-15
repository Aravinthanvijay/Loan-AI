"""
PAN card specific parser.
Extracts PAN number, name, date of birth, and father's name.
"""

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PANParser:
    """Parse PAN card OCR output to extract structured data."""

    # PAN number pattern: 5 letters + 4 digits + 1 letter
    PAN_PATTERN = r'[A-Z]{5}[0-9]{4}[A-Z]'

    # Date patterns: DD/MM/YYYY or DD-MM-YYYY
    DATE_PATTERN = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'

    # Name pattern (all caps, multiple words)
    NAME_PATTERN = r'\b([A-Z][A-Z\s]{2,40})\b'

    @staticmethod
    def parse(ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse PAN card OCR result.

        Args:
            ocr_result: Result from OCRExtractor.extract_from_image()

        Returns:
            Structured PAN card data
        """
        raw_text = ocr_result.get("raw_text", "")
        confidence = ocr_result.get("avg_confidence", 0.0)

        # Normalize text
        text = PANParser._normalize_text(raw_text)

        # Extract fields
        pan_number = PANParser._extract_pan_number(text)
        dob = PANParser._extract_date_of_birth(text)
        name = PANParser._extract_name(text)
        fathers_name = PANParser._extract_fathers_name(text)

        result = {
            "pan_number": pan_number,
            "name": name,
            "date_of_birth": dob,
            "fathers_name": fathers_name,
            "raw_text": raw_text,
            "ocr_confidence": confidence,
            "extraction_successful": pan_number is not None,
            "fields_extracted": sum([
                pan_number is not None,
                name is not None,
                dob is not None,
                fathers_name is not None,
            ]),
        }

        logger.info(f"PAN parsed: PAN={pan_number}, Name={name}, DOB={dob}")
        return result

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Clean and normalize OCR output text."""
        # Remove special characters except alphanumeric, space, /, -
        text = re.sub(r'[^\w\s/\-.]', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Convert to uppercase
        return text.upper().strip()

    @staticmethod
    def _extract_pan_number(text: str) -> Optional[str]:
        """Extract PAN number using regex."""
        # Fix common OCR errors (O→0, l→1, I→1)
        corrected = text.replace('O', '0').replace('l', '1').replace('I', '1')

        # Search in original first, then corrected
        for t in [text, corrected]:
            matches = re.findall(PANParser.PAN_PATTERN, t)
            if matches:
                # Return the most likely match (longest unique pattern)
                for match in matches:
                    if PANParser._validate_pan(match):
                        return match

        return None

    @staticmethod
    def _extract_date_of_birth(text: str) -> Optional[str]:
        """Extract date of birth from PAN card text."""
        matches = re.findall(PANParser.DATE_PATTERN, text)
        if matches:
            # PAN card DOB is usually the first date found
            dob = matches[0]
            # Normalize format to DD/MM/YYYY
            dob = dob.replace('-', '/')
            return dob
        return None

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """Extract applicant name from PAN card."""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Name line: all caps, 2-4 words, no numbers
            if (re.match(r'^[A-Z][A-Z\s]{4,40}$', line)
                    and not re.search(r'\d', line)
                    and len(line.split()) >= 2
                    and 'INCOME' not in line
                    and 'INDIA' not in line
                    and 'GOVT' not in line
                    and 'TAX' not in line):
                return line.strip()
        return None

    @staticmethod
    def _extract_fathers_name(text: str) -> Optional[str]:
        """Extract father's name from PAN card."""
        lines = text.split('\n')
        found_name = False
        for line in lines:
            line = line.strip()
            # Father's name typically appears after the applicant's name
            if found_name:
                if (re.match(r'^[A-Z][A-Z\s]{4,40}$', line)
                        and not re.search(r'\d', line)
                        and len(line.split()) >= 2
                        and 'INCOME' not in line):
                    return line.strip()
            if PANParser._looks_like_name(line):
                found_name = True
        return None

    @staticmethod
    def _looks_like_name(text: str) -> bool:
        """Check if text looks like a person's name."""
        return (bool(re.match(r'^[A-Z][A-Z\s]{4,40}$', text))
                and not re.search(r'\d', text)
                and len(text.split()) >= 2)

    @staticmethod
    def _validate_pan(pan: str) -> bool:
        """Validate PAN number format."""
        if not pan or len(pan) != 10:
            return False
        pattern = r'^[A-Z]{3}[PCHABGJLFTE][A-Z][0-9]{4}[A-Z]$'
        return bool(re.match(pattern, pan))