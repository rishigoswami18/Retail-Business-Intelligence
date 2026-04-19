"""
=============================================================================
STEP 5: CUSTOMER SEGMENTATION - RFM ANALYSIS
=============================================================================
Retail Business Intelligence Project
Author: [Your Name]
Description: Performs RFM analysis to segment customers.
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import timedelta

# CONFIGURATION
CLEAN_DATA_PATH = os.path.join("data", "cleaned", "superstore_cleaned.csv")
CHARTS_DIR = os.path.join("visualizations", "rfm")
OUTPUT_DIR = os.path.join("data", "rfm")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("  RETAIL BI - RFM ANALYSIS")
print("=" * 70)

# LOAD DATA
df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=['Order Date'])
reference_date = df['Order Date'].max() + timedelta(days=1)

# CALC RFM
rfm = df.groupby('Customer ID').agg({
    'Order Date': lambda x: (reference_date - x.max()).days,
    'Order ID': 'nunique',
    'Sales': 'sum'
}).reset_index()

rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']

# SCORING
rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

# SEGMENTATION
def assign_segment(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r >= 4 and f >= 4 and m >= 4: return 'Champions'
    if f >= 4 and m >= 3: return 'Loyal Customers'
    if r >= 4 and f >= 2: return 'Promising'
    if r <= 2 and f >= 3: return 'At Risk'
    if r <= 2 and f <= 2: return 'Hibernating'
    return 'Need Attention'

rfm['Segment'] = rfm.apply(assign_segment, axis=1)

# VISUALIZE
fig, ax = plt.subplots(figsize=(12, 7))
rfm['Segment'].value_counts().plot(kind='barh', ax=ax, color='skyblue')
plt.title('Customer Segments Distribution')
plt.savefig(os.path.join(CHARTS_DIR, 'segment_distribution.png'))
plt.close()

# EXPORT
rfm.to_csv(os.path.join(OUTPUT_DIR, 'customer_rfm_segments.csv'), index=False)
print(f"[OK] RFM analysis complete. Data saved to {OUTPUT_DIR}")
print("\n" + "=" * 70)
