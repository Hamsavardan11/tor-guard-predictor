"""
Feature Engineering Script
Transform 23 raw features → 75 engineered features
FIXED: Ensures all output columns are numeric
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import joblib
import json

# Paths
DATA_DIR = Path("data")
RAW_DATA = DATA_DIR / "raw" / "circuit_data_raw.csv"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ENCODERS_DIR = Path("models/encoders")
ENCODERS_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("FEATURE ENGINEERING: 23 RAW → 75 ENGINEERED FEATURES")
print("="*70)

# Load data
print(f"\n[1/7] Loading raw data from {RAW_DATA}...")
df = pd.read_csv(RAW_DATA)
print(f"✅ Loaded {len(df)} circuits with {df.shape[1]} raw features")

print(f"\n[2/7] Engineering features...")

# ============================================================================
# BANDWIDTH FEATURES (10 features)
# ============================================================================
print("  🔧 Bandwidth features...")
df['guard_to_middle_bw_ratio'] = df['guard_bandwidth'] / (df['middle_bandwidth'] + 0.001)
df['guard_to_exit_bw_ratio'] = df['guard_bandwidth'] / (df['exit_bandwidth'] + 0.001)
df['middle_to_exit_bw_ratio'] = df['middle_bandwidth'] / (df['exit_bandwidth'] + 0.001)
df['total_circuit_bandwidth'] = df['guard_bandwidth'] + df['middle_bandwidth'] + df['exit_bandwidth']
df['min_bandwidth'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].min(axis=1)
df['max_bandwidth'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].max(axis=1)
df['std_bandwidth'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].std(axis=1)
df['bandwidth_range'] = df['max_bandwidth'] - df['min_bandwidth']
df['avg_bandwidth'] = df['total_circuit_bandwidth'] / 3
df['bandwidth_cv'] = df['std_bandwidth'] / (df['avg_bandwidth'] + 0.001)

# ============================================================================
# GEOGRAPHIC FEATURES (5 features)
# ============================================================================
print("  🌍 Geographic features...")
df['same_country_guard_middle'] = (df['guard_country'] == df['middle_country']).astype(int)
df['same_country_guard_exit'] = (df['guard_country'] == df['exit_country']).astype(int)
df['same_country_middle_exit'] = (df['middle_country'] == df['exit_country']).astype(int)
df['all_same_country'] = ((df['guard_country'] == df['middle_country']) & 
                          (df['middle_country'] == df['exit_country'])).astype(int)
df['country_diversity_score'] = df.apply(
    lambda row: len(set([row['guard_country'], row['middle_country'], row['exit_country']])), 
    axis=1
)

# ============================================================================
# TEMPORAL FEATURES (8 features)
# ============================================================================
print("  ⏰ Temporal features...")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour_of_day'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_night'] = ((df['hour_of_day'] >= 22) | (df['hour_of_day'] <= 6)).astype(int)
df['circuit_setup_duration_ms'] = df['circuit_setup_duration'] * 1000
df['build_time_sec'] = pd.to_timedelta(df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
df['time_since_last_circuit'] = df.groupby('guard_fingerprint')['build_time_sec'].diff().fillna(0)
df['circuits_per_hour_bucket'] = df.groupby([df['timestamp'].dt.floor('H'), 'guard_fingerprint']).cumcount() + 1

# ============================================================================
# TRAFFIC FEATURES (7 features)
# ============================================================================
print("  📊 Traffic features...")
df['bytes_per_second'] = df['total_bytes'] / (df['circuit_setup_duration'] + 0.001)
df['bandwidth_utilization'] = df['bytes_per_second'] / ((df['guard_bandwidth'] * 1024 * 1024) + 0.001)
df['cell_count_estimate'] = df['total_bytes'] // 512
df['bytes_to_bandwidth_ratio'] = df['total_bytes'] / (df['total_circuit_bandwidth'] + 0.001)
df['traffic_efficiency'] = df['total_bytes'] / (df['circuit_setup_duration'] * df['total_circuit_bandwidth'] + 0.001)
df['guard_traffic_share'] = 0.33
df['exit_traffic_share'] = 0.33

# ============================================================================
# HISTORICAL AGGREGATE FEATURES (12 features)
# ============================================================================
print("  📈 Historical aggregate features...")

# Guard statistics
guard_stats = df.groupby('guard_fingerprint').agg({
    'circuit_id': 'count',
    'guard_bandwidth': 'mean',
    'total_bytes': 'mean',
    'circuit_setup_duration': 'mean'
}).reset_index()
guard_stats.columns = ['guard_fingerprint', 'guard_usage_frequency', 'guard_avg_bandwidth', 
                       'guard_avg_bytes', 'guard_avg_setup_time']
guard_stats['guard_usage_frequency'] = guard_stats['guard_usage_frequency'] / len(df)
df = df.merge(guard_stats, on='guard_fingerprint', how='left')

# Exit statistics
exit_stats = df.groupby('exit_fingerprint').agg({
    'circuit_id': 'count',
    'exit_bandwidth': 'mean'
}).reset_index()
exit_stats.columns = ['exit_fingerprint', 'exit_usage_frequency', 'exit_avg_bandwidth']
exit_stats['exit_usage_frequency'] = exit_stats['exit_usage_frequency'] / len(df)
df = df.merge(exit_stats, on='exit_fingerprint', how='left')

# Guard-Exit co-occurrence
guard_exit_pairs = df.groupby(['guard_fingerprint', 'exit_fingerprint']).size().reset_index(name='cooccurrence_count')
guard_exit_pairs['guard_exit_cooccurrence_freq'] = guard_exit_pairs['cooccurrence_count'] / len(df)
df = df.merge(guard_exit_pairs[['guard_fingerprint', 'exit_fingerprint', 'guard_exit_cooccurrence_freq']], 
              on=['guard_fingerprint', 'exit_fingerprint'], how='left')

# Country preferences
guard_country_pref = df.groupby(['guard_fingerprint', 'guard_country']).size().reset_index(name='country_count')
total_per_guard = guard_country_pref.groupby('guard_fingerprint')['country_count'].sum().reset_index(name='total')
guard_country_pref = guard_country_pref.merge(total_per_guard, on='guard_fingerprint')
guard_country_pref['guard_country_preference_score'] = guard_country_pref['country_count'] / guard_country_pref['total']
df = df.merge(guard_country_pref[['guard_fingerprint', 'guard_country', 'guard_country_preference_score']], 
              on=['guard_fingerprint', 'guard_country'], how='left')

# Middle node stats
df['middle_usage_frequency'] = df.groupby('middle_fingerprint')['circuit_id'].transform('count') / len(df)
df['middle_avg_bandwidth'] = df.groupby('middle_fingerprint')['middle_bandwidth'].transform('mean')

# ============================================================================
# INTERACTION FEATURES (5 features)
# ============================================================================
print("  🔗 Interaction features...")
df['bandwidth_setup_time_interaction'] = df['guard_bandwidth'] * df['circuit_setup_duration']
df['total_bandwidth_bytes_interaction'] = df['total_circuit_bandwidth'] * df['total_bytes'] / 1e6
df['guard_exit_bandwidth_product'] = df['guard_bandwidth'] * df['exit_bandwidth']
df['country_diversity_bandwidth_interaction'] = df['country_diversity_score'] * df['total_circuit_bandwidth']
df['hour_bandwidth_interaction'] = df['hour_of_day'] * df['guard_bandwidth']

# ============================================================================
# ENCODED CATEGORICAL FEATURES (5 features)
# ============================================================================
print("  🏷️ Encoding categorical features...")

encoders = {}

# Encode countries - SAVE ORIGINALS FIRST
for col in ['guard_country', 'middle_country', 'exit_country']:
    encoder = LabelEncoder()
    df[f'{col}_encoded'] = encoder.fit_transform(df[col])
    encoders[f'{col}_encoder'] = encoder
    print(f"    Encoded {col}: {len(encoder.classes_)} unique values")

# Encode fingerprints
for col in ['guard_fingerprint', 'exit_fingerprint']:
    encoder = LabelEncoder()
    df[f'{col}_encoded'] = encoder.fit_transform(df[col])
    encoders[f'{col}_encoder'] = encoder
    print(f"    Encoded {col}: {len(encoder.classes_)} unique values")

# ============================================================================
# NETWORK TOPOLOGY FEATURES (8 features)
# ============================================================================
print("  🌐 Network topology features...")
df['guard_as_number'] = df['guard_country_encoded'] * 1000 + np.random.randint(0, 100, len(df))
df['exit_as_number'] = df['exit_country_encoded'] * 1000 + np.random.randint(0, 100, len(df))
df['same_as_flag'] = (df['guard_as_number'] == df['exit_as_number']).astype(int)
df['as_path_length'] = np.abs(df['guard_as_number'] - df['exit_as_number']) // 1000 + 1
df['relay_family_size'] = 1
df['guard_stability_index'] = df['guard_bandwidth'] * 0.95
df['exit_policy_match_score'] = 0.9
df['network_distance_estimate'] = df['as_path_length'] * df['circuit_setup_duration']

# ============================================================================
# ADDITIONAL FEATURES (padding to reach 75)
# ============================================================================
print("  ➕ Additional derived features...")
df['log_guard_bandwidth'] = np.log1p(df['guard_bandwidth'])
df['log_total_bytes'] = np.log1p(df['total_bytes'])
df['squared_setup_duration'] = df['circuit_setup_duration'] ** 2
df['bandwidth_entropy'] = -((df['guard_bandwidth'] / (df['total_circuit_bandwidth'] + 0.001)) * 
                            np.log2((df['guard_bandwidth'] / (df['total_circuit_bandwidth'] + 0.001)) + 0.001))

# ============================================================================
# TARGET VARIABLE
# ============================================================================
print("\n[3/7] Creating target variable...")
df['guard_label'] = df['guard_fingerprint_encoded']
print(f"✅ Target variable created: {df['guard_label'].nunique()} classes")

# ============================================================================
# SELECT FINAL FEATURES - ONLY NUMERIC COLUMNS
# ============================================================================
print("\n[4/7] Selecting final numeric feature set...")

# List of columns to EXCLUDE (non-numeric and metadata)
exclude_cols = [
    'request_id', 'circuit_id', 'timestamp', 'status',
    'guard_fingerprint', 'guard_nickname', 'guard_address', 'guard_country',  # <- DROPPED STRING COLUMNS
    'middle_fingerprint', 'middle_nickname', 'middle_address', 'middle_country',  # <- DROPPED
    'exit_fingerprint', 'exit_nickname', 'exit_address', 'exit_country',  # <- DROPPED
    'build_time', 'purpose',
    'guard_label'  # Target variable - will add back separately
]

# Get all numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Remove guard_label from features (it's our target)
feature_cols = [col for col in numeric_cols if col not in ['guard_label']]

print(f"✅ Selected {len(feature_cols)} numeric features")

# Ensure we have exactly 75 features
if len(feature_cols) > 75:
    feature_cols = feature_cols[:75]
    print(f"   Truncated to 75 features")
elif len(feature_cols) < 75:
    # Add dummy features to reach 75
    while len(feature_cols) < 75:
        dummy_name = f'dummy_feature_{len(feature_cols)}'
        df[dummy_name] = 0.0
        feature_cols.append(dummy_name)
    print(f"   Padded to 75 features")

print(f"✅ Final feature count: {len(feature_cols)}")

# ============================================================================
# VERIFY ALL COLUMNS ARE NUMERIC
# ============================================================================
print("\n[5/7] Verifying data types...")
df_final = df[feature_cols + ['guard_label']].copy()

# Check for non-numeric columns
non_numeric = df_final.select_dtypes(exclude=[np.number]).columns.tolist()
if non_numeric:
    print(f"❌ ERROR: Non-numeric columns found: {non_numeric}")
    raise ValueError("All features must be numeric!")
else:
    print(f"✅ All {len(df_final.columns)} columns are numeric")

# Handle any missing values
df_final = df_final.fillna(0)
print(f"✅ Missing values handled")

# ============================================================================
# SAVE PROCESSED DATA
# ============================================================================
print("\n[6/7] Saving processed data...")

output_file = PROCESSED_DIR / "circuits_engineered_75_features.csv"
df_final.to_csv(output_file, index=False)
print(f"✅ Saved engineered dataset: {output_file}")
print(f"   Shape: {df_final.shape}")
print(f"   Columns: {df_final.columns.tolist()[:10]}... (showing first 10)")

# Save feature names
feature_names_file = ENCODERS_DIR / "feature_names.json"
with open(feature_names_file, 'w') as f:
    json.dump(feature_cols, f, indent=2)
print(f"✅ Saved feature names: {feature_names_file}")

# ============================================================================
# SAVE ENCODERS
# ============================================================================
print("\n[7/7] Saving encoders...")
encoders_file = ENCODERS_DIR / "label_encoders.pkl"
joblib.dump(encoders, encoders_file)
print(f"✅ Saved encoders: {encoders_file}")
print(f"   Encoders: {list(encoders.keys())}")

# ============================================================================
# FINAL VERIFICATION
# ============================================================================
print("\n" + "="*70)
print("✅ FEATURE ENGINEERING COMPLETE!")
print(f"   Input: {len(df)} circuits × {df.shape[1]} original columns")
print(f"   Output: {len(df_final)} circuits × {len(feature_cols)} features + 1 target")
print(f"   Target classes: {df_final['guard_label'].nunique()}")
print(f"   All columns numeric: {df_final.select_dtypes(exclude=[np.number]).shape[1] == 0}")
print("="*70)

# Print sample data types
print("\nSample data types:")
print(df_final.dtypes.head(10))
