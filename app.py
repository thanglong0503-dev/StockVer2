"""
================================================================================
MODULE: app.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.7.0-TREASURE-VAULT-MERGED
THEME: CYBERPUNK HUD
DESCRIPTION: 
    - Full Logic: Login -> Sidebar -> Radar (Cached) -> Analyst (Deep Dive).
    - Fixed: Radar does NOT re-scan when selecting a stock.
    - Features: AI Prophet Crosshair, Monte Carlo, Zoomable Charts.
    - NEW: TREASURE VAULT (Gold & Silver Realtime Price).
================================================================================
"""
# [NEW IMPORT]
from backend.commodities import get_gold_price, get_silver_price
# [NEW IMPORT] Module quản lý User & Portfolio
from backend.database import register_user, login_user, add_transaction, get_user_portfolio
# Thêm get_all_users_admin và delete_user_admin vào dòng import
# Thêm init_admin_account vào import
from backend.database import register_user, login_user, add_transaction, get_user_portfolio, get_all_users_admin, delete_user_admin, init_admin_account, delete_portfolio_stock

# Gọi hàm này ngay đầu file để chắc chắn Admin luôn tồn tại
init_admin_account()
import streamlit as st
import sys
import os
import time
import pandas as pd
import streamlit.components.v1 as components
from frontend.components import render_market_galaxy
# Sửa backend.stock_list thành backend.sectors
from backend.sectors import get_full_market_list, get_all_sector_names, get_sector_list_data
# ==============================================================================
# 1. SYSTEM CONFIGURATION
# ==============================================================================
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    layout="wide", 
    page_title="TL-TERMINAL V36.7", 
    page_icon="💠",
    initial_sidebar_state="expanded",
    menu_items={'About': "Thang Long Terminal - Advanced Market Intelligence System"}
)

# Import Modules (Kèm xử lý lỗi nếu thiếu file)
try:
    from backend.data import get_pro_data, get_history_df, get_stock_news_google, get_stock_data_full, get_market_indices
    from backend.ai import run_monte_carlo, run_prophet_ai
    from backend.logic import analyze_smart_v36, analyze_fundamental
    from backend.stock_list import get_full_market_list
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_interactive_chart, render_market_overview, render_analysis_section
except ImportError as e:
    st.error(f"❌ SYSTEM CRITICAL ERROR: MISSING MODULES. \n{e}")
    st.stop()

# ==============================================================================
# 2. STATE MANAGEMENT (KHỞI TẠO BỘ NHỚ ĐỆM)
# ==============================================================================
# Biến lưu trữ kết quả quét Radar (Để không phải quét lại)
if 'radar_data' not in st.session_state:
    st.session_state['radar_data'] = pd.DataFrame() 

# Biến lưu trạng thái đăng nhập
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False

# Biến lưu danh sách quét mặc định
if 'scan_list' not in st.session_state: 
    st.session_state['scan_list'] = "HPG, SSI, FPT, MWG, VCB, STB, DIG, NVL, PDR, VIX, DGC, VND"

# ==============================================================================
# 3. SECURE AUTH LAYER (LOGIN & REGISTER - NEW)
# ==============================================================================
def render_auth_screen():
    """Màn hình xác thực Cyberpunk (Có Đăng Ký & Đăng Nhập)"""
    st.markdown("""
    <style>
        .login-box { max-width: 400px; margin: 50px auto; padding: 30px; background: rgba(0, 0, 0, 0.8); border: 1px solid #00f3ff; box-shadow: 0 0 30px rgba(0, 243, 255, 0.2); border-radius: 10px; }
        .login-title { font-family: 'Rajdhani', sans-serif; font-size: 28px; font-weight: 800; color: #fff; text-align: center; margin-bottom: 20px; text-shadow: 0 0 10px #00f3ff; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown('<div class="login-box"><div class="login-title">THANG LONG CITADEL</div>', unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 ĐĂNG NHẬP", "📝 ĐĂNG KÝ"])
        
        # --- FORM ĐĂNG NHẬP ---
        with tab_login:
            with st.form("login_form"):
                user = st.text_input("Tài khoản", placeholder="Username")
                pwd = st.text_input("Mật khẩu", type="password", placeholder="Password")
                if st.form_submit_button("ACCESS SYSTEM", type="primary", use_container_width=True):
                    success, info = login_user(user, pwd)
                    if success:
                        st.session_state['logged_in'] = True
                        # Lưu info user vào session để dùng sau
                        st.session_state['user_info'] = {"username": user, "name": info['name']}
                        st.success(f"Chào mừng {info['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("⛔ Sai tài khoản hoặc mật khẩu")

        # --- FORM ĐĂNG KÝ ---
        with tab_register:
            with st.form("reg_form"):
                new_user = st.text_input("Tạo Username", placeholder="VD: stock_master")
                new_pwd = st.text_input("Tạo Password", type="password")
                full_name = st.text_input("Họ và Tên", placeholder="Nguyễn Văn A")
                email = st.text_input("Email (Tùy chọn)")
                if st.form_submit_button("CREATE IDENTITY", use_container_width=True):
                    if new_user and new_pwd:
                        ok, msg = register_user(new_user, new_pwd, full_name, email)
                        if ok: st.success(msg)
                        else: st.error(msg)
                    else:
                        st.warning("Vui lòng nhập đủ thông tin.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# [QUAN TRỌNG] Gọi hàm này thay vì render_secure_login cũ
if not st.session_state['logged_in']:
    load_hardcore_css()
    # render_secure_login() <-- Xóa dòng cũ này đi
    render_auth_screen()      # <-- Thay bằng dòng mới này
    st.stop()
# ==============================================================================
# 4. MAIN COMMAND CENTER
# ==============================================================================
load_hardcore_css()
render_header()

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.markdown("### 🎛️ SYSTEM CONTROL")
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px; background:#111; padding:10px; border:1px solid #333;">
        <div style="width:10px; height:10px; background:#00ff41; border-radius:50%; box-shadow:0 0 5px #00ff41;"></div>
        <div style="color:#00ff41; font-family:Rajdhani; font-weight:700;">ONLINE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📡 TARGET SCANNER")
    
    # [TÍNH NĂNG MỚI] 1. QUÉT THEO NGÀNH (SECTOR SCAN)
    st.markdown("<span style='color:#00f3ff; font-size:12px'>⚡ QUÉT NHANH THEO NGÀNH</span>", unsafe_allow_html=True)
    
    # Lấy danh sách tên các ngành
    sector_options = ["-- Chọn Nhóm Ngành --"] + get_all_sector_names()
    selected_sector = st.selectbox("Chọn Hạm Đội:", sector_options, label_visibility="collapsed")
    
    # Logic: Nếu chọn ngành -> Tự động điền vào ô Watchlist
    if selected_sector != "-- Chọn Nhóm Ngành --":
        ticker_group = get_sector_list_data(selected_sector)
        st.session_state['scan_list'] = ", ".join(ticker_group)

    st.markdown("---") # Đường kẻ ngăn cách

    # [TÍNH NĂNG CŨ] 2. QUÉT THEO SÀN (EXCHANGE SCAN)
    st.markdown("<span style='color:#00f3ff; font-size:12px'>🏛️ HOẶC QUÉT TOÀN SÀN</span>", unsafe_allow_html=True)
    
    c_hose, c_hnx, c_upcom = st.columns(3)
    if c_hose.button("HOSE", key="btn_hose"): st.session_state['scan_list'] = ", ".join(get_full_market_list("HOSE"))
    if c_hnx.button("HNX", key="btn_hnx"): st.session_state['scan_list'] = ", ".join(get_full_market_list("HNX"))
    if c_upcom.button("UPCOM", key="btn_upcom"): st.session_state['scan_list'] = ", ".join(get_full_market_list("UPCOM"))
        
    # Ô INPUT HIỂN THỊ KẾT QUẢ (GIỮ NGUYÊN)
    st.text_area("WATCHLIST HIỆN TẠI:", value=st.session_state['scan_list'], height=100, key="txt_watchlist_display", disabled=True)
    
    # NÚT KÍCH HOẠT QUÉT (GIỮ NGUYÊN)
    if st.button("EXECUTE SCAN", key="btn_scan", type="primary", use_container_width=True):
        # Lấy dữ liệu từ session_state['scan_list']
        raw_list = st.session_state['scan_list']
        ticker_list = [t.strip().upper() for t in raw_list.split(',') if t.strip()]
        
        if ticker_list:
            with st.spinner("SCANNING TARGETS..."):
                st.session_state['radar_data'] = get_pro_data(ticker_list) 
            st.rerun()

    # (Phần Logout giữ nguyên)
    
    with st.expander("SYSTEM LOGS", expanded=True):
        st.markdown('<div style="font-family:monospace; font-size:10px; color:#555;">> SYSTEM_READY... OK<br>> DATABASE_LOADED... OK<br>> CACHE_CLEARED... OK</div>', unsafe_allow_html=True)

    # ... (Code nút LOGOUT cũ nằm ở trên) ...
    if st.button("LOGOUT / TERMINATE", key="btn_logout"):
        st.session_state['logged_in'] = False
        st.session_state['user_info'] = {}
        st.rerun()

# ======================================================
    # 👇 ADMIN HQ LEVEL 2 (GOD MODE - X-RAY VISION) 👇
    # ======================================================
    current_user = st.session_state.get('user_info', {}).get('username', '')
    
    # Thay 'admin' bằng tên tài khoản BOSS của ngài
    if current_user == "admin": 
        st.divider()
        st.markdown("### 🛡️ ADMIN HQ (GOD MODE)")
        
        # 1. DANH SÁCH TỔNG QUAN (USER LIST)
        with st.expander("👥 DANH SÁCH KHÁCH HÀNG", expanded=True):
            df_users = get_all_users_admin()
            if not df_users.empty:
                st.dataframe(df_users, hide_index=True, use_container_width=True)
            else:
                st.info("Chưa có user nào.")

        # 2. MÁY SOI VÍ (PORTFOLIO INSPECTOR) - [TÍNH NĂNG MỚI]
        st.markdown("#### 🔍 SOI VÍ KHÁCH HÀNG (X-RAY)")
        
        if not df_users.empty:
            # Chọn user để soi
            list_users = df_users["Username"].unique().tolist()
            
            # Chia cột: Chọn User và Nút Xóa nằm cạnh nhau
            c_adm_1, c_adm_2 = st.columns([3, 1])
            
            with c_adm_1:
                target_user = st.selectbox("Chọn đối tượng để kiểm tra:", list_users)
            
            with c_adm_2:
                st.write("") # Căn lề
                st.write("")
                # Nút xóa user (dời xuống đây cho tiện tay)
                if st.button("❌ XÓA USER", type="primary"):
                    if target_user == "admin":
                        st.error("Không thể tự sát!")
                    else:
                        delete_user_admin(target_user)
                        st.success(f"Đã tiễn {target_user} ra đảo!")
                        time.sleep(1)
                        st.rerun()

            # --- HIỂN THỊ CHI TIẾT VÍ CỦA NGƯỜI ĐÓ ---
            if target_user:
                st.markdown(f"Danh mục của: **{target_user}**")
                # Gọi hàm lấy portfolio của user đó (kèm tính lãi lỗ real-time luôn)
                df_target = get_user_portfolio(target_user)
                
                if not df_target.empty:
                    # Tính tổng tài sản của khách
                    total_nav = df_target['total_value'].sum()
                    total_pl = df_target['profit_loss'].sum()
                    
                    # Hiển thị dashboard nhỏ
                    m1, m2 = st.columns(2)
                    m1.metric("Tổng Tài Sản", f"{total_nav:,.0f} K")
                    m2.metric("Đang Lãi/Lỗ", f"{total_pl:,.0f} K", delta_color="normal")
                    
                    # Hiện bảng chi tiết
                    st.dataframe(
                        df_target,
                        column_config={
                            "symbol": "Mã",
                            "volume": "KL",
                            "price_avg": st.column_config.NumberColumn("Vốn", format="%.2f"),
                            "market_price": st.column_config.NumberColumn("Giá TT", format="%.2f"),
                            "profit_loss": st.column_config.NumberColumn("Lãi/Lỗ", format="%.0f"),
                            "percent_pl": st.column_config.NumberColumn("%", format="%.2f %%"),
                        },
                        hide_index=True, use_container_width=True
                    )
                else:
                    st.warning("Ví của đối tượng này đang trống (Chưa mua gì).")
        else:
            st.info("Hệ thống vắng tanh.")

    st.divider()
    
    # === NEW: LIVE TERMINAL LOG ===
    st.markdown("### 📟 SYSTEM TERMINAL")
    
    # Tạo nội dung Log giả lập ngẫu nhiên cho ngầu
    import random
    
    logs = [
        "[SYSTEM] Establishing secure uplink...",
        "[DATA] Fetching realtime ticks from HOSE...",
        "[AI] Neural Network V40 loaded.",
        "[ALERT] Volatility detected in Banking Sector.",
        "[SCAN] Searching for Shark footprints...",
        "[INFO] Latency: 12ms | Packet Loss: 0%",
        "[CRYPTO] Bitcoin correlation check: NEGATIVE",
        "[UPDATE] Financial Reports Q4 synced."
    ]
    
    # Chọn ngẫu nhiên 4 dòng để hiển thị
    active_logs = random.sample(logs, 4)
    log_html = "".join([f"<div style='margin-bottom:2px;'>{l}</div>" for l in active_logs])
    
    st.markdown(f"""
    <div style="
        background-color: #000;
        border: 1px solid #333;
        border-left: 3px solid #00ff41;
        padding: 10px;
        font-family: 'Courier New', monospace;
        font-size: 10px;
        color: #00ff41;
        height: 120px;
        overflow-y: hidden;
        text-shadow: 0 0 5px #00ff41;
        opacity: 0.8;
    ">
        <div style="border-bottom: 1px dashed #333; margin-bottom: 5px; color: #fff;">ROOT@THANGLONG:~# tail -f /var/log/syslog</div>
        {log_html}
        <div style="animation: blink 1s infinite;">_</div>
    </div>
    """, unsafe_allow_html=True)

# --- MARKET OVERVIEW ---
with st.spinner("UPDATING MARKET FEED..."):
    indices = get_market_indices()
    render_market_overview(indices)

    # === [NEW] CYBER TICKER: DÒNG CHẢY DỮ LIỆU (ĐÃ FIX HTML 1 DÒNG) ===
    if indices:
        # 1. Tạo chuỗi HTML từ dữ liệu Indices (Dùng f-string 1 dòng)
        ticker_items = []
        for i in indices:
            color = "#00ff41" if i['Change'] >= 0 else "#ff0055"
            arrow = "▲" if i['Change'] >= 0 else "▼"
            
            # [FIX QUAN TRỌNG]: Viết thành 1 dòng dài, không xuống dòng
            item_html = f"<span style='margin:0 15px; font-family:Rajdhani, sans-serif;'><span style='color:#00f3ff; font-weight:800;'>{i['Name']}</span> <span style='color:#fff; font-weight:600;'>{i['Price']:,.2f}</span> <span style='color:{color}; font-size:14px;'>{arrow} {abs(i['Pct']):.2f}%</span></span><span style='color:#333;'> // </span>"
            
            ticker_items.append(item_html)
        
        # Nối lại và nhân 3 để chạy vòng lặp
        ticker_content = "".join(ticker_items) * 3 

        # 2. Render CSS Animation
        st.markdown(f"""
        <style>
            .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; border-top: 1px solid #333; border-bottom: 1px solid #333; white-space: nowrap; box-sizing: border-box; height: 40px; display: flex; align-items: center; margin-bottom: 10px; }}
            .ticker-move {{ display: inline-block; white-space: nowrap; animation: ticker-scroll 30s linear infinite; }}
            .ticker-move:hover {{ animation-play-state: paused; }}
            @keyframes ticker-scroll {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-50%, 0, 0); }} }}
            .ticker-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, #0e1117 0%, transparent 5%, transparent 95%, #0e1117 100%); pointer-events: none; z-index: 2; }}
        </style>
        <div style="position: relative;">
            <div class="ticker-wrap">
                <div class="ticker-move">{ticker_content}</div>
            </div>
            <div class="ticker-overlay"></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ==============================================================================
# MAIN TABS: 3 KHU VỰC CHÍNH (ĐÃ THÊM TAB PORTFOLIO)
# ==============================================================================
main_tab1, main_tab2, main_tab3 = st.tabs([
    "🚀 STOCK COMMAND CENTER", 
    "💼 MY PORTFOLIO (SỔ TAY ĐẦU TƯ)", 
    "💰 TREASURE VAULT (GOLD/SILVER)"
])

# ==============================================================================
# TAB 1: STOCK COMMAND CENTER (TOÀN BỘ CODE CŨ NẰM Ở ĐÂY)
# ==============================================================================
with main_tab1:
    col_radar, col_analyst = st.columns([1.5, 2.5])

    # === LEFT PANE: RADAR (HIỂN THỊ TỪ BỘ NHỚ) ===
    with col_radar:
        st.markdown('<div class="glass-box"><h4>📡 MARKET RADAR</h4>', unsafe_allow_html=True)
        
        df_radar = st.session_state['radar_data']
        
        if not df_radar.empty:
            # CHỈ LẤY NHỮNG CỘT CẦN THIẾT
            df_display = df_radar[["Symbol", "Price", "Pct", "Signal", "Score", "Trend"]]

            st.dataframe(
                df_display,
                column_config={
                    "Symbol": st.column_config.TextColumn("SYM", width="small", help="Mã cổ phiếu"),
                    "Price": st.column_config.NumberColumn("PRICE", format="%.2f", width="small"),
                    "Pct": st.column_config.NumberColumn("%", format="%.2f %%", width="small"),
                    "Signal": st.column_config.TextColumn("ACTION", width="medium"),
                    "Score": st.column_config.ProgressColumn("POWER", format="%d/10", min_value=0, max_value=10, width="medium"),
                    "Trend": st.column_config.LineChartColumn("MINI CHART", width="large")
                },
                hide_index=True,
                use_container_width=True,
                height=400 
            )

            # 👉 HIỂN THỊ GALAXY 3D
            st.markdown("---") 
            render_market_galaxy(df_radar)
            
        else:
            # Nếu chưa có dữ liệu
            st.info("AWAITING SCAN COMMAND...")
            st.caption("Please click 'EXECUTE SCAN' on the sidebar.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # === RIGHT PANE: ANALYST CENTER (ĐỘC LẬP) ===
    with col_analyst:
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        
        target_symbol = "HPG" # Giá trị mặc định
        
        # Nếu Radar có dữ liệu -> Chọn từ Radar
        if not df_radar.empty:
            symbol_list = df_radar['Symbol'].tolist()
            # Selectbox này thay đổi sẽ KHÔNG kích hoạt lại việc quét Radar
            target_symbol = st.selectbox("SELECT TARGET FROM RADAR", symbol_list)
        # Nếu Radar trống -> Nhập tay
        else:
            target_symbol = st.text_input("MANUAL TARGET ENTRY", value="HPG").upper()

        if target_symbol:
            st.markdown(f"<h1 style='color:#00f3ff; margin-top:-10px; font-family:Rajdhani; text-shadow:0 0 10px #00f3ff;'>{target_symbol} // DEEP DIVE</h1>", unsafe_allow_html=True)
            
            # Phần xử lý dữ liệu chi tiết cho 1 mã
            hist_df = get_history_df(target_symbol)
            info, fin, bal, cash, divs, splits = get_stock_data_full(target_symbol)
            
            tech_res = analyze_smart_v36(hist_df)
            from backend.logic import analyze_fundamental_full
            fund_res = analyze_fundamental_full(info, fin, bal, cash)

            if tech_res and fund_res:
                render_analysis_section(tech_res, fund_res)
            
            st.markdown("---")

            t1, t2, t3, t4, t5, t6, t7 = st.tabs(["CHART", "TRADINGVIEW", "AI_PROPHET", "MONTE_CARLO", "NEWS", "FINANCIALS", "PROFILE"])
            
            # TAB 1: CHART (Crosshair Neon)
            with t1: render_interactive_chart(hist_df, target_symbol)
            
            # TAB 2: TV
            with t2:
                components.html(f"""<div class="tradingview-widget-container"><div id="tv_widget"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width":"100%","height":550,"symbol":"HOSE:{target_symbol}","interval":"D","theme":"dark","style":"1","locale":"en","toolbar_bg":"#f1f3f6","enable_publishing":false,"container_id":"tv_widget"}});</script></div>""", height=560)
            
            # TAB 3: AI (Crosshair Neon + Time Selector)
            with t3:
                st.markdown("### 🔮 NEURAL NETWORK FORECAST")
                
                # [NEW] CHỌN KHUNG THỜI GIAN DỰ BÁO
                c_ai_1, c_ai_2 = st.columns([1, 3])
                
                with c_ai_1:
                    # Hộp chọn thời gian
                    time_option = st.selectbox(
                        "⏳ TẦM NHÌN (TIMEFRAME)",
                        ["3 Tháng (90 ngày)", "6 Tháng (180 ngày)", "12 Tháng (1 Năm)", "1 Tháng (30 ngày)"],
                        index=0 # Mặc định chọn 3 tháng
                    )
                    
                    # Mapping từ chữ sang số ngày
                    days_map = {
                        "1 Tháng (30 ngày)": 30,
                        "3 Tháng (90 ngày)": 90,
                        "6 Tháng (180 ngày)": 180,
                        "12 Tháng (1 Năm)": 365
                    }
                    selected_days = days_map[time_option]

                with c_ai_2:
                    st.write("") # Căn lề cho nút bấm thẳng hàng
                    st.write("")
                    # Nút bấm kích hoạt
                    if st.button(f"🚀 KÍCH HOẠT AI ({selected_days} NGÀY)", key="btn_ai", type="primary"):
                        with st.spinner(f"ĐANG TÍNH TOÁN DỰ BÁO {selected_days} NGÀY TỚI..."):
                            # Truyền số ngày (selected_days) vào hàm AI
                            fig_ai = run_prophet_ai(hist_df, periods=selected_days)
                            
                            if fig_ai: 
                                st.plotly_chart(fig_ai, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                            else: 
                                st.error("DỮ LIỆU KHÔNG ĐỦ ĐỂ DỰ BÁO XA")
            
            # TAB 4: MONTE CARLO
            with t4:
                st.markdown("### 🌌 MULTIVERSE SIMULATION")
                if st.button("RUN SIMULATION", key="btn_mc"):
                    fig_mc, fig_hist, stats = run_monte_carlo(hist_df)
                    if fig_mc:
                        st.plotly_chart(fig_mc, use_container_width=True)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("MEAN", f"{stats['mean']:,.0f}")
                        m2.metric("UPSIDE (95%)", f"{stats['top_5']:,.0f}")
                        m3.metric("PROBABILITY", f"{stats['prob_up']:.1f}%")
                        st.plotly_chart(fig_hist, use_container_width=True)
            
            # TAB 5: NEWS
            with t5:
                news = get_stock_news_google(target_symbol)
                if news:
                    for n in news: st.markdown(f"- [{n['title']}]({n['link']})")
                else: st.info("NO NEWS DATA.")
                
            # TAB 6: FINANCE
            with t6:
                if not fin.empty: 
                    st.dataframe(fin.iloc[:, :4], use_container_width=True)
                else: st.warning("NO FINANCIAL DATA.")
                
            # TAB 7: PROFILE
            with t7:
                c1, c2 = st.columns(2)
                with c1: st.info(f"SECTOR: {info.get('sector', 'N/A')}")
                with c2: 
                    if not divs.empty: st.bar_chart(divs.head(10))

        st.markdown('</div>', unsafe_allow_html=True)
# === TAB 2: MY PORTFOLIO (SỔ TAY ĐẦU TƯ) - [CÓ NÚT BÁN] ===
with main_tab2:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    # Import hàm xóa mới (Lưu ý: Ngài nhớ thêm delete_portfolio_stock vào dòng import đầu file app.py nhé)
    from backend.database import delete_portfolio_stock 
    
    user_name = st.session_state.get('user_info', {}).get('name', 'Unknown')
    current_user = st.session_state.get('user_info', {}).get('username', '')

    # Header
    c_p1, c_p2 = st.columns([3, 1])
    with c_p1: st.markdown(f"### 💼 DANH MỤC ĐẦU TƯ CỦA: <span style='color:#00f3ff'>{user_name}</span>", unsafe_allow_html=True)
    with c_p2: 
        if st.button("🔄 CẬP NHẬT P/L", use_container_width=True): st.rerun()

    col_input, col_table = st.columns([1, 2])
    
    # --- CỘT TRÁI: KHU VỰC GIAO DỊCH ---
    with col_input:
        # Chia làm 2 tab con: MUA và BÁN
        tab_buy, tab_sell = st.tabs(["🟢 NHẬP MUA", "🔴 BÁN / XÓA"])
        
        # 1. FORM MUA (Code cũ)
        with tab_buy:
            with st.form("portfolio_add"):
                p_symbol = st.text_input("Mã CK (VD: HPG)", max_chars=3).upper()
                p_vol = st.number_input("Khối lượng", min_value=10, step=100)
                p_price = st.number_input("Giá vốn (Nghìn VNĐ)", min_value=0.0, step=0.1, format="%.2f")
                
                if st.form_submit_button("LƯU VÀO VÍ", type="primary", use_container_width=True):
                    if p_symbol and p_vol > 0:
                        ok = add_transaction(current_user, p_symbol, p_vol, p_price)
                        if ok: st.success(f"Đã mua {p_symbol}!")
                        else: st.error("Lỗi hệ thống.")
                        time.sleep(1)
                        st.rerun()

        # 2. FORM BÁN (MỚI TINH)
        with tab_sell:
            st.info("Chọn mã cổ phiếu đã bán để xóa khỏi danh sách theo dõi.")
            
            # Lấy danh sách các mã đang có trong ví để hiển thị vào Selectbox
            df_temp = get_user_portfolio(current_user)
            if not df_temp.empty:
                my_stock_list = df_temp['symbol'].unique().tolist()
                stock_to_sell = st.selectbox("Chọn mã cần xóa", my_stock_list)
                
                if st.button(f"🗑️ XÓA {stock_to_sell} KHỎI VÍ", type="secondary", use_container_width=True):
                    delete_portfolio_stock(current_user, stock_to_sell)
                    st.success(f"Đã xóa {stock_to_sell} thành công!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Ví đang trống, chưa có gì để bán.")

    # --- CỘT PHẢI: BẢNG DANH MỤC (GIỮ NGUYÊN) ---
    with col_table:
        st.markdown("#### 📊 HIỆU SUẤT REAL-TIME")
        
        if current_user:
            df_port = get_user_portfolio(current_user)
            
            if not df_port.empty:
                total_invest = df_port['cost_value'].sum()
                total_pl = df_port['profit_loss'].sum()
                total_pct = (total_pl / total_invest * 100) if total_invest > 0 else 0
                
                m1, m2 = st.columns(2)
                m1.metric("TỔNG VỐN", f"{total_invest:,.0f} K")
                m2.metric("LÃI/LỖ TỔNG", f"{total_pl:,.0f} K", f"{total_pct:.2f}%")
                
                st.dataframe(
                    df_port,
                    column_config={
                        "symbol": "Mã CK",
                        "volume": "Khối lượng",
                        "price_avg": st.column_config.NumberColumn("Giá Vốn", format="%.2f"),
                        "market_price": st.column_config.NumberColumn("Giá TT", format="%.2f"),
                        "profit_loss": st.column_config.NumberColumn("Lãi/Lỗ", format="%.0f"),
                        "percent_pl": st.column_config.NumberColumn("% Lãi", format="%.2f %%"),
                    },
                    hide_index=True, use_container_width=True
                )
            else:
                st.info("Ví trống. Hãy nhập lệnh mua bên trái!")

    st.markdown('</div>', unsafe_allow_html=True)
# ==============================================================================
# === TAB 3: TREASURE VAULT (CODE CŨ CỦA NGÀI - CHUYỂN TỪ main_tab2 SANG main_tab3) ===
with main_tab3:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    # HEADER CÓ NÚT BẤM
    c_title, c_btn = st.columns([3, 1])
    with c_title:
        st.markdown("### 🏆 PRECIOUS METALS (REAL-TIME)")
    with c_btn:
        if st.button("🔄 CẬP NHẬT (LIVE)", type="primary", use_container_width=True):
            st.rerun()

    col_gold, col_silver = st.columns(2)
    
    # --- 1. KHO VÀNG (SJC/PNJ) ---
    with col_gold:
        st.markdown("""<div style='background: linear-gradient(45deg, #FFD700, #B8860B); padding: 10px; border-radius: 5px; color: black; font-weight: bold; text-align: center; margin-bottom: 10px;'>👑 GOLD PRICE (WEB-GIA)</div>""", unsafe_allow_html=True)
        
        df_gold = get_gold_price()
        
        # [CHECK] Nếu có dữ liệu thì hiện bảng, không thì báo lỗi
        if not df_gold.empty:
            st.dataframe(
                df_gold,
                column_config={
                    "Loại vàng": st.column_config.TextColumn("Loại Vàng", width="medium"),
                    "Mua vào": st.column_config.TextColumn("Giá Mua", width="small"),
                    "Bán ra": st.column_config.TextColumn("Giá Bán", width="small"),
                },
                hide_index=True, use_container_width=True, height=500
            )
        else:
            st.error("⚠️ KHÔNG LẤY ĐƯỢC DỮ LIỆU VÀNG")
            st.caption("Kiểm tra kết nối mạng hoặc nguồn webgia.com đang bảo trì.")

    # --- 2. KHO BẠC (PHÚ QUÝ) ---
    with col_silver:
        st.markdown("""<div style='background: linear-gradient(45deg, #C0C0C0, #708090); padding: 10px; border-radius: 5px; color: black; font-weight: bold; text-align: center; margin-bottom: 10px;'>🥈 SILVER PRICE (PHU QUY)</div>""", unsafe_allow_html=True)
        
        df_silver = get_silver_price()
        
        # [CHECK]
        if not df_silver.empty:
            st.dataframe(
                df_silver,
                column_config={
                    "SẢN PHẨM": st.column_config.TextColumn("Sản Phẩm", width="medium"),
                    "ĐƠN VỊ": st.column_config.TextColumn("ĐVT", width="small"),
                    "GIÁ MUA VÀO": st.column_config.TextColumn("Mua Vào", width="small"),
                    "GIÁ BÁN RA": st.column_config.TextColumn("Bán Ra", width="small"),
                },
                hide_index=True, use_container_width=True, height=500
            )
        else:
            st.error("⚠️ KHÔNG LẤY ĐƯỢC DỮ LIỆU BẠC")
            st.caption("Không thể kết nối đến máy chủ Phu Quy Group.")
    
    st.markdown("---")
    st.caption("ℹ️ Chế độ Strict Mode: Chỉ hiển thị dữ liệu thực tế tại thời điểm bấm nút.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center; color:#444; font-size:10px; margin-top:50px;">THANG LONG TERMINAL SYSTEM V36.7 // ENCRYPTED</div>', unsafe_allow_html=True)

# ==============================================================================
# 5. FOOTER (THANH TRẠNG THÁI NGANG - CYBER COMMANDER STYLE)
# ==============================================================================
st.markdown("""
<style>
    /* 1. Ẩn footer mặc định của Streamlit */
    footer {visibility: hidden;}

    /* 2. Tạo thanh footer mới cố định ở đáy */
    .cyber-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0a0a0a; /* Nền đen tối */
        color: #888;                /* Màu chữ xám mặc định */
        text-align: center;
        padding: 10px 0;
        font-family: 'Rajdhani', sans-serif;
        font-size: 14px;
        letter-spacing: 1px;
        border-top: 1px solid #333; /* Viền trên nhẹ */
        z-index: 9999; /* Đảm bảo luôn nổi lên trên cùng */
    }

    /* 3. Hiệu ứng Neon cho chữ THANGLONG */
    .neon-green {
        color: #00ff41; /* Xanh lá neon */
        font-weight: 700;
        text-shadow: 0 0 5px #00ff41, 0 0 10px #00ff41; /* Hiệu ứng phát sáng */
    }
</style>

<div class="cyber-footer">
    🚀 TL-TERMINAL | DEVELOPED BY <span class="neon-green">THANGLONG</span> | © 2026
</div>
""", unsafe_allow_html=True)
