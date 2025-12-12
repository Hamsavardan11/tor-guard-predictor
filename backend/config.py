"""
Backend Configuration
"""

from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = False
API_WORKERS = 1

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

# Model Paths
MODELS_DIR = PROJECT_ROOT / "models"
XGBOOST_MODEL = MODELS_DIR / "xgboost" / "xgboost_v1.json"
LIGHTGBM_MODEL = MODELS_DIR / "lightgbm" / "lightgbm_v1.pkl"
CATBOOST_MODEL = MODELS_DIR / "catboost" / "catboost_v1.cbm"
ENSEMBLE_MODEL = MODELS_DIR / "ensemble" / "ensemble_v1.pkl"
SHAP_EXPLAINER = MODELS_DIR / "shap" / "shap_explainer_xgboost.pkl"

# Data Paths
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA = DATA_DIR / "processed" / "circuits_engineered_75_features.csv"
ENCODERS_DIR = MODELS_DIR / "encoders"
LABEL_ENCODERS = ENCODERS_DIR / "label_encoders.pkl"
FEATURE_NAMES = ENCODERS_DIR / "feature_names.json"

# Model Configuration
DEFAULT_MODEL = "ensemble"
DEFAULT_TOP_K = 10
MAX_TOP_K = 50

# Feature Engineering Config
NUM_FEATURES = 75
NUM_CLASSES = 500

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Application Metadata
APP_TITLE = "TOR Guard Node Predictor API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "ML-based TOR guard node prediction for Tamil Nadu Police Cyber Crime Wing"
