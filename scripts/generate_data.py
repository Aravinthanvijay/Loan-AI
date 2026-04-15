"""
Generate synthetic Indian loan application data for training the ML model.
Creates 5000+ records with realistic Indian-specific distributions.
"""

import csv
import random
import os
import string
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "loan_applications.csv")
NUM_RECORDS = 5500

EMPLOYERS = [
    "Tata Consultancy Services", "Infosys", "Wipro", "HCL Technologies",
    "Tech Mahindra", "Reliance Industries", "HDFC Bank", "ICICI Bank",
    "State Bank of India", "Bajaj Finance", "Larsen & Toubro", "Mahindra & Mahindra",
    "Bharti Airtel", "ITC Limited", "Asian Paints", "Maruti Suzuki",
    "Hindustan Unilever", "Nestle India", "Sun Pharma", "Dr Reddy's Labs",
    "Accenture India", "Cognizant", "Capgemini", "Deloitte India",
    "Amazon India", "Flipkart", "Google India", "Microsoft India",
    "Self Employed", "Freelance", "Small Business", "Startup",
]

LOAN_PURPOSES = ["home", "personal", "business", "education", "vehicle", "medical", "marriage", "travel"]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Shaurya", "Ananya", "Diya", "Myra", "Sara", "Anika", "Aadhya",
    "Priya", "Neha", "Rahul", "Amit", "Deepak", "Suresh", "Raj", "Pooja",
    "Sneha", "Kavita", "Ravi", "Vijay", "Manish", "Rohit", "Sanjay", "Meera",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Nair",
    "Iyer", "Joshi", "Deshmukh", "Rao", "Pillai", "Menon", "Chauhan",
    "Agarwal", "Mehta", "Shah", "Jain", "Bhatia", "Kapoor", "Malhotra",
]


def generate_pan():
    """Generate a realistic Indian PAN number."""
    letters = string.ascii_uppercase
    pan = (
        random.choice(letters) + random.choice(letters) + random.choice(letters)
        + random.choice("PCHABGJLFTE")
        + random.choice(letters)
        + str(random.randint(1000, 9999))
        + random.choice(letters)
    )
    return pan


def generate_phone():
    """Generate a valid Indian mobile number."""
    return str(random.choice([6, 7, 8, 9])) + ''.join([str(random.randint(0, 9)) for _ in range(9)])


def generate_record(idx):
    """Generate a single synthetic loan application record."""
    age = random.choices(
        range(21, 66),
        weights=[1]*4 + [2]*5 + [4]*10 + [3]*10 + [2]*8 + [1]*8,
        k=1
    )[0]

    employment_type = random.choices(
        ["salaried", "self_employed"],
        weights=[75, 25],
        k=1
    )[0]

    if employment_type == "salaried":
        monthly_income = random.choices(
            [random.randint(15000, 30000), random.randint(30000, 60000),
             random.randint(60000, 120000), random.randint(120000, 300000),
             random.randint(300000, 800000)],
            weights=[20, 35, 25, 15, 5],
            k=1
        )[0]
        employer = random.choice(EMPLOYERS[:28])
    else:
        monthly_income = random.choices(
            [random.randint(10000, 25000), random.randint(25000, 50000),
             random.randint(50000, 150000), random.randint(150000, 500000)],
            weights=[25, 35, 30, 10],
            k=1
        )[0]
        employer = random.choice(EMPLOYERS[28:])

    years_employed = min(age - 21, max(0, random.gauss(age * 0.3, 3)))
    years_employed = round(max(0, years_employed), 1)

    loan_purpose = random.choices(
        LOAN_PURPOSES,
        weights=[25, 25, 15, 10, 15, 5, 3, 2],
        k=1
    )[0]

    annual_income = monthly_income * 12
    if loan_purpose == "home":
        lo = int(annual_income * 2)
        hi = int(min(annual_income * 8, 5000000))
    elif loan_purpose == "vehicle":
        lo = int(annual_income * 0.3)
        hi = int(min(annual_income * 2, 2000000))
    elif loan_purpose == "education":
        lo = 100000
        hi = min(int(annual_income * 3), 3000000)
    elif loan_purpose == "business":
        lo = int(annual_income * 0.5)
        hi = int(min(annual_income * 5, 5000000))
    else:
        lo = 50000
        hi = min(int(annual_income * 1.5), 2000000)

    lo = max(50000, lo)
    hi = max(lo + 1, hi)
    loan_amount = random.randint(lo, hi)

    existing_loans = random.choices([0, 1, 2, 3, 4, 5], weights=[30, 30, 20, 10, 7, 3], k=1)[0]
    existing_emi = 0
    if existing_loans > 0:
        emi_max = max(3001, int(monthly_income * 0.15))
        existing_emi = sum(random.randint(2000, emi_max) for _ in range(existing_loans))
        existing_emi = min(existing_emi, int(monthly_income * 0.6))

    bureau_score = int(random.gauss(720, 80))
    bureau_score = max(300, min(900, bureau_score))

    # --- Default calculation (target variable) ---
    foir = existing_emi / monthly_income if monthly_income > 0 else 1
    loan_to_income = loan_amount / annual_income if annual_income > 0 else 10
    default_prob = 0.0

    # Risk factors
    if bureau_score < 550:
        default_prob += 0.35
    elif bureau_score < 650:
        default_prob += 0.20
    elif bureau_score < 700:
        default_prob += 0.10
    elif bureau_score > 800:
        default_prob -= 0.10

    if foir > 0.5:
        default_prob += 0.25
    elif foir > 0.4:
        default_prob += 0.10

    if loan_to_income > 5:
        default_prob += 0.15
    elif loan_to_income > 3:
        default_prob += 0.05

    if age < 25:
        default_prob += 0.05
    if age > 55:
        default_prob += 0.05

    if years_employed < 1:
        default_prob += 0.10
    elif years_employed > 10:
        default_prob -= 0.05

    if existing_loans > 3:
        default_prob += 0.10

    if employment_type == "self_employed":
        default_prob += 0.05

    if monthly_income < 20000:
        default_prob += 0.05
    elif monthly_income > 150000:
        default_prob -= 0.05

    # Add noise
    default_prob += random.gauss(0, 0.08)
    default_prob = max(0.01, min(0.95, default_prob))

    default = 1 if random.random() < default_prob else 0

    return {
        "full_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "age": age,
        "pan_number": generate_pan(),
        "phone": generate_phone(),
        "email": f"user{idx}@example.com",
        "monthly_income": monthly_income,
        "employment_type": employment_type,
        "employer_name": employer,
        "years_employed": years_employed,
        "loan_amount": loan_amount,
        "loan_purpose": loan_purpose,
        "existing_loans": existing_loans,
        "existing_emi": existing_emi,
        "bureau_score": bureau_score,
        "annual_income": annual_income,
        "foir": round(foir, 4),
        "loan_to_income": round(loan_to_income, 4),
        "default": default,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = [generate_record(i) for i in range(NUM_RECORDS)]

    fieldnames = list(records[0].keys())
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    defaults = sum(1 for r in records if r["default"] == 1)
    print(f"[OK] Generated {len(records)} synthetic loan applications")
    print(f"   Default rate: {defaults}/{len(records)} ({defaults/len(records)*100:.1f}%)")
    print(f"   Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
