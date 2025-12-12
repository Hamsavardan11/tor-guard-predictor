"""
Health check endpoint
"""

from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """
    Health check endpoint
    Returns status of API and loaded models
    """
    
    model_registry = request.app.state.model_registry
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": model_registry.list_models(),
        "num_models": len(model_registry.models),
        "encoders_loaded": len(model_registry.encoders) > 0,
        "shap_available": model_registry.shap_explainer is not None
    }
