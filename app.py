"""
MySpeedTest - Premium Commercial SaaS Internet Speed Test Platform
100% Python • Streamlit • Plotly • SQLite • Custom Multi-Threaded Engine
Exact recreation of modern SaaS neumorphic speedtest dashboard
Engineered & Developed by Mohsin
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import math
import base64
from typing import Dict, Any, List, Optional

# Backend modules
import network_info
import speed_engine
import history_manager

# Page Configuration: Full width modern SaaS layout
st.set_page_config(
    page_title="MySpeedTest | Test. Track. Share.",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Database
history_manager.init_db()

# Session State Initialization
if "engine" not in st.session_state:
    st.session_state.engine = speed_engine.SpeedTestEngine()

if "is_testing" not in st.session_state:
    st.session_state.is_testing = False

if "last_results" not in st.session_state:
    st.session_state.last_results = None

if "network_info" not in st.session_state:
    st.session_state.network_info = network_info.get_client_network_info()

if "selected_server" not in st.session_state:
    # Default to global fastest Anycast edge immediately to prevent blocking initial page load
    st.session_state.selected_server = network_info.DEFAULT_SERVERS[0]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "speedtest"


# ==========================================
# EXACT SAAS NEUMORPHIC THEME CSS
# ==========================================
SAAS_THEME_CSS = """
<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css");
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");

/* Clean Streamlit reset */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Airy Neumorphic SaaS Light Background */
.stApp {
    background: #f2f5fc !important;
    color: #1e293b !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Page constraint */
.block-container {
    max-width: 1440px !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    margin: 0 auto !important;
}

/* Sidebar Brand */
.sidebar-logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 8px 24px 8px;
}
.sidebar-logo-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: linear-gradient(135deg, #1e6bfb 0%, #3b82f6 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 800;
    box-shadow: 0 6px 16px rgba(30, 107, 251, 0.35);
}
.sidebar-logo-title {
    font-size: 1.35rem;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.sidebar-logo-tag {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 500;
    margin-top: 2px;
}

/* Left sidebar navigation buttons */
div[data-testid="column"]:first-child div.stButton > button {
    border-radius: 12px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 16px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin-bottom: 4px !important;
}
div[data-testid="column"]:first-child div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
}
div[data-testid="column"]:first-child div.stButton > button[kind="secondary"]:hover {
    background: #f8faff !important;
    border-color: #1e6bfb !important;
    color: #1e6bfb !important;
}
div[data-testid="column"]:first-child div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e6bfb 0%, #3b82f6 100%) !important;
    background-color: #1e6bfb !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(30, 107, 251, 0.35) !important;
}

/* Rocket Promo Card in Sidebar */
.rocket-card {
    background: linear-gradient(180deg, #f8faff 0%, #edf3fc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 24px 18px;
    text-align: center;
    margin-top: 36px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.rocket-icon-circle {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: #dbeafe;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 14px auto;
    font-size: 1.4rem;
    color: #1e6bfb;
}
.rocket-title {
    font-size: 0.95rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.3;
    margin-bottom: 4px;
}
.rocket-sub {
    font-size: 0.78rem;
    color: #64748b;
    margin-bottom: 16px;
}
.rocket-btn-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 50px;
    background: #1e6bfb;
    color: #ffffff;
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(30, 107, 251, 0.25);
}

/* Top Pill Bar */
.top-pill-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0 16px 0;
}
.pill-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
.dot-green {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
}

/* Main Speed Title */
.main-speed-title-box {
    text-align: center;
    margin-bottom: 16px;
}
.main-speed-title {
    font-size: 1.75rem;
    font-weight: 900;
    color: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    letter-spacing: -0.5px;
}
.main-speed-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-top: 4px;
}

/* Metric Wave Cards (Download & Upload) */
.metric-side-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 24px 16px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.03);
    height: 280px;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
}
.icon-circle-download {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #e6fcf5;
    color: #12b886;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 800;
    margin: 0 auto 10px auto;
}
.icon-circle-upload {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #f3e8ff;
    color: #a855f7;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 800;
    margin: 0 auto 10px auto;
}
.metric-side-label {
    font-size: 0.92rem;
    font-weight: 700;
    color: #475569;
}
.metric-side-value {
    font-size: 2.3rem;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1.1;
    margin: 6px 0 2px 0;
}
.metric-side-unit {
    font-size: 0.85rem;
    color: #94a3b8;
    font-weight: 600;
}

/* Waves rendered via clean CSS data URIs */
.wave-green {
    height: 20px;
    width: 100%;
    margin-top: auto;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 20'%3E%3Cpath d='M0 10 Q25 0 50 10 T100 10' fill='none' stroke='%2312b886' stroke-width='2.5' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat center;
    background-size: 100% 100%;
}
.wave-purple {
    height: 20px;
    width: 100%;
    margin-top: auto;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 20'%3E%3Cpath d='M0 10 Q25 20 50 10 T100 10' fill='none' stroke='%23a855f7' stroke-width='2.5' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat center;
    background-size: 100% 100%;
}

/* Center Speedometer Neumorphic Box */
.gauge-card-box {
    background: #ffffff;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 20px rgba(0,0,0,0.03);
    height: 280px;
    min-height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    box-sizing: border-box;
    overflow: hidden;
}

/* Ping & Jitter Pills Under Gauge */
.sub-metrics-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 16px 0;
}
.sub-metric-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 24px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 50px;
    font-size: 0.92rem;
    font-weight: 700;
    color: #1e293b;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

/* Buttons */
div.stButton > button {
    border-radius: 50px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.25s ease !important;
}
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #1e6bfb 0%, #3b82f6 100%) !important;
    background-color: #1e6bfb !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(30, 107, 251, 0.35) !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(30, 107, 251, 0.45) !important;
}
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}
div.stButton > button[kind="secondary"]:hover,
div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}

/* Right Panel Cards */
.panel-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.03);
    margin-bottom: 18px;
}
.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.95rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}
.panel-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.85rem;
}
.panel-row:last-child {
    border-bottom: none;
}
.panel-row-label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #64748b;
    font-weight: 600;
}
.panel-row-val {
    color: #0f172a;
    font-weight: 700;
    text-align: right;
    max-width: 170px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Recent Tests Mini Table */
.recent-table-header {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
}
.recent-table-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    font-size: 0.8rem;
    padding: 9px 0;
    border-bottom: 1px solid #f8fafc;
    align-items: center;
    color: #334155;
    font-weight: 600;
}

/* Trust Badge Card */
.trust-badge-card {
    background: linear-gradient(135deg, #e8fbf4 0%, #f0fdf9 100%);
    border: 1px solid #bbf7d0;
    border-radius: 18px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.trust-icon {
    font-size: 1.6rem;
    color: #10b981;
}
.trust-title {
    font-size: 0.88rem;
    font-weight: 800;
    color: #065f46;
}
.trust-sub {
    font-size: 0.75rem;
    color: #047857;
}

/* Footer Credits */
.footer-credits-box {
    text-align: center;
    padding: 24px 0 10px 0;
    margin-top: 36px;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 0.86rem;
}
.footer-highlight {
    color: #1e6bfb;
    font-weight: 800;
}
</style>
"""
st.html(SAAS_THEME_CSS)


# ==========================================
# EXACT VECTOR SPEEDOMETER (BASE64 SVG - IMMUNE TO DOMPURIFY)
# ==========================================
def map_speed_to_deg(val: float) -> float:
    """Non-linear dial mapping matching exact reference image ticks."""
    val = float(val)
    if val <= 0:
        return 210.0
    if val <= 10.0:
        return 210.0 - (val / 10.0) * 30.0
    if val <= 25.0:
        return 180.0 - ((val - 10.0) / 15.0) * 35.0
    if val <= 50.0:
        return 145.0 - ((val - 25.0) / 25.0) * 35.0
    if val <= 100.0:
        return 110.0 - ((val - 50.0) / 50.0) * 40.0
    if val <= 250.0:
        return 70.0 - ((val - 100.0) / 150.0) * 35.0
    if val <= 500.0:
        return 35.0 - ((val - 250.0) / 250.0) * 60.0
    return -25.0


def build_speedometer_html(speed: float) -> str:
    """
    Constructs the exact smooth gradient gauge from the reference screenshot
    and Yudiz-style animated speedometer (with Mbps units).
    Encoded as Base64 SVG img to prevent Streamlit DOMPurify stripping SVG tags.
    """
    val = float(speed)
    deg = map_speed_to_deg(val)
    rad = math.radians(deg)
    cx, cy, r = 200, 132, 105

    # Background Arc (210° to -30°, 240° sweep)
    x1 = cx + r * math.cos(math.radians(210))
    y1 = cy - r * math.sin(math.radians(210))
    x2 = cx + r * math.cos(math.radians(-30))
    y2 = cy - r * math.sin(math.radians(-30))
    bg_arc = f"M {x1:.1f} {y1:.1f} A {r} {r} 0 1 1 {x2:.1f} {y2:.1f}"

    # Swept progress arc
    swept = 210.0 - deg
    if swept > 0.5:
        cur_x = cx + r * math.cos(rad)
        cur_y = cy - r * math.sin(rad)
        large_arc = 1 if swept > 180 else 0
        active_arc = f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large_arc} 1 {cur_x:.1f} {cur_y:.1f}" fill="none" stroke="url(#speedGrad)" stroke-width="14" stroke-linecap="round"/>'
    else:
        active_arc = ""

    # Needle
    tip_len = 66
    tip_x = cx + tip_len * math.cos(rad)
    tip_y = cy - tip_len * math.sin(rad)
    perp = rad + math.pi / 2
    bx1 = cx + 4.5 * math.cos(perp)
    by1 = cy - 4.5 * math.sin(perp)
    bx2 = cx - 4.5 * math.cos(perp)
    by2 = cy + 4.5 * math.sin(perp)
    tail_x = cx - 7.0 * math.cos(rad)
    tail_y = cy + 7.0 * math.sin(rad)
    needle = f'<polygon points="{tip_x:.1f},{tip_y:.1f} {bx1:.1f},{by1:.1f} {tail_x:.1f},{tail_y:.1f} {bx2:.1f},{by2:.1f}" fill="#1e293b"/>'

    # Ticks matching reference image: 0, 10, 25, 50, 100, 250, 500+
    ticks = [(0, "0", 210), (10, "10", 180), (25, "25", 145), (50, "50", 110), (100, "100", 70), (250, "250", 35), (500, "500+", -25)]
    t_svg = []
    r_text = 82
    for _, tl, td in ticks:
        tx = cx + r_text * math.cos(math.radians(td))
        ty = cy - r_text * math.sin(math.radians(td))
        t_svg.append(f'<text x="{tx:.1f}" y="{ty:.1f}" fill="#64748b" font-size="11" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="Inter, sans-serif">{tl}</text>')

    ticks_markup = "".join(t_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" width="100%" height="240">
<defs>
    <linearGradient id="speedGrad" x1="0%" y1="100%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#00c6ff"/>
        <stop offset="30%" stop-color="#3b82f6"/>
        <stop offset="65%" stop-color="#8b5cf6"/>
        <stop offset="100%" stop-color="#d946ef"/>
    </linearGradient>
</defs>
<!-- Gradient Background Arc (always visible with 0.28 opacity) -->
<path d="{bg_arc}" fill="none" stroke="url(#speedGrad)" stroke-width="14" stroke-linecap="round" opacity="0.28"/>
<!-- Bright Active Progress Arc -->
{active_arc}
{ticks_markup}
{needle}
<circle cx="{cx}" cy="{cy}" r="7.5" fill="#1e293b"/>
<circle cx="{cx}" cy="{cy}" r="2.5" fill="#ffffff"/>
<text x="{cx}" y="{cy + 44}" fill="#0f172a" font-size="38" font-weight="900" text-anchor="middle" font-family="Inter, sans-serif" letter-spacing="-1px">{val:.2f}</text>
<text x="{cx}" y="{cy + 64}" fill="#64748b" font-size="13" font-weight="700" text-anchor="middle" font-family="Inter, sans-serif">Mbps</text>
</svg>"""

    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<div class="gauge-card-box"><img src="data:image/svg+xml;base64,{b64}" style="width:100%; max-width:380px; height:auto; display:block; margin:0 auto;" alt="speedometer" /></div>'


def build_speed_graph_plotly(dl_samples: List[float], ul_samples: List[float]) -> go.Figure:
    """Exact clean white speed graph with blue and purple spline curves matching reference."""
    fig = go.Figure()
    if dl_samples:
        x_dl = [round(i * 0.08, 2) for i in range(len(dl_samples))]
        fig.add_trace(go.Scatter(
            x=x_dl,
            y=dl_samples,
            mode="lines",
            name="Download",
            line=dict(color="#1e6bfb", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(30, 107, 251, 0.07)"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=[0, 1, 2, 3, 4, 5],
            y=[0, 0, 0, 0, 0, 0],
            mode="lines",
            name="Download",
            line=dict(color="#f1f5f9", width=1)
        ))

    if ul_samples:
        x_ul = [round(i * 0.08, 2) for i in range(len(ul_samples))]
        fig.add_trace(go.Scatter(
            x=x_ul,
            y=ul_samples,
            mode="lines",
            name="Upload",
            line=dict(color="#a855f7", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(168, 85, 247, 0.07)"
        ))

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 500], tickvals=[0, 250, 500], color="#94a3b8"),
        margin=dict(l=35, r=20, t=10, b=25),
        height=165,
        showlegend=False
    )
    return fig


# ==========================================
# 3-COLUMN MASTER DASHBOARD LAYOUT
# ==========================================
net = st.session_state.network_info
srv = st.session_state.selected_server
lr = st.session_state.last_results

col_left, col_center, col_right = st.columns([1.3, 3.4, 1.8], gap="large")


# ------------------------------------------
# COLUMN 1: LEFT NAVIGATION SIDEBAR
# ------------------------------------------
with col_left:
    st.html("""
    <div class="sidebar-logo-container">
        <div class="sidebar-logo-icon"><i class="fa-solid fa-gauge-high"></i></div>
        <div>
            <div class="sidebar-logo-title">MySpeedTest</div>
            <div class="sidebar-logo-tag">Test. Track. Share.</div>
        </div>
    </div>
    """)

    # Nav Menu
    p_active = st.session_state.nav_page

    if st.button("Speed Test", key="nav_speedtest", type="primary" if p_active == "speedtest" else "secondary", use_container_width=True):
        st.session_state.nav_page = "speedtest"
        st.rerun()

    if st.button("History", key="nav_history", type="primary" if p_active == "history" else "secondary", use_container_width=True):
        st.session_state.nav_page = "history"
        st.rerun()

    if st.button("Settings", key="nav_settings", type="primary" if p_active == "settings" else "secondary", use_container_width=True):
        st.session_state.nav_page = "settings"
        st.rerun()

    if st.button("About", key="nav_about", type="primary" if p_active == "about" else "secondary", use_container_width=True):
        st.session_state.nav_page = "about"
        st.rerun()

    # Rocket Promo Card
    st.html("""
    <div class="rocket-card">
        <div class="rocket-icon-circle"><i class="fa-solid fa-rocket"></i></div>
        <div class="rocket-title">Get the best internet experience</div>
        <div class="rocket-sub">Fast. Reliable. Always.</div>
        <div class="rocket-btn-badge">Start Test &rarr;</div>
    </div>
    """)


# ------------------------------------------
# COLUMN 2: CENTER STAGE (THE STAR)
# ------------------------------------------
with col_center:
    # 1. Top Pills Bar
    location_str = f"{net.get('city', 'Detecting...')}, {net.get('country', '')}".strip(", ")
    st.html(f"""
    <div class="top-pill-bar">
        <div style="display:flex; gap:10px;">
            <div class="pill-chip">
                <span class="dot-green"></span>
                <span><i class="fa-solid fa-server" style="color:#64748b; margin-right:4px;"></i> Server: Auto Select</span>
            </div>
            <div class="pill-chip">
                <span><i class="fa-solid fa-location-dot" style="color:#ef4444; margin-right:4px;"></i> Location: {location_str}</span>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            <div class="pill-chip" style="cursor:pointer;">
                <span><i class="fa-solid fa-sun" style="color:#f59e0b; margin-right:4px;"></i> <i class="fa-solid fa-moon" style="color:#64748b;"></i></span>
            </div>
            <div class="pill-chip" style="cursor:pointer; color:#1e6bfb;">
                <span><i class="fa-solid fa-share-nodes" style="margin-right:4px;"></i> Share Results</span>
            </div>
        </div>
    </div>
    """)

    if st.session_state.nav_page == "speedtest":
        # 2. Main Title
        st.html("""
        <div class="main-speed-title-box">
            <div class="main-speed-title">
                <i class="fa-solid fa-wifi" style="color:#1e6bfb;"></i>
                <span>Internet Speed Test</span>
            </div>
            <div class="main-speed-sub">Check your download, upload speed and network performance</div>
        </div>
        """)

        # 3. Flanking Metric Cards + In-Place DOM Vector Speedometer
        cur_dl = f"{lr['download_mbps']:.2f}" if lr else "0.00"
        cur_ul = f"{lr['upload_mbps']:.2f}" if lr else "0.00"
        cur_speed = lr["download_mbps"] if lr else 0.0
        cur_ping = f"{lr['ping_ms']:.0f}" if lr else "--"
        cur_jitter = f"{lr['jitter_ms']:.0f}" if lr else "--"

        card_col1, card_col2, card_col3 = st.columns([1, 2.1, 1], gap="medium")

        dl_box_ph = card_col1.empty()
        gauge_ph = card_col2.empty()
        ul_box_ph = card_col3.empty()

        def render_download_card(val: str):
            dl_box_ph.html(f"""
            <div class="metric-side-card">
                <div>
                    <div class="icon-circle-download"><i class="fa-solid fa-arrow-down"></i></div>
                    <div class="metric-side-label">Download</div>
                    <div class="metric-side-value">{val}</div>
                    <div class="metric-side-unit">Mbps</div>
                </div>
                <div class="wave-green"></div>
            </div>
            """)

        def render_upload_card(val: str):
            ul_box_ph.html(f"""
            <div class="metric-side-card">
                <div>
                    <div class="icon-circle-upload"><i class="fa-solid fa-arrow-up"></i></div>
                    <div class="metric-side-label">Upload</div>
                    <div class="metric-side-value">{val}</div>
                    <div class="metric-side-unit">Mbps</div>
                </div>
                <div class="wave-purple"></div>
            </div>
            """)

        # Initial Render
        render_download_card(cur_dl)
        render_upload_card(cur_ul)
        gauge_ph.html(build_speedometer_html(cur_speed))

        # 4. Ping and Jitter Pills (FontAwesome Icons, No Emojis)
        sub_pills_ph = st.empty()
        def render_sub_pills(p_val="--", j_val="--"):
            sub_pills_ph.html(f"""
            <div class="sub-metrics-row">
                <div class="sub-metric-pill">
                    <i class="fa-solid fa-bolt" style="color:#1e6bfb; font-size:1.05rem;"></i>
                    <span style="color:#64748b;">Ping</span>
                    <span>{p_val} ms</span>
                </div>
                <div class="sub-metric-pill">
                    <i class="fa-solid fa-chart-line" style="color:#a855f7; font-size:1.05rem;"></i>
                    <span style="color:#64748b;">Jitter</span>
                    <span>{j_val} ms</span>
                </div>
            </div>
            """)
        render_sub_pills(p_val=cur_ping, j_val=cur_jitter)

        # 5. Buttons: Start Test & Stop Test
        b_c1, b_c2 = st.columns([1, 1])
        with b_c1:
            start_btn = st.button("Start Test", key="btn_start_main", type="primary", use_container_width=True)
        with b_c2:
            stop_btn = st.button("Stop Test", key="btn_stop_main", type="secondary", use_container_width=True)

        if stop_btn and st.session_state.is_testing:
            st.session_state.engine.stop()
            st.session_state.is_testing = False
            st.warning("Benchmark stopped by user.")

        # 6. Bottom Speed Graph Card
        st.html("""
        <div style="background:#ffffff; border-radius:20px; padding:18px 22px 10px 22px; border:1px solid #e2e8f0; box-shadow:0 8px 20px rgba(0,0,0,0.03); margin-top:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-size:0.95rem; font-weight:800; color:#0f172a; display:flex; align-items:center; gap:8px;">
                    <i class="fa-solid fa-chart-line" style="color:#1e6bfb;"></i>
                    <span>Speed Graph</span>
                </div>
                <div style="font-size:0.8rem; font-weight:700; color:#64748b; display:flex; gap:16px;">
                    <span><i class="fa-solid fa-circle" style="color:#1e6bfb; font-size:9px; margin-right:4px;"></i> Download</span>
                    <span><i class="fa-solid fa-circle" style="color:#a855f7; font-size:9px; margin-right:4px;"></i> Upload</span>
                </div>
            </div>
        """)
        chart_ph = st.empty()
        chart_ph.plotly_chart(
            build_speed_graph_plotly(
                lr.get("download_samples", []) if lr else [],
                lr.get("upload_samples", []) if lr else []
            ),
            width="stretch",
            key="saas_live_speed_graph"
        )
        st.html("</div>")

        # ==========================================
        # SPEED TEST EXECUTION LOOP (SMOOTH & ZERO SHUTTER)
        # ==========================================
        if start_btn and not st.session_state.is_testing:
            st.session_state.is_testing = True
            engine = st.session_state.engine
            target_server = st.session_state.selected_server

            def on_ping_cb(sample_ms, ping_v, jitter_v, prog):
                render_sub_pills(p_val=f"{ping_v:.0f}", j_val=f"{jitter_v:.0f}")
                gauge_ph.html(build_speedometer_html(0.0))

            def on_dl_cb(inst_mbps, avg_mbps, peak_mbps, prog, samples):
                render_download_card(f"{inst_mbps:.2f}")
                gauge_ph.html(build_speedometer_html(inst_mbps))

            def on_ul_cb(inst_mbps, avg_mbps, peak_mbps, prog, samples):
                render_upload_card(f"{inst_mbps:.2f}")
                gauge_ph.html(build_speedometer_html(inst_mbps))

            results = engine.run_full_test(
                server=target_server,
                on_ping_update=on_ping_cb,
                on_download_update=on_dl_cb,
                on_upload_update=on_ul_cb
            )

            st.session_state.is_testing = False

            if not results.get("aborted") and not results.get("error"):
                st.session_state.last_results = results
                history_manager.save_test_result(
                    download_mbps=results["download_mbps"],
                    upload_mbps=results["upload_mbps"],
                    ping_ms=results["ping_ms"],
                    jitter_ms=results["jitter_ms"],
                    peak_download=results.get("peak_download", results["download_mbps"]),
                    peak_upload=results.get("peak_upload", results["upload_mbps"]),
                    ip_address=net.get("ip", "Unknown"),
                    isp=net.get("isp", "Unknown"),
                    server_name=target_server.get("name", "Unknown"),
                    server_location=target_server.get("location", "Unknown")
                )
                chart_ph.plotly_chart(
                    build_speed_graph_plotly(results.get("download_samples", []), results.get("upload_samples", [])),
                    width="stretch"
                )
                render_download_card(f"{results['download_mbps']:.2f}")
                render_upload_card(f"{results['upload_mbps']:.2f}")
                gauge_ph.html(build_speedometer_html(results['download_mbps']))
                st.balloons()
                st.rerun()

    elif st.session_state.nav_page == "history":
        st.markdown("### <i class='fa-solid fa-chart-simple' style='color:#1e6bfb;'></i> **Complete Speed Test History**", unsafe_allow_html=True)
        stats = history_manager.get_summary_stats()
        s_c1, s_c2, s_c3, s_c4 = st.columns(4)
        s_c1.metric("Total Tests", stats["total_tests"])
        s_c2.metric("Avg Download", f"{stats['avg_download']} Mbps")
        s_c3.metric("Avg Upload", f"{stats['avg_upload']} Mbps")
        s_c4.metric("Lowest Ping", f"{stats['lowest_ping']} ms")

        all_hist = history_manager.get_all_history()
        if not all_hist.empty:
            st.dataframe(all_hist, use_container_width=True, hide_index=True)

            d_c1, d_c2 = st.columns([2, 1])
            with d_c1:
                del_id = st.selectbox("Select Record ID to Delete", options=all_hist["id"].tolist())
                if st.button("Delete Selected Record", key="btn_del_rec", type="secondary"):
                    history_manager.delete_test_record(del_id)
                    st.success(f"Record #{del_id} deleted successfully.")
                    st.rerun()
            with d_c2:
                st.download_button(
                    "Export Full History (CSV)",
                    data=history_manager.export_csv_data(),
                    file_name="myspeedtest_full_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("No speed test history recorded yet.")

    elif st.session_state.nav_page == "settings":
        st.markdown("### <i class='fa-solid fa-gear' style='color:#1e6bfb;'></i> **Testing Server Configuration**", unsafe_allow_html=True)
        all_servers = network_info.get_available_servers()
        s_names = [f"{s['name']} ({s['location']})" for s in all_servers]
        picked_server = st.selectbox("Active Server", options=s_names)
        st.session_state.selected_server = all_servers[s_names.index(picked_server)]
        st.success(f"Connected to {st.session_state.selected_server['name']}")

    elif st.session_state.nav_page == "about":
        st.markdown("### <i class='fa-solid fa-circle-info' style='color:#1e6bfb;'></i> **About MySpeedTest**", unsafe_allow_html=True)
        st.markdown("""
        **MySpeedTest** is an open-source, production-grade broadband telemetry platform built 100% in Python.
        - **RFC 3550 Standard Jitter Analysis**
        - **Zero Simulation Guarantee:** 100% genuine multi-stream chunk socket transfers
        - **SQLite Data Persistence**
        """)


# ------------------------------------------
# COLUMN 3: RIGHT SIDEBAR (Network & Tests)
# ------------------------------------------
with col_right:
    # 1. Network Information Card
    ip_str = net.get("ip", "Detecting...")
    isp_str = net.get("isp", "--")
    loc_str = f"{net.get('city', '--')}, {net.get('country', '')}".strip(", ")
    srv_str = srv.get("name", "--")

    st.html(f"""
    <div class="panel-card">
        <div class="panel-header">
            <span style="display:flex; align-items:center; gap:10px;">
                <i class="fa-solid fa-network-wired" style="color:#1e6bfb; font-size:1.1rem;"></i> Network Information
            </span>
            <i class="fa-solid fa-signal" style="color:#10b981;"></i>
        </div>
        <div class="panel-row">
            <div class="panel-row-label"><i class="fa-solid fa-globe"></i> IP Address</div>
            <div class="panel-row-val">{ip_str}</div>
        </div>
        <div class="panel-row">
            <div class="panel-row-label"><i class="fa-solid fa-building"></i> ISP</div>
            <div class="panel-row-val" title="{isp_str}">{isp_str}</div>
        </div>
        <div class="panel-row">
            <div class="panel-row-label"><i class="fa-solid fa-location-dot"></i> Location</div>
            <div class="panel-row-val">{loc_str}</div>
        </div>
        <div class="panel-row">
            <div class="panel-row-label"><i class="fa-solid fa-server"></i> Selected Server</div>
            <div class="panel-row-val" title="{srv_str}">{srv_str}</div>
        </div>
        <div class="panel-row">
            <div class="panel-row-label"><i class="fa-solid fa-ethernet"></i> Connection Type</div>
            <div class="panel-row-val">Broadband</div>
        </div>
    </div>
    """)

    # 2. Recent Tests Card
    recent_df = history_manager.get_all_history().head(4)
    rows_markup = []
    if not recent_df.empty:
        for _, r_data in recent_df.iterrows():
            ts = r_data["timestamp"]
            date_short = ts.split(" ")[0] if " " in ts else ts
            rows_markup.append(f"""
            <div class="recent-table-row">
                <div style="font-size:0.75rem;">{date_short}</div>
                <div style="color:#1e6bfb;"><i class="fa-solid fa-arrow-down" style="font-size:10px; margin-right:2px;"></i> {r_data['download_mbps']:.0f}</div>
                <div style="color:#a855f7;"><i class="fa-solid fa-arrow-up" style="font-size:10px; margin-right:2px;"></i> {r_data['upload_mbps']:.0f}</div>
                <div>{r_data['ping_ms']:.0f} ms</div>
            </div>
            """)
    else:
        rows_markup.append("<div style='color:#94a3b8; font-size:0.8rem; padding:12px 0; text-align:center;'>No test history yet</div>")

    st.html(f"""
    <div class="panel-card">
        <div class="panel-header">
            <span style="display:flex; align-items:center; gap:10px;">
                <i class="fa-solid fa-clock-rotate-left" style="color:#1e6bfb; font-size:1.1rem;"></i> Recent Tests
            </span>
            <span style="color:#1e6bfb; font-size:0.82rem; font-weight:700; cursor:pointer;">View All <i class="fa-solid fa-arrow-right" style="font-size:10px; margin-left:3px;"></i></span>
        </div>
        <div class="recent-table-header">
            <div>Date</div>
            <div>Download</div>
            <div>Upload</div>
            <div>Ping</div>
        </div>
        {''.join(rows_markup)}
    </div>
    """)

    # 3. Trust Badge Card
    st.html("""
    <div class="trust-badge-card">
        <div class="trust-icon"><i class="fa-solid fa-shield-halved"></i></div>
        <div>
            <div class="trust-title">Fast • Secure • Reliable</div>
            <div class="trust-sub">Your internet performance, in real time.</div>
        </div>
    </div>
    """)


# ==========================================
# FOOTER CREDITS (ENGINEERED BY MOHSIN)
# ==========================================
st.html("""
<div class="footer-credits-box">
    <div>Designed & Engineered with <i class="fa-solid fa-heart" style="color:#ef4444; margin:0 4px;"></i> by <span class="footer-highlight">Mohsin</span></div>
    <div style="font-size:0.78rem; color:#94a3b8; margin-top:5px;">
        MySpeedTest SaaS Platform • 100% Python Engine • RFC 3550 Standard Jitter • <i class="fa-brands fa-github" style="margin-left:4px;"></i> <b>@csibmohsin</b>
    </div>
</div>
""")
