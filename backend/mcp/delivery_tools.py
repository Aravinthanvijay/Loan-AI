"""MCP tools for Agent 6 Delivery — result persistence."""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


async def save_result_to_db(application_id: str, agent_key: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Save an agent's result to the application document in MongoDB."""
    from backend.db.repositories.application_repo import ApplicationRepository

    update = {agent_key: result}
    await ApplicationRepository.update_application(application_id, update)
    logger.info(f"Saved {agent_key} for application {application_id}")

    return {"saved": True, "agent_key": agent_key, "application_id": application_id}


async def update_application_status(application_id: str, status: str, **extra_fields) -> Dict[str, Any]:
    """Update the application status and optional extra fields."""
    from backend.db.repositories.application_repo import ApplicationRepository

    update = {"status": status, "updated_at": datetime.utcnow()}
    update.update(extra_fields)

    await ApplicationRepository.update_application(application_id, update)
    logger.info(f"Updated application {application_id} status to {status}")

    return {"updated": True, "application_id": application_id, "status": status}


async def save_final_decision(
    application_id: str,
    decision: str,
    confidence: float,
    reasoning: str,
    key_factors: list,
) -> Dict[str, Any]:
    """Save the final AI decision to the application."""
    from backend.db.repositories.application_repo import ApplicationRepository

    update = {
        "final_decision": decision,
        "ai_confidence": confidence,
        "ai_reasoning": reasoning,
        "ai_key_factors": key_factors,
        "processing_completed_at": datetime.utcnow(),
    }

    if decision == "approve":
        update["status"] = "approved"
    elif decision == "reject":
        update["status"] = "rejected"
    else:
        update["status"] = "pending_admin"

    await ApplicationRepository.update_application(application_id, update)
    logger.info(f"Saved final decision for {application_id}: {decision} (confidence: {confidence})")

    return {"saved": True, "decision": decision}