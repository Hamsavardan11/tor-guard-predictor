"""
FastAPI Main Application - FIXED VERSION
TOR Guard Node Predictor - TN Police Hackathon 2025
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from backend.core.model_loader import get_registry
from backend.api import predict, health, explain, counterfactual, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting TOR Guard Predictor API...")
    print("📦 Loading ML models...")
    try:
        registry = get_registry()
        registry.load_all_models()
        print("✅ All models loaded successfully!")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        raise
    
    yield
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="TOR Guard Node Predictor API",
    description="ML-based TOR guard node prediction for Tamil Nadu Police",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration - ALLOW ALL ORIGINS FOR DEVELOPMENT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(explain.router, tags=["Explainability"])
app.include_router(counterfactual.router, tags=["Counterfactual"])
app.include_router(models.router, tags=["Models"])


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
