import streamlit as st 
from PIL import Image
import pandas as pd
import requests
import plotly.express as px

# PAGE CONFIG
st.set_page_config(page_title="Fake Store Insights", page_icon="🎡", layout="wide")

# LOGO
img = Image.open("logo.png") 
st.image(img, width=160)

st.title("💾Fake Store API Dashboard")

# API 
API = "https://fakestoreapi.com/products"

@st.cache_data
def load_data():
    response = requests.get(API)
    data = response.json()
    return pd.DataFrame(data)

df = load_data()

# CLEANING 
df['price'] = df['price'].astype(float)
df['Category'] = df['category'].astype(str)

# Only display these columns
DISPLAY_COLS = ['id', 'title', 'price', 'category']

# SIDEBAR FILTER
with st.sidebar:
    st.header("🧧Filters")
    categories = st.multiselect(
        "Select Category",
        df['Category'].unique(),
        default=df['Category'].unique()
    )

# Prevent empty selection
if not categories:
    categories = df['Category'].unique()

filtered_df = df[df['Category'].isin(categories)]

# DATASET 
st.subheader("✨Dataset Overview")
st.dataframe(df[DISPLAY_COLS], use_container_width=True)

st.divider()

# KPI 
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

if filtered_df.empty:
    with col1:
        st.metric("Total Products", 0)
    with col2:
        st.metric("Average Price", "N/A")
    with col3:
        st.metric("Highest Price", "N/A")

    st.warning("No data available for selected filters")

else:
    total_products = len(filtered_df)
    avg_price = filtered_df['price'].mean()
    max_price = filtered_df['price'].max()
    overall_avg = df['price'].mean()

    with col1:
        st.metric("Total Products", total_products)

    with col2:
        st.metric(
            "Average Price",
            f"${avg_price:.2f}",
            delta=f"{avg_price - overall_avg:.2f} vs overall"
        )

    with col3:
        st.metric("Highest Price", f"${max_price:.2f}")

st.divider()

#  CHARTS
st.subheader("Analytics")

if filtered_df.empty:
    st.info("No data to display charts")

else:
    col_left, col_right = st.columns(2)

    with col_left:
        cate_count = filtered_df["category"].value_counts().reset_index()
        fig_bar = px.bar(
            cate_count,
            x="category",
            y="count",
            title="Products Count by Category",
            color="category"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        fig_hist = px.histogram(
            filtered_df,
            x='price',
            nbins=20,
            title="Price Distribution"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Scatter
    fig_scatter = px.scatter(
        filtered_df,
        x="id",
        y="price",
        color="category",
        title="Price vs Product ID"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# TABLE 
st.subheader("Filtered Products")
st.dataframe(filtered_df[DISPLAY_COLS], use_container_width=True)

# DOWNLOAD
csv = filtered_df[DISPLAY_COLS].to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ grab the csv",
    data=csv,
    file_name="filtered_products.csv",
    mime="text/csv",
)