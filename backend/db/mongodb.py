"""
MongoDB connection management using Motor (async driver).
Provides connection lifecycle and database access.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, ClassVar
import logging

from backend.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: ClassVar[Optional[AsyncIOMotorClient]] = None


async def connect_to_mongo():
    """
    Connect to MongoDB and create indexes.
    Called during application startup.
    """
    try:
        MongoDB.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        
        # Test connection
        await MongoDB.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB at {settings.MONGODB_URL}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    if MongoDB.client:
        MongoDB.client.close()
        logger.info("✅ Closed MongoDB connection")


def get_database():
    """Get the database instance."""
    if MongoDB.client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo() first.")
    return MongoDB.client[settings.MONGODB_DB_NAME]


async def create_indexes():
    """Create indexes for all collections."""
    db = get_database()
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("pan_number", unique=True)
    await db.users.create_index("phone")
    
    # Applications collection indexes
    await db.applications.create_index("user_id")
    await db.applications.create_index("application_id", unique=True)
    await db.applications.create_index("status")
    await db.applications.create_index([("created_at", -1)])
    await db.applications.create_index([("user_id", 1), ("created_at", -1)])
    
    # Blacklist collection indexes
    await db.blacklist.create_index("pan_number", unique=True)
    await db.blacklist.create_index("reason")
    
    # Admins collection indexes
    await db.admins.create_index("email", unique=True)
    
    # Audit logs collection indexes
    await db.audit_logs.create_index("application_id")
    await db.audit_logs.create_index("admin_id")
    await db.audit_logs.create_index([("timestamp", -1)])
    
    logger.info("✅ Created database indexes")