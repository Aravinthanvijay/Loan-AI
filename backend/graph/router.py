"""
Conditional routing logic for LangGraph workflow.
Decides whether to continue to next agent or stop early.
"""

from typing import Dict, Any


def should_continue_after_agent(state: Dict[str, Any], agent_number: int) -> str:
    """
    Determine if workflow should continue or stop after an agent.

    Returns:
        "continue" or "stop"
    """

    if agent_number == 1:
        agent1 = state.get("agent1_result", {})
        # Hard stop for blacklisted applicants only
        if agent1.get("blacklist_check") is False:
            return "stop"  # Blacklisted → all agents stop, go to decision
        if len(agent1.get("validation_errors", [])) > 5:
            return "stop"  # Too many validation errors
        return "continue"

    elif agent_number == 4:
        agent4 = state.get("agent4_result", {})
        hard_failures = agent4.get("hard_rule_failures", [])
        # If ALL hard rules failed, still continue for complete analysis
        return "continue"

    return "continue"