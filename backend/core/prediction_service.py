"""
Prediction Service
Handles ML inference and result formatting
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
import xgboost as xgb


class PredictionService:
    """Service for making guard node predictions"""
    
    def __init__(self, model_registry, feature_engineer):
        self.model_registry = model_registry
        self.feature_engineer = feature_engineer
    
    def predict(self, input_data: Dict[str, Any], model_name: str = "ensemble", top_k: int = 10) -> Dict[str, Any]:
        """
        Make prediction for guard node
        
        Args:
            input_data: Input features
            model_name: Which model to use
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with predictions and metadata
        """
        
        # Engineer features
        features = self.feature_engineer.engineer_from_input(input_data)
        features_2d = features.reshape(1, -1)
        
        # Get model
        model = self.model_registry.get_model(model_name)
        
        # Predict probabilities
        if model_name == 'xgboost':
            # XGBoost Booster requires DMatrix
            dmatrix = xgb.DMatrix(features_2d, feature_names=self.feature_engineer.feature_names)
            probs = model.predict(dmatrix)[0]
        else:
            # sklearn-like interface
            probs = model.predict_proba(features_2d)[0]
        
        # Get top-k indices
        top_indices = np.argsort(probs)[-top_k:][::-1]
        
        # Format predictions
        predictions = []
        for rank, idx in enumerate(top_indices, 1):
            predictions.append({
                "rank": rank,
                "guard_index": int(idx),
                "guard_fingerprint": f"Guard_{idx:03d}",  # Placeholder - will be mapped from training
                "guard_ip": self._get_guard_ip(idx),
                "country": self._get_guard_country(idx),
                "confidence": float(probs[idx] * 100),  # Convert to percentage
                "probability": float(probs[idx]),
                "bandwidth": self._get_guard_bandwidth(idx)
            })
        
        return {
            "success": True,
            "predictions": predictions,
            "model_used": model_name,
            "total_guards": len(probs),
            "top_k": top_k
        }
    
    def _get_guard_ip(self, guard_idx: int) -> str:
        """Map guard index to IP (placeholder)"""
        # In production, this would lookup from database
        return f"192.168.{guard_idx // 255}.{guard_idx % 255}"
    
    def _get_guard_country(self, guard_idx: int) -> str:
        """Map guard index to country (placeholder)"""
        countries = ['DE', 'US', 'GB', 'FR', 'NL', 'CA', 'SE', 'CH', 'AT', 'JP']
        return countries[guard_idx % len(countries)]
    
    def _get_guard_bandwidth(self, guard_idx: int) -> float:
        """Map guard index to bandwidth (placeholder)"""
        # Simulated bandwidth between 1-10 MB/s
        np.random.seed(guard_idx)
        return round(np.random.uniform(1.0, 10.0), 2)
