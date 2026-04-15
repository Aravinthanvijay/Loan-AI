"""
Agent 4: Business Rules Engine
Applies hard business rules for loan eligibility.
These are non-negotiable criteria (age, income, FOIR, bureau score).
"""

import logging
from typing import Dict, Any, List, Tuple

from backend.agents.base_agent import BaseAgent
from backend.config import settings


class RulesAgent(BaseAgent):
    """
    Agent 4 responsibilities:
    1. Age eligibility check (21-65 years)
    2. Minimum income check (Rs 15,000/month)
    3. FOIR check (max 50% fixed obligation ratio)
    4. Loan-to-value ratio check
    5. Employment stability check
    6. Bureau score check (if available from credit data)
    """

    def __init__(self):
        super().__init__("RulesAgent", 4)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all business rules and return pass/fail for each."""

        application_data = state.get("application_data", {})
        agent3_result = state.get("agent3_result", {})

        rules_passed = []
        rules_failed = []
        rule_details = {}

        # Extract data
        age = int(application_data.get("age", 0))
        income = float(application_data.get("monthly_income", 0))
        loan_amount = float(application_data.get("loan_amount", 0))
        existing_emi = float(application_data.get("existing_emi", 0))
        existing_loans = int(application_data.get("existing_loans", 0))
        employment_type = application_data.get("employment_type", "")
        years_employed = float(application_data.get("years_employed", 0) or 0)
        credit_score = agent3_result.get("credit_score", 0)
        default_probability = agent3_result.get("default_probability", 1.0)

        # ── Rule 1: Age Check ────────────────────────────────────────────
        rule1_pass = settings.MIN_AGE <= age <= settings.MAX_AGE
        rule_details["age_check"] = {
            "passed": rule1_pass,
            "value": age,
            "requirement": f"{settings.MIN_AGE}-{settings.MAX_AGE} years",
            "message": "Age within eligible range" if rule1_pass else f"Age {age} outside range {settings.MIN_AGE}-{settings.MAX_AGE}",
        }
        (rules_passed if rule1_pass else rules_failed).append("age_check")

        # ── Rule 2: Minimum Income ───────────────────────────────────────
        rule2_pass = income >= settings.MIN_INCOME
        rule_details["minimum_income"] = {
            "passed": rule2_pass,
            "value": income,
            "requirement": f"Rs {settings.MIN_INCOME:,.0f}/month",
            "message": f"Income Rs {income:,.0f} meets minimum" if rule2_pass else f"Income Rs {income:,.0f} below minimum Rs {settings.MIN_INCOME:,.0f}",
        }
        (rules_passed if rule2_pass else rules_failed).append("minimum_income")

        # ── Rule 3: FOIR Check ───────────────────────────────────────────
        # Projected EMI = loan_amount / (tenure_months) approximately
        estimated_new_emi = (loan_amount * 0.01)  # Rough estimate at ~1% per month
        total_emi = existing_emi + estimated_new_emi
        foir = (total_emi / income) if income > 0 else 1.0
        rule3_pass = foir <= settings.MAX_FOIR
        rule_details["foir_check"] = {
            "passed": rule3_pass,
            "value": round(foir, 4),
            "requirement": f"Max {settings.MAX_FOIR:.0%}",
            "message": f"FOIR {foir:.1%} within limit" if rule3_pass else f"FOIR {foir:.1%} exceeds max {settings.MAX_FOIR:.0%}",
            "existing_emi": existing_emi,
            "estimated_new_emi": round(estimated_new_emi, 2),
            "total_emi": round(total_emi, 2),
        }
        (rules_passed if rule3_pass else rules_failed).append("foir_check")

        # ── Rule 4: Maximum Loan Amount ──────────────────────────────────
        rule4_pass = loan_amount <= settings.MAX_LOAN_AMOUNT
        rule_details["max_loan_amount"] = {
            "passed": rule4_pass,
            "value": loan_amount,
            "requirement": f"Max Rs {settings.MAX_LOAN_AMOUNT:,.0f}",
            "message": f"Loan amount within limit" if rule4_pass else f"Loan amount Rs {loan_amount:,.0f} exceeds max",
        }
        (rules_passed if rule4_pass else rules_failed).append("max_loan_amount")

        # ── Rule 5: Credit Score (from Agent 3) ──────────────────────────
        rule5_pass = credit_score >= settings.MIN_BUREAU_SCORE
        rule_details["bureau_score"] = {
            "passed": rule5_pass,
            "value": credit_score,
            "requirement": f"Min score {settings.MIN_BUREAU_SCORE}",
            "message": f"Credit score {credit_score} acceptable" if rule5_pass else f"Credit score {credit_score} below minimum {settings.MIN_BUREAU_SCORE}",
        }
        (rules_passed if rule5_pass else rules_failed).append("bureau_score")

        # ── Rule 6: Loan-to-Income Ratio ─────────────────────────────────
        # Loan should not exceed 60x monthly income (5 years of full salary)
        max_eligible_loan = income * 60
        rule6_pass = loan_amount <= max_eligible_loan
        rule_details["loan_to_income"] = {
            "passed": rule6_pass,
            "value": round(loan_amount / (income * 12), 2) if income > 0 else 99,
            "requirement": "Max 5x annual income",
            "message": f"Loan-to-income ratio acceptable" if rule6_pass else f"Loan amount exceeds 5x annual income",
        }
        (rules_passed if rule6_pass else rules_failed).append("loan_to_income")

        # ── Rule 7: Employment Stability ─────────────────────────────────
        if employment_type == "salaried":
            rule7_pass = years_employed >= 1.0
            rule_details["employment_stability"] = {
                "passed": rule7_pass,
                "value": years_employed,
                "requirement": "Min 1 year employment",
                "message": f"{years_employed:.1f} years employed" + ("" if rule7_pass else " — below minimum 1 year"),
            }
        else:
            rule7_pass = years_employed >= 2.0
            rule_details["employment_stability"] = {
                "passed": rule7_pass,
                "value": years_employed,
                "requirement": "Min 2 years for self-employed",
                "message": f"{years_employed:.1f} years in business" + ("" if rule7_pass else " — below minimum 2 years"),
            }
        (rules_passed if rule7_pass else rules_failed).append("employment_stability")

        # ── Rule 8: Existing Loan Count ──────────────────────────────────
        rule8_pass = existing_loans <= 3
        rule_details["existing_loans"] = {
            "passed": rule8_pass,
            "value": existing_loans,
            "requirement": "Max 3 existing loans",
            "message": f"{existing_loans} existing loans" + ("" if rule8_pass else " — exceeds maximum 3"),
        }
        (rules_passed if rule8_pass else rules_failed).append("existing_loans")

        # ── Summary ──────────────────────────────────────────────────────
        # Application passes if no HARD rules failed
        # Hard rules: age, income, bureau_score, foir
        hard_rules = {"age_check", "minimum_income", "bureau_score", "foir_check"}
        hard_failures = [r for r in rules_failed if r in hard_rules]
        passed = len(hard_failures) == 0

        return {
            "status": "pass" if passed else "fail",
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "hard_rule_failures": hard_failures,
            "soft_rule_failures": [r for r in rules_failed if r not in hard_rules],
            "rule_details": rule_details,
            "rules_summary": {
                "total": len(rule_details),
                "passed": len(rules_passed),
                "failed": len(rules_failed),
            },
            "passed": passed,
        }