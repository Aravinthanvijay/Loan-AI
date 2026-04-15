"""Admin-facing routes for reviewing and deciding on applications."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import logging

from backend.auth.dependencies import get_current_admin
from backend.db.repositories.application_repo import ApplicationRepository
from backend.db.repositories.audit_repo import AuditRepository
from backend.db.repositories.blacklist_repo import BlacklistRepository
from backend.db.models import ApplicationStatus, DecisionType
from backend.utils.response import APIResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)


class DecisionRequest(BaseModel):
    decision: str  # "approve" or "reject"
    notes: Optional[str] = None


class BlacklistRequest(BaseModel):
    pan_number: str
    reason: str
    name: Optional[str] = None


@router.get("/applications")
async def get_all_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_admin: dict = Depends(get_current_admin),
):
    """Get paginated list of all loan applications."""
    try:
        skip = (page - 1) * per_page
        apps = await ApplicationRepository.get_all_applications(skip=skip, limit=per_page, status=status)
        total = await ApplicationRepository.count_applications(status=status)
        return APIResponse.paginated(data=apps, total=total, page=page, per_page=per_page)
    except Exception as e:
        logger.error(f"Error retrieving applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving applications: {str(e)}")


@router.get("/applications/{application_id}")
async def get_application_detail(
    application_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    """Get full detail of a specific application including all agent results."""
    app = await ApplicationRepository.get_application_by_id(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return APIResponse.success(data=app)


@router.post("/applications/{application_id}/decide")
async def make_decision(
    application_id: str,
    request: DecisionRequest,
    current_admin: dict = Depends(get_current_admin),
):
    """Make a final approval/rejection decision on an application."""
    app = await ApplicationRepository.get_application_by_id(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if request.decision not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")

    status = ApplicationStatus.APPROVED if request.decision == "approve" else ApplicationStatus.REJECTED

    await ApplicationRepository.update_application(application_id, {
        "status": status.value,
        "final_decision": request.decision,
        "admin_decision": request.decision,
        "admin_notes": request.notes,
        "decided_by": current_admin["admin_id"],
        "decided_at": datetime.now(timezone.utc),
    })

    # Create audit log
    await AuditRepository.create_audit_log({
        "admin_id": current_admin["admin_id"],
        "application_id": application_id,
        "action": request.decision,
        "decision": request.decision,
        "notes": request.notes,
    })

    return APIResponse.success(message=f"Application {request.decision}d successfully")


@router.get("/trace/{application_id}")
async def get_agent_trace(
    application_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    """Get the full agent processing trace for an application."""
    app = await ApplicationRepository.get_application_by_id(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    trace = {
        "application_id": application_id,
        "agent1_intake": app.get("agent1_result"),
        "agent2_document": app.get("agent2_result"),
        "agent3_credit": app.get("agent3_result"),
        "agent4_rules": app.get("agent4_result"),
        "agent5_policy": app.get("agent5_result"),
        "agent6_decision": app.get("agent6_result"),
    }

    return APIResponse.success(data=trace)


@router.post("/blacklist")
async def add_to_blacklist(
    request: BlacklistRequest,
    current_admin: dict = Depends(get_current_admin),
):
    """Add a PAN number to the blacklist."""
    entry = await BlacklistRepository.add_to_blacklist({
        "pan_number": request.pan_number.upper(),
        "reason": request.reason,
        "name": request.name,
        "added_by": current_admin["admin_id"],
    })
    return APIResponse.success(data={"blacklist_id": entry.blacklist_id}, message="Added to blacklist")


@router.get("/stats")
async def get_stats(current_admin: dict = Depends(get_current_admin)):
    """Get application statistics for admin dashboard."""
    total = await ApplicationRepository.count_applications()
    approved = await ApplicationRepository.count_applications("approved")
    rejected = await ApplicationRepository.count_applications("rejected")
    pending = await ApplicationRepository.count_applications("pending_admin")
    processing = await ApplicationRepository.count_applications("processing")

    return APIResponse.success(data={
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending_review": pending,
        "processing": processing,
        "approval_rate": f"{(approved / total * 100):.1f}%" if total > 0 else "N/A",
    })