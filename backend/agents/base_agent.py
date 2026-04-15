"""
Base agent class that all 6 agents inherit from.
Provides common structure, logging, error handling, and timing.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for all loan processing agents.
    Every agent must implement the process() method.
    """

    def __init__(self, agent_name: str, agent_number: int):
        self.agent_name = agent_name
        self.agent_number = agent_number
        self.logger = logging.getLogger(f"agent.{agent_name}")

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent and handle errors gracefully.
        Wraps the process() method with timing and logging.
        """
        start_time = time.time()
        self.logger.info(f"Agent {self.agent_number} ({self.agent_name}) starting...")

        try:
            result = await self.process(state)
            elapsed = round(time.time() - start_time, 2)
            self.logger.info(
                f"Agent {self.agent_number} ({self.agent_name}) completed in {elapsed}s"
            )
            result["agent_elapsed_seconds"] = elapsed
            result["agent_completed_at"] = datetime.now(timezone.utc).isoformat()
            return result

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            self.logger.error(
                f"Agent {self.agent_number} ({self.agent_name}) FAILED after {elapsed}s: {e}",
                exc_info=True
            )
            return {
                "status": "error",
                "error": str(e),
                "agent_number": self.agent_number,
                "agent_name": self.agent_name,
                "agent_elapsed_seconds": elapsed,
                "agent_completed_at": datetime.utcnow().isoformat(),
            }

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core agent logic. Must be implemented by each agent.

        Args:
            state: The shared LangGraph state dict

        Returns:
            Dict with agent results. Must include "status" key.
        """
        pass

    def _pass_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to return a passing result."""
        return {"status": "pass", **data}

    def _fail_result(self, reason: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Helper to return a failing result."""
        result = {"status": "fail", "reason": reason}
        if data:
            result.update(data)
        return result