"""
================================================================================
MODULE: app.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.2.0-CORE-ONLINE
THEME: CYBERPUNK HUD
DESCRIPTION: 
    Main entry point. Orchestrates Data, Logic, AI, and UI components.
    Features:
    - Secure Access Layer (Login)
    - Real-time System Logs
    - Modular Tab Architecture
    - Embedded TradingView & Plotly Engines
================================================================================
"""

import streamlit as st
import sys
import os
import time
import pandas as pd
import streamlit.components.v1 as components

# 1. SYSTEM BOOTSTRAP (Cấu hình khởi động)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    layout="wide", 
    page_title="TL-TERMINAL V36.2", 
    page_icon="💠",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Thang Long Terminal - Advanced Market Intelligence"
    }
)

# 2. MODULE IMPORT (Kèm xử lý lỗi)
try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full, get_market_indices
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36, analyze_fundamental
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_interactive_chart, render_market_overview, render_analysis_section
except ImportError as e:
    st.error(f"❌ SYSTEM CRITICAL ERROR: MISSING MODULES. {e}")
    st.stop()

# ==============================================================================
# 3. SECURE LOGIN LAYER (Màn hình đăng nhập Cyberpunk)
# ==============================================================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

def render_secure_login():
    # Inject CSS riêng cho trang Login
    st.markdown("""
    <style>
        .login-box {
            max-width: 400px; margin: 100px auto; padding: 40px;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00f3ff;
            box-shadow: 0 0 50px rgba(0, 243, 255, 0.2);
            text-align: center;
            border-radius: 10px;
            position: relative;
        }
        .login-title {
            font-family: 'Rajdhani', sans-serif; font-size: 32px; font-weight: 800; color: #fff;
            text-shadow: 0 0 10px #00f3ff; letter-spacing: 4px; margin-bottom: 20px;
        }
        .stTextInput input {
            text-align: center; color: #00f3ff !important; border-color: #333 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="login-box">
        <div class="login-title">SYSTEM ACCESS</div>
        <div style="color: #555; font-size: 12px; margin-bottom: 20px;">RESTRICTED AREA // LEVEL 5 CLEARANCE</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.form("login_form"):
            user = st.text_input("IDENTITY", placeholder="USER_ID")
            pwd = st.text_input("KEY_PHRASE", type="password", placeholder="ACCESS_CODE")
            
            if st.form_submit_button("INITIATE UPLINK", type="primary", use_container_width=True):
                # Fake loading effect
                with st.spinner("VERIFYING BIOMETRICS..."):
                    time.sleep(1)
                
                if (user == "admin" and pwd == "admin123") or (user == "stock" and pwd == "stock123"):
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("⛔ ACCESS DENIED: INVALID CREDENTIALS")

if not st.session_state['logged_in']:
    load_hardcore_css() # Load font cho trang login
    render_secure_login()
    st.stop()

# ==============================================================================
# 4. MAIN COMMAND CENTER (Giao diện chính)
# ==============================================================================

# Khởi động giao diện
load_hardcore_css()
render_header()

# --- SIDEBAR: SYSTEM CONTROL ---
with st.sidebar:
    st.markdown("### 🎛️ SYSTEM CONTROL")
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px; background:#111; padding:10px; border:1px solid #333;">
        <div style="width:10px; height:10px; background:#00ff41; border-radius:50%; box-shadow:0 0 5px #00ff41;"></div>
        <div style="color:#00ff41; font-family:Rajdhani; font-weight:700;">ONLINE</div>
        <div style="color:#555; font-size:10px; margin-left:auto;">LATENCY: 12ms</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📡 TARGET SCANNER")
    default_list = "HPG, SSI, FPT, MWG, VCB, STB, DIG, NVL, PDR, VIX, DGC, VND"
    user_tickers = st.text_area("WATCHLIST INPUT", value=default_list, height=100, help="Enter symbols separated by comma")
    
    if st.button("EXECUTE SCAN", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    
    # System Log Simulation
    with st.expander("SYSTEM LOGS", expanded=True):
        st.markdown("""
        <div style="font-family:monospace; font-size:10px; color:#555; height:150px; overflow-y:auto;">
            > SYS_INIT... OK<br>
            > CONNECTING TO DATA FEED... OK<br>
            > LOADING NEURAL NETS... OK<br>
            > DECRYPTING STREAM... OK<br>
            > READY FOR INPUT_<br>
            <span style="color:#00f3ff; animation: blink 1s infinite;">_</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("TERMINATE SESSION"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- MARKET TAPE ---
with st.spinner("ESTABLISHING DATA LINK..."):
    indices = get_market_indices()
    render_market_overview(indices)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# --- DUAL PANE LAYOUT ---
col_radar, col_analyst = st.columns([1.5, 2.5])

# === LEFT PANE: RADAR ===
with col_radar:
    st.markdown('<div class="glass-box"><h4>📡 MARKET RADAR</h4>', unsafe_allow_html=True)
    
    ticker_list = [t.strip().upper() for t in user_tickers.split(',') if t.strip()]
    
    with st.spinner("SCANNING SECTOR..."):
        df_radar = get_pro_data(ticker_list)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("SYM", width="small"),
                "Price": st.column_config.NumberColumn("PX (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("% CHG", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("ALGO"),
                "Score": st.column_config.ProgressColumn("STR", format="%d", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("TREND"),
            },
            hide_index=True, use_container_width=True, height=680
        )
    else:
        st.warning("NO TARGETS FOUND.")
    st.markdown('</div>', unsafe_allow_html=True)

# === RIGHT PANE: ANALYST CENTER ===
with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    if not df_radar.empty:
        selected = st.selectbox("SELECT TARGET", df_radar['Symbol'])
        
        st.markdown(f"<h1 style='color:#00f3ff; margin-top:-10px; font-family:Rajdhani; text-shadow:0 0 10px #00f3ff;'>{selected} // DEEP DIVE</h1>", unsafe_allow_html=True)
        
        # Load Data
        hist_df = get_history_df(selected)
        info, fin, bal, cash, divs, splits = get_stock_data_full(selected)
        
        # Analyze
        tech_res = analyze_smart_v36(hist_df)
        fund_res = analyze_fundamental(info, fin)

        if tech_res and fund_res:
            render_analysis_section(tech_res, fund_res)
        
        st.markdown("---")

        # TABS
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "CHART", "TRADINGVIEW", "AI_PROPHET", "MONTE_CARLO", "NEWS_FEED", "FINANCIALS", "PROFILE"
        ])
        
        # TAB 1: INTERACTIVE CHART (ZOOM/PAN)
        with t1:
            render_interactive_chart(hist_df, selected)

        # TAB 2: TRADINGVIEW EMBED
        with t2:
            st.markdown("### EXTERNAL DATA FEED")
            components.html(f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                  "width": "100%", "height": 550,
                  "symbol": "HOSE:{selected}",
                  "interval": "D", "timezone": "Asia/Ho_Chi_Minh",
                  "theme": "dark", "style": "1", "locale": "en",
                  "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                  "allow_symbol_change": true, "container_id": "tradingview_widget"
              }});
              </script>
            </div>
            """, height=560)

       # TAB 3: PROPHET FORECAST
        with t3:
            st.markdown("### 🔮 NEURAL NETWORK FORECAST (60 DAYS)")
            if st.button("INITIATE AI MODEL", type="primary"):
                with st.spinner("TRAINING MODELS..."):
                    fig_ai = run_prophet_ai(hist_df)
                    if fig_ai: 
                        # Thêm config scrollZoom=True ở đây
                        st.plotly_chart(fig_ai, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                    else: st.error("DATA INSUFFICIENT FOR PREDICTION.")

        # TAB 4: MONTE CARLO
        with t4:
            st.markdown("### 🌌 MULTIVERSE SIMULATION (1000 PATHS)")
            if st.button("RUN SIMULATION"):
                fig_mc, fig_hist, stats = run_monte_carlo(hist_df)
                if fig_mc:
                    st.plotly_chart(fig_mc, use_container_width=True)
                    # Cyber Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("EXPECTED MEAN", f"{stats['mean']:,.0f}")
                    m2.metric("BULL CASE (95%)", f"{stats['top_5']:,.0f}", delta="UPSIDE")
                    m3.metric("PROBABILITY > CURRENT", f"{stats['prob_up']:.1f}%")
                    st.plotly_chart(fig_hist, use_container_width=True)

        # TAB 5: NEWS
        with t5:
            news_list = get_stock_news_google(selected)
            if news_list:
                for n in news_list:
                    st.markdown(f"""
                    <div style="background:#0a0f14; padding:15px; border:1px solid #222; margin-bottom:10px; border-left: 2px solid #00f3ff;">
                        <a href="{n['link']}" target="_blank" style="color:#fff; font-weight:700; text-decoration:none; font-family:Rajdhani; font-size:18px;">{n['title']}</a>
                        <div style="color:#666; font-size:12px; margin-top:5px; text-transform:uppercase;">SOURCE: {n.get('source', 'UNKNOWN')} | {n['published']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 6: FINANCIALS
        with t6:
            if not fin.empty:
                st.subheader("INCOME STATEMENT (BILLION VND)")
                fin_display = fin.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(fin_display.style.format("{:,.1f}"), use_container_width=True)

        # TAB 7: PROFILE
        with t7:
            c_left, c_right = st.columns(2)
            with c_left:
                st.info(f"SECTOR: {info.get('sector', 'N/A').upper()}")
                st.info(f"EMPLOYEES: {info.get('fullTimeEmployees', 'N/A')}")
                st.caption(info.get('longBusinessSummary', 'NO DATA.'))
            with c_right:
                if not divs.empty:
                    st.markdown("### DIVIDEND YIELD")
                    div_data = divs.reset_index()
                    div_data.columns = ['DATE', 'VALUE']
                    st.bar_chart(div_data.set_index('DATE').head(10))

    st.markdown('</div>', unsafe_allow_html=True)

# 5. FOOTER
st.markdown("""
<div style="text-align:center; color:#444; font-size:10px; margin-top:50px; font-family:monospace;">
    THANG LONG TERMINAL SYSTEM V36.2 // ENCRYPTED CONNECTION ESTABLISHED
</div>
""", unsafe_allow_html=True)
