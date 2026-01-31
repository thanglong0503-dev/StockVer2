# Tìm dòng import backend/frontend và thêm vào:
from backend.data import get_pro_data, get_history_df, get_market_indices # <--- Thêm get_market_indices
from frontend.components import render_score_card_v36, render_interactive_chart, render_market_overview # <--- Thêm render_market_overview
import streamlit as st
import sys
import os

# CONFIG
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
st.set_page_config(layout="wide", page_title="Thang Long Terminal", page_icon="🐲")

# IMPORT
try:
    from backend.data import get_pro_data, get_history_df
    from backend.logic import analyze_smart_v36, analyze_fundamental_fake
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_score_card_v36, render_interactive_chart
except ImportError:
    st.error("System Error: Modules not found.")
    st.stop()

# MAIN UI
load_hardcore_css()
render_header()
# ... code cũ ...
load_hardcore_css()
render_header()

# --- KHU VỰC CHỈ SỐ THỊ TRƯỜNG (NEW) ---
with st.spinner("Updating Global Indices..."):
    market_data = get_market_indices()
    render_market_overview(market_data)

st.markdown("---") # Đường kẻ ngang phân cách cho đẹp

# --- INPUT ---
WATCHLIST = ...
# ... code cũ ...
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX"]

col_left, col_right = st.columns([1.8, 2.2])

# --- LEFT: MARKET RADAR ---
with col_left:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Rajdhani; margin-top:0;">📡 MARKET RADAR (LIVE)</h3>', unsafe_allow_html=True)
    
    with st.spinner("Scanning Market Data..."):
        df_radar = get_pro_data(WATCHLIST)
        
    if not df_radar.empty:
        # Cấu hình tiếng Anh cho bảng
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Ticker", width="small"),
                "Price": st.column_config.NumberColumn("Price (K)"),
                "Pct": st.column_config.NumberColumn("Change %", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Signal", width="medium"),
                "Score": st.column_config.ProgressColumn("Power", format="%d/10", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("Trend (30D)"),
                # Ẩn các cột phụ không cần thiết
                "Change": None, "RSI": None
            },
            hide_index=True, use_container_width=True, height=650
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: ANALYST CENTER ---
with col_right:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Rajdhani; margin-top:0;">🎯 ANALYST CENTER</h3>', unsafe_allow_html=True)
    
    if not df_radar.empty:
        col_sel, _ = st.columns([1, 2])
        with col_sel:
            selected = st.selectbox("SELECT ASSET:", df_radar['Symbol'])
        
        hist_df = get_history_df(selected)
        tech_result = analyze_smart_v36(hist_df)
        
        if tech_result:
            # 1. SCORE CARD & SIGNALS
            c1, c2 = st.columns([1, 1.5])
            with c1:
                render_score_card_v36(tech_result)
            with c2:
                st.markdown("#### ✅ POSITIVE SIGNALS")
                for p in tech_result['pros']: st.success(p)
                
                st.markdown("#### ⚠️ WARNINGS")
                if tech_result['cons']:
                    for c in tech_result['cons']: st.error(c)
                else:
                    st.info("No major warnings detected.")

            # 2. INTERACTIVE CHART (ZOOMABLE)
            st.markdown("---")
            render_interactive_chart(hist_df, selected)
            
    st.markdown('</div>', unsafe_allow_html=True)
