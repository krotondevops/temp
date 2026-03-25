import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── CONFIG ───────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard Cierres Consolidados", layout="wide")

# ─── AUTENTICACIÓN ────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; margin-top:60px;">
        <img src="https://portalclientes.kroton.com.pe/images/kroton_logo.png" style="width:180px; margin-bottom:24px;">
        <h2 style="font-family:'Inter',sans-serif; color:#0f172a; margin-bottom:8px;">Dashboard de Ventas</h2>
        <p style="color:#64748b; font-size:14px; margin-bottom:16px;">Ingrese la clave de acceso para continuar</p>
    </div>
    """, unsafe_allow_html=True)
    _col_l, _col_c, _col_r = st.columns([1.2, 1, 1.2])
    with _col_c:
        _pwd = st.text_input("Clave de acceso", type="password", placeholder="Ingrese la clave")
        if st.button("Ingresar", use_container_width=True):
            if _pwd == "krt2030":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    st.stop()

MESES_ORDEN = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


# ─── CARGA DE DATOS ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Cierres Consolidados v2.xlsx", sheet_name="Cierres_consolidados")
    df["FECHA_2"] = pd.to_datetime(df["FECHA_2"])
    df["ANIO"] = df["FECHA_2"].dt.year
    df["MES_NUM"] = df["FECHA_2"].dt.month
    df["ANIO_MES"] = df["FECHA_2"].dt.to_period("M").astype(str)
    df["VENTA USD"] = pd.to_numeric(df["VENTA USD"], errors="coerce").fillna(0)
    df["COSTO USD"] = pd.to_numeric(df["COSTO USD"], errors="coerce").fillna(0)
    df["MARGEN USD"] = pd.to_numeric(df["MARGEN USD"], errors="coerce").fillna(0)
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0)
    df = df[~df["CATEGORIA_LINEA"].isin(["FINANZAS_NC", "OTROS"])]
    df = df[~df["LINEA"].isin(["FINANZAS_NC", "OTROS"])]
    return df


df = load_data()


@st.cache_data
def load_stock():
    ds = pd.read_excel("stock_historico.xlsx", sheet_name="stock_historico")
    ds["FECHA"] = pd.to_datetime(ds["Fecha al inicio de cada mes"])
    ds["ANIO"] = ds["FECHA"].dt.year
    ds["MES_NUM"] = ds["FECHA"].dt.month
    ds["STOCK COSTO USD"] = pd.to_numeric(ds["STOCK COSTO USD"], errors="coerce").fillna(0)
    ds["UNIDADES"] = pd.to_numeric(ds["UNIDADES"], errors="coerce").fillna(0)
    return ds


df_stock = load_stock()


@st.cache_data
def load_sellout_retail():
    dso = pd.read_excel("SELL_OUT_retail.xlsx", sheet_name="Sell_out_retail")
    dso["Fecha"] = pd.to_datetime(dso["Fecha"])
    dso["ANIO"] = dso["Fecha"].dt.year
    dso["MES_NUM"] = dso["Fecha"].dt.month
    dso["ANIO_MES"] = dso["Fecha"].dt.to_period("M").astype(str)
    dso["Venta neta"] = pd.to_numeric(dso["Venta neta"], errors="coerce").fillna(0)
    dso["Unidades vendidas"] = pd.to_numeric(dso["Unidades vendidas"], errors="coerce").fillna(0)
    dso["PVP"] = pd.to_numeric(dso["PVP"], errors="coerce").fillna(0)
    return dso


df_sellout = load_sellout_retail()


@st.cache_data
def load_stock_sellout():
    dsk = pd.read_excel("SELL_OUT_retail.xlsx", sheet_name="Stock_SellOut")
    dsk["Stock valorizado"] = pd.to_numeric(dsk["Stock valorizado"], errors="coerce").fillna(0)
    dsk["Stock Unidades"] = pd.to_numeric(dsk["Stock Unidades"], errors="coerce").fillna(0)
    return dsk


df_stock_so = load_stock_sellout()


# ─── FUNCIONES ────────────────────────────────────────────────────────
def calc_margen_pct(venta, margen):
    """Replica la lógica DAX de % Margen Final."""
    if venta == 0:
        return 0.0
    if venta < 0:
        return (margen / venta) * -1
    return margen / venta


# ─── SIDEBAR / FILTROS ────────────────────────────────────────────────
st.sidebar.markdown(
    '<img src="https://portalclientes.kroton.com.pe/images/kroton_logo.png" '
    'style="width:150px; border-radius:0;">',
    unsafe_allow_html=True,
)

# ─── NAVEGACIÓN ──────────────────────────────────────────────────────
st.sidebar.markdown("---")
_page = st.sidebar.radio("Navegación", ["Dashboard", "Market Share"], horizontal=True, key="nav_page")
st.sidebar.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# PÁGINA: MARKET SHARE
# ═══════════════════════════════════════════════════════════════════════
if _page == "Market Share":
    _ms_tab_catv, _ms_tab_computo = st.tabs(["Línea CATV", "Línea COMPUTO"])

    with _ms_tab_catv:
        st.subheader("Market Share — Línea CATV")

        # Datos de market share CATV por año
        _ms_data = [
            {"empresa": "NVL",                  "2023_monto": 2564908.05, "2023_ms": 8.90,  "2024_monto": 1826249.54, "2024_ms": 7.99,  "2025_monto": 2792469.21, "2025_ms": 13.65, "2026_monto": 525384.99,  "2026_ms": 23.90},
            {"empresa": "OPTICTIMES",           "2023_monto": 9028407.06, "2023_ms": 31.32, "2024_monto": 4882733.11, "2024_ms": 21.37, "2025_monto": 2674399.25, "2025_ms": 13.07, "2026_monto": 439790.20,  "2026_ms": 20.01},
            {"empresa": "MACROTEL",             "2023_monto": 2041904.83, "2023_ms": 7.08,  "2024_monto": 4305252.09, "2024_ms": 18.85, "2025_monto": 2157461.69, "2025_ms": 10.54, "2026_monto": 347823.72,  "2026_ms": 15.82},
            {"empresa": "RING RING",            "2023_monto": 3367944.02, "2023_ms": 11.68, "2024_monto": 3216781.28, "2024_ms": 14.08, "2025_monto": 2003302.14, "2025_ms": 9.79,  "2026_monto": 204580.32,  "2026_ms": 9.31},
            {"empresa": "LANLY",                "2023_monto": 0,          "2023_ms": 0.00,  "2024_monto": 0,          "2024_ms": 0.00,  "2025_monto": 664405.89,  "2025_ms": 3.25,  "2026_monto": 152936.80,  "2026_ms": 6.96},
            {"empresa": "HAYEX",                "2023_monto": 5396810.95, "2023_ms": 18.72, "2024_monto": 3406382.91, "2024_ms": 14.91, "2025_monto": 2227740.65, "2025_ms": 10.89, "2026_monto": 138771.43,  "2026_ms": 6.31},
            {"empresa": "LATIC",                "2023_monto": 0,          "2023_ms": 0.00,  "2024_monto": 0,          "2024_ms": 0.00,  "2025_monto": 1369412.97, "2025_ms": 6.69,  "2026_monto": 133336.52,  "2026_ms": 6.07},
            {"empresa": "LIEFERANT",            "2023_monto": 1816200.30, "2023_ms": 6.30,  "2024_monto": 1542084.62, "2024_ms": 6.75,  "2025_monto": 1087556.14, "2025_ms": 5.32,  "2026_monto": 124920.14,  "2026_ms": 5.68},
            {"empresa": "SCIENTIFIC SATELLITE", "2023_monto": 1548781.48, "2023_ms": 5.37,  "2024_monto": 1219518.03, "2024_ms": 5.34,  "2025_monto": 1310996.48, "2025_ms": 6.41,  "2026_monto": 99209.96,   "2026_ms": 4.51},
            {"empresa": "KROTON",               "2023_monto": 2355368.77, "2023_ms": 8.17,  "2024_monto": 1181422.97, "2024_ms": 5.17,  "2025_monto": 3247458.12, "2025_ms": 15.87, "2026_monto": 61374.52,   "2026_ms": 2.79},
            {"empresa": "WURFEL",               "2023_monto": 467369.90,  "2023_ms": 1.62,  "2024_monto": 1264690.70, "2024_ms": 5.54,  "2025_monto": 926070.67,  "2025_ms": 4.53,  "2026_monto": 31477.21,   "2026_ms": 1.43},
            {"empresa": "MULTIPLAY",            "2023_monto": 241196.60,  "2023_ms": 0.84,  "2024_monto": 0,          "2024_ms": 0.00,  "2025_monto": 0,          "2025_ms": 0.00,  "2026_monto": 0,          "2026_ms": 0.00},
        ]
        _ms_total = {
            "2023_monto": 28828891.96, "2024_monto": 22845115.25, "2025_monto": 20461273.20, "2026_monto": 2198231.79,
        }

        _kroton_ms = {"2023": 8.17, "2024": 5.17, "2025": 15.87, "2026": 2.79}

        # ── Mini gráfico de evolución Kroton MS + KPI ──
        _ms_krt_col1, _ms_krt_col2 = st.columns([1.2, 1])

        with _ms_krt_col1:
            fig_krt_ms = go.Figure()
            _krt_years = list(_kroton_ms.keys())
            _krt_values = list(_kroton_ms.values())
            fig_krt_ms.add_trace(go.Scatter(
                x=_krt_years, y=_krt_values,
                mode="lines+markers+text",
                line=dict(color="#E31C25", width=3, shape="spline", smoothing=0.8),
                marker=dict(size=10, color="#E31C25", line=dict(width=2, color="white")),
                text=[f"{v:.1f}%" for v in _krt_values],
                textposition="top center",
                textfont=dict(size=14, color="#E31C25", family="Inter, sans-serif"),
                fill="tozeroy",
                fillcolor="rgba(227,28,37,0.06)",
                cliponaxis=False,
            ))
            fig_krt_ms.update_layout(
                height=220,
                margin=dict(t=30, b=30, l=20, r=20),
                plot_bgcolor="white",
                title=dict(text="Evolución Market Share Kroton", font=dict(size=13, color="#334155")),
                yaxis=dict(showticklabels=False, showgrid=False, title="", range=[0, max(_krt_values) * 1.5]),
                xaxis=dict(showgrid=False, type="category"),
            )
            st.plotly_chart(fig_krt_ms, use_container_width=True)

        with _ms_krt_col2:
            _krt_best_year = max(_kroton_ms, key=_kroton_ms.get)
            _krt_best_val = _kroton_ms[_krt_best_year]
            _krt_current = _kroton_ms["2026"]
            _krt_prev = _kroton_ms["2025"]
            _krt_delta = _krt_current - _krt_prev
            _krt_delta_color = "#10B981" if _krt_delta >= 0 else "#EF4444"
            _krt_delta_arrow = "&#9650;" if _krt_delta >= 0 else "&#9660;"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #0f172a, #1e3a5f); border-radius:12px; padding:20px 24px; color:white; margin-top:8px;">
                <div style="font-size:11px; color:rgba(148,163,184,0.7); letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">KROTON EN EL MERCADO CATV</div>
                <div style="display:flex; gap:24px; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">MS Actual (2026)</div>
                        <div style="font-size:28px; font-weight:700; color:#f1f5f9;">{_krt_current:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">Mejor Año</div>
                        <div style="font-size:28px; font-weight:700; color:#38bdf8;">{_krt_best_val:.2f}%</div>
                        <div style="font-size:11px; color:rgba(148,163,184,0.5);">{_krt_best_year}</div>
                    </div>
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">vs 2025</div>
                        <div style="font-size:28px; font-weight:700; color:{_krt_delta_color};">{_krt_delta_arrow} {_krt_delta:+.2f}pp</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Tabla de Market Share ──
        def _fmt_monto(v):
            if v == 0:
                return '<span style="color:#cbd5e1;">—</span>'
            return f"{v:,.2f}"

        def _fmt_ms(v):
            if v == 0:
                return '<span style="color:#cbd5e1;">0.00%</span>'
            return f"{v:.2f}%"

        def _ms_bar(v, max_v=32):
            w = min(v / max_v * 100, 100) if max_v > 0 else 0
            return f'<div style="position:relative; min-width:60px;"><div style="position:absolute; top:0; left:0; height:100%; width:{w:.0f}%; background:rgba(37,99,235,0.08); border-radius:3px;"></div><span style="position:relative; z-index:1;">{v:.2f}%</span></div>'

        _rows_html = ""
        for i, row in enumerate(_ms_data):
            is_kroton = row["empresa"] == "KROTON"
            bg = "background:linear-gradient(90deg, rgba(227,28,37,0.08), rgba(227,28,37,0.03));" if is_kroton else (
                "background:#f8fafc;" if i % 2 == 0 else "background:#ffffff;"
            )
            fw = "font-weight:700;" if is_kroton else "font-weight:400;"
            border = "border-left:3px solid #E31C25;" if is_kroton else "border-left:3px solid transparent;"
            name_color = "color:#E31C25;" if is_kroton else "color:#0f172a;"

            _rows_html += f"""<tr style="{bg}">
                <td style="padding:10px 14px; {border} {fw} {name_color} white-space:nowrap; font-size:13px;">{row['empresa']}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; color:#334155; {fw} font-variant-numeric:tabular-nums;">{_fmt_monto(row['2023_monto'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; {fw}">{_ms_bar(row['2023_ms'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; color:#334155; {fw} font-variant-numeric:tabular-nums;">{_fmt_monto(row['2024_monto'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; {fw}">{_ms_bar(row['2024_ms'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; color:#334155; {fw} font-variant-numeric:tabular-nums;">{_fmt_monto(row['2025_monto'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; {fw}">{_ms_bar(row['2025_ms'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; color:#334155; {fw} font-variant-numeric:tabular-nums;">{_fmt_monto(row['2026_monto'])}</td>
                <td style="padding:10px 12px; text-align:right; font-size:13px; {fw}">{_ms_bar(row['2026_ms'])}</td>
            </tr>"""

        _rows_html += f"""<tr style="background:#0f172a;">
            <td style="padding:12px 14px; font-weight:700; color:#f1f5f9; font-size:13px; border-left:3px solid #38bdf8;">Total general</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#f1f5f9; font-size:13px; font-variant-numeric:tabular-nums;">{_ms_total['2023_monto']:,.2f}</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#38bdf8; font-size:13px;">100.00%</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#f1f5f9; font-size:13px; font-variant-numeric:tabular-nums;">{_ms_total['2024_monto']:,.2f}</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#38bdf8; font-size:13px;">100.00%</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#f1f5f9; font-size:13px; font-variant-numeric:tabular-nums;">{_ms_total['2025_monto']:,.2f}</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#38bdf8; font-size:13px;">100.00%</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#f1f5f9; font-size:13px; font-variant-numeric:tabular-nums;">{_ms_total['2026_monto']:,.2f}</td>
            <td style="padding:12px 12px; text-align:right; font-weight:700; color:#38bdf8; font-size:13px;">100.00%</td>
        </tr>"""

        _ms_table_html = f"""
        <div style="overflow-x:auto; border-radius:12px; box-shadow:0 2px 12px rgba(15,23,42,0.08); border:1px solid #e2e8f0;">
            <table style="width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;">
                <thead>
                    <tr style="background:#0f172a;">
                        <th rowspan="2" style="padding:12px 14px; color:#f1f5f9; font-size:12px; text-align:left; letter-spacing:0.5px; font-weight:600; vertical-align:middle; border-right:1px solid rgba(255,255,255,0.1);">LINEA CATV</th>
                        <th colspan="2" style="padding:10px 12px; color:#38bdf8; font-size:12px; text-align:center; letter-spacing:1px; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);">2023</th>
                        <th colspan="2" style="padding:10px 12px; color:#38bdf8; font-size:12px; text-align:center; letter-spacing:1px; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);">2024</th>
                        <th colspan="2" style="padding:10px 12px; color:#38bdf8; font-size:12px; text-align:center; letter-spacing:1px; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);">2025</th>
                        <th colspan="2" style="padding:10px 12px; color:#38bdf8; font-size:12px; text-align:center; letter-spacing:1px; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.1);">2026</th>
                    </tr>
                    <tr style="background:#1e293b;">
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500;">MONTO</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500; border-right:1px solid rgba(255,255,255,0.1);">% MARKET SHARE</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500;">MONTO</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500; border-right:1px solid rgba(255,255,255,0.1);">% MARKET SHARE</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500;">MONTO</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500; border-right:1px solid rgba(255,255,255,0.1);">% MARKET SHARE</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500;">MONTO</th>
                        <th style="padding:8px 12px; color:#94a3b8; font-size:10px; text-align:right; letter-spacing:1px; text-transform:uppercase; font-weight:500;">% MARKET SHARE</th>
                    </tr>
                </thead>
                <tbody>
                    {_rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(_ms_table_html, unsafe_allow_html=True)

    with _ms_tab_computo:
        st.subheader("Market Share — Línea COMPUTO")

        # ── Datos Sell-In Market Share por Distribuidor ──
        _comp_dist = [
            {"dist": "DIGICORP",                    "2023": 11, "2024": 10, "2025": 13, "yoy": 56,    "vs2023": 64},
            {"dist": "FYCO GLOBAL SERVICES S.A.",    "2023": 0,  "2024": 3,  "2025": 0,  "yoy": -100,  "vs2023": None},
            {"dist": "HAYEX TECHNOLOGY S.A.C.",      "2023": 2,  "2024": 5,  "2025": 0,  "yoy": -100,  "vs2023": -100},
            {"dist": "INTCOMEX PERU S.A.C.",         "2023": 22, "2024": 24, "2025": 31, "yoy": 60,    "vs2023": 94},
            {"dist": "IT DISTRIBUTION S.A.",         "2023": 7,  "2024": 3,  "2025": 6,  "yoy": 114,   "vs2023": 12},
            {"dist": "KROTON S.A.C.",                "2023": 47, "2024": 49, "2025": 40, "yoy": -1,    "vs2023": 17},
            {"dist": "RING RING & ENERGY CORP.",     "2023": 0,  "2024": 0,  "2025": 2,  "yoy": None,  "vs2023": None},
            {"dist": "SEGO SEGURIDAD OPTIMA S.A.",   "2023": 11, "2024": 7,  "2025": 9,  "yoy": 66,    "vs2023": 16},
        ]
        _comp_dist_total = {"2023": 100, "2024": 100, "2025": 100, "yoy": 22, "vs2023": 39}

        # Kroton COMPUTO MS evolución
        _krt_comp_ms = {"2023": 47, "2024": 49, "2025": 40}

        _comp_krt_col1, _comp_krt_col2 = st.columns([1.2, 1])

        with _comp_krt_col1:
            fig_krt_comp = go.Figure()
            _kc_years = list(_krt_comp_ms.keys())
            _kc_values = list(_krt_comp_ms.values())
            fig_krt_comp.add_trace(go.Scatter(
                x=_kc_years, y=_kc_values,
                mode="lines+markers+text",
                line=dict(color="#0EA5E9", width=3, shape="spline", smoothing=0.8),
                marker=dict(size=10, color="#0EA5E9", line=dict(width=2, color="white")),
                text=[f"{v}%" for v in _kc_values],
                textposition="top center",
                textfont=dict(size=14, color="#0EA5E9", family="Inter, sans-serif"),
                fill="tozeroy",
                fillcolor="rgba(14,165,233,0.06)",
                cliponaxis=False,
            ))
            fig_krt_comp.update_layout(
                height=220,
                margin=dict(t=30, b=30, l=20, r=20),
                plot_bgcolor="white",
                title=dict(text="Evolución Market Share Kroton — COMPUTO", font=dict(size=13, color="#334155")),
                yaxis=dict(showticklabels=False, showgrid=False, title="", range=[0, max(_kc_values) * 1.4]),
                xaxis=dict(showgrid=False, type="category"),
            )
            st.plotly_chart(fig_krt_comp, use_container_width=True)

        with _comp_krt_col2:
            _kc_current = _krt_comp_ms["2025"]
            _kc_prev = _krt_comp_ms["2024"]
            _kc_delta = _kc_current - _kc_prev
            _kc_best_year = max(_krt_comp_ms, key=_krt_comp_ms.get)
            _kc_best_val = _krt_comp_ms[_kc_best_year]
            _kc_delta_color = "#10B981" if _kc_delta >= 0 else "#EF4444"
            _kc_delta_arrow = "&#9650;" if _kc_delta >= 0 else "&#9660;"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #0f172a, #1e3a5f); border-radius:12px; padding:20px 24px; color:white; margin-top:8px;">
                <div style="font-size:11px; color:rgba(148,163,184,0.7); letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">KROTON EN LÍNEA COMPUTO</div>
                <div style="display:flex; gap:24px; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">MS Actual (2025)</div>
                        <div style="font-size:28px; font-weight:700; color:#f1f5f9;">{_kc_current}%</div>
                    </div>
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">Mejor Año</div>
                        <div style="font-size:28px; font-weight:700; color:#38bdf8;">{_kc_best_val}%</div>
                        <div style="font-size:11px; color:rgba(148,163,184,0.5);">{_kc_best_year}</div>
                    </div>
                    <div>
                        <div style="font-size:10px; color:rgba(148,163,184,0.6); text-transform:uppercase;">YoY</div>
                        <div style="font-size:28px; font-weight:700; color:{_kc_delta_color};">{_kc_delta_arrow} {_kc_delta:+d}pp</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Sección: Sell-In Market Share ──
        st.markdown("""
        <div style="margin-top:32px; margin-bottom:20px; position:relative; overflow:hidden; border-radius:12px; padding:24px 28px; background:linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 40%, #99f6e4 100%); border-left:5px solid #14b8a6;">
            <div style="position:absolute; top:-20px; right:-10px; width:120px; height:120px; background:radial-gradient(circle, rgba(20,184,166,0.15) 0%, transparent 70%); pointer-events:none;"></div>
            <div style="font-family:'Inter',sans-serif; font-size:24px; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">Sell-In Market Share</div>
            <div style="font-family:'Inter',sans-serif; font-size:13px; color:#475569; margin-top:4px;">Participación de mercado por distribuidor y marca — Línea COMPUTO</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabla 1: Sell-In Market Share por Distribuidor ──
        st.markdown("##### Por Distribuidor")

        def _comp_pct(v):
            if v is None:
                return '<span style="color:#cbd5e1;">—</span>'
            return f"{v}%"

        def _comp_growth(v):
            if v is None:
                return '<span style="color:#cbd5e1;">—</span>'
            color = "#10B981" if v > 0 else "#EF4444" if v < 0 else "#64748b"
            arrow = "&#9650;" if v > 0 else "&#9660;" if v < 0 else ""
            return f'<span style="color:{color}; font-weight:600;">{arrow} {v:+d}%</span>'

        _comp_rows = ""
        for i, r in enumerate(_comp_dist):
            is_krt = "KROTON" in r["dist"]
            bg = "background:linear-gradient(90deg, rgba(14,165,233,0.08), rgba(14,165,233,0.02));" if is_krt else (
                "background:#f8fafc;" if i % 2 == 0 else "background:#ffffff;"
            )
            fw = "font-weight:700;" if is_krt else "font-weight:400;"
            border = "border-left:3px solid #0EA5E9;" if is_krt else "border-left:3px solid transparent;"
            nc = "color:#0EA5E9;" if is_krt else "color:#0f172a;"

            _comp_rows += f"""<tr style="{bg}">
                <td style="padding:10px 14px; {border} {fw} {nc} white-space:nowrap; font-size:13px;">{r['dist']}</td>
                <td style="padding:10px 12px; text-align:center; font-size:13px; {fw}">{_comp_pct(r['2023'])}</td>
                <td style="padding:10px 12px; text-align:center; font-size:13px; {fw}">{_comp_pct(r['2024'])}</td>
                <td style="padding:10px 12px; text-align:center; font-size:13px; {fw}">{_comp_pct(r['2025'])}</td>
                <td style="padding:10px 12px; text-align:center; font-size:13px;">{_comp_growth(r['yoy'])}</td>
                <td style="padding:10px 12px; text-align:center; font-size:13px;">{_comp_growth(r['vs2023'])}</td>
            </tr>"""

        _comp_rows += f"""<tr style="background:#0f172a;">
            <td style="padding:12px 14px; font-weight:700; color:#f1f5f9; font-size:13px; border-left:3px solid #38bdf8;">Total general</td>
            <td style="padding:12px 12px; text-align:center; font-weight:700; color:#38bdf8; font-size:13px;">{_comp_dist_total['2023']}%</td>
            <td style="padding:12px 12px; text-align:center; font-weight:700; color:#38bdf8; font-size:13px;">{_comp_dist_total['2024']}%</td>
            <td style="padding:12px 12px; text-align:center; font-weight:700; color:#38bdf8; font-size:13px;">{_comp_dist_total['2025']}%</td>
            <td style="padding:12px 12px; text-align:center; font-weight:700; color:#10B981; font-size:13px;">&#9650; +{_comp_dist_total['yoy']}%</td>
            <td style="padding:12px 12px; text-align:center; font-weight:700; color:#10B981; font-size:13px;">&#9650; +{_comp_dist_total['vs2023']}%</td>
        </tr>"""

        _comp_t1_html = f"""
        <div style="overflow-x:auto; border-radius:12px; box-shadow:0 2px 12px rgba(15,23,42,0.08); border:1px solid #e2e8f0; margin-bottom:32px;">
            <table style="width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;">
                <thead>
                    <tr style="background:#0f172a;">
                        <th style="padding:12px 14px; color:#f1f5f9; font-size:12px; text-align:left; font-weight:600; letter-spacing:0.5px;">Distribuidor</th>
                        <th style="padding:12px 12px; color:#38bdf8; font-size:12px; text-align:center; font-weight:600;">2023</th>
                        <th style="padding:12px 12px; color:#38bdf8; font-size:12px; text-align:center; font-weight:600;">2024</th>
                        <th style="padding:12px 12px; color:#38bdf8; font-size:12px; text-align:center; font-weight:600;">2025</th>
                        <th style="padding:12px 12px; color:#F59E0B; font-size:12px; text-align:center; font-weight:600;">YoY</th>
                        <th style="padding:12px 12px; color:#F59E0B; font-size:12px; text-align:center; font-weight:600;">vs 2023</th>
                    </tr>
                </thead>
                <tbody>{_comp_rows}</tbody>
            </table>
        </div>
        """
        st.markdown(_comp_t1_html, unsafe_allow_html=True)

        # ── Tabla 2: Market Share por Brand / División ──
        st.markdown("##### Por Brand / División")

        _comp_brand = [
            {"brand": "Mercusys",       "div": "",                      "digicorp": 12, "intcomex": 58, "itd": 11, "kroton": 19, "rr": 0,  "sego": 0,  "tpe": 2,   "growth": 100},
            {"brand": "Omada",          "div": "",                      "digicorp": 23, "intcomex": 20, "itd": 3,  "kroton": 38, "rr": 1,  "sego": 15, "tpe": 15,  "growth": 53},
            {"brand": "Tapo",           "div": "",                      "digicorp": 12, "intcomex": 54, "itd": 5,  "kroton": 29, "rr": 0,  "sego": 0,  "tpe": 15,  "growth": 22},
            {"brand": "TP-Link",        "div": "Consumer Networking",   "digicorp": 11, "intcomex": 29, "itd": 7,  "kroton": 41, "rr": 1,  "sego": 10, "tpe": 75,  "growth": 41},
            {"brand": "TP-Link",        "div": "Enterprise Networking", "digicorp": 11, "intcomex": 16, "itd": 7,  "kroton": 50, "rr": 0,  "sego": 16, "tpe": 17,  "growth": 28},
            {"brand": "TP-Link",        "div": "Service Provider",      "digicorp": 10, "intcomex": 8,  "itd": 0,  "kroton": 55, "rr": 24, "sego": 3,  "tpe": 8,   "growth": -67},
        ]
        _comp_brand_tplink = {"brand": "Total TP-Link", "div": "", "digicorp": 11, "intcomex": 25, "itd": 7, "kroton": 44, "rr": 3, "sego": 10, "tpe": 65, "growth": 11}
        _comp_brand_vigi = {"brand": "VIGI", "div": "", "digicorp": 0, "intcomex": 81, "itd": 0, "kroton": 19, "rr": 0, "sego": 0, "tpe": 2, "growth": 13728}
        _comp_brand_total = {"brand": "Total general", "div": "", "digicorp": 13, "intcomex": 31, "itd": 6, "kroton": 40, "rr": 2, "sego": 9, "tpe": 100, "growth": 22}

        _dist_cols = ["DIGICORP", "INTCOMEX", "ITD", "KROTON", "RING RING", "SEGO", "TPE", "Growth"]
        _dist_keys = ["digicorp", "intcomex", "itd", "kroton", "rr", "sego", "tpe", "growth"]

        def _brand_cell(v, key, is_total=False):
            if key == "growth":
                color = "#10B981" if v > 0 else "#EF4444" if v < 0 else "#64748b"
                arrow = "&#9650;" if v > 0 else "&#9660;" if v < 0 else ""
                return f'<span style="color:{color}; font-weight:600;">{arrow} {v:+,d}%</span>'
            fw = "font-weight:700;" if is_total else ""
            # Highlight Kroton column
            if key == "kroton":
                return f'<span style="color:#0EA5E9; font-weight:600;">{v}%</span>'
            return f'<span style="{fw}">{v}%</span>'

        def _brand_row(r, bg_style, is_subtotal=False, is_total=False):
            fw = "font-weight:700;" if is_subtotal or is_total else "font-weight:400;"
            nc = "color:#0f172a;"
            border = "border-left:3px solid transparent;"
            if is_total:
                bg_style = "background:#0f172a;"
                nc = "color:#f1f5f9;"
                border = "border-left:3px solid #38bdf8;"
            elif is_subtotal:
                bg_style = "background:#e2e8f0;"

            brand_text = r['brand']
            div_text = r['div']

            cells = f'<td style="padding:10px 14px; {border} {fw} {nc} font-size:13px; white-space:nowrap;">{brand_text}</td>'
            cells += f'<td style="padding:10px 12px; {fw} {nc} font-size:12px; color:#64748b;">{div_text}</td>'
            for key in _dist_keys:
                cell_color = "color:#38bdf8;" if is_total else ""
                cells += f'<td style="padding:10px 12px; text-align:center; font-size:13px; {cell_color}">{_brand_cell(r[key], key, is_total)}</td>'
            return f'<tr style="{bg_style}">{cells}</tr>'

        _brand_rows = ""
        for i, r in enumerate(_comp_brand):
            bg = "background:#f8fafc;" if i % 2 == 0 else "background:#ffffff;"
            _brand_rows += _brand_row(r, bg)

        _brand_rows += _brand_row(_comp_brand_tplink, "", is_subtotal=True)
        _brand_rows += _brand_row(_comp_brand_vigi, "background:#ffffff;")
        _brand_rows += _brand_row(_comp_brand_total, "", is_total=True)

        _th_style = 'padding:12px 10px; font-size:11px; text-align:center; font-weight:600; letter-spacing:0.5px;'
        _comp_t2_html = f"""
        <div style="overflow-x:auto; border-radius:12px; box-shadow:0 2px 12px rgba(15,23,42,0.08); border:1px solid #e2e8f0;">
            <table style="width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;">
                <thead>
                    <tr style="background:#0f172a;">
                        <th style="{_th_style} color:#f1f5f9; text-align:left; padding-left:14px;">Brand</th>
                        <th style="{_th_style} color:#f1f5f9; text-align:left;">División</th>
                        <th style="{_th_style} color:#94a3b8;">DIGICORP</th>
                        <th style="{_th_style} color:#94a3b8;">INTCOMEX</th>
                        <th style="{_th_style} color:#94a3b8;">ITD</th>
                        <th style="{_th_style} color:#0EA5E9;">KROTON</th>
                        <th style="{_th_style} color:#94a3b8;">RING RING</th>
                        <th style="{_th_style} color:#94a3b8;">SEGO</th>
                        <th style="{_th_style} color:#F59E0B;">TPE</th>
                        <th style="{_th_style} color:#F59E0B;">Growth</th>
                    </tr>
                </thead>
                <tbody>{_brand_rows}</tbody>
            </table>
        </div>
        """
        st.markdown(_comp_t2_html, unsafe_allow_html=True)

        # ── Sección: Sell-In vs Sell-Through ──
        st.markdown("""
        <div style="margin-top:40px; margin-bottom:20px; position:relative; overflow:hidden; border-radius:12px; padding:24px 28px; background:linear-gradient(135deg, #fffbeb 0%, #fef3c7 40%, #fde68a 100%); border-left:5px solid #f59e0b;">
            <div style="position:absolute; top:-20px; right:-10px; width:120px; height:120px; background:radial-gradient(circle, rgba(245,158,11,0.15) 0%, transparent 70%); pointer-events:none;"></div>
            <div style="font-family:'Inter',sans-serif; font-size:24px; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">Sell-In vs. Sell-Through</div>
            <div style="font-family:'Inter',sans-serif; font-size:13px; color:#475569; margin-top:4px;">Comparativo mensual de ingreso vs salida — Línea COMPUTO (2025)</div>
        </div>
        """, unsafe_allow_html=True)

        _sivst_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]
        _sivst_si = [622455, 305504, 489050, 484340, 357704, 307907, 461754, 547588, 125086, 419007, 737095, 399560]
        _sivst_st = [714552, 448717, 516263, 543543, 488994, 609858, 478213, 471032, 670989, 405073, 591251, 460300]
        _sivst_si_total = 5257050
        _sivst_st_total = 6398785

        # ── Tabla resumen ──
        _sivst_cells_si = "".join([f'<td style="padding:10px 8px; text-align:right; font-size:12px; color:#B45309; font-weight:500; font-variant-numeric:tabular-nums;">{v:,.0f}</td>' for v in _sivst_si])
        _sivst_cells_st = "".join([f'<td style="padding:10px 8px; text-align:right; font-size:12px; color:#0891B2; font-weight:500; font-variant-numeric:tabular-nums;">{v:,.0f}</td>' for v in _sivst_st])

        _sivst_table = f"""
        <div style="overflow-x:auto; border-radius:12px; box-shadow:0 2px 12px rgba(15,23,42,0.08); border:1px solid #e2e8f0; margin-bottom:24px;">
            <table style="width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;">
                <thead>
                    <tr style="background:#0f172a;">
                        <th style="padding:10px 14px; color:#f1f5f9; font-size:11px; text-align:left; font-weight:600; min-width:100px;"></th>
                        {"".join([f'<th style="padding:10px 8px; color:#38bdf8; font-size:11px; text-align:right; font-weight:600;">{m}</th>' for m in _sivst_meses])}
                        <th style="padding:10px 10px; color:#F59E0B; font-size:11px; text-align:right; font-weight:700;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background:#fffbeb;">
                        <td style="padding:10px 14px; font-weight:700; font-size:12px; color:#B45309; border-left:3px solid #F59E0B;">Sell-In</td>
                        {_sivst_cells_si}
                        <td style="padding:10px 10px; text-align:right; font-weight:700; font-size:12px; color:#B45309; font-variant-numeric:tabular-nums;">${_sivst_si_total:,.0f}</td>
                    </tr>
                    <tr style="background:#ecfeff;">
                        <td style="padding:10px 14px; font-weight:700; font-size:12px; color:#0891B2; border-left:3px solid #06B6D4;">Sell-Through</td>
                        {_sivst_cells_st}
                        <td style="padding:10px 10px; text-align:right; font-weight:700; font-size:12px; color:#0891B2; font-variant-numeric:tabular-nums;">${_sivst_st_total:,.0f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        st.markdown(_sivst_table, unsafe_allow_html=True)

        # ── Gráfico Sell-In vs Sell-Through ──
        fig_sivst = go.Figure()

        fig_sivst.add_trace(go.Scatter(
            x=_sivst_meses, y=_sivst_si,
            name="Sell-In",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=3, shape="spline", smoothing=0.8),
            marker=dict(size=7, color="#F59E0B"),
            hovertemplate="<b>Sell-In</b><br>%{x}: $%{y:,.0f}<extra></extra>",
        ))

        fig_sivst.add_trace(go.Scatter(
            x=_sivst_meses, y=_sivst_st,
            name="Sell-Through",
            mode="lines+markers",
            line=dict(color="#06B6D4", width=3, shape="spline", smoothing=0.8),
            marker=dict(size=7, color="#06B6D4"),
            hovertemplate="<b>Sell-Through</b><br>%{x}: $%{y:,.0f}<extra></extra>",
        ))

        fig_sivst.update_layout(
            height=420,
            margin=dict(t=30, b=40, l=20, r=20),
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                        font=dict(size=13)),
            yaxis=dict(showgrid=True, gridcolor="rgba(226,232,240,0.6)", gridwidth=1,
                       tickformat=",.0f", tickfont=dict(size=11, color="#94a3b8"),
                       title=""),
            xaxis=dict(showgrid=False, type="category"),
        )
        st.plotly_chart(fig_sivst, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
st.sidebar.title("Filtros")

all_canales = sorted(df["CANAL"].unique())
all_categorias = sorted(df["CATEGORIA_LINEA"].unique())
all_vendedores = sorted(df["VENDEDOR_NUEVO"].unique())
all_anios = sorted(df["ANIO"].unique())
all_meses = sorted(df["MES"].unique(), key=lambda m: MESES_ORDEN.get(m, 0))

# Filtros tipo lista con expander colapsable
def filtro_lista(label, opciones, key_prefix, default=None, expanded=False):
    with st.sidebar.expander(label, expanded=expanded):
        todos_default = default is None
        todos = st.checkbox("Todos", value=todos_default, key=f"{key_prefix}_todos")
        if todos:
            return list(opciones)
        seleccionados = []
        for op in opciones:
            val_default = (op in default) if default else False
            if st.checkbox(str(op), value=val_default, key=f"{key_prefix}_{op}"):
                seleccionados.append(op)
        return seleccionados if seleccionados else list(opciones)

canal_sel = filtro_lista("Canal", all_canales, "canal", default=["RETAIL"], expanded=True)
cat_sel = filtro_lista("Categoría", all_categorias, "cat")
vend_sel = filtro_lista("Vendedor", all_vendedores, "vend")
anio_sel = filtro_lista("Año", all_anios, "anio")
mes_sel = filtro_lista("Mes", all_meses, "mes")

# Aplicar filtros
mask = (
    df["ANIO"].isin(anio_sel)
    & df["MES"].isin(mes_sel)
    & df["CANAL"].isin(canal_sel)
    & df["CATEGORIA_LINEA"].isin(cat_sel)
    & df["VENDEDOR_NUEVO"].isin(vend_sel)
)
dff = df[mask].copy()

# Excluir clientes no relevantes
dff = dff[~dff["CLIENTE"].isin(["TP-LINK PERU S.A.C.", "SAGA FALABELLA S.A."])]

# Agrupar razones sociales por grupo
dff["CLIENTE"] = dff["CLIENTE"].replace({
    "TIENDAS DEL MEJORAMIENTO DEL HOGAR S.A.": "SODIMAC",
    "SODIMAC PERU ORIENTE S.A.C.": "SODIMAC",
    "HOMECENTERS PERUANOS S.A.": "PROMART",
    "HOMECENTERS PERUANOS ORIENTE S.A.C.": "PROMART",
})


# ─── HEADER ───────────────────────────────────────────────────────────
total_venta = dff["VENTA USD"].sum()
total_margen = dff["MARGEN USD"].sum()
pct_margen = calc_margen_pct(total_venta, total_margen)

# Venta promedio mensual por año
dff_2025 = dff[dff["ANIO"] == 2025]
dff_2026 = dff[dff["ANIO"] == 2026]
meses_2025 = dff_2025["MES_NUM"].nunique()
meses_2026 = dff_2026["MES_NUM"].nunique()
prom_2025 = dff_2025["VENTA USD"].sum() / meses_2025 if meses_2025 > 0 else 0
prom_2026 = dff_2026["VENTA USD"].sum() / meses_2026 if meses_2026 > 0 else 0
margen_2025 = calc_margen_pct(dff_2025["VENTA USD"].sum(), dff_2025["MARGEN USD"].sum())
margen_2026 = calc_margen_pct(dff_2026["VENTA USD"].sum(), dff_2026["MARGEN USD"].sum())

# Ticket promedio por año: solo documentos con venta positiva
docs_pos_2025 = dff_2025.groupby("TIPO_DOC")["VENTA USD"].sum()
docs_pos_2025 = docs_pos_2025[docs_pos_2025 > 0]
ticket_2025 = docs_pos_2025.mean() if len(docs_pos_2025) > 0 else 0

docs_pos_2026 = dff_2026.groupby("TIPO_DOC")["VENTA USD"].sum()
docs_pos_2026 = docs_pos_2026[docs_pos_2026 > 0]
ticket_2026 = docs_pos_2026.mean() if len(docs_pos_2026) > 0 else 0

# Formatear ventas en miles (K) para mejor legibilidad
def fmt_k(val):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:,.2f}M"
    if abs(val) >= 1_000:
        return f"${val/1_000:,.1f}K"
    return f"${val:,.0f}"

# YoY Sell In
_si_yoy = ((prom_2026 / prom_2025) - 1) if prom_2025 != 0 else 0

# ── Estilos globales del dashboard ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Ocultar métricas nativas */
[data-testid="stMetricValue"] { font-size: 1.6rem !important; }

/* Header principal */
.dash-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
    border-radius: 16px;
    padding: 28px 32px 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(15, 23, 42, 0.3), 0 2px 8px rgba(0,0,0,0.1);
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.dash-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.dash-title {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0;
}
.dash-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 400;
    color: rgba(148,163,184,0.8);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
}

/* Sección KPI */
.kpi-section {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 8px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.kpi-section:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(255,255,255,0.15);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.kpi-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: rgba(148,163,184,0.7);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.kpi-section-label .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}
.kpi-year {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: rgba(56,189,248,0.6);
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.kpi-row {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}
.kpi-card {
    flex: 1;
    min-width: 100px;
}
.kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 500;
    color: rgba(148,163,184,0.6);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.kpi-value {
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
    line-height: 1.2;
}
.kpi-value.accent { color: #38bdf8; }
.kpi-value.green { color: #34d399; }
.kpi-value.amber { color: #fbbf24; }

/* Badge YoY */
.yoy-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    margin-left: 12px;
    vertical-align: middle;
}
.yoy-badge.up { background: rgba(52,211,153,0.15); color: #34d399; }
.yoy-badge.down { background: rgba(248,113,113,0.15); color: #f87171; }

/* Divider */
.kpi-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 14px 0;
}

/* Columnas año lado a lado */
.kpi-years-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Construir HTML del header ──
_canal_tag = f'<span style="font-size:12px; background:rgba(56,189,248,0.15); color:#38bdf8; padding:3px 12px; border-radius:20px; font-weight:600; letter-spacing:0.5px; margin-left:12px; vertical-align:middle;">{", ".join(canal_sel)}</span>' if len(canal_sel) < len(all_canales) else ''

_si_yoy_cls = "up" if _si_yoy >= 0 else "down"
_si_yoy_arrow = "&#9650;" if _si_yoy >= 0 else "&#9660;"
_si_yoy_badge = f'<span class="yoy-badge {_si_yoy_cls}">{_si_yoy_arrow} {_si_yoy:+.1%}</span>'

_header_html = f'''<div class="dash-header">
  <div class="dash-title">Dashboard de Ventas {_canal_tag}</div>
  <div class="dash-subtitle">Kroton &mdash; Resumen ejecutivo</div>

  <div class="kpi-section">
    <div class="kpi-section-label">{'<span class="dot" style="background:#38bdf8;"></span>SELL IN' if canal_sel == ["RETAIL"] else ''} {_si_yoy_badge}</div>
    <div class="kpi-years-grid">
      <div>
        <div class="kpi-year">2025</div>
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-label">Vta. Prom. Mes</div><div class="kpi-value accent">{fmt_k(prom_2025)}</div></div>
          <div class="kpi-card"><div class="kpi-label">Margen</div><div class="kpi-value green">{margen_2025:.1%}</div></div>
          <div class="kpi-card"><div class="kpi-label">Ticket Prom.</div><div class="kpi-value">{fmt_k(ticket_2025)}</div></div>
        </div>
      </div>
      <div>
        <div class="kpi-year">2026</div>
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-label">Vta. Prom. Mes</div><div class="kpi-value accent">{fmt_k(prom_2026)}</div></div>
          <div class="kpi-card"><div class="kpi-label">Margen</div><div class="kpi-value green">{margen_2026:.1%}</div></div>
          <div class="kpi-card"><div class="kpi-label">Ticket Prom.</div><div class="kpi-value">{fmt_k(ticket_2026)}</div></div>
        </div>
      </div>
    </div>
  </div>'''

# Sell Out KPIs (solo RETAIL)
if canal_sel == ["RETAIL"]:
    _TC_KPI = 3.40
    _so_kpi_25 = df_sellout[df_sellout["ANIO"] == 2025]
    _so_kpi_26 = df_sellout[df_sellout["ANIO"] == 2026]
    _so_m25 = _so_kpi_25["MES_NUM"].nunique() or 1
    _so_m26 = _so_kpi_26["MES_NUM"].nunique() or 1
    _so_prom_vta_25 = (_so_kpi_25["Venta neta"].sum() / _TC_KPI) / _so_m25
    _so_prom_vta_26 = (_so_kpi_26["Venta neta"].sum() / _TC_KPI) / _so_m26
    _so_prom_uds_25 = _so_kpi_25["Unidades vendidas"].sum() / _so_m25
    _so_prom_uds_26 = _so_kpi_26["Unidades vendidas"].sum() / _so_m26
    _so_ticket_25 = _so_kpi_25["PVP"].mean() / _TC_KPI if len(_so_kpi_25) > 0 else 0
    _so_ticket_26 = _so_kpi_26["PVP"].mean() / _TC_KPI if len(_so_kpi_26) > 0 else 0
    _so_yoy_kpi = ((_so_prom_vta_26 / _so_prom_vta_25) - 1) if _so_prom_vta_25 != 0 else 0
    _so_yoy_cls = "up" if _so_yoy_kpi >= 0 else "down"
    _so_yoy_arrow = "&#9650;" if _so_yoy_kpi >= 0 else "&#9660;"
    _so_yoy_badge = f'<span class="yoy-badge {_so_yoy_cls}">{_so_yoy_arrow} {_so_yoy_kpi:+.1%}</span>'

    _header_html += f'''
  <div class="kpi-divider"></div>
  <div class="kpi-section">
    <div class="kpi-section-label"><span class="dot" style="background:#34d399;"></span>SELL OUT RETAIL {_so_yoy_badge}</div>
    <div class="kpi-years-grid">
      <div>
        <div class="kpi-year">2025</div>
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-label">Vta. Prom. Mes</div><div class="kpi-value accent">{fmt_k(_so_prom_vta_25)}</div></div>
          <div class="kpi-card"><div class="kpi-label">Und. Prom. Mes</div><div class="kpi-value amber">{_so_prom_uds_25:,.0f}</div></div>
          <div class="kpi-card"><div class="kpi-label">Ticket Prom.</div><div class="kpi-value">${_so_ticket_25:,.1f}</div></div>
        </div>
      </div>
      <div>
        <div class="kpi-year">2026</div>
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-label">Vta. Prom. Mes</div><div class="kpi-value accent">{fmt_k(_so_prom_vta_26)}</div></div>
          <div class="kpi-card"><div class="kpi-label">Und. Prom. Mes</div><div class="kpi-value amber">{_so_prom_uds_26:,.0f}</div></div>
          <div class="kpi-card"><div class="kpi-label">Ticket Prom.</div><div class="kpi-value">${_so_ticket_26:,.1f}</div></div>
        </div>
      </div>
    </div>
  </div>'''

_header_html += '</div>'
st.markdown(_header_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# 1. EVOLUTIVO MENSUAL — Venta USD + % Margen
# ═══════════════════════════════════════════════════════════════════════
MESES_ESP = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}

st.markdown("---")
st.subheader("Evolutivo Mensual Sell In — Venta USD y % Margen")

evo = (
    dff.groupby(["ANIO", "MES_NUM", "ANIO_MES"])
    .agg(VENTA=("VENTA USD", "sum"), MARGEN=("MARGEN USD", "sum"))
    .reset_index()
    .sort_values(["ANIO", "MES_NUM"])
)
evo["% Margen"] = evo.apply(lambda r: calc_margen_pct(r["VENTA"], r["MARGEN"]), axis=1)
evo["MES_LABEL"] = evo.apply(lambda r: f"{MESES_ESP[r['MES_NUM']]} {r['ANIO']}", axis=1)

if canal_sel == ["RETAIL"]:
    # ── RETAIL: barras agrupadas por CLIENTE_GRUPO ──
    _cg_palette = {
        "SODIMAC": "#2563EB",
        "PROMART": "#E67E22",
        "COOLBOX": "#E31C25",
    }

    evo_cg = (
        dff[dff["CLIENTE_GRUPO"] != "ESTILOS"]
        .groupby(["CLIENTE_GRUPO", "ANIO", "MES_NUM"])
        .agg(VENTA=("VENTA USD", "sum"))
        .reset_index()
        .sort_values(["ANIO", "MES_NUM"])
    )
    evo_cg["MES_LABEL"] = evo_cg.apply(
        lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
    )

    _si_x_labels = evo["MES_LABEL"].tolist()
    _si_totales = evo_cg.groupby("MES_LABEL")["VENTA"].sum().reindex(_si_x_labels).fillna(0)
    _si_max_bar = evo_cg.groupby("MES_LABEL")["VENTA"].max().reindex(_si_x_labels).fillna(0)

    fig_evo = make_subplots(specs=[[{"secondary_y": True}]])

    _cg_order = evo_cg.groupby("CLIENTE_GRUPO")["VENTA"].sum().sort_values(ascending=False).index
    for _cg in _cg_order:
        _cg_data = evo_cg[evo_cg["CLIENTE_GRUPO"] == _cg]
        _color = _cg_palette.get(_cg, "#6B7280")
        fig_evo.add_trace(
            go.Bar(
                x=_cg_data["MES_LABEL"],
                y=_cg_data["VENTA"],
                name=_cg,
                marker_color=_color,
                customdata=_cg_data["VENTA"].apply(fmt_k),
                hovertemplate="<b>%{x}</b><br>" + _cg + ": %{customdata}<extra></extra>",
                cliponaxis=False,
            ),
            secondary_y=False,
        )

    # % Margen (línea general)
    fig_evo.add_trace(
        go.Scatter(
            x=evo["MES_LABEL"],
            y=evo["% Margen"],
            name="% Margen",
            mode="lines+markers+text",
            line=dict(color="#F59E0B", width=3, shape="spline", smoothing=0.8),
            marker=dict(size=8),
            text=evo["% Margen"].apply(lambda v: f"{v:.1%}"),
            textposition="top center",
            textfont=dict(size=14, color="#F59E0B"),
            cliponaxis=False,
        ),
        secondary_y=True,
    )

    # Anotaciones con total mensual
    _si_annotations = []
    for _lbl in _si_x_labels:
        _total_val = _si_totales.get(_lbl, 0)
        _max_bar_val = _si_max_bar.get(_lbl, 0)
        if _total_val > 0:
            _si_annotations.append(dict(
                x=_lbl,
                y=_max_bar_val * 1.35,
                text=f"<b>{fmt_k(_total_val)}</b>",
                showarrow=False,
                font=dict(size=12, color="#334155", family="Inter, sans-serif"),
                xanchor="center",
                yanchor="bottom",
            ))

    _si_venta_max = _si_totales.max() if not _si_totales.empty else 1
    fig_evo.update_layout(
        height=500,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        yaxis2_title="",
        barmode="group",
        bargap=0.25,
        bargroupgap=0.05,
        plot_bgcolor="white",
        annotations=_si_annotations,
    )
    fig_evo.update_yaxes(showticklabels=False, title="", showgrid=False, range=[0, _si_venta_max * 2.0], secondary_y=False)
    fig_evo.update_yaxes(showticklabels=False, title="", showgrid=False, secondary_y=True, range=[0, evo["% Margen"].max() * 1.3] if not evo.empty else None)
    fig_evo.update_xaxes(showgrid=False, categoryorder="array", categoryarray=_si_x_labels)

else:
    # ── Otros canales: barra única ──
    if not evo.empty:
        idx_best = evo["VENTA"].idxmax()
        idx_worst = evo["VENTA"].idxmin()
        text_colors = []
        for i in evo.index:
            if i == idx_best:
                text_colors.append("#10B981")
            elif i == idx_worst:
                text_colors.append("#EF4444")
            else:
                text_colors.append("#1E3A5F")
    else:
        text_colors = "#1E3A5F"

    fig_evo = make_subplots(specs=[[{"secondary_y": True}]])

    fig_evo.add_trace(
        go.Bar(
            x=evo["MES_LABEL"],
            y=evo["VENTA"],
            name="Venta USD",
            marker_color="#2563EB",
            text=evo["VENTA"].apply(fmt_k),
            textposition="outside",
            textfont=dict(size=14, color=text_colors),
            cliponaxis=False,
        ),
        secondary_y=False,
    )

    fig_evo.add_trace(
        go.Scatter(
            x=evo["MES_LABEL"],
            y=evo["% Margen"],
            name="% Margen",
            mode="lines+markers+text",
            line=dict(color="#F59E0B", width=3, shape="spline", smoothing=0.8),
            marker=dict(size=8),
            text=evo["% Margen"].apply(lambda v: f"{v:.1%}"),
            textposition="top center",
            textfont=dict(size=14, color="#F59E0B"),
            cliponaxis=False,
        ),
        secondary_y=True,
    )

    venta_max = evo["VENTA"].max() if not evo.empty else 1
    fig_evo.update_layout(
        height=450,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis2_title="",
        bargap=0.3,
        plot_bgcolor="white",
    )
    fig_evo.update_yaxes(showticklabels=False, title="", showgrid=False, range=[0, venta_max * 2.2], secondary_y=False)
    fig_evo.update_yaxes(showticklabels=False, title="", showgrid=False, secondary_y=True, range=[0, evo["% Margen"].max() * 1.3] if not evo.empty else None)
    fig_evo.update_xaxes(showgrid=False)

st.plotly_chart(fig_evo, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# 2. EVOLUTIVO TICKET PROMEDIO
# ═══════════════════════════════════════════════════════════════════════
st.subheader("Evolutivo Mensual Sell In — Ticket Promedio")

evo_ticket = (
    dff.groupby(["ANIO", "MES_NUM", "TIPO_DOC"])
    .agg(VENTA=("VENTA USD", "sum"))
    .reset_index()
)
evo_ticket = evo_ticket[evo_ticket["VENTA"] > 0]
evo_ticket_mes = (
    evo_ticket.groupby(["ANIO", "MES_NUM"])
    .agg(TICKET=("VENTA", "mean"))
    .reset_index()
    .sort_values(["ANIO", "MES_NUM"])
)
evo_ticket_mes["MES_LABEL"] = evo_ticket_mes.apply(
    lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
)

fig_ticket = go.Figure()
fig_ticket.add_trace(
    go.Scatter(
        x=evo_ticket_mes["MES_LABEL"],
        y=evo_ticket_mes["TICKET"],
        mode="lines+markers+text",
        line=dict(color="#8B5CF6", width=3, shape="spline", smoothing=0.8),
        marker=dict(size=8, color="#8B5CF6"),
        text=evo_ticket_mes["TICKET"].apply(lambda v: f"${v:,.0f}"),
        textposition="top center",
        textfont=dict(size=16, color="#5B21B6"),
        cliponaxis=False,
        name="Ticket Promedio",
    )
)

fig_ticket.update_layout(
    height=400,
    margin=dict(t=50, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="white",
)
fig_ticket.update_yaxes(showticklabels=False, showgrid=False, title="")
fig_ticket.update_xaxes(showgrid=False)
st.plotly_chart(fig_ticket, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# 3. TOP 10 Y BOTTOM 10 CLIENTES POR AÑO
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Top 10 y Bottom 10 Clientes — Sell In")

def ranking_clientes(data, year):
    data_year = data[data["ANIO"] == year]
    n_meses = data_year["MES_NUM"].nunique()
    n_meses = n_meses if n_meses > 0 else 1
    total_vta = data_year["VENTA USD"].sum()
    agg = (
        data_year.groupby("CLIENTE")
        .agg(VENTA=("VENTA USD", "sum"), MARGEN=("MARGEN USD", "sum"))
        .reset_index()
    )
    agg["Vta Prom Mes"] = agg["VENTA"] / n_meses
    agg["% Participación"] = agg["VENTA"] / total_vta if total_vta != 0 else 0
    agg["% Margen"] = agg.apply(lambda r: calc_margen_pct(r["VENTA"], r["MARGEN"]), axis=1)
    agg = agg.sort_values("VENTA", ascending=False)
    top10 = agg.head(10).reset_index(drop=True)
    top10.index = top10.index + 1
    bottom10 = agg.tail(10).sort_values("VENTA", ascending=True).reset_index(drop=True)
    bottom10.index = bottom10.index + 1
    return top10, bottom10

for year in sorted(dff["ANIO"].unique()):
    st.markdown(f"#### {int(year)}")
    top10, bottom10 = ranking_clientes(dff, year)

    tab_top, tab_bot = st.tabs(["Top 10", "Bottom 10"])
    with tab_top:
        t10 = top10[["CLIENTE", "Vta Prom Mes", "% Participación", "% Margen"]].copy()
        t10.columns = ["Cliente", "Vta Prom Mes", "% Partic.", "% Margen"]
        st.dataframe(
            t10.style.format({"Vta Prom Mes": "${:,.0f}", "% Partic.": "{:.2%}", "% Margen": "{:.2%}"})
            .bar(subset=["% Partic."], color="#bbf7d0", vmin=0),
            use_container_width=True,
            height=420,
        )
    with tab_bot:
        b10 = bottom10[["CLIENTE", "Vta Prom Mes", "% Participación", "% Margen"]].copy()
        b10.columns = ["Cliente", "Vta Prom Mes", "% Partic.", "% Margen"]
        st.dataframe(
            b10.style.format({"Vta Prom Mes": "${:,.0f}", "% Partic.": "{:.2%}", "% Margen": "{:.2%}"})
            .bar(subset=["% Partic."], color="#fecaca", vmin=0),
            use_container_width=True,
            height=420,
        )


# ═══════════════════════════════════════════════════════════════════════
# 4. PARTICIPACIÓN EN VENTAS — Categoría Línea y Línea
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Participación en Ventas — Sell In")

col_cat_pie, col_lin_bar = st.columns(2)

# Donut por Categoría Línea
with col_cat_pie:
    part_cat = (
        dff.groupby("CATEGORIA_LINEA")["VENTA USD"].sum()
        .reset_index()
        .sort_values("VENTA USD", ascending=False)
    )
    fig_part_cat = go.Figure(
        go.Pie(
            labels=part_cat["CATEGORIA_LINEA"],
            values=part_cat["VENTA USD"],
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=14),
            marker=dict(colors=["#2563EB", "#10B981", "#F59E0B", "#EF4444",
                                "#8B5CF6", "#EC4899", "#06B6D4", "#6B7280"]),
        )
    )
    fig_part_cat.update_layout(
        title=dict(text="Por Categoría Línea", font=dict(size=14)),
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
        showlegend=False,
    )
    st.plotly_chart(fig_part_cat, use_container_width=True)

# Barras horizontales por Línea (Top 15)
with col_lin_bar:
    part_lin = (
        dff.groupby("LINEA")["VENTA USD"].sum()
        .reset_index()
        .sort_values("VENTA USD", ascending=False)
        .head(10)
        .sort_values("VENTA USD", ascending=True)
    )
    total_vta_lin = dff["VENTA USD"].sum()
    part_lin["% Partic."] = part_lin["VENTA USD"] / total_vta_lin if total_vta_lin != 0 else 0

    fig_part_lin = go.Figure(
        go.Bar(
            y=part_lin["LINEA"],
            x=part_lin["% Partic."],
            orientation="h",
            marker_color="#2563EB",
            text=part_lin["% Partic."].apply(lambda v: f"{v:.1%}"),
            textposition="inside",
            textfont=dict(size=13, color="white"),
            insidetextanchor="end",
        )
    )
    fig_part_lin.update_layout(
        title=dict(text="Top 10 Líneas", font=dict(size=14)),
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(tickfont=dict(size=12)),
        plot_bgcolor="white",
    )
    fig_part_lin.update_yaxes(showgrid=False)
    st.plotly_chart(fig_part_lin, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# 5. EVOLUTIVO DE STOCK — Valorización mensual
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Evolutivo de Stock Sell In — Valorización USD")

# Filtrar stock por canal (coincidencia parcial en BODEGA NOMBRE)
_stock = df_stock.copy()
if len(canal_sel) < len(all_canales):
    _bodega_mask = _stock["BODEGA NOMBRE"].apply(
        lambda b: any(c.upper() in b.upper() for c in canal_sel)
    )
    _stock = _stock[_bodega_mask]

# Filtros internos de stock
_SABCT_ORDEN = ["S", "A", "B", "C", "T", "Nuevo", "Obsoleto", "Intangible"]

def _sort_sabct(vals):
    conocidos = [v for v in _SABCT_ORDEN if v in vals]
    otros = sorted(v for v in vals if v not in _SABCT_ORDEN)
    return conocidos + otros

_stk_cats = sorted(_stock["CATEGORIA_LINEA"].unique())
_stk_lins = sorted(_stock["LINEA"].unique())
_stk_subs = sorted(_stock["SUBCATEGORIA"].unique())
_stk_sabc = _sort_sabct(_stock["SABCT"].unique())

_fc1, _fc2, _fc3, _fc4 = st.columns(4)
with _fc1:
    _sel_cat_stk = st.multiselect("Categoría", _stk_cats, default=None, key="stk_cat",
                                   placeholder="Todas")
    if not _sel_cat_stk:
        _sel_cat_stk = list(_stk_cats)
with _fc2:
    _sel_lin_stk = st.multiselect("Línea", _stk_lins, default=None, key="stk_lin",
                                   placeholder="Todas")
    if not _sel_lin_stk:
        _sel_lin_stk = list(_stk_lins)
with _fc3:
    _sel_sub_stk = st.multiselect("Subcategoría", _stk_subs, default=None, key="stk_sub",
                                   placeholder="Todas")
    if not _sel_sub_stk:
        _sel_sub_stk = list(_stk_subs)
with _fc4:
    _sel_sabc_stk = st.multiselect("SABCT", _stk_sabc, default=None, key="stk_sabc",
                                    placeholder="Todos")
    if not _sel_sabc_stk:
        _sel_sabc_stk = list(_stk_sabc)

# Rango de días en almacén por rangos predefinidos
_DIAS_RANGOS = {
    "Menor a 30 Días": (0, 30),
    "31 a 90 Días": (31, 90),
    "91 a 180 Días": (91, 180),
    "181 a 360 Días": (181, 360),
    "361 a 720 Días": (361, 720),
    "721 Días a más": (721, 999999),
}
st.markdown("<span style='font-size:14px; color:#64748b;'>Días en Almacén</span>", unsafe_allow_html=True)
_fd_cols = st.columns(len(_DIAS_RANGOS) + 2)
with _fd_cols[0]:
    _dias_todos = st.checkbox("Todos", value=True, key="stk_dias_todos")
_dias_sel = []
if not _dias_todos:
    for i, (lbl, rng) in enumerate(_DIAS_RANGOS.items()):
        with _fd_cols[i + 1]:
            if st.checkbox(lbl, value=False, key=f"stk_dias_{rng[0]}"):
                _dias_sel.append(rng)
    if _dias_sel:
        _stock = _stock[
            _stock["DIAS EN ALMACEN"].isna()
            | _stock["DIAS EN ALMACEN"].apply(
                lambda d: any(lo <= d <= hi for lo, hi in _dias_sel)
            )
        ]
with _fd_cols[-1]:
    if st.button("Restablecer", key="stk_reset"):
        for k in list(st.session_state.keys()):
            if k.startswith("stk_"):
                del st.session_state[k]
        st.rerun()

if _sel_cat_stk:
    _stock = _stock[_stock["CATEGORIA_LINEA"].isin(_sel_cat_stk)]
if _sel_lin_stk:
    _stock = _stock[_stock["LINEA"].isin(_sel_lin_stk)]
if _sel_sub_stk:
    _stock = _stock[_stock["SUBCATEGORIA"].isin(_sel_sub_stk)]
if _sel_sabc_stk:
    _stock = _stock[_stock["SABCT"].isin(_sel_sabc_stk)]

_stock_evo = (
    _stock.groupby(["ANIO", "MES_NUM"])
    .agg(STOCK_USD=("STOCK COSTO USD", "sum"), UNIDADES=("UNIDADES", "sum"))
    .reset_index()
    .sort_values(["ANIO", "MES_NUM"])
)
_stock_evo["MES_LABEL"] = _stock_evo.apply(
    lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
)

# Detalle por SABCT para hover
_stock_sabct = (
    _stock.groupby(["ANIO", "MES_NUM", "SABCT"])
    .agg(S_USD=("STOCK COSTO USD", "sum"))
    .reset_index()
)
_hover_texts = []
for _, row in _stock_evo.iterrows():
    _det = _stock_sabct[
        (_stock_sabct["ANIO"] == row["ANIO"]) & (_stock_sabct["MES_NUM"] == row["MES_NUM"])
    ].copy()
    _det["_ord"] = _det["SABCT"].apply(lambda s: _SABCT_ORDEN.index(s) if s in _SABCT_ORDEN else len(_SABCT_ORDEN))
    _det = _det.sort_values("_ord")
    _total = row["STOCK_USD"]
    _lines = [f"<b>{row['MES_LABEL']}</b>", f"<b>Total: {fmt_k(_total)}</b>", ""]
    for _, d in _det.iterrows():
        _pct = d["S_USD"] / _total * 100 if _total != 0 else 0
        _lines.append(f"{d['SABCT']}: {fmt_k(d['S_USD'])} ({_pct:.1f}%)")
    _hover_texts.append("<br>".join(_lines))

fig_stock = go.Figure()
fig_stock.add_trace(
    go.Bar(
        x=_stock_evo["MES_LABEL"],
        y=_stock_evo["STOCK_USD"],
        marker_color="#0EA5E9",
        text=_stock_evo["STOCK_USD"].apply(fmt_k),
        textposition="outside",
        textfont=dict(size=13, color="#0C4A6E"),
        cliponaxis=False,
        name="Stock USD",
        hovertext=_hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
    )
)

_stock_max = _stock_evo["STOCK_USD"].max() if not _stock_evo.empty else 1
fig_stock.update_layout(
    height=420,
    margin=dict(t=50, b=40),
    plot_bgcolor="white",
    bargap=0.3,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
fig_stock.update_yaxes(showticklabels=False, showgrid=False, title="", range=[0, _stock_max * 1.4])
fig_stock.update_xaxes(showgrid=False)
st.plotly_chart(fig_stock, use_container_width=True)

# ── Stock Sell Out por Sub-Categoría (solo RETAIL) ──
if canal_sel == ["RETAIL"]:
    st.subheader("Stock Sell Out Retail — Top 10 Sub-Categorías por Retailer (USD)")

    _TC_SO = 3.40
    _stk_so = df_stock_so.copy()
    _stk_so["STOCK_USD"] = _stk_so["Stock valorizado"] / _TC_SO

    _so_col_sod, _so_col_pro = st.columns(2)

    for _ret, _col, _color in [("SODIMAC", _so_col_sod, "#2563EB"), ("PROMART", _so_col_pro, "#10B981")]:
        _stk_ret = _stk_so[_stk_so["Retailer"] == _ret]
        _stk_ret_agg = (
            _stk_ret.groupby("SUB-Categor\u00eda_2")
            .agg(STOCK_USD=("STOCK_USD", "sum"), UNIDADES=("Stock Unidades", "sum"))
            .reset_index()
            .sort_values("STOCK_USD", ascending=False)
            .head(10)
            .sort_values("STOCK_USD", ascending=True)
        )

        fig_ret = go.Figure(
            go.Bar(
                y=_stk_ret_agg["SUB-Categor\u00eda_2"],
                x=_stk_ret_agg["STOCK_USD"],
                orientation="h",
                marker_color=_color,
                text=_stk_ret_agg["STOCK_USD"].apply(fmt_k),
                textposition="outside",
                textfont=dict(size=11, color=_color),
                cliponaxis=False,
                customdata=_stk_ret_agg["UNIDADES"],
                hovertemplate="<b>%{y}</b><br>Stock: %{text}<br>Unidades: %{customdata:,.0f}<extra></extra>",
            )
        )

        _ret_max = _stk_ret_agg["STOCK_USD"].max() if not _stk_ret_agg.empty else 1
        fig_ret.update_layout(
            title=dict(text=_ret, font=dict(size=14)),
            height=420,
            margin=dict(t=40, b=30, l=180, r=60),
            plot_bgcolor="white",
            xaxis=dict(showticklabels=False, showgrid=False, range=[0, _ret_max * 1.4]),
            yaxis=dict(tickfont=dict(size=11)),
        )
        fig_ret.update_yaxes(showgrid=False)
        with _col:
            st.plotly_chart(fig_ret, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# 6. ANÁLISIS DE PUNTOS CLAVE — Insights de Negocio
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Análisis de Puntos Clave — Sell In")

# ── Cálculos base ────────────────────────────────────────────────────
_vta25 = dff_2025["VENTA USD"].sum()
_vta26 = dff_2026["VENTA USD"].sum()
_mar25 = dff_2025["MARGEN USD"].sum()
_mar26 = dff_2026["MARGEN USD"].sum()
_pct25 = calc_margen_pct(_vta25, _mar25)
_pct26 = calc_margen_pct(_vta26, _mar26)
_n25 = dff_2025["MES_NUM"].nunique() or 1
_n26 = dff_2026["MES_NUM"].nunique() or 1
_prom25 = _vta25 / _n25
_prom26 = _vta26 / _n26
_yoy = ((_prom26 / _prom25) - 1) if _prom25 != 0 else 0

# Concentración de clientes (Top 5 vs total)
_cli_vta = dff.groupby("CLIENTE")["VENTA USD"].sum().sort_values(ascending=False)
_top5_share = _cli_vta.head(5).sum() / _cli_vta.sum() if _cli_vta.sum() != 0 else 0
_top10_share = _cli_vta.head(10).sum() / _cli_vta.sum() if _cli_vta.sum() != 0 else 0
_n_clientes = len(_cli_vta[_cli_vta > 0])

# Categoría más rentable
_cat_agg = (
    dff.groupby("CATEGORIA_LINEA")
    .agg(V=("VENTA USD", "sum"), M=("MARGEN USD", "sum"))
    .reset_index()
)
_cat_agg["pct"] = _cat_agg.apply(lambda r: calc_margen_pct(r["V"], r["M"]), axis=1)
_cat_total_v = _cat_agg["V"].sum()
_cat_agg_sig = _cat_agg[_cat_agg["V"] >= _cat_total_v * 0.01] if _cat_total_v > 0 else _cat_agg
_cat_agg_sig = _cat_agg_sig.sort_values("pct", ascending=False)
_cat_agg = _cat_agg.sort_values("pct", ascending=False)
_best_cat = _cat_agg_sig.iloc[0] if not _cat_agg_sig.empty else None
_worst_cat = _cat_agg.iloc[-1] if not _cat_agg.empty else None

# Canal más fuerte
_canal_agg = (
    dff.groupby("CANAL")
    .agg(V=("VENTA USD", "sum"), M=("MARGEN USD", "sum"))
    .reset_index()
)
_canal_agg["pct"] = _canal_agg.apply(lambda r: calc_margen_pct(r["V"], r["M"]), axis=1)
_canal_top = _canal_agg.sort_values("V", ascending=False).iloc[0] if not _canal_agg.empty else None
_canal_best_margin = _canal_agg.sort_values("pct", ascending=False).iloc[0] if not _canal_agg.empty else None

# Mejor y peor mes (venta promedio mensual normalizada)
_mes_agg = (
    dff.groupby(["ANIO", "MES_NUM"])
    .agg(V=("VENTA USD", "sum"))
    .reset_index()
    .sort_values("V", ascending=False)
)
_best_month = _mes_agg.iloc[0] if not _mes_agg.empty else None
_worst_month = _mes_agg.iloc[-1] if not _mes_agg.empty else None

# Variación margen YoY
_margen_delta = _pct26 - _pct25

# ── Renderizado ──────────────────────────────────────────────────────
def _insight_card(icon, title, value, detail, color="#1E3A5F"):
    st.markdown(
        f"""<div style="background:#f8fafc; border-left:4px solid {color};
        padding:12px 16px; margin-bottom:10px; border-radius:0 8px 8px 0;">
        <span style="font-size:14px; color:#64748b;">{icon} {title}</span><br>
        <span style="font-size:22px; font-weight:700; color:{color};">{value}</span><br>
        <span style="font-size:13px; color:#475569;">{detail}</span>
        </div>""",
        unsafe_allow_html=True,
    )

ins_c1, ins_c2 = st.columns(2)

with ins_c1:
    # 1. Crecimiento YoY
    _yoy_color = "#10B981" if _yoy >= 0 else "#EF4444"
    _yoy_icon = "▲" if _yoy >= 0 else "▼"
    _insight_card(
        _yoy_icon, "Crecimiento YoY (Vta Prom Mes)",
        f"{_yoy:+.1%}",
        f"2025: {fmt_k(_prom25)}/mes ({_n25} meses) → 2026: {fmt_k(_prom26)}/mes ({_n26} meses)",
        _yoy_color,
    )

    # 2. Variación de margen
    _md_color = "#10B981" if _margen_delta >= 0 else "#EF4444"
    _md_icon = "▲" if _margen_delta >= 0 else "▼"
    _insight_card(
        _md_icon, "Variación de Margen YoY",
        f"{_margen_delta:+.1%} pp",
        f"2025: {_pct25:.1%} → 2026: {_pct26:.1%}. {'Mejora en rentabilidad.' if _margen_delta >= 0 else 'Alerta: margen en contracción.'}",
        _md_color,
    )

    # 3. Mejor mes
    if _best_month is not None:
        _bm_lbl = f"{MESES_ESP[int(_best_month['MES_NUM'])]} {int(_best_month['ANIO'])}"
        _insight_card(
            "★", "Mejor Mes",
            f"{_bm_lbl} — {fmt_k(_best_month['V'])}",
            "Mayor facturación registrada en el período seleccionado.",
            "#2563EB",
        )

    # 4. Categoría más rentable
    if _best_cat is not None:
        _insight_card(
            "◆", "Categoría Más Rentable",
            f"{_best_cat['CATEGORIA_LINEA']} — {_best_cat['pct']:.1%}",
            f"Sobre una venta de {fmt_k(_best_cat['V'])}.",
            "#10B981",
        )

with ins_c2:
    # 5. Concentración de clientes
    _conc_color = "#EF4444" if _top5_share > 0.5 else "#F59E0B" if _top5_share > 0.3 else "#10B981"
    _conc_msg = "Alta concentración: riesgo de dependencia." if _top5_share > 0.5 else "Concentración moderada." if _top5_share > 0.3 else "Cartera diversificada."
    _insight_card(
        "⊕", "Concentración Top 5 Clientes",
        f"{_top5_share:.1%} de la venta total",
        f"Top 10 = {_top10_share:.1%}. {_n_clientes} clientes activos. {_conc_msg}",
        _conc_color,
    )

    # 6. Canal líder
    if _canal_top is not None:
        _canal_share = _canal_top["V"] / dff["VENTA USD"].sum() if dff["VENTA USD"].sum() != 0 else 0
        _insight_card(
            "◈", "Canal Líder en Volumen",
            f"{_canal_top.name if isinstance(_canal_top.name, str) else _canal_top['CANAL']} — {_canal_share:.1%}",
            f"Venta: {fmt_k(_canal_top['V'])}. Margen: {_canal_top['pct']:.1%}.",
            "#2563EB",
        )

    # 7. Canal con mejor margen
    if _canal_best_margin is not None and _canal_top is not None:
        if _canal_best_margin["CANAL"] != _canal_top["CANAL"]:
            _insight_card(
                "◈", "Canal Más Rentable",
                f"{_canal_best_margin['CANAL']} — {_canal_best_margin['pct']:.1%}",
                f"Venta: {fmt_k(_canal_best_margin['V'])}. Oportunidad de crecimiento en canal rentable.",
                "#8B5CF6",
            )

    # 8. Peor mes / alerta
    if _worst_month is not None:
        _wm_lbl = f"{MESES_ESP[int(_worst_month['MES_NUM'])]} {int(_worst_month['ANIO'])}"
        _insight_card(
            "▾", "Mes Más Bajo",
            f"{_wm_lbl} — {fmt_k(_worst_month['V'])}",
            "Mes con menor facturación. Revisar estacionalidad o factores externos.",
            "#EF4444",
        )

    # 9. Categoría menos rentable
    if _worst_cat is not None and _worst_cat["CATEGORIA_LINEA"] != (_best_cat["CATEGORIA_LINEA"] if _best_cat is not None else ""):
        _insight_card(
            "▾", "Categoría Menos Rentable",
            f"{_worst_cat['CATEGORIA_LINEA']} — {_worst_cat['pct']:.1%}",
            f"Sobre una venta de {fmt_k(_worst_cat['V'])}. Evaluar pricing o mix de productos.",
            "#EF4444",
        )


# ═══════════════════════════════════════════════════════════════════════
# 7. SELL OUT RETAIL (solo cuando canal = RETAIL)
# ═══════════════════════════════════════════════════════════════════════
if canal_sel == ["RETAIL"]:
    st.markdown("---")
    st.subheader("Evolutivo Mensual — Sell Out Retail (USD)")

    _TC_PEN_USD = 3.40

    # Construir eje X ordenado (único para barras y línea)
    _so_meses_orden = (
        df_sellout[["ANIO", "MES_NUM"]].drop_duplicates()
        .sort_values(["ANIO", "MES_NUM"])
    )
    _so_x_labels = [
        f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}"
        for _, r in _so_meses_orden.iterrows()
    ]

    # Agrupar por Retailer y mes
    evo_so_ret = (
        df_sellout.groupby(["Retailer", "ANIO", "MES_NUM"])
        .agg(VENTA=("Venta neta", "sum"), UNIDADES=("Unidades vendidas", "sum"))
        .reset_index()
        .sort_values(["ANIO", "MES_NUM"])
    )
    evo_so_ret["VENTA"] = evo_so_ret["VENTA"] / _TC_PEN_USD
    evo_so_ret["MES_LABEL"] = evo_so_ret.apply(
        lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
    )

    # Total de unidades por mes para la línea
    evo_so_uds = (
        df_sellout.groupby(["ANIO", "MES_NUM"])
        .agg(UNIDADES=("Unidades vendidas", "sum"))
        .reset_index()
        .sort_values(["ANIO", "MES_NUM"])
    )
    evo_so_uds["MES_LABEL"] = evo_so_uds.apply(
        lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
    )

    # Total por mes para anotaciones
    _so_totales = (
        evo_so_ret.groupby("MES_LABEL")["VENTA"].sum()
        .reindex(_so_x_labels)
        .fillna(0)
    )

    # Máximo por barra individual (para posicionar el total encima)
    _so_max_bar = (
        evo_so_ret.groupby("MES_LABEL")["VENTA"].max()
        .reindex(_so_x_labels)
        .fillna(0)
    )

    fig_so = go.Figure()

    for _ret, _color in [("SODIMAC", "#2563EB"), ("PROMART", "#10B981")]:
        _ret_data = evo_so_ret[evo_so_ret["Retailer"] == _ret]
        fig_so.add_trace(
            go.Bar(
                x=_ret_data["MES_LABEL"],
                y=_ret_data["VENTA"],
                name=_ret,
                marker_color=_color,
                text=_ret_data["VENTA"].apply(fmt_k),
                textposition="outside",
                textfont=dict(size=16, color=_color, family="Inter, sans-serif"),
                cliponaxis=False,
            ),
        )

    _so_venta_max = _so_totales.max() if not _so_totales.empty else 1

    # Anotaciones con el total mensual centrado encima de cada grupo de barras
    _so_annotations = []
    for _lbl in _so_x_labels:
        _total_val = _so_totales.get(_lbl, 0)
        _max_bar_val = _so_max_bar.get(_lbl, 0)
        if _total_val > 0:
            _so_annotations.append(dict(
                x=_lbl,
                y=_max_bar_val * 1.45,
                text=f"<b>{fmt_k(_total_val)}</b>",
                showarrow=False,
                font=dict(size=12, color="#64748b", family="Inter, sans-serif"),
                xanchor="center",
                yanchor="bottom",
            ))

    fig_so.update_layout(
        height=500,
        margin=dict(t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.05,
        plot_bgcolor="white",
        annotations=_so_annotations,
    )
    fig_so.update_yaxes(showticklabels=False, title="", showgrid=False,
                        range=[0, _so_venta_max * 2.0])
    fig_so.update_xaxes(showgrid=False, categoryorder="array", categoryarray=_so_x_labels)

    st.plotly_chart(fig_so, use_container_width=True)

    # ── Ticket Promedio Sell Out Retail ──
    st.subheader("Evolutivo Mensual — Ticket Promedio Sell Out Retail (USD)")

    evo_so_ticket = (
        df_sellout.groupby(["ANIO", "MES_NUM"])
        .agg(PVP_PROM=("PVP", "mean"))
        .reset_index()
        .sort_values(["ANIO", "MES_NUM"])
    )
    evo_so_ticket["PVP_USD"] = evo_so_ticket["PVP_PROM"] / _TC_PEN_USD
    evo_so_ticket["MES_LABEL"] = evo_so_ticket.apply(
        lambda r: f"{MESES_ESP[int(r['MES_NUM'])]} {int(r['ANIO'])}", axis=1
    )

    fig_so_ticket = go.Figure()
    fig_so_ticket.add_trace(
        go.Scatter(
            x=evo_so_ticket["MES_LABEL"],
            y=evo_so_ticket["PVP_USD"],
            mode="lines+markers+text",
            line=dict(color="#8B5CF6", width=3, shape="spline", smoothing=0.8),
            marker=dict(size=8, color="#8B5CF6"),
            text=evo_so_ticket["PVP_USD"].apply(lambda v: f"${v:,.1f}"),
            textposition="top center",
            textfont=dict(size=16, color="#5B21B6"),
            cliponaxis=False,
            name="Ticket Promedio",
        )
    )

    fig_so_ticket.update_layout(
        height=400,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
    )
    fig_so_ticket.update_yaxes(showticklabels=False, showgrid=False, title="")
    fig_so_ticket.update_xaxes(showgrid=False)
    st.plotly_chart(fig_so_ticket, use_container_width=True)

    # ── Top 10 y Bottom 10 Tiendas Sell Out Retail ──
    st.markdown("---")
    st.subheader("Top 10 y Bottom 10 Tiendas — Sell Out Retail")

    def ranking_tiendas_retail(data, year):
        data_year = data[data["ANIO"] == year]
        n_meses = data_year["MES_NUM"].nunique()
        n_meses = n_meses if n_meses > 0 else 1
        total_vta = data_year["Venta neta"].sum()
        agg = (
            data_year.groupby("Descripción de Tienda")
            .agg(VENTA=("Venta neta", "sum"), UNIDADES=("Unidades vendidas", "sum"))
            .reset_index()
        )
        agg["VENTA_USD"] = agg["VENTA"] / _TC_PEN_USD
        agg["Vta Prom Mes"] = agg["VENTA_USD"] / n_meses
        agg["% Participación"] = agg["VENTA"] / total_vta if total_vta != 0 else 0
        agg["Uds Totales"] = agg["UNIDADES"]
        agg = agg.sort_values("VENTA_USD", ascending=False)
        top10 = agg.head(10).reset_index(drop=True)
        top10.index = top10.index + 1
        bottom10 = agg[agg["VENTA_USD"] > 0].tail(10).sort_values("VENTA_USD", ascending=True).reset_index(drop=True)
        bottom10.index = bottom10.index + 1
        return top10, bottom10

    for year in sorted(df_sellout["ANIO"].unique()):
        st.markdown(f"#### {int(year)}")
        so_top10, so_bot10 = ranking_tiendas_retail(df_sellout, year)

        so_tab_top, so_tab_bot = st.tabs(["Top 10", "Bottom 10"])
        with so_tab_top:
            st10 = so_top10[["Descripción de Tienda", "Vta Prom Mes", "% Participación", "Uds Totales"]].copy()
            st10.columns = ["Tienda", "Vta Prom Mes", "% Partic.", "Uds Totales"]
            st.dataframe(
                st10.style.format({"Vta Prom Mes": "${:,.0f}", "% Partic.": "{:.2%}", "Uds Totales": "{:,.0f}"})
                .bar(subset=["% Partic."], color="#bbf7d0", vmin=0),
                use_container_width=True,
                height=420,
            )
        with so_tab_bot:
            sb10 = so_bot10[["Descripción de Tienda", "Vta Prom Mes", "% Participación", "Uds Totales"]].copy()
            sb10.columns = ["Tienda", "Vta Prom Mes", "% Partic.", "Uds Totales"]
            st.dataframe(
                sb10.style.format({"Vta Prom Mes": "${:,.0f}", "% Partic.": "{:.2%}", "Uds Totales": "{:,.0f}"})
                .bar(subset=["% Partic."], color="#fecaca", vmin=0),
                use_container_width=True,
                height=420,
            )

    # ── Análisis de Puntos Clave — Sell Out ──
    st.markdown("---")
    st.subheader("Análisis de Puntos Clave — Sell Out Retail")

    _so_25 = df_sellout[df_sellout["ANIO"] == 2025]
    _so_26 = df_sellout[df_sellout["ANIO"] == 2026]
    _so_vta25 = _so_25["Venta neta"].sum() / _TC_PEN_USD
    _so_vta26 = _so_26["Venta neta"].sum() / _TC_PEN_USD
    _so_uds25 = _so_25["Unidades vendidas"].sum()
    _so_uds26 = _so_26["Unidades vendidas"].sum()
    _so_n25 = _so_25["MES_NUM"].nunique() or 1
    _so_n26 = _so_26["MES_NUM"].nunique() or 1
    _so_prom25 = _so_vta25 / _so_n25
    _so_prom26 = _so_vta26 / _so_n26
    _so_yoy = ((_so_prom26 / _so_prom25) - 1) if _so_prom25 != 0 else 0

    # Concentración tiendas (Top 5 vs total)
    _so_tienda_vta = df_sellout.groupby("Descripción de Tienda")["Venta neta"].sum().sort_values(ascending=False)
    _so_total_vta = _so_tienda_vta.sum()
    _so_top5_share = _so_tienda_vta.head(5).sum() / _so_total_vta if _so_total_vta != 0 else 0
    _so_top10_share = _so_tienda_vta.head(10).sum() / _so_total_vta if _so_total_vta != 0 else 0
    _so_n_tiendas = len(_so_tienda_vta[_so_tienda_vta > 0])

    # Categoría con más venta
    _so_cat_agg = (
        df_sellout.groupby("CATEGORIA_LINEA")
        .agg(V=("Venta neta", "sum"), U=("Unidades vendidas", "sum"))
        .reset_index()
    )
    _so_cat_agg["V_USD"] = _so_cat_agg["V"] / _TC_PEN_USD
    _so_cat_agg = _so_cat_agg.sort_values("V_USD", ascending=False)
    _so_best_cat = _so_cat_agg.iloc[0] if not _so_cat_agg.empty else None
    _so_worst_cat = _so_cat_agg.iloc[-1] if not _so_cat_agg.empty else None

    # Retailer con más venta
    _so_ret_agg = df_sellout.groupby("Retailer")["Venta neta"].sum().sort_values(ascending=False)
    _so_ret_top = _so_ret_agg.index[0] if not _so_ret_agg.empty else None
    _so_ret_top_share = _so_ret_agg.iloc[0] / _so_ret_agg.sum() if _so_ret_agg.sum() != 0 else 0

    # Mejor y peor mes
    _so_mes_agg = (
        df_sellout.groupby(["ANIO", "MES_NUM"])
        .agg(V=("Venta neta", "sum"))
        .reset_index()
    )
    _so_mes_agg["V_USD"] = _so_mes_agg["V"] / _TC_PEN_USD
    _so_mes_agg = _so_mes_agg.sort_values("V_USD", ascending=False)
    _so_best_m = _so_mes_agg.iloc[0] if not _so_mes_agg.empty else None
    _so_worst_m = _so_mes_agg.iloc[-1] if not _so_mes_agg.empty else None

    # Ticket promedio YoY
    _so_ticket25 = (_so_25["PVP"].mean() / _TC_PEN_USD) if len(_so_25) > 0 else 0
    _so_ticket26 = (_so_26["PVP"].mean() / _TC_PEN_USD) if len(_so_26) > 0 else 0
    _so_ticket_delta = _so_ticket26 - _so_ticket25

    # Renderizado
    _so_c1, _so_c2 = st.columns(2)

    with _so_c1:
        # 1. Crecimiento YoY
        _so_yoy_color = "#10B981" if _so_yoy >= 0 else "#EF4444"
        _so_yoy_icon = "▲" if _so_yoy >= 0 else "▼"
        _insight_card(
            _so_yoy_icon, "Crecimiento YoY (Vta Prom Mes)",
            f"{_so_yoy:+.1%}",
            f"2025: {fmt_k(_so_prom25)}/mes ({_so_n25} meses) → 2026: {fmt_k(_so_prom26)}/mes ({_so_n26} meses)",
            _so_yoy_color,
        )

        # 2. Variación Ticket Promedio
        _so_td_color = "#10B981" if _so_ticket_delta >= 0 else "#EF4444"
        _so_td_icon = "▲" if _so_ticket_delta >= 0 else "▼"
        _insight_card(
            _so_td_icon, "Variación Ticket Promedio YoY",
            f"{_so_ticket_delta:+.1f} USD",
            f"2025: ${_so_ticket25:.1f} → 2026: ${_so_ticket26:.1f}. {'Mejora en precio promedio.' if _so_ticket_delta >= 0 else 'Precio promedio en descenso.'}",
            _so_td_color,
        )

        # 3. Mejor mes
        if _so_best_m is not None:
            _so_bm_lbl = f"{MESES_ESP[int(_so_best_m['MES_NUM'])]} {int(_so_best_m['ANIO'])}"
            _insight_card(
                "★", "Mejor Mes",
                f"{_so_bm_lbl} — {fmt_k(_so_best_m['V_USD'])}",
                "Mayor venta sell out registrada en el período.",
                "#2563EB",
            )

        # 4. Categoría líder
        if _so_best_cat is not None:
            _so_bc_share = _so_best_cat["V_USD"] / (_so_cat_agg["V_USD"].sum()) if _so_cat_agg["V_USD"].sum() != 0 else 0
            _insight_card(
                "◆", "Categoría Líder",
                f"{_so_best_cat['CATEGORIA_LINEA']} — {_so_bc_share:.1%}",
                f"Venta: {fmt_k(_so_best_cat['V_USD'])}. Uds: {_so_best_cat['U']:,.0f}.",
                "#10B981",
            )

    with _so_c2:
        # 5. Concentración tiendas
        _so_conc_color = "#EF4444" if _so_top5_share > 0.5 else "#F59E0B" if _so_top5_share > 0.3 else "#10B981"
        _so_conc_msg = "Alta concentración: riesgo de dependencia." if _so_top5_share > 0.5 else "Concentración moderada." if _so_top5_share > 0.3 else "Cartera diversificada."
        _insight_card(
            "⊕", "Concentración Top 5 Tiendas",
            f"{_so_top5_share:.1%} de la venta total",
            f"Top 10 = {_so_top10_share:.1%}. {_so_n_tiendas} tiendas activas. {_so_conc_msg}",
            _so_conc_color,
        )

        # 6. Retailer líder
        if _so_ret_top is not None:
            _insight_card(
                "◈", "Retailer Líder",
                f"{_so_ret_top} — {_so_ret_top_share:.1%}",
                f"Venta: {fmt_k(_so_ret_agg.iloc[0] / _TC_PEN_USD)}.",
                "#2563EB",
            )

        # 7. Peor mes
        if _so_worst_m is not None:
            _so_wm_lbl = f"{MESES_ESP[int(_so_worst_m['MES_NUM'])]} {int(_so_worst_m['ANIO'])}"
            _insight_card(
                "▾", "Mes Más Bajo",
                f"{_so_wm_lbl} — {fmt_k(_so_worst_m['V_USD'])}",
                "Mes con menor venta sell out. Revisar estacionalidad o abastecimiento.",
                "#EF4444",
            )

        # 8. Categoría con menor venta
        if _so_worst_cat is not None and _so_worst_cat["CATEGORIA_LINEA"] != (_so_best_cat["CATEGORIA_LINEA"] if _so_best_cat is not None else ""):
            _so_wc_share = _so_worst_cat["V_USD"] / (_so_cat_agg["V_USD"].sum()) if _so_cat_agg["V_USD"].sum() != 0 else 0
            _insight_card(
                "▾", "Categoría con Menor Venta",
                f"{_so_worst_cat['CATEGORIA_LINEA']} — {_so_wc_share:.1%}",
                f"Venta: {fmt_k(_so_worst_cat['V_USD'])}. Evaluar surtido o visibilidad en tienda.",
                "#EF4444",
            )

