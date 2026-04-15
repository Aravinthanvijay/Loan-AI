"""MCP tools for Agent 1 Intake."""

import re
from typing import Dict, Any


async def validate_pan_format(pan_number: str) -> Dict[str, Any]:
    """Validate PAN number format."""
    pattern = r'^[A-Z]{3}[PCHABGJLFTE][A-Z][0-9]{4}[A-Z]$'
    is_valid = bool(re.match(pattern, pan_number.upper()))
    return {"valid": is_valid, "pan_number": pan_number.upper()}


async def check_blacklist_db(pan_number: str) -> Dict[str, Any]:
    """Check PAN against blacklist in MongoDB."""
    from backend.db.repositories.blacklist_repo import BlacklistRepository
    is_blacklisted = await BlacklistRepository.is_blacklisted(pan_number)
    entry = None
    if is_blacklisted:
        entry = await BlacklistRepository.get_blacklist_entry(pan_number)
    return {
        "is_blacklisted": is_blacklisted,
        "reason": entry.get("reason") if entry else None,
    }


async def check_duplicate_application(user_id: str, loan_amount: float) -> Dict[str, Any]:
    """Check for duplicate applications."""
    from backend.db.repositories.application_repo import ApplicationRepository
    is_duplicate = await ApplicationRepository.check_duplicate_application(user_id, loan_amount)
    return {"is_duplicate": is_duplicate}