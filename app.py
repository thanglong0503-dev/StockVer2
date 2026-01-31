# app.py
import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# --- CẤU HÌNH PATH (QUAN TRỌNG ĐỂ FIX IMPORT ERROR) ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- CẤU HÌNH TRANG ---
st.set_page_config(layout="wide", page_title="Thang Long Terminal", page_icon="🐲")

# IMPORT MODULES (Sau khi đã sys.path.append)
try:
    from backend.data import get_pro_data, get_history_df
    from backend.ai import run_prophet_engine, run_monte_carlo_engine
    from frontend.ui import load_hardcore_css, render_header
except ImportError as e:
    st.error(f"❌ Lỗi Import: {e}. Vui lòng kiểm tra file __init__.py trong thư mục backend/ và frontend/.")
    st.stop()

# --- LOAD GIAO DIỆN ---
load_hardcore_css()
render_header()

# --- DANH SÁCH MÃ ---
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX", "GEX"]

# --- LAYOUT CHÍNH ---
col_radar, col_analyst = st.columns([2, 1.2])

# CỘT TRÁI: RADAR
with col_radar:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('### 📡 RADAR THỊ TRƯỜNG', unsafe_allow_html=True)
    
    with st.spinner("Đang quét dữ liệu..."):
        df_pro = get_pro_data(WATCHLIST)
    
    if not df_pro.empty:
        st.dataframe(
            df_pro,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã CK", width="small"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Tín hiệu"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", min_value=0, max_value=10, format="%d/10"),
                "Trend": st.column_config.LineChartColumn("Trend 30D", y_min=0)
            },
            hide_index=True, use_container_width=True, height=650
        )
    else:
        st.warning("Không lấy được dữ liệu. Hãy kiểm tra kết nối mạng.")
    st.markdown('</div>', unsafe_allow_html=True)

# CỘT PHẢI: PHÂN TÍCH AI (KHU VỰC KHOANH ĐỎ ĐÃ FIX)
with col_analyst:
    st.markdown('<div class="glass-box" style="min-height: 800px;">', unsafe_allow_html=True)
    st.markdown('### 🎯 TRUNG TÂM PHÂN TÍCH', unsafe_allow_html=True)

    if not df_pro.empty:
        # SELECTBOX (Đã được CSS fix màu nền)
        st.markdown('<p style="color:#9ca3af; font-size:0.8rem; margin-bottom:5px;">CHỌN MỤC TIÊU:</p>', unsafe_allow_html=True)
        selected_ticker = st.selectbox("CHỌN MỤC TIÊU", df_pro['Symbol'], label_visibility="collapsed")
        
        # CARD INFO
        row = df_pro[df_pro['Symbol'] == selected_ticker].iloc[0]
        color = "#10b981" if row['Pct'] >= 0 else "#ef4444"
        
        st.markdown(f"""
        <div style="background: #111827; padding: 20px; border-radius: 12px; border: 1px solid #374151; margin: 20px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h1 style="margin:0; font-size: 3.5rem; font-family: 'Rajdhani'; color: white; line-height: 1;">{selected_ticker}</h1>
                <div style="text-align:right;">
                    <div style="font-size: 2.2rem; font-weight:bold; color: {color};">{row['Price']:.2f}</div>
                    <div style="color: {color}; font-weight:bold; background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 4px;">{row['Pct']*100:.2f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TABS CHỨC NĂNG
        t1, t2 = st.tabs(["🔮 PROPHET AI", "🌌 MONTE CARLO"])

        # TAB 1: PROPHET
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            # BUTTON PRIMARY (Màu xanh neon nổi bật)
            if st.button("KÍCH HOẠT DỰ BÁO GIÁ", key="btn_prophet", use_container_width=True, type="primary"):
                with st.spinner("AI đang tính toán..."):
                    hist_df = get_history_df(selected_ticker)
                    forecast = run_prophet_engine(hist_df)
                    
                    if forecast is not None:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Dự báo', line=dict(color='#06b6d4', width=3)))
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', line=dict(width=0), showlegend=False))
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(6, 182, 212, 0.1)', showlegend=False))
                        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)
                        st.success("Dự báo hoàn tất!")

        # TAB 2: MONTE CARLO
        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("CHẠY MÔ PHỎNG ĐA VŨ TRỤ", key="btn_monte", use_container_width=True, type="secondary"):
                with st.spinner("Đang mở cổng lượng tử..."):
                    hist_df = get_history_df(selected_ticker)
                    mc_df = run_monte_carlo_engine(hist_df)
                    fig_mc = px.line(mc_df, color_discrete_sequence=['rgba(16, 185, 129, 0.1)'])
                    fig_mc.update_layout(template="plotly_dark", height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=30,b=0))
                    st.plotly_chart(fig_mc, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
