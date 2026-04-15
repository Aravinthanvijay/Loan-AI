"""
OCR fine-tuning utilities.
Generates synthetic training data and fine-tunes Tesseract for Indian documents.
"""

import os
import random
import string
import logging
from typing import List, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


class OCRFineTuner:
    """
    Fine-tuning utilities for OCR on Indian documents.
    Generates synthetic training data and optimizes Tesseract config.
    """

    INDIAN_NAMES = [
        "RAHUL KUMAR SHARMA", "PRIYA DEVI SINGH", "AMIT GUPTA",
        "SUNITA PATEL", "RAJESH VERMA", "ANITA KUMARI", "VIJAY KUMAR",
        "MEENA REDDY", "SURESH NAIR", "KAVITHA KRISHNAN",
        "MANOJ TIWARI", "GEETA JOSHI", "RAVI SHANKAR", "POOJA YADAV"
    ]

    EMPLOYERS = [
        "INFOSYS LIMITED", "TATA CONSULTANCY SERVICES LTD",
        "WIPRO TECHNOLOGIES PVT LTD", "HCL TECHNOLOGIES LIMITED",
        "RELIANCE INDUSTRIES LIMITED", "HDFC BANK LIMITED",
        "STATE BANK OF INDIA", "ICICI BANK LIMITED",
        "MAHINDRA AND MAHINDRA LTD", "LARSEN AND TOUBRO LIMITED"
    ]

    @staticmethod
    def generate_synthetic_pan_image(
        pan_number: str = None,
        name: str = None,
        dob: str = None,
        output_path: str = None,
        add_noise: bool = True,
    ) -> Image.Image:
        """
        Generate a synthetic PAN card image for testing/training.

        Args:
            pan_number: PAN number (auto-generated if None)
            name: Name on card (random if None)
            dob: Date of birth (random if None)
            output_path: Save to this path if provided
            add_noise: Add realistic image noise

        Returns:
            PIL Image of synthetic PAN card
        """
        # Generate random data if not provided
        if pan_number is None:
            pan_number = OCRFineTuner._generate_pan()
        if name is None:
            name = random.choice(OCRFineTuner.INDIAN_NAMES)
        if dob is None:
            dob = OCRFineTuner._generate_dob()

        # Card dimensions (standard PAN card ratio)
        width, height = 856, 540
        img = Image.new('RGB', (width, height), color='#F5F5DC')  # Beige background

        draw = ImageDraw.Draw(img)

        # Try to use a monospace font; fallback to default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large

        # Header
        draw.rectangle([0, 0, width, 60], fill='#0D47A1')
        draw.text((width // 2 - 180, 15), "INCOME TAX DEPARTMENT", font=font_large, fill='white')

        # Govt of India text
        draw.text((20, 70), "GOVT. OF INDIA", font=font_small, fill='#333333')

        # PAN Number (large, prominent)
        draw.text((20, 160), "Permanent Account Number", font=font_small, fill='#555555')
        draw.text((20, 190), pan_number, font=font_large, fill='#000000')

        # Name
        draw.text((20, 260), "Name", font=font_small, fill='#555555')
        draw.text((20, 285), name, font=font_medium, fill='#000000')

        # DOB
        draw.text((20, 370), "Date of Birth", font=font_small, fill='#555555')
        draw.text((20, 395), dob, font=font_medium, fill='#000000')

        # Signature line
        draw.line([550, 450, 820, 450], fill='#333333', width=2)
        draw.text((600, 460), "Signature", font=font_small, fill='#555555')

        # Add noise if requested
        if add_noise:
            img = OCRFineTuner._add_image_noise(img)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, quality=85)
            logger.info(f"Saved synthetic PAN card: {output_path}")

        return img

    @staticmethod
    def generate_synthetic_salary_slip(
        employee_name: str = None,
        employer_name: str = None,
        gross_salary: float = None,
        net_salary: float = None,
        month: str = None,
        pan_number: str = None,
        output_path: str = None,
    ) -> Image.Image:
        """Generate a synthetic salary slip image."""
        if employee_name is None:
            employee_name = random.choice(OCRFineTuner.INDIAN_NAMES)
        if employer_name is None:
            employer_name = random.choice(OCRFineTuner.EMPLOYERS)
        if gross_salary is None:
            gross_salary = random.randint(25000, 150000)
        if net_salary is None:
            net_salary = int(gross_salary * random.uniform(0.75, 0.88))
        if month is None:
            months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
                     "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
            month = f"{random.choice(months)} 2024"
        if pan_number is None:
            pan_number = OCRFineTuner._generate_pan()

        basic = int(gross_salary * 0.4)
        hra = int(gross_salary * 0.2)
        allowances = gross_salary - basic - hra
        deductions = gross_salary - net_salary
        pf = int(basic * 0.12)
        tax = deductions - pf

        width, height = 900, 700
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font_title = ImageFont.load_default()
            font_header = font_title
            font_body = font_title

        # Company header
        draw.rectangle([0, 0, width, 70], fill='#1565C0')
        draw.text((20, 20), employer_name, font=font_title, fill='white')
        draw.text((20, 50), "SALARY SLIP", font=font_header, fill='#BBDEFB')

        # Employee info box
        draw.rectangle([20, 80, width - 20, 160], outline='#CCCCCC', width=1)
        draw.text((30, 90), f"Employee Name: {employee_name}", font=font_body, fill='black')
        draw.text((30, 115), f"Month: {month}", font=font_body, fill='black')
        draw.text((30, 140), f"PAN: {pan_number}", font=font_body, fill='black')

        # Earnings section
        y = 180
        draw.text((30, y), "EARNINGS", font=font_header, fill='#1565C0')
        y += 30
        draw.line([20, y, width // 2 - 10, y], fill='#CCCCCC')
        y += 10
        for label, amount in [("Basic Salary", basic), ("HRA", hra), ("Allowances", allowances)]:
            draw.text((30, y), label, font=font_body, fill='black')
            draw.text((300, y), f"Rs. {amount:,}", font=font_body, fill='black')
            y += 30

        draw.line([20, y, width // 2 - 10, y], fill='black')
        y += 5
        draw.text((30, y), "GROSS SALARY", font=font_header, fill='black')
        draw.text((300, y), f"Rs. {gross_salary:,}", font=font_header, fill='black')
        y += 40

        # Deductions
        draw.text((width // 2 + 20, 180), "DEDUCTIONS", font=font_header, fill='#C62828')
        dy = 210
        for label, amount in [("PF", pf), ("Income Tax", tax)]:
            draw.text((width // 2 + 20, dy), label, font=font_body, fill='black')
            draw.text((width // 2 + 280, dy), f"Rs. {amount:,}", font=font_body, fill='black')
            dy += 30

        # Net salary
        draw.rectangle([20, y, width - 20, y + 50], fill='#E3F2FD')
        draw.text((30, y + 10), "NET TAKE HOME SALARY", font=font_header, fill='black')
        draw.text((500, y + 10), f"Rs. {net_salary:,}", font=font_header, fill='#1B5E20')

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, quality=90)
            logger.info(f"Saved synthetic salary slip: {output_path}")

        return img

    @staticmethod
    def generate_training_samples(
        output_dir: str,
        num_samples: int = 50
    ) -> List[Dict]:
        """
        Generate multiple training samples for testing and fine-tuning.

        Args:
            output_dir: Directory to save images
            num_samples: Number of samples to generate

        Returns:
            List of metadata dicts for each sample
        """
        samples = []
        pan_dir = os.path.join(output_dir, "pan_cards")
        salary_dir = os.path.join(output_dir, "salary_slips")
        os.makedirs(pan_dir, exist_ok=True)
        os.makedirs(salary_dir, exist_ok=True)

        for i in range(num_samples):
            pan = OCRFineTuner._generate_pan()
            name = random.choice(OCRFineTuner.INDIAN_NAMES)
            dob = OCRFineTuner._generate_dob()
            gross = random.randint(20000, 200000)

            pan_path = os.path.join(pan_dir, f"pan_{i+1:03d}.jpg")
            OCRFineTuner.generate_synthetic_pan_image(
                pan_number=pan, name=name, dob=dob, output_path=pan_path
            )

            salary_path = os.path.join(salary_dir, f"salary_{i+1:03d}.jpg")
            OCRFineTuner.generate_synthetic_salary_slip(
                employee_name=name, pan_number=pan,
                gross_salary=gross, output_path=salary_path
            )

            samples.append({
                "index": i + 1,
                "pan_number": pan,
                "name": name,
                "dob": dob,
                "gross_salary": gross,
                "pan_image": pan_path,
                "salary_image": salary_path,
            })

        logger.info(f"Generated {num_samples} training samples in {output_dir}")
        return samples

    @staticmethod
    def _generate_pan() -> str:
        """Generate a valid format PAN number."""
        letters = string.ascii_uppercase
        first_three = ''.join(random.choices(letters, k=3))
        fourth = random.choice("PCHABGJLFTE")
        fifth = random.choice(letters)
        digits = ''.join(random.choices(string.digits, k=4))
        last = random.choice(letters)
        return f"{first_three}{fourth}{fifth}{digits}{last}"

    @staticmethod
    def _generate_dob() -> str:
        """Generate a random date of birth for working age person."""
        year = random.randint(1960, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{day:02d}/{month:02d}/{year}"

    @staticmethod
    def _add_image_noise(img: Image.Image, intensity: float = 0.02) -> Image.Image:
        """Add realistic noise to synthetic image."""
        img_array = np.array(img).astype(np.float32)
        noise = np.random.normal(0, intensity * 255, img_array.shape)
        noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)