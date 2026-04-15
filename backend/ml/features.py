"""
Feature extraction for ML model.
Converts raw application data into model-ready feature vector.
"""

from typing import Dict, Any, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Must match the order used during model training
FEATURE_NAMES = [
    "age",
    "annual_income",
    "loan_amount",
    "loan_percent_income",
    "existing_loans",
    "existing_emi",
    "foir",
    "loan_to_income",
    "employment_type_encoded",
    "years_employed",
    "loan_purpose_encoded",
]

LOAN_PURPOSE_MAP = {
    "home": 0, "personal": 1, "business": 2, "education": 3,
    "vehicle": 4, "medical": 5, "marriage": 6, "travel": 7, "other": 8
}

EMPLOYMENT_MAP = {"salaried": 0, "self_employed": 1}


class FeatureExtractor:
    """Extract features from application data for ML model."""

    @staticmethod
    def extract(
        app_data: Dict[str, Any],
        salary_extracted: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        Extract feature vector from application + OCR data.

        Args:
            app_data: Raw application form data
            salary_extracted: OCR-extracted salary data (from Agent 2)

        Returns:
            Dict mapping feature_name → value
        """
        if salary_extracted is None:
            salary_extracted = {}

        age = float(app_data.get("age", 30))
        monthly_income = float(app_data.get("monthly_income", 0))
        annual_income = monthly_income * 12

        loan_amount = float(app_data.get("loan_amount", 0))
        existing_emi = float(app_data.get("existing_emi", 0))
        existing_loans = int(app_data.get("existing_loans", 0))
        years_employed = float(app_data.get("years_employed", 0) or 0)

        # Use OCR-verified salary if available (more reliable)
        ocr_gross = salary_extracted.get("gross_salary")
        ocr_net = salary_extracted.get("net_salary")
        if ocr_gross and ocr_gross > 0:
            verified_income = ocr_gross * 12
        elif ocr_net and ocr_net > 0:
            verified_income = ocr_net * 12
        else:
            verified_income = annual_income

        # Derived features
        foir = existing_emi / monthly_income if monthly_income > 0 else 0
        loan_percent_income = loan_amount / verified_income if verified_income > 0 else 0
        loan_to_income = loan_amount / (monthly_income * 12) if monthly_income > 0 else 0

        emp_encoded = EMPLOYMENT_MAP.get(app_data.get("employment_type", "salaried"), 0)
        purpose_encoded = LOAN_PURPOSE_MAP.get(app_data.get("loan_purpose", "personal"), 1)

        features = {
            "age": age,
            "annual_income": verified_income,
            "loan_amount": loan_amount,
            "loan_percent_income": round(loan_percent_income, 4),
            "existing_loans": existing_loans,
            "existing_emi": existing_emi,
            "foir": round(foir, 4),
            "loan_to_income": round(loan_to_income, 4),
            "employment_type_encoded": emp_encoded,
            "years_employed": years_employed,
            "loan_purpose_encoded": purpose_encoded,
        }

        logger.debug(f"Extracted features: {features}")
        return features

    @staticmethod
    def to_array(features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array in correct order."""
        return np.array([features.get(name, 0) for name in FEATURE_NAMES]).reshape(1, -1)