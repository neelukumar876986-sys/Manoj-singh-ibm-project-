# 🛒 Retail Sales Analytics Dashboard

A Python data analytics project that loads, cleans, analyses, and visualises a retail sales dataset using **Pandas**, **NumPy**, **Plotly**, and **Streamlit**. The project covers the full analytics pipeline — from raw CSV ingestion to actionable business insights — served through an interactive multi-tab web dashboard.

---

## 📁 Project Structure

```
├── app.py                    # Streamlit frontend (7-tab dashboard)
├── data_analytics.py         # Core analytics engine (load, clean, analyse)
├── retail_sales_dataset.csv  # Source dataset (4,310 orders)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 📊 Dataset Overview

**File:** `retail_sales_dataset.csv`  
**Rows:** ~4,310 orders | **Columns:** 21

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `order_date` | Date the order was placed |
| `customer_id` / `customer_name` | Customer details |
| `age` / `gender` | Customer demographics |
| `region` / `city` | Geographic information |
| `product_category` / `product_name` | Product details |
| `quantity` | Units ordered |
| `unit_price` | Price per unit (₹) |
| `discount_pct` | Discount applied (0–1) |
| `sales_amount` | Recorded revenue after discount |
| `profit` | Net profit on the order |
| `shipping_cost` | Shipping fee charged |
| `payment_method` | Payment channel used |
| `customer_satisfaction` | Rating (1–5) |
| `return_flag` | Whether the order was returned |
| `order_status` | Delivered / Returned / Cancelled / Pending |
| `days_to_ship` | Fulfilment speed in days |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone / Download the project

```bash
git clone <your-repo-url>
cd retail-sales-analytics
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**
```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.20.0
```

### 3. Run the dashboard

```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

---

## 🔬 Analytics Pipeline

### Step 1 — Load Data (`load_data`)
Reads `retail_sales_dataset.csv` into a Pandas DataFrame using `pd.read_csv()`.

### Step 2 — Clean & Validate (`clean_data`)
Returns a cleaned DataFrame **and** a quality report dictionary.

| Issue | Fix Applied |
|---|---|
| Mixed date formats (YYYY-MM-DD and DD/MM/YYYY) | `pd.to_datetime(..., infer_format=False)` |
| Non-numeric values in numeric columns | `pd.to_numeric(..., errors="coerce")` → NaN |
| Missing `discount_pct` | Filled with `0` (no discount assumed) |
| Missing `customer_satisfaction` | Filled with column **median** |
| Missing `age` / `days_to_ship` | Filled with column **median** |
| Fully duplicate rows | Dropped with `drop_duplicates()` |

### Step 3 — Calculate Sales
A new column is derived:

```python
df["calculated_sales"] = df["quantity"] * df["unit_price"]
```

This represents **gross pre-discount sales**. The difference from `sales_amount` reflects discounts, returns, and adjustments.

### Step 4 — Group & Summarise
Aggregation functions produce totals, counts, and averages across multiple dimensions:

| Function | Grouped By | Metrics |
|---|---|---|
| `overall_kpis()` | Entire dataset | Revenue, profit, orders, AOV, margin, satisfaction, return rate |
| `by_category()` | Product category | Revenue, profit, margin %, quantity, avg discount |
| `by_region()` | Region | Revenue, profit, orders, AOV |
| `by_gender()` | Gender | Orders, revenue, avg satisfaction |
| `by_payment()` | Payment method | Orders, revenue |
| `monthly_trend()` | Month | Revenue, profit, order count |
| `top_products()` | Product name | Revenue, quantity, profit |
| `by_order_status()` | Order status | Count, revenue |
| `age_distribution()` | Age group (binned) | Revenue |

### Step 5 — Charts
All charts are built with **Plotly** (interactive, hover-enabled):

| Chart Type | Used For |
|---|---|
| Grouped Bar | Revenue vs Profit by category |
| Horizontal Bar | Product ranking, region revenue, payment methods, profit margin |
| Donut / Pie | Order status distribution, region share, gender split |
| Dual-axis Line + Bar | Monthly revenue, profit, and order count trend |
| Heatmap | Region × Category revenue matrix |
| Scatter | Discount % vs Revenue (sampled) |
| Bubble | Profit vs Revenue by category (size = quantity) |
| Histogram | Customer satisfaction distribution |
| Bar (age groups) | Revenue by age group |

### Step 6 — Business Insights (`generate_insights`)
Automatically generates plain-English insight strings from the computed KPIs:

- Top revenue category and its profit margin
- Top-performing region
- Return rate assessment (flagged if > 15%)
- Average customer satisfaction score
- Profit margin health check
- Most preferred payment method
- Discount level assessment

---

## 🖥️ Dashboard Tabs

| Tab | Content |
|---|---|
| **📊 Overview** | 8 KPI metric cards, revenue vs profit bar chart, order status donut pie + table |
| **🗂️ By Category** | Summary table with gradient styling, profit margin bar, top-10 products chart |
| **🌍 By Region** | Regional table, revenue bar + pie charts, region × category heatmap |
| **📈 Trends** | Dual-axis monthly trend chart, yearly revenue comparison, monthly data table |
| **👥 Customers** | Gender analysis, revenue by age group, payment method breakdown, satisfaction histogram |
| **🧹 Data Quality** | Missing-value report (before & after), cleaning steps applied, raw data preview |
| **💡 Insights** | Auto-generated insight cards, discount scatter, profit-revenue bubble chart, recommendations |

### Sidebar Filters
All tabs respond live to the following sidebar filters:

- **Order Year** — filter by one or more years
- **Region** — filter by geographic region
- **Product Category** — filter by category
- **Order Status** — include/exclude Delivered, Returned, Cancelled, Pending

---

## 📸 Key Metrics Displayed

| KPI | Description |
|---|---|
| Total Orders | Count of all orders in the filtered dataset |
| Total Revenue | Sum of `sales_amount` |
| Total Profit | Sum of `profit` |
| Avg Order Value | Mean `sales_amount` per order |
| Total Quantity Sold | Sum of `quantity` |
| Avg Profit Margin | Mean of `profit / sales_amount` × 100 |
| Avg Satisfaction | Mean `customer_satisfaction` score |
| Return Rate % | % of orders with `return_flag = True` |

---

## 🛠️ Tech Stack

| Library | Version | Role |
|---|---|---|
| [Streamlit](https://streamlit.io) | ≥ 1.35 | Web frontend & UI components |
| [Pandas](https://pandas.pydata.org) | ≥ 2.0 | Data loading, cleaning, aggregation |
| [NumPy](https://numpy.org) | ≥ 1.26 | Numeric operations |
| [Plotly](https://plotly.com/python/) | ≥ 5.20 | Interactive charts |

---

## 📂 File Reference

### `data_analytics.py`
Pure Python analytics module with no UI code. Import it independently to run analyses in a notebook or script:

```python
import data_analytics as da

df_raw = da.load_data("retail_sales_dataset.csv")
df, report = da.clean_data(df_raw)
kpis = da.overall_kpis(df)
print(kpis)
```

### `app.py`
Streamlit application. All chart rendering, layout, sidebar filters, and tab navigation live here. Calls `data_analytics` functions and passes results to Plotly for visualisation.

---

## 📌 Business Recommendations Generated

1. **Invest in Top Categories** — Focus marketing on highest-revenue categories.
2. **Reduce Return Rate** — Investigate product quality, descriptions, and shipping.
3. **Optimise Discounts** — Avoid steep discounts in low-margin categories.
4. **Expand in Top Regions** — Scale what works; pilot growth in under-served areas.
5. **Loyalty for High-Value Age Groups** — Target top revenue-generating demographics.
6. **Payment Diversification** — Ensure preferred methods are available; incentivise high-value ones.

---

## 📄 License

This project is for educational and analytical purposes.
