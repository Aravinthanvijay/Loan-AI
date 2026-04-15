"""Validate input data quality before ML inference."""

from typing import Dict, Any, List, Tuple
import numpy as np


class DataValidator:
    """Validate feature data before passing to ML model."""

    VALID_RANGES = {
        "age": (18, 80),
        "annual_income": (60000, 100000000),
        "loan_amount": (10000, 50000000),
        "foir": (0.0, 1.0),
        "loan_percent_income": (0.0, 10.0),
        "years_employed": (0.0, 50.0),
    }

    @staticmethod
    def validate(features: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate feature values are within expected ranges."""
        warnings = []
        for field, (min_val, max_val) in DataValidator.VALID_RANGES.items():
            val = features.get(field)
            if val is not None:
                if val < min_val or val > max_val:
                    warnings.append(f"{field}={val} outside expected range [{min_val}, {max_val}]")
        return len(warnings) == 0, warnings