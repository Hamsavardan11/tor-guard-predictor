"""
Ensemble Model Creation
Combines XGBoost, LightGBM, CatBoost predictions
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import json
import time
from pathlib import Path

# Paths
DATA_FILE = Path("data/processed/circuits_engineered_75_features.csv")
XGBOOST_MODEL = Path("models/xgboost/xgboost_v1.json")
LIGHTGBM_MODEL = Path("models/lightgbm/lightgbm_v1.pkl")
CATBOOST_MODEL = Path("models/catboost/catboost_v1.cbm")
ENSEMBLE_DIR = Path("models/ensemble")
ENSEMBLE_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("CREATING ENSEMBLE MODEL")
print("="*70)

# Load data
print(f"\n[1/5] Loading data...")
df = pd.read_csv(DATA_FILE)
X = df.drop('guard_label', axis=1)
y = df['guard_label']

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

# Load all three models
print(f"\n[2/5] Loading all trained models...")

# XGBoost
xgb_model = xgb.Booster()
xgb_model.load_model(str(XGBOOST_MODEL))
print(f"   ✅ XGBoost loaded")

# LightGBM
lgb_model = joblib.load(LIGHTGBM_MODEL)
print(f"   ✅ LightGBM loaded")

# CatBoost
cat_model = CatBoostClassifier()
cat_model.load_model(str(CATBOOST_MODEL))
print(f"   ✅ CatBoost loaded")

# Generate predictions from each model
print(f"\n[3/5] Generating predictions from all models...")

# XGBoost predictions
dtest = xgb.DMatrix(X_test, feature_names=X.columns.tolist())
xgb_proba = xgb_model.predict(dtest)
print(f"   ✅ XGBoost predictions generated")

# LightGBM predictions
lgb_proba = lgb_model.predict_proba(X_test)
print(f"   ✅ LightGBM predictions generated")

# CatBoost predictions
cat_proba = cat_model.predict_proba(X_test)
print(f"   ✅ CatBoost predictions generated")

# Combine predictions with weighted average
print(f"\n[4/5] Combining predictions (weighted ensemble)...")
weights = {
    'xgboost': 0.4,
    'lightgbm': 0.3,
    'catboost': 0.3
}

ensemble_proba = (
    weights['xgboost'] * xgb_proba +
    weights['lightgbm'] * lgb_proba +
    weights['catboost'] * cat_proba
)

print(f"   Ensemble weights: XGBoost={weights['xgboost']}, LightGBM={weights['lightgbm']}, CatBoost={weights['catboost']}")

# Evaluate ensemble
print(f"\n[5/5] Evaluating ensemble performance...")

def compute_top_k_accuracy(y_true, y_pred_proba, k=5):
    top_k_preds = np.argsort(y_pred_proba, axis=1)[:, -k:]
    correct = sum([y_true.iloc[i] in top_k_preds[i] for i in range(len(y_true))])
    return correct / len(y_true)

y_pred = np.argmax(ensemble_proba, axis=1)

metrics = {
    'top_1_accuracy': float(accuracy_score(y_test, y_pred)),
    'top_3_accuracy': float(compute_top_k_accuracy(y_test, ensemble_proba, k=3)),
    'top_5_accuracy': float(compute_top_k_accuracy(y_test, ensemble_proba, k=5)),
    'top_10_accuracy': float(compute_top_k_accuracy(y_test, ensemble_proba, k=10)),
    'top_20_accuracy': float(compute_top_k_accuracy(y_test, ensemble_proba, k=20)),
    'num_samples_test': len(X_test),
    'ensemble_components': ['xgboost', 'lightgbm', 'catboost'],
    'ensemble_weights': weights
}

print(f"\n📊 ENSEMBLE MODEL PERFORMANCE:")
print(f"   Top-1 Accuracy:  {metrics['top_1_accuracy']*100:.2f}%")
print(f"   Top-3 Accuracy:  {metrics['top_3_accuracy']*100:.2f}%")
print(f"   Top-5 Accuracy:  {metrics['top_5_accuracy']*100:.2f}%")
print(f"   Top-10 Accuracy: {metrics['top_10_accuracy']*100:.2f}%")
print(f"   Top-20 Accuracy: {metrics['top_20_accuracy']*100:.2f}%")

# Save ensemble metadata
ensemble_data = {
    'models': {
        'xgboost': str(XGBOOST_MODEL),
        'lightgbm': str(LIGHTGBM_MODEL),
        'catboost': str(CATBOOST_MODEL)
    },
    'weights': weights,
    'performance': metrics
}

model_file = ENSEMBLE_DIR / "ensemble_v1.pkl"
joblib.dump(ensemble_data, model_file)
print(f"\n✅ Ensemble metadata saved: {model_file}")

metrics_file = ENSEMBLE_DIR / "ensemble_v1_metrics.json"
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"✅ Metrics saved: {metrics_file}")

print("\n" + "="*70)
print("✅ ENSEMBLE CREATION COMPLETE!")
print(f"   Combined {len(ensemble_data['models'])} models")
print(f"   Best Top-10 Accuracy: {metrics['top_10_accuracy']*100:.2f}%")
print("="*70)
