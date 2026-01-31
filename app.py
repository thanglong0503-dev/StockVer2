import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
st.set_page_config(layout="wide", page_title="Thang Long Ultimate", page_icon="🐲")

try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full, get_market_indices
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36, analyze_fundamental # <-- Import logic mới
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_interactive_chart, render_market_overview, render_analysis_section # <-- Import Component mới
except ImportError:
    st.error("Lỗi hệ thống.")
    st.stop()

# LOGIN & UI SETUP
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']:
    # (Giữ code login cũ của bạn ở đây)
    st.session_state['logged_in'] = True # Bypass tạm để test, bạn tự bỏ dòng này nếu cần login
    
load_hardcore_css()
render_header()

# 1. MARKET BAR (ĐÃ CÓ GOLD, NASDAQ)
with st.spinner("Đang kết nối thị trường..."):
    render_market_overview(get_market_indices())
st.markdown("---")

col_radar, col_analyst = st.columns([1.5, 2.5])

# LEFT
with col_radar:
    st.markdown('<div class="glass-box"><h3>📡 RADAR</h3>', unsafe_allow_html=True)
    df_radar = get_pro_data(["HPG","SSI","FPT","MWG","VCB","STB","DIG","NVL","PDR","VIX"])
    if not df_radar.empty: st.dataframe(df_radar, hide_index=True, use_container_width=True, height=600)
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT
with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    if not df_radar.empty:
        selected = st.selectbox("CHỌN MÃ:", df_radar['Symbol'])
        
        # LOAD DATA
        hist_df = get_history_df(selected)
        info, fin, bal, divs = get_stock_data_full(selected) # Lấy data cơ bản
        news_list = get_stock_news_google(selected)

        # PHÂN TÍCH (LOGIC MỚI)
        tech_res = analyze_smart_v36(hist_df)
        fund_res = analyze_fundamental(info, fin)

        # *** HIỂN THỊ 2 CARD KỸ THUẬT & CƠ BẢN ***
        if tech_res and fund_res:
            render_analysis_section(tech_res, fund_res)
        
        # TABS
        t1, t2, t3, t4, t5, t6, t7 = st.tabs(["📊 Biểu Đồ", "📉 TradingView", "🔮 AI Prophet", "🌌 Đa Vũ Trụ", "📰 Tin Tức", "💰 Tài Chính", "🏢 Hồ Sơ"])
        
        with t1: render_interactive_chart(hist_df, selected)
        # (Giữ nguyên các tab khác như code bài trước)
        with t5: 
             for n in news_list: st.write(f"- [{n['title']}]({n['link']})")
        with t6:
             if not fin.empty: st.dataframe(fin.iloc[:, :4])

    st.markdown('</div>', unsafe_allow_html=True)
