import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

# CONFIG
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
st.set_page_config(layout="wide", page_title="Thang Long Ultimate", page_icon="🐲")

# IMPORT
try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_score_card_v36, render_interactive_chart, render_market_overview
except ImportError:
    st.error("Lỗi hệ thống: Vui lòng kiểm tra lại file backend.")
    st.stop()

# ==========================================
# 🔐 1. HỆ THỐNG ĐĂNG NHẬP (KHÔI PHỤC)
# ==========================================
USERS = {"admin": "admin123", "stock": "stock123", "guest": "123456"}

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

def login_ui():
    st.markdown("<h1 style='text-align: center; color: #0ea5e9;'>🐲 STOCK THANG LONG LOGIN</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Đăng Nhập", type="primary", use_container_width=True):
            if user in USERS and USERS[user] == pwd:
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

if not st.session_state['logged_in']:
    login_ui()
    st.stop()

# ==========================================
# 🚀 2. GIAO DIỆN CHÍNH
# ==========================================
load_hardcore_css()
render_header()

# SIDEBAR
with st.sidebar:
    st.success("✅ Đã đăng nhập")
    if st.button("Đăng Xuất"):
        st.session_state['logged_in'] = False
        st.rerun()
    st.markdown("---")
    st.write("Triết lý: Dòng tiền thông minh + Tăng trưởng")

# 1. THANH CHỈ SỐ
# (Code rút gọn lấy ETF cho nhanh - giống bài trước)
import yfinance as yf
indices = []
for item in [{"n":"VN30 ETF","s":"E1VFVN30.VN"}, {"n":"DOW JONES","s":"^DJI"}]:
    try:
        h = yf.Ticker(item['s']).history(period="5d")
        now = h['Close'].iloc[-1]; chg = now - h['Close'].iloc[-2]
        indices.append({"Name": item['n'], "Price": now, "Change": chg, "Pct": chg/h['Close'].iloc[-2]*100, "Color": "#10b981" if chg>=0 else "#ef4444", "Status": "LIVE"})
    except: pass
render_market_overview(indices)
st.markdown("---")

# 2. CHIA CỘT
col_radar, col_analyst = st.columns([1.5, 2.5])

with col_radar:
    st.markdown('<div class="glass-box"><h3>📡 RADAR</h3>', unsafe_allow_html=True)
    df_radar = get_pro_data(["HPG","SSI","FPT","MWG","VCB","STB","DIG","NVL"])
    if not df_radar.empty:
        st.dataframe(df_radar, hide_index=True, use_container_width=True, height=600)
    st.markdown('</div>', unsafe_allow_html=True)

with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    if not df_radar.empty:
        selected = st.selectbox("CHỌN MÃ:", df_radar['Symbol'])
        
        # TẢI DỮ LIỆU FULL
        hist_df = get_history_df(selected)
        info, fin, bal, cash, divs, splits = get_stock_data_full(selected)
        news_list = get_stock_news_google(selected)

        # 3. HỆ THỐNG TABS (Y HỆT ẢNH)
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "📊 Biểu Đồ", "📉 TradingView", "🔮 AI Prophet", 
            "🌌 Đa Vũ Trụ", "📰 Tin Tức", "💰 Tài Chính", "🏢 Hồ Sơ"
        ])
        
        # TAB 1: BIỂU ĐỒ
        with t1:
            render_interactive_chart(hist_df, selected)
        
        # TAB 2: TRADINGVIEW
        with t2:
            st.components.v1.html(f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{"width": "100%","height": 500,"symbol": "HOSE:{selected}","interval": "D","theme": "dark","locale": "vi_VN","container_id": "tradingview_widget"}});
              </script>
            </div>
            """, height=500)

        # TAB 3: AI PROPHET
        with t3:
            fig_ai = run_prophet_ai(hist_df)
            if fig_ai: st.plotly_chart(fig_ai, use_container_width=True)
            else: st.warning("Cần cài đặt thư viện Prophet")

        # TAB 4: ĐA VŨ TRỤ (MONTE CARLO)
        with t4:
            st.markdown("### 🌌 Mô Phỏng Tương Lai (Monte Carlo)")
            if st.button("Chạy Giả Lập 1000 Kịch Bản"):
                fig_mc, fig_hist, stats = run_monte_carlo(hist_df)
                if fig_mc:
                    st.plotly_chart(fig_mc, use_container_width=True)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Trung Bình", f"{stats['mean']:,.0f}")
                    c2.metric("Kịch Bản Tốt", f"{stats['top_5']:,.0f}")
                    c3.metric("Xác Suất Tăng", f"{stats['prob_up']:.1f}%")
                    st.plotly_chart(fig_hist, use_container_width=True)

        # TAB 5: TIN TỨC (Dùng code cũ Feedparser)
        with t5:
            st.markdown(f"### 📰 Tin tức: {selected}")
            for n in news_list:
                st.markdown(f"""
                <div style="background:#1f2937; padding:10px; border-radius:5px; margin-bottom:10px; border-left: 3px solid #0ea5e9;">
                    <a href="{n['link']}" target="_blank" style="color:white; font-weight:bold; text-decoration:none;">{n['title']}</a>
                    <div style="color:#9ca3af; font-size:0.8rem; margin-top:5px;">🕒 {n['published']}</div>
                </div>
                """, unsafe_allow_html=True)

        # TAB 6: TÀI CHÍNH (Format đẹp như ảnh)
        with t6:
            st.markdown("### 💰 Báo Cáo Tài Chính (Quý)")
            if not fin.empty:
                st.subheader("Kết Quả Kinh Doanh")
                st.dataframe(fin.iloc[:, :4], use_container_width=True) # Lấy 4 quý gần nhất
            if not bal.empty:
                st.subheader("Cân Đối Kế Toán")
                st.dataframe(bal.iloc[:, :4], use_container_width=True)

        # TAB 7: HỒ SƠ & CỔ TỨC
        with t7:
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("### 🏢 Hồ Sơ")
                st.info(f"Ngành: {info.get('sector', 'N/A')}")
                st.write(info.get('longBusinessSummary', 'Chưa có mô tả'))
            with c_right:
                st.markdown("### 🎁 Lịch Sử Cổ Tức")
                if not divs.empty:
                    # Vẽ biểu đồ cổ tức
                    div_data = divs.reset_index()
                    div_data.columns = ['Ngày', 'Giá Trị']
                    fig_div = go.Figure(go.Bar(x=div_data['Ngày'], y=div_data['Giá Trị'], marker_color='#10b981'))
                    fig_div.update_layout(title="Cổ tức tiền mặt", template="plotly_dark", height=300)
                    st.plotly_chart(fig_div, use_container_width=True)
                    st.dataframe(div_data.sort_values('Ngày', ascending=False).head(5), use_container_width=True)
                else:
                    st.info("Không có dữ liệu cổ tức gần đây.")

    st.markdown('</div>', unsafe_allow_html=True)
