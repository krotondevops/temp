import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Kroton · Cierres Consolidados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS – professional, clean, responsive
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit extras ── */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #e2e8f0;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label {
    color: #cbd5e1 !important;
    font-weight: 500;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
    transition: transform .15s ease, box-shadow .15s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,.1);
}
.kpi-icon {
    font-size: 1.6rem;
    margin-bottom: .25rem;
}
.kpi-label {
    font-size: .75rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: .15rem;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.kpi-delta {
    font-size: .78rem;
    font-weight: 500;
    margin-top: .25rem;
}
.kpi-delta.positive { color: #16a34a; }
.kpi-delta.negative { color: #dc2626; }

/* ── Section headers ── */
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: #334155;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: .35rem;
    margin-bottom: .75rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}

/* ── Chart containers ── */
div[data-testid="stPlotlyChart"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .kpi-value { font-size: 1.2rem; }
    .kpi-label { font-size: .65rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data loading (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos …")
def load_data() -> pd.DataFrame:
    df = pd.read_excel("Cierres Consolidados v2.xlsx", sheet_name="Cierres_consolidados")
    # Fix encoding issue on AÑO column
    cols = {c: "AÑO" for c in df.columns if "A" in c and "O" in c and len(c) == 3 and c not in ("MES",)}
    if cols:
        df.rename(columns=cols, inplace=True)
    # Ensure AÑO exists
    if "AÑO" not in df.columns and "FECHA" in df.columns:
        df["AÑO"] = df["FECHA"].dt.year
    # Month order
    month_order = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    df["MES"] = pd.Categorical(df["MES"], categories=month_order, ordered=True)
    df["MES_NUM"] = df["MES"].cat.codes + 1
    # Margin %
    df["MARGEN_%"] = (df["MARGEN USD"] / df["VENTA USD"].replace(0, pd.NA) * 100).fillna(0)
    return df


df_raw = load_data()

# ─────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:1rem 0 .5rem'>"
        "<span style='font-size:1.8rem'>📊</span><br>"
        "<span style='font-size:1.1rem;font-weight:700;color:#f8fafc;letter-spacing:.04em'>"
        "Kroton Analytics</span><br>"
        "<span style='font-size:.72rem;color:#94a3b8'>Cierres Consolidados</span>"
        "</div><hr style='border-color:#334155;margin:.5rem 0 1rem'>",
        unsafe_allow_html=True,
    )

    # Year
    years = sorted(df_raw["AÑO"].dropna().unique().astype(int))
    sel_years = st.multiselect("Año", years, default=years, key="year")

    # Month
    all_months = [m for m in df_raw["MES"].cat.categories if m in df_raw["MES"].values]
    sel_months = st.multiselect("Mes", all_months, default=all_months, key="month")

    # Channel
    channels = sorted(df_raw["CANAL"].dropna().unique())
    sel_channels = st.multiselect("Canal", channels, default=channels, key="channel")

    # Category
    categories = sorted(df_raw["CATEGORIA_LINEA"].dropna().unique())
    sel_categories = st.multiselect("Categoría", categories, default=categories, key="cat")

    # Seller (optional – search)
    sellers = sorted(df_raw["VENDEDOR_2"].dropna().unique())
    sel_sellers = st.multiselect("Vendedor (opcional)", sellers, default=[], key="seller")

    st.markdown("<hr style='border-color:#334155;margin:1rem 0'>", unsafe_allow_html=True)
    st.caption("Datos: Cierres Consolidados v2")

# ─────────────────────────────────────────────
# Apply filters
# ─────────────────────────────────────────────
df = df_raw.copy()
if sel_years:
    df = df[df["AÑO"].isin(sel_years)]
if sel_months:
    df = df[df["MES"].isin(sel_months)]
if sel_channels:
    df = df[df["CANAL"].isin(sel_channels)]
if sel_categories:
    df = df[df["CATEGORIA_LINEA"].isin(sel_categories)]
if sel_sellers:
    df = df[df["VENDEDOR_2"].isin(sel_sellers)]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def fmt_usd(val: float) -> str:
    """Format number as compact USD string."""
    if abs(val) >= 1_000_000:
        return f"$ {val/1_000_000:,.2f} M"
    if abs(val) >= 1_000:
        return f"$ {val/1_000:,.1f} K"
    return f"$ {val:,.0f}"


def kpi_html(icon: str, label: str, value: str, delta: str = "", delta_positive: bool = True) -> str:
    delta_html = ""
    if delta:
        cls = "positive" if delta_positive else "negative"
        arrow = "↑" if delta_positive else "↓"
        delta_html = f"<div class='kpi-delta {cls}'>{arrow} {delta}</div>"
    return (
        f"<div class='kpi-card'>"
        f"<div class='kpi-icon'>{icon}</div>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"{delta_html}"
        f"</div>"
    )


CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#334155"),
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc", font_size=12),
)

PALETTE = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"]

# ─────────────────────────────────────────────
# Title
# ─────────────────────────────────────────────
st.markdown(
    "<h2 style='margin:0 0 .25rem;color:#0f172a;font-weight:700'>"
    "📊 Dashboard · Cierres Consolidados</h2>"
    "<p style='color:#64748b;font-size:.85rem;margin-bottom:1.25rem'>"
    "Análisis de ventas, costos y márgenes — datos actualizados</p>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
total_venta = df["VENTA USD"].sum()
total_costo = df["COSTO USD"].sum()
total_margen = df["MARGEN USD"].sum()
margen_pct = (total_margen / total_venta * 100) if total_venta else 0
total_qty = df["CANTIDAD"].sum()
n_clients = df["COD_CLIENTE"].nunique()
n_docs = df["TIPO_DOC"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(kpi_html("💰", "Venta Total", fmt_usd(total_venta)), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_html("📦", "Costo Total", fmt_usd(total_costo)), unsafe_allow_html=True)
with k3:
    st.markdown(
        kpi_html("📈", "Margen Total", fmt_usd(total_margen), f"{margen_pct:.1f}%", margen_pct > 0),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(kpi_html("🔢", "Cantidad", f"{total_qty:,.0f}"), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_html("👥", "Clientes", f"{n_clients:,}"), unsafe_allow_html=True)
with k6:
    st.markdown(kpi_html("📄", "Documentos", f"{n_docs:,}"), unsafe_allow_html=True)

st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Row 1 – Monthly trend + Channel donut
# ─────────────────────────────────────────────
col_trend, col_donut = st.columns([3, 2])

with col_trend:
    st.markdown("<div class='section-header'>📅 Evolución Mensual de Ventas</div>", unsafe_allow_html=True)
    monthly = (
        df.groupby(["AÑO", "MES", "MES_NUM"], observed=True)
        .agg({"VENTA USD": "sum", "MARGEN USD": "sum"})
        .reset_index()
        .sort_values(["AÑO", "MES_NUM"])
    )
    monthly["Periodo"] = monthly["MES"].astype(str) + " " + monthly["AÑO"].astype(int).astype(str)

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    for i, year in enumerate(sorted(monthly["AÑO"].unique())):
        yd = monthly[monthly["AÑO"] == year]
        fig_trend.add_trace(
            go.Bar(
                x=yd["MES"].astype(str),
                y=yd["VENTA USD"],
                name=f"Venta {int(year)}",
                marker_color=PALETTE[i % len(PALETTE)],
                marker_cornerradius=4,
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=yd["MES"].astype(str),
                y=yd["MARGEN USD"],
                name=f"Margen {int(year)}",
                mode="lines+markers",
                line=dict(color=PALETTE[(i + 2) % len(PALETTE)], width=2.5),
                marker=dict(size=6),
            ),
            secondary_y=True,
        )
    fig_trend.update_layout(
        **CHART_LAYOUT,
        barmode="group",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", font_size=11),
        height=380,
    )
    fig_trend.update_yaxes(title_text="Venta (USD)", secondary_y=False, gridcolor="#e2e8f0")
    fig_trend.update_yaxes(title_text="Margen (USD)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_donut:
    st.markdown("<div class='section-header'>📡 Venta por Canal</div>", unsafe_allow_html=True)
    by_channel = df.groupby("CANAL", observed=True)["VENTA USD"].sum().reset_index()
    by_channel = by_channel[by_channel["VENTA USD"] > 0].sort_values("VENTA USD", ascending=False)
    fig_donut = px.pie(
        by_channel,
        values="VENTA USD",
        names="CANAL",
        hole=0.55,
        color_discrete_sequence=PALETTE,
    )
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=11,
        hovertemplate="<b>%{label}</b><br>Venta: $%{value:,.0f}<extra></extra>",
    )
    fig_donut.update_layout(**CHART_LAYOUT, height=380, showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────
# Row 2 – Category bar + Margin waterfall
# ─────────────────────────────────────────────
col_cat, col_margin = st.columns(2)

with col_cat:
    st.markdown("<div class='section-header'>🏷️ Venta por Categoría</div>", unsafe_allow_html=True)
    by_cat = (
        df.groupby("CATEGORIA_LINEA", observed=True)
        .agg({"VENTA USD": "sum", "MARGEN USD": "sum"})
        .reset_index()
    )
    by_cat = by_cat[by_cat["VENTA USD"] > 0].sort_values("VENTA USD", ascending=False)
    fig_cat = go.Figure()
    fig_cat.add_trace(
        go.Bar(
            y=by_cat["CATEGORIA_LINEA"],
            x=by_cat["VENTA USD"],
            name="Venta",
            orientation="h",
            marker_color="#3b82f6",
            marker_cornerradius=4,
        )
    )
    fig_cat.add_trace(
        go.Bar(
            y=by_cat["CATEGORIA_LINEA"],
            x=by_cat["MARGEN USD"],
            name="Margen",
            orientation="h",
            marker_color="#10b981",
            marker_cornerradius=4,
        )
    )
    fig_cat.update_layout(
        **CHART_LAYOUT,
        barmode="group",
        height=370,
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor="#e2e8f0"),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_margin:
    st.markdown("<div class='section-header'>📊 Margen (%) por Canal</div>", unsafe_allow_html=True)
    margin_ch = (
        df.groupby("CANAL", observed=True)
        .agg({"VENTA USD": "sum", "MARGEN USD": "sum"})
        .reset_index()
    )
    margin_ch = margin_ch[margin_ch["VENTA USD"] > 0]
    margin_ch["MARGEN_%"] = (margin_ch["MARGEN USD"] / margin_ch["VENTA USD"] * 100).round(1)
    margin_ch = margin_ch.sort_values("MARGEN_%", ascending=False)

    fig_mpct = go.Figure(
        go.Bar(
            x=margin_ch["CANAL"],
            y=margin_ch["MARGEN_%"],
            marker_color=[
                "#16a34a" if v > 15 else "#f59e0b" if v > 0 else "#dc2626"
                for v in margin_ch["MARGEN_%"]
            ],
            marker_cornerradius=6,
            text=[f"{v:.1f}%" for v in margin_ch["MARGEN_%"]],
            textposition="outside",
            textfont=dict(size=12, color="#334155"),
        )
    )
    fig_mpct.update_layout(
        **CHART_LAYOUT, height=370, yaxis=dict(title="Margen %", gridcolor="#e2e8f0")
    )
    st.plotly_chart(fig_mpct, use_container_width=True)

# ─────────────────────────────────────────────
# Row 3 – Top sellers + Zone map
# ─────────────────────────────────────────────
col_sell, col_zone = st.columns(2)

with col_sell:
    st.markdown("<div class='section-header'>🏆 Top 15 Vendedores</div>", unsafe_allow_html=True)
    top_sellers = (
        df.groupby("VENDEDOR_2", observed=True)
        .agg({"VENTA USD": "sum", "MARGEN USD": "sum"})
        .reset_index()
        .sort_values("VENTA USD", ascending=False)
        .head(15)
    )
    top_sellers["MARGEN_%"] = (
        top_sellers["MARGEN USD"] / top_sellers["VENTA USD"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)

    fig_sell = go.Figure()
    fig_sell.add_trace(
        go.Bar(
            y=top_sellers["VENDEDOR_2"],
            x=top_sellers["VENTA USD"],
            orientation="h",
            marker_color="#3b82f6",
            marker_cornerradius=4,
            name="Venta USD",
            hovertemplate="<b>%{y}</b><br>Venta: $%{x:,.0f}<extra></extra>",
        )
    )
    fig_sell.update_layout(
        **CHART_LAYOUT,
        height=450,
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        xaxis=dict(gridcolor="#e2e8f0", title="Venta (USD)"),
    )
    st.plotly_chart(fig_sell, use_container_width=True)

with col_zone:
    st.markdown("<div class='section-header'>🗺️ Top 20 Zonas</div>", unsafe_allow_html=True)
    top_zones = (
        df.groupby("ZONA", observed=True)
        .agg({"VENTA USD": "sum", "MARGEN USD": "sum"})
        .reset_index()
        .dropna(subset=["ZONA"])
    )
    top_zones = top_zones[top_zones["VENTA USD"] > 0].sort_values("VENTA USD", ascending=False).head(20)
    fig_zone = go.Figure(
        go.Bar(
            y=top_zones["ZONA"],
            x=top_zones["VENTA USD"],
            orientation="h",
            marker=dict(
                color=top_zones["VENTA USD"],
                colorscale=[[0, "#bfdbfe"], [1, "#1d4ed8"]],
                cornerradius=4,
            ),
            hovertemplate="<b>%{y}</b><br>Venta: $%{x:,.0f}<extra></extra>",
        )
    )
    fig_zone.update_layout(
        **CHART_LAYOUT,
        height=450,
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="#e2e8f0", title="Venta (USD)"),
    )
    st.plotly_chart(fig_zone, use_container_width=True)

# ─────────────────────────────────────────────
# Row 4 – Top lines treemap
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>🧩 Venta por Línea de Producto</div>", unsafe_allow_html=True)
by_line = (
    df.groupby(["CATEGORIA_LINEA", "LINEA"], observed=True)["VENTA USD"]
    .sum()
    .reset_index()
)
by_line = by_line[by_line["VENTA USD"] > 0]
fig_tree = px.treemap(
    by_line,
    path=["CATEGORIA_LINEA", "LINEA"],
    values="VENTA USD",
    color="VENTA USD",
    color_continuous_scale="Blues",
)
fig_tree.update_layout(**CHART_LAYOUT, height=420, coloraxis_showscale=False)
fig_tree.update_traces(
    hovertemplate="<b>%{label}</b><br>Venta: $%{value:,.0f}<extra></extra>",
    textfont=dict(size=12),
)
st.plotly_chart(fig_tree, use_container_width=True)

# ─────────────────────────────────────────────
# Row 5 – Detailed table
# ─────────────────────────────────────────────
with st.expander("📋 Ver tabla de datos detallada", expanded=False):
    display_cols = [
        "FECHA", "AÑO", "MES", "CANAL", "VENDEDOR_2", "CATEGORIA_LINEA",
        "LINEA", "ARTICULO", "ZONA", "CANTIDAD", "VENTA USD", "COSTO USD", "MARGEN USD",
    ]
    existing_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(
        df[existing_cols].sort_values("FECHA", ascending=False).head(500),
        use_container_width=True,
        height=400,
    )
    st.caption(f"Mostrando las primeras 500 filas de {len(df):,} registros filtrados.")
