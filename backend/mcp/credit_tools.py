"""MCP tools for Agent 3 Credit Scoring."""

from typing import Dict, Any


def load_xgboost_model() -> Dict[str, Any]:
    """Load the XGBoost model."""
    from backend.ml.inference import ModelInference
    ModelInference.load_model()
    return {"loaded": ModelInference._model is not None}


def predict_default_probability(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict default probability from features."""
    from backend.ml.inference import ModelInference
    return ModelInference.predict(features)


def generate_shap_values(features: Dict[str, float]) -> Dict[str, Any]:
    """Generate SHAP values for features."""
    from backend.ml.shap_explain import SHAPExplainer
    return SHAPExplainer.explain(features)