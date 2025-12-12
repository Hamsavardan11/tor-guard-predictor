"""
Explainability endpoint
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import numpy as np

from backend.core.feature_engineering import FeatureEngineer
from backend.core.explainability_service import ExplainabilityService

router = APIRouter()


class ExplainRequest(BaseModel):
    """Request model for explanation"""
    input_features: dict = Field(..., description="Input features to explain")
    guard_index: int = Field(..., description="Guard index to explain")
    model_id: str = Field("xgboost", description="Model to explain")


@router.post("/explain")
async def explain_prediction(request_data: ExplainRequest, request: Request):
    """
    Generate SHAP-based explanation for a prediction
    
    Returns feature importance and natural language explanation
    """
    
    try:
        # Get model registry
        model_registry = request.app.state.model_registry
        
        # Initialize services
        feature_engineer = FeatureEngineer(
            encoders=model_registry.encoders,
            feature_names=model_registry.feature_names
        )
        
        explainability_service = ExplainabilityService(
            model_registry=model_registry,
            feature_engineer=feature_engineer
        )
        
        # Engineer features
        features = feature_engineer.engineer_from_input(request_data.input_features)
        
        # Generate explanation
        result = explainability_service.explain_prediction(
            features=features,
            guard_idx=request_data.guard_index,
            model_name=request_data.model_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.get("/feature-importance/{model_id}")
async def get_feature_importance(model_id: str, request: Request):
    """
    Get global feature importance for a model
    """
    
    try:
        model_registry = request.app.state.model_registry
        
        feature_engineer = FeatureEngineer(
            encoders=model_registry.encoders,
            feature_names=model_registry.feature_names
        )
        
        explainability_service = ExplainabilityService(
            model_registry=model_registry,
            feature_engineer=feature_engineer
        )
        
        importance = explainability_service.get_feature_importance(model_name=model_id)
        
        return {
            "success": True,
            "model": model_id,
            "feature_importance": importance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature importance failed: {str(e)}")
