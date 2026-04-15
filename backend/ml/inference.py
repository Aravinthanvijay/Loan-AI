"""
ML model inference.
Loads trained XGBoost model and makes predictions.
"""

import joblib
import json
import numpy as np
import logging
import os
from typing import Dict, Any

from backend.config import settings
from backend.ml.features import FeatureExtractor

logger = logging.getLogger(__name__)


class ModelInference:
    """Load and run XGBoost model for credit scoring."""

    _model = None
    _scaler = None
    _feature_names = None
    _model_version = "untrained"

    @classmethod
    def load_model(cls):
        """Load model artifacts from disk."""
        try:
            if os.path.exists(settings.MODEL_PATH):
                cls._model = joblib.load(settings.MODEL_PATH)
                logger.info(f"Loaded ML model from {settings.MODEL_PATH}")
            else:
                logger.warning(f"Model not found at {settings.MODEL_PATH}. Run scripts/train_model.py first.")

            if os.path.exists(settings.SCALER_PATH):
                cls._scaler = joblib.load(settings.SCALER_PATH)

            if os.path.exists(settings.FEATURE_NAMES_PATH):
                with open(settings.FEATURE_NAMES_PATH, "r") as f:
                    meta = json.load(f)
                    cls._model_version = meta.get("version", "1.0")

        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")

    @classmethod
    def predict(cls, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict default probability for given features.

        Args:
            features: Feature dict from FeatureExtractor.extract()

        Returns:
            Dict with default_probability and raw_score
        """
        if cls._model is None:
            cls.load_model()

        if cls._model is None:
            raise RuntimeError("ML model not available. Train it first with scripts/train_model.py")

        # Convert to array
        X = FeatureExtractor.to_array(features)

        # Scale if scaler available
        if cls._scaler is not None:
            X = cls._scaler.transform(X)

        # Predict
        default_prob = float(cls._model.predict_proba(X)[0][1])

        return {
            "default_probability": round(default_prob, 4),
            "raw_score": round(default_prob, 4),
        }

    @classmethod
    def get_model_version(cls) -> str:
        return cls._model_version