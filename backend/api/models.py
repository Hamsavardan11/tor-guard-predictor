"""
Models management endpoint
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/models")
async def list_models(request: Request):
    """
    List all available models
    
    Returns metadata about each loaded model
    """
    
    model_registry = request.app.state.model_registry
    
    models_info = []
    for model_name in model_registry.list_models():
        models_info.append({
            "id": model_name,
            "name": model_name.upper(),
            "description": f"{model_name.capitalize()} model for guard prediction",
            "status": "loaded",
            "recommended": model_name == "ensemble"
        })
    
    return {
        "success": True,
        "models": models_info,
        "total": len(models_info),
        "default_model": "ensemble"
    }
