"""MCP tools for Agent 4 Rules Engine."""

from typing import Dict, Any, List, Tuple
from backend.config import settings


def check_age_rule(age: int) -> Dict[str, Any]:
    """Check if applicant age is within allowed range."""
    passed = settings.MIN_AGE <= age <= settings.MAX_AGE
    return {
        "rule": "age_check",
        "passed": passed,
        "hard_rule": True,
        "details": {
            "applicant_age": age,
            "min_age": settings.MIN_AGE,
            "max_age": settings.MAX_AGE,
        },
        "reason": None if passed else f"Age {age} outside allowed range {settings.MIN_AGE}-{settings.MAX_AGE}",
    }


def check_income_rule(monthly_income: float) -> Dict[str, Any]:
    """Check if applicant meets minimum income requirement."""
    passed = monthly_income >= settings.MIN_INCOME
    return {
        "rule": "income_check",
        "passed": passed,
        "hard_rule": True,
        "details": {
            "monthly_income": monthly_income,
            "min_income": settings.MIN_INCOME,
        },
        "reason": None if passed else f"Monthly income Rs {monthly_income:,.0f} below minimum Rs {settings.MIN_INCOME:,.0f}",
    }


def check_foir_rule(monthly_income: float, existing_emi: float, proposed_emi: float = 0) -> Dict[str, Any]:
    """Check Fixed Obligation to Income Ratio (FOIR)."""
    if monthly_income <= 0:
        return {
            "rule": "foir_check",
            "passed": False,
            "hard_rule": True,
            "details": {"foir": 1.0, "max_foir": settings.MAX_FOIR},
            "reason": "Monthly income is zero or negative",
        }

    total_obligations = existing_emi + proposed_emi
    foir = total_obligations / monthly_income
    passed = foir <= settings.MAX_FOIR

    return {
        "rule": "foir_check",
        "passed": passed,
        "hard_rule": True,
        "details": {
            "foir": round(foir, 4),
            "existing_emi": existing_emi,
            "proposed_emi": proposed_emi,
            "monthly_income": monthly_income,
            "max_foir": settings.MAX_FOIR,
        },
        "reason": None if passed else f"FOIR {foir:.1%} exceeds maximum {settings.MAX_FOIR:.0%}",
    }


def check_loan_amount_rule(loan_amount: float) -> Dict[str, Any]:
    """Check if loan amount is within maximum allowed."""
    passed = loan_amount <= settings.MAX_LOAN_AMOUNT
    return {
        "rule": "loan_amount_check",
        "passed": passed,
        "hard_rule": True,
        "details": {
            "loan_amount": loan_amount,
            "max_loan_amount": settings.MAX_LOAN_AMOUNT,
        },
        "reason": None if passed else f"Loan amount Rs {loan_amount:,.0f} exceeds maximum Rs {settings.MAX_LOAN_AMOUNT:,.0f}",
    }


def check_bureau_score_rule(bureau_score: int) -> Dict[str, Any]:
    """Check if bureau/CIBIL score meets minimum requirement."""
    passed = bureau_score >= settings.MIN_BUREAU_SCORE
    return {
        "rule": "bureau_score_check",
        "passed": passed,
        "hard_rule": True,
        "details": {
            "bureau_score": bureau_score,
            "min_bureau_score": settings.MIN_BUREAU_SCORE,
        },
        "reason": None if passed else f"Bureau score {bureau_score} below minimum {settings.MIN_BUREAU_SCORE}",
    }


def run_all_rules(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run all business rules and return aggregated results."""
    age = int(application_data.get("age", 0))
    monthly_income = float(application_data.get("monthly_income", 0))
    existing_emi = float(application_data.get("existing_emi", 0))
    loan_amount = float(application_data.get("loan_amount", 0))
    bureau_score = int(application_data.get("bureau_score", 0))

    rules = [
        check_age_rule(age),
        check_income_rule(monthly_income),
        check_foir_rule(monthly_income, existing_emi),
        check_loan_amount_rule(loan_amount),
        check_bureau_score_rule(bureau_score),
    ]

    passed = [r for r in rules if r["passed"]]
    failed = [r for r in rules if not r["passed"]]
    hard_failures = [r["rule"] for r in failed if r.get("hard_rule")]

    return {
        "all_rules": rules,
        "rules_passed": [r["rule"] for r in passed],
        "rules_failed": [r["rule"] for r in failed],
        "hard_rule_failures": hard_failures,
        "total_passed": len(passed),
        "total_failed": len(failed),
        "overall_pass": len(hard_failures) == 0,
    }