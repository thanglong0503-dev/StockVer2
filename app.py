import streamlit as st
import sys
import os
import streamlit.components.v1 as components
import pandas as pd

# ==============================================================================
# 1. CẤU HÌNH & IMPORT
# ==============================================================================
# Thêm đường dẫn để Python tìm thấy các module trong thư mục con
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Cấu hình trang (Phải đặt đầu tiên)
st.set_page_config(
    layout="wide", 
    page_title="Thang Long Terminal V36.1", 
    page_icon="🐲",
    initial_sidebar_state="expanded"
)

# Import Module (Có bắt lỗi để dễ debug)
try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full, get_market_indices
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36, analyze_fundamental
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_interactive_chart, render_market_overview, render_analysis_section
except ImportError as e:
    st.error(f"❌ LỖI HỆ THỐNG: {e}")
    st.info("💡 Gợi ý: Hãy kiểm tra xem bạn đã tạo đủ các file trong thư mục 'backend' và 'frontend' chưa.")
    st.stop()

# ==============================================================================
# 2. HỆ THỐNG ĐĂNG NHẬP (LOGIN SYSTEM)
# ==============================================================================
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False

def render_login():
    st.markdown("""
        <style>
        .stTextInput input {text-align: center;} 
        </style>
        <br><br><br>
        <h1 style='text-align: center; color: #0ea5e9; font-family: Rajdhani; font-size: 3rem;'>
            🐲 THANG LONG TERMINAL
        </h1>
        <p style='text-align: center; color: #64748b; letter-spacing: 2px;'>RESTRICTED ACCESS AREA</p>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.form("login_form"):
            user = st.text_input("CODENAME", placeholder="admin / stock")
            pwd = st.text_input("PASSWORD", type="password", placeholder="admin123 / stock123")
            btn = st.form_submit_button("ACCESS SYSTEM", type="primary", use_container_width=True)
            
            if btn:
                if (user == "admin" and pwd == "admin123") or (user == "stock" and pwd == "stock123"):
                    st.session_state['logged_in'] = True
                    st.toast("✅ Access Granted!", icon="🔓")
                    st.rerun()
                else:
                    st.error("⛔ Access Denied!")

if not st.session_state['logged_in']:
    render_login()
    st.stop() # Dừng code tại đây nếu chưa login

# ==============================================================================
# 3. GIAO DIỆN CHÍNH (MAIN DASHBOARD)
# ==============================================================================

# Nạp CSS & Header
load_hardcore_css()
render_header()

# --- SIDEBAR (TRẠM ĐIỀU KHIỂN) ---
with st.sidebar:
    st.markdown("### 🎛️ CONTROL PANEL")
    st.success("🟢 ONLINE")
    
    st.markdown("---")
    st.markdown("### 📡 SCANNER")
    # Danh sách mã mặc định để quét
    default_tickers = "HPG, SSI, FPT, MWG, VCB, STB, DIG, NVL, PDR, VIX, DGC, VND, TCB, MBB"
    user_tickers = st.text_area("Nhập mã (cách nhau dấu phẩy):", value=default_tickers, height=100)
    
    if st.button("🚀 QUÉT RADAR", type="primary", use_container_width=True):
        st.cache_data.clear() # Xóa cache để làm mới dữ liệu
        st.rerun()
        
    st.markdown("---")
    if st.button("LOGOUT / ĐĂNG XUẤT"):
        st.session_state['logged_in'] = False
        st.rerun()
    
    st.markdown("---")
    st.caption("Developed by Thang Long Team\nVersion 36.1 Ultimate")

# --- PHẦN 1: THANH CHỈ SỐ (TICKER TAPE) ---
with st.spinner("Connecting Global Markets..."):
    # Lấy dữ liệu chỉ số (ETF VN30, Gold, Bitcoin...)
    indices = get_market_indices()
    render_market_overview(indices)

st.markdown("---")

# --- PHẦN 2: CHIA CỘT (RADAR vs ANALYST) ---
col_radar, col_analyst = st.columns([1.5, 2.5])

# === CỘT TRÁI: RADAR ===
with col_radar:
    st.markdown('<div class="glass-box"><h3>📡 MARKET RADAR</h3>', unsafe_allow_html=True)
    
    # Xử lý input từ sidebar
    ticker_list = [t.strip().upper() for t in user_tickers.split(',') if t.strip()]
    
    with st.spinner("Scanning data..."):
        df_radar = get_pro_data(ticker_list)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Mã", width="small"),
                "Price": st.column_config.NumberColumn("Giá (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Tín hiệu"),
                "Score": st.column_config.ProgressColumn("Sức mạnh", format="%d", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("Trend (30D)"),
            },
            hide_index=True, use_container_width=True, height=700
        )
    else:
        st.warning("Không có dữ liệu. Hãy kiểm tra lại mã cổ phiếu.")
    st.markdown('</div>', unsafe_allow_html=True)

# === CỘT PHẢI: TRUNG TÂM PHÂN TÍCH ===
with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    if not df_radar.empty:
        # Chọn mã để phân tích sâu
        selected = st.selectbox("CHỌN MÃ CỔ PHIẾU:", df_radar['Symbol'])
        
        st.markdown(f"<h1 style='color:#0ea5e9; margin-top:-10px; font-family:Rajdhani;'>{selected} - ANALYST CENTER</h1>", unsafe_allow_html=True)
        
        # Tải dữ liệu chi tiết (Deep Dive)
        with st.spinner(f"Đang tải dữ liệu sâu của {selected}..."):
            hist_df = get_history_df(selected)
            info, fin, bal, cash, divs, splits = get_stock_data_full(selected)
            news_list = get_stock_news_google(selected)

        # 1. CHẤM ĐIỂM KÉP (KỸ THUẬT & CƠ BẢN)
        tech_res = analyze_smart_v36(hist_df)
        fund_res = analyze_fundamental(info, fin)

        if tech_res and fund_res:
            render_analysis_section(tech_res, fund_res)
        
        st.markdown("---")

        # 2. HỆ THỐNG TABS CHỨC NĂNG
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
            st.markdown("### 📉 Biểu đồ Real-time (TradingView)")
            # Nhúng Widget TradingView
            components.html(f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                  "width": "100%", "height": 500,
                  "symbol": "HOSE:{selected}",
                  "interval": "D", "timezone": "Asia/Ho_Chi_Minh",
                  "theme": "dark", "style": "1", "locale": "vi_VN",
                  "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                  "allow_symbol_change": true, "container_id": "tradingview_widget"
              }});
              </script>
            </div>
            """, height=520)

        # --- TAB 3: AI PROPHET ---
        with t3:
            st.markdown("### 🔮 AI Tiên Tri (Dự báo xu hướng 60 ngày)")
            if st.button("Kích hoạt AI Prophet", type="primary"):
                with st.spinner("AI đang training mô hình..."):
                    fig_ai = run_prophet_ai(hist_df)
                    if fig_ai: 
                        st.plotly_chart(fig_ai, use_container_width=True)
                    else: 
                        st.warning("⚠️ Không thể chạy mô hình (Thiếu thư viện Prophet hoặc dữ liệu ít).")

        # --- TAB 4: ĐA VŨ TRỤ (MONTE CARLO) ---
        with t4:
            st.markdown("### 🌌 Giả lập 1000 Kịch bản Tương lai (Monte Carlo)")
            if st.button("Mở cổng Đa Vũ Trụ"):
                fig_mc, fig_hist, stats = run_monte_carlo(hist_df)
                if fig_mc:
                    st.plotly_chart(fig_mc, use_container_width=True)
                    
                    # Thống kê xác suất
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Kỳ vọng (Trung bình)", f"{stats['mean']:,.0f}")
                    c2.metric("Kịch bản Tốt (Top 5%)", f"{stats['top_5']:,.0f}", delta="Bull Case")
                    c3.metric("Xác suất Tăng giá", f"{stats['prob_up']:.1f}%")
                    
                    st.plotly_chart(fig_hist, use_container_width=True)

        # --- TAB 5: TIN TỨC ---
        with t5:
            st.markdown(f"### 📰 Tin tức mới nhất về {selected}")
            if news_list:
                for n in news_list:
                    # Card tin tức
                    st.markdown(f"""
                    <div style="
                        background:#1f2937; padding:15px; border-radius:8px; 
                        margin-bottom:12px; border-left: 4px solid #0ea5e9;
                        transition: transform 0.2s;
                    ">
                        <a href="{n['link']}" target="_blank" style="
                            color:white; font-weight:700; font-size:1rem; 
                            text-decoration:none; display:block; margin-bottom:5px;
                        ">{n['title']}</a>
                        <div style="
                            display:flex; justify-content:space-between; 
                            color:#94a3b8; font-size:0.8rem;
                        ">
                            <span>🕒 {n['published']}</span>
                            <span>Nguồn: {n.get('source', 'Google News')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Chưa tìm thấy tin tức mới.")

        # --- TAB 6: TÀI CHÍNH ---
        with t6:
            st.markdown("### 💰 Báo Cáo Tài Chính (Rút gọn)")
            if not fin.empty:
                st.subheader("1. Kết Quả Kinh Doanh")
                # Format hiển thị Tỷ đồng
                fin_display = fin.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(fin_display.style.format("{:,.1f} Tỷ"), use_container_width=True)
            
            if not bal.empty:
                st.subheader("2. Cân Đối Kế Toán")
                bal_display = bal.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(bal_display.style.format("{:,.1f} Tỷ"), use_container_width=True)
                
            if not cash.empty:
                st.subheader("3. Lưu Chuyển Tiền Tệ")
                cash_display = cash.iloc[:, :4].apply(lambda x: x / 1e9 if pd.api.types.is_numeric_dtype(x) else x)
                st.dataframe(cash_display.style.format("{:,.1f} Tỷ"), use_container_width=True)

        # --- TAB 7: HỒ SƠ & CỔ TỨC ---
        with t7:
            c_left, c_right = st.columns(2)
            
            with c_left:
                st.markdown("### 🏢 Hồ Sơ Doanh Nghiệp")
                st.info(f"📍 Ngành nghề: {info.get('sector', 'N/A')}")
                st.info(f"👥 Nhân sự: {info.get('fullTimeEmployees', 'N/A')}")
                st.info(f"🌍 Website: {info.get('website', 'N/A')}")
                
                with st.expander("📝 Mô tả chi tiết", expanded=True):
                    st.write(info.get('longBusinessSummary', 'Chưa có mô tả.'))

            with c_right:
                st.markdown("### 🎁 Lịch Sử Cổ Tức")
                if not divs.empty:
                    # Chế biến dữ liệu cổ tức
                    div_data = divs.reset_index()
                    div_data.columns = ['Ngày', 'Giá Trị']
                    div_data['Ngày'] = div_data['Ngày'].dt.strftime('%Y-%m-%d')
                    
                    # Chart Cổ tức
                    fig_div = go.Figure(go.Bar(
                        x=div_data['Ngày'], 
                        y=div_data['Giá Trị'], 
                        marker_color='#10b981',
                        name='Cổ tức'
                    ))
                    fig_div.update_layout(
                        title="Tiền mặt (VND)", 
                        template="plotly_dark", 
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_div, use_container_width=True)
                    
                    # Bảng dữ liệu
                    st.dataframe(div_data.sort_values('Ngày', ascending=False).head(10), use_container_width=True)
                else:
                    st.info("Không có dữ liệu trả cổ tức gần đây.")

    st.markdown('</div>', unsafe_allow_html=True)
