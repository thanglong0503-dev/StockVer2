import streamlit as st
import sys
import os

# --- 1. CẤU HÌNH ĐƯỜNG DẪN (QUAN TRỌNG) ---
# Dòng này giúp app tìm thấy folder backend và frontend
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- 2. SETUP TRANG ---
st.set_page_config(layout="wide", page_title="Thang Long Ultimate", page_icon="🐲")

# --- 3. IMPORT MODULE (ĐÃ SỬA TÊN FILE IMPORT) ---
try:
    # Backend
    from backend.data import get_pro_data, get_history_df
    # LƯU Ý: Import từ 'logic' chứ không phải 'logic_v36' vì tên file của bạn là logic.py
    from backend.logic import analyze_smart_v36, analyze_fundamental_fake 
    
    # Frontend
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_score_card_v36, render_chart_v36
    
except ImportError as e:
    st.error(f"❌ LỖI IMPORT: {e}")
    st.stop()

# --- 4. CHẠY GIAO DIỆN ---
load_hardcore_css()
render_header()

# Danh sách mã chứng khoán
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX"]

# --- LAYOUT CHIA CỘT ---
col_radar, col_analyst = st.columns([1.5, 2.5])

# CỘT TRÁI: BẢNG GIÁ
with col_radar:
    st.markdown('<div class="glass-box"><h3>📡 RADAR THỊ TRƯỜNG</h3>', unsafe_allow_html=True)
    with st.spinner("Đang tải dữ liệu..."):
        df_radar = get_pro_data(WATCHLIST)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã"),
                "Price": st.column_config.NumberColumn("Giá"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", format="%d", min_value=0, max_value=10),
            },
            hide_index=True, use_container_width=True, height=600
        )
    st.markdown('</div>', unsafe_allow_html=True)

# CỘT PHẢI: PHÂN TÍCH CHUYÊN SÂU
with col_analyst:
    st.markdown('<div class="glass-box"><h3>🎯 PHÂN TÍCH KỸ THUẬT (V36.1)</h3>', unsafe_allow_html=True)
    
    if not df_radar.empty:
        # Chọn mã từ bảng
        selected = st.selectbox("Chọn mã để soi:", df_radar['Symbol'])
        
        # Lấy data lịch sử & Chạy logic
        hist_df = get_history_df(selected)
        
        # GỌI HÀM PHÂN TÍCH
        tech_result = analyze_smart_v36(hist_df)
        fund_result = analyze_fundamental_fake(selected)
        
        if tech_result:
            # Hiển thị 2 cột: Thẻ điểm & Thông tin
            c1, c2 = st.columns(2)
            
            with c1:
                render_score_card_v36(tech_result)
            
            with c2:
                st.markdown("#### ✅ TÍN HIỆU TÍCH CỰC")
                for p in tech_result['pros']: st.success(p)
                
                st.markdown("#### ⚠️ CẢNH BÁO")
                for c in tech_result['cons']: st.error(c)
                if not tech_result['cons']: st.info("Chưa có cảnh báo nguy hiểm.")

            # Vẽ biểu đồ
            st.markdown("---")
            render_chart_v36(hist_df, selected)
            
    st.markdown('</div>', unsafe_allow_html=True)
