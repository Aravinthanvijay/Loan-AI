"""
Agent 6: LLM Decision Agent
Uses Groq mixtral-8x7b-32768 to synthesize all agent outputs and make final decision.
This agent reasons like an experienced loan officer.
"""

import logging
import json
from typing import Dict, Any

from groq import Groq

from backend.agents.base_agent import BaseAgent
from backend.config import settings


class DecisionAgent(BaseAgent):
    """
    Agent 6 responsibilities:
    1. Collect ALL outputs from Agents 1-5
    2. Build comprehensive prompt for Groq
    3. Groq Mixtral reasons over all evidence
    4. Return structured decision: APPROVE / REJECT / MANUAL_REVIEW
    5. Provide detailed reasoning and key factors
    """

    def __init__(self):
        super().__init__("DecisionAgent", 6)
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Use Groq Mixtral to make final loan decision based on all agent outputs."""

        application_data = state.get("application_data", {})
        agent1 = state.get("agent1_result", {})
        agent2 = state.get("agent2_result", {})
        agent3 = state.get("agent3_result", {})
        agent4 = state.get("agent4_result", {})
        agent5 = state.get("agent5_result", {})

        # ── Step 1: Check for hard stops ─────────────────────────────────
        # Only auto-reject for blacklisted applicants
        if agent1.get("blacklist_check") is False:
            return {
                "status": "complete",
                "decision": "reject",
                "confidence": 0.99,
                "reasoning": "Application auto-rejected: Applicant PAN is on the blacklist.",
                "key_factors": ["Blacklisted PAN number"],
                "recommendations": ["No further processing"],
                "auto_decision": True,
                "requires_hitl": False,
                "passed": True,  # Agent completed (with auto-reject)
            }

        # ── Step 2: Build LLM prompt for AI recommendation ──────────────────
        prompt = self._build_prompt(application_data, agent1, agent2, agent3, agent4, agent5)

        # ── Step 3: Call Groq LLM ──────────────────────────────────────────
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                max_tokens=1500,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            llm_output = response.choices[0].message.content
            parsed = self._parse_llm_response(llm_output)

        except Exception as e:
            self.logger.error(f"Groq API call failed: {e}")
            # Fallback to rule-based decision
            parsed = self._rule_based_fallback(agent3, agent4)

        # ── IMPORTANT: ALL non-blacklisted applications require manual review ──
        # Even if LLM recommends approval, admin must make final decision
        llm_recommendation = parsed["decision"]
        
        return {
            "status": "complete",
            "decision": "manual_review",  # Force all to manual review
            "requires_hitl": True,
            "confidence": 0.0,  # No auto-confidence since human reviews
            "reasoning": f"MANUAL REVIEW REQUIRED: AI Agent recommendation: {llm_recommendation.upper()}. {parsed['reasoning']}",
            "llm_recommendation": llm_recommendation,  # Include AI recommendation for admin reference
            "key_factors": parsed["key_factors"],
            "recommendations": parsed["recommendations"],
            "auto_decision": False,
            "passed": True,  # Agent 6 completed successfully (decision pending admin action)
        }

    def _get_system_prompt(self) -> str:
        return """You are an experienced senior loan underwriting officer at an Indian bank.
You must make fair, accurate, and explainable loan decisions based on data provided.

You must respond ONLY in this exact JSON format:
{
  "decision": "approve" | "reject" | "manual_review",
  "confidence": 0.0 to 1.0,
  "reasoning": "2-3 sentence explanation of your decision",
  "key_factors": ["factor1", "factor2", "factor3"],
  "recommendations": ["recommendation1", "recommendation2"]
}

Guidelines:
- APPROVE: Strong application, all rules pass, low-medium risk, documents verified
- REJECT: Critical rule failures, high risk, fraud indicators, blacklisted
- MANUAL_REVIEW: Borderline cases, document issues, medium-high risk with compensating factors
- Be specific about Indian lending context (RBI guidelines, FOIR limits)
- Do not add any text outside the JSON"""

    def _build_prompt(self, app, a1, a2, a3, a4, a5) -> str:
        return f"""LOAN APPLICATION UNDERWRITING DECISION REQUEST

=== APPLICANT PROFILE ===
Name: {app.get('full_name', 'N/A')}
Age: {app.get('age', 'N/A')} years
Employment: {app.get('employment_type', 'N/A')} at {app.get('employer_name', 'N/A')}
Years Employed: {app.get('years_employed', 'N/A')}
Monthly Income: Rs {float(app.get('monthly_income', 0)):,.0f}
Loan Amount Requested: Rs {float(app.get('loan_amount', 0)):,.0f}
Loan Purpose: {app.get('loan_purpose', 'N/A')}
Existing Loans: {app.get('existing_loans', 0)}
Existing Monthly EMI: Rs {float(app.get('existing_emi', 0)):,.0f}

=== AGENT 1: INTAKE VALIDATION ===
Status: {a1.get('status', 'unknown').upper()}
Blacklist Check: {'CLEAR' if a1.get('blacklist_check') else 'FLAGGED'}
Duplicate Check: {'CLEAR' if a1.get('duplicate_check') else 'DUPLICATE FOUND'}
Validation Errors: {json.dumps(a1.get('validation_errors', []))}
FOIR: {a1.get('validated_data', {}).get('foir', 'N/A')}

=== AGENT 2: DOCUMENT VERIFICATION ===
Status: {a2.get('status', 'unknown').upper()}
PAN Card Extracted: {a2.get('pan_extracted', {}).get('pan_number', 'Not extracted')}
Salary OCR Gross: Rs {a2.get('salary_extracted', {}).get('gross_salary', 'Not extracted')}
Salary OCR Net: Rs {a2.get('salary_extracted', {}).get('net_salary', 'Not extracted')}
Document Issues: {json.dumps(a2.get('issues', []))}
OCR Confidence: {a2.get('ocr_confidence', {}).get('average', 0):.0f}%

=== AGENT 3: CREDIT SCORING ===
Credit Score: {a3.get('credit_score', 'N/A')} (scale 300-900)
Default Probability: {a3.get('default_probability', 'N/A')}
Risk Band: {a3.get('risk_band', 'N/A').upper()}
Top Risk Factors: {json.dumps([f.get('description', '') for f in a3.get('top_factors', [])[:3]])}

=== AGENT 4: RULES ENGINE ===
Status: {a4.get('status', 'unknown').upper()}
Rules Passed: {json.dumps(a4.get('rules_passed', []))}
Rules Failed: {json.dumps(a4.get('rules_failed', []))}
Hard Rule Failures: {json.dumps(a4.get('hard_rule_failures', []))}

=== AGENT 5: POLICY COMPLIANCE ===
Policy Violations: {json.dumps(a5.get('policy_violations', []))}
Policy Recommendations: {json.dumps(a5.get('policy_recommendations', []))}

Based on all the above information, provide your underwriting decision in the required JSON format."""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Groq's JSON response."""
        try:
            # Strip any markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            parsed = json.loads(cleaned.strip())

            # Validate required fields
            return {
                "decision": parsed.get("decision", "manual_review"),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reasoning": parsed.get("reasoning", "Decision based on application analysis"),
                "key_factors": parsed.get("key_factors", []),
                "recommendations": parsed.get("recommendations", []),
            }
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse LLM response: {e}. Raw: {response_text[:200]}")
            return {
                "decision": "manual_review",
                "confidence": 0.5,
                "reasoning": "Automated decision parsing failed. Manual review required.",
                "key_factors": ["System parsing error"],
                "recommendations": ["Manual underwriter review recommended"],
            }

    def _rule_based_fallback(self, agent3: Dict, agent4: Dict) -> Dict[str, Any]:
        """Fallback decision when Groq API is unavailable."""
        hard_failures = agent4.get("hard_rule_failures", [])
        risk_band = agent3.get("risk_band", "high")

        if hard_failures:
            return {
                "decision": "reject",
                "confidence": 0.85,
                "reasoning": f"Application rejected due to hard rule failures: {', '.join(hard_failures)}",
                "key_factors": hard_failures,
                "recommendations": [],
            }
        elif risk_band == "low":
            return {
                "decision": "approve",
                "confidence": 0.75,
                "reasoning": "Application approved based on rules compliance and low risk profile",
                "key_factors": ["All rules passed", "Low credit risk"],
                "recommendations": [],
            }
        else:
            return {
                "decision": "manual_review",
                "confidence": 0.6,
                "reasoning": "Medium-high risk application requires manual underwriter review",
                "key_factors": ["Risk level requires human review"],
                "recommendations": ["Assign to senior underwriter"],
            }