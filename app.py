import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import time
import sqlite3
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Churn Guard", page_icon="📡", layout="wide")

# ── PALETTE ───────────────────────────────────────────────────────────────────
TEAL_LIGHT  = "#78B9B5"
TEAL_MID    = "#0F828C"
BLUE_DEEP   = "#065084"
PURPLE_DEEP = "#320A6B"

# ── THEME STATE ───────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

if dark:
    BG        = "#060d1a"
    SURFACE   = "#0b1628"
    SURFACE2  = "#101e35"
    TEXT      = "#e8f4f4"
    MUTED     = "rgba(120,185,181,0.55)"
    CARD_BG   = "linear-gradient(135deg, rgba(15,130,140,0.12), rgba(6,80,132,0.10))"
    CARD_BOR  = "rgba(120,185,181,0.18)"
    PLY_TPL   = "plotly_dark"
    PLY_BG    = "rgba(11,22,40,0.6)"
    SIDEBAR   = f"linear-gradient(180deg, {PURPLE_DEEP} 0%, #1a0740 60%, #0a0520 100%)"
    TITLE_C   = f"{TEAL_LIGHT}, {TEAL_MID}, {BLUE_DEEP}"
    INPUT_BG  = "#101e35"
    HR_COL    = "rgba(120,185,181,0.12)"
    BODY_TXT  = "#c4dedd"
    # ── Chart-specific colors (dark) ──
    CHART_FONT     = TEAL_LIGHT          # axis labels, tick text
    CHART_TITLE    = TEAL_LIGHT
    CHART_GRID     = "rgba(120,185,181,0.12)"
    CHART_AXIS_LINE= TEAL_LIGHT
    CHART_TICK     = TEAL_LIGHT
    CHART_LEGEND   = TEAL_LIGHT
else:
    BG        = "#f0f8f9"
    SURFACE   = "#ffffff"
    SURFACE2  = "#e2f0f1"
    TEXT      = "#0d2b30"
    MUTED     = "#2a6b72"
    CARD_BG   = "linear-gradient(135deg, rgba(15,130,140,0.10), rgba(6,80,132,0.07))"
    CARD_BOR  = "rgba(6,80,132,0.30)"
    PLY_TPL   = "plotly_white"
    PLY_BG    = "rgba(240,247,248,0.8)"
    SIDEBAR   = f"linear-gradient(180deg, {BLUE_DEEP} 0%, {TEAL_MID} 60%, #0a9ea8 100%)"
    TITLE_C   = f"{BLUE_DEEP}, {TEAL_MID}, #0a9ea8"
    INPUT_BG  = "#ffffff"
    HR_COL    = "rgba(6,80,132,0.18)"
    BODY_TXT  = "#0a3d42"
    # ── Chart-specific colors (light) ──
    CHART_FONT     = "#0d2b30"           # dark text on white charts
    CHART_TITLE    = BLUE_DEEP
    CHART_GRID     = "rgba(6,80,132,0.12)"
    CHART_AXIS_LINE= BLUE_DEEP
    CHART_TICK     = "#0d2b30"
    CHART_LEGEND   = "#0d2b30"

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600;800&family=Space+Mono&display=swap)');

:root {{
  --teal-light:  {TEAL_LIGHT};
  --teal-mid:    {TEAL_MID};
  --blue-deep:   {BLUE_DEEP};
  --purple-deep: {PURPLE_DEEP};
}}

html, body, .stApp {{
  background: {BG} !important;
  color: {TEXT} !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: background 0.3s ease, color 0.3s ease;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: {SIDEBAR} !important;
  border-right: 1px solid {CARD_BOR} !important;
}}
section[data-testid="stSidebar"] * {{
  color: #ffffff !important;
  font-family: 'DM Sans', sans-serif !important;
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stSelectbox label {{
  color: #ffffff !important;
  font-weight: 600 !important;
  font-size: 13px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div {{
  color: {'#0d2b30' if not dark else '#e8f4f4'} !important;
}}
section[data-testid="stSidebar"] .stSlider > div > div > div > div {{
  background: {TEAL_MID} !important;
}}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
  background: {TEAL_LIGHT} !important;
  border: 2px solid {TEAL_MID} !important;
  box-shadow: 0 0 10px {TEAL_MID}80 !important;
}}
/* Slider value bubble in sidebar */
section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {{
  color: rgba(255,255,255,0.75) !important;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
  font-family: 'DM Sans', sans-serif !important;
  color: {'#78B9B5' if dark else '#065084'} !important;
}}

/* ── Cards ── */
.churn-card {{
  background: {CARD_BG};
  border: 1px solid {CARD_BOR};
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 32px rgba(50,10,107,0.15);
}}

/* ── Hero ── */
.hero-title {{
  font-size: 52px;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(135deg, {TITLE_C});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
  line-height: 1.1;
  margin-bottom: 8px;
}}
.hero-sub {{
  text-align: center;
  color: {MUTED};
  font-size: 17px;
  letter-spacing: 0.5px;
  margin-bottom: 36px;
}}

/* ── Labels ── */
.section-label {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: {TEAL_MID};
  margin-bottom: 4px;
}}

/* Main area form labels — force visibility in both modes */
.stSlider label,
.stSelectbox label,
.stNumberInput label,
.stFileUploader label,
.stTextInput label {{
  color: {TEXT} !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}}

/* Selectbox selected value text */
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-baseweb="select"] span {{
  color: {TEXT} !important;
}}

/* Number input text */
[data-testid="stNumberInput"] input {{
  background: {INPUT_BG} !important;
  border-color: {CARD_BOR} !important;
  color: {TEXT} !important;
  border-radius: 8px !important;
  font-size: 14px !important;
}}

/* ── Top-5 badge ── */
.top5-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, rgba(15,130,140,0.18), rgba(6,80,132,0.14));
  border: 1px solid {TEAL_MID};
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: {'#78B9B5' if dark else '#065084'};
  margin-bottom: 14px;
}}

/* ── Rank pills ── */
.rank-pill {{
  display: inline-block;
  background: linear-gradient(135deg, {TEAL_MID}, {BLUE_DEEP});
  color: white;
  font-size: 10px;
  font-weight: 800;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  margin-right: 6px;
}}

/* ── Risk badges ── */
.risk-badge-high {{
  background: linear-gradient(135deg, #7f1d1d, #991b1b);
  border: 1px solid #f87171;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #fecaca;
  text-align: center;
}}
.risk-badge-med {{
  background: linear-gradient(135deg, #78350f, #92400e);
  border: 1px solid #fbbf24;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #fde68a;
  text-align: center;
}}
.risk-badge-low {{
  background: linear-gradient(135deg, #064e3b, #065f46);
  border: 1px solid #34d399;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #a7f3d0;
  text-align: center;
}}

/* ── KPI cards ── */
.kpi-card {{
  background: {CARD_BG};
  border: 1px solid {CARD_BOR};
  border-radius: 14px;
  padding: 20px 16px;
  text-align: center;
  transition: transform 0.2s ease;
}}
.kpi-card:hover {{ transform: translateY(-2px); }}
.kpi-number {{
  font-size: 32px;
  font-weight: 800;
  color: {'#78B9B5' if dark else '#065084'};
  line-height: 1.1;
}}
.kpi-label {{
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: {MUTED};
  margin-top: 4px;
}}

.divider {{
  border: none;
  border-top: 1px solid {HR_COL};
  margin: 28px 0;
}}

/* ── All general buttons ── */
.stButton > button {{
  background: linear-gradient(135deg, {TEAL_MID}, {BLUE_DEEP}) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 10px 28px !important;
  letter-spacing: 0.3px !important;
  box-shadow: 0 4px 20px rgba(15,130,140,0.35) !important;
  transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
  box-shadow: 0 6px 28px rgba(120,185,181,0.45) !important;
  transform: translateY(-1px) !important;
}}

/* ── PREDICT button (primary CTA) ── */
div[data-testid="stButton"]:has(button[kind="primary"]) > button {{
  background: linear-gradient(135deg, #f97316, #ef4444, #dc2626) !important;
  color: #ffffff !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  padding: 18px 56px !important;
  border-radius: 14px !important;
  border: 2px solid rgba(255,180,100,0.55) !important;
  box-shadow:
    0 0 0 4px rgba(249,115,22,0.18),
    0 8px 40px rgba(239,68,68,0.55),
    0 2px 8px rgba(0,0,0,0.4) !important;
  letter-spacing: 0.8px !important;
  text-transform: uppercase !important;
  animation: predict-pulse 2.4s ease-in-out infinite !important;
  width: 100% !important;
  transition: all 0.18s ease !important;
}}
div[data-testid="stButton"]:has(button[kind="primary"]) > button:hover {{
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow:
    0 0 0 6px rgba(249,115,22,0.25),
    0 16px 56px rgba(239,68,68,0.65),
    0 4px 12px rgba(0,0,0,0.45) !important;
  animation: none !important;
}}
@keyframes predict-pulse {{
  0%   {{ box-shadow: 0 0 0 4px rgba(249,115,22,0.18), 0 8px 40px rgba(239,68,68,0.55); }}
  50%  {{ box-shadow: 0 0 0 10px rgba(249,115,22,0.08), 0 12px 60px rgba(239,68,68,0.75); }}
  100% {{ box-shadow: 0 0 0 4px rgba(249,115,22,0.18), 0 8px 40px rgba(239,68,68,0.55); }}
}}

/* ── DOWNLOAD REPORT button — amber/gold so it stands out ── */
[data-testid="stDownloadButton"] > button {{
  background: linear-gradient(135deg, #d97706, #b45309) !important;
  color: #ffffff !important;
  border: 1px solid #fbbf24 !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 10px 28px !important;
  box-shadow: 0 4px 20px rgba(217,119,6,0.45) !important;
  transition: all 0.2s ease !important;
  width: 100% !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
  background: linear-gradient(135deg, #f59e0b, #d97706) !important;
  box-shadow: 0 6px 28px rgba(251,191,36,0.55) !important;
  transform: translateY(-1px) !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: {CARD_BG} !important;
  border: 1px solid {CARD_BOR} !important;
  border-radius: 12px !important;
  padding: 16px !important;
}}
[data-testid="stMetricLabel"] {{
  color: {MUTED} !important;
  font-weight: 600 !important;
}}
[data-testid="stMetricLabel"] p {{
  color: {'#9ec8c6' if dark else '#2a6b72'} !important;
  font-weight: 600 !important;
  font-size: 13px !important;
}}
[data-testid="stMetricValue"] {{
  color: {'#78B9B5' if dark else '#065084'} !important;
  font-weight: 800 !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
  border: 1px solid {CARD_BOR} !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}}

/* ── Tabs ── */
div[data-testid="stTabs"] button {{
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  color: {MUTED} !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
  color: {'#78B9B5' if dark else '#065084'} !important;
  border-bottom: 2px solid {TEAL_MID} !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {{
  background: {CARD_BG} !important;
  border: 2px dashed {CARD_BOR} !important;
  border-radius: 12px !important;
}}
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] div {{
  color: {TEXT} !important;
}}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: {TEAL_MID} !important; }}

/* ── Alert boxes (light mode explicit) ── */
[data-testid="stInfo"] {{
  background: {'rgba(6,80,132,0.08)' if not dark else 'rgba(15,130,140,0.12)'} !important;
  color: {'#065084' if not dark else '#c4dedd'} !important;
  border-left: 4px solid {TEAL_MID} !important;
}}
[data-testid="stInfo"] p {{
  color: {'#065084' if not dark else '#c4dedd'} !important;
}}
[data-testid="stSuccess"] p {{
  color: {'#064e3b' if not dark else '#a7f3d0'} !important;
}}
[data-testid="stWarning"] p {{
  color: {'#92400e' if not dark else '#fde68a'} !important;
}}
[data-testid="stError"] p {{
  color: {'#7f1d1d' if not dark else '#fecaca'} !important;
}}

/* ── Markdown paragraphs (main area) ── */
.stMarkdown p, .stMarkdown span, .stMarkdown li {{
  color: {TEXT} !important;
}}
p, li {{
  color: {TEXT} !important;
}}

/* ── Caption ── */
.stCaption, .stCaption p {{
  color: {MUTED} !important;
}}

/* ══════════════════════════════════════════════
   RESPONSIVE — Tablet (max 1024px)
══════════════════════════════════════════════ */
@media screen and (max-width: 1024px) {{
  .hero-title {{ font-size: 38px !important; letter-spacing: -0.5px; }}
  .hero-sub   {{ font-size: 15px !important; }}
  .block-container {{ padding: 1.2rem 1.5rem !important; }}
  .kpi-number {{ font-size: 26px !important; }}
  .kpi-label  {{ font-size: 11px !important; }}
  .churn-card {{ padding: 20px 22px !important; }}
}}

/* ══════════════════════════════════════════════
   RESPONSIVE — Mobile (max 768px)
══════════════════════════════════════════════ */
@media screen and (max-width: 768px) {{
  .block-container {{ padding: 0.8rem 0.8rem !important; }}
  .hero-title {{ font-size: 28px !important; letter-spacing: -0.3px; margin-bottom: 6px; }}
  .hero-sub   {{ font-size: 13px !important; margin-bottom: 20px !important; }}
  .churn-card {{ padding: 16px 16px !important; border-radius: 12px !important; margin-bottom: 12px !important; }}
  .kpi-card   {{ padding: 14px 10px !important; border-radius: 10px !important; }}
  .kpi-number {{ font-size: 22px !important; }}
  .kpi-label  {{ font-size: 10px !important; letter-spacing: 1px; }}
  .section-label {{ font-size: 10px !important; letter-spacing: 1.5px; }}
  .risk-badge-high, .risk-badge-med, .risk-badge-low {{
    font-size: 14px !important; padding: 12px 14px !important; border-radius: 8px !important;
  }}
  .stButton > button {{
    font-size: 13px !important; padding: 8px 16px !important;
    height: auto !important; width: 100% !important;
  }}
  [data-testid="stDownloadButton"] > button {{
    font-size: 13px !important; padding: 8px 16px !important; width: 100% !important;
  }}
  [data-testid="stMetric"] {{ padding: 12px !important; }}
  [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
  section[data-testid="stSidebar"] {{ min-width: 260px !important; max-width: 80vw !important; }}
  div[data-testid="stTabs"] {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch; }}
  div[data-testid="stTabs"] > div {{ flex-wrap: nowrap !important; min-width: max-content; }}
  div[data-testid="stTabs"] button {{ font-size: 12px !important; padding: 6px 10px !important; white-space: nowrap; }}
  [data-testid="stDataFrame"] {{ font-size: 12px !important; overflow-x: auto !important; }}
  div[data-testid="stPlotlyChart"] {{ padding: 0.2rem !important; }}
  [data-testid="stNumberInput"] input {{ font-size: 14px !important; }}
  [data-baseweb="select"] {{ font-size: 13px !important; }}
  [data-testid="stSlider"] {{ padding: 0 4px !important; }}
  [data-testid="column"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
  .divider {{ margin: 16px 0 !important; }}
  [data-testid="stFileUploadDropzone"] {{ padding: 20px 12px !important; }}
  /* Stack KPI cards on mobile */
  .kpi-row {{ flex-direction: column !important; }}
}}

/* ══════════════════════════════════════════════
   RESPONSIVE — Small mobile (max 480px)
══════════════════════════════════════════════ */
@media screen and (max-width: 480px) {{
  .hero-title {{ font-size: 22px !important; }}
  .hero-sub   {{ font-size: 12px !important; }}
  .kpi-number {{ font-size: 18px !important; }}
  .churn-card {{ padding: 12px 12px !important; }}
  .risk-badge-high, .risk-badge-med, .risk-badge-low {{
    font-size: 13px !important; padding: 10px 12px !important;
  }}
  [data-testid="stMetricValue"] {{ font-size: 1.2rem !important; }}
  div[data-testid="stTabs"] button {{ font-size: 11px !important; padding: 5px 8px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ── THEME TOGGLE ──────────────────────────────────────────────────────────────
_tc1, _tc2 = st.columns([10, 1])
with _tc2:
    toggle_label = "☀️" if dark else "🌙"
    if st.button(toggle_label, help="Toggle Light / Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">', unsafe_allow_html=True)
st.markdown('<div class="hero-title">📡 Churn Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Telecom Customer Churn Prediction · Powered by Random Forest</div>',
            unsafe_allow_html=True)

# ── LOAD MODEL ────────────────────────────────────────────────────────────────
try:
    model   = joblib.load("churn_model.pkl")
    scaler  = joblib.load("scaler.pkl")
    columns = joblib.load("columns.pkl")
except Exception as e:
    st.error(f"⚠ Model files not found: {e}")
    st.stop()

# ── SQLITE HISTORY ────────────────────────────────────────────────────────────
DB_PATH = "churn_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT,
            tenure     INTEGER,
            monthly    REAL,
            contract   TEXT,
            internet   TEXT,
            churn_prob REAL,
            risk_tier  TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(tenure, monthly, contract, internet, prob):
    init_db()
    tier = "High" if prob > 0.66 else ("Medium" if prob > 0.33 else "Low")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (timestamp,tenure,monthly,contract,internet,churn_prob,risk_tier) "
        "VALUES (?,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tenure, monthly,
         contract, internet, round(prob * 100, 2), tier)
    )
    conn.commit()
    conn.close()

def load_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM predictions ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def get_kpi_stats():
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM predictions", conn)
        conn.close()
        if df.empty:
            return 0, 0.0, 0, 0
        return (len(df), df["churn_prob"].mean(),
                int((df["churn_prob"] > 66).sum()),
                int((df["churn_prob"] <= 33).sum()))
    except:
        return 0, 0.0, 0, 0

# ── KPI BANNER ────────────────────────────────────────────────────────────────
total_pred, avg_risk, high_risk_count, low_risk_count = get_kpi_stats()

st.markdown('<div class="section-label">Dashboard KPIs</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number">{total_pred}</div>'
                f'<div class="kpi-label">Total Predictions</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number">{avg_risk:.1f}%</div>'
                f'<div class="kpi-label">Avg Churn Risk</div></div>', unsafe_allow_html=True)
with k3:
    _red = "#f87171" if dark else "#b91c1c"
    st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:{_red};">'
                f'{high_risk_count}</div><div class="kpi-label">High Risk Customers</div>'
                f'</div>', unsafe_allow_html=True)
with k4:
    _grn = "#34d399" if dark else "#065f46"
    st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:{_grn};">'
                f'{low_risk_count}</div><div class="kpi-label">Low Risk Customers</div>'
                f'</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── PROJECT INFO ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="churn-card">
  <div class="section-label">About this Dashboard</div>
  <p style="margin:10px 0 6px;font-size:15px;color:{BODY_TXT};">
    Predicts telecom customer churn probability using the
    <strong>top 5 highest-impact features</strong> identified via Random Forest feature importance.
    All 41 model features are handled internally — only the signals that matter most are shown.
  </p>
  <p style="margin:0;font-size:13px;color:{MUTED};">
    Built with Scikit-Learn · Streamlit · Plotly &nbsp;|&nbsp;
    👩‍💻 Developed by <strong>Mahreen Begum</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("## 📋 Customer Profile")
st.sidebar.markdown(
    '<div class="top5-badge">⚡ Top-5 Predictive Features</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<p style='font-size:12px;color:rgba(255,255,255,0.65);margin:-8px 0 12px;'>"
    "Only the highest-impact signals are shown.<br>"
    "All other model inputs use safe defaults.</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

st.sidebar.markdown(
    '<span class="rank-pill">2</span>**Tenure** — account age',
    unsafe_allow_html=True
)
tenure = st.sidebar.slider("Tenure (months)", 0, 72, 12)

st.sidebar.markdown(
    '<span class="rank-pill">3</span>**Monthly Charges** — spend level',
    unsafe_allow_html=True
)
monthly = st.sidebar.slider("Monthly Charges (₹)", 100, 1500, 500, step=50)

total_charges_est = tenure * monthly
st.sidebar.markdown(
    f"<div style='background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.25);"
    f"border-radius:8px;padding:10px 14px;margin:8px 0 16px;font-size:12px;color:rgba(255,255,255,0.85);'>"
    f"<strong style='color:#ffffff;'>① TotalCharges</strong> · #1 feature<br>"
    f"Auto-computed: {tenure} × ₹{monthly} = <strong style='color:#ffffff;'>"
    f"₹{total_charges_est:,.0f}</strong></div>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

st.sidebar.markdown(
    '<span class="rank-pill">4</span>**Contract Type** — commitment level',
    unsafe_allow_html=True
)
contract = st.sidebar.selectbox(
    "Contract Type",
    ["Month-to-month", "One year", "Two year"]
)
st.sidebar.markdown("---")

st.sidebar.markdown(
    '<span class="rank-pill">5</span>**Online Security** — add-on adoption',
    unsafe_allow_html=True
)
online_security = st.sidebar.selectbox(
    "Online Security",
    ["No", "Yes", "No internet service"]
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size:11px;color:rgba(255,255,255,0.45);text-align:center;'>"
    "36 remaining model features<br>set to neutral baseline defaults</p>",
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# ── BUILD FULL 41-FEATURE INPUT ROW ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def build_input_row(tenure, monthly, contract, online_security):
    row = {col: 0 for col in columns}
    row["TotalCharges"]                        = tenure * monthly
    row["tenure"]                              = tenure
    row["MonthlyCharges"]                      = monthly
    row["Contract_Month-to-month"]             = 1 if contract == "Month-to-month" else 0
    row["Contract_One year"]                   = 1 if contract == "One year"       else 0
    row["Contract_Two year"]                   = 1 if contract == "Two year"       else 0
    row["OnlineSecurity_0"]                    = 1 if online_security == "No"                  else 0
    row["OnlineSecurity_1"]                    = 1 if online_security == "Yes"                 else 0
    row["OnlineSecurity_No internet service"]  = 1 if online_security == "No internet service" else 0
    row["SeniorCitizen"]    = 0
    row["Partner"]          = 0
    row["Dependents"]       = 0
    row["PhoneService"]     = 1
    row["PaperlessBilling"] = 1
    row["gender_Female"]    = 0
    row["gender_Male"]      = 0
    row["MultipleLines_0"]               = 1
    row["MultipleLines_1"]               = 0
    row["MultipleLines_No phone service"] = 0
    row["InternetService_0"]           = 0
    row["InternetService_DSL"]         = 0
    row["InternetService_Fiber optic"] = 1
    row["OnlineBackup_0"]                   = 1
    row["OnlineBackup_1"]                   = 0
    row["OnlineBackup_No internet service"] = 0
    row["DeviceProtection_0"]                   = 1
    row["DeviceProtection_1"]                   = 0
    row["DeviceProtection_No internet service"] = 0
    row["TechSupport_0"]                   = 1
    row["TechSupport_1"]                   = 0
    row["TechSupport_No internet service"] = 0
    row["StreamingTV_0"]                   = 1
    row["StreamingTV_1"]                   = 0
    row["StreamingTV_No internet service"] = 0
    row["StreamingMovies_0"]                   = 1
    row["StreamingMovies_1"]                   = 0
    row["StreamingMovies_No internet service"] = 0
    row["PaymentMethod_Bank transfer (automatic)"] = 0
    row["PaymentMethod_Credit card (automatic)"]   = 0
    row["PaymentMethod_Electronic check"]          = 1
    row["PaymentMethod_Mailed check"]              = 0
    df_row = pd.DataFrame([row])
    for col in columns:
        if col not in df_row.columns:
            df_row[col] = 0
    return df_row[columns]

input_df = build_input_row(tenure, monthly, contract, online_security)
scaled   = scaler.transform(input_df)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Predict",
    "🧠 SHAP Explainer",
    "💰 Cost Estimator",
    "📂 Batch Analysis",
    "📋 History"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREDICT
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 Run Prediction")

    _VAL_C = TEAL_LIGHT if dark else "#065084"
    st.markdown(f"""
    <div class="churn-card" style="padding:18px 24px;margin-bottom:18px;">
      <div class="section-label">Active Input Summary · Top-5 Features</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:12px;">
        <div>
          <span style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">① TOTAL CHARGES (auto)</span>
          <div style="font-weight:700;color:{_VAL_C};font-size:16px;margin-top:2px;">₹{total_charges_est:,.0f}</div>
        </div>
        <div>
          <span style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">② TENURE</span>
          <div style="font-weight:700;color:{_VAL_C};font-size:16px;margin-top:2px;">{tenure} mo</div>
        </div>
        <div>
          <span style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">③ MONTHLY CHARGES</span>
          <div style="font-weight:700;color:{_VAL_C};font-size:16px;margin-top:2px;">₹{monthly}</div>
        </div>
        <div>
          <span style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">④ CONTRACT</span>
          <div style="font-weight:700;color:{_VAL_C};font-size:16px;margin-top:2px;">{contract}</div>
        </div>
        <div>
          <span style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">⑤ ONLINE SECURITY</span>
          <div style="font-weight:700;color:{_VAL_C};font-size:16px;margin-top:2px;">{online_security}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ PREDICT CHURN RISK", key="predict_main", type="primary", use_container_width=True):
        with st.spinner("Analyzing customer profile..."):
            time.sleep(1.0)

        prob = model.predict_proba(scaled)[0][1]
        pct  = prob * 100
        save_prediction(tenure, monthly, contract, "Fiber optic (default)", prob)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if pct > 66:
                st.markdown(f'<div class="risk-badge-high">🚨 HIGH CHURN RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
                st.snow()
            elif pct > 33:
                st.markdown(f'<div class="risk-badge-med">⚠️ MODERATE RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-badge-low">✅ LOW CHURN RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
                st.balloons()
        with col2:
            st.metric("Churn Probability", f"{pct:.1f}%")
        with col3:
            risk_label = "High 🔴" if pct > 66 else ("Medium 🟡" if pct > 33 else "Low 🟢")
            st.metric("Risk Tier", risk_label)

        # ── Gauge chart ───────────────────────────────────────────────────────
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct,
            number={"suffix": "%", "font": {"size": 36, "color": CHART_FONT}},
            delta={"reference": 50, "increasing": {"color": "#f87171"},
                   "decreasing": {"color": "#34d399"}},
            title={"text": "Churn Risk Score", "font": {"color": CHART_TITLE, "size": 18}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": CHART_TICK,
                    "tickfont": {"color": CHART_TICK}
                },
                "bar":  {"color": TEAL_MID, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0,  33], "color": "rgba(52,211,153,0.15)"},
                    {"range": [33, 66], "color": "rgba(251,191,36,0.15)"},
                    {"range": [66,100], "color": "rgba(248,113,113,0.15)"},
                ],
                "threshold": {"line": {"color": "#f87171", "width": 3}, "value": 50}
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": CHART_FONT},
            height=280, margin=dict(t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── PDF Export ────────────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 📄 Export Detailed Report")
        try:
            from fpdf import FPDF
            import os

            import fpdf as _fpdf_pkg
            _fpdf_dir    = os.path.dirname(_fpdf_pkg.__file__)
            _dv_reg      = os.path.join(_fpdf_dir, "fonts", "DejaVuSans.ttf")
            _dv_bold     = os.path.join(_fpdf_dir, "fonts", "DejaVuSans-Bold.ttf")
            _has_unicode = os.path.exists(_dv_reg) and os.path.exists(_dv_bold)
            _R = "\u20b9" if _has_unicode else "Rs."

            tier_txt    = "High" if pct > 66 else ("Medium" if pct > 33 else "Low")
            tenure_band = ("New (0-12 mo)"        if tenure <= 12
                           else "Growing (13-36 mo)"   if tenure <= 36
                           else "Established (37-60 mo)" if tenure <= 60
                           else "Loyal (60+ mo)")
            charge_band = ("Budget (<= Rs.300)"        if monthly <= 300
                           else "Mid-range (Rs.301-700)"  if monthly <= 700
                           else "Premium (Rs.701-1100)"   if monthly <= 1100
                           else "High-value (>Rs.1100)")
            ltv_est   = monthly * 12 * (3 if contract == "Two year"
                                        else 2 if contract == "One year" else 1)
            rev_at_risk  = ltv_est * prob
            industry_avg = 26.0

            drivers = []
            if contract == "Month-to-month":
                drivers.append(("Contract Type",
                    "Month-to-month customers are 3x more likely to churn than annual subscribers. "
                    "No long-term commitment means zero switching cost for the customer."))
            if online_security == "No":
                drivers.append(("No Online Security",
                    "Customers without add-on services show higher churn. Add-ons increase "
                    "perceived value and raise the cost of switching to a competitor."))
            if tenure <= 12:
                drivers.append(("Low Tenure",
                    f"At {tenure} month(s), this customer is in the highest-risk early churn window "
                    f"(months 1-12). Loyalty has not yet been established."))
            if monthly > 1000:
                drivers.append(("High Monthly Charges",
                    f"At {_R}{monthly:,}/mo, this customer pays above the high-value threshold. "
                    "Price sensitivity and perceived value mismatch are key churn triggers."))
            if not drivers:
                drivers.append(("Strong Retention Profile",
                    "No major churn risk factors detected. This customer exhibits characteristics "
                    "associated with long-term retention."))

            actions = []
            priority = 1
            if contract == "Month-to-month":
                actions.append((priority, "Offer Annual Contract Discount",
                    "Provide a 15-20% discount on an annual or two-year plan. "
                    "Frame it as a loyalty reward. Reduces churn probability by ~30%."))
                priority += 1
            if tenure <= 12:
                actions.append((priority, "Launch Early Loyalty Programme",
                    "Enrol the customer in a months 3-12 loyalty scheme with reward points, "
                    "free data top-ups, or waived fees. Early intervention reduces churn by up to 25%."))
                priority += 1
            if online_security == "No":
                actions.append((priority, "Upsell Online Security Add-on",
                    "Offer a 3-month free trial of Online Security. Customers with 2+ add-ons churn "
                    "40% less. Bundle with device protection for higher uptake."))
                priority += 1
            if monthly > 1000:
                actions.append((priority, "Conduct Pricing Review Call",
                    "Assign a dedicated account manager to review the customer's plan. Offer a plan "
                    "optimisation that reduces the bill by Rs.100-200/mo while retaining core services."))
                priority += 1
            if not actions:
                actions.append((1, "Proactive Satisfaction Check-in",
                    "Schedule a quarterly satisfaction call. Introduce the customer to new features "
                    "or services to deepen engagement. Maintain current positive trajectory."))

            _head_font = [None]

            class PDF(FPDF):
                def header(self):
                    self.set_font(_head_font[0], "B", 15)
                    self.set_fill_color(6, 80, 132)
                    self.set_text_color(255, 255, 255)
                    self.cell(0, 14, "  ChurnGuard  |  Customer Churn Intelligence Report",
                              new_x="LMARGIN", new_y="NEXT", align="L", fill=True)
                    self.set_draw_color(120, 185, 181)
                    self.set_line_width(0.8)
                    self.ln(3)

                def footer(self):
                    self.set_y(-14)
                    self.set_font(_head_font[0], "", 8)
                    self.set_text_color(150, 150, 150)
                    self.cell(0, 8,
                        f"ChurnGuard Analytics  |  Generated {datetime.now().strftime('%d %b %Y %H:%M')}  |  Confidential",
                        align="C")

                def section_title(self, txt):
                    self.set_font(_head_font[0], "B", 11)
                    self.set_fill_color(230, 243, 255)
                    self.set_text_color(6, 80, 132)
                    self.cell(0, 8, f"  {txt}", new_x="LMARGIN", new_y="NEXT", fill=True)
                    self.set_text_color(30, 30, 30)
                    self.ln(2)

                def body_line(self, txt, bold=False, color=(30, 30, 30), size=10):
                    style = "B" if bold else ""
                    self.set_font(_head_font[0], style, size)
                    self.set_text_color(*color)
                    self.cell(0, 6, txt, new_x="LMARGIN", new_y="NEXT")
                    self.set_text_color(30, 30, 30)

                def two_col(self, label, value, label_w=80):
                    self.set_font(_head_font[0], "B", 10)
                    self.set_text_color(80, 80, 80)
                    self.cell(label_w, 6, label)
                    self.set_font(_head_font[0], "", 10)
                    self.set_text_color(20, 20, 20)
                    self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")
                    self.set_text_color(30, 30, 30)

                def wrapped_line(self, label, body_txt, label_w=52):
                    self.set_font(_head_font[0], "B", 10)
                    self.set_text_color(6, 80, 132)
                    self.cell(label_w, 6, label)
                    self.set_font(_head_font[0], "", 10)
                    self.set_text_color(30, 30, 30)
                    self.multi_cell(0, 6, body_txt)
                    self.ln(1)

            pdf = PDF()
            if _has_unicode:
                pdf.add_font("DejaVu",  "",  _dv_reg,  uni=True)
                pdf.add_font("DejaVu",  "B", _dv_bold, uni=True)
                _head_font[0] = "DejaVu"
            else:
                _head_font[0] = "Helvetica"

            pdf.set_margins(14, 14, 14)
            pdf.add_page()

            pdf.section_title("1. Executive Summary")
            risk_color = (180, 30, 30) if pct > 66 else (180, 100, 0) if pct > 33 else (20, 120, 60)
            pdf.set_font(_head_font[0], "B", 22)
            pdf.set_text_color(*risk_color)
            pdf.cell(0, 12, f"  Churn Risk: {pct:.1f}%  |  Tier: {tier_txt}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(30, 30, 30)
            pdf.set_font(_head_font[0], "", 10)

            if pct > 66:
                summary_txt = (
                    f"This customer is classified as HIGH RISK with a churn probability of {pct:.1f}%. "
                    f"Immediate intervention is strongly recommended. The industry average churn rate "
                    f"for telecom is approximately {industry_avg:.0f}%; this customer's risk is "
                    f"{pct - industry_avg:.1f} percentage points above that benchmark. "
                    f"Based on an estimated LTV of {_R}{ltv_est:,}, the projected revenue at risk "
                    f"is {_R}{rev_at_risk:,.0f}. Prioritise this customer for your highest-impact "
                    f"retention interventions within the next 7 days.")
            elif pct > 33:
                summary_txt = (
                    f"This customer is classified as MODERATE RISK with a churn probability of {pct:.1f}%. "
                    f"Proactive engagement is advised before risk escalates. The industry telecom average "
                    f"is approximately {industry_avg:.0f}%; this customer is {abs(pct - industry_avg):.1f} "
                    f"percentage points {'above' if pct > industry_avg else 'below'} that benchmark. "
                    f"Estimated revenue at risk stands at {_R}{rev_at_risk:,.0f} based on projected LTV "
                    f"of {_R}{ltv_est:,}. A targeted retention offer within 30 days is recommended.")
            else:
                summary_txt = (
                    f"This customer is classified as LOW RISK with a churn probability of {pct:.1f}%. "
                    f"The industry average churn rate for telecom is approximately {industry_avg:.0f}%; "
                    f"this customer is {industry_avg - pct:.1f} percentage points below that benchmark — "
                    f"a strong retention signal. Estimated LTV is {_R}{ltv_est:,}. Continue standard "
                    f"engagement practices and monitor for any shifts in usage or billing patterns.")
            pdf.multi_cell(0, 6, summary_txt)
            pdf.ln(4)

            pdf.section_title("2. Customer Profile")
            pdf.two_col("Tenure",           f"{tenure} months  ({tenure_band})")
            pdf.two_col("Monthly Charges",  f"{_R}{monthly:,}  ({charge_band})")
            pdf.two_col("Total Charges",    f"{_R}{total_charges_est:,.0f}  (auto-computed)")
            pdf.two_col("Contract Type",    contract)
            pdf.two_col("Online Security",  online_security)
            pdf.two_col("Estimated LTV",    f"{_R}{ltv_est:,}")
            pdf.two_col("Revenue at Risk",  f"{_R}{rev_at_risk:,.0f}")
            pdf.two_col("Report Generated", datetime.now().strftime("%d %b %Y  %H:%M:%S"))
            pdf.ln(4)

            pdf.section_title("3. Risk Benchmarking")
            pdf.set_font(_head_font[0], "", 10)
            benchmarks = [
                ("Metric",                 "This Customer",    "Industry Benchmark"),
                ("Churn Probability",       f"{pct:.1f}%",      f"~{industry_avg:.0f}% avg"),
                ("Tenure Stability",        tenure_band,        "Loyal = 60+ months"),
                ("Monthly Spend Tier",      charge_band,        "Avg: Rs.400-600/mo"),
                ("Contract Commitment",     contract,           "Best: Two year"),
                ("Add-on Adoption",         online_security,    "Ideal: Yes (reduces churn 40%)"),
            ]
            col_widths = [72, 55, 55]
            for i, row_data in enumerate(benchmarks):
                if i == 0:
                    pdf.set_font(_head_font[0], "B", 9)
                    pdf.set_fill_color(210, 230, 245)
                    fill = True
                else:
                    pdf.set_font(_head_font[0], "", 9)
                    pdf.set_fill_color(245, 250, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
                    fill = True
                for cell, w in zip(row_data, col_widths):
                    pdf.cell(w, 6, f" {cell}", border=1, fill=fill)
                pdf.ln()
            pdf.ln(4)

            pdf.section_title("4. Churn Driver Analysis")
            pdf.set_font(_head_font[0], "", 10)
            pdf.multi_cell(0, 6,
                "The following factors were identified as the primary contributors to this "
                "customer's churn risk score, based on the Random Forest model's top-5 "
                "feature importances (TotalCharges, Tenure, MonthlyCharges, Contract, OnlineSecurity):")
            pdf.ln(2)
            for feature, explanation in drivers:
                pdf.wrapped_line(f"[!] {feature}:", explanation)
            pdf.ln(2)

            pdf.section_title("5. Prioritised Retention Action Plan")
            pdf.set_font(_head_font[0], "", 10)
            pdf.multi_cell(0, 6,
                "Actions are ranked by expected impact on churn reduction. "
                "Execute in order for maximum retention effect.")
            pdf.ln(2)
            for rank, action_title, action_body in actions:
                pdf.set_font(_head_font[0], "B", 10)
                pdf.set_text_color(6, 80, 132)
                pdf.cell(0, 7, f"  Action {rank}: {action_title}",
                         new_x="LMARGIN", new_y="NEXT")
                pdf.set_font(_head_font[0], "", 9)
                pdf.set_text_color(50, 50, 50)
                pdf.set_x(pdf.get_x() + 8)
                pdf.multi_cell(0, 5, action_body)
                pdf.set_text_color(30, 30, 30)
                pdf.ln(2)
            pdf.ln(2)

            pdf.section_title("6. Financial Impact Summary")
            campaign_est = 500
            lift_est     = 0.25
            new_prob_est = max(0, prob - lift_est)
            saved_est    = ltv_est * (prob - new_prob_est)
            net_est      = saved_est - campaign_est
            pdf.set_font(_head_font[0], "", 10)
            pdf.multi_cell(0, 6,
                f"Assuming a standard retention campaign cost of {_R}{campaign_est:,} "
                f"and an expected churn reduction of {lift_est*100:.0f}%:")
            pdf.ln(2)
            pdf.two_col("Estimated Customer LTV:",         f"{_R}{ltv_est:,}")
            pdf.two_col("Revenue at Risk (no action):",    f"{_R}{rev_at_risk:,.0f}")
            pdf.two_col("Expected Revenue Saved:",         f"{_R}{saved_est:,.0f}")
            pdf.two_col("Estimated Campaign Cost:",        f"{_R}{campaign_est:,}")
            pdf.two_col("Projected Net ROI:",              f"{_R}{net_est:,.0f}")
            roi_ratio = saved_est / campaign_est if campaign_est > 0 else 0
            pdf.two_col("Return on Investment:",
                        f"{roi_ratio:.1f}x  (every {_R}1 spent returns {_R}{roi_ratio:.1f})")
            pdf.ln(4)

            pdf.section_title("7. Model & Methodology Notes")
            pdf.set_font(_head_font[0], "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5,
                "Model: Random Forest Classifier  |  Trees: 300  |  Max Depth: 10  |  "
                "Class Weight: Balanced  |  Training Data: Telco Customer Churn Dataset (7,043 records)\n"
                "Feature Engineering: One-hot encoding for categorical variables, StandardScaler "
                "normalisation, TotalCharges auto-derived as Tenure x MonthlyCharges.\n"
                "Top-5 Features by Importance: TotalCharges (16.9%), Tenure (14.4%), "
                "MonthlyCharges (14.4%), Contract_Month-to-month (5.5%), OnlineSecurity_No (3.3%).\n"
                "This report is generated by ChurnGuard and is intended for internal business use only. "
                "Predictions are probabilistic and should be used alongside human judgement.")
            pdf.set_text_color(30, 30, 30)

            pdf_bytes = pdf.output()
            st.download_button(
                label="⬇️ Download Detailed PDF Report",
                data=bytes(pdf_bytes),
                file_name=f"churnguard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except ImportError:
            st.info("Install fpdf2 to enable PDF export:  pip install fpdf2")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

        # ── Retention Recommendations ─────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 💡 Retention Recommendations")
        recs = []
        if contract == "Month-to-month":
            recs.append("📄 **Offer a discounted annual contract** — MTM customers churn 3x more.")
        if online_security == "No":
            recs.append("🔒 **Upsell Online Security** — add-ons increase switching costs.")
        if tenure < 12:
            recs.append("🎁 **Apply loyalty discount in months 3-12** — early churn window is highest risk.")
        if monthly > 1000:
            recs.append("💰 **Review pricing** — high monthly charges strongly correlate with churn.")
        if not recs:
            recs.append("✅ Strong retention indicators — no urgent actions needed.")
        for r in recs:
            st.markdown(
                f"<div class='churn-card' style='padding:14px 20px;margin-bottom:10px;'>{r}</div>",
                unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Feature Importance chart ───────────────────────────────────────────────
    st.markdown("### 📊 Feature Importance")
    try:
        import pandas as _pd
        imp_df = _pd.DataFrame({
            "Feature":    columns,
            "Importance": model.feature_importances_
        }).sort_values("Importance", ascending=True).tail(15)

        top5_features = {"TotalCharges", "tenure", "MonthlyCharges",
                         "Contract_Month-to-month", "OnlineSecurity_0"}
        imp_df["IsTop5"] = imp_df["Feature"].isin(top5_features)
        imp_df["Color"]  = imp_df["IsTop5"].apply(
            lambda x: TEAL_MID if x else ("rgba(120,185,181,0.35)" if dark else "rgba(6,80,132,0.30)")
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=imp_df["Importance"],
            y=imp_df["Feature"],
            orientation="h",
            marker_color=imp_df["Color"],
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=PLY_BG,
            font={"color": CHART_FONT, "family": "DM Sans"},
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=420,
            template=PLY_TPL
        )
        fig.update_xaxes(
            gridcolor=CHART_GRID,
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            linecolor=CHART_AXIS_LINE
        )
        fig.update_yaxes(
            gridcolor=CHART_GRID,
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            linecolor=CHART_AXIS_LINE
        )
        st.plotly_chart(fig, use_container_width=True)
        _cap_c = TEAL_LIGHT if dark else BLUE_DEEP
        st.caption(f"Highlighted bars = Top-5 features used in the sidebar inputs.")
    except Exception as e:
        st.info(f"Feature importance unavailable: {e}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Correlation Heatmap ───────────────────────────────────────────────────
    st.markdown("### 🔥 Feature Correlation Matrix")
    try:
        df_raw = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
        df_raw["TotalCharges"] = pd.to_numeric(df_raw["TotalCharges"], errors="coerce")
        df_raw["Churn"] = df_raw["Churn"].map({"Yes": 1, "No": 0})
        corr = df_raw.select_dtypes(include="number").corr()
        fig = px.imshow(
            corr, text_auto=".2f",
            color_continuous_scale=[[0, PURPLE_DEEP], [0.5, TEAL_MID], [1, TEAL_LIGHT]],
            template=PLY_TPL
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": CHART_FONT, "family": "DM Sans"},
            margin=dict(t=10, b=0)
        )
        fig.update_xaxes(tickfont={"color": CHART_TICK}, title_font={"color": CHART_FONT})
        fig.update_yaxes(tickfont={"color": CHART_TICK}, title_font={"color": CHART_FONT})
        # Ensure annotation text (the .2f values) is readable
        fig.update_traces(textfont={"color": "#ffffff" if dark else "#0d2b30"})
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Dataset CSV not found — skipping correlation heatmap.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SHAP EXPLAINER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🧠 SHAP Explainability")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>What is SHAP?</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        SHAP (SHapley Additive exPlanations) shows <strong>which features pushed the
        prediction up or down</strong> for this specific customer.
        Red bars increase churn risk, green bars decrease it.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔬 Explain This Prediction", key="shap_btn"):
        try:
            import shap
            import numpy as np
            with st.spinner("Computing SHAP values..."):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(scaled)

            if isinstance(shap_vals, list):
                sv = np.array(shap_vals[1][0]).flatten()
            else:
                sv = np.array(shap_vals)
                if sv.ndim == 3:
                    sv = sv[0, :, 1]
                elif sv.ndim == 2:
                    sv = sv[0]
                else:
                    sv = sv.flatten()

            shap_df = pd.DataFrame({
                "Feature":    list(columns),
                "SHAP Value": sv.tolist(),
                "Abs":        np.abs(sv).tolist()
            }).sort_values("Abs", ascending=True).tail(15)

            shap_df["Color"] = shap_df["SHAP Value"].apply(
                lambda x: "#f87171" if x > 0 else "#34d399"
            )

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=shap_df["SHAP Value"],
                y=shap_df["Feature"],
                orientation="h",
                marker_color=shap_df["Color"],
                hovertemplate="<b>%{y}</b><br>SHAP: %{x:.4f}<extra></extra>"
            ))
            fig.add_vline(x=0, line_color=CHART_AXIS_LINE, line_width=1.5, line_dash="dash")
            fig.update_layout(
                title={"text": "Feature Contributions to This Prediction",
                       "font": {"color": CHART_TITLE, "size": 16}},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=PLY_BG,
                font={"color": CHART_FONT, "family": "DM Sans"},
                template=PLY_TPL,
                xaxis_title="SHAP Value (impact on churn probability)",
                margin=dict(l=0, r=0, t=50, b=0),
                height=460
            )
            fig.update_xaxes(
                gridcolor=CHART_GRID,
                tickfont={"color": CHART_TICK},
                title_font={"color": CHART_FONT},
                linecolor=CHART_AXIS_LINE
            )
            fig.update_yaxes(
                gridcolor=CHART_GRID,
                tickfont={"color": CHART_TICK},
                title_font={"color": CHART_FONT},
                linecolor=CHART_AXIS_LINE
            )
            st.plotly_chart(fig, use_container_width=True)

            top_pos = shap_df[shap_df["SHAP Value"] > 0].nlargest(3, "SHAP Value")
            top_neg = shap_df[shap_df["SHAP Value"] < 0].nsmallest(3, "SHAP Value")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔴 Top Churn Drivers")
                for _, row in top_pos.iterrows():
                    st.markdown(
                        f"<div class='churn-card' style='padding:12px 18px;margin-bottom:8px;'>"
                        f"<strong style='color:{CHART_TITLE};'>{row['Feature']}</strong><br>"
                        f"<span style='color:#f87171;font-size:13px;'>"
                        f"SHAP: +{row['SHAP Value']:.4f} — raises churn risk</span>"
                        f"</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("#### 🟢 Top Retention Signals")
                for _, row in top_neg.iterrows():
                    st.markdown(
                        f"<div class='churn-card' style='padding:12px 18px;margin-bottom:8px;'>"
                        f"<strong style='color:{CHART_TITLE};'>{row['Feature']}</strong><br>"
                        f"<span style='color:#34d399;font-size:13px;'>"
                        f"SHAP: {row['SHAP Value']:.4f} — lowers churn risk</span>"
                        f"</div>", unsafe_allow_html=True)

        except ImportError:
            st.error("SHAP not installed. Run:  pip install shap")
        except Exception as e:
            st.error(f"SHAP computation failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHURN COST ESTIMATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 💰 Churn Cost Estimator")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Business ROI Calculator</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Enter your business metrics to calculate <strong>expected revenue at risk</strong>
        and the <strong>ROI of a retention campaign</strong> for this customer.
        </p>
    </div>
    """, unsafe_allow_html=True)

    prob_live = model.predict_proba(scaled)[0][1]
    pct_live  = prob_live * 100

    ce1, ce2 = st.columns(2)
    with ce1:
        ltv = st.number_input(
            "Customer Lifetime Value (₹)", min_value=0, value=36000, step=1000,
            help="Total revenue expected from this customer over their lifetime")
        campaign_cost = st.number_input(
            "Retention Campaign Cost (₹)", min_value=0, value=500, step=100,
            help="Cost to run a targeted retention offer for this customer")
    with ce2:
        retention_lift = st.number_input(
            "Expected Churn Reduction (%)", min_value=1, max_value=100, value=30, step=5,
            help="How much the campaign is expected to reduce churn probability")
        discount_rate = st.number_input(
            "Annual Discount Rate (%)", min_value=0, max_value=50, value=10, step=1,
            help="Used to calculate Net Present Value of at-risk revenue")

    if st.button("📊 Calculate ROI", key="roi_btn"):
        rev_at_risk    = ltv * prob_live
        new_prob       = max(0, prob_live - (retention_lift / 100))
        rev_saved      = ltv * (prob_live - new_prob)
        net_roi        = rev_saved - campaign_cost
        roi_pct        = ((rev_saved - campaign_cost) / campaign_cost * 100) if campaign_cost > 0 else 0
        breakeven_prob = campaign_cost / ltv if ltv > 0 else 0

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        with r1: st.metric("Revenue at Risk", f"₹{rev_at_risk:,.0f}")
        with r2: st.metric("Revenue Saved",   f"₹{rev_saved:,.0f}")
        with r3: st.metric("Net ROI",
                           f"+₹{net_roi:,.0f}" if net_roi >= 0 else f"-₹{abs(net_roi):,.0f}")
        with r4: st.metric("ROI %",           f"{roi_pct:.0f}%")

        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Revenue at Risk", "Campaign Cost", "Revenue Saved", "Net ROI"],
            y=[rev_at_risk, -campaign_cost, rev_saved, 0],
            connector={"line": {"color": TEAL_MID}},
            increasing={"marker": {"color": "#34d399"}},
            decreasing={"marker": {"color": "#f87171"}},
            totals={"marker":    {"color": TEAL_MID}},
            text=[f"₹{rev_at_risk:,.0f}", f"-₹{campaign_cost:,.0f}",
                  f"+₹{rev_saved:,.0f}",  f"₹{net_roi:,.0f}"],
            textposition="outside"
        ))
        fig.update_layout(
            title={"text": "Retention Campaign ROI Waterfall",
                   "font": {"color": CHART_TITLE, "size": 16}},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=PLY_BG,
            font={"color": CHART_FONT, "family": "DM Sans"},
            template=PLY_TPL,
            height=380,
            margin=dict(t=50, b=0)
        )
        fig.update_xaxes(
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            gridcolor=CHART_GRID,
            linecolor=CHART_AXIS_LINE
        )
        fig.update_yaxes(
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            gridcolor=CHART_GRID,
            linecolor=CHART_AXIS_LINE
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if net_roi > 0:
            st.markdown(f"""
            <div class='risk-badge-low' style='font-size:15px;text-align:left;padding:18px 24px;'>
            <strong>Campaign is financially justified.</strong><br>
            For every ₹1 spent on retention, you earn back ₹{roi_pct/100:.1f}.
            Break-even churn probability: {breakeven_prob*100:.1f}%.
            Current risk ({pct_live:.1f}%) {'exceeds' if prob_live > breakeven_prob else 'is below'} break-even.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='risk-badge-high' style='font-size:15px;text-align:left;padding:18px 24px;'>
            <strong>Campaign may not be cost-effective.</strong><br>
            Revenue saved (₹{rev_saved:,.0f}) is less than campaign cost (₹{campaign_cost:,.0f}).
            Consider a lower-cost retention channel or targeting higher-LTV customers.
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BATCH ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📂 Batch Customer Analysis")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Bulk Scoring</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Upload a CSV of customer records. The model scores every row and returns
        churn probabilities and risk tiers. Missing columns are auto-filled.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload customer CSV", type=["csv"])

    if uploaded:
        try:
            batch_df = pd.read_csv(uploaded)
            st.success(f"Loaded {len(batch_df):,} customer records")

            for col in columns:
                if col not in batch_df.columns:
                    batch_df[col] = 0
            batch_scaled = scaler.transform(batch_df[columns])
            probs = model.predict_proba(batch_scaled)[:, 1]

            batch_df["Churn_Probability_%"] = (probs * 100).round(1)
            batch_df["Risk_Tier"] = pd.cut(
                probs * 100, bins=[0, 33, 66, 100],
                labels=["Low", "Medium", "High"]
            )

            b1, b2, b3, b4 = st.columns(4)
            with b1: st.metric("Total Customers", f"{len(batch_df):,}")
            with b2: st.metric("Avg Churn Risk",  f"{probs.mean()*100:.1f}%")
            with b3: st.metric("High Risk (>66%)", f"{(probs > 0.66).sum():,}")
            with b4: st.metric("Low Risk (<33%)",  f"{(probs < 0.33).sum():,}")

            tier_counts = batch_df["Risk_Tier"].value_counts()
            fig = px.pie(
                values=tier_counts.values, names=tier_counts.index,
                color_discrete_map={"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"},
                hole=0.45, template=PLY_TPL, title="Customer Risk Distribution"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": CHART_FONT, "family": "DM Sans"},
                height=350,
                legend={"font": {"color": CHART_LEGEND}}
            )
            fig.update_traces(textfont_color=CHART_FONT)
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.histogram(
                batch_df, x="Churn_Probability_%", nbins=20,
                color_discrete_sequence=[TEAL_MID], template=PLY_TPL,
                title="Churn Probability Distribution"
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=PLY_BG,
                font={"color": CHART_FONT, "family": "DM Sans"},
                height=300,
                xaxis_title="Churn Probability (%)",
                yaxis_title="Number of Customers"
            )
            fig2.update_xaxes(tickfont={"color": CHART_TICK}, gridcolor=CHART_GRID)
            fig2.update_yaxes(tickfont={"color": CHART_TICK}, gridcolor=CHART_GRID)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Scored Customers (sorted by risk)")
            st.dataframe(
                batch_df.sort_values("Churn_Probability_%", ascending=False),
                use_container_width=True
            )
            st.download_button(
                label="⬇️ Download Scored CSV",
                data=batch_df.to_csv(index=False),
                file_name=f"churn_scored_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Could not process file: {e}")
    else:
        st.markdown(f"""
        <div class='churn-card' style='text-align:center;padding:40px 20px;'>
            <div style='font-size:40px;margin-bottom:12px;'>📋</div>
            <div style='font-size:16px;font-weight:600;color:{BODY_TXT};margin-bottom:8px;'>
                Drop a CSV file above to begin
            </div>
            <div style='font-size:13px;color:{MUTED};'>
                Any missing columns will be auto-filled with zero (baseline).
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📋 Prediction History")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Logged Predictions</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Every prediction is automatically saved here.
        Track risk trends over time across different customer profiles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hist_df = load_history()

    if hist_df.empty:
        st.info("No predictions logged yet. Run a prediction in the Predict tab first.")
    else:
        h1, h2, h3 = st.columns(3)
        with h1: st.metric("Total Logged",    f"{len(hist_df):,}")
        with h2: st.metric("Avg Risk",         f"{hist_df['churn_prob'].mean():.1f}%")
        with h3: st.metric("High Risk Logged", f"{(hist_df['churn_prob'] > 66).sum():,}")

        hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
        fig = px.line(
            hist_df.sort_values("timestamp"),
            x="timestamp", y="churn_prob", markers=True,
            color_discrete_sequence=[TEAL_MID], template=PLY_TPL,
            title="Churn Risk Over Time"
        )
        fig.add_hline(y=66, line_dash="dash", line_color="#f87171",
                      annotation_text="High Risk Threshold",
                      annotation_font_color="#f87171")
        fig.add_hline(y=33, line_dash="dash", line_color="#fbbf24",
                      annotation_text="Medium Risk Threshold",
                      annotation_font_color="#fbbf24")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=PLY_BG,
            font={"color": CHART_FONT, "family": "DM Sans"},
            height=350,
            xaxis_title="Time",
            yaxis_title="Churn Probability (%)"
        )
        fig.update_xaxes(
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            gridcolor=CHART_GRID,
            linecolor=CHART_AXIS_LINE
        )
        fig.update_yaxes(
            tickfont={"color": CHART_TICK},
            title_font={"color": CHART_FONT},
            gridcolor=CHART_GRID,
            linecolor=CHART_AXIS_LINE
        )
        st.plotly_chart(fig, use_container_width=True)

        tier_hist = hist_df["risk_tier"].value_counts()
        fig2 = px.bar(
            x=tier_hist.index, y=tier_hist.values,
            color=tier_hist.index,
            color_discrete_map={"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"},
            template=PLY_TPL, title="Risk Tier Distribution (all time)"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=PLY_BG,
            font={"color": CHART_FONT, "family": "DM Sans"},
            height=300,
            showlegend=False,
            xaxis_title="Risk Tier",
            yaxis_title="Count"
        )
        fig2.update_xaxes(tickfont={"color": CHART_TICK}, gridcolor=CHART_GRID)
        fig2.update_yaxes(tickfont={"color": CHART_TICK}, gridcolor=CHART_GRID)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### All Logged Predictions")
        display_df = hist_df.drop(columns=["id"]).rename(columns={
            "timestamp": "Time",       "tenure":     "Tenure",
            "monthly":   "Monthly(₹)", "contract":   "Contract",
            "internet":  "Internet",   "churn_prob": "Churn %",
            "risk_tier": "Risk Tier"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        dl_col, clr_col = st.columns([3, 1])
        with dl_col:
            st.download_button(
                "⬇️ Download History CSV",
                hist_df.to_csv(index=False),
                "prediction_history.csv",
                "text/csv"
            )
        with clr_col:
            if st.button("🗑️ Clear History"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM predictions")
                conn.commit()
                conn.close()
                st.success("History cleared.")
                st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;color:{MUTED};font-size:13px;padding-bottom:20px;">
  Churn Intelligence Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Scikit-Learn
  &nbsp;·&nbsp; <strong style="color:{TEAL_LIGHT if dark else BLUE_DEEP};">Developed by Mahreen Begum</strong>
</div>
""", unsafe_allow_html=True)
