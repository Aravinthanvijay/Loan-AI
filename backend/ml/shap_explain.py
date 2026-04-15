"""SHAP explainability for ML model predictions."""

import numpy as np
import logging
from typing import Dict, Any, List

from backend.ml.inference import ModelInference
from backend.ml.features import FeatureExtractor, FEATURE_NAMES

logger = logging.getLogger(__name__)

# Try to import SHAP, but don't fail if torch DLL issues occur
try:
    import shap
    SHAP_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"SHAP not available: {e}. Will use feature importance instead.")
    SHAP_AVAILABLE = False


class SHAPExplainer:
    """Generate SHAP explanations for model predictions."""

    _explainer = None

    @classmethod
    def _get_explainer(cls):
        if not SHAP_AVAILABLE:
            return None
        if cls._explainer is None and ModelInference._model is not None:
            try:
                cls._explainer = shap.TreeExplainer(ModelInference._model)
            except (ImportError, OSError) as e:
                logger.warning(f"Could not create SHAP explainer: {e}")
                return None
        return cls._explainer

    @classmethod
    def explain(cls, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate SHAP values for a prediction.
        Returns top factors that influenced the decision.
        Falls back to feature importance if SHAP unavailable.
        """
        explainer = cls._get_explainer()
        
        # If SHAP is not available, use model feature importance
        if explainer is None or not SHAP_AVAILABLE:
            logger.info("Using feature importance instead of SHAP values")
            return cls._explain_with_feature_importance(features)

        try:
            X = FeatureExtractor.to_array(features)
            if ModelInference._scaler:
                X = ModelInference._scaler.transform(X)

            shap_values = explainer.shap_values(X)

            # For binary classification, shap_values[1] is for class 1 (default)
            if isinstance(shap_values, list):
                sv = shap_values[1][0]
            else:
                sv = shap_values[0]

            # Map to feature names
            shap_dict = {name: round(float(sv[i]), 4) for i, name in enumerate(FEATURE_NAMES)}

            # Top 5 factors sorted by absolute impact
            sorted_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            top_factors = []
            for feature, shap_val in sorted_factors:
                top_factors.append({
                    "factor": feature,
                    "shap_value": shap_val,
                    "impact": "increases_risk" if shap_val > 0 else "decreases_risk",
                    "feature_value": round(features.get(feature, 0), 4),
                })

            return {
                "shap_values": shap_dict,
                "top_factors": top_factors,
            }
        except Exception as e:
            logger.warning(f"SHAP explain failed, using feature importance: {e}")
            return cls._explain_with_feature_importance(features)

    @classmethod
    def _explain_with_feature_importance(cls, features: Dict[str, float]) -> Dict[str, Any]:
        """Fallback: use model's feature importance instead of SHAP."""
        if ModelInference._model is None:
            return {
                "shap_values": {},
                "top_factors": [],
                "method": "No model loaded",
            }

        try:
            # Get XGBoost feature importance
            importances = ModelInference._model.feature_importances_
            importance_dict = {name: round(float(imp), 4) for name, imp in zip(FEATURE_NAMES, importances)}

            # Top 5 features
            sorted_features = sorted(importance_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            top_factors = []
            for feature, importance in sorted_features:
                top_factors.append({
                    "factor": feature,
                    "importance": importance,
                    "method": "feature_importance",
                    "feature_value": round(features.get(feature, 0), 4),
                })

            return {
                "shap_values": importance_dict,
                "top_factors": top_factors,
                "method": "feature_importance_fallback",
            }
        except Exception as e:
            logger.error(f"Feature importance extraction failed: {e}")
            return {
                "shap_values": {},
                "top_factors": [],
                "method": "error",
            }