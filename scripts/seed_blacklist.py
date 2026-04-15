"""
Seed the MongoDB blacklist collection with synthetic blacklisted PAN numbers.
"""

import asyncio
import csv
import os
import random
import string
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.db.mongodb import connect_to_mongo, close_mongo_connection, get_database

REASONS = [
    "Fraudulent loan application detected",
    "Identity theft confirmed by investigation",
    "Multiple defaults across financial institutions",
    "Willful defaulter as per RBI classification",
    "Fake documents submitted in previous application",
    "CIBIL score permanently damaged due to fraud",
    "Court-ordered financial restriction",
    "Money laundering investigation subject",
    "Repeated bounced cheques and payment defaults",
    "Previous loan write-off by lending institution",
]

NAMES = [
    "Vikram Malhotra", "Sunil Dubey", "Rakesh Pandey", "Priya Tiwari",
    "Deepika Chauhan", "Manoj Yadav", "Sunita Devi", "Rajesh Mishra",
    "Anita Kumari", "Bharat Bhushan", "Sandeep Jha", "Geeta Rani",
    "Mukesh Agarwal", "Poonam Singh", "Ramesh Sahu", "Kavya Nair",
    "Arjun Pillai", "Meena Iyer", "Siddharth Rao", "Lakshmi Reddy",
    "Govind Sharma", "Asha Devi", "Prakash Verma", "Neelam Gupta",
    "Harish Kumar", "Seema Jain", "Dinesh Patel", "Usha Mehta",
    "Kiran Bhatia", "Omprakash Yadav", "Savita Kumari", "Ashok Tiwari",
    "Nirmala Pandey", "Satish Dubey", "Kusum Devi", "Mahendra Shah",
    "Pushpa Rani", "Yogesh Agarwal", "Indira Mishra", "Baldev Singh",
    "Sarita Chauhan", "Ganesh Joshi", "Kamla Devi", "Naresh Malhotra",
    "Radha Kumari", "Kishore Kapoor", "Manju Devi", "Surender Kumar",
    "Parveen Bano", "Trilok Chand",
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic")


def generate_pan():
    letters = string.ascii_uppercase
    return (
        random.choice(letters) + random.choice(letters) + random.choice(letters)
        + random.choice("PCHABGJLFTE")
        + random.choice(letters)
        + str(random.randint(1000, 9999))
        + random.choice(letters)
    )


async def seed():
    await connect_to_mongo()
    db = get_database()

    # Clear existing blacklist
    await db.blacklist.delete_many({})

    entries = []
    pans_used = set()
    for i in range(50):
        pan = generate_pan()
        while pan in pans_used:
            pan = generate_pan()
        pans_used.add(pan)

        entry = {
            "blacklist_id": f"BL-{i+1:04d}",
            "pan_number": pan,
            "name": NAMES[i] if i < len(NAMES) else f"Person {i+1}",
            "reason": random.choice(REASONS),
            "added_by": "system",
            "is_active": True,
        }
        entries.append(entry)

    await db.blacklist.insert_many(entries)

    # Save CSV backup
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "blacklist.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["blacklist_id", "pan_number", "name", "reason"])
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e[k] for k in ["blacklist_id", "pan_number", "name", "reason"]})

    print(f"✅ Seeded {len(entries)} blacklist entries into MongoDB")
    print(f"   CSV backup: {csv_path}")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed())
