"""
generate_data.py
Generates synthetic dark-store perishables data and loads into SQLite.
Run this ONCE before launching the dashboard.
"""

import pandas as pd
import numpy as np
import sqlite3
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
DB_PATH = "darkstore.db"
N_DAYS  = 90          # 3 months of history
START   = datetime(2024, 10, 1)

# ── MASTER DATA ──────────────────────────────────────────────────────────────
CATEGORIES = {
    "Dairy":      {"shelf_life": 7,  "margin": 0.18, "vendors": ["MilkMart", "DairyBest"]},
    "Fruits":     {"shelf_life": 4,  "margin": 0.22, "vendors": ["FreshFarms", "OrganicHub"]},
    "Vegetables": {"shelf_life": 3,  "margin": 0.20, "vendors": ["GreenLeaf", "FreshFarms"]},
    "Bakery":     {"shelf_life": 2,  "margin": 0.30, "vendors": ["BakeCo", "LocalBread"]},
    "Meat":       {"shelf_life": 3,  "margin": 0.25, "vendors": ["MeatMaster", "FreshCut"]},
    "Beverages":  {"shelf_life": 30, "margin": 0.15, "vendors": ["DrinkCo", "CoolSip"]},
}

SKUS = [
    # Dairy
    ("SKU001", "Full Cream Milk 1L",     "Dairy",      45, 58),
    ("SKU002", "Greek Yogurt 400g",      "Dairy",      38, 52),
    ("SKU003", "Paneer 200g",            "Dairy",      65, 80),
    ("SKU004", "Butter 100g",            "Dairy",      52, 68),
    ("SKU005", "Cheddar Cheese 200g",    "Dairy",      95, 120),
    # Fruits
    ("SKU006", "Banana Dozen",           "Fruits",     28, 40),
    ("SKU007", "Apple Royal 1kg",        "Fruits",     85, 110),
    ("SKU008", "Watermelon Whole",       "Fruits",     60, 85),
    ("SKU009", "Mango Alphonso 6pc",     "Fruits",     120, 155),
    ("SKU010", "Strawberry 250g",        "Fruits",     95, 130),
    # Vegetables
    ("SKU011", "Tomato 500g",            "Vegetables", 18, 28),
    ("SKU012", "Spinach 250g",           "Vegetables", 22, 32),
    ("SKU013", "Onion 1kg",              "Vegetables", 30, 42),
    ("SKU014", "Capsicum Mix 500g",      "Vegetables", 45, 60),
    ("SKU015", "Baby Potato 500g",       "Vegetables", 35, 48),
    # Bakery
    ("SKU016", "Whole Wheat Bread",      "Bakery",     38, 52),
    ("SKU017", "Croissant 2pc",          "Bakery",     55, 75),
    ("SKU018", "Burger Buns 6pc",        "Bakery",     42, 58),
    # Meat
    ("SKU019", "Chicken Breast 500g",    "Meat",       185, 240),
    ("SKU020", "Eggs 12pc",              "Meat",       78, 95),
    # Beverages
    ("SKU021", "Orange Juice 1L",        "Beverages",  85, 110),
    ("SKU022", "Green Tea 25 bags",      "Beverages",  120, 155),
]

# ── VENDOR LEAD TIME (days) ──────────────────────────────────────────────────
VENDOR_LEAD = {
    "MilkMart":   {"avg": 1.2, "std": 0.3},
    "DairyBest":  {"avg": 1.5, "std": 0.5},
    "FreshFarms": {"avg": 1.0, "std": 0.2},
    "OrganicHub": {"avg": 2.5, "std": 0.8},  # unreliable
    "GreenLeaf":  {"avg": 1.1, "std": 0.2},
    "BakeCo":     {"avg": 0.8, "std": 0.1},
    "LocalBread": {"avg": 0.9, "std": 0.2},
    "MeatMaster": {"avg": 1.3, "std": 0.3},
    "FreshCut":   {"avg": 1.8, "std": 0.6},
    "DrinkCo":    {"avg": 2.0, "std": 0.4},
    "CoolSip":    {"avg": 2.2, "std": 0.5},
}

# ── BUILD SKU MASTER ─────────────────────────────────────────────────────────
sku_rows = []
for sku_id, name, cat, cost, price in SKUS:
    vendors = CATEGORIES[cat]["vendors"]
    vendor  = random.choice(vendors)
    sku_rows.append({
        "sku_id":       sku_id,
        "sku_name":     name,
        "category":     cat,
        "cost_price":   cost,
        "selling_price":price,
        "shelf_life_days": CATEGORIES[cat]["shelf_life"],
        "vendor":       vendor,
        "reorder_point": random.randint(10, 20),
    })
df_sku = pd.DataFrame(sku_rows)

# ── BUILD DAILY INVENTORY & SALES ────────────────────────────────────────────
inv_rows = []
for day_offset in range(N_DAYS):
    date = START + timedelta(days=day_offset)
    is_weekend = date.weekday() >= 5
    day_mult = 1.35 if is_weekend else 1.0
    # festival bump (Diwali week simulation)
    if 20 <= day_offset <= 27:
        day_mult *= 1.6

    for _, sku in df_sku.iterrows():
        cat = sku["category"]
        # base demand with category seasonality
        base = {
            "Dairy":      np.random.poisson(55),
            "Fruits":     np.random.poisson(40),
            "Vegetables": np.random.poisson(70),
            "Bakery":     np.random.poisson(30),
            "Meat":       np.random.poisson(25),
            "Beverages":  np.random.poisson(20),
        }[cat]
        demand = int(base * day_mult)

        # opening stock (simulate)
        opening = random.randint(30, 120)

        # stockout if opening < demand
        actual_sold = min(demand, opening)
        stockout    = max(0, demand - opening)

        # wastage: short-shelf items waste more when oversupplied
        shelf = sku["shelf_life_days"]
        waste_rate = max(0, np.random.normal(
            0.05 if shelf > 5 else 0.12 if shelf > 2 else 0.18,
            0.03
        ))
        units_wasted = int(opening * waste_rate)

        # vendor lead time
        vl   = VENDOR_LEAD[sku["vendor"]]
        lead = round(max(0.5, np.random.normal(vl["avg"], vl["std"])), 1)

        # fill rate
        fill_rate = round(actual_sold / demand, 4) if demand > 0 else 1.0

        inv_rows.append({
            "date":          date.strftime("%Y-%m-%d"),
            "sku_id":        sku["sku_id"],
            "opening_stock": opening,
            "demand":        demand,
            "units_sold":    actual_sold,
            "units_wasted":  units_wasted,
            "stockout_units":stockout,
            "fill_rate":     fill_rate,
            "vendor_lead_days": lead,
            "restock_ordered": 1 if opening <= sku["reorder_point"] else 0,
        })

df_inv = pd.DataFrame(inv_rows)

# ── WRITE TO SQLITE ───────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df_sku.to_sql("sku_master",    conn, if_exists="replace", index=False)
df_inv.to_sql("daily_inventory", conn, if_exists="replace", index=False)

# ── CREATE ANALYTICAL VIEWS ───────────────────────────────────────────────────
conn.executescript("""
DROP VIEW IF EXISTS v_wastage_summary;
CREATE VIEW v_wastage_summary AS
SELECT
    d.sku_id,
    s.sku_name,
    s.category,
    s.vendor,
    s.shelf_life_days,
    SUM(d.units_wasted)                          AS total_units_wasted,
    SUM(d.units_sold)                            AS total_units_sold,
    ROUND(SUM(d.units_wasted)*1.0 /
          NULLIF(SUM(d.units_sold)+SUM(d.units_wasted),0)*100, 2) AS wastage_pct,
    ROUND(SUM(d.units_wasted) * s.cost_price, 0) AS wastage_value_rs
FROM daily_inventory d
JOIN sku_master s USING (sku_id)
GROUP BY d.sku_id;

DROP VIEW IF EXISTS v_fill_rate_summary;
CREATE VIEW v_fill_rate_summary AS
SELECT
    s.category,
    s.vendor,
    ROUND(AVG(d.fill_rate)*100, 2)               AS avg_fill_rate_pct,
    SUM(d.stockout_units)                        AS total_stockout_units,
    COUNT(CASE WHEN d.fill_rate < 0.85 THEN 1 END) AS low_fill_days
FROM daily_inventory d
JOIN sku_master s USING (sku_id)
GROUP BY s.category, s.vendor;

DROP VIEW IF EXISTS v_vendor_performance;
CREATE VIEW v_vendor_performance AS
SELECT
    s.vendor,
    s.category,
    ROUND(AVG(d.vendor_lead_days), 2)            AS avg_lead_days,
    ROUND(MAX(d.vendor_lead_days), 2)            AS max_lead_days,
    SUM(d.stockout_units)                        AS total_stockouts,
    ROUND(AVG(d.fill_rate)*100, 2)               AS avg_fill_rate_pct
FROM daily_inventory d
JOIN sku_master s USING (sku_id)
GROUP BY s.vendor, s.category;

DROP VIEW IF EXISTS v_daily_category;
CREATE VIEW v_daily_category AS
SELECT
    d.date,
    s.category,
    SUM(d.units_sold)    AS units_sold,
    SUM(d.demand)        AS total_demand,
    SUM(d.units_wasted)  AS units_wasted,
    SUM(d.stockout_units)AS stockout_units,
    ROUND(AVG(d.fill_rate)*100,2) AS avg_fill_rate
FROM daily_inventory d
JOIN sku_master s USING (sku_id)
GROUP BY d.date, s.category;
""")

conn.commit()
conn.close()
print(f"✅ Database created: {DB_PATH}")
print(f"   SKUs: {len(df_sku)} | Days: {N_DAYS} | Rows: {len(df_inv)}")
