"""
Agent 3: Credit Scoring Agent
Uses trained XGBoost model to predict default probability.
Generates SHAP explanations for explainability.
"""

import logging
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.ml.inference import ModelInference
from backend.ml.features import FeatureExtractor
from backend.ml.shap_explain import SHAPExplainer


class CreditAgent(BaseAgent):
    """
    Agent 3 responsibilities:
    1. Extract features from application + OCR data
    2. Run XGBoost model for default probability prediction
    3. Generate credit score (300-900 scale)
    4. Generate SHAP explanations for top factors
    5. Assign risk band: low/medium/high
    """

    RISK_BANDS = {
        "low": (0.0, 0.2),
        "medium": (0.2, 0.5),
        "high": (0.5, 1.0),
    }

    def __init__(self):
        super().__init__("CreditAgent", 3)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compute credit score and default probability."""

        application_data = state.get("application_data", {})
        agent2_result = state.get("agent2_result", {})
        salary_extracted = agent2_result.get("salary_extracted", {})

        # ── Step 1: Build feature vector ─────────────────────────────────
        features = FeatureExtractor.extract(application_data, salary_extracted)
        self.logger.info(f"Extracted {len(features)} features for credit scoring")

        # ── Step 2: Run ML model ─────────────────────────────────────────
        try:
            prediction = ModelInference.predict(features)
            default_probability = prediction["default_probability"]
            raw_score = prediction["raw_score"]
        except Exception as e:
            self.logger.warning(f"ML model failed, using rule-based scoring: {e}")
            default_probability = self._rule_based_score(application_data)
            raw_score = default_probability

        # ── Step 3: Convert to credit score (300-900 scale) ──────────────
        # Higher default probability → lower credit score
        credit_score = int(900 - (default_probability * 600))
        credit_score = max(300, min(900, credit_score))

        # ── Step 4: Assign risk band ─────────────────────────────────────
        risk_band = "high"
        for band, (low, high) in self.RISK_BANDS.items():
            if low <= default_probability < high:
                risk_band = band
                break

        # ── Step 5: SHAP explanations ────────────────────────────────────
        shap_values = {}
        top_factors = []
        try:
            shap_result = SHAPExplainer.explain(features)
            shap_values = shap_result.get("shap_values", {})
            top_factors = shap_result.get("top_factors", [])
        except Exception as e:
            self.logger.warning(f"SHAP explanation failed: {e}")
            top_factors = self._generate_rule_factors(application_data, default_probability)

        # ── Determine pass/fail ──────────────────────────────────────────
        # Pass if default probability < 0.5 (below 50% chance of default)
        passed = default_probability < 0.5

        return {
            "status": "pass" if passed else "fail",
            "credit_score": credit_score,
            "default_probability": round(default_probability, 4),
            "risk_band": risk_band,
            "shap_values": shap_values,
            "top_factors": top_factors,
            "features_used": features,
            "model_version": ModelInference.get_model_version(),
            "passed": passed,
        }

    def _rule_based_score(self, app_data: Dict[str, Any]) -> float:
        """Fallback rule-based scoring when ML model is unavailable."""
        score = 0.3  # Base default probability

        income = float(app_data.get("monthly_income", 0))
        loan = float(app_data.get("loan_amount", 0))
        age = int(app_data.get("age", 30))
        existing_loans = int(app_data.get("existing_loans", 0))
        existing_emi = float(app_data.get("existing_emi", 0))

        # Income-to-loan ratio
        if income > 0:
            ratio = loan / (income * 12)
            if ratio > 5:
                score += 0.2
            elif ratio > 3:
                score += 0.1

        # Age factor
        if age < 25 or age > 60:
            score += 0.1

        # Existing debt burden
        if existing_loans > 2:
            score += 0.15
        if income > 0 and existing_emi / income > 0.4:
            score += 0.15

        return min(score, 0.95)

    def _generate_rule_factors(
        self, app_data: Dict[str, Any], probability: float
    ):
        """Generate human-readable factors when SHAP is unavailable."""
        factors = []
        income = float(app_data.get("monthly_income", 0))
        loan = float(app_data.get("loan_amount", 0))
        existing_emi = float(app_data.get("existing_emi", 0))

        if income > 0:
            ratio = loan / (income * 12)
            factors.append({
                "factor": "loan_to_income_ratio",
                "value": round(ratio, 2),
                "impact": "negative" if ratio > 4 else "positive",
                "description": f"Loan amount is {ratio:.1f}x annual income",
            })

        if income > 0 and existing_emi > 0:
            foir = existing_emi / income
            factors.append({
                "factor": "existing_obligations",
                "value": round(foir, 2),
                "impact": "negative" if foir > 0.3 else "positive",
                "description": f"Existing EMIs consume {foir:.0%} of income",
            })

        return factors