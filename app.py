# app.py
import streamlit as st
import sys
import os
import plotly.express as px

# Setup
st.set_page_config(layout="wide", page_title="Thang Long Terminal V2", page_icon="🐲")
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.data import get_pro_data, get_history_df
from backend.ai import run_prophet_engine, run_monte_carlo_engine
from frontend.ui import load_custom_css, render_header, render_kpi_card

load_custom_css()
render_header()

# --- INPUT ---
watchlist = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL"]

# --- LAYOUT CHÍNH ---
col_table, col_cmd = st.columns([2, 1]) # Chia 2:1 để bên phải rộng hơn cho AI

with col_table:
    st.markdown('<div class="glass-box"><h3>📡 RADAR THỊ TRƯỜNG</h3>', unsafe_allow_html=True)
    with st.spinner("Đang quét tín hiệu vệ tinh..."):
        df = get_pro_data(watchlist)
    
    if not df.empty:
        st.dataframe(
            df,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã", width="small"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Tín hiệu", width="medium"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", min_value=0, max_value=10, format="%d/10"),
                "Trend": st.column_config.LineChartColumn("Trend 30D")
            },
            hide_index=True, use_container_width=True, height=600
        )
    st.markdown('</div>', unsafe_allow_html=True)

with col_cmd:
    if not df.empty:
        # Chọn mã để phân tích sâu
        selected = st.selectbox("🎯 CHỌN MỤC TIÊU PHÂN TÍCH:", df['Symbol'])
        
        # Lấy data lịch sử cho AI
        history_df = get_history_df(selected)
        
        # TABS CHỨC NĂNG CAO CẤP
        t1, t2, t3 = st.tabs(["🔮 PROPHET AI", "🌌 MONTE CARLO", "📊 TRADINGVIEW"])
        
        with t1:
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            if st.button("Kích hoạt Prophet AI", key="btn_ai", use_container_width=True):
                with st.spinner("AI đang tính toán..."):
                    forecast = run_prophet_engine(history_df)
                    fig = px.line(forecast, x='ds', y=['yhat', 'yhat_lower', 'yhat_upper'], 
                                  color_discrete_sequence=['#22d3ee', '#334155', '#334155'])
                    fig.update_layout(template="plotly_dark", height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(f"Dự báo giá {selected} 30 ngày tới hoàn tất.")
            else:
                st.info("Nhấn nút để chạy mô hình dự báo.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with t2:
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            if st.button("Mở cổng Đa Vũ Trụ", key="btn_mc", use_container_width=True):
                with st.spinner("Đang mô phỏng 100 kịch bản..."):
                    mc_df = run_monte_carlo_engine(history_df)
                    fig = px.line(mc_df, color_discrete_sequence=['rgba(34, 197, 94, 0.1)']) # Màu xanh mờ
                    fig.update_layout(template="plotly_dark", height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with t3:
             st.components.v1.html(f"""
                <div class="tradingview-widget-container">
                  <div id="tv_mini"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                      "width": "100%", "height": 350, "symbol": "HOSE:{selected}",
                      "interval": "D", "timezone": "Asia/Ho_Chi_Minh", "theme": "dark",
                      "style": "1", "toolbar_bg": "#f1f3f6", "hide_top_toolbar": true,
                      "container_id": "tv_mini"
                  }});
                  </script>
                </div>
            """, height=350)
