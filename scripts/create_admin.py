"""
Create the default admin user in MongoDB.
Admin: admin@loanai.com / admin123
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import bcrypt
from backend.db.mongodb import connect_to_mongo, close_mongo_connection, get_database


async def create_admin():
    await connect_to_mongo()
    db = get_database()

    admin_email = "admin@loanai.com"
    existing = await db.admins.find_one({"email": admin_email})
    if existing:
        print(f"[SKIP] Admin '{admin_email}' already exists.")
        await close_mongo_connection()
        return

    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")

    admin_data = {
        "admin_id": "admin-001",
        "email": admin_email,
        "full_name": "System Administrator",
        "hashed_password": hashed,
        "role": "super_admin",
        "is_active": True,
    }

    await db.admins.insert_one(admin_data)
    print(f"[OK] Created admin user:")
    print(f"     Email:    {admin_email}")
    print(f"     Password: admin123")
    print(f"     Role:     super_admin")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(create_admin())