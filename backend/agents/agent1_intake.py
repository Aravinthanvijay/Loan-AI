"""
Agent 1: Intake Agent
Validates user form data, checks blacklist, detects duplicates.
This is the first gate — bad applications are rejected here early.
"""

import re
import logging
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.db.repositories.blacklist_repo import BlacklistRepository
from backend.db.repositories.application_repo import ApplicationRepository
from backend.utils.validators import InputValidator


class IntakeAgent(BaseAgent):
    """
    Agent 1 responsibilities:
    1. Validate all form fields (PAN, phone, age, income, loan amount)
    2. Check PAN against blacklist database
    3. Check for duplicate applications in last 24 hours
    4. Basic data quality checks
    """

    def __init__(self):
        super().__init__("IntakeAgent", 1)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate intake data and run blacklist/duplicate checks."""

        application_data = state.get("application_data", {})
        validation_errors = []
        warnings = []

        # ── Step 1: Validate PAN number ──────────────────────────────────
        pan = application_data.get("pan_number", "")
        pan_valid, pan_error = InputValidator.validate_pan(pan)
        if not pan_valid:
            validation_errors.append(f"PAN validation: {pan_error}")

        # ── Step 2: Validate phone ──────────────────────────────────────
        phone = application_data.get("phone", "")
        phone_valid, phone_error = InputValidator.validate_phone(phone)
        if not phone_valid:
            validation_errors.append(f"Phone validation: {phone_error}")

        # ── Step 3: Validate age ────────────────────────────────────────
        age = application_data.get("age", 0)
        age_valid, age_error = InputValidator.validate_age(int(age))
        if not age_valid:
            validation_errors.append(f"Age validation: {age_error}")

        # ── Step 4: Validate income ──────────────────────────────────────
        income = float(application_data.get("monthly_income", 0))
        income_valid, income_error = InputValidator.validate_income(income)
        if not income_valid:
            validation_errors.append(f"Income validation: {income_error}")

        # ── Step 5: Validate loan amount ─────────────────────────────────
        loan_amount = float(application_data.get("loan_amount", 0))
        loan_valid, loan_error = InputValidator.validate_loan_amount(loan_amount, income)
        if not loan_valid:
            validation_errors.append(f"Loan amount: {loan_error}")

        # ── Step 6: Validate FOIR ──────────────────────────────────────
        existing_emi = float(application_data.get("existing_emi", 0))
        if income > 0:
            foir_valid, foir_error = InputValidator.validate_foir(existing_emi, income)
            if not foir_valid:
                validation_errors.append(f"FOIR check: {foir_error}")

        # ── Step 7: Blacklist check ──────────────────────────────────────
        blacklisted = False
        blacklist_reason = None
        if pan_valid:
            blacklisted = await BlacklistRepository.is_blacklisted(pan)
            if blacklisted:
                entry = await BlacklistRepository.get_blacklist_entry(pan)
                blacklist_reason = entry.get("reason", "On blacklist") if entry else "On blacklist"
                validation_errors.append(f"Applicant is blacklisted: {blacklist_reason}")

        # ── Step 8: Duplicate application check ─────────────────────────
        is_duplicate = False
        user_id = application_data.get("user_id", "")
        if user_id:
            is_duplicate = await ApplicationRepository.check_duplicate_application(
                user_id, loan_amount, hours=24
            )
            if is_duplicate:
                warnings.append("Duplicate application detected within 24 hours")

        # ── Step 9: Employment validation ───────────────────────────────
        employment_type = application_data.get("employment_type", "")
        if employment_type not in ["salaried", "self_employed"]:
            validation_errors.append(f"Invalid employment type: {employment_type}")

        if employment_type == "salaried":
            employer = application_data.get("employer_name", "")
            if not employer or len(employer.strip()) < 2:
                validation_errors.append("Employer name required for salaried applicants")

        # ── Step 10: Loan purpose validation ────────────────────────────
        valid_purposes = [
            "home", "personal", "business", "education",
            "vehicle", "medical", "marriage", "travel", "other"
        ]
        loan_purpose = application_data.get("loan_purpose", "").lower()
        if loan_purpose not in valid_purposes:
            warnings.append(f"Non-standard loan purpose: {loan_purpose}")

        # ── Compile result ───────────────────────────────────────────────
        passed = len(validation_errors) == 0

        return {
            "status": "pass" if passed else "fail",
            "blacklist_check": not blacklisted,
            "duplicate_check": not is_duplicate,
            "validation_errors": validation_errors,
            "warnings": warnings,
            "validated_data": {
                "pan_number": pan.upper() if pan else "",
                "monthly_income": income,
                "loan_amount": loan_amount,
                "age": age,
                "foir": round(existing_emi / income, 4) if income > 0 else 0,
            },
            "fields_validated": 9,
            "passed": passed,
        }