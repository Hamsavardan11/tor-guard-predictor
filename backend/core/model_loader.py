"""
Model Loader - Load and manage ML models
"""

import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
import joblib
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import (
    XGBOOST_MODEL, LIGHTGBM_MODEL, CATBOOST_MODEL, 
    ENSEMBLE_MODEL, FEATURE_NAMES, LABEL_ENCODERS
)


class ModelRegistry:
    """Registry for all ML models"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.feature_names = None
        self.encoders = None
        self.num_classes = 500
        
    def load_all_models(self):
        """Load all trained models"""
        print("📦 Loading ML models...")
        
        # Load XGBoost
        try:
            print(f"  Loading XGBoost from {XGBOOST_MODEL}")
            xgb_model = xgb.Booster()
            xgb_model.load_model(str(XGBOOST_MODEL))
            self.models['xgboost'] = xgb_model
            print(f"  ✅ XGBoost loaded")
        except Exception as e:
            print(f"  ⚠️ XGBoost load failed: {e}")
            
        # Load LightGBM
        try:
            print(f"  Loading LightGBM from {LIGHTGBM_MODEL}")
            lgb_model = joblib.load(LIGHTGBM_MODEL)
            self.models['lightgbm'] = lgb_model
            print(f"  ✅ LightGBM loaded")
        except Exception as e:
            print(f"  ⚠️ LightGBM load failed: {e}")
            
        # Load CatBoost
        try:
            print(f"  Loading CatBoost from {CATBOOST_MODEL}")
            cat_model = CatBoostClassifier()
            cat_model.load_model(str(CATBOOST_MODEL))
            self.models['catboost'] = cat_model
            print(f"  ✅ CatBoost loaded")
        except Exception as e:
            print(f"  ⚠️ CatBoost load failed: {e}")
            
        # Load Ensemble metadata
        try:
            print(f"  Loading Ensemble from {ENSEMBLE_MODEL}")
            ensemble_data = joblib.load(ENSEMBLE_MODEL)
            self.models['ensemble'] = ensemble_data
            print(f"  ✅ Ensemble loaded")
        except Exception as e:
            print(f"  ⚠️ Ensemble load failed: {e}")
            
        # Load feature names
        try:
            with open(FEATURE_NAMES, 'r') as f:
                self.feature_names = json.load(f)
            print(f"  ✅ Feature names loaded: {len(self.feature_names)} features")
        except Exception as e:
            print(f"  ⚠️ Feature names load failed: {e}")
            
        # Load encoders
        try:
            self.encoders = joblib.load(LABEL_ENCODERS)
            print(f"  ✅ Label encoders loaded")
        except Exception as e:
            print(f"  ⚠️ Encoders load failed: {e}")
            
        if not self.models:
            raise RuntimeError("❌ No models loaded successfully!")
            
        print(f"✅ All models loaded successfully!")
        
    def get_model(self, model_id: str):
        """Get a specific model by ID"""
        return self.models.get(model_id)
        
    def list_models(self) -> list:
        """List all available models"""
        return list(self.models.keys())
        
    def predict(self, model_id: str, features: np.ndarray, top_k: int = 10):
        """Make prediction using specified model"""
        
        if model_id not in self.models:
            raise ValueError(f"Model '{model_id}' not found. Available: {self.list_models()}")
            
        model = self.models[model_id]
        
        # Handle different model types
        if model_id == 'xgboost':
            dmatrix = xgb.DMatrix(features, feature_names=self.feature_names)
            proba = model.predict(dmatrix)
            
        elif model_id == 'lightgbm':
            proba = model.predict_proba(features)
            
        elif model_id == 'catboost':
            proba = model.predict_proba(features)
            
        elif model_id == 'ensemble':
            # Ensemble: average predictions from all models
            xgb_model = self.models.get('xgboost')
            lgb_model = self.models.get('lightgbm')
            cat_model = self.models.get('catboost')
            
            probas = []
            
            if xgb_model:
                dmatrix = xgb.DMatrix(features, feature_names=self.feature_names)
                probas.append(xgb_model.predict(dmatrix) * 0.4)
                
            if lgb_model:
                probas.append(lgb_model.predict_proba(features) * 0.3)
                
            if cat_model:
                probas.append(cat_model.predict_proba(features) * 0.3)
                
            if not probas:
                raise RuntimeError("No models available for ensemble")
                
            proba = np.sum(probas, axis=0)
        else:
            raise ValueError(f"Unknown model type: {model_id}")
            
        # Get top-k predictions
        top_k_indices = np.argsort(proba[0])[-top_k:][::-1]
        top_k_probs = proba[0][top_k_indices]
        
        # Normalize to percentages
        total_prob = np.sum(top_k_probs)
        if total_prob > 0:
            top_k_probs = (top_k_probs / total_prob) * 100
            
        return top_k_indices, top_k_probs
        
    def encode_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """Encode raw input into feature vector"""
        
        # This is a simplified version - you'd implement full feature engineering here
        # For now, create a basic feature vector
        
        features = np.zeros((1, len(self.feature_names)))
        
        # Extract basic features (simplified)
        features[0, 0] = raw_data.get('bandwidth', 7.5)
        features[0, 1] = raw_data.get('circuit_setup_duration', 2.0)
        features[0, 2] = raw_data.get('total_bytes', 500000)
        
        # Encode country if encoders available
        if self.encoders and 'exit_country_encoder' in self.encoders:
            try:
                country_encoded = self.encoders['exit_country_encoder'].transform([raw_data.get('exit_country', 'US')])[0]
                features[0, 3] = country_encoded
            except:
                features[0, 3] = 0
                
        return features


# Global registry instance
registry = ModelRegistry()


def get_registry() -> ModelRegistry:
    """Get the global model registry"""
    return registry
