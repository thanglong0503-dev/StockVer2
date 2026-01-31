# app.py
import streamlit as st
import sys
import os

# 1. CẤU HÌNH PATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 2. CONFIG TRANG
st.set_page_config(layout="wide", page_title="Thang Long Terminal", page_icon="🐲")

# 3. IMPORT
try:
    from backend.data import get_pro_data, get_history_df, get_market_indices
    from backend.logic import analyze_smart_v36, analyze_fundamental_fake
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_score_card_v36, render_interactive_chart, render_market_overview
except ImportError as e:
    st.error(f"❌ System Error: {e}")
    st.stop()

# 4. CHẠY GIAO DIỆN (CHỈ GỌI 1 LẦN)
load_hardcore_css()
render_header() # Hàm này đã chứa đồng hồ rồi, nên nó sẽ hiển thị Header + Clock

# 5. HIỂN THỊ CHỈ SỐ THỊ TRƯỜNG (VNINDEX, DOW JONES...)
with st.spinner("Fetching Global Market Data..."):
    market_data = get_market_indices()
    # Nếu không lấy được VNINDEX thì vẫn hiện các cái khác
    if market_data:
        render_market_overview(market_data)
    else:
        st.warning("⚠️ Market Data unavailable (Check Internet/API)")

st.markdown("---") # Đường kẻ phân cách

# 6. INPUT LIST
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX"]

# 7. CHIA CỘT CHÍNH
col_left, col_right = st.columns([1.8, 2.2])

# --- CỘT TRÁI: RADAR ---
with col_left:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Rajdhani; margin-top:0;">📡 MARKET RADAR (LIVE)</h3>', unsafe_allow_html=True)
    
    with st.spinner("Scanning..."):
        df_radar = get_pro_data(WATCHLIST)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Ticker", width="small"),
                "Price": st.column_config.NumberColumn("Price (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("Change %", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Signal", width="medium"),
                "Score": st.column_config.ProgressColumn("Power", format="%d/10", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("Trend (30D)"),
            },
            hide_index=True, use_container_width=True, height=600
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- CỘT PHẢI: ANALYST ---
with col_right:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Rajdhani; margin-top:0;">🎯 ANALYST CENTER</h3>', unsafe_allow_html=True)
    
    if not df_radar.empty:
        col_sel, _ = st.columns([1, 2])
        with col_sel:
            # Chọn mã
            selected = st.selectbox("SELECT ASSET:", df_radar['Symbol'])
        
        # Lấy data và phân tích
        hist_df = get_history_df(selected)
        tech_result = analyze_smart_v36(hist_df)
        
        if tech_result:
            # Thẻ điểm & Tín hiệu
            c1, c2 = st.columns([1, 1.5])
            with c1: render_score_card_v36(tech_result)
            with c2:
                st.markdown("#### ✅ POSITIVE SIGNALS")
                for p in tech_result['pros']: st.success(p)
                st.markdown("#### ⚠️ WARNINGS")
                if tech_result['cons']:
                    for c in tech_result['cons']: st.error(c)
                else: st.info("No major warnings.")

            # Biểu đồ
            st.markdown("---")
            render_interactive_chart(hist_df, selected)
            
    st.markdown('</div>', unsafe_allow_html=True)
