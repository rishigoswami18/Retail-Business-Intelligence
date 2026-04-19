"""
=============================================================================
STEP 2: DATA CLEANING & FEATURE ENGINEERING
=============================================================================
Retail Business Intelligence Project
Author: [Your Name]
Description: Cleans the Superstore dataset, handles missing values, removes
             duplicates, converts data types, and engineers new features
             for downstream analysis.
=============================================================================
"""

import pandas as pd
import numpy as np
import warnings
import os

warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# 1. LOAD THE RAW DATASET
# -----------------------------------------------------------------------------
RAW_DATA_PATH = os.path.join("data", "Retail-Supply-Chain-Sales-Dataset.xlsx")
CLEAN_DATA_PATH = os.path.join("data", "cleaned", "superstore_cleaned.csv")

print("=" * 70)
print("  RETAIL BI - DATA CLEANING PIPELINE")
print("=" * 70)

try:
    df = pd.read_excel(RAW_DATA_PATH)
    print(f"\n[OK] Dataset loaded successfully: {RAW_DATA_PATH}")
except Exception as e:
    print(f"\n[ERROR] Error loading Excel file: {e}")
    raise

print(f"   Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# -----------------------------------------------------------------------------
# 2. INITIAL DATA INSPECTION
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  INITIAL DATA INSPECTION")
print("-" * 70)

print("\n[INFO] Column Names & Data Types:")
print(df.dtypes.to_string())

print(f"\n[INFO] First 5 rows:")
print(df.head().to_string())

print(f"\n[INFO] Dataset Info:")
print(f"   Total Records   : {df.shape[0]:,}")
print(f"   Total Columns   : {df.shape[1]}")
print(f"   Memory Usage    : {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# -----------------------------------------------------------------------------
# 3. HANDLE MISSING VALUES
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  HANDLING MISSING VALUES")
print("-" * 70)

missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct.round(2)
}).query('`Missing Count` > 0')

if missing_df.empty:
    print("\n[OK] No missing values found!")
else:
    print(f"\n[WARN] Missing values detected:")
    print(missing_df.to_string())
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"   -> {col}: filled {missing[col]} nulls with median ({median_val:.2f})")
    
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            print(f"   -> {col}: filled {missing[col]} nulls with mode ('{mode_val}')")

print(f"\n   Remaining missing values: {df.isnull().sum().sum()}")

# -----------------------------------------------------------------------------
# 4. REMOVE DUPLICATES
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  REMOVING DUPLICATES")
print("-" * 70)

duplicates_before = df.duplicated().sum()
print(f"\n   Duplicate rows found: {duplicates_before}")

if duplicates_before > 0:
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"   [OK] Removed {duplicates_before} duplicate rows")
    print(f"   New shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
else:
    print("   [OK] No duplicates found - dataset is clean!")

# -----------------------------------------------------------------------------
# 5. CONVERT DATA TYPES
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  CONVERTING DATA TYPES")
print("-" * 70)

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
print("   [OK] 'Order Date' -> datetime64")
print("   [OK] 'Ship Date'  -> datetime64")

numeric_fields = ['Sales', 'Quantity', 'Discount', 'Profit']
for col in numeric_fields:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"   [OK] '{col}' -> numeric")

if 'Postal Code' in df.columns:
    df['Postal Code'] = df['Postal Code'].astype(str)
    print("   [OK] 'Postal Code' -> string")

cat_cols = ['Ship Mode', 'Segment', 'Country', 'City', 'State', 
            'Region', 'Category', 'Sub-Category']
for col in cat_cols:
    if col in df.columns:
        df[col] = df[col].astype('category')
        print(f"   [OK] '{col}' -> category")

# -----------------------------------------------------------------------------
# 6. FEATURE ENGINEERING
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  FEATURE ENGINEERING")
print("-" * 70)

df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
print("   [OK] Created 'Shipping_Days'")

df['Revenue'] = df['Sales']
print("   [OK] Created 'Revenue'")

df['Profit_Margin'] = np.where(df['Sales'] != 0, (df['Profit'] / df['Sales']) * 100, 0)
print("   [OK] Created 'Profit_Margin'")

df['Cost'] = df['Sales'] - df['Profit']
print("   [OK] Created 'Cost'")

df['Has_Discount'] = (df['Discount'] > 0).astype(int)
print("   [OK] Created 'Has_Discount'")

df['Order_Year'] = df['Order Date'].dt.year
df['Order_Month'] = df['Order Date'].dt.month
df['Order_Quarter'] = df['Order Date'].dt.quarter
df['Order_DayOfWeek'] = df['Order Date'].dt.day_name()
df['Order_YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
print("   [OK] Created date components")

df['Order_Size'] = pd.cut(df['Quantity'], bins=[0, 2, 5, 10, float('inf')], labels=['Small', 'Medium', 'Large', 'Bulk'])
print("   [OK] Created 'Order_Size'")

df['Profit_Category'] = np.where(df['Profit'] > 0, 'Profitable', np.where(df['Profit'] == 0, 'Break-Even', 'Loss'))
print("   [OK] Created 'Profit_Category'")

# -----------------------------------------------------------------------------
# 7. DATA VALIDATION - FINAL CHECKS
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  FINAL DATA VALIDATION")
print("-" * 70)

print(f"\n   Final Shape       : {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"   Missing Values    : {df.isnull().sum().sum()}")
print(f"   Total Revenue     : ${df['Revenue'].sum():,.2f}")
print(f"   Total Profit      : ${df['Profit'].sum():,.2f}")
print(f"   Unique Customers  : {df['Customer ID'].nunique():,}")

# -----------------------------------------------------------------------------
# 8. EXPORT CLEANED DATASET
# -----------------------------------------------------------------------------
print("\n" + "-" * 70)
print("  EXPORTING CLEANED DATA")
print("-" * 70)

os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
df.to_csv(CLEAN_DATA_PATH, index=False)
print(f"\n   [OK] Cleaned dataset saved to: {CLEAN_DATA_PATH}")

# Summary report
summary_path = os.path.join("data", "cleaned", "data_summary.txt")
with open(summary_path, 'w') as f:
    f.write(f"SUPERSTORE CLEANED DATA SUMMARY\nTotal Records: {df.shape[0]:,}\n")
    f.write(f"Total Revenue: ${df['Revenue'].sum():,.2f}\nTotal Profit: ${df['Profit'].sum():,.2f}\n")

print(f"   [OK] Summary report saved to: {summary_path}")
print("\n" + "=" * 70)
print("  [OK] DATA CLEANING PIPELINE COMPLETE!")
print("=" * 70)
