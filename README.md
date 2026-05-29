# 🥬 Dark Store Perishables Intelligence Dashboard

**Stack:** Python · Pandas · SQLite (SQL) · Streamlit · Plotly  
**Simulates:** 90-day ops data for a 22-SKU, 6-category Gurgaon dark store

---

## Setup (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data + build SQLite DB
python generate_data.py

# 3. Launch dashboard
streamlit run app.py
```

---

## What's inside

| Module | What it does |
|--------|-------------|
| `generate_data.py` | Builds synthetic inventory + sales data; loads into SQLite with analytical views |
| `app.py` | Streamlit dashboard with 6 analytical sections |
| `darkstore.db` | SQLite database (auto-generated) |

## SQL Views (queryable in the app)
- `v_wastage_summary` — wastage % and ₹ loss per SKU
- `v_fill_rate_summary` — fill rate and stockouts by category + vendor  
- `v_vendor_performance` — lead time, fill rate, stockout count per vendor
- `v_daily_category` — daily aggregates by category

## Dashboard Sections
1. **KPI Cards** — Wastage value, fill rate, stockouts, lead time
2. **Wastage by SKU** — Top 10 loss drivers with threshold flags
3. **Fill Rate Scatter** — Category × vendor with danger zone
4. **7-Day Rolling Demand** — Trend by category
5. **Wastage vs Sales Trend** — Daily bar + line combo
6. **Vendor Matrix** — Lead time vs fill rate quadrant chart
7. **SQL Explorer** — 5 preset queries + custom SQL runner
8. **SKU Deep Dive** — Per-SKU demand, wastage, fill rate over time
