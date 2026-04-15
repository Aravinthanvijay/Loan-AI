"""Tests for Agent 3 Credit Scoring."""

import pytest
from unittest.mock import patch, MagicMock
from backend.agents.agent3_credit import CreditAgent


@pytest.mark.asyncio
async def test_low_risk_passes(sample_application_data):
    agent = CreditAgent()
    state = {
        "application_data": sample_application_data,
        "agent2_result": {"salary_extracted": {"gross_salary": 75000, "net_salary": 60000}},
    }
    with patch("backend.ml.inference.ModelInference.predict",
               return_value={"default_probability": 0.15, "raw_score": 0.15}):
        result = await agent.run(state)
    assert result["status"] == "pass"
    assert result["risk_band"] == "low"
    assert result["credit_score"] > 700


@pytest.mark.asyncio
async def test_high_risk_fails(sample_application_data):
    agent = CreditAgent()
    state = {
        "application_data": sample_application_data,
        "agent2_result": {"salary_extracted": {}},
    }
    with patch("backend.ml.inference.ModelInference.predict",
               return_value={"default_probability": 0.75, "raw_score": 0.75}):
        result = await agent.run(state)
    assert result["status"] == "fail"
    assert result["risk_band"] == "high"