# app.py
import streamlit as st
import pandas as pd
import sys
import os

# --- 1. SETUP HỆ THỐNG ---
st.set_page_config(layout="wide", page_title="ThangLong Terminal", page_icon="🐲")

# Import modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.data import get_market_data
from frontend.ui import load_custom_css, render_header, render_kpi_card

# Load CSS ngay lập tức
load_custom_css()

# --- 2. HEADER & KPI ---
render_header()

# Giả lập KPI thị trường (Thực tế nên lấy từ API index)
c1, c2, c3, c4 = st.columns(4)
with c1: render_kpi_card("VN-INDEX", "1,254.30", "+12.5 (0.8%)", True)
with c2: render_kpi_card("VN30", "1,280.10", "+8.2 (0.6%)", True)
with c3: render_kpi_card("HNX", "230.50", "-1.2 (-0.5%)", False)
with c4: render_kpi_card("THANH KHOẢN", "18.5K Tỷ", "Cao", True)

# --- 3. MAIN DASHBOARD ---
st.markdown("<br>", unsafe_allow_html=True)
col_table, col_ai = st.columns([3, 1]) # Tỉ lệ 3:1 chuẩn Pro

# --- DANH SÁCH MÃ ---
watchlist = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "VND", "DIG", "NVL", "ACB", "MBB", "TCB"]

with col_table:
    st.markdown('<div class="glass-box" style="padding: 10px 20px;">', unsafe_allow_html=True)
    
    # Filter giả lập
    f1, f2, f3 = st.columns([4, 1, 1])
    with f1: st.markdown("### 🔥 MARKET WATCHLIST")
    with f2: st.button("HOSE", use_container_width=True)
    with f3: st.button("VN30", use_container_width=True, type="primary")

    # LOAD DATA
    with st.spinner("⚡ Initializing Uplink..."):
        df = get_market_data(watchlist)

    if not df.empty:
        # BẢNG GIÁ PRO
        st.dataframe(
            df,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã CK", width="small"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f", width="small"),
                "Change": st.column_config.NumberColumn("+/-", format="%.2f", width="small"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%", width="small"),
                "Volume": st.column_config.NumberColumn("KL", format="%.0f", width="medium"),
                "Trend": st.column_config.LineChartColumn(
                    "Trend (20D)", 
                    width="large",
                    y_min=None, y_max=None # Để None để chart tự scale theo biên độ giá
                )
            },
            hide_index=True,
            use_container_width=True,
            height=600
        )
    else:
        st.error("⚠️ Mất kết nối dữ liệu. Vui lòng kiểm tra API.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CỘT PHẢI: AI COMMANDER ---
with col_ai:
    # Khung AI Thông Minh
    st.markdown("""
    <div class="glass-box" style="border: 1px solid #38bdf8;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
            <div style="width:10px; height:10px; background:#38bdf8; border-radius:50%; box-shadow: 0 0 10px #38bdf8;"></div>
            <div style="font-family:'Rajdhani'; font-weight:700; font-size:1.2rem; color:#fff;">AI COMMANDER</div>
        </div>
        <div style="font-size:0.9rem; color:#cbd5e1; line-height:1.6; border-left: 2px solid #38bdf8; padding-left: 10px;">
            Thị trường đang trong pha <b>Tăng Giá</b>. Dòng tiền tập trung mạnh vào nhóm <b>Công nghệ (FPT)</b> và <b>Thép (HPG)</b>.
            <br><br>
            Khuyến nghị: <span style="color:#22c55e; font-weight:bold;">CANH MUA</span> khi có nhịp chỉnh.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chi tiết mã (Interactive)
    if not df.empty:
        selected_code = st.selectbox("Phân tích nhanh:", df['Symbol'])
        row = df[df['Symbol'] == selected_code].iloc[0]
        
        is_bullish = row['Pct'] >= 0
        color = "#22c55e" if is_bullish else "#ef4444"
        
        st.markdown(f"""
        <div class="glass-box" style="text-align:center;">
            <h1 style="margin:0; font-size:3rem; color:{color}; font-family:'Rajdhani'">{row['Symbol']}</h1>
            <h2 style="margin:0; color:white;">{row['Price']:.2f}</h2>
            <div style="color:{color}; font-weight:bold; font-size:1.2rem; margin-top:5px;">
                {row['Pct']:.2f}%
            </div>
            <div style="margin-top:20px; text-align:left;">
                <p style="color:#94a3b8; font-size:0.8rem;">KLGD: <span style="color:white">{row['Volume']:,.0f}</span></p>
                <button style="width:100%; padding:10px; background:{color}; color:black; font-weight:bold; border:none; border-radius:4px; cursor:pointer;">
                    {'ĐẶT LỆNH MUA' if is_bullish else 'CẮT LỖ NGAY'}
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
