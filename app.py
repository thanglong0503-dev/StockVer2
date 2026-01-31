# app.py
import streamlit as st
import sys
import os

# Cấu hình trang (Phải để đầu tiên)
st.set_page_config(layout="wide", page_title="DNSE Pro", page_icon="⚡")

# Import module
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.data import get_batch_data
from frontend.ui import load_dnse_css, render_header, render_sidebar_detail

# 1. Load giao diện
load_dnse_css()
render_header()

# 2. Xử lý logic
col_list, col_detail = st.columns([3, 1])

# DANH SÁCH MÃ THEO DÕI (Sửa list này tùy thích)
watchlist = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "VND", "DIG", "NVL"]

with st.spinner("Đang tải data thị trường..."):
    df = get_batch_data(watchlist)

# CỘT TRÁI: Bảng giá
with col_list:
    st.subheader("🔥 Bảng giá trực tuyến")
    if not df.empty:
        st.dataframe(
            df,
            column_config={
                "Mã": st.column_config.TextColumn("Mã", width="small"),
                "Giá": st.column_config.NumberColumn("Giá", format="%.2f", width="small"),
                "%": st.column_config.NumberColumn("%", format="%.2f %%", width="small"),
                "Xu hướng": st.column_config.LineChartColumn("Trend (20p)", y_min=0, width="medium"),
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )

# CỘT PHẢI: Chi tiết & AI
with col_detail:
    if not df.empty:
        selected = st.selectbox("Chi tiết mã:", df['Mã'])
        info = df[df['Mã'] == selected].iloc[0]
        render_sidebar_detail(info)
        
        st.info("🤖 **Ensa AI:** Dòng tiền đang vào mạnh, xu hướng tích cực!")
