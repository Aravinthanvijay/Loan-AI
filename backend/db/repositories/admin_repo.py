"""
Admin repository for CRUD operations on admins collection.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from backend.db.mongodb import get_database
from backend.db.models import Admin


class AdminRepository:
    """Repository for admin operations."""
    
    @staticmethod
    async def create_admin(admin_data: Dict[str, Any]) -> Admin:
        """Create a new admin user."""
        db = get_database()
        admin = Admin(**admin_data)
        
        await db.admins.insert_one(admin.dict())
        return admin
    
    @staticmethod
    async def get_admin_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get admin by email."""
        db = get_database()
        return await db.admins.find_one({"email": email, "is_active": True})
    
    @staticmethod
    async def get_admin_by_id(admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin by admin_id."""
        db = get_database()
        return await db.admins.find_one({"admin_id": admin_id, "is_active": True})
    
    @staticmethod
    async def update_last_login(admin_id: str) -> bool:
        """Update admin's last login time."""
        db = get_database()
        result = await db.admins.update_one(
            {"admin_id": admin_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def admin_exists_by_email(email: str) -> bool:
        """Check if admin exists by email."""
        db = get_database()
        count = await db.admins.count_documents({"email": email})
        return count > 0