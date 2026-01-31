import streamlit as st
import sys
import os

# --- CẤU HÌNH ---
st.set_page_config(layout="wide", page_title="Stock V2", page_icon="🐲")

# --- KẾT NỐI MODULE ---
# Giúp app tìm thấy folder backend và frontend
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.data import get_stock_data, get_news
from backend.logic import analyze_technical
from backend.ai import run_monte_carlo_sim
from frontend.ui import load_css, render_kpi_cards, render_chart_tradingview, plot_monte_carlo

# --- GIAO DIỆN CHÍNH ---
load_css() # Load giao diện đẹp

# Sidebar
st.sidebar.title("🐲 STOCK V2")
symbol = st.sidebar.text_input("Mã CP:", "HPG").upper()
tabs = st.tabs(["📊 Tổng Quan", "🔮 AI Dự Báo", "📰 Tin Tức"])

if symbol:
    # 1. Lấy dữ liệu
    df = get_stock_data(symbol)
    
    if df is not None:
        # 2. Tab Tổng Quan
        with tabs[0]:
            # Tính toán
            result = analyze_technical(df)
            
            # Hiển thị
            col1, col2 = st.columns([1, 2])
            with col1:
                render_kpi_cards(result)
                st.write("✅ **Điểm mạnh:**")
                for p in result['pros']: st.success(p)
                st.write("⚠️ **Cảnh báo:**")
                for c in result['cons']: st.warning(c)
                
            with col2:
                render_chart_tradingview(symbol)
        
        # 3. Tab AI
        with tabs[1]:
            if st.button("Chạy Monte Carlo"):
                sim_df = run_monte_carlo_sim(df)
                plot_monte_carlo(sim_df)
                
        # 4. Tab Tin Tức
        with tabs[2]:
            news = get_news(symbol)
            for n in news:
                st.markdown(f"- [{n['title']}]({n['link']}) ({n['published']})")

    else:
        st.error(f"Không tìm thấy mã {symbol}")
