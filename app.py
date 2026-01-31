# app.py
import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# --- SETUP CƠ BẢN ---
st.set_page_config(layout="wide", page_title="Thang Long Terminal V3", page_icon="🐲")
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.data import get_pro_data, get_history_df
from backend.ai import run_prophet_engine, run_monte_carlo_engine
from frontend.ui import load_hardcore_css, render_header

# --- LOAD GIAO DIỆN ---
load_hardcore_css()
render_header()

# --- DANH SÁCH MÃ ---
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX", "GEX"]

# --- MAIN LAYOUT (CHIA 2 CỘT 65% - 35%) ---
col_radar, col_analyst = st.columns([2, 1.2])

# ==========================================
# CỘT TRÁI: RADAR THỊ TRƯỜNG (TABLE)
# ==========================================
with col_radar:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('### 📡 RADAR THỊ TRƯỜNG (REAL-TIME)', unsafe_allow_html=True)
    
    with st.spinner("Đang quét dữ liệu vệ tinh..."):
        df_pro = get_pro_data(WATCHLIST)
    
    if not df_pro.empty:
        st.dataframe(
            df_pro,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã CK", width="small"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f", width="small"),
                "Change": st.column_config.NumberColumn("+/-", format="%.2f", width="small"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%", width="small"),
                "RSI": st.column_config.NumberColumn("RSI", format="%.1f", width="small"),
                "Signal": st.column_config.TextColumn("Tín hiệu", width="medium"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", min_value=0, max_value=10, format="%d/10", width="medium"),
                "Trend": st.column_config.LineChartColumn("Trend (30D)", width="medium", y_min=0)
            },
            hide_index=True,
            use_container_width=True,
            height=650
        )
    else:
        st.error("Không kết nối được dữ liệu. Vui lòng kiểm tra lại mạng hoặc API.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# CỘT PHẢI: TRUNG TÂM PHÂN TÍCH (AI)
# ==========================================
with col_analyst:
    st.markdown('<div class="glass-box" style="min-height: 800px;">', unsafe_allow_html=True)
    st.markdown('### 🎯 TRUNG TÂM PHÂN TÍCH', unsafe_allow_html=True)

    if not df_pro.empty:
        # SELECTBOX ĐÃ ĐƯỢC FIX CSS MÀU SẮC
        selected_ticker = st.selectbox("CHỌN MỤC TIÊU:", df_pro['Symbol'])
        
        # Lấy info mã đang chọn
        row = df_pro[df_pro['Symbol'] == selected_ticker].iloc[0]
        color = "#10b981" if row['Pct'] >= 0 else "#ef4444"
        
        # CARD THÔNG TIN NHANH
        st.markdown(f"""
        <div style="background: #1f2937; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h1 style="margin:0; font-size: 3rem; font-family: 'Rajdhani'; color: white;">{selected_ticker}</h1>
                <div style="text-align:right;">
                    <div style="font-size: 2rem; font-weight:bold; color: {color};">{row['Price']:.2f}</div>
                    <div style="color: {color}; font-weight:bold;">{row['Pct']*100:.2f}%</div>
                </div>
            </div>
            <div style="margin-top: 10px; font-family: 'Inter'; font-size: 0.9rem; color: #9ca3af;">
                Tín hiệu: <span style="color: white; font-weight: bold;">{row['Signal']}</span> | 
                RSI: <span style="color: white; font-weight: bold;">{row['RSI']}</span> | 
                Score: <span style="color: white; font-weight: bold;">{row['Score']}/10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TABS CHỨC NĂNG
        t1, t2, t3 = st.tabs(["🔮 PROPHET AI", "🌌 MONTE CARLO", "📊 TRADINGVIEW"])

        # --- TAB 1: PROPHET ---
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("KÍCH HOẠT PROPHET AI", key="btn_prophet", use_container_width=True, type="primary"):
                with st.spinner(f"AI đang phân tích {selected_ticker}..."):
                    hist_df = get_history_df(selected_ticker)
                    forecast = run_prophet_engine(hist_df)
                    
                    if forecast is not None:
                        # Vẽ chart đẹp bằng Plotly
                        fig = go.Figure()
                        # Dữ liệu thực
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Dự báo', line=dict(color='#06b6d4', width=2)))
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', name='Upper', line=dict(width=0), showlegend=False))
                        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', name='Lower', line=dict(width=0), fill='tonexty', fillcolor='rgba(6, 182, 212, 0.2)', showlegend=False))
                        
                        fig.update_layout(
                            template="plotly_dark", 
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            height=350, margin=dict(l=0, r=0, t=30, b=0),
                            title="Dự báo xu hướng 30 ngày tới"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Dự báo giá
                        next_price = forecast['yhat'].iloc[-1]
                        st.success(f"Dự báo giá sau 30 ngày: ~{next_price:,.0f} VND")
                    else:
                        st.error("Không đủ dữ liệu lịch sử.")

        # --- TAB 2: MONTE CARLO ---
        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("MỞ CỔNG ĐA VŨ TRỤ", key="btn_monte", use_container_width=True, type="secondary"):
                with st.spinner("Đang chạy mô phỏng..."):
                    hist_df = get_history_df(selected_ticker)
                    mc_df = run_monte_carlo_engine(hist_df)
                    
                    fig_mc = px.line(mc_df, color_discrete_sequence=['rgba(16, 185, 129, 0.2)'])
                    fig_mc.update_layout(
                        template="plotly_dark", 
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        height=350, showlegend=False,
                        title="50 Kịch bản tương lai (Monte Carlo)"
                    )
                    st.plotly_chart(fig_mc, use_container_width=True)

        # --- TAB 3: TRADINGVIEW ---
        with t3:
            st.components.v1.html(f"""
                <div class="tradingview-widget-container">
                  <div id="tv_chart"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                      "width": "100%", "height": 400, "symbol": "HOSE:{selected_ticker}",
                      "interval": "D", "timezone": "Asia/Ho_Chi_Minh", "theme": "dark",
                      "style": "1", "locale": "vi_VN", "toolbar_bg": "#1f2937", 
                      "enable_publishing": false, "hide_top_toolbar": true,
                      "container_id": "tv_chart"
                  }});
                  </script>
                </div>
            """, height=420)

    st.markdown('</div>', unsafe_allow_html=True)
