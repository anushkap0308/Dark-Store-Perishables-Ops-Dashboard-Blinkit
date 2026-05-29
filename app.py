"""
app.py  —  Dark Store Perishables Ops Dashboard
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perishables Ops Dashboard",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "darkstore.db"

# ── COLOURS ───────────────────────────────────────────────────────────────────
C = {
    "green":  "#00C49A",
    "yellow": "#FFD600",
    "red":    "#FF3B3B",
    "orange": "#FF6B00",
    "bg":     "#0F0F0F",
    "card":   "#1A1A1A",
    "text":   "#F0F0F0",
}

CAT_COLORS = {
    "Dairy":      "#4FC3F7",
    "Fruits":     "#FF8A65",
    "Vegetables": "#81C784",
    "Bakery":     "#FFD54F",
    "Meat":       "#F06292",
    "Beverages":  "#CE93D8",
}

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 40%, #0a1628 100%) !important;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1726 0%, #111827 100%) !important;
    border-right: 1px solid rgba(0,196,154,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #c9d8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label {
    color: #7fa8d8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* KPI metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #151e30 0%, #1a2540 100%) !important;
    border: 1px solid rgba(0,196,154,0.2) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,196,154,0.15) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #7fa8d8 !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8f4ff !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* Section headers */
h1, h2, h3, h4 {
    color: #e8f4ff !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Story section labels */
.story-label {
    display: inline-block;
    background: linear-gradient(90deg, #00C49A22, transparent);
    border-left: 3px solid #00C49A;
    color: #00C49A !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 3px 12px 3px 10px !important;
    margin-bottom: 6px !important;
    border-radius: 0 4px 4px 0 !important;
}

/* Chart section wrapper */
.chart-card {
    background: linear-gradient(135deg, #111827 0%, #151f2e 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3);
}

/* Dividers */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.07) !important;
    margin: 2rem 0 !important;
}

/* Plotly chart backgrounds */
.js-plotly-plot {
    border-radius: 12px;
}

/* Data tables */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,196,154,0.15) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00C49A, #0097a7) !important;
    color: #001a14 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.04em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00e0b0, #00b8c8) !important;
    transform: translateY(-1px) !important;
}

/* Text area */
.stTextArea textarea {
    background: #0d1117 !important;
    color: #a8d4b0 !important;
    border: 1px solid rgba(0,196,154,0.25) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #c9d8f0 !important;
    border-radius: 8px !important;
}

/* Caption */
.stCaption {
    color: #4a6080 !important;
    font-size: 0.73rem !important;
}

/* Banner hero */
.hero-banner {
    background: linear-gradient(135deg, #0a1628 0%, #0f2040 50%, #0a1a30 100%);
    border: 1px solid rgba(0,196,154,0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,196,154,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

/* Narrative callout */
.narrative-box {
    background: linear-gradient(90deg, rgba(0,196,154,0.07), rgba(0,196,154,0.02));
    border-left: 3px solid rgba(0,196,154,0.5);
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0 1rem 0;
    color: #9ec8b4 !important;
    font-size: 0.85rem;
    line-height: 1.6;
}

/* Alert box */
.alert-box {
    background: linear-gradient(90deg, rgba(255,59,59,0.1), rgba(255,59,59,0.03));
    border-left: 3px solid rgba(255,59,59,0.6);
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0 1rem 0;
    color: #f5a0a0 !important;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ── DB HELPERS ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df_wastage  = query("SELECT * FROM v_wastage_summary ORDER BY wastage_value_rs DESC")
df_fill     = query("SELECT * FROM v_fill_rate_summary ORDER BY avg_fill_rate_pct ASC")
df_vendor   = query("SELECT * FROM v_vendor_performance ORDER BY avg_lead_days DESC")
df_daily    = query("SELECT * FROM v_daily_category ORDER BY date")
df_sku      = query("SELECT * FROM sku_master")
df_inv_raw  = query("SELECT d.*, s.sku_name, s.category, s.cost_price, s.selling_price, s.vendor FROM daily_inventory d JOIN sku_master s USING(sku_id)")

df_daily["date"] = pd.to_datetime(df_daily["date"])

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Blinkit-logo.svg/320px-Blinkit-logo.svg.png", width=120)

st.sidebar.markdown("""
<div style="margin: 0.8rem 0; padding: 0.6rem 0.8rem; background: rgba(0,196,154,0.08); border-radius: 8px; border: 1px solid rgba(0,196,154,0.2);">
  <div style="font-size: 0.72rem; color: #00C49A; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;">🥬 Perishables Ops</div>
  <div style="font-size: 0.78rem; color: #7fa8d8; margin-top: 3px;">Gurgaon Dark Store · 90d</div>
</div>
""", unsafe_allow_html=True)

categories = ["All"] + sorted(df_sku["category"].unique().tolist())
sel_cat = st.sidebar.selectbox("Filter by Category", categories)

date_min = df_daily["date"].min().date()
date_max = df_daily["date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(date_min, date_max),
                                    min_value=date_min, max_value=date_max)

st.sidebar.markdown("---")
st.sidebar.markdown('<div style="font-size:0.72rem; color:#7fa8d8; letter-spacing:0.1em; text-transform:uppercase; font-weight:700; margin-bottom:8px;">⚙️ Alert Thresholds</div>', unsafe_allow_html=True)
waste_thresh  = st.sidebar.slider("Flag wastage above (%)", 5, 25, 12)
fill_thresh   = st.sidebar.slider("Flag fill rate below (%)", 70, 95, 85)
lead_thresh   = st.sidebar.slider("Flag lead time above (days)", 1.0, 3.0, 2.0, 0.1)

# ── FILTER ────────────────────────────────────────────────────────────────────
df_daily_f = df_daily[
    (df_daily["date"] >= pd.Timestamp(date_range[0])) &
    (df_daily["date"] <= pd.Timestamp(date_range[1]))
]
if sel_cat != "All":
    df_daily_f  = df_daily_f[df_daily_f["category"] == sel_cat]
    df_wastage_f = df_wastage[df_wastage["category"] == sel_cat]
    df_fill_f    = df_fill[df_fill["category"] == sel_cat]
    df_vendor_f  = df_vendor[df_vendor["category"] == sel_cat]
    df_inv_f     = df_inv_raw[df_inv_raw["category"] == sel_cat]
else:
    df_wastage_f = df_wastage.copy()
    df_fill_f    = df_fill.copy()
    df_vendor_f  = df_vendor.copy()
    df_inv_f     = df_inv_raw.copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
    <span style="font-size:2.2rem;">🥬</span>
    <div>
      <h1 style="margin:0; font-size:1.8rem; font-weight:700; color:#e8f4ff; letter-spacing:-0.02em;">
        Dark Store Perishables Intelligence Dashboard
      </h1>
      <p style="margin:4px 0 0 0; color:#5a7fa0; font-size:0.82rem; letter-spacing:0.05em;">
        SIMULATED 90-DAY OPS DATA &nbsp;·&nbsp; 22 SKUs &nbsp;·&nbsp; 6 CATEGORIES &nbsp;·&nbsp; GURGAON DARK STORE
      </p>
    </div>
  </div>
  <p style="margin:0; color:#7fa8d8; font-size:0.9rem; line-height:1.6; max-width:720px;">
    Track where your perishables bleed money — from high-waste SKUs and supplier delays to demand gaps and stockouts. 
    Every rupee lost to spoilage or missed sale is visible here.
  </p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_waste_val   = int(df_wastage_f["wastage_value_rs"].sum())
avg_fill          = round(df_fill_f["avg_fill_rate_pct"].mean(), 1)
total_stockouts   = int(df_fill_f["total_stockout_units"].sum())
avg_lead          = round(df_vendor_f["avg_lead_days"].mean(), 2)
worst_waste_cat   = df_wastage_f.groupby("category")["wastage_pct"].mean().idxmax() if not df_wastage_f.empty else "—"
low_fill_vendors  = int((df_vendor_f["avg_fill_rate_pct"] < fill_thresh).sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("💸 Wastage Value",   f"₹{total_waste_val:,}",   "90-day loss")
k2.metric("📦 Avg Fill Rate",   f"{avg_fill}%",             f"Target: 95%",
          delta_color="inverse" if avg_fill < 90 else "normal")
k3.metric("🚫 Total Stockouts", f"{total_stockouts:,}",     "units")
k4.metric("🚚 Avg Lead Time",   f"{avg_lead}d",             "vendor avg")
k5.metric("⚠️ High Wastage Cat", worst_waste_cat,           "worst offender")
k6.metric("🔴 Low Fill Vendors", f"{low_fill_vendors}",     f"below {fill_thresh}%")

st.markdown("---")

# ── STORY SECTION 1: WHERE IS THE MONEY GOING? ────────────────────────────────
st.markdown('<div class="story-label">💸 Chapter 1 — Where is the money bleeding?</div>', unsafe_allow_html=True)
st.markdown("#### 🗑️ Wastage by SKU & Fill Rate Performance")
st.markdown("""
<div class="narrative-box">
  The chart below reveals your top 10 money-losing SKUs. A longer bar = more rupees lost to spoilage. 
  The colour gradient shifts from green (acceptable) → yellow (watch) → red (critical), based on wastage % vs your threshold.
  On the right, bubbles map each SKU's fill rate vs stockout volume — bigger bubbles = more low-fill days.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    top_waste = df_wastage_f.nlargest(10, "wastage_value_rs")
    top_waste["flag"] = top_waste["wastage_pct"].apply(
        lambda x: "🔴 Critical" if x > waste_thresh else "🟡 Watch" if x > waste_thresh*0.7 else "🟢 OK"
    )
    fig = px.bar(
        top_waste, x="wastage_value_rs", y="sku_name",
        orientation="h", color="wastage_pct",
        color_continuous_scale=[[0,"#00C49A"],[0.5,"#FFD600"],[1,"#FF3B3B"]],
        labels={"wastage_value_rs": "Wastage Value (₹)", "sku_name": "", "wastage_pct": "Wastage %"},
        hover_data=["category", "wastage_pct", "shelf_life_days", "flag"],
    )
    fig.update_layout(
        height=360, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d8f0", family="Space Grotesk"),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(
            tickfont=dict(color="#7fa8d8", size=10),
            title=dict(text="Waste%", font=dict(color="#7fa8d8", size=10)),
            len=0.6, thickness=10,
            x=1.0,
        ),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11, color="#c9d8f0")),
        xaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
        hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
    )
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.scatter(
        df_fill_f, x="avg_fill_rate_pct", y="total_stockout_units",
        color="category", size="low_fill_days",
        color_discrete_map=CAT_COLORS,
        labels={"avg_fill_rate_pct":"Avg Fill Rate %","total_stockout_units":"Total Stockout Units","low_fill_days":"Low Fill Days"},
        hover_data=["vendor","low_fill_days"],
    )
    fig2.add_vline(x=fill_thresh, line_dash="dash", line_color="#FF3B3B",
                   annotation_text=f"Threshold {fill_thresh}%",
                   annotation_font_color="#FF3B3B", annotation_font_size=11)
    fig2.update_layout(
        height=360, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d8f0", family="Space Grotesk"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#c9d8f0"),
                    bordercolor="rgba(255,255,255,0.08)", borderwidth=1),
        xaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
        hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── STORY SECTION 2: HOW IS DEMAND MOVING? ────────────────────────────────────
st.markdown('<div class="story-label">📈 Chapter 2 — How is demand moving across categories?</div>', unsafe_allow_html=True)
st.markdown("#### 📈 7-Day Rolling Demand &amp; Daily Wastage Trends")
st.markdown("""
<div class="narrative-box">
  Demand rhythms reveal replenishment windows. The rolling average smooths noise — watch for category dips that 
  precede wastage spikes on the right chart. When demand drops but supply stays constant, waste climbs.
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    pivot = df_daily_f.pivot_table(index="date", columns="category",
                                    values="units_sold", aggfunc="sum").fillna(0)
    pivot_roll = pivot.rolling(7).mean().dropna()
    fig3 = go.Figure()
    for cat in pivot_roll.columns:
        fig3.add_trace(go.Scatter(
            x=pivot_roll.index, y=pivot_roll[cat], name=cat,
            line=dict(width=2.5, color=CAT_COLORS.get(cat, "#aaa")),
            mode="lines",
            fill="tozeroy",
            fillcolor=f"rgba{tuple(int(CAT_COLORS.get(cat, '#aaa').lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.07,)}",
        ))
    fig3.update_layout(
        height=320, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d8f0", family="Space Grotesk"),
        legend=dict(orientation="h", y=-0.25, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11, color="#c9d8f0")),
        xaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
        hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    agg = df_daily_f.groupby("date")[["units_sold","units_wasted"]].sum().reset_index()
    agg["wastage_pct"] = (agg["units_wasted"] / (agg["units_sold"] + agg["units_wasted"]) * 100).round(2)
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Bar(x=agg["date"], y=agg["units_wasted"],
                           name="Units Wasted", marker_color="#FF3B3B",
                           marker_line_width=0, opacity=0.75), secondary_y=False)
    fig4.add_trace(go.Scatter(x=agg["date"], y=agg["wastage_pct"],
                               name="Wastage %",
                               line=dict(color="#FFD600", width=2.5),
                               mode="lines"), secondary_y=True)
    fig4.update_layout(
        height=320, margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d8f0", family="Space Grotesk"),
        legend=dict(orientation="h", y=-0.25, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11, color="#c9d8f0")),
        barmode="overlay",
        xaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.03)"),
        hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
    )
    fig4.update_yaxes(title_text="Units Wasted", secondary_y=False,
                      title_font=dict(color="#FF3B3B", size=11),
                      tickfont=dict(size=10, color="#7fa8d8"),
                      gridcolor="rgba(255,255,255,0.04)")
    fig4.update_yaxes(title_text="Wastage %", secondary_y=True,
                      title_font=dict(color="#FFD600", size=11),
                      tickfont=dict(size=10, color="#7fa8d8"))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── STORY SECTION 3: VENDOR HEALTH ────────────────────────────────────────────
st.markdown('<div class="story-label">🚚 Chapter 3 — Which vendors are dragging you down?</div>', unsafe_allow_html=True)
st.markdown("#### 🚚 Vendor Performance: Lead Time vs Fill Rate")

# Danger zone highlight
danger_vendors = df_vendor_f[
    (df_vendor_f["avg_lead_days"] > lead_thresh) &
    (df_vendor_f["avg_fill_rate_pct"] < fill_thresh)
]
if not danger_vendors.empty:
    vendor_names = ", ".join(danger_vendors["vendor"].tolist())
    st.markdown(f"""
    <div class="alert-box">
      ⚠️ <strong>Danger zone vendors:</strong> {vendor_names} — high lead time AND low fill rate. Immediate review recommended.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="narrative-box">
      Bottom-right quadrant = danger zone. Vendors there have both slow delivery and poor fill rates. 
      Bubble size indicates total stockout count. Aim for top-left.
    </div>
    """, unsafe_allow_html=True)

fig5 = px.scatter(
    df_vendor_f, x="avg_lead_days", y="avg_fill_rate_pct",
    color="category", size="total_stockouts", text="vendor",
    color_discrete_map=CAT_COLORS,
    labels={"avg_lead_days":"Avg Lead Time (days)","avg_fill_rate_pct":"Avg Fill Rate %",
            "total_stockouts":"Total Stockouts"},
    hover_data=["total_stockouts","max_lead_days"],
)
fig5.add_vline(x=lead_thresh, line_dash="dash", line_color="#FF6B00",
               annotation_text=f"Lead flag >{lead_thresh}d",
               annotation_font_color="#FF6B00", annotation_font_size=11)
fig5.add_hline(y=fill_thresh, line_dash="dash", line_color="#FF3B3B",
               annotation_text=f"Fill floor {fill_thresh}%",
               annotation_font_color="#FF3B3B", annotation_font_size=11)
fig5.update_traces(textposition="top center",
                   textfont=dict(size=9, color="#c9d8f0"))
fig5.add_annotation(x=lead_thresh+0.05, y=fill_thresh-2,
                     text="⚠️ Danger Zone", showarrow=False,
                     font=dict(color="#FF3B3B", size=11))

# Add quadrant shading
fig5.add_shape(type="rect",
    x0=lead_thresh, x1=df_vendor_f["avg_lead_days"].max()+0.3,
    y0=df_vendor_f["avg_fill_rate_pct"].min()-1, y1=fill_thresh,
    fillcolor="rgba(255,59,59,0.05)", line_width=0)

fig5.update_layout(
    height=400, margin=dict(l=0,r=0,t=20,b=0),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c9d8f0", family="Space Grotesk"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#c9d8f0"),
                bordercolor="rgba(255,255,255,0.08)", borderwidth=1),
    xaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
    yaxis=dict(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)"),
    hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── STORY SECTION 4: SQL EXPLORER ─────────────────────────────────────────────
st.markdown('<div class="story-label">🔍 Chapter 4 — Dig deeper with SQL</div>', unsafe_allow_html=True)
st.markdown("#### 🔍 SQL Explorer — Run Your Own Queries")

PRESET_QUERIES = {
    "Top 5 highest wastage SKUs":
        "SELECT sku_name, category, wastage_pct, wastage_value_rs FROM v_wastage_summary ORDER BY wastage_value_rs DESC LIMIT 5",
    "Fill rate below threshold by vendor":
        f"SELECT vendor, category, avg_fill_rate_pct, total_stockout_units FROM v_vendor_performance WHERE avg_fill_rate_pct < {fill_thresh} ORDER BY avg_fill_rate_pct ASC",
    "Vendor lead time ranking":
        "SELECT vendor, category, avg_lead_days, max_lead_days, total_stockouts FROM v_vendor_performance ORDER BY avg_lead_days DESC",
    "Daily stockouts last 7 days":
        "SELECT date, category, stockout_units FROM v_daily_category WHERE date >= date('now','-7 days') ORDER BY date DESC, stockout_units DESC",
    "SKU profitability vs wastage loss":
        "SELECT s.sku_name, s.category, s.selling_price - s.cost_price AS margin_rs, w.wastage_value_rs, ROUND(w.wastage_value_rs * 1.0 / NULLIF((s.selling_price - s.cost_price),0), 1) AS wastage_to_margin_ratio FROM v_wastage_summary w JOIN sku_master s USING(sku_id) ORDER BY wastage_to_margin_ratio DESC",
    "Custom query": "",
}

preset = st.selectbox("Preset queries", list(PRESET_QUERIES.keys()))
sql_input = st.text_area("SQL", value=PRESET_QUERIES[preset], height=80)

if st.button("▶ Run Query", type="primary"):
    try:
        result = query(sql_input)
        st.dataframe(result, use_container_width=True)
        st.caption(f"Returned {len(result)} rows")
    except Exception as e:
        st.error(f"Query error: {e}")

st.markdown("---")

# ── STORY SECTION 5: SKU DEEP DIVE ────────────────────────────────────────────
st.markdown('<div class="story-label">🔬 Chapter 5 — SKU deep dive</div>', unsafe_allow_html=True)
st.markdown("#### 🔬 SKU Deep Dive")
st.markdown("""
<div class="narrative-box">
  Zoom into a single SKU to understand its demand-supply story — where demand exceeded supply, 
  where product was wasted, and how the fill rate behaved over the 90-day window.
</div>
""", unsafe_allow_html=True)

sku_options = df_sku["sku_name"].tolist()
sel_sku = st.selectbox("Select SKU", sku_options)
sku_id  = df_sku[df_sku["sku_name"] == sel_sku]["sku_id"].values[0]

sku_data = df_inv_raw[df_inv_raw["sku_id"] == sku_id].copy()
sku_data["date"] = pd.to_datetime(sku_data["date"])
sku_data = sku_data.sort_values("date")

s1, s2, s3, s4 = st.columns(4)
s1.metric("Avg Daily Demand", f"{sku_data['demand'].mean():.0f} units")
s2.metric("Avg Fill Rate",    f"{sku_data['fill_rate'].mean()*100:.1f}%")
s3.metric("Total Wasted",     f"{sku_data['units_wasted'].sum()} units")
s4.metric("Wastage Value",    f"₹{(sku_data['units_wasted'] * sku_data['cost_price']).sum():,.0f}")

fig6 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                     subplot_titles=("Demand vs Sold vs Wasted", "Fill Rate & Stockouts"),
                     vertical_spacing=0.12)
fig6.add_trace(go.Scatter(x=sku_data["date"], y=sku_data["demand"],
               name="Demand", line=dict(color="#4a6080", dash="dot", width=1.5)), row=1, col=1)
fig6.add_trace(go.Scatter(x=sku_data["date"], y=sku_data["units_sold"],
               name="Sold", line=dict(color=C["green"], width=2.5),
               fill="tozeroy", fillcolor="rgba(0,196,154,0.08)"), row=1, col=1)
fig6.add_trace(go.Bar(x=sku_data["date"], y=sku_data["units_wasted"],
               name="Wasted", marker_color=C["red"],
               marker_line_width=0, opacity=0.7), row=1, col=1)
fig6.add_trace(go.Scatter(x=sku_data["date"], y=sku_data["fill_rate"]*100,
               name="Fill Rate %", line=dict(color=C["yellow"], width=2.5)), row=2, col=1)
fig6.add_trace(go.Bar(x=sku_data["date"], y=sku_data["stockout_units"],
               name="Stockouts", marker_color=C["orange"],
               marker_line_width=0, opacity=0.7), row=2, col=1)
fig6.update_layout(
    height=440, margin=dict(l=0,r=0,t=30,b=0),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c9d8f0", family="Space Grotesk"),
    legend=dict(orientation="h", y=-0.08, bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#c9d8f0")),
    hoverlabel=dict(bgcolor="#1a2540", font_color="#e8f4ff", font_family="Space Grotesk"),
)
fig6.update_xaxes(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.03)")
fig6.update_yaxes(tickfont=dict(size=10, color="#7fa8d8"), gridcolor="rgba(255,255,255,0.04)")
for ann in fig6.layout.annotations:
    ann.font.color = "#7fa8d8"
    ann.font.size = 12

st.plotly_chart(fig6, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between; padding:0.5rem 0;">
  <p style="color:#2a4060; font-size:0.73rem; margin:0;">
    Built by Anushka Pandey &nbsp;·&nbsp; Thapar Institute 2027 &nbsp;·&nbsp; Python + SQL + Streamlit &nbsp;·&nbsp; Perishables Ops simulation
  </p>
  <p style="color:#2a4060; font-size:0.73rem; margin:0;">🥬 Perishables Ops · Gurgaon</p>
</div>
""", unsafe_allow_html=True)
