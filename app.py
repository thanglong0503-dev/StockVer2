import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components

# 1. CẤU HÌNH HỆ THỐNG
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
st.set_page_config(layout="wide", page_title="Thang Long Ultimate", page_icon="🐲")

# 2. IMPORT MODULE (Bắt lỗi nếu thiếu file)
try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full, get_market_indices
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36, analyze_fundamental
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_interactive_chart, render_market_overview, render_analysis_section
except ImportError as e:
    st.error(f"❌ Lỗi hệ thống: {e}. Hãy kiểm tra lại các file trong thư mục backend/frontend.")
    st.stop()

# ==========================================
# 🔐 3. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

def login_ui():
    st.markdown("<h1 style='text-align: center; color: #0ea5e9; font-family: Rajdhani;'>🐲 THANG LONG TERMINAL ACCESS</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("LOGIN / ĐĂNG NHẬP")
            
            if submitted:
                # User mặc định: admin / admin123
                if user == "admin" and pwd == "admin123":
                    st.session_state['logged_in'] = True
                    st.rerun()
                elif user == "stock" and pwd == "stock123":
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")

if not st.session_state['logged_in']:
    login_ui()
    st.stop()

# ==========================================
# 🚀 4. GIAO DIỆN CHÍNH (MAIN UI)
# ==========================================
load_hardcore_css()
render_header()

# SIDEBAR (TRẠM ĐIỀU KHIỂN)
with st.sidebar:
    st.title("🎛️ CONTROL PANEL")
    st.success("✅ System Online")
    if st.button("LOGOUT / ĐĂNG XUẤT", type="primary"):
        st.session_state['logged_in'] = False
        st.rerun()
    st.markdown("---")
    st.info("Triết lý: Dòng tiền thông minh + Tăng trưởng bền vững.")

# --- PHẦN 1: THANH CHỈ SỐ (MARKET BAR) ---
# (Bao gồm: VN30 ETF, Dow Jones, Nasdaq, Gold, Bitcoin)
with st.spinner("Connecting Global Markets..."):
    market_indices = get_market_indices()
    render_market_overview(market_indices)

st.markdown("---")

# --- PHẦN 2: CHIA CỘT (RADAR vs ANALYST) ---
col_radar, col_analyst = st.columns([1.5, 2.5])

# === CỘT TRÁI: RADAR QUÉT MÃ ===
with col_radar:
    st.markdown('<div class="glass-box"><h3>📡 RADAR THỊ TRƯỜNG</h3>', unsafe_allow_html=True)
    
    # List mặc định để quét
    WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX", "DGC", "VND"]
    
    with st.spinner("Scanning tickers..."):
        df_radar = get_pro_data(WATCHLIST)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Tín hiệu"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", format="%d", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("Trend 30D"),
            },
            hide_index=True, use_container_width=True, height=650
        )
    else:
        st.warning("Không lấy được dữ liệu bảng giá.")
    st.markdown('</div>', unsafe_allow_html=True)

# === CỘT PHẢI: TRUNG TÂM PHÂN TÍCH ===
with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    if not df_radar.empty:
        # Chọn mã từ Radar
        selected = st.selectbox("CHỌN MÃ CỔ PHIẾU:", df_radar['Symbol'])
        
        # Tiêu đề mã
        st.markdown(f"<h1 style='color:#06b6d4; margin-top:-10px; font-family:Rajdhani;'>{selected} - ANALYST CENTER</h1>", unsafe_allow_html=True)
        
        # Tải dữ liệu chi tiết
        with st.spinner(f"Đang tải dữ liệu {selected}..."):
            hist_df = get_history_df(selected)
            info, fin, bal, divs = get_stock_data_full(selected)
            news_list = get_stock_news_google(selected)

        # 1. CHẤM ĐIỂM KÉP (KỸ THUẬT & CƠ BẢN)
        tech_res = analyze_smart_v36(hist_df)
        fund_res = analyze_fundamental(info, fin)

        if tech_res and fund_res:
            render_analysis_section(tech_res, fund_res)
        
        st.markdown("---")

        # 2. HỆ THỐNG TABS CHỨC NĂNG (ĐỦ 7 TAB)
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "📊 Biểu Đồ", 
            "📉 TradingView", 
            "🔮 AI Prophet", 
            "🌌 Đa Vũ Trụ", 
            "📰 Tin Tức", 
            "💰 Tài Chính", 
            "🏢 Hồ Sơ & Cổ Tức"
        ])
        
        # --- TAB 1: CHART TƯƠNG TÁC ---
        with t1:
            render_interactive_chart(hist_df, selected)

        # --- TAB 2: TRADINGVIEW WIDGET ---
        with t2:
            st.markdown("Biểu đồ Real-time từ TradingView (Nguồn quốc tế)")
            components.html(f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                  "width": "100%",
                  "height": 500,
                  "symbol": "HOSE:{selected}",
                  "interval": "D",
                  "timezone": "Asia/Ho_Chi_Minh",
                  "theme": "dark",
                  "style": "1",
                  "locale": "vi_VN",
                  "enable_publishing": false,
                  "allow_symbol_change": true,
                  "container_id": "tradingview_widget"
              }});
              </script>
            </div>
            """, height=500)

        # --- TAB 3: AI PROPHET ---
        with t3:
            st.markdown("### 🔮 AI Prophet Dự Báo Xu Hướng")
            if st.button("Kích hoạt AI Tiên Tri"):
                with st.spinner("AI đang tính toán..."):
                    fig_ai = run_prophet_ai(hist_df)
                    if fig_ai: 
                        st.plotly_chart(fig_ai, use_container_width=True)
                    else: 
                        st.warning("Cần cài đặt thư viện 'prophet' để dùng tính năng này.")

        # --- TAB 4: ĐA VŨ TRỤ (MONTE CARLO) ---
        with t4:
            st.markdown("### 🌌 Giả Lập 1000 Kịch Bản Tương Lai")
            if st.button("Chạy Mô Phỏng Monte Carlo"):
                fig_mc, fig_hist, stats = run_monte_carlo(hist_df)
                if fig_mc:
                    st.plotly_chart(fig_mc, use_container_width=True)
                    
                    # Thống kê
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Giá Trung Bình (Kỳ vọng)", f"{stats['mean']:,.0f}")
                    m2.metric("Kịch Bản Tốt Nhất (Top 5%)", f"{stats['top_5']:,.0f}", delta="Bull Case")
                    m3.metric("Xác Suất Tăng Giá", f"{stats['prob_up']:.1f}%")
                    
                    st.plotly_chart(fig_hist, use_container_width=True)

        # --- TAB 5: TIN TỨC ---
        with t5:
            st.markdown(f"### 📰 Tin tức mới nhất về {selected}")
            if news_list:
                for n in news_list:
                    st.markdown(f"""
                    <div style="background:#1f2937; padding:12px; border-radius:8px; margin-bottom:10px; border-left: 4px solid #0ea5e9;">
                        <a href="{n['link']}" target="_blank" style="color:white; font-weight:bold; font-size:1rem; text-decoration:none;">{n['title']}</a>
                        <div style="color:#9ca3af; font-size:0.8rem; margin-top:5px;">🕒 {n['published']} | Nguồn: Google News</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Không tìm thấy tin tức mới.")

        # --- TAB 6: TÀI CHÍNH ---
        with t6:
            st.markdown("### 💰 Báo Cáo Tài Chính (Quý)")
            if not fin.empty:
                st.subheader("Kết Quả Kinh Doanh")
                # Format số liệu cho đẹp (chia tỷ đồng)
                fin_display = fin.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(fin_display.style.format("{:,.1f} Tỷ"), use_container_width=True)
            
            if not bal.empty:
                st.subheader("Cân Đối Kế Toán")
                bal_display = bal.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(bal_display.style.format("{:,.1f} Tỷ"), use_container_width=True)

        # --- TAB 7: HỒ SƠ & CỔ TỨC ---
        with t7:
            c_left, c_right = st.columns(2)
            
            with c_left:
                st.markdown("### 🏢 Hồ Sơ Doanh Nghiệp")
                st.info(f"Ngành nghề: {info.get('sector', 'N/A')}")
                st.info(f"Nhân sự: {info.get('fullTimeEmployees', 'N/A')}")
                with st.expander("Xem mô tả chi tiết", expanded=True):
                    st.write(info.get('longBusinessSummary', 'Chưa có mô tả.'))

            with c_right:
                st.markdown("### 🎁 Lịch Sử Cổ Tức")
                if not divs.empty:
                    # Vẽ biểu đồ cổ tức
                    div_data = divs.reset_index()
                    div_data.columns = ['Date', 'Amount']
                    
                    fig_div = go.Figure(go.Bar(
                        x=div_data['Date'], 
                        y=div_data['Amount'], 
                        marker_color='#10b981',
                        name='Cổ tức'
                    ))
                    fig_div.update_layout(title="Cổ tức tiền mặt (VND)", template="plotly_dark", height=300)
                    st.plotly_chart(fig_div, use_container_width=True)
                    
                    # Bảng chi tiết
                    st.dataframe(div_data.sort_values('Date', ascending=False).head(5), use_container_width=True)
                else:
                    st.info("Không có dữ liệu cổ tức gần đây.")

    st.markdown('</div>', unsafe_allow_html=True) # Đóng div glass-box
