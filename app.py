"""
app.py
------
Streamlit frontend for Retail Sales Analytics Dashboard.
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data_analytics as da

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS  — clean, readable styling
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fa; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 18px 22px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }
    .kpi-label { font-size: 13px; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #1f2937; margin-top: 4px; }

    /* Section headers */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin: 28px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Insight card */
    .insight-card {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 15px;
        color: #1e3a5f;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING  (cached)
# ============================================================
@st.cache_data(show_spinner="Loading dataset…")
def get_data():
    raw = da.load_data("retail_sales_dataset.csv")
    df, report = da.clean_data(raw)
    return df, report

df_full, quality_report = get_data()

# ============================================================
# SIDEBAR — FILTERS
# ============================================================
with st.sidebar:
    st.markdown("## 🛒 Retail Analytics")
    st.markdown("---")

    st.markdown("### 🔍 Filters")

    # Year filter
    available_years = sorted(df_full["year"].dropna().unique().astype(int).tolist())
    selected_years = st.multiselect(
        "Order Year",
        options=available_years,
        default=available_years,
    )

    # Region filter
    regions = sorted(df_full["region"].dropna().unique().tolist())
    selected_regions = st.multiselect(
        "Region",
        options=regions,
        default=regions,
    )

    # Category filter
    categories = sorted(df_full["product_category"].dropna().unique().tolist())
    selected_categories = st.multiselect(
        "Product Category",
        options=categories,
        default=categories,
    )

    # Order Status filter
    statuses = sorted(df_full["order_status"].dropna().unique().tolist())
    selected_statuses = st.multiselect(
        "Order Status",
        options=statuses,
        default=statuses,
    )

    st.markdown("---")
    st.caption("Data: retail_sales_dataset.csv")

# Apply filters
df = df_full[
    df_full["year"].isin(selected_years) &
    df_full["region"].isin(selected_regions) &
    df_full["product_category"].isin(selected_categories) &
    df_full["order_status"].isin(selected_statuses)
]

if df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust the sidebar filters.")
    st.stop()

# ============================================================
# NAVIGATION TABS
# ============================================================
tab_overview, tab_category, tab_region, tab_trends, tab_customers, tab_quality, tab_insights = st.tabs([
    "📊 Overview",
    "🗂️ By Category",
    "🌍 By Region",
    "📈 Trends",
    "👥 Customers",
    "🧹 Data Quality",
    "💡 Insights",
])

kpis = da.overall_kpis(df)

# ------------------------------------------------------------------
# TAB 1 — OVERVIEW
# ------------------------------------------------------------------
with tab_overview:
    st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    def kpi_card(col, label, value):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>""", unsafe_allow_html=True)

    kpi_card(c1, "Total Orders",        f"{kpis['total_orders']:,}")
    kpi_card(c2, "Total Revenue",       f"₹{kpis['total_revenue']:,.0f}")
    kpi_card(c3, "Total Profit",        f"₹{kpis['total_profit']:,.0f}")
    kpi_card(c4, "Avg Order Value",     f"₹{kpis['avg_order_value']:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    kpi_card(c5, "Qty Sold",            f"{kpis['total_quantity_sold']:,}")
    kpi_card(c6, "Avg Profit Margin",   f"{kpis['avg_profit_margin']:.1f}%")
    kpi_card(c7, "Avg Satisfaction",    f"{kpis['avg_customer_satisfaction']:.2f} / 5")
    kpi_card(c8, "Return Rate",         f"{kpis['return_rate_pct']:.1f}%")

    st.markdown('<div class="section-title">Sales = Quantity × Unit Price (Calculated)</div>', unsafe_allow_html=True)
    st.info(
        "The **Calculated Sales** column was derived as `quantity × unit_price` (gross, pre-discount).  \n"
        f"**Total Calculated Sales:** ₹{kpis['total_calculated_sales']:,.0f}  |  "
        f"**Total Recorded Revenue (sales_amount):** ₹{kpis['total_revenue']:,.0f}  \n"
        "The difference reflects discounts, returns, and adjustments captured in `sales_amount`."
    )

    st.markdown('<div class="section-title">Revenue vs Profit by Category</div>', unsafe_allow_html=True)
    cat_df = da.by_category(df)
    fig_bar = px.bar(
        cat_df,
        x="product_category",
        y=["total_revenue", "total_profit"],
        barmode="group",
        labels={"value": "Amount (₹)", "product_category": "Category", "variable": "Metric"},
        color_discrete_map={"total_revenue": "#3b82f6", "total_profit": "#10b981"},
        template="plotly_white",
    )
    fig_bar.update_layout(legend_title_text="", height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="section-title">Order Status Distribution</div>', unsafe_allow_html=True)
    status_df = da.by_order_status(df)
    col_left, col_right = st.columns(2)
    with col_left:
        fig_pie = px.pie(
            status_df,
            names="order_status",
            values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white",
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(height=380, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.dataframe(
            status_df.rename(columns={
                "order_status":"Status","count":"Orders","total_revenue":"Revenue (₹)"
            }).style.format({"Revenue (₹)": "₹{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

# ------------------------------------------------------------------
# TAB 2 — BY CATEGORY
# ------------------------------------------------------------------
with tab_category:
    st.markdown('<div class="section-title">Category Summary</div>', unsafe_allow_html=True)
    cat_df = da.by_category(df)

    # Format for display
    cat_display = cat_df.copy()
    cat_display.columns = [
        "Category","Orders","Revenue (₹)","Profit (₹)",
        "Avg Order (₹)","Qty Sold","Avg Discount","Avg Satisfaction","Profit Margin %"
    ]
    st.dataframe(
        cat_display.style.format({
            "Revenue (₹)":    "₹{:,.0f}",
            "Profit (₹)":     "₹{:,.0f}",
            "Avg Order (₹)":  "₹{:,.0f}",
            "Avg Discount":   "{:.1%}",
            "Avg Satisfaction":"{:.2f}",
            "Profit Margin %": "{:.1f}%",
        }).background_gradient(subset=["Revenue (₹)"], cmap="Blues"),
        use_container_width=True, hide_index=True
    )

    st.markdown('<div class="section-title">Profit Margin % by Category</div>', unsafe_allow_html=True)
    fig_margin = px.bar(
        cat_df.sort_values("profit_margin_pct"),
        x="profit_margin_pct",
        y="product_category",
        orientation="h",
        labels={"profit_margin_pct": "Profit Margin (%)", "product_category": ""},
        color="profit_margin_pct",
        color_continuous_scale="RdYlGn",
        template="plotly_white",
    )
    fig_margin.update_layout(height=380, coloraxis_showscale=False)
    st.plotly_chart(fig_margin, use_container_width=True)

    st.markdown('<div class="section-title">Top 10 Products by Revenue</div>', unsafe_allow_html=True)
    top_prod = da.top_products(df, n=10)
    fig_prod = px.bar(
        top_prod.sort_values("total_revenue"),
        x="total_revenue",
        y="product_name",
        orientation="h",
        labels={"total_revenue": "Revenue (₹)", "product_name": ""},
        color="total_revenue",
        color_continuous_scale="Blues",
        template="plotly_white",
        text="total_revenue",
    )
    fig_prod.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig_prod.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig_prod, use_container_width=True)

# ------------------------------------------------------------------
# TAB 3 — BY REGION
# ------------------------------------------------------------------
with tab_region:
    st.markdown('<div class="section-title">Regional Performance</div>', unsafe_allow_html=True)
    reg_df = da.by_region(df)

    # Summary table
    reg_display = reg_df.copy()
    reg_display.columns = ["Region","Orders","Revenue (₹)","Profit (₹)","Avg Order (₹)"]
    st.dataframe(
        reg_display.style.format({
            "Revenue (₹)": "₹{:,.0f}",
            "Profit (₹)":  "₹{:,.0f}",
            "Avg Order (₹)":"₹{:,.0f}",
        }).background_gradient(subset=["Revenue (₹)"], cmap="Purples"),
        use_container_width=True, hide_index=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Revenue by Region</div>', unsafe_allow_html=True)
        fig_reg_bar = px.bar(
            reg_df.sort_values("total_revenue", ascending=True),
            x="total_revenue", y="region", orientation="h",
            labels={"total_revenue":"Revenue (₹)","region":""},
            color="total_revenue", color_continuous_scale="Purples",
            template="plotly_white",
        )
        fig_reg_bar.update_layout(height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_reg_bar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Revenue Share by Region</div>', unsafe_allow_html=True)
        fig_reg_pie = px.pie(
            reg_df, names="region", values="total_revenue",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.35, template="plotly_white",
        )
        fig_reg_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_reg_pie.update_layout(height=340)
        st.plotly_chart(fig_reg_pie, use_container_width=True)

    st.markdown('<div class="section-title">Category Breakdown by Region</div>', unsafe_allow_html=True)
    heat_df = df.groupby(["region","product_category"])["sales_amount"].sum().reset_index()
    heat_pivot = heat_df.pivot(index="region", columns="product_category", values="sales_amount").fillna(0)
    fig_heat = px.imshow(
        heat_pivot,
        labels=dict(x="Category", y="Region", color="Revenue (₹)"),
        color_continuous_scale="YlOrRd",
        aspect="auto",
        template="plotly_white",
        text_auto=".2s",
    )
    fig_heat.update_layout(height=380)
    st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------------------------------
# TAB 4 — TRENDS
# ------------------------------------------------------------------
with tab_trends:
    st.markdown('<div class="section-title">Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
    trend_df = da.monthly_trend(df)

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Scatter(x=trend_df["month"], y=trend_df["total_revenue"],
                   name="Revenue", line=dict(color="#3b82f6", width=2.5), mode="lines+markers"),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Scatter(x=trend_df["month"], y=trend_df["total_profit"],
                   name="Profit", line=dict(color="#10b981", width=2.5, dash="dash"), mode="lines+markers"),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Bar(x=trend_df["month"], y=trend_df["total_orders"],
               name="Orders", marker_color="#e5e7eb", opacity=0.5),
        secondary_y=True,
    )
    fig_trend.update_layout(
        hovermode="x unified", legend=dict(orientation="h", y=1.08),
        template="plotly_white", height=420,
    )
    fig_trend.update_yaxes(title_text="Amount (₹)", secondary_y=False)
    fig_trend.update_yaxes(title_text="Order Count", secondary_y=True)
    fig_trend.update_xaxes(tickangle=45)
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('<div class="section-title">Yearly Revenue Comparison</div>', unsafe_allow_html=True)
    yr_df = df.groupby("year")["sales_amount"].sum().reset_index()
    fig_yr = px.bar(
        yr_df, x="year", y="sales_amount",
        labels={"sales_amount":"Revenue (₹)","year":"Year"},
        color="sales_amount", color_continuous_scale="Blues",
        template="plotly_white", text="sales_amount",
    )
    fig_yr.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig_yr.update_layout(height=360, coloraxis_showscale=False, xaxis=dict(type="category"))
    st.plotly_chart(fig_yr, use_container_width=True)

    st.markdown('<div class="section-title">Monthly Revenue Data Table</div>', unsafe_allow_html=True)
    st.dataframe(
        trend_df.rename(columns={
            "month":"Month","total_revenue":"Revenue (₹)",
            "total_profit":"Profit (₹)","total_orders":"Orders"
        }).style.format({"Revenue (₹)":"₹{:,.0f}","Profit (₹)":"₹{:,.0f}"}),
        use_container_width=True, hide_index=True
    )

# ------------------------------------------------------------------
# TAB 5 — CUSTOMERS
# ------------------------------------------------------------------
with tab_customers:
    st.markdown('<div class="section-title">Gender Analysis</div>', unsafe_allow_html=True)
    gender_df = da.by_gender(df)

    col1, col2 = st.columns(2)
    with col1:
        fig_gen = px.pie(
            gender_df, names="gender", values="total_revenue",
            hole=0.4,
            color_discrete_sequence=["#3b82f6","#ec4899","#f59e0b"],
            template="plotly_white",
        )
        fig_gen.update_traces(textinfo="percent+label", textposition="outside")
        fig_gen.update_layout(height=340)
        st.plotly_chart(fig_gen, use_container_width=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        gd = gender_df.copy()
        gd.columns = ["Gender","Orders","Revenue (₹)","Avg Satisfaction"]
        st.dataframe(
            gd.style.format({"Revenue (₹)":"₹{:,.0f}","Avg Satisfaction":"{:.2f}"}),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="section-title">Revenue by Age Group</div>', unsafe_allow_html=True)
    age_df = da.age_distribution(df)
    fig_age = px.bar(
        age_df, x="age_group", y="sales_amount",
        labels={"sales_amount":"Revenue (₹)","age_group":"Age Group"},
        color="sales_amount", color_continuous_scale="Oranges",
        template="plotly_white",
    )
    fig_age.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(fig_age, use_container_width=True)

    st.markdown('<div class="section-title">Payment Method Breakdown</div>', unsafe_allow_html=True)
    pay_df = da.by_payment(df)
    col3, col4 = st.columns(2)
    with col3:
        fig_pay = px.bar(
            pay_df.sort_values("total_revenue", ascending=True),
            x="total_revenue", y="payment_method", orientation="h",
            labels={"total_revenue":"Revenue (₹)","payment_method":""},
            color="total_revenue", color_continuous_scale="Teal",
            template="plotly_white",
        )
        fig_pay.update_layout(height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_pay, use_container_width=True)
    with col4:
        pd_display = pay_df.copy()
        pd_display.columns = ["Payment Method","Orders","Revenue (₹)"]
        st.dataframe(
            pd_display.style.format({"Revenue (₹)":"₹{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="section-title">Customer Satisfaction Distribution</div>', unsafe_allow_html=True)
    fig_sat = px.histogram(
        df, x="customer_satisfaction", nbins=10,
        labels={"customer_satisfaction":"Satisfaction Score","count":"Count"},
        color_discrete_sequence=["#6366f1"],
        template="plotly_white",
    )
    fig_sat.update_layout(height=320, bargap=0.1)
    st.plotly_chart(fig_sat, use_container_width=True)

# ------------------------------------------------------------------
# TAB 6 — DATA QUALITY
# ------------------------------------------------------------------
with tab_quality:
    st.markdown('<div class="section-title">Data Quality Report</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Rows",      quality_report["total_rows_raw"])
    c2.metric("Cleaned Rows",  quality_report["total_rows_clean"])
    c3.metric("Duplicate Rows Removed", quality_report["duplicate_rows"])

    st.markdown('<div class="section-title">Missing Values — Before Cleaning</div>', unsafe_allow_html=True)
    if quality_report["missing_before"]:
        mv_before = pd.DataFrame.from_dict(
            quality_report["missing_before"], orient="index", columns=["Missing Count"]
        ).reset_index().rename(columns={"index":"Column"})
        mv_before["Missing %"] = (mv_before["Missing Count"] / quality_report["total_rows_raw"] * 100).round(2)
        st.dataframe(mv_before.style.format({"Missing %":"{:.2f}%"}), use_container_width=True, hide_index=True)
    else:
        st.success("No missing values found in raw data.")

    st.markdown('<div class="section-title">Missing Values — After Cleaning</div>', unsafe_allow_html=True)
    if quality_report["missing_after"]:
        mv_after = pd.DataFrame.from_dict(
            quality_report["missing_after"], orient="index", columns=["Remaining Missing"]
        ).reset_index().rename(columns={"index":"Column"})
        st.dataframe(mv_after, use_container_width=True, hide_index=True)
    else:
        st.success("✅ All critical missing values resolved after cleaning.")

    st.markdown('<div class="section-title">Cleaning Steps Applied</div>', unsafe_allow_html=True)
    steps = [
        ("Date Parsing",          "Parsed `order_date` with mixed formats (YYYY-MM-DD and DD/MM/YYYY)."),
        ("Numeric Coercion",      "Coerced age, quantity, unit_price, discount_pct, profit, etc. to numeric; non-parseable values → NaN."),
        ("Discount Fill",         "Filled missing `discount_pct` values with **0** (no discount assumed)."),
        ("Satisfaction Fill",     "Filled missing `customer_satisfaction` with **median** score."),
        ("Age / Days Fill",       "Filled missing `age` and `days_to_ship` with column **median**."),
        ("Duplicate Removal",     f"Removed {quality_report['duplicate_rows']} fully-duplicate rows."),
        ("Calculated Sales",      "Added `calculated_sales = quantity × unit_price` column."),
        ("Time Columns",          "Extracted `year` and `month` columns from `order_date`."),
    ]
    for step, desc in steps:
        st.markdown(f"- **{step}:** {desc}")

    st.markdown('<div class="section-title">Raw Data Preview (first 50 rows)</div>', unsafe_allow_html=True)
    preview_cols = ["order_id","order_date","customer_name","product_category","product_name",
                    "quantity","unit_price","calculated_sales","sales_amount","profit",
                    "discount_pct","region","order_status","customer_satisfaction"]
    available = [c for c in preview_cols if c in df_full.columns]
    st.dataframe(
        df_full[available].head(50).style.format({
            "unit_price":        "₹{:.2f}",
            "calculated_sales":  "₹{:,.2f}",
            "sales_amount":      "₹{:,.2f}",
            "profit":            "₹{:,.2f}",
            "discount_pct":      "{:.1%}",
        }),
        use_container_width=True, hide_index=True
    )

# ------------------------------------------------------------------
# TAB 7 — BUSINESS INSIGHTS
# ------------------------------------------------------------------
with tab_insights:
    st.markdown('<div class="section-title">AI-Driven Business Insights</div>', unsafe_allow_html=True)
    insights = da.generate_insights(df, kpis)
    for insight in insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Revenue vs Discount Scatter</div>', unsafe_allow_html=True)
    st.caption("Explore how discount levels correlate with revenue across categories.")
    fig_scatter = px.scatter(
        df.sample(min(1000, len(df)), random_state=42),
        x="discount_pct", y="sales_amount",
        color="product_category",
        size="quantity",
        hover_data=["product_name","region","order_status"],
        labels={"discount_pct":"Discount %","sales_amount":"Revenue (₹)","product_category":"Category"},
        template="plotly_white",
        opacity=0.65,
    )
    fig_scatter.update_layout(height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-title">Profit vs Revenue by Category (Bubble)</div>', unsafe_allow_html=True)
    cat_df2 = da.by_category(df)
    fig_bubble = px.scatter(
        cat_df2,
        x="total_revenue", y="total_profit",
        size="total_quantity", color="product_category",
        text="product_category",
        labels={"total_revenue":"Revenue (₹)","total_profit":"Profit (₹)","product_category":"Category"},
        template="plotly_white",
    )
    fig_bubble.update_traces(textposition="top center")
    fig_bubble.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown('<div class="section-title">Recommendations</div>', unsafe_allow_html=True)
    recs = [
        ("Invest in Top Categories",  "Focus marketing spend on the highest-revenue categories identified in the Category tab."),
        ("Reduce Return Rate",         "Investigate return reasons — product quality, description accuracy, or shipping damage may be culprits."),
        ("Optimise Discounts",         "Analyse the discount vs profit scatter; avoid steep discounts in low-margin categories."),
        ("Expand in Top Regions",      "Double down on high-performing regions while piloting growth strategies in under-served areas."),
        ("Loyalty for High-Value Ages","Target the most revenue-generating age groups with loyalty programs and personalised offers."),
        ("Payment Diversification",    "Ensure preferred payment methods are always available; consider incentivising high-value methods."),
    ]
    for title, detail in recs:
        with st.expander(f"📌 {title}"):
            st.write(detail)
