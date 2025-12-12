"""
Explainability Service
SHAP-based explanations for predictions
"""

import numpy as np
import shap
from typing import Dict, List, Any


class ExplainabilityService:
    """Service for generating SHAP explanations"""
    
    def __init__(self, model_registry, feature_engineer):
        self.model_registry = model_registry
        self.feature_engineer = feature_engineer
        self.shap_explainer = model_registry.shap_explainer
    
    def explain_prediction(self, features: np.ndarray, guard_idx: int, model_name: str = "xgboost") -> Dict[str, Any]:
        """
        Generate SHAP explanation for a specific prediction
        
        Args:
            features: Feature vector (75,)
            guard_idx: Index of predicted guard
            model_name: Model to explain
            
        Returns:
            Dictionary with SHAP values and natural language explanation
        """
        
        # Get SHAP values
        if self.shap_explainer is None:
            # Create explainer on-the-fly if not pre-computed
            model = self.model_registry.get_model(model_name)
            self.shap_explainer = shap.TreeExplainer(model)
        
        shap_values = self.shap_explainer.shap_values(features.reshape(1, -1))
        
        # Handle multi-class output (shap_values is list of arrays)
        if isinstance(shap_values, list):
            # Get SHAP values for the predicted class
            shap_values_guard = shap_values[guard_idx][0]
        else:
            shap_values_guard = shap_values[0]
        
        # Get feature names
        feature_names = self.feature_engineer.feature_names
        
        # Get top contributing features
        top_features = self._get_top_features(shap_values_guard, features, feature_names, top_n=10)
        
        # Generate natural language explanation
        explanation_text = self._generate_explanation(top_features, guard_idx)
        
        return {
            "success": True,
            "guard_index": guard_idx,
            "shap_values": shap_values_guard.tolist(),
            "feature_names": feature_names,
            "top_features": top_features,
            "explanation": explanation_text,
            "base_value": float(self.shap_explainer.expected_value) if hasattr(self.shap_explainer, 'expected_value') else 0.0
        }
    
    def _get_top_features(self, shap_values: np.ndarray, features: np.ndarray, 
                         feature_names: List[str], top_n: int = 10) -> List[Dict]:
        """Get top N features by absolute SHAP value"""
        
        # Get absolute SHAP values
        abs_shap = np.abs(shap_values)
        
        # Get top indices
        top_indices = np.argsort(abs_shap)[-top_n:][::-1]
        
        top_features = []
        for idx in top_indices:
            top_features.append({
                "feature_name": feature_names[idx],
                "feature_value": float(features[idx]),
                "shap_value": float(shap_values[idx]),
                "contribution": "positive" if shap_values[idx] > 0 else "negative",
                "impact_percentage": float(abs_shap[idx] / abs_shap.sum() * 100)
            })
        
        return top_features
    
    def _generate_explanation(self, top_features: List[Dict], guard_idx: int) -> str:
        """Generate human-readable explanation"""
        
        explanation = f"This guard (Guard_{guard_idx:03d}) was predicted because:\n\n"
        
        for i, feat in enumerate(top_features[:5], 1):
            name = feat['feature_name']
            value = feat['feature_value']
            impact = feat['impact_percentage']
            contribution = feat['contribution']
            
            symbol = "✅" if contribution == "positive" else "⚠️"
            
            # Format feature name for readability
            readable_name = name.replace('_', ' ').title()
            
            explanation += f"{symbol} {readable_name}: {value:.2f} "
            explanation += f"({'+'if contribution == 'positive' else '-'}{impact:.1f}% impact)\n"
        
        return explanation
    
    def get_feature_importance(self, model_name: str = "xgboost") -> List[Dict]:
        """Get global feature importance for a model"""
        
        model = self.model_registry.get_model(model_name)
        feature_names = self.feature_engineer.feature_names
        
        # Get feature importance (varies by model type)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'get_score'):
            # XGBoost Booster
            importance_dict = model.get_score(importance_type='gain')
            importances = np.array([importance_dict.get(f'f{i}', 0) for i in range(len(feature_names))])
        else:
            importances = np.zeros(len(feature_names))
        
        # Normalize
        if importances.sum() > 0:
            importances = importances / importances.sum() * 100
        
        # Sort and format
        sorted_indices = np.argsort(importances)[::-1]
        
        feature_importance = []
        for idx in sorted_indices[:20]:  # Top 20 features
            feature_importance.append({
                "feature_name": feature_names[idx],
                "importance": float(importances[idx]),
                "rank": len(feature_importance) + 1
            })
        
        return feature_importance
