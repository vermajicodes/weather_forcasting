import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# gotta be first or streamlit throws a fit lol
st.set_page_config(
    page_title="Real-Time-price-Monitoring-Alert-System",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# all the css stuff – yeah i know inline styles are cringe but streamlit forces your hand
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #161a23;
    --border:    #252b38;
    --accent:    #f4a944;
    --accent2:   #6c63ff;
    --text:      #e8eaf0;
    --muted:     #7a8299;
    --success:   #34d399;
    --danger:    #f87171;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
    padding-top: 2rem;
}
[data-testid="stSidebar"] h2 { color: var(--accent) !important; }
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 0.8rem; letter-spacing: .06em; text-transform: uppercase; }

.dash-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d0f14 60%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 12px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.dash-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.dash-header p { color: var(--muted); margin: 0; font-size: 0.88rem; }

.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    transition: border-color .2s;
}
.kpi-card:hover { border-color: var(--accent); }
.kpi-label { font-size: 0.78rem; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; margin-bottom: .4rem; }
.kpi-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: var(--accent); }
.kpi-sub   { font-size: 0.78rem; color: var(--muted); margin-top: .2rem; }

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: .75rem;
    margin: 1.8rem 0 1rem;
    letter-spacing: .02em;
}

[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }

[data-testid="stDownloadButton"] > button {
    background: var(--accent) !important;
    color: #0d0f14 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: .55rem 1.4rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: opacity .2s !important;
}
[data-testid="stDownloadButton"] > button:hover { opacity: .85 !important; }

.stPlotlyChart { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }

/* hiding streamlit's default footer/header bc why would i want that */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# reusable chart styler so i don't repeat myself a million times
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,26,35,1)",
    font_color="#e8eaf0",
    font_family="DM Sans",
    title_font_family="Syne",
    title_font_size=16,
    colorway=["#f4a944", "#6c63ff", "#34d399", "#f87171", "#60c5f1", "#f4d03f"],
    xaxis=dict(gridcolor="#252b38", linecolor="#252b38", tickfont_size=11),
    yaxis=dict(gridcolor="#252b38", linecolor="#252b38", tickfont_size=11),
    margin=dict(t=50, b=40, l=50, r=20),
    hoverlabel=dict(bgcolor="#1a1f2e", bordercolor="#252b38", font_color="#e8eaf0"),
)

def vibe_chart(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


API_URL = "https://fakestoreapi.com/products"

@st.cache_data  # caching this so it doesn't re-fetch every time i touch a slider
def load_data():
    resp = requests.get(API_URL, timeout=10)
    df = pd.DataFrame(resp.json())
    df["price"]    = df["price"].astype(float)
    df["category"] = df["category"].astype(str)
    # the rating col is a nested dict, kinda annoying ngl
    df["rating_rate"]  = df["rating"].apply(lambda x: x.get("rate", 0))
    df["rating_count"] = df["rating"].apply(lambda x: x.get("count", 0))
    return df

df = load_data()


# sidebar filters
with st.sidebar:
    st.markdown("## 🛍️ Fake Store")
    st.markdown("---")
    st.markdown("**FILTERS**")

    categories = st.multiselect(
        "Category",
        options=df["category"].unique(),
        default=df["category"].unique(),
    )

    price_range = st.slider(
        "Price Range ($)",
        float(df["price"].min()),
        float(df["price"].max()),
        (float(df["price"].min()), float(df["price"].max())),
    )

    min_rating = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.1)

    st.markdown("---")
    st.markdown(f"<small style='color:#7a8299'>Showing filtered results</small>", unsafe_allow_html=True)


# filter the df based on whatever the user picked
filtered_df = df[
    df["category"].isin(categories) &
    df["price"].between(*price_range) &
    (df["rating_rate"] >= min_rating)
]


st.markdown("""
<div class="dash-header">
  <div>
    <h1>🎡 Real-Time-price-Monitoring-Alert-System</h1>
    <p>pulling live data from fakestoreapi.com &nbsp;·&nbsp; built with streamlit + plotly</p>
  </div>
</div>
""", unsafe_allow_html=True)


# the 4 stat cards at the top
c1, c2, c3, c4 = st.columns(4)

# grabbed the priciest item name for the subtitle, truncating it so it doesn't overflow
priciest = (
    filtered_df.loc[filtered_df["price"].idxmax(), "title"][:28] + "…"
    if len(filtered_df) else "—"
)

kpis = [
    (c1, "Total Products",  str(len(filtered_df)),                          "in current filter"),
    (c2, "Avg Price",       f"${filtered_df['price'].mean():.2f}",          "across categories"),
    (c3, "Highest Price",   f"${filtered_df['price'].max():.2f}",           priciest),
    (c4, "Avg Rating",      f"{filtered_df['rating_rate'].mean():.2f} ⭐",  f"{int(filtered_df['rating_count'].sum()):,} total votes"),
]

for col, label, value, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)


# --- charts ---

st.markdown('<p class="section-title">Category Breakdown</p>', unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

with ch1:
    cat_count = filtered_df["category"].value_counts().reset_index()
    cat_count.columns = ["category", "count"]
    fig_bar = px.bar(cat_count, x="category", y="count", title="Products per Category", text="count")
    fig_bar.update_traces(marker_color="#f4a944", textposition="outside", textfont_color="#e8eaf0")
    st.plotly_chart(vibe_chart(fig_bar), use_container_width=True)

with ch2:
    cat_avg = filtered_df.groupby("category")["price"].mean().reset_index()
    fig_pie = px.pie(cat_avg, names="category", values="price", title="Avg Price Share by Category", hole=0.45)
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(vibe_chart(fig_pie), use_container_width=True)


st.markdown('<p class="section-title">Price & Rating Analysis</p>', unsafe_allow_html=True)
ch3, ch4 = st.columns(2)

with ch3:
    fig_hist = px.histogram(filtered_df, x="price", nbins=20, title="Price Distribution", color_discrete_sequence=["#6c63ff"])
    fig_hist.update_traces(marker_line_color="#0d0f14", marker_line_width=1)
    st.plotly_chart(vibe_chart(fig_hist), use_container_width=True)

with ch4:
    # bubble size = how many ppl rated it, color = category
    fig_scatter = px.scatter(
        filtered_df, x="price", y="rating_rate",
        color="category", size="rating_count",
        hover_data=["title"],
        title="Price vs Rating (bigger bubble = more reviews)",
    )
    st.plotly_chart(vibe_chart(fig_scatter), use_container_width=True)


st.markdown('<p class="section-title">All Products</p>', unsafe_allow_html=True)

display_cols = ["id", "title", "category", "price", "rating_rate", "rating_count"]
st.dataframe(
    filtered_df[display_cols].rename(columns={"rating_rate": "rating", "rating_count": "votes"}),
    use_container_width=True,
    hide_index=True,
)

# export button at the bottom
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ grab the csv",
    data=csv,
    file_name="filtered_products.csv",
    mime="text/csv",
)