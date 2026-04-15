"""MCP tools for Agent 5 Policy RAG."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def search_policy_index(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search FAISS policy index for relevant clauses."""
    from backend.rag.retriever import PolicyRetriever
    results = PolicyRetriever.search(query, top_k=top_k)
    return results


def rank_policy_clauses(results: List[Dict], application_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Rank and annotate policy clauses based on application context."""
    ranked = []
    for result in results:
        text = result.get("text", "").lower()
        relevance_boost = 0

        # Boost relevance based on application context
        age = application_data.get("age", 30)
        if age < 25 and "age" in text:
            relevance_boost += 0.1
        if age > 55 and "age" in text:
            relevance_boost += 0.1

        income = float(application_data.get("monthly_income", 0))
        if income < 20000 and "income" in text:
            relevance_boost += 0.1

        foir = float(application_data.get("existing_emi", 0)) / max(income, 1)
        if foir > 0.4 and "foir" in text:
            relevance_boost += 0.15

        entry = result.copy()
        entry["adjusted_score"] = round(entry.get("similarity_score", 0.5) + relevance_boost, 4)
        ranked.append(entry)

    ranked.sort(key=lambda x: x["adjusted_score"], reverse=True)
    return ranked


def check_policy_compliance(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check application against all relevant policy rules."""
    violations = []
    recommendations = []

    age = int(application_data.get("age", 30))
    income = float(application_data.get("monthly_income", 0))
    loan_amount = float(application_data.get("loan_amount", 0))
    existing_emi = float(application_data.get("existing_emi", 0))
    employment_type = application_data.get("employment_type", "salaried")
    years_employed = float(application_data.get("years_employed", 0) or 0)

    # Age policy checks
    if age < 21 or age > 65:
        violations.append(f"Age {age} outside policy range 21-65")
    elif age < 25:
        recommendations.append("Young applicant (< 25): additional income verification recommended")

    # Income policy checks
    min_income = 15000 if employment_type == "salaried" else 20000
    if income < min_income:
        violations.append(f"Income Rs {income:,.0f} below policy minimum Rs {min_income:,.0f} for {employment_type}")

    # FOIR check
    foir = existing_emi / income if income > 0 else 1
    if foir > 0.5:
        violations.append(f"FOIR {foir:.1%} exceeds maximum 50%")
    elif foir > 0.4:
        recommendations.append(f"FOIR {foir:.1%} is elevated — closer scrutiny recommended")

    # Loan-to-income ratio
    annual_income = income * 12
    if annual_income > 0:
        lti = loan_amount / annual_income
        max_lti = 5 if employment_type == "salaried" else 4
        if lti > max_lti:
            violations.append(f"Loan-to-income ratio {lti:.1f}x exceeds {max_lti}x policy limit")
        elif lti > max_lti * 0.8:
            recommendations.append(f"Loan-to-income ratio {lti:.1f}x approaching limit")

    # Employment stability
    if employment_type == "salaried" and years_employed < 0.5:
        recommendations.append("Less than 6 months with current employer — verify stability")
    elif employment_type == "self_employed" and years_employed < 2:
        violations.append(f"Self-employed with only {years_employed:.1f} years — policy requires 2 years minimum")

    return {
        "violations": violations,
        "recommendations": recommendations,
        "compliant": len(violations) == 0,
    }