"""
LangGraph workflow definition.
Connects all 6 agents as sequential nodes with conditional routing.
"""

import logging
from langgraph.graph import StateGraph, END

from backend.graph.state import LoanApplicationState
from backend.graph.router import should_continue_after_agent
from backend.agents.agent1_intake import IntakeAgent
from backend.agents.agent2_document import DocumentAgent
from backend.agents.agent3_credit import CreditAgent
from backend.agents.agent4_rules import RulesAgent
from backend.agents.agent5_policy import PolicyAgent
from backend.agents.agent6_decision import DecisionAgent

logger = logging.getLogger(__name__)


class LoanWorkflow:
    """Builds and compiles the 6-agent LangGraph workflow."""

    def __init__(self):
        self.agent1 = IntakeAgent()
        self.agent2 = DocumentAgent()
        self.agent3 = CreditAgent()
        self.agent4 = RulesAgent()
        self.agent5 = PolicyAgent()
        self.agent6 = DecisionAgent()
        self._graph = None

    def build(self) -> StateGraph:
        """Build the LangGraph StateGraph with all nodes and edges."""

        workflow = StateGraph(LoanApplicationState)

        # ── Add agent nodes ──────────────────────────────────────────────
        workflow.add_node("agent1_intake", self._run_agent1)
        workflow.add_node("agent2_document", self._run_agent2)
        workflow.add_node("agent3_credit", self._run_agent3)
        workflow.add_node("agent4_rules", self._run_agent4)
        workflow.add_node("agent5_policy", self._run_agent5)
        workflow.add_node("agent6_decision", self._run_agent6)

        # ── Set entry point ──────────────────────────────────────────────
        workflow.set_entry_point("agent1_intake")

        # ── Add conditional edges (with early stopping) ──────────────────
        # After Agent 1: if blacklisted → stop, else continue
        workflow.add_conditional_edges(
            "agent1_intake",
            lambda state: should_continue_after_agent(state, 1),
            {
                "continue": "agent2_document",
                "stop": "agent6_decision",  # Jump to decision for blacklisted
            }
        )

        # After Agent 2: always continue for complete analysis
        workflow.add_edge("agent2_document", "agent3_credit")

        # After Agent 3: always continue
        workflow.add_edge("agent3_credit", "agent4_rules")

        # After Agent 4: if all hard rules failed → jump to decision
        workflow.add_conditional_edges(
            "agent4_rules",
            lambda state: should_continue_after_agent(state, 4),
            {
                "continue": "agent5_policy",
                "stop": "agent6_decision",
            }
        )

        # After Agent 5: always go to decision
        workflow.add_edge("agent5_policy", "agent6_decision")

        # After Agent 6: end
        workflow.add_edge("agent6_decision", END)

        self._graph = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")
        return self._graph

    def get_compiled_graph(self):
        """Get or build the compiled graph."""
        if self._graph is None:
            self.build()
        return self._graph

    async def _run_agent1(self, state: LoanApplicationState) -> dict:
        result = await self.agent1.run(state)
        return {
            "agent1_result": result,
            "current_agent": 1,
            "processing_log": state.get("processing_log", []) + [f"Agent 1 completed: {result.get('status')}"]
        }

    async def _run_agent2(self, state: LoanApplicationState) -> dict:
        result = await self.agent2.run(state)
        return {
            "agent2_result": result,
            "current_agent": 2,
            "processing_log": state.get("processing_log", []) + [f"Agent 2 completed: {result.get('status')}"]
        }

    async def _run_agent3(self, state: LoanApplicationState) -> dict:
        result = await self.agent3.run(state)
        return {
            "agent3_result": result,
            "current_agent": 3,
            "processing_log": state.get("processing_log", []) + [f"Agent 3 completed: credit_score={result.get('credit_score')}"]
        }

    async def _run_agent4(self, state: LoanApplicationState) -> dict:
        result = await self.agent4.run(state)
        return {
            "agent4_result": result,
            "current_agent": 4,
            "processing_log": state.get("processing_log", []) + [f"Agent 4 completed: {result.get('status')}"]
        }

    async def _run_agent5(self, state: LoanApplicationState) -> dict:
        result = await self.agent5.run(state)
        return {
            "agent5_result": result,
            "current_agent": 5,
            "processing_log": state.get("processing_log", []) + [f"Agent 5 completed: {result.get('policies_found', 0)} policies found"]
        }

    async def _run_agent6(self, state: LoanApplicationState) -> dict:
        result = await self.agent6.run(state)
        return {
            "agent6_result": result,
            "current_agent": 6,
            "workflow_status": "completed",
            "processing_log": state.get("processing_log", []) + [f"Agent 6 completed: decision={result.get('decision')}"]
        }