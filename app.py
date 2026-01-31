import streamlit as st
import sys
import os

# --- FIX IMPORT ERROR ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- LOAD MODULE ---
from backend.data import get_pro_data, get_history_df
from backend.logic_v36 import analyze_smart_v36, analyze_fundamental_fake
from frontend.ui import load_hardcore_css, render_header
from frontend.components import render_score_card_v36, render_fundamental_card, render_chart_v36

st.set_page_config(layout="wide", page_title="Thang Long Ultimate", page_icon="🐲")
load_hardcore_css()
render_header()

# --- INPUT ---
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL"]

# --- LAYOUT CHÍNH ---
col_left, col_right = st.columns([1.5, 2.5])

with col_left:
    st.markdown("### 📡 RADAR (REAL-TIME)")
    with st.spinner("Load Data..."):
        df_radar = get_pro_data(WATCHLIST)
    
    if not df_radar.empty:
        # Bảng giá thu gọn
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã"),
                "Price": st.column_config.NumberColumn("Giá"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Score": st.column_config.ProgressColumn("Điểm", max_value=10, format="%d"),
            },
            hide_index=True, use_container_width=True, height=600
        )

with col_right:
    st.markdown("### 🎯 PHÂN TÍCH CHUYÊN SÂU (V36.1)")
    
    if not df_radar.empty:
        # 1. Chọn Mã
        selected = st.selectbox("Chọn mã để soi:", df_radar['Symbol'])
        
        # 2. Lấy Data lịch sử & Tính toán
        hist_df = get_history_df(selected)
        tech_result = analyze_smart_v36(hist_df)
        fund_result = analyze_fundamental_fake(selected)
        
        if tech_result:
            # 3. HIỂN THỊ THẺ ĐIỂM & CƠ BẢN (NHƯ ẢNH CŨ)
            c1, c2 = st.columns(2)
            with c1:
                render_score_card_v36(tech_result)
                # List Pros (Điểm tốt)
                st.markdown("<br>", unsafe_allow_html=True)
                for p in tech_result['pros']: 
                    st.success(f"✅ {p}")
            
            with c2:
                render_fundamental_card(fund_result)
                # List Cons (Cảnh báo)
                st.markdown("<br>", unsafe_allow_html=True)
                for c in tech_result['cons']:
                    st.error(f"⚠️ {c}")
            
            # 4. BIỂU ĐỒ NẾN TO ĐÙNG
            st.markdown("---")
            render_chart_v36(hist_df, selected)
