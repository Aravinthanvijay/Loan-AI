"""
Input validators for form data.
Validates PAN, phone, email, Aadhaar, and loan amounts.
"""

import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Validators for all user input fields."""

    @staticmethod
    def validate_pan(pan: str) -> Tuple[bool, Optional[str]]:
        """Validate PAN number format."""
        if not pan:
            return False, "PAN number is required"
        pan = pan.upper().strip()
        if len(pan) != 10:
            return False, f"PAN must be 10 characters, got {len(pan)}"
        pattern = r'^[A-Z]{3}[PCHABGJLFTE][A-Z][0-9]{4}[A-Z]$'
        if not re.match(pattern, pan):
            return False, "Invalid PAN format (e.g., ABCDE1234F)"
        return True, None

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate Indian mobile number."""
        if not phone:
            return False, "Phone number is required"
        phone = re.sub(r'[\s\-+]', '', phone)
        if phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        pattern = r'^[6-9]\d{9}$'
        if not re.match(pattern, phone):
            return False, "Invalid Indian mobile number (must start with 6-9, 10 digits)"
        return True, None

    @staticmethod
    def validate_aadhaar(aadhaar: str) -> Tuple[bool, Optional[str]]:
        """Validate Aadhaar number (12 digits)."""
        if not aadhaar:
            return False, "Aadhaar is required"
        aadhaar = re.sub(r'\s', '', aadhaar)
        if not re.match(r'^\d{12}$', aadhaar):
            return False, "Aadhaar must be exactly 12 digits"
        if aadhaar[0] in '01':
            return False, "Invalid Aadhaar number"
        return True, None

    @staticmethod
    def validate_age(age: int) -> Tuple[bool, Optional[str]]:
        """Validate age for loan eligibility."""
        if age < 21:
            return False, f"Minimum age for loan is 21 years (provided: {age})"
        if age > 65:
            return False, f"Maximum age for loan is 65 years (provided: {age})"
        return True, None

    @staticmethod
    def validate_income(income: float) -> Tuple[bool, Optional[str]]:
        """Validate minimum income."""
        if income < 15000:
            return False, f"Minimum monthly income is Rs 15,000 (provided: Rs {income:,.0f})"
        if income > 10000000:
            return False, "Income amount seems unrealistic"
        return True, None

    @staticmethod
    def validate_loan_amount(amount: float, monthly_income: float) -> Tuple[bool, Optional[str]]:
        """Validate loan amount against income."""
        if amount < 10000:
            return False, "Minimum loan amount is Rs 10,000"
        if amount > 5000000:
            return False, "Maximum loan amount is Rs 50,00,000"
        max_loan = monthly_income * 60  # 5 years x 12 months
        if amount > max_loan:
            return False, f"Loan amount exceeds maximum eligible amount of Rs {max_loan:,.0f}"
        return True, None

    @staticmethod
    def validate_foir(emi: float, income: float) -> Tuple[bool, Optional[str]]:
        """Validate FOIR (Fixed Obligation to Income Ratio)."""
        if income <= 0:
            return False, "Invalid income"
        foir = emi / income
        if foir > 0.5:
            return False, f"FOIR {foir:.1%} exceeds maximum allowed 50%"
        return True, None

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input — remove potentially dangerous chars."""
        return re.sub(r'[<>&"\']', '', text).strip()[:500]