"""
Counterfactual Analysis Service
What-if scenario analysis with feature modifications
"""

import numpy as np
from typing import Dict, List, Any


class CounterfactualService:
    """Service for counterfactual analysis"""
    
    def __init__(self, prediction_service, feature_engineer):
        self.prediction_service = prediction_service
        self.feature_engineer = feature_engineer
    
    def analyze_counterfactual(self, original_input: Dict[str, Any], 
                               modified_features: Dict[str, Any],
                               model_name: str = "ensemble") -> Dict[str, Any]:
        """
        Analyze what-if scenario by modifying features
        
        Args:
            original_input: Original input data
            modified_features: Dictionary of features to modify
            model_name: Model to use for prediction
            
        Returns:
            Comparison of original vs modified predictions
        """
        
        # Get original prediction
        original_prediction = self.prediction_service.predict(
            original_input, 
            model_name=model_name, 
            top_k=10
        )
        
        # Create modified input
        modified_input = original_input.copy()
        modified_input.update(modified_features)
        
        # Get modified prediction
        modified_prediction = self.prediction_service.predict(
            modified_input,
            model_name=model_name,
            top_k=10
        )
        
        # Compare predictions
        comparison = self._compare_predictions(
            original_prediction['predictions'],
            modified_prediction['predictions']
        )
        
        # Analyze sensitivity
        sensitivity = self._analyze_sensitivity(
            original_prediction,
            modified_prediction,
            modified_features
        )
        
        return {
            "success": True,
            "original": original_prediction,
            "modified": modified_prediction,
            "comparison": comparison,
            "sensitivity": sensitivity,
            "modified_features": modified_features
        }
    
    def _compare_predictions(self, original: List[Dict], modified: List[Dict]) -> Dict[str, Any]:
        """Compare two prediction sets"""
        
        # Create index maps
        orig_map = {p['guard_index']: p for p in original}
        mod_map = {p['guard_index']: p for p in modified}
        
        # Track rank changes
        rank_changes = []
        
        for guard_idx in set(list(orig_map.keys()) + list(mod_map.keys())):
            orig_rank = orig_map[guard_idx]['rank'] if guard_idx in orig_map else None
            mod_rank = mod_map[guard_idx]['rank'] if guard_idx in mod_map else None
            
            orig_conf = orig_map[guard_idx]['confidence'] if guard_idx in orig_map else 0
            mod_conf = mod_map[guard_idx]['confidence'] if guard_idx in mod_map else 0
            
            if orig_rank is not None or mod_rank is not None:
                rank_changes.append({
                    "guard_index": guard_idx,
                    "original_rank": orig_rank,
                    "modified_rank": mod_rank,
                    "rank_change": (orig_rank - mod_rank) if (orig_rank and mod_rank) else None,
                    "confidence_change": mod_conf - orig_conf
                })
        
        # Sort by absolute confidence change
        rank_changes.sort(key=lambda x: abs(x['confidence_change']), reverse=True)
        
        return {
            "rank_changes": rank_changes[:10],
            "top_guard_changed": original[0]['guard_index'] != modified[0]['guard_index'],
            "average_confidence_change": np.mean([rc['confidence_change'] for rc in rank_changes if rc['confidence_change'] is not None])
        }
    
    def _analyze_sensitivity(self, original: Dict, modified: Dict, 
                            modified_features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how sensitive predictions are to feature changes"""
        
        sensitivity_scores = []
        
        for feature_name, new_value in modified_features.items():
            # Calculate impact
            confidence_delta = modified['predictions'][0]['confidence'] - original['predictions'][0]['confidence']
            
            sensitivity_scores.append({
                "feature": feature_name,
                "original_value": "N/A",  # Would need to track original
                "new_value": new_value,
                "confidence_impact": confidence_delta,
                "sensitivity": "high" if abs(confidence_delta) > 5 else "medium" if abs(confidence_delta) > 2 else "low"
            })
        
        return {
            "feature_sensitivities": sensitivity_scores,
            "overall_impact": sum([abs(s['confidence_impact']) for s in sensitivity_scores])
        }
    
    def get_critical_thresholds(self, input_data: Dict[str, Any], 
                                feature_name: str,
                                model_name: str = "ensemble") -> Dict[str, Any]:
        """
        Find critical threshold where prediction changes
        (Binary search for threshold values)
        """
        
        # This is a simplified version - full
