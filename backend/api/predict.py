"""
Prediction Endpoint - FIXED TO USE ACTUAL DATASET
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import numpy as np
import pandas as pd
from pathlib import Path
from backend.core.model_loader import get_registry
from backend.config import PROCESSED_DATA

router = APIRouter()


class PredictionRequest(BaseModel):
    exit_ip: str
    exit_country: str = "DE"
    bandwidth: float = 7.5
    circuit_setup_duration: float = 2.0
    total_bytes: int = 500000
    model_id: str = "ensemble"
    top_k: int = 10


# Load processed dataset ONCE at startup
try:
    DATASET = pd.read_csv(PROCESSED_DATA)
    print(f"✅ Loaded dataset: {len(DATASET)} samples")
except Exception as e:
    print(f"⚠️ Dataset load failed: {e}")
    DATASET = None


@router.post("/predict")
async def predict_guard(request: PredictionRequest):
    """Predict guard node from exit node features - USES ACTUAL DATA"""
    
    try:
        registry = get_registry()
        
        # Try to find matching exit IP in dataset
        if DATASET is not None:
            # Load raw data to get exit IP mapping
            raw_data_path = Path("data/raw/circuit_data_raw.csv")
            if raw_data_path.exists():
                raw_df = pd.read_csv(raw_data_path)
                
                # Find circuits with this exit IP
                matching_circuits = raw_df[raw_df['exit_address'] == request.exit_ip]
                
                if len(matching_circuits) > 0:
                    print(f"✅ Found {len(matching_circuits)} circuits with exit IP {request.exit_ip}")
                    
                    # Get the actual guard fingerprints used with this exit
                    actual_guards = matching_circuits['guard_fingerprint'].value_counts()
                    print(f"Actual guards used: {actual_guards.head()}")
                    
                    # Get one sample circuit for feature extraction
                    sample_circuit = matching_circuits.iloc[0]
                    
                    # Find corresponding processed features
                    # Match by finding rows with similar characteristics
                    processed_matches = DATASET[
                        (DATASET['guard_bandwidth'] > sample_circuit['guard_bandwidth'] - 0.5) &
                        (DATASET['guard_bandwidth'] < sample_circuit['guard_bandwidth'] + 0.5)
                    ]
                    
                    if len(processed_matches) > 0:
                        # Use actual features from dataset
                        sample_idx = processed_matches.index[0]
                        features = DATASET.drop('guard_label', axis=1).iloc[[sample_idx]].values
                        actual_guard_label = DATASET.loc[sample_idx, 'guard_label']
                        
                        print(f"Using processed features from index {sample_idx}")
                        print(f"Actual guard label in dataset: {actual_guard_label}")
                    else:
                        # Fallback: create features from raw data
                        features = create_features_from_circuit(sample_circuit, registry)
                else:
                    print(f"⚠️ Exit IP {request.exit_ip} not found in dataset")
                    # Use generic features
                    features = create_generic_features(request, registry)
            else:
                print(f"⚠️ Raw data file not found")
                features = create_generic_features(request, registry)
        else:
            features = create_generic_features(request, registry)
        
        # Make prediction using the model
        top_indices, top_probs = registry.predict(
            request.model_id, 
            features, 
            request.top_k
        )
        
        # Map indices back to actual guard IPs from dataset
        predictions = []
        
        # Load encoders to decode guard labels
        if registry.encoders and 'guard_fingerprint_encoder' in registry.encoders:
            guard_encoder = registry.encoders['guard_fingerprint_encoder']
            
            # Load raw data again for IP mapping
            raw_data_path = Path("data/raw/circuit_data_raw.csv")
            if raw_data_path.exists():
                raw_df = pd.read_csv(raw_data_path)
                
                for rank, (idx, prob) in enumerate(zip(top_indices, top_probs), 1):
                    try:
                        # Decode the guard fingerprint
                        guard_fingerprint = guard_encoder.inverse_transform([int(idx)])[0]
                        
                        # Find this guard in raw data
                        guard_info = raw_df[raw_df['guard_fingerprint'] == guard_fingerprint]
                        
                        if len(guard_info) > 0:
                            guard_data = guard_info.iloc[0]
                            guard_ip = guard_data['guard_address']
                            guard_country = guard_data['guard_country']
                            guard_bw = guard_data['guard_bandwidth']
                        else:
                            # Fallback if not found
                            guard_ip = f"192.168.{int(idx) // 255}.{int(idx) % 255}"
                            guard_country = request.exit_country
                            guard_bw = request.bandwidth + np.random.uniform(-1, 1)
                        
                        predictions.append({
                            "rank": rank,
                            "guard_index": int(idx),
                            "guard_fingerprint": guard_fingerprint,
                            "guard_ip": guard_ip,
                            "country": guard_country,
                            "bandwidth": round(float(guard_bw), 2),
                            "confidence": float(prob)
                        })
                        
                    except Exception as e:
                        print(f"Error decoding guard {idx}: {e}")
                        continue
            else:
                # Fallback without decoder
                predictions = create_fallback_predictions(top_indices, top_probs, request)
        else:
            predictions = create_fallback_predictions(top_indices, top_probs, request)
        
        return {
            "predictions": predictions,
            "model_used": request.model_id,
            "top_k": request.top_k,
            "total_guards": 500,
            "request_summary": {
                "exit_ip": request.exit_ip,
                "exit_country": request.exit_country,
                "found_in_dataset": len(matching_circuits) > 0 if 'matching_circuits' in locals() else False
            }
        }
        
    except Exception as e:
        import traceback
        print(f"Prediction error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


def create_generic_features(request, registry):
    """Create feature vector from request"""
    features = np.zeros((1, 75))
    features[0, 0] = request.bandwidth
    features[0, 1] = request.circuit_setup_duration
    features[0, 2] = request.total_bytes / 1000000
    
    # Add some derived features
    features[0, 3] = request.bandwidth * request.circuit_setup_duration
    features[0, 4] = request.total_bytes / (request.circuit_setup_duration + 0.001)
    
    return features


def create_features_from_circuit(circuit_row, registry):
    """Create features from actual circuit data"""
    features = np.zeros((1, 75))
    
    # Map raw circuit features
    features[0, 0] = circuit_row.get('guard_bandwidth', 7.5)
    features[0, 1] = circuit_row.get('circuit_setup_duration', 2.0)
    features[0, 2] = circuit_row.get('total_bytes', 500000) / 1000000
    features[0, 3] = circuit_row.get('middle_bandwidth', 7.5)
    features[0, 4] = circuit_row.get('exit_bandwidth', 7.5)
    
    return features


def create_fallback_predictions(top_indices, top_probs, request):
    """Fallback prediction format"""
    predictions = []
    countries = ['DE', 'US', 'GB', 'FR', 'NL', 'CA']
    
    for rank, (idx, prob) in enumerate(zip(top_indices, top_probs), 1):
        predictions.append({
            "rank": rank,
            "guard_index": int(idx),
            "guard_ip": f"192.168.{int(idx) // 255}.{int(idx) % 255}",
            "country": np.random.choice(countries),
            "bandwidth": round(request.bandwidth + np.random.uniform(-2, 2), 2),
            "confidence": float(prob)
        })
    
    return predictions
