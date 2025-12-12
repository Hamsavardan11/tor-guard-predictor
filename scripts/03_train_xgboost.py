"""
XGBoost Model Training
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import json
import time
from pathlib import Path

# Paths
DATA_FILE = Path("data/processed/circuits_engineered_75_features.csv")
MODEL_DIR = Path("models/xgboost")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("TRAINING XGBOOST MODEL")
print("="*70)

# Load data
print(f"\n[1/5] Loading engineered data...")
df = pd.read_csv(DATA_FILE)
print(f"✅ Loaded {len(df)} samples with {df.shape[1]-1} features")

# Prepare data
X = df.drop('guard_label', axis=1)
y = df['guard_label']

print(f"   Features: {X.shape[1]}")
print(f"   Classes: {y.nunique()}")
print(f"   Class distribution: {y.value_counts().describe()}")

# Split data
print(f"\n[2/5] Splitting data (70% train, 15% val, 15% test)...")
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1765, random_state=42, stratify=y_temp)

print(f"   Train: {len(X_train)} samples")
print(f"   Val: {len(X_val)} samples")
print(f"   Test: {len(X_test)} samples")

# Create DMatrix
print(f"\n[3/5] Creating DMatrix...")
dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=X.columns.tolist())
dval = xgb.DMatrix(X_val, label=y_val, feature_names=X.columns.tolist())
dtest = xgb.DMatrix(X_test, label=y_test, feature_names=X.columns.tolist())

# XGBoost parameters
params = {
    'objective': 'multi:softprob',
    'num_class': y.nunique(),
    'max_depth': 10,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 1,
    'gamma': 0,
    'reg_alpha': 0,
    'reg_lambda': 1,
    'eval_metric': 'mlogloss',
    'tree_method': 'hist',
    'predictor': 'cpu_predictor',
    'random_state': 42
}

print(f"\n[4/5] Training XGBoost model...")
print(f"   Parameters: {params}")

start_time = time.time()

# Train model
evals = [(dtrain, 'train'), (dval, 'val')]
model = xgb.train(
    params,
    dtrain,
    num_boost_round=300,
    evals=evals,
    early_stopping_rounds=20,
    verbose_eval=10
)

training_time = time.time() - start_time
print(f"\n✅ Training completed in {training_time:.2f} seconds")

# Evaluate
print(f"\n[5/5] Evaluating model...")

def compute_top_k_accuracy(y_true, y_pred_proba, k=5):
    """Compute Top-K accuracy"""
    top_k_preds = np.argsort(y_pred_proba, axis=1)[:, -k:]
    correct = sum([y_true.iloc[i] in top_k_preds[i] for i in range(len(y_true))])
    return correct / len(y_true)

# Predictions
y_pred_proba = model.predict(dtest)
y_pred = np.argmax(y_pred_proba, axis=1)

# Metrics
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

print(f"\n📊 XGBOOST MODEL PERFORMANCE:")
print(f"   Top-1 Accuracy:  {metrics['top_1_accuracy']*100:.2f}%")
print(f"   Top-3 Accuracy:  {metrics['top_3_accuracy']*100:.2f}%")
print(f"   Top-5 Accuracy:  {metrics['top_5_accuracy']*100:.2f}%")
print(f"   Top-10 Accuracy: {metrics['top_10_accuracy']*100:.2f}%")
print(f"   Top-20 Accuracy: {metrics['top_20_accuracy']*100:.2f}%")

# Save model
model_file = MODEL_DIR / "xgboost_v1.json"
model.save_model(str(model_file))
print(f"\n✅ Model saved: {model_file}")

# Save metrics
metrics_file = MODEL_DIR / "xgboost_v1_metrics.json"
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"✅ Metrics saved: {metrics_file}")

# Feature importance
importance = model.get_score(importance_type='gain')
feature_importance = pd.DataFrame([
    {'feature': f, 'importance': importance.get(f, 0)} 
    for f in X.columns
]).sort_values('importance', ascending=False)

importance_file = MODEL_DIR / "xgboost_v1_feature_importance.csv"
feature_importance.to_csv(importance_file, index=False)
print(f"✅ Feature importance saved: {importance_file}")

print("\n" + "="*70)
print("✅ XGBOOST TRAINING COMPLETE!")
print("="*70)
