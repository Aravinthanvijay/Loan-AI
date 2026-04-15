"""
Graph executor — runs the LangGraph workflow for a given application.
Handles state initialization, persistence to MongoDB, and error recovery.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from backend.graph.workflow import LoanWorkflow
from backend.db.repositories.application_repo import ApplicationRepository
from backend.db.models import ApplicationStatus

logger = logging.getLogger(__name__)

# Singleton workflow instance
_workflow = None


def get_workflow() -> LoanWorkflow:
    global _workflow
    if _workflow is None:
        _workflow = LoanWorkflow()
        _workflow.build()
    return _workflow


class GraphExecutor:
    """Execute the LangGraph workflow for loan processing."""

    @staticmethod
    async def run_workflow(application_id: str, application_data: Dict[str, Any]):
        """
        Run the full 6-agent workflow for an application.
        This is called as a background task from the user route.
        """
        logger.info(f"Starting workflow for application: {application_id}")

        # Update status to processing
        await ApplicationRepository.update_application(application_id, {
            "status": ApplicationStatus.PROCESSING.value,
            "processing_started_at": datetime.utcnow(),
        })

        # Initialize state
        initial_state = {
            "application_id": application_id,
            "application_data": application_data,
            "agent1_result": None,
            "agent2_result": None,
            "agent3_result": None,
            "agent4_result": None,
            "agent5_result": None,
            "agent6_result": None,
            "current_agent": 0,
            "workflow_status": "running",
            "stop_reason": None,
            "errors": [],
            "processing_log": [f"Workflow started at {datetime.utcnow().isoformat()}"],
        }

        try:
            workflow = get_workflow()
            graph = workflow.get_compiled_graph()

            # Run the graph
            final_state = await graph.ainvoke(initial_state)

            # Save all agent results to MongoDB
            await GraphExecutor._persist_results(application_id, final_state)

            # ── All applications require manual review ──
            # Admin must review and make final approval/rejection decision
            final_status = ApplicationStatus.MANUAL_REVIEW

            await ApplicationRepository.update_application(application_id, {
                "status": final_status.value,
                "requires_hitl": True,
                "processing_completed_at": datetime.utcnow(),
            })

            logger.info(f"Workflow completed for {application_id}: Requires manual review")

        except Exception as e:
            logger.error(f"Workflow FAILED for {application_id}: {e}", exc_info=True)
            await ApplicationRepository.update_application(application_id, {
                "status": ApplicationStatus.FAILED.value,
                "processing_completed_at": datetime.utcnow(),
            })

    @staticmethod
    async def _persist_results(application_id: str, final_state: Dict[str, Any]):
        """Save all agent results to MongoDB."""
        update_data = {}

        for i in range(1, 7):
            result_key = f"agent{i}_result"
            if final_state.get(result_key):
                update_data[result_key] = final_state[result_key]

        if update_data:
            await ApplicationRepository.update_application(application_id, update_data)