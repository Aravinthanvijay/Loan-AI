import asyncio
from backend.db.mongodb import get_database

async def test():
    db = get_database()
    count = await db.applications.count_documents({})
    print(f'Applications in DB: {count}')

asyncio.run(test())