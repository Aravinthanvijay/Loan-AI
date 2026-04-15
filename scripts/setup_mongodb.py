"""
Set up MongoDB indexes for optimal query performance.
Run once during initial setup.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.db.mongodb import connect_to_mongo, close_mongo_connection, get_database


async def create_indexes():
    """Create indexes on all collections."""
    db = get_database()
    
    print("[INFO] Creating MongoDB indexes...")

    # Applications collection
    collections = {
        "applications": [
            {"keys": [("application_id", 1)], "unique": True},
            {"keys": [("user_id", 1)], "unique": False},
            {"keys": [("status", 1)], "unique": False},
            {"keys": [("created_at", -1)], "unique": False},
            {"keys": [("pan_number", 1)], "unique": False},
            {"keys": [("email", 1)], "unique": False},
        ],
        "users": [
            {"keys": [("user_id", 1)], "unique": True},
            {"keys": [("email", 1)], "unique": True},
            {"keys": [("pan_number", 1)], "unique": True},
        ],
        "admins": [
            {"keys": [("admin_id", 1)], "unique": True},
            {"keys": [("email", 1)], "unique": True},
        ],
        "blacklist": [
            {"keys": [("pan_number", 1)], "unique": True},
        ],
        "documents": [
            {"keys": [("application_id", 1)], "unique": False},
            {"keys": [("uploaded_at", -1)], "unique": False},
        ],
        "audit_logs": [
            {"keys": [("application_id", 1)], "unique": False},
            {"keys": [("created_at", -1)], "unique": False},
        ],
    }

    for collection_name, indexes in collections.items():
        collection = db[collection_name]
        for index_info in indexes:
            try:
                index_name = await collection.create_index(
                    index_info["keys"], 
                    unique=index_info.get("unique", False)
                )
                print(f"  ✓ {collection_name}: {index_name}")
            except Exception as e:
                print(f"  ✗ {collection_name}: {e}")

    print("[OK] MongoDB indexes created successfully")


async def main():
    await connect_to_mongo()
    await create_indexes()
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
