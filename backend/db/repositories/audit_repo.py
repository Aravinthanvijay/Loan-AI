"""
Audit repository for logging admin actions.
"""

from typing import Dict, Any, List
from datetime import datetime

from backend.db.mongodb import get_database
from backend.db.models import AuditLog


class AuditRepository:
    """Repository for audit log operations."""
    
    @staticmethod
    async def create_audit_log(log_data: Dict[str, Any]) -> AuditLog:
        """Create an audit log entry."""
        db = get_database()
        audit_log = AuditLog(**log_data)
        
        await db.audit_logs.insert_one(audit_log.dict())
        return audit_log
    
    @staticmethod
    async def get_logs_by_application(application_id: str) -> List[Dict[str, Any]]:
        """Get all audit logs for an application."""
        db = get_database()
        cursor = db.audit_logs.find({"application_id": application_id}).sort("timestamp", -1)
        return await cursor.to_list(length=100)
    
    @staticmethod
    async def get_logs_by_admin(admin_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit logs for a specific admin."""
        db = get_database()
        cursor = db.audit_logs.find({"admin_id": admin_id}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def get_recent_logs(limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit logs."""
        db = get_database()
        cursor = db.audit_logs.find({}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)