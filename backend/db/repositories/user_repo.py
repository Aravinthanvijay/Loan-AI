"""
User repository for CRUD operations on users collection.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from backend.db.mongodb import get_database
from backend.db.models import User


class UserRepository:
    """Repository for user operations."""
    
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        db = get_database()
        user = User(**user_data)
        
        result = await db.users.insert_one(user.dict())
        user_data['_id'] = result.inserted_id
        
        return user
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        db = get_database()
        return await db.users.find_one({"email": email})
    
    @staticmethod
    async def get_user_by_pan(pan_number: str) -> Optional[Dict[str, Any]]:
        """Get user by PAN number."""
        db = get_database()
        return await db.users.find_one({"pan_number": pan_number.upper()})
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user_id."""
        db = get_database()
        return await db.users.find_one({"user_id": user_id})
    
    @staticmethod
    async def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information."""
        db = get_database()
        update_data['updated_at'] = datetime.utcnow()
        
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def user_exists_by_email(email: str) -> bool:
        """Check if user exists by email."""
        db = get_database()
        count = await db.users.count_documents({"email": email})
        return count > 0
    
    @staticmethod
    async def user_exists_by_pan(pan_number: str) -> bool:
        """Check if user exists by PAN."""
        db = get_database()
        count = await db.users.count_documents({"pan_number": pan_number.upper()})
        return count > 0