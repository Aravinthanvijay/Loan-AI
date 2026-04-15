"""
Agent 5: Policy RAG Agent
Retrieves relevant underwriting policy clauses using FAISS similarity search.
Checks if application complies with written policies.
"""

import logging
from typing import Dict, Any, List

from backend.agents.base_agent import BaseAgent
from backend.rag.retriever import PolicyRetriever


class PolicyAgent(BaseAgent):
    """
    Agent 5 responsibilities:
    1. Build context summary from previous agent results
    2. Query FAISS index for relevant policy clauses
    3. Check application against retrieved policies
    4. Identify policy violations or recommendations
    5. Return relevant policy text for Agent 6 (LLM)
    """

    def __init__(self):
        super().__init__("PolicyAgent", 5)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and evaluate relevant policies for this application."""

        application_data = state.get("application_data", {})
        agent3_result = state.get("agent3_result", {})
        agent4_result = state.get("agent4_result", {})

        # ── Step 1: Build query context ──────────────────────────────────
        queries = self._build_queries(application_data, agent3_result, agent4_result)

        # ── Step 2: Retrieve policy clauses ──────────────────────────────
        all_policies = []
        policy_violations = []
        policy_recommendations = []

        retriever = PolicyRetriever()

        for query in queries:
            try:
                results = retriever.search(query, top_k=3)
                for result in results:
                    # Avoid duplicates
                    if not any(p["text"] == result["text"] for p in all_policies):
                        all_policies.append(result)
            except Exception as e:
                self.logger.warning(f"Policy retrieval failed for query '{query}': {e}")

        # ── Step 3: Check for policy violations ──────────────────────────
        policy_violations = self._check_policy_compliance(
            application_data, agent3_result, agent4_result
        )

        # ── Step 4: Generate recommendations ────────────────────────────
        policy_recommendations = self._generate_recommendations(
            application_data, agent4_result
        )

        passed = len(policy_violations) == 0

        return {
            "status": "pass" if passed else "review",  # Policy issues don't auto-fail
            "relevant_policies": all_policies[:8],  # Top 8 most relevant
            "policy_violations": policy_violations,
            "policy_recommendations": policy_recommendations,
            "queries_used": queries,
            "policies_found": len(all_policies),
            "passed": True,  # Policy agent never hard-fails, just flags
        }

    def _build_queries(
        self,
        app_data: Dict[str, Any],
        agent3: Dict[str, Any],
        agent4: Dict[str, Any],
    ) -> List[str]:
        """Build targeted queries for policy retrieval."""
        queries = []

        employment_type = app_data.get("employment_type", "salaried")
        loan_purpose = app_data.get("loan_purpose", "personal")
        loan_amount = float(app_data.get("loan_amount", 0))
        risk_band = agent3.get("risk_band", "medium")
        rules_failed = agent4.get("rules_failed", [])

        queries.append(f"{employment_type} loan {loan_purpose} eligibility criteria")
        queries.append(f"loan amount {int(loan_amount/100000)} lakh approval policy")
        queries.append(f"{risk_band} risk applicant underwriting guidelines")

        if "foir_check" in rules_failed:
            queries.append("high debt obligation income ratio policy")
        if "bureau_score" in rules_failed:
            queries.append("low credit score loan rejection policy")
        if loan_purpose in ["business", "self_employed"]:
            queries.append("self employed business loan documentation requirements")

        return queries[:5]  # Max 5 queries

    def _check_policy_compliance(
        self,
        app_data: Dict[str, Any],
        agent3: Dict[str, Any],
        agent4: Dict[str, Any],
    ) -> List[str]:
        """Identify specific policy violations."""
        violations = []

        # Check hard failures against policies
        hard_failures = agent4.get("hard_rule_failures", [])

        if "age_check" in hard_failures:
            violations.append("Policy Section 3.1: Applicant age outside eligibility band (21-65 years)")
        if "minimum_income" in hard_failures:
            violations.append("Policy Section 4.2: Income below minimum threshold for loan product")
        if "bureau_score" in hard_failures:
            violations.append("Policy Section 5.1: Credit score insufficient for standard loan approval")
        if "foir_check" in hard_failures:
            violations.append("Policy Section 4.4: Fixed obligation ratio exceeds RBI guideline of 50%")

        risk_band = agent3.get("risk_band", "low")
        loan_amount = float(app_data.get("loan_amount", 0))

        if risk_band == "high" and loan_amount > 1000000:
            violations.append("Policy Section 6.3: High-risk applicants restricted to loans below Rs 10 lakh")

        return violations

    def _generate_recommendations(
        self, app_data: Dict[str, Any], agent4: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable policy recommendations."""
        recommendations = []
        soft_failures = agent4.get("soft_rule_failures", [])

        if "employment_stability" in soft_failures:
            recommendations.append("Request additional employment proof or consider co-applicant")
        if "existing_loans" in soft_failures:
            recommendations.append("Request NOC from existing lenders before proceeding")
        if float(app_data.get("loan_amount", 0)) > 2500000:
            recommendations.append("Amounts above Rs 25 lakh require additional income verification")

        return recommendations