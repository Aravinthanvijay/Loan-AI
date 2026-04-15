"""
Shared state schema for LangGraph workflow.
This dict is passed between all 6 agents and updated at each step.
"""

from typing import Dict, Any, Optional, List
from typing_extensions import TypedDict


class LoanApplicationState(TypedDict):
    """
    The shared state that flows through all 6 agents.
    Each agent reads from this and adds its results.
    LangGraph requires TypedDict for state schema.
    """

    # Core application data (set at start, read-only for agents)
    application_id: str
    application_data: Dict[str, Any]

    # Agent results (each agent populates its own field)
    agent1_result: Optional[Dict[str, Any]]
    agent2_result: Optional[Dict[str, Any]]
    agent3_result: Optional[Dict[str, Any]]
    agent4_result: Optional[Dict[str, Any]]
    agent5_result: Optional[Dict[str, Any]]
    agent6_result: Optional[Dict[str, Any]]

    # Workflow control
    current_agent: int
    workflow_status: str  # "running", "completed", "failed", "stopped"
    stop_reason: Optional[str]  # If workflow stopped early

    # Metadata
    errors: List[str]
    processing_log: List[str]