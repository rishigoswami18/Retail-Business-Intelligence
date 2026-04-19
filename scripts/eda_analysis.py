"""
=============================================================================
STEP 4: EXPLORATORY DATA ANALYSIS (EDA)
=============================================================================
Retail Business Intelligence Project
Author: [Your Name]
Description: Comprehensive EDA with charts and actionable insights.
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# CONFIGURATION
CLEAN_DATA_PATH = os.path.join("data", "cleaned", "superstore_cleaned.csv")
CHARTS_DIR = os.path.join("visualizations", "eda")
os.makedirs(CHARTS_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams.update({
    'figure.figsize': (14, 7),
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 13,
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.dpi': 200
})

COLORS = {
    'primary': '#2563EB',
    'secondary': '#7C3AED',
    'success': '#059669',
    'danger': '#DC2626',
    'warning': '#D97706',
    'info': '#0891B2',
    'palette': ['#2563EB', '#7C3AED', '#059669', '#DC2626', '#D97706', '#0891B2']
}

print("=" * 70)
print("  RETAIL BI - EXPLORATORY DATA ANALYSIS")
print("=" * 70)

# LOAD CLEANED DATA
df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=['Order Date', 'Ship Date'])
print(f"\n[OK] Loaded cleaned dataset: {df.shape[0]:,} rows")

# 1. Monthly Revenue & Profit Trend
print("\n[CHART 1] Monthly Revenue & Profit Trend")
monthly = df.groupby('Order_YearMonth').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
fig, ax1 = plt.subplots(figsize=(16, 7))
ax1.bar(range(len(monthly)), monthly['Sales'], color=COLORS['primary'], alpha=0.7, label='Revenue')
ax2 = ax1.twinx()
ax2.plot(range(len(monthly)), monthly['Profit'], color=COLORS['danger'], linewidth=2.5, marker='o', label='Profit')
ax1.set_xticks(range(0, len(monthly), 3))
ax1.set_xticklabels(monthly['Order_YearMonth'].iloc[::3], rotation=45)
plt.title('Monthly Revenue & Profit Trend')
plt.savefig(os.path.join(CHARTS_DIR, '01_revenue_profit_trend.png'))
plt.close()

# 2. Distributions
print("[CHART 2] Distributions")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
sns.histplot(df['Sales'], bins=50, kde=True, ax=axes[0], color=COLORS['primary'])
sns.histplot(df['Profit'], bins=50, kde=True, ax=axes[1], color=COLORS['success'])
plt.savefig(os.path.join(CHARTS_DIR, '02_distributions.png'))
plt.close()

# 3. Correlation Heatmap
print("[CHART 3] Correlation Heatmap")
numeric_cols = ['Sales', 'Quantity', 'Discount', 'Profit', 'Shipping_Days', 'Profit_Margin', 'Cost']
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0)
plt.title('Correlation Heatmap')
plt.savefig(os.path.join(CHARTS_DIR, '03_correlation_heatmap.png'))
plt.close()

# 4. Category Performance
print("[CHART 4] Category Performance")
cat_perf = df.groupby('Category')[['Sales', 'Profit']].sum().sort_values('Sales')
cat_perf['Sales'].plot(kind='barh', color=COLORS['palette'])
plt.title('Revenue by Category')
plt.savefig(os.path.join(CHARTS_DIR, '04_category_analysis.png'))
plt.close()

# 5. Regional Performance
print("[CHART 5] Regional Performance")
region_perf = df.groupby('Region')[['Sales', 'Profit']].sum()
region_perf.plot(kind='bar', color=[COLORS['primary'], COLORS['success']])
plt.title('Revenue & Profit by Region')
plt.savefig(os.path.join(CHARTS_DIR, '05_region_analysis.png'))
plt.close()

# 6. Discount impact
print("[CHART 6] Discount Impact")
sns.scatterplot(data=df.sample(min(1000, len(df))), x='Discount', y='Profit', hue='Category')
plt.axhline(0, color='red', linestyle='--')
plt.title('Discount vs ProfitImpact')
plt.savefig(os.path.join(CHARTS_DIR, '06_discount_vs_profit.png'))
plt.close()

print("\n" + "=" * 70)
print("  [OK] EDA COMPLETE - 6 CHARTS GENERATED")
print("=" * 70)
