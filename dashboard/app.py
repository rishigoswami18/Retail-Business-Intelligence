import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config for premium look
st.set_page_config(page_title="Retail BI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for glassmorphism aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# LOAD DATA
@st.cache_data
def load_data():
    file_path = "data/cleaned/superstore_cleaned.csv"
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

if df is None:
    st.error("Cleaned data not found. Please run 'data_cleaning.py' first.")
    st.stop()

# SIDEBAR FILTERS
st.sidebar.title("📊 BI Filters")
region_filter = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
category_filter = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[(df['Region'].isin(region_filter)) & (df['Category'].isin(category_filter))]

# HEADER
st.title("🚀 Retail Business Intelligence Dashboard")
st.markdown("---")

# KPI ROW
col1, col2, col3, col4 = st.columns(4)
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0
total_orders = filtered_df['Order ID'].nunique()

col1.metric("Total Revenue", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{avg_margin:.1f}% Margin")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Avg Discount", f"{filtered_df['Discount'].mean()*100:.1f}%")

st.markdown("---")

# CHARTS ROW 1
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Monthly Sales Trend")
    trend_df = filtered_df.groupby('Order_YearMonth')['Sales'].sum().reset_index()
    fig_trend = px.line(trend_df, x='Order_YearMonth', y='Sales', markers=True, 
                        template="plotly_dark", color_discrete_sequence=['#2563EB'])
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("🌍 Profit by State")
    state_profit = filtered_df.groupby('State')['Profit'].sum().reset_index()
    fig_map = px.choropleth(state_profit, locations='State', locationmode="USA-states", 
                             color='Profit', scope="usa", template="plotly_dark",
                             color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_map, use_container_width=True)

# CHARTS ROW 2
c3, c4 = st.columns(2)

with c3:
    st.subheader("🏷️ Category Performance")
    cat_df = filtered_df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    fig_cat = px.bar(cat_df, x='Category', y=['Sales', 'Profit'], barmode='group',
                     template="plotly_dark", color_discrete_sequence=['#2563EB', '#059669'])
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    st.subheader("💸 Discount vs Profitability")
    # Sample for performance if needed, but 10k rows is fine for Plotly
    fig_scatter = px.scatter(filtered_df, x='Discount', y='Profit', color='Category',
                             trendline="ols", template="plotly_dark", hover_name="Product Name")
    st.plotly_chart(fig_scatter, use_container_width=True)

# DATA TABLE
st.subheader("📋 Top Performing Products")
top_products = filtered_df.groupby('Product Name').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum'
}).sort_values('Sales', ascending=False).head(10)
st.table(top_products.style.format("${:,.2f}", subset=['Sales', 'Profit']))

st.markdown("---")
st.info("💡 **Analyst Note:** Use the sidebar to filter regions and see how discounting impacts different product categories in real-time.")
