"""Tests for Agent 1 Intake."""

import pytest
from backend.agents.agent1_intake import IntakeAgent


@pytest.mark.asyncio
async def test_valid_application_passes(sample_application_data, mock_db):
    agent = IntakeAgent()
    state = {"application_data": sample_application_data}
    result = await agent.run(state)
    assert result["status"] == "pass"
    assert result["blacklist_check"] is True
    assert len(result["validation_errors"]) == 0


@pytest.mark.asyncio
async def test_invalid_pan_fails(sample_application_data, mock_db):
    sample_application_data["pan_number"] = "INVALID"
    agent = IntakeAgent()
    state = {"application_data": sample_application_data}
    result = await agent.run(state)
    assert result["status"] == "fail"
    assert any("PAN" in err for err in result["validation_errors"])


@pytest.mark.asyncio
async def test_underage_fails(sample_application_data, mock_db):
    sample_application_data["age"] = 18
    agent = IntakeAgent()
    state = {"application_data": sample_application_data}
    result = await agent.run(state)
    assert result["status"] == "fail"


@pytest.mark.asyncio
async def test_low_income_fails(sample_application_data, mock_db):
    sample_application_data["monthly_income"] = 5000
    agent = IntakeAgent()
    state = {"application_data": sample_application_data}
    result = await agent.run(state)
    assert result["status"] == "fail"