"""
Data Preparation — F1 2026 Season: Lap Times & Telemetry
==========================================================
Dataset: Kaggle — stevefza/f1-2026-bahrain-testing-day-2
Author: Felipe Tomelin
Course: Data Science — FURB

Steps:
    1. Load raw CSVs
    2. Standardize column names
    3. Handle missing values
    4. Parse and validate data types
    5. Remove duplicates
    6. Feature engineering (derived columns)
    7. Outlier detection & treatment
    8. Export cleaned dataset
"""

import pandas as pd
import numpy as np
import os
import glob
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
RAW_DATA_DIR = "../data/raw"         # CSVs originais (não commitados — baixar do Kaggle)
CLEAN_DATA_DIR = "../data/processed"  # Saída dos dados tratados
os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD ALL CSVs
# ─────────────────────────────────────────────
print("=== [1] Loading raw CSVs ===")

csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in '{RAW_DATA_DIR}'. "
        "Please download the dataset from Kaggle:\n"
        "  https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2"
    )

dfs = []
for f in csv_files:
    df_temp = pd.read_csv(f, low_memory=False)
    df_temp["_source_file"] = os.path.basename(f)
    dfs.append(df_temp)
    print(f"  Loaded: {os.path.basename(f)} — {len(df_temp):,} rows × {df_temp.shape[1]} cols")

df_raw = pd.concat(dfs, ignore_index=True)
print(f"\n  Combined: {len(df_raw):,} rows × {df_raw.shape[1]} columns")

# ─────────────────────────────────────────────
# 2. STANDARDIZE COLUMN NAMES
# ─────────────────────────────────────────────
print("\n=== [2] Standardizing column names ===")

def normalize_col(col: str) -> str:
    """snake_case, strip spaces, lowercase."""
    return (
        col.strip()
           .lower()
           .replace(" ", "_")
           .replace("-", "_")
           .replace("(", "")
           .replace(")", "")
           .replace("/", "_per_")
    )

df_raw.columns = [normalize_col(c) for c in df_raw.columns]
print(f"  Columns after normalization: {list(df_raw.columns)}")

# ─────────────────────────────────────────────
# 3. HANDLE MISSING VALUES
# ─────────────────────────────────────────────
print("\n=== [3] Missing values analysis ===")

missing_summary = df_raw.isnull().sum()
missing_pct = (missing_summary / len(df_raw) * 100).round(2)
missing_report = pd.DataFrame({
    "missing_count": missing_summary,
    "missing_pct": missing_pct
}).query("missing_count > 0").sort_values("missing_pct", ascending=False)

print(missing_report.to_string())

# Strategy:
#  - Numeric cols with < 20% missing → median imputation
#  - Categorical cols with < 20% missing → mode / "Unknown"
#  - Cols with ≥ 80% missing → drop

HIGH_MISSING_THRESHOLD = 80.0
cols_to_drop = missing_report[missing_report["missing_pct"] >= HIGH_MISSING_THRESHOLD].index.tolist()
if cols_to_drop:
    print(f"\n  Dropping cols with ≥{HIGH_MISSING_THRESHOLD}% missing: {cols_to_drop}")
    df_raw.drop(columns=cols_to_drop, inplace=True)

for col in df_raw.columns:
    if df_raw[col].isnull().sum() == 0:
        continue
    if df_raw[col].dtype in [np.float64, np.int64, float, int]:
        df_raw[col].fillna(df_raw[col].median(), inplace=True)
    else:
        mode_val = df_raw[col].mode()
        fill_val = mode_val[0] if not mode_val.empty else "Unknown"
        df_raw[col].fillna(fill_val, inplace=True)

print(f"\n  Missing values after imputation: {df_raw.isnull().sum().sum()}")

# ─────────────────────────────────────────────
# 4. PARSE & VALIDATE DATA TYPES
# ─────────────────────────────────────────────
print("\n=== [4] Data type validation ===")

# Lap time columns — convert "MM:SS.mmm" strings to float seconds if needed
def parse_laptime(val):
    """Convert 'M:SS.mmm' or 'SS.mmm' string to float seconds."""
    if pd.isnull(val):
        return np.nan
    val = str(val).strip()
    try:
        if ":" in val:
            parts = val.split(":")
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        return float(val)
    except Exception:
        return np.nan

# Common laptime column names in F1 datasets
LAPTIME_COLS = [c for c in df_raw.columns if any(
    kw in c for kw in ["laptime", "lap_time", "time", "sector"]
)]

for col in LAPTIME_COLS:
    if df_raw[col].dtype == object:
        df_raw[col] = df_raw[col].apply(parse_laptime)
        print(f"  Parsed '{col}' → float seconds")

# Lap number → int
if "lap_number" in df_raw.columns:
    df_raw["lap_number"] = pd.to_numeric(df_raw["lap_number"], errors="coerce").astype("Int64")

# Boolean flags
BOOL_COLS = [c for c in df_raw.columns if any(
    kw in c for kw in ["is_", "pit", "fresh_tyre", "deleted"]
)]
for col in BOOL_COLS:
    if df_raw[col].dtype == object:
        df_raw[col] = df_raw[col].map(
            {"True": True, "False": False, "1": True, "0": False, True: True, False: False}
        ).astype("boolean")

print("  Data types:\n", df_raw.dtypes.to_string())

# ─────────────────────────────────────────────
# 5. REMOVE DUPLICATES
# ─────────────────────────────────────────────
print("\n=== [5] Duplicate removal ===")

n_before = len(df_raw)
df_raw.drop_duplicates(inplace=True)
n_after = len(df_raw)
print(f"  Removed {n_before - n_after:,} duplicate rows ({n_before:,} → {n_after:,})")

# ─────────────────────────────────────────────
# 6. FEATURE ENGINEERING
# ─────────────────────────────────────────────
print("\n=== [6] Feature engineering ===")

# 6a. Lap time in MM:SS format (human-readable derived column)
if "laptime_seconds" in df_raw.columns or any("time" in c for c in df_raw.columns):
    laptime_col = next((c for c in df_raw.columns if "laptime" in c or "lap_time" in c), None)
    if laptime_col and df_raw[laptime_col].dtype in [float, np.float64]:
        df_raw["laptime_formatted"] = df_raw[laptime_col].apply(
            lambda s: f"{int(s // 60)}:{s % 60:06.3f}" if pd.notnull(s) else None
        )
        print("  Created: laptime_formatted")

# 6b. Tyre life category
if "tyre_life" in df_raw.columns:
    df_raw["tyre_life_category"] = pd.cut(
        df_raw["tyre_life"],
        bins=[0, 5, 15, 30, 100],
        labels=["New (0-5)", "Used (6-15)", "High-Life (16-30)", "Old (30+)"]
    )
    print("  Created: tyre_life_category")

# 6c. Speed delta from session median
speed_cols = [c for c in df_raw.columns if "speed" in c]
for col in speed_cols:
    delta_col = f"{col}_delta_pct"
    median_speed = df_raw[col].median()
    if median_speed and median_speed != 0:
        df_raw[delta_col] = ((df_raw[col] - median_speed) / median_speed * 100).round(3)
        print(f"  Created: {delta_col}")

# 6d. Session type tag from source file name
if "_source_file" in df_raw.columns:
    def tag_session(fname):
        fname_lower = str(fname).lower()
        if "quali" in fname_lower:
            return "Qualifying"
        elif "fp1" in fname_lower or "fp2" in fname_lower or "fp3" in fname_lower:
            return "Practice"
        elif "race" in fname_lower:
            return "Race"
        elif "testing" in fname_lower or "bahrain" in fname_lower:
            return "Pre-Season Testing"
        return "Unknown"

    df_raw["session_tag"] = df_raw["_source_file"].apply(tag_session)
    print("  Created: session_tag")

# Drop helper column
df_raw.drop(columns=["_source_file"], inplace=True, errors="ignore")

# ─────────────────────────────────────────────
# 7. OUTLIER DETECTION & TREATMENT
# ─────────────────────────────────────────────
print("\n=== [7] Outlier treatment (IQR method) ===")

NUMERIC_COLS = df_raw.select_dtypes(include=[np.number]).columns.tolist()

outlier_report = []
for col in NUMERIC_COLS:
    Q1 = df_raw[col].quantile(0.25)
    Q3 = df_raw[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 3 * IQR    # using 3×IQR (less aggressive for F1 telemetry)
    upper = Q3 + 3 * IQR
    n_outliers = ((df_raw[col] < lower) | (df_raw[col] > upper)).sum()
    if n_outliers > 0:
        outlier_report.append({
            "column": col,
            "outliers": n_outliers,
            "pct": round(n_outliers / len(df_raw) * 100, 2),
            "lower_fence": round(lower, 4),
            "upper_fence": round(upper, 4)
        })
        # Cap outliers (Winsorization) instead of removing rows
        df_raw[col] = df_raw[col].clip(lower=lower, upper=upper)

outlier_df = pd.DataFrame(outlier_report)
print(outlier_df.to_string(index=False) if not outlier_df.empty else "  No outliers detected.")

# ─────────────────────────────────────────────
# 8. EXPORT CLEANED DATASET
# ─────────────────────────────────────────────
print("\n=== [8] Exporting cleaned dataset ===")

output_path = os.path.join(CLEAN_DATA_DIR, "f1_2026_laps_cleaned.csv")
df_raw.to_csv(output_path, index=False)
print(f"  Saved: {output_path}")
print(f"  Final shape: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")

print("\n✅ Data Preparation complete!")
print(f"   Columns: {list(df_raw.columns)}")
