"""
Build FAISS index from the underwriting policy document.
Chunks the policy text, generates embeddings, and saves the index.
"""

import os
import sys
import pickle
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

POLICY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "policies", "underwriting_policy.txt")
EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "embeddings")


def chunk_policy(text, chunk_size=500, overlap=100):
    """Split policy text into overlapping chunks by paragraph."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_id": len(chunks),
            })
            # Keep overlap
            words = current_chunk.split()
            overlap_words = words[-min(len(words), overlap // 5):]
            current_chunk = " ".join(overlap_words) + "\n\n" + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "chunk_id": len(chunks),
        })

    return chunks


def build():
    if not os.path.exists(POLICY_PATH):
        print(f"❌ Policy file not found at {POLICY_PATH}")
        print("   Creating a default policy file...")
        os.makedirs(os.path.dirname(POLICY_PATH), exist_ok=True)
        with open(POLICY_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_POLICY)
        print(f"   ✅ Created default policy at {POLICY_PATH}")

    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        policy_text = f.read()

    chunks = chunk_policy(policy_text)
    print(f"📄 Chunked policy into {len(chunks)} segments")

    # Generate embeddings
    print("🔄 Generating embeddings with sentence-transformers...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [c["text"] for c in chunks]
        embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings).astype(np.float32)
    except ImportError:
        print("⚠️  sentence-transformers not installed, generating random embeddings for demo")
        embeddings = np.random.rand(len(chunks), 384).astype(np.float32)
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms

    # Build FAISS index
    import faiss
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity (pre-normalized)
    index.add(embeddings)

    # Save
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    index_path = os.path.join(EMBEDDINGS_DIR, "faiss_index.bin")
    chunks_path = os.path.join(EMBEDDINGS_DIR, "policy_embeddings.pkl")

    faiss.write_index(index, index_path)
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)

    print(f"✅ FAISS index saved to {index_path}")
    print(f"✅ Policy chunks saved to {chunks_path}")
    print(f"   Index dimension: {dimension}, vectors: {index.ntotal}")


DEFAULT_POLICY = """LOAN UNDERWRITING POLICY DOCUMENT
Version 2.0 — Effective Date: January 2024

SECTION 1: ELIGIBILITY CRITERIA

1.1 Age Requirements
The minimum age for loan applicants is 21 years. The maximum age at loan maturity should not exceed 65 years. Applicants below 25 years are considered higher risk and require additional income verification.

1.2 Income Requirements
Minimum monthly income for salaried applicants: Rs 15,000. Minimum monthly income for self-employed applicants: Rs 20,000. Income must be verifiable through salary slips, bank statements, or IT returns.

1.3 Employment Stability
Salaried applicants must have a minimum of 6 months with current employer. Self-employed applicants must demonstrate 2 years of business continuity. Government employees and PSU employees are considered lower risk.

SECTION 2: FINANCIAL ASSESSMENT

2.1 Fixed Obligation to Income Ratio (FOIR)
Maximum FOIR allowed is 50% (0.50). FOIR is calculated as: (Total existing EMI + Proposed EMI) / Monthly Income. Applicants with FOIR between 40-50% require additional scrutiny. FOIR below 30% is considered healthy.

2.2 Loan-to-Income Ratio
Maximum loan amount should not exceed 60 times the monthly income for salaried applicants. For self-employed, maximum is 48 times monthly income. Home loans may be extended up to 84 times monthly income with adequate collateral.

2.3 Bureau Score Requirements
Minimum CIBIL/bureau score required: 650. Score 750+ is considered excellent and qualifies for preferential rates. Score 650-700 requires additional documentation. Score below 650 should be auto-rejected unless strong compensating factors exist.

SECTION 3: DOCUMENT VERIFICATION

3.1 Mandatory Documents
PAN Card — Must be valid and match applicant details. Salary Slip — Last 3 months for salaried applicants. Bank Statements — Last 6 months showing salary credits. Address Proof — Aadhaar, Passport, or Utility Bill.

3.2 Cross-Verification Rules
PAN name must match application name (fuzzy match allowed up to 80% similarity). Salary on slip must be within 10% of declared income. Any mismatch above threshold triggers manual review.

3.3 OCR Confidence Threshold
Minimum OCR confidence for automated processing: 70%. Documents with confidence below 70% require manual verification. Blurred or damaged documents should be flagged for re-upload.

SECTION 4: RISK CLASSIFICATION

4.1 Risk Bands
LOW RISK: Bureau score 750+, FOIR < 30%, stable employment > 5 years. MEDIUM RISK: Bureau score 700-749, FOIR 30-40%, employment 2-5 years. HIGH RISK: Bureau score 650-699, FOIR 40-50%, employment < 2 years. VERY HIGH RISK: Bureau score < 650 or FOIR > 50% — auto-reject recommended.

4.2 Compensating Factors
High income (> Rs 1,00,000/month) can offset medium bureau score. Long employment history (> 10 years) can compensate for higher FOIR. Collateral-backed loans have reduced risk weight.

SECTION 5: FRAUD DETECTION

5.1 Blacklist Checks
All applicants must be checked against the internal blacklist database. Blacklisted PAN numbers result in automatic rejection. Previously rejected applicants within 90 days should be flagged.

5.2 Duplicate Application Detection
Same PAN + similar loan amount within 24 hours = potential duplicate. Same phone number + same employer within 7 days = suspicious. Multiple applications from same IP address within 1 hour = block.

SECTION 6: DECISION GUIDELINES

6.1 Auto-Approve Criteria
Bureau score 750+, FOIR < 30%, all documents verified, no blacklist hit, salaried with 3+ years employment, loan amount within 36x monthly income.

6.2 Auto-Reject Criteria
Blacklisted PAN, bureau score below 550, FOIR > 60%, fake documents detected, age outside 21-65 range.

6.3 Manual Review Triggers
FOIR between 45-50%, bureau score 650-700, document OCR confidence 60-70%, income mismatch > 15%, self-employed with < 2 years history, loan amount > 48x monthly income.

SECTION 7: RBI COMPLIANCE

7.1 Fair Lending Practices
All decisions must be non-discriminatory based on gender, religion, caste, or region. Income-based assessment must be the primary criterion. Rejection reasons must be clearly documented and communicable to applicant.

7.2 Interest Rate Guidelines
Risk-based pricing is permitted within RBI-prescribed limits. Higher risk applicants may be charged up to 2% additional spread. Prepayment penalties follow RBI circular guidelines.
"""


if __name__ == "__main__":
    build()