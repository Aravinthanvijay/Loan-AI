"""
Train the XGBoost credit scoring model.
Run this script once to generate model artifacts.
Usage: python -m backend.ml.train
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data() -> pd.DataFrame:
    """Load training data from Kaggle dataset or synthetic fallback."""
    raw_path = "data/raw/credit_risk_dataset.csv"
    synthetic_path = "data/synthetic/loan_applications.csv"

    if os.path.exists(raw_path):
        logger.info(f"Loading Kaggle dataset from {raw_path}")
        df = pd.read_csv(raw_path)
        return preprocess_kaggle_data(df)
    elif os.path.exists(synthetic_path):
        logger.info(f"Loading synthetic dataset from {synthetic_path}")
        return pd.read_csv(synthetic_path)
    else:
        logger.warning("No dataset found, generating synthetic data")
        return generate_synthetic_data(n=5000)


def preprocess_kaggle_data(df: pd.DataFrame) -> pd.DataFrame:
    """Map Kaggle credit risk dataset columns to our feature names."""
    mapping = {
        "person_age": "age",
        "person_income": "annual_income",
        "loan_amnt": "loan_amount",
        "loan_percent_income": "loan_percent_income",
        "loan_status": "default",
    }
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})

    # Add derived features if not present
    if "foir" not in df.columns:
        df["foir"] = 0.3
    if "existing_loans" not in df.columns:
        df["existing_loans"] = 0
    if "existing_emi" not in df.columns:
        df["existing_emi"] = 0
    if "loan_to_income" not in df.columns:
        df["loan_to_income"] = df["loan_amount"] / df["annual_income"].replace(0, 1)
    if "employment_type_encoded" not in df.columns:
        df["employment_type_encoded"] = 0
    if "years_employed" not in df.columns:
        df["years_employed"] = 3.0
    if "loan_purpose_encoded" not in df.columns:
        df["loan_purpose_encoded"] = 1

    df = df.dropna(subset=["default"])
    return df


def generate_synthetic_data(n: int = 5000) -> pd.DataFrame:
    """Generate synthetic loan data for training."""
    np.random.seed(42)
    data = {
        "age": np.random.randint(21, 65, n),
        "annual_income": np.random.randint(180000, 2400000, n),
        "loan_amount": np.random.randint(50000, 5000000, n),
        "loan_percent_income": np.random.uniform(0.05, 0.9, n),
        "existing_loans": np.random.randint(0, 5, n),
        "existing_emi": np.random.randint(0, 50000, n),
        "foir": np.random.uniform(0.1, 0.7, n),
        "loan_to_income": np.random.uniform(0.1, 6.0, n),
        "employment_type_encoded": np.random.randint(0, 2, n),
        "years_employed": np.random.uniform(0, 20, n),
        "loan_purpose_encoded": np.random.randint(0, 9, n),
    }
    df = pd.DataFrame(data)
    # Simulate defaults based on risk factors
    risk = (
        (df["foir"] > 0.5).astype(int) * 0.3
        + (df["loan_percent_income"] > 0.5).astype(int) * 0.25
        + (df["loan_to_income"] > 4).astype(int) * 0.2
        + (df["existing_loans"] > 2).astype(int) * 0.15
        + np.random.uniform(0, 0.1, n)
    )
    df["default"] = (risk > 0.45).astype(int)
    return df


def train():
    """Full training pipeline."""
    feature_cols = [
        "age", "annual_income", "loan_amount", "loan_percent_income",
        "existing_loans", "existing_emi", "foir", "loan_to_income",
        "employment_type_encoded", "years_employed", "loan_purpose_encoded"
    ]

    df = load_data()
    df = df.fillna(0)

    X = df[feature_cols]
    y = df["default"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Handle class imbalance
    try:
        smote = SMOTE(random_state=42)
        X_train, y_train = smote.fit_resample(X_train, y_train)
        logger.info(f"SMOTE applied: {len(X_train)} training samples")
    except Exception as e:
        logger.warning(f"SMOTE failed: {e}")

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="auc",
        random_state=42,
    )
    model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=50)

    # Evaluate
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    logger.info(f"Model ROC-AUC: {auc:.4f}")
    print(classification_report(y_test, (y_pred_proba > 0.5).astype(int)))

    # Save artifacts
    os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
    joblib.dump(model, settings.MODEL_PATH)
    joblib.dump(scaler, settings.SCALER_PATH)
    with open(settings.FEATURE_NAMES_PATH, "w") as f:
        json.dump({"features": feature_cols, "version": "1.0", "auc": auc}, f)

    logger.info(f"✅ Model saved to {settings.MODEL_PATH}")
    logger.info(f"✅ Scaler saved to {settings.SCALER_PATH}")
    return model, scaler


if __name__ == "__main__":
    train()