"""Integration test for full 6-agent workflow."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_full_workflow_low_risk(sample_application_data):
    """Test complete workflow with a low-risk application."""
    from backend.graph.workflow import LoanWorkflow

    with patch("backend.db.repositories.blacklist_repo.BlacklistRepository.is_blacklisted",
               AsyncMock(return_value=False)), \
         patch("backend.db.repositories.application_repo.ApplicationRepository.check_duplicate_application",
               AsyncMock(return_value=False)), \
         patch("backend.ml.inference.ModelInference.predict",
               return_value={"default_probability": 0.12, "raw_score": 0.12}), \
         patch("backend.ml.inference.ModelInference._model", MagicMock()), \
         patch("backend.rag.retriever.PolicyRetriever.search", return_value=[]), \
         patch("groq.Groq.chat.completions.create") as mock_groq:

        mock_groq.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"decision":"approve","confidence":0.9,"reasoning":"Strong profile","key_factors":["Good income"],"recommendations":[]}'))]
        )

        workflow = LoanWorkflow()
        workflow.build()
        graph = workflow.get_compiled_graph()

        initial_state = {
            "application_id": "TEST001",
            "application_data": sample_application_data,
            "agent1_result": None, "agent2_result": None,
            "agent3_result": None, "agent4_result": None,
            "agent5_result": None, "agent6_result": None,
            "current_agent": 0, "workflow_status": "running",
            "stop_reason": None, "errors": [], "processing_log": [],
        }

        final_state = await graph.ainvoke(initial_state)

        assert final_state["agent6_result"] is not None
        assert final_state["agent6_result"]["decision"] in ["approve", "reject", "manual_review"]