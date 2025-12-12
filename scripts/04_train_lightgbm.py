"""
LightGBM Model Training
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import json
import time
from pathlib import Path

# Paths
DATA_FILE = Path("data/processed/circuits_engineered_75_features.csv")
MODEL_DIR = Path("models/lightgbm")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("TRAINING LIGHTGBM MODEL")
print("="*70)

# Load data
print(f"\n[1/5] Loading engineered data...")
df = pd.read_csv(DATA_FILE)
print(f"✅ Loaded {len(df)} samples")

# Prepare data
X = df.drop('guard_label', axis=1)
y = df['guard_label']

# Split data
print(f"\n[2/5] Splitting data...")
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1765, random_state=42, stratify=y_temp)

print(f"   Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# LightGBM parameters
params = {
    'objective': 'multiclass',
    'num_class': y.nunique(),
    'metric': 'multi_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 255,
    'learning_rate': 0.1,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0,
    'random_state': 42
}

print(f"\n[3/5] Training LightGBM model...")
print(f"   Parameters: {params}")

start_time = time.time()

# Train model
model = lgb.LGBMClassifier(**params, n_estimators=300)
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    eval_metric='multi_logloss',
    callbacks=[lgb.early_stopping(20), lgb.log_evaluation(10)]
)

training_time = time.time() - start_time
print(f"\n✅ Training completed in {training_time:.2f} seconds")

# Evaluate
print(f"\n[4/5] Evaluating model...")

def compute_top_k_accuracy(y_true, y_pred_proba, k=5):
    top_k_preds = np.argsort(y_pred_proba, axis=1)[:, -k:]
    correct = sum([y_true.iloc[i] in top_k_preds[i] for i in range(len(y_true))])
    return correct / len(y_true)

y_pred_proba = model.predict_proba(X_test)
y_pred = np.argmax(y_pred_proba, axis=1)

metrics = {
    'top_1_accuracy': float(accuracy_score(y_test, y_pred)),
    'top_3_accuracy': float(compute_top_k_accuracy(y_test, y_pred_proba, k=3)),
    'top_5_accuracy': float(compute_top_k_accuracy(y_test, y_pred_proba, k=5)),
    'top_10_accuracy': float(compute_top_k_accuracy(y_test, y_pred_proba, k=10)),
    'top_20_accuracy': float(compute_top_k_accuracy(y_test, y_pred_proba, k=20)),
    'training_time_seconds': training_time,
    'num_samples_train': len(X_train),
    'num_samples_test': len(X_test),
    'num_features': X.shape[1],
    'num_classes': y.nunique()
}

print(f"\n📊 LIGHTGBM MODEL PERFORMANCE:")
print(f"   Top-1 Accuracy:  {metrics['top_1_accuracy']*100:.2f}%")
print(f"   Top-5 Accuracy:  {metrics['top_5_accuracy']*100:.2f}%")
print(f"   Top-10 Accuracy: {metrics['top_10_accuracy']*100:.2f}%")

# Save model
print(f"\n[5/5] Saving model...")
model_file = MODEL_DIR / "lightgbm_v1.pkl"
joblib.dump(model, model_file)
print(f"✅ Model saved: {model_file}")

metrics_file = MODEL_DIR / "lightgbm_v1_metrics.json"
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"✅ Metrics saved: {metrics_file}")

print("\n" + "="*70)
print("✅ LIGHTGBM TRAINING COMPLETE!")
print("="*70)
