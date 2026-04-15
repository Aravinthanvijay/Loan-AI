"""
Blacklist repository for CRUD operations on blacklist collection.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.db.mongodb import get_database
from backend.db.models import Blacklist


class BlacklistRepository:
    """Repository for blacklist operations."""
    
    @staticmethod
    async def add_to_blacklist(blacklist_data: Dict[str, Any]) -> Blacklist:
        """Add entry to blacklist."""
        db = get_database()
        blacklist_entry = Blacklist(**blacklist_data)
        
        await db.blacklist.insert_one(blacklist_entry.dict())
        return blacklist_entry
    
    @staticmethod
    async def is_blacklisted(pan_number: str) -> bool:
        """Check if PAN is blacklisted."""
        db = get_database()
        count = await db.blacklist.count_documents({
            "pan_number": pan_number.upper(),
            "is_active": True
        })
        return count > 0
    
    @staticmethod
    async def get_blacklist_entry(pan_number: str) -> Optional[Dict[str, Any]]:
        """Get blacklist entry by PAN."""
        db = get_database()
        return await db.blacklist.find_one({
            "pan_number": pan_number.upper(),
            "is_active": True
        })
    
    @staticmethod
    async def get_all_blacklist(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all blacklist entries."""
        db = get_database()
        cursor = db.blacklist.find({"is_active": True}).sort("added_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def remove_from_blacklist(pan_number: str) -> bool:
        """Deactivate blacklist entry."""
        db = get_database()
        result = await db.blacklist.update_one(
            {"pan_number": pan_number.upper()},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0