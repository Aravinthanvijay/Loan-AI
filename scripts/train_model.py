"""
Train XGBoost classifier on synthetic loan data for default prediction.
Saves model, scaler, and feature metadata to backend/ml/artifacts/.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import joblib

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic", "loan_applications.csv")
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "ml", "artifacts")

FEATURE_COLUMNS = [
    "age",
    "annual_income",
    "loan_amount",
    "existing_loans",
    "existing_emi",
    "foir",
    "loan_to_income",
    "years_employed",
    "employment_type_encoded",
    "loan_purpose_encoded",
    "bureau_score",
]

EMPLOYMENT_MAP = {"salaried": 0, "self_employed": 1}
LOAN_PURPOSE_MAP = {
    "home": 0, "personal": 1, "business": 2, "education": 3,
    "vehicle": 4, "medical": 5, "marriage": 6, "travel": 7, "other": 8
}


def train():
    print("📊 Loading data...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Loaded {len(df)} records, default rate: {df['default'].mean()*100:.1f}%")

    # Encode categoricals
    df["employment_type_encoded"] = df["employment_type"].map(EMPLOYMENT_MAP).fillna(0).astype(int)
    df["loan_purpose_encoded"] = df["loan_purpose"].map(LOAN_PURPOSE_MAP).fillna(8).astype(int)

    X = df[FEATURE_COLUMNS].copy()
    y = df["default"].copy()

    # Handle missing values
    X = X.fillna(0)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"   Train default rate: {y_train.mean()*100:.1f}%")

    # SMOTE for class balance
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"   After SMOTE: {len(X_train_resampled)} samples")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost
    print("\n🤖 Training XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    model.fit(
        X_train_scaled, y_train_resampled,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Default", "Default"]))
    print(f"   ROC AUC Score: {roc_auc:.4f}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"   Confusion Matrix:\n{cm}")

    # Save artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    model_path = os.path.join(ARTIFACTS_DIR, "model.pkl")
    scaler_path = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
    meta_path = os.path.join(ARTIFACTS_DIR, "feature_names.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "version": "1.0",
        "feature_names": FEATURE_COLUMNS,
        "training_date": datetime.utcnow().isoformat(),
        "training_samples": len(X_train_resampled),
        "test_samples": len(X_test),
        "roc_auc": round(roc_auc, 4),
        "model_type": "XGBClassifier",
        "employment_map": EMPLOYMENT_MAP,
        "loan_purpose_map": LOAN_PURPOSE_MAP,
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Saved model to {model_path}")
    print(f"✅ Saved scaler to {scaler_path}")
    print(f"✅ Saved metadata to {meta_path}")


if __name__ == "__main__":
    train()
