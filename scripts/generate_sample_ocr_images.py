"""
Script to generate synthetic OCR test images.
Run this once to populate data/ocr_samples/ folder.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ocr.fine_tuner import OCRFineTuner

if __name__ == "__main__":
    output_dir = "data/ocr_samples"
    print(f"Generating OCR test samples in {output_dir}...")
    samples = OCRFineTuner.generate_training_samples(output_dir=output_dir, num_samples=10)
    print(f"✅ Generated {len(samples)} sample pairs")
    for s in samples[:3]:
        print(f"  PAN: {s['pan_number']} | Name: {s['name']} | Gross: Rs {s['gross_salary']:,}")
    print("Done! Images are in data/ocr_samples/pan_cards/ and data/ocr_samples/salary_slips/")