"""
Data Analysis Script
Analyze raw CSV data and generate statistics
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Paths
DATA_DIR = Path("data/raw")
CSV_FILE = DATA_DIR / "circuit_data_raw.csv"
METADATA_DIR = Path("data/metadata")
METADATA_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("TOR GUARD PREDICTOR - DATA ANALYSIS")
print("="*60)

# Load data
print(f"\n[1/5] Loading data from {CSV_FILE}...")
df = pd.read_csv(CSV_FILE)
print(f"✅ Loaded {len(df)} circuits")

# Basic statistics
print(f"\n[2/5] Analyzing dataset...")
print(f"  Columns: {df.shape[1]}")
print(f"  Rows: {df.shape[0]}")
print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Guard node analysis
unique_guards = df['guard_fingerprint'].nunique()
unique_exits = df['exit_fingerprint'].nunique()
print(f"\n  Unique guard nodes: {unique_guards}")
print(f"  Unique exit nodes: {unique_exits}")
print(f"  Unique middle nodes: {df['middle_fingerprint'].nunique()}")

# Country distribution
print(f"\n[3/5] Country distribution:")
print(f"  Guard countries: {df['guard_country'].value_counts().to_dict()}")
print(f"  Exit countries: {df['exit_country'].value_counts().to_dict()}")

# Bandwidth statistics
print(f"\n[4/5] Bandwidth statistics:")
print(f"  Guard bandwidth: {df['guard_bandwidth'].describe()}")
print(f"  Exit bandwidth: {df['exit_bandwidth'].describe()}")

# Save metadata
print(f"\n[5/5] Saving metadata...")
metadata = {
    "total_circuits": len(df),
    "unique_guards": unique_guards,
    "unique_exits": unique_exits,
    "guard_countries": df['guard_country'].value_counts().to_dict(),
    "exit_countries": df['exit_country'].value_counts().to_dict(),
    "columns": df.columns.tolist()
}

with open(METADATA_DIR / "data_stats.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Metadata saved to {METADATA_DIR / 'data_stats.json'}")
print("\n" + "="*60)
print("✅ DATA ANALYSIS COMPLETE!")
print("="*60)
