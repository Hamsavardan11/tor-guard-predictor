"""
Counterfactual analysis endpoint
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from backend.core.feature_engineering import FeatureEngineer
from backend.core.prediction_service import PredictionService
from backend.core.counterfactual_service import CounterfactualService

router = APIRouter()


class CounterfactualRequest(BaseModel):
    """Request model for counterfactual analysis"""
    original_input: Dict[str, Any] = Field(..., description="Original input features")
    modified_features: Dict[str, Any] = Field(..., description="Features to modify")
    model_id: str = Field("ensemble", description="Model to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_input": {
                    "exit_country": "DE",
                    "bandwidth": 7.5
                },
                "modified_features": {
                    "bandwidth": 10.0,
                    "exit_country": "US"
                },
                "model_id": "ensemble"
            }
        }


@router.post("/counterfactual")
async def analyze_counterfactual(request_data: CounterfactualRequest, request: Request):
    """
    Analyze what-if scenarios by modifying input features
    
    Returns comparison of original vs modified predictions
    """
    
    try:
        # Get model registry
        model_registry = request.app.state.model_registry
        
        # Initialize services
        feature_engineer = FeatureEngineer(
            encoders=model_registry.encoders,
            feature_names=model_registry.feature_names
        )
        
        prediction_service = PredictionService(
            model_registry=model_registry,
            feature_engineer=feature_engineer
        )
        
        counterfactual_service = CounterfactualService(
            prediction_service=prediction_service,
            feature_engineer=feature_engineer
        )
        
        # Analyze counterfactual
        result = counterfactual_service.analyze_counterfactual(
            original_input=request_data.original_input,
            modified_features=request_data.modified_features,
            model_name=request_data.model_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Counterfactual analysis failed: {str(e)}")
