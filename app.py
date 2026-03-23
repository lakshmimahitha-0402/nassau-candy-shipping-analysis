import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import base64

warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG — must be first Streamlit command
# ============================================================
st.set_page_config(
    page_title="Nassau Candy — Shipping Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DARK THEME STYLING
# ============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1a1d24;
        border-right: 1px solid #2d3139;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1a1d24;
        border: 1px solid #2d3139;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="metric-container"] label {
        color: #9ca3af !important;
        font-size: 13px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    h1, h2, h3 { color: #ffffff !important; }

    /* Divider */
    hr { border-color: #2d3139 !important; }

    /* Section label */
    .section-label {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #2d3139;
    }

    /* Page title */
    .page-title {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 20px;
    }

    /* Hide streamlit menu & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD & CLEAN DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")

    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True)

    raw_diff        = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Lead Time"] = raw_diff % 365

    factory_map = {
        "Wonka Bar - Nutty Crunch Surprise"  : "Lot's O' Nuts",
        "Wonka Bar - Fudge Mallows"          : "Lot's O' Nuts",
        "Wonka Bar -Scrumdiddlyumptious"     : "Lot's O' Nuts",
        "Wonka Bar - Milk Chocolate"         : "Wicked Choccy's",
        "Wonka Bar - Triple Dazzle Caramel"  : "Wicked Choccy's",
        "Laffy Taffy"                        : "Sugar Shack",
        "SweeTARTS"                          : "Sugar Shack",
        "Nerds"                              : "Sugar Shack",
        "Fun Dip"                            : "Sugar Shack",
        "Fizzy Lifting Drinks"               : "Sugar Shack",
        "Everlasting Gobstopper"             : "Secret Factory",
        "Lickable Wallpaper"                 : "Secret Factory",
        "Wonka Gum"                          : "Secret Factory",
        "Hair Toffee"                        : "The Other Factory",
        "Kazookles"                          : "The Other Factory",
    }
    df["Factory"]      = df["Product Name"].map(factory_map)
    df["Route Region"] = df["Factory"] + " -> " + df["Region"]
    df["Route State"]  = df["Factory"] + " -> " + df["State/Province"]
    df["Order Year"]   = df["Order Date"].dt.year
    df["Order Month"]  = df["Order Date"].dt.month

    threshold        = df["Lead Time"].mean() + df["Lead Time"].std()
    df["Is Delayed"] = df["Lead Time"] > threshold

    return df, round(threshold, 1)

df, DELAY_THRESHOLD = load_data()


# ============================================================
# MATPLOTLIB DARK STYLE
# ============================================================
def set_dark_style():
    plt.rcParams.update({
        "figure.facecolor" : "#1a1d24",
        "axes.facecolor"   : "#1a1d24",
        "axes.edgecolor"   : "#2d3139",
        "axes.labelcolor"  : "#9ca3af",
        "axes.titlecolor"  : "#ffffff",
        "xtick.color"      : "#9ca3af",
        "ytick.color"      : "#9ca3af",
        "text.color"       : "#ffffff",
        "grid.color"       : "#2d3139",
        "grid.linestyle"   : "--",
        "grid.alpha"       : 0.5,
        "axes.grid"        : True,
        "font.size"        : 10,
    })

set_dark_style()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    # Nassau Candy logo
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px 0;'>
        <div style='font-size:22px; font-weight:900; letter-spacing:3px; color:#ffffff;'>
            NASSAU <span style='color:#c9a84c;'>CANDY</span>
        </div>
        <div style='font-size:10px; color:#c9a84c; letter-spacing:2px; margin-top:2px;'>
            SHIPPING INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown("**📅 Date & Scope**")

    # Date range picker
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    date_range = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Handle case where user selects only 1 date (still picking)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    st.markdown("**📍 Location**")
    all_regions = ["All"] + sorted(df["Region"].unique().tolist())
    selected_region = st.selectbox("Region", all_regions)

    all_states = ["All"] + sorted(df["State/Province"].unique().tolist())
    selected_state = st.selectbox("State", all_states)

    st.markdown("**🏭 Operations**")
    all_factories = ["All"] + sorted(df["Factory"].unique().tolist())
    selected_factory = st.selectbox("Factory", all_factories)

    all_modes = ["All"] + sorted(df["Ship Mode"].unique().tolist())
    selected_mode = st.selectbox("Ship Mode", all_modes)

    st.markdown("**⏱️ Lead Time**")
    selected_lt = st.slider(
        "Max Lead Time (days)",
        min_value=int(df["Lead Time"].min()),
        max_value=int(df["Lead Time"].max()),
        value=int(df["Lead Time"].max())
    )

    st.markdown("---")

    # Dashboard module switcher
    st.markdown("**📊 Dashboard Module**")
    page = st.radio(
        label="",
        options=[
            "Route Efficiency Overview",
            "Geographic Analysis",
            "Ship Mode Comparison",
            "Route Drill-Down",
        ]
    )

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:#555;'>Delay threshold: {DELAY_THRESHOLD} days</div>",
        unsafe_allow_html=True
    )


# ============================================================
# APPLY FILTERS
# ============================================================
fdf = df.copy()

# Apply date range filter
fdf = fdf[
    (fdf["Order Date"].dt.date >= start_date) &
    (fdf["Order Date"].dt.date <= end_date)
]

# Apply other filters
if selected_region  != "All": fdf = fdf[fdf["Region"]          == selected_region]
if selected_state   != "All": fdf = fdf[fdf["State/Province"]  == selected_state]
if selected_factory != "All": fdf = fdf[fdf["Factory"]         == selected_factory]
if selected_mode    != "All": fdf = fdf[fdf["Ship Mode"]       == selected_mode]
fdf = fdf[fdf["Lead Time"] <= selected_lt]


# ============================================================
# LOGO HEADER — every page
# ============================================================
st.markdown("""
<div style='text-align:center; padding:10px 0 24px 0;'>
    <div style='font-size:42px; font-weight:900; letter-spacing:6px; color:#ffffff;'>
        NASSAU <span style='color:#c9a84c;'>CANDY</span>
    </div>
    <div style='font-size:12px; color:#c9a84c; letter-spacing:4px; margin-top:4px;'>
        SPECIALTY CONFECTIONS &amp; FINE FOODS
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# PAGE 1 — ROUTE EFFICIENCY OVERVIEW
# ============================================================
if page == "Route Efficiency Overview":

    st.markdown('<div class="page-title">Route Efficiency Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Factory-to-customer route performance across all regions</div>', unsafe_allow_html=True)

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📦 Total Orders",   f"{len(fdf):,}")
    c2.metric("⏱️ Avg Lead Time",  f"{fdf['Lead Time'].mean():.1f} days")
    c3.metric("⚠️ Delay Rate",     f"{fdf['Is Delayed'].mean()*100:.1f}%")
    c4.metric("💰 Total Sales",    f"${fdf['Sales'].sum():,.0f}")
    c5.metric("📈 Total Profit",   f"${fdf['Gross Profit'].sum():,.0f}")

    st.markdown("---")

    # Build route KPI table from filtered data
    route_kpi = fdf.groupby("Route Region").agg(
        Total_Orders  = ("Lead Time", "count"),
        Avg_Lead_Time = ("Lead Time", "mean"),
        Delay_Rate    = ("Is Delayed", "mean"),
        Total_Sales   = ("Sales", "sum"),
    ).reset_index().round(2)

    if len(route_kpi) > 1:
        mx = route_kpi["Avg_Lead_Time"].max()
        mn = route_kpi["Avg_Lead_Time"].min()
        route_kpi["Efficiency_Score"] = (
            100 - ((route_kpi["Avg_Lead_Time"] - mn) / (mx - mn) * 100)
        ).round(1)
    else:
        route_kpi["Efficiency_Score"] = 100.0

    route_kpi = route_kpi.sort_values("Avg_Lead_Time").reset_index(drop=True)

    if len(route_kpi) >= 2:
        top10    = route_kpi.head(10)
        bottom10 = route_kpi.tail(10).sort_values("Avg_Lead_Time", ascending=False)

        col_l, col_r = st.columns(2)

        # Top 10
        with col_l:
            st.markdown('<div class="section-label">✅ Top 10 Most Efficient Routes</div>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(top10["Route Region"], top10["Avg_Lead_Time"],
                    color="#2ecc71", edgecolor="#1a1d24", height=0.6)
            ax.set_xlim(170, 186)
            ax.set_xlabel("Avg Lead Time (days)")
            ax.invert_yaxis()
            ax.set_title("Fastest Routes", color="#ffffff")
            for i, val in enumerate(top10["Avg_Lead_Time"]):
                ax.text(val + 0.05, i, f"{val:.1f}d",
                        va="center", fontsize=8, color="#ffffff")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        # Bottom 10
        with col_r:
            st.markdown('<div class="section-label">❌ Bottom 10 Slowest Routes</div>', unsafe_allow_html=True)
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.barh(bottom10["Route Region"], bottom10["Avg_Lead_Time"],
                     color="#e74c3c", edgecolor="#1a1d24", height=0.6)
            ax2.set_xlim(170, 186)
            ax2.set_xlabel("Avg Lead Time (days)")
            ax2.invert_yaxis()
            ax2.set_title("Slowest Routes", color="#ffffff")
            for i, val in enumerate(bottom10["Avg_Lead_Time"]):
                ax2.text(val + 0.05, i, f"{val:.1f}d",
                         va="center", fontsize=8, color="#ffffff")
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
    else:
        st.warning("Not enough routes. Try removing some filters.")

    st.markdown("---")
    st.markdown('<div class="section-label">📋 Full Route Leaderboard</div>', unsafe_allow_html=True)
    with st.expander("View Full Table"):
        st.dataframe(route_kpi, use_container_width=True)


# ============================================================
# PAGE 2 — GEOGRAPHIC ANALYSIS
# ============================================================
elif page == "Geographic Analysis":

    st.markdown('<div class="page-title">Geographic Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Regional bottlenecks and factory performance heatmap</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Orders",   f"{len(fdf):,}")
    c2.metric("⏱️ Avg Lead Time",  f"{fdf['Lead Time'].mean():.1f} days")
    c3.metric("⚠️ Delay Rate",     f"{fdf['Is Delayed'].mean()*100:.1f}%")
    c4.metric("🗺️ States Covered", f"{fdf['State/Province'].nunique()}")

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Heatmap
    with col_l:
        st.markdown('<div class="section-label">🔥 Factory × Region Heatmap</div>', unsafe_allow_html=True)
        pivot = fdf.groupby(["Factory", "Region"])["Lead Time"].mean().unstack()
        if not pivot.empty:
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            sns.heatmap(
                pivot, annot=True, fmt=".1f",
                cmap="RdYlGn_r",
                linewidths=0.5, linecolor="#0e1117",
                ax=ax3,
                annot_kws={"size": 10, "color": "white"},
                cbar_kws={"label": "Avg Lead Time (days)"}
            )
            ax3.set_title("Avg Lead Time: Factory vs Region", color="#ffffff")
            ax3.set_ylabel("Factory")
            ax3.set_xlabel("Customer Region")
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close()

    # Region bar chart
    with col_r:
        st.markdown('<div class="section-label">📍 Lead Time by Region</div>', unsafe_allow_html=True)
        region_lt   = fdf.groupby("Region")["Lead Time"].mean().sort_values(ascending=False)
        overall_avg = fdf["Lead Time"].mean()
        colors_r    = ["#e74c3c" if v > overall_avg else "#2ecc71" for v in region_lt.values]

        fig4, ax4 = plt.subplots(figsize=(7, 4))
        bars = ax4.bar(region_lt.index, region_lt.values,
                       color=colors_r, edgecolor="#1a1d24", width=0.5)
        ax4.axhline(overall_avg, color="#c9a84c", linestyle="--",
                    linewidth=1.5, label=f"Avg: {overall_avg:.1f}d")
        ax4.set_ylim(170, 186)
        ax4.set_ylabel("Avg Lead Time (days)")
        ax4.set_title("Lead Time by Customer Region", color="#ffffff")
        ax4.legend()
        for bar, val in zip(bars, region_lt.values):
            ax4.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.1,
                     f"{val:.1f}", ha="center", fontsize=9, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

    st.markdown("---")

    # Bottleneck scatter — full width
    st.markdown('<div class="section-label">📍 Geographic Bottleneck: Volume vs Lead Time</div>', unsafe_allow_html=True)
    st.markdown("States in the **top-right** = high volume AND slow shipping = biggest problem areas")

    state_data = fdf.groupby("State/Province").agg(
        Avg_Lead_Time = ("Lead Time", "mean"),
        Total_Orders  = ("Lead Time", "count"),
        Delay_Rate    = ("Is Delayed", "mean"),
    ).reset_index()

    if len(state_data) > 1:
        fig5, ax5 = plt.subplots(figsize=(13, 6))
        scatter = ax5.scatter(
            state_data["Total_Orders"],
            state_data["Avg_Lead_Time"],
            c=state_data["Delay_Rate"],
            cmap="RdYlGn_r",
            s=state_data["Total_Orders"] * 0.5 + 40,
            alpha=0.8,
            edgecolors="#2d3139",
            linewidth=0.8
        )
        plt.colorbar(scatter, ax=ax5, label="Delay Rate")
        state_data["risk"] = state_data["Total_Orders"] * state_data["Avg_Lead_Time"]
        top5 = state_data.nlargest(5, "risk")
        for _, row in top5.iterrows():
            ax5.annotate(
                row["State/Province"],
                (row["Total_Orders"], row["Avg_Lead_Time"]),
                fontsize=8, ha="center", va="bottom", color="#c9a84c",
                xytext=(0, 8), textcoords="offset points"
            )
        ax5.set_xlabel("Number of Orders (Volume)")
        ax5.set_ylabel("Avg Lead Time (days)")
        ax5.set_title("Bottleneck Map: High Volume + High Lead Time = Problem States",
                      color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()


# ============================================================
# PAGE 3 — SHIP MODE COMPARISON
# ============================================================
elif page == "Ship Mode Comparison":

    st.markdown('<div class="page-title">Ship Mode Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Performance, delay rate and cost across all shipping methods</div>', unsafe_allow_html=True)

    mode_kpi = fdf.groupby("Ship Mode").agg(
        Total_Orders  = ("Lead Time", "count"),
        Avg_Lead_Time = ("Lead Time", "mean"),
        Delay_Rate    = ("Is Delayed", "mean"),
        Avg_Cost      = ("Cost", "mean"),
        Total_Sales   = ("Sales", "sum"),
    ).reset_index().round(2)
    mode_kpi = mode_kpi.sort_values("Avg_Lead_Time")

    # One metric card per ship mode
    st.markdown('<div class="section-label">📊 Key Stats by Ship Mode</div>', unsafe_allow_html=True)
    cols = st.columns(len(mode_kpi))
    for i, (_, row) in enumerate(mode_kpi.iterrows()):
        cols[i].metric(
            row["Ship Mode"],
            f"{row['Avg_Lead_Time']:.1f}d",
            f"Delay: {row['Delay_Rate']*100:.1f}%"
        )

    st.markdown("---")

    colors_mode = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]

    col1, col2, col3 = st.columns(3)

    # Lead Time chart
    with col1:
        st.markdown('<div class="section-label">⏱️ Avg Lead Time</div>', unsafe_allow_html=True)
        fig6, ax6 = plt.subplots(figsize=(5, 4))
        bars = ax6.bar(mode_kpi["Ship Mode"], mode_kpi["Avg_Lead_Time"],
                       color=colors_mode[:len(mode_kpi)],
                       edgecolor="#1a1d24", width=0.5)
        ax6.set_ylim(170, 186)
        ax6.set_ylabel("Days")
        ax6.set_title("Avg Lead Time (days)", color="#ffffff")
        ax6.tick_params(axis="x", rotation=15)
        for bar in bars:
            ax6.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.05,
                     f"{bar.get_height():.1f}",
                     ha="center", fontsize=9, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

    # Delay Rate chart
    with col2:
        st.markdown('<div class="section-label">⚠️ Delay Rate</div>', unsafe_allow_html=True)
        fig7, ax7 = plt.subplots(figsize=(5, 4))
        bars2 = ax7.bar(mode_kpi["Ship Mode"], mode_kpi["Delay_Rate"] * 100,
                        color=colors_mode[:len(mode_kpi)],
                        edgecolor="#1a1d24", width=0.5)
        ax7.set_ylabel("%")
        ax7.set_title("Delay Rate (%)", color="#ffffff")
        ax7.tick_params(axis="x", rotation=15)
        for bar in bars2:
            ax7.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.1,
                     f"{bar.get_height():.1f}%",
                     ha="center", fontsize=9, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig7)
        plt.close()

    # Cost chart
    with col3:
        st.markdown('<div class="section-label">💰 Avg Cost per Order</div>', unsafe_allow_html=True)
        fig8, ax8 = plt.subplots(figsize=(5, 4))
        bars3 = ax8.bar(mode_kpi["Ship Mode"], mode_kpi["Avg_Cost"],
                        color=colors_mode[:len(mode_kpi)],
                        edgecolor="#1a1d24", width=0.5)
        ax8.set_ylabel("$")
        ax8.set_title("Avg Cost per Order ($)", color="#ffffff")
        ax8.tick_params(axis="x", rotation=15)
        for bar in bars3:
            ax8.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.02,
                     f"${bar.get_height():.2f}",
                     ha="center", fontsize=9, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig8)
        plt.close()

    st.markdown("---")

    # Boxplot
    st.markdown('<div class="section-label">📦 Lead Time Spread by Ship Mode</div>', unsafe_allow_html=True)
    order_modes  = mode_kpi["Ship Mode"].tolist()
    data_by_mode = [fdf[fdf["Ship Mode"] == m]["Lead Time"].values for m in order_modes]

    fig9, ax9 = plt.subplots(figsize=(12, 5))
    bp = ax9.boxplot(
        data_by_mode, labels=order_modes,
        patch_artist=True,
        medianprops={"color": "#ffffff", "linewidth": 2},
        whiskerprops={"color": "#9ca3af"},
        capprops={"color": "#9ca3af"},
        flierprops={"markerfacecolor": "#e74c3c", "markersize": 4}
    )
    for patch, color in zip(bp["boxes"], colors_mode):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax9.axhline(fdf["Lead Time"].mean(), color="#c9a84c",
                linestyle="--", linewidth=1.5,
                label=f"Overall Mean: {fdf['Lead Time'].mean():.1f}d")
    ax9.set_ylabel("Lead Time (days)")
    ax9.set_title("Lead Time Distribution by Ship Mode", color="#ffffff")
    ax9.legend()
    plt.tight_layout()
    st.pyplot(fig9)
    plt.close()

    st.markdown("---")

    # Monthly trend
    st.markdown('<div class="section-label">📈 Monthly Lead Time & Delay Trend</div>', unsafe_allow_html=True)
    monthly = fdf.groupby(["Order Year", "Order Month"]).agg(
        Avg_Lead_Time = ("Lead Time", "mean"),
        Delay_Rate    = ("Is Delayed", "mean"),
    ).reset_index()
    monthly["Period"] = (
        monthly["Order Year"].astype(str) + "-" +
        monthly["Order Month"].astype(str).str.zfill(2)
    )
    monthly = monthly.sort_values("Period")

    if len(monthly) > 1:
        fig10, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
        axes[0].plot(monthly["Period"], monthly["Avg_Lead_Time"],
                     marker="o", color="#3498db", linewidth=2, markersize=5)
        axes[0].axhline(fdf["Lead Time"].mean(), color="#c9a84c",
                        linestyle="--", alpha=0.8,
                        label=f"Avg: {fdf['Lead Time'].mean():.1f}d")
        axes[0].set_ylabel("Avg Lead Time (days)")
        axes[0].set_title("Monthly Average Lead Time", color="#ffffff")
        axes[0].legend()

        axes[1].bar(monthly["Period"], monthly["Delay_Rate"] * 100,
                    color="#e74c3c", alpha=0.8, edgecolor="#1a1d24")
        axes[1].set_ylabel("Delay Rate (%)")
        axes[1].set_title("Monthly Delay Rate (%)", color="#ffffff")
        axes[1].tick_params(axis="x", rotation=45)

        tick_pos = range(0, len(monthly), 3)
        axes[1].set_xticks(list(tick_pos))
        axes[1].set_xticklabels(
            [monthly["Period"].iloc[i] for i in tick_pos], rotation=45
        )
        plt.tight_layout()
        st.pyplot(fig10)
        plt.close()


# ============================================================
# PAGE 4 — ROUTE DRILL-DOWN
# ============================================================
elif page == "Route Drill-Down":

    st.markdown('<div class="page-title">Route Drill-Down</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">State-level insights and individual order details</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Filtered Orders", f"{len(fdf):,}")
    c2.metric("⏱️ Avg Lead Time",   f"{fdf['Lead Time'].mean():.1f} days")
    c3.metric("⚠️ Delayed Orders",  f"{fdf['Is Delayed'].sum():,}")
    c4.metric("💰 Avg Sale Value",  f"${fdf['Sales'].mean():.2f}")

    st.markdown("---")

    col_l, col_r = st.columns(2)
    avg_lt = fdf["Lead Time"].mean()

    # Product chart
    with col_l:
        st.markdown('<div class="section-label">🍫 Lead Time by Product</div>', unsafe_allow_html=True)
        prod_lt  = fdf.groupby("Product Name")["Lead Time"].mean().sort_values(ascending=False)
        colors_p = ["#e74c3c" if v > avg_lt else "#2ecc71" for v in prod_lt.values]

        fig11, ax11 = plt.subplots(figsize=(7, 6))
        ax11.barh(prod_lt.index, prod_lt.values,
                  color=colors_p, edgecolor="#1a1d24")
        ax11.axvline(avg_lt, color="#c9a84c", linestyle="--",
                     linewidth=1.5, label=f"Avg: {avg_lt:.1f}d")
        ax11.set_xlim(170, 186)
        ax11.set_xlabel("Avg Lead Time (days)")
        ax11.set_title("Avg Lead Time by Product", color="#ffffff")
        ax11.invert_yaxis()
        ax11.legend()
        plt.tight_layout()
        st.pyplot(fig11)
        plt.close()

    with col_r:
        # Division chart
        st.markdown('<div class="section-label">📦 Lead Time by Division</div>', unsafe_allow_html=True)
        div_lt   = fdf.groupby("Division")["Lead Time"].mean().sort_values(ascending=False)
        colors_d = ["#e74c3c" if v > avg_lt else "#2ecc71" for v in div_lt.values]

        fig12, ax12 = plt.subplots(figsize=(7, 3))
        bars = ax12.bar(div_lt.index, div_lt.values,
                        color=colors_d, edgecolor="#1a1d24", width=0.4)
        ax12.axhline(avg_lt, color="#c9a84c", linestyle="--",
                     linewidth=1.5, label=f"Avg: {avg_lt:.1f}d")
        ax12.set_ylim(170, 186)
        ax12.set_ylabel("Avg Lead Time (days)")
        ax12.set_title("By Division", color="#ffffff")
        ax12.legend()
        for bar, val in zip(bars, div_lt.values):
            ax12.text(bar.get_x() + bar.get_width()/2,
                      bar.get_height() + 0.05,
                      f"{val:.1f}d", ha="center", fontsize=9, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig12)
        plt.close()

        # Factory chart
        st.markdown('<div class="section-label">🏭 Lead Time by Factory</div>', unsafe_allow_html=True)
        fact_lt  = fdf.groupby("Factory")["Lead Time"].mean().sort_values(ascending=False)
        colors_f = ["#e74c3c" if v > avg_lt else "#2ecc71" for v in fact_lt.values]

        fig13, ax13 = plt.subplots(figsize=(7, 3))
        bars2 = ax13.bar(fact_lt.index, fact_lt.values,
                         color=colors_f, edgecolor="#1a1d24", width=0.5)
        ax13.axhline(avg_lt, color="#c9a84c", linestyle="--",
                     linewidth=1.5, label=f"Avg: {avg_lt:.1f}d")
        ax13.set_ylim(170, 186)
        ax13.set_ylabel("Avg Lead Time (days)")
        ax13.set_title("By Factory", color="#ffffff")
        ax13.tick_params(axis="x", rotation=20)
        ax13.legend()
        for bar, val in zip(bars2, fact_lt.values):
            ax13.text(bar.get_x() + bar.get_width()/2,
                      bar.get_height() + 0.05,
                      f"{val:.1f}d", ha="center", fontsize=8, color="#ffffff")
        plt.tight_layout()
        st.pyplot(fig13)
        plt.close()

    st.markdown("---")

    # Orders table
    st.markdown('<div class="section-label">📋 Order-Level Shipment Details</div>', unsafe_allow_html=True)
    st.markdown(f"Showing **{min(300, len(fdf))}** of **{len(fdf):,}** filtered orders")

    st.dataframe(
        fdf[[
            "Order Date", "Ship Mode", "Factory", "Region",
            "State/Province", "Product Name", "Division",
            "Lead Time", "Is Delayed", "Sales", "Gross Profit"
        ]].head(300),
        use_container_width=True
    )

    csv_data = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_data,
        file_name="nassau_filtered_data.csv",
        mime="text/csv"
    )


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64("unified logo.png") 


# ============================================================
# FOOTER
# ============================================================
st.divider()

col1, col2, col3 ,col4= st.columns(4)

with col1:
    st.markdown(
        f'<img src="data:image/png;base64,{logo_b64}" style="height:45px;">',
        unsafe_allow_html=True
    )

with col2:
    st.caption("Mentored by [Sai Prasad Kagne](https://www.linkedin.com/in/saiprasad-kagne/)")

with col3:
    st.caption("Created by [Lakshmi Mahitha Noudu](https://www.linkedin.com/in/lakshmi-mahitha-noudu-490160268)")

with col4:
    st.caption("Version 1.1 | Last updated: March 2026")