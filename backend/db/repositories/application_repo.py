"""
Application repository for CRUD operations on applications collection.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.db.mongodb import get_database
from backend.db.models import Application, ApplicationStatus


class ApplicationRepository:
    """Repository for loan application operations."""
    
    @staticmethod
    async def create_application(app_data: Dict[str, Any]) -> Application:
        """Create a new loan application."""
        db = get_database()
        application = Application(**app_data)
        
        result = await db.applications.insert_one(application.dict())
        app_data['_id'] = result.inserted_id
        
        return application
    
    @staticmethod
    async def get_application_by_id(application_id: str) -> Optional[Dict[str, Any]]:
        """Get application by application_id."""
        db = get_database()
        return await db.applications.find_one({"application_id": application_id})
    
    @staticmethod
    async def get_applications_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Get all applications for a user."""
        db = get_database()
        try:
            count = await db.applications.count_documents({"user_id": user_id})
            
            cursor = db.applications.find({"user_id": user_id}).sort("created_at", -1)
            apps = await cursor.to_list(length=None)
            
            return apps if apps else []
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching applications for user {user_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_all_applications(
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all applications with pagination."""
        db = get_database()
        
        try:
            query = {}
            if status:
                query["status"] = status
            
            # Fetch count
            count = await db.applications.count_documents(query)
            
            # Fetch paginated results
            cursor = db.applications.find(query).sort("created_at", -1).skip(skip).limit(limit)
            apps = await cursor.to_list(length=None)
            
            return apps if apps else []
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching applications: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def update_application(
        application_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update application data."""
        db = get_database()
        update_data['updated_at'] = datetime.utcnow()
        
        result = await db.applications.update_one(
            {"application_id": application_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def update_status(application_id: str, status: ApplicationStatus) -> bool:
        """Update application status."""
        return await ApplicationRepository.update_application(
            application_id,
            {"status": status.value}
        )
    
    @staticmethod
    async def save_agent_result(
        application_id: str,
        agent_number: int,
        result: Dict[str, Any]
    ) -> bool:
        """Save agent result to application."""
        field_name = f"agent{agent_number}_result"
        return await ApplicationRepository.update_application(
            application_id,
            {field_name: result}
        )
    
    @staticmethod
    async def check_duplicate_application(
        user_id: str,
        loan_amount: float,
        hours: int = 24
    ) -> bool:
        """Check for duplicate applications within time window."""
        db = get_database()
        
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        count = await db.applications.count_documents({
            "user_id": user_id,
            "loan_amount": loan_amount,
            "created_at": {"$gte": cutoff_time}
        })
        
        return count > 0
    
    @staticmethod
    async def count_applications(status: Optional[str] = None) -> int:
        """Count applications by status."""
        db = get_database()
        query = {"status": status} if status else {}
        return await db.applications.count_documents(query)