"""
Feature Engineering Pipeline
Transforms raw input into 75 features for ML models
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List


class FeatureEngineer:
    """Feature engineering for circuit data"""
    
    def __init__(self, encoders: Dict[str, Any], feature_names: List[str]):
        self.encoders = encoders
        self.feature_names = feature_names
    
    def engineer_from_input(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Transform API input into 75-feature vector
        
        Args:
            input_data: Dictionary with keys:
                - exit_fingerprint (optional)
                - exit_ip (optional)
                - exit_country
                - timestamp
                - bandwidth (optional)
                - guard_fingerprint (for counterfactual)
                - middle_fingerprint (for counterfactual)
                
        Returns:
            np.ndarray: Feature vector of shape (75,)
        """
        
        features = {}
        
        # Extract base features
        exit_country = input_data.get('exit_country', 'DE')
        bandwidth = input_data.get('bandwidth', 7.5)
        timestamp = input_data.get('timestamp', datetime.now().isoformat())
        
        # Parse timestamp
        try:
            dt = pd.to_datetime(timestamp)
            hour_of_day = dt.hour
            day_of_week = dt.dayofweek
        except:
            hour_of_day = 14
            day_of_week = 3
        
        # [1-7] Bandwidth features (using provided or estimated values)
        guard_bw = input_data.get('guard_bandwidth', bandwidth * 1.2)
        middle_bw = input_data.get('middle_bandwidth', bandwidth * 1.1)
        exit_bw = bandwidth
        
        features['guard_bandwidth'] = guard_bw
        features['middle_bandwidth'] = middle_bw
        features['exit_bandwidth'] = exit_bw
        features['guard_to_middle_bw_ratio'] = guard_bw / (middle_bw + 0.001)
        features['guard_to_exit_bw_ratio'] = guard_bw / (exit_bw + 0.001)
        features['middle_to_exit_bw_ratio'] = middle_bw / (exit_bw + 0.001)
        features['total_circuit_bandwidth'] = guard_bw + middle_bw + exit_bw
        features['min_bandwidth'] = min(guard_bw, middle_bw, exit_bw)
        features['max_bandwidth'] = max(guard_bw, middle_bw, exit_bw)
        features['std_bandwidth'] = np.std([guard_bw, middle_bw, exit_bw])
        
        # [8-12] Geographic features
        guard_country = input_data.get('guard_country', 'DE')
        middle_country = input_data.get('middle_country', 'NL')
        
        features['same_country_guard_middle'] = int(guard_country == middle_country)
        features['same_country_guard_exit'] = int(guard_country == exit_country)
        features['same_country_middle_exit'] = int(middle_country == exit_country)
        features['country_diversity_score'] = len(set([guard_country, middle_country, exit_country]))
        
        # [13-20] Historical aggregate features (estimated from typical patterns)
        # In production, these would come from database lookups
        features['guard_usage_frequency'] = 0.5  # Normalized frequency
        features['middle_usage_frequency'] = 0.5
        features['exit_usage_frequency'] = 0.5
        features['guard_exit_cooccurrence_freq'] = 0.1
        features['guard_avg_bandwidth_all_circuits'] = guard_bw * 1.05
        features['guard_country_preference_score'] = 0.3
        features['middle_avg_bandwidth'] = middle_bw * 1.02
        features['exit_avg_bandwidth'] = exit_bw * 0.98
        
        # [21-25] Encoded categorical features
        # Encode countries
        if 'guard_country_encoder' in self.encoders:
            try:
                features['guard_country_encoded'] = self.encoders['guard_country_encoder'].transform([guard_country])[0]
            except:
                features['guard_country_encoded'] = 0
        else:
            features['guard_country_encoded'] = hash(guard_country) % 50
        
        if 'middle_country_encoder' in self.encoders:
            try:
                features['middle_country_encoded'] = self.encoders['middle_country_encoder'].transform([middle_country])[0]
            except:
                features['middle_country_encoded'] = 0
        else:
            features['middle_country_encoded'] = hash(middle_country) % 50
        
        if 'exit_country_encoder' in self.encoders:
            try:
                features['exit_country_encoded'] = self.encoders['exit_country_encoder'].transform([exit_country])[0]
            except:
                features['exit_country_encoded'] = 0
        else:
            features['exit_country_encoded'] = hash(exit_country) % 50
        
        # Fingerprint encoding (if provided)
        guard_fp = input_data.get('guard_fingerprint', 'UNKNOWN')
        if 'guard_fingerprint_encoder' in self.encoders:
            try:
                features['guard_fingerprint_encoded'] = self.encoders['guard_fingerprint_encoder'].transform([guard_fp])[0]
            except:
                features['guard_fingerprint_encoded'] = 0
        else:
            features['guard_fingerprint_encoded'] = hash(guard_fp) % 500
        
        features['exit_fingerprint_encoded'] = hash(input_data.get('exit_fingerprint', 'UNKNOWN')) % 500
        
        # [26-27] Interaction features
        circuit_setup_duration = input_data.get('circuit_setup_duration', 2.0)
        total_bytes = input_data.get('total_bytes', 500000)
        
        features['bandwidth_setup_time_interaction'] = bandwidth * circuit_setup_duration
        features['total_bandwidth_bytes_interaction'] = (guard_bw + middle_bw + exit_bw) * total_bytes / 1000000
        
        # [28-37] Temporal features (NEW from Chutney - simulated for now)
        features['circuit_build_latency_ms'] = circuit_setup_duration * 1000
        features['hour_of_day'] = hour_of_day
        features['day_of_week'] = day_of_week
        features['circuit_lifetime_sec'] = input_data.get('circuit_lifetime', 60.0)
        features['time_since_last_circuit'] = 5.0  # Seconds
        features['cell_count_actual'] = total_bytes // 512
        features['cell_interarrival_mean_ms'] = 10.5
        features['stream_setup_latency_ms'] = 150.0
        features['idle_time_ratio'] = 0.3
        features['closure_reason_encoded'] = 0  # NORMAL
        
        # [38-45] Traffic features (NEW)
        features['bytes_sent_guard_to_middle'] = total_bytes * 0.48
        features['bytes_recv_middle_to_guard'] = total_bytes * 0.48
        features['bytes_sent_asymmetry_ratio'] = 1.2
        features['bandwidth_utilization'] = 0.65
        features['traffic_burst_score'] = 0.8
        features['congestion_indicator'] = 0.15
        features['stream_count'] = input_data.get('stream_count', 3)
        features['stream_multiplexing_count'] = 3
        
        # [46-52] Network topology features (NEW - simulated)
        features['guard_as_number'] = hash(guard_country) % 10000
        features['exit_as_number'] = hash(exit_country) % 10000
        features['same_as_flag'] = 0
        features['as_path_length'] = 3
        features['relay_family_size'] = 1
        features['exit_policy_match_score'] = 0.9
        features['guard_stability_index'] = guard_bw * 0.95
        
        # [53-75] Additional padding features (to reach 75 total)
        for i in range(53, 76):
            if f'feature_{i}' not in features:
                features[f'feature_{i}'] = 0.0
        
        # Convert to ordered numpy array matching feature_names
        feature_vector = np.zeros(75)
        for i, name in enumerate(self.feature_names):
            if name in features:
                feature_vector[i] = features[name]
        
        return feature_vector
    
    def engineer_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw circuit dataframe
        (Used during training)
        """
        # This will be implemented in the training script
        pass
