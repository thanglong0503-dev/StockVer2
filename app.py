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

import streamlit as st
import sys
import os
import time
import pandas as pd
import streamlit.components.v1 as components

# ==============================================================================
# QUẢN LÝ IMPORT MODULES CỦA HỆ THỐNG
# ==============================================================================
from frontend.components import render_market_galaxy
from backend.commodities import get_gold_price, get_silver_price
from backend.sectors import get_full_market_list, get_all_sector_names, get_sector_list_data

# Gộp toàn bộ hàm Database vào 1 khối cho gọn, XÓA SẠCH đồ thừa của Prophet
from backend.database import (
    init_admin_account, 
    register_user, 
    login_user, 
    get_all_users_admin, 
    delete_user_admin,
    add_transaction, 
    get_user_portfolio, 
    delete_portfolio_stock,
    save_user_note, 
    get_user_note,
    save_search_history, 
    get_search_history
)

# Gọi hàm này để chắc chắn Admin luôn tồn tại
init_admin_account()
# --- ĐỘNG CƠ TÍNH CHỈ BÁO SỢ HÃI & THAM LAM (ĐÃ NÂNG CẤP ĐỘ NHẠY) ---
import numpy as np # Đảm bảo trên đầu file app.py của ngài có import numpy as np

@st.cache_data(ttl=1800) # Cứ 30 phút cập nhật tâm lý 1 lần cho nhẹ máy
def get_fear_greed_index():
    try:
        # Lấy 4 trụ lớn nhất + Thêm SSI (Ông hoàng nhạy sóng ngành Chứng khoán)
        symbols = ['VCB.VN', 'VHM.VN', 'VIC.VN', 'HPG.VN', 'SSI.VN']
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=45)
        
        data = yf.download(symbols, start=start_date, end=end_date, progress=False)
        if data.empty: return 50, "TRUNG TÍNH", "#aaaaaa"
        
        # Lấy đúng cột Close bất chấp định dạng cũ hay mới của yfinance
        if 'Close' in data:
            close_df = data['Close']
        else:
            return 50, "TRUNG TÍNH", "#aaaaaa"
            
        score_list = []
        for sym in symbols:
            # Bỏ qua nếu mã này bị lỗi không có dữ liệu
            if sym not in close_df.columns: continue 
            close_p = close_df[sym].dropna()
            if len(close_p) < 15: continue
            
            # 1. TÍNH CHỈ SỐ NỀN TẢNG (RSI 14)
            delta = close_p.diff()
            gain = delta.clip(lower=0).rolling(window=14).mean()
            loss = -delta.clip(upper=0).rolling(window=14).mean()
            
            # Thay thế 0 bằng NaN để tránh lỗi chia cho 0 (Silent Error)
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            if pd.isna(current_rsi): current_rsi = 50
            
            # 2. TÍNH CÚ SỐC TÂM LÝ (MOMENTUM SHOCK)
            # Biến động % của ngày hôm nay so với hôm qua
            daily_return = (close_p.iloc[-1] - close_p.iloc[-2]) / close_p.iloc[-2] * 100
            
            # Hệ số nhân: Giảm 1% -> trừ 5 điểm tâm lý. Sàn (-7%) -> Trừ thẳng 35 điểm tâm lý!
            shock_factor = daily_return * 5 
            
            # Trộn lẫn Xu hướng (RSI) và Cảm xúc (Shock)
            final_sym_score = current_rsi + shock_factor
            
            # Ép điểm số không được vượt quá 100 hoặc nhỏ hơn 0
            final_sym_score = max(0, min(100, final_sym_score))
            score_list.append(final_sym_score)
            
        if not score_list: return 50, "TRUNG TÍNH", "#aaaaaa"
        
        # Tính điểm trung bình (0 - 100)
        score = int(sum(score_list) / len(score_list))
        
        # Phân loại tâm lý (Tinh chỉnh biên độ hẹp lại để nhạy bén hơn)
        if score <= 25: return score, "SỢ HÃI TỘT ĐỘ", "#ff3366"  # Đỏ rực
        elif score <= 45: return score, "SỢ HÃI", "#ffbc00"       # Cam
        elif score <= 55: return score, "TRUNG TÍNH", "#aaaaaa"   # Xám bạc
        elif score <= 75: return score, "THAM LAM", "#28c840"     # Xanh lá
        else: return score, "THAM LAM TỘT ĐỘ", "#00d2ff"          # Xanh lam
        
    except Exception as e:
        # Nếu có lỗi lặt vặt thì mặc định báo Trung tính để app không bị sập
        return 50, "TRUNG TÍNH", "#aaaaaa"
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
# --- ĐỘ GIAO DIỆN (UI/UX CUSTOMIZATION PRO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap');

    /* 1. Ép font cho toàn bộ thanh Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* 2. Ép font cho tất cả các Tiêu đề (H1 - H6) trong App và Sidebar */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important; /* Viết hoa toàn bộ cho ngầu */
        letter-spacing: 1px !important;
    }
    
    /* 3. Chỉnh nhẹ màu cho các chữ nổi bật */
    .stMarkdown p strong {
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 0.5px !important;
    }
</style>
""", unsafe_allow_html=True)
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
# ==============================================================================
# 4. MAIN COMMAND CENTER
# ==============================================================================
load_hardcore_css()

# Gọi tính toán
fg_score, fg_label, fg_color = get_fear_greed_index()

# Truyền vào hàm để tự nó vẽ
render_header(fg_score, fg_label, fg_color)

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.markdown("### ⎛ SYSTEM CONTROL")
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px; background:#111; padding:10px; border:1px solid #333;">
        <div style="width:10px; height:10px; background:#00ff41; border-radius:50%; box-shadow:0 0 5px #00ff41;"></div>
        <div style="color:#00ff41; font-family:Rajdhani; font-weight:700;">ONLINE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⌖ TARGET SCANNER")
    
    # 1. QUÉT THEO NGÀNH (Logic Fix: Chỉ cập nhật khi thay đổi lựa chọn)
    st.markdown("<span style='color:#00f3ff; font-size:12px'>⟁ QUÉT NHANH THEO NGÀNH</span>", unsafe_allow_html=True)
    
    # Khởi tạo biến theo dõi nếu chưa có
    if 'prev_sector' not in st.session_state: st.session_state['prev_sector'] = "NONE"

    sector_options = ["-- Chọn Nhóm Ngành --"] + get_all_sector_names()
    selected_sector = st.selectbox("Chọn Hạm Đội:", sector_options, label_visibility="collapsed")
    
    # [FIX QUAN TRỌNG] Chỉ chạy lệnh khi ngài THỰC SỰ đổi lựa chọn khác
    if selected_sector != st.session_state['prev_sector']:
        st.session_state['prev_sector'] = selected_sector # Lưu lại cái mới chọn
        if selected_sector != "-- Chọn Nhóm Ngành --":
            ticker_group = get_sector_list_data(selected_sector)
            st.session_state['scan_list'] = ", ".join(ticker_group)
            st.rerun() # Tải lại trang ngay để hiện list

    st.markdown("---")

    # 2. QUÉT THEO SÀN (Nút bấm được ưu tiên)
    st.markdown("<span style='color:#00f3ff; font-size:12px'>▤ HOẶC QUÉT TOÀN SÀN</span>", unsafe_allow_html=True)
    
    c_hose, c_hnx, c_upcom = st.columns(3)
    
    # Thêm st.rerun() vào sau mỗi nút để Text Area cập nhật ngay lập tức
    if c_hose.button("HOSE", key="btn_hose"): 
        st.session_state['scan_list'] = ", ".join(get_full_market_list("HOSE"))
        st.rerun()
        
    if c_hnx.button("HNX", key="btn_hnx"): 
        st.session_state['scan_list'] = ", ".join(get_full_market_list("HNX"))
        st.rerun()

    if c_upcom.button("UPCOM", key="btn_upcom"): 
        st.session_state['scan_list'] = ", ".join(get_full_market_list("UPCOM"))
        st.rerun()
     # 👇 DÁN ĐOẠN NÀY VÀO DƯỚI 3 NÚT BẤM SÀN 👇
    
    st.markdown("---") # Kẻ ngang cho đẹp

    # HIỂN THỊ LIST HIỆN TẠI (Để ngài biết đang chuẩn bị quét cái gì)
    st.text_area("WATCHLIST HIỆN TẠI:", value=st.session_state['scan_list'], height=100, key="txt_watchlist_display", disabled=True)
    
    # 🔴 NÚT KÍCH HOẠT QUÉT (QUAN TRỌNG NHẤT)
    if st.button("EXECUTE SCAN", key="btn_scan", type="primary", use_container_width=True):
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
# MAIN TABS: 4 KHU VỰC CHIẾN LƯỢC
# ==============================================================================
# Khai báo Tab với Icon Unicode Đơn sắc (Monochromatic)
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6, main_tab7 = st.tabs([
    "⎈ COMMAND CENTER",     # Icon Bánh lái / Radar
    "⌗ MY PORTFOLIO",       # Icon Lưới dữ liệu
    "⛃ TREASURE VAULT",     # Icon Database / Khối tài sản
    "⚙ CÔNG CỤ & GHI CHÚ",    # Icon Bánh răng hệ thống
    "◳ TRÌNH DUYỆT",        # Icon Cửa sổ màn hình
    "⚡ TỔNG HỢP GIAO DỊCH",   # Icon Tia chớp xung nhịp
    "◴ KIỂM ĐỊNH (BACKTEST)" # Icon Đồng hồ thời gian
])

# ==============================================================================
# TAB 1: STOCK COMMAND CENTER (TOÀN BỘ CODE CŨ NẰM Ở ĐÂY)
# ==============================================================================
with main_tab1:
    col_radar, col_analyst = st.columns([1.5, 2.5])

    # === LEFT PANE: RADAR (HIỂN THỊ TỪ BỘ NHỚ) ===
    with col_radar:
        st.markdown('<div class="glass-box"><h4>⌖ MARKET RADAR</h4>', unsafe_allow_html=True)
        
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
            
            # TAB 2: TRADINGVIEW BẢN FULL (ADVANCED CHART ĐỘC LẬP)
            with t2:
                # Không cần st.text_input nữa, dùng luôn thanh Search của chính TradingView!
                components.html("""
                <div class="tradingview-widget-container" style="height:100%;width:100%">
                  <div id="tradingview_advanced" style="height:750px;width:100%"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget(
                  {
                  "autosize": true,
                  "symbol": "BINANCE:BTCUSDT",
                  "interval": "D",
                  "timezone": "Asia/Ho_Chi_Minh",
                  "theme": "dark",
                  "style": "1",
                  "locale": "vi_VN",
                  "enable_publishing": false,
                  "backgroundColor": "#131722",
                  "gridColor": "#1f293d",
                  "hide_top_toolbar": false,
                  "hide_legend": false,
                  "save_image": false,
                  "container_id": "tradingview_advanced",
                  "withdateranges": true,
                  "hide_side_toolbar": false,
                  "allow_symbol_change": true,
                  "details": true,
                  "hotlist": true,
                  "calendar": false,
                  "show_popup_button": true,
                  "popup_width": "1000",
                  "popup_height": "650"
                }
                  );
                  </script>
                </div>
                """, height=800)
            
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
                    if st.button(f"⎋ KÍCH HOẠT AI ({selected_days} NGÀY)", key="btn_ai", type="primary"):
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
# === TAB 2: MY PORTFOLIO (SỔ TAY ĐẦU TƯ) - [BẢN NÂNG CẤP ASSET MANAGEMENT] ===
        with main_tab2:
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            
            from backend.database import delete_portfolio_stock 
            
            user_name = st.session_state.get('user_info', {}).get('name', 'Unknown')
            current_user = st.session_state.get('user_info', {}).get('username', '')

            # Header
            c_p1, c_p2 = st.columns([3, 1])
            with c_p1: st.markdown(f"### 💼 TỔNG TÀI SẢN (NAV): <span style='color:#00f3ff'>{user_name}</span>", unsafe_allow_html=True)
            with c_p2: 
                if st.button("🔄 LÀM MỚI BẢNG GIÁ", use_container_width=True): st.rerun()

            # Lấy dữ liệu từ Database mới (Bây giờ nó nhả ra 2 biến)
            df_port, total_realized_pl = get_user_portfolio(current_user)

            # --- KHU VỰC 1: BẢNG TỔNG QUAN (DASHBOARD) ---
            if not df_port.empty:
                total_invest = df_port['cost_value'].sum()
                total_unrealized_pl = df_port['profit_loss'].sum()
                total_nav = total_invest + total_unrealized_pl + total_realized_pl # NAV = Giá trị cổ phiếu + Tiền lãi đã chốt
                total_pct = (total_unrealized_pl / total_invest * 100) if total_invest > 0 else 0
                
                # 4 Ô Metric hoành tráng
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💰 TỔNG NAV", f"{total_nav:,.0f} K")
                m2.metric("💳 VỐN ĐẦU TƯ", f"{total_invest:,.0f} K")
                m3.metric("📈 ĐANG TẠM LÃI/LỖ", f"{total_unrealized_pl:,.0f} K", f"{total_pct:.2f}%")
                m4.metric("🏦 ĐÃ CHỐT LỜI/LỖ", f"{total_realized_pl:,.0f} K")
                
                st.markdown("---")

            col_input, col_table = st.columns([1, 2])
            
            # --- CỘT TRÁI: KHU VỰC GIAO DỊCH (NHẬP MUA / BÁN) ---
            with col_input:
                tab_buy, tab_sell, tab_delete = st.tabs(["🟢 MUA", "🔴 BÁN", "🗑️ XÓA LỖI"])
                
                # 1. FORM MUA
                with tab_buy:
                    with st.form("portfolio_buy"):
                        p_symbol = st.text_input("Mã CK (VD: HPG)", max_chars=3).upper()
                        p_vol = st.number_input("Khối lượng MUA", min_value=10, step=100)
                        p_price = st.number_input("Giá vốn (Nghìn VNĐ)", min_value=0.0, step=0.1, format="%.2f")
                        if st.form_submit_button("XÁC NHẬN MUA", type="primary", use_container_width=True):
                            if p_symbol and p_vol > 0:
                                ok = add_transaction(current_user, p_symbol, p_vol, p_price, action="BUY")
                                if ok: st.success(f"Đã mua {p_vol} {p_symbol}!")
                                else: st.error("Lỗi hệ thống.")
                                time.sleep(1)
                                st.rerun()

                # 2. FORM BÁN CHỐT LỜI (Ghi nhận Realized P/L)
                with tab_sell:
                    if not df_port.empty:
                        with st.form("portfolio_sell"):
                            # Lấy danh sách mã đang cầm
                            my_stock_list = df_port['symbol'].unique().tolist()
                            sell_symbol = st.selectbox("Chọn mã BÁN", my_stock_list)
                            
                            # Hiển thị số lượng tối đa đang có (gợi ý)
                            max_vol = int(df_port[df_port['symbol'] == sell_symbol]['volume'].iloc[0])
                            
                            sell_vol = st.number_input(f"Khối lượng BÁN (Tối đa: {max_vol})", min_value=10, max_value=max_vol, step=100)
                            sell_price = st.number_input("Giá bán (Nghìn VNĐ)", min_value=0.0, step=0.1, format="%.2f")
                            
                            if st.form_submit_button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                                if sell_vol > 0 and sell_price > 0:
                                    ok = add_transaction(current_user, sell_symbol, sell_vol, sell_price, action="SELL")
                                    if ok: st.success(f"Đã chốt {sell_vol} {sell_symbol}!")
                                    else: st.error("Lỗi hệ thống.")
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.warning("Ví đang trống, không có hàng để bán.")
                        
                # 3. FORM XÓA (Chỉ dùng khi nhập sai)
                with tab_delete:
                    if not df_port.empty:
                        del_symbol = st.selectbox("Chọn mã XÓA BỎ HOÀN TOÀN", df_port['symbol'].unique().tolist())
                        st.caption("⚠️ Nút này sẽ xóa toàn bộ lịch sử mua/bán của mã này. Chỉ dùng khi nhập sai.")
                        if st.button(f"🗑️ XÓA SẠCH {del_symbol}", type="secondary", use_container_width=True):
                            delete_portfolio_stock(current_user, del_symbol)
                            st.success("Đã xóa hoàn toàn!")
                            time.sleep(1)
                            st.rerun()

            # --- CỘT PHẢI: BẢNG DANH MỤC & BIỂU ĐỒ HIỆU SUẤT ---
            with col_table:
                if not df_port.empty:
                    # 1. ĐƯA BẢNG CHI TIẾT LÊN TRÊN (Để ngài dễ nhìn số liệu thực tế trước)
                    st.dataframe(
                        df_port[['symbol', 'volume', 'price_avg', 'market_price', 'profit_loss', 'percent_pl']],
                        column_config={
                            "symbol": "Mã CK",
                            "volume": "Số lượng",
                            "price_avg": st.column_config.NumberColumn("Giá Vốn", format="%.2f"),
                            "market_price": st.column_config.NumberColumn("Giá TT", format="%.2f"),
                            "profit_loss": st.column_config.NumberColumn("Tạm Lãi/Lỗ", format="%.0f"),
                            "percent_pl": st.column_config.NumberColumn("% Hiệu suất", format="%.2f %%"),
                        },
                        hide_index=True, use_container_width=True
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 2. VẼ 2 BIỂU ĐỒ DẠNG LINE (TĂNG TRƯỞNG & NAV)
                    import plotly.express as px
                    import yfinance as yf
                    import datetime
                    
                    symbols = df_port['symbol'].tolist()
                    volumes = df_port.set_index('symbol')['volume'].to_dict()
                    
                    # Lấy dữ liệu 3 tháng (90 ngày) gần nhất để vẽ đường
                    end_date = datetime.datetime.now()
                    start_date = end_date - datetime.timedelta(days=90)
                    
                    try:
                        tickers = [f"{sym}.VN" for sym in symbols]
                        hist_data = yf.download(tickers, start=start_date, end=end_date, progress=False)
                        
                        if 'Close' in hist_data:
                            close_df = hist_data['Close']
                        else:
                            close_df = hist_data
                            
                        # Nếu ví chỉ có 1 mã thì yfinance trả về Series, cần bọc lại thành DataFrame
                        if isinstance(close_df, pd.Series):
                            close_df = close_df.to_frame(name=tickers[0])
                            
                        # Dọn dẹp tên cột và quy đổi giá về Nghìn VNĐ
                        close_df.columns = [c.replace('.VN', '') for c in close_df.columns]
                        close_df = close_df / 1000.0
                        close_df = close_df.ffill() # Điền dữ liệu rỗng cho các ngày T7, CN
                        
                        # --- TÍNH TOÁN ĐƯỜNG CHỈ SỐ ---
                        # 1. Đường Tổng Tài Sản (NAV = Số lượng hiện tại * Giá từng ngày trong quá khứ)
                        nav_series = pd.Series(0.0, index=close_df.index)
                        for sym in symbols:
                            if sym in close_df.columns:
                                nav_series += close_df[sym] * volumes[sym]
                                
                        # 2. Đường % Lợi nhuận (Biến động chuẩn hóa Base 0 so với 90 ngày trước)
                        pct_df = (close_df / close_df.iloc[0] - 1) * 100
                        
                        # --- HIỂN THỊ CHẺ ĐÔI (ĐÃ MỞ KHÓA ZOOM & KÉO THẢ) ---
                        c_chart1, c_chart2 = st.columns(2)
                        
                        with c_chart1:
                            # Biểu đồ 1: Các đường Line của từng cổ phiếu
                            fig1 = px.line(pct_df, title="📈 % Hiệu suất từng mã (3 Tháng)", template="plotly_dark")
                            fig1.update_layout(
                                height=350, margin=dict(l=10, r=10, t=40, b=10), 
                                yaxis_title="% Lợi nhuận", showlegend=False,
                                hovermode="x unified", # Gióng hàng ngang dọc khi trỏ chuột
                                dragmode="zoom"        # Chế độ mặc định là bôi đen để zoom
                            )
                            # BẬT SCROLL ZOOM & TOOLBAR
                            st.plotly_chart(fig1, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                            
                        with c_chart2:
                            # Biểu đồ 2: Tăng trưởng Tổng tài sản có đổ bóng mờ (Area Line)
                            fig2 = px.line(x=nav_series.index, y=nav_series.values, title="💰 Tăng trưởng NAV Quy Chiếu", template="plotly_dark")
                            fig2.update_traces(line_color='#00f3ff', fill='tozeroy', fillcolor='rgba(0, 243, 255, 0.1)') 
                            fig2.update_layout(
                                height=350, margin=dict(l=10, r=10, t=40, b=10), 
                                yaxis_title="Nghìn VNĐ", xaxis_title="",
                                hovermode="x unified", # Gióng hàng ngang dọc khi trỏ chuột
                                dragmode="zoom"        # Chế độ mặc định là bôi đen để zoom
                            )
                            # BẬT SCROLL ZOOM & TOOLBAR
                            st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                            
                    except Exception as e:
                        st.caption("Đang tải dữ liệu để vẽ biểu đồ, xin chờ giây lát...")

                else:
                    st.info("Ví trống. Hãy nhập lệnh MUA bên trái để bắt đầu theo dõi tài sản!")

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
# ==============================================================================
# === TAB 4: CÔNG CỤ (MÁY TÍNH NGẮN HẠN, DÀI HẠN & SỔ TAY) ===
# ==============================================================================
import pandas as pd
import time

with main_tab4:
    st.markdown("""
    <div style="background-color:#1e1e1e; padding:15px; border-radius: 10px; border-left: 5px solid #28c840; margin-bottom: 20px;">
        <h3 style="color:white; margin:0;">🧰 TRUNG TÂM CÔNG CỤ & KẾ HOẠCH TÀI CHÍNH</h3>
    </div>
    """, unsafe_allow_html=True)
    
    c_tools_1, c_tools_2 = st.columns([1.5, 1])
    
    with c_tools_1:
        # --- PHẦN 1: MÁY TÍNH LÃI LỖ NGẮN HẠN (T+) ---
        st.markdown('<div class="glass-box"><h4>🧮 TÍNH TOÁN LÃI LỖ NGẮN HẠN (T+)</h4>', unsafe_allow_html=True)
        with st.form("short_term_form"):
            col_calc_1, col_calc_2 = st.columns(2)
            with col_calc_1:
                sim_vol = st.number_input("Số Lượng CP", min_value=100, step=100, value=1000)
                sim_price_in = st.number_input("Giá Vốn", min_value=0.1, step=0.1, value=25.0, format="%.2f")
            with col_calc_2:
                sim_price_target = st.number_input("Giá Mục Tiêu", min_value=0.1, step=0.1, value=28.5, format="%.2f")
                st.write("")
                st.write("")
            
            if st.form_submit_button("⚖️ DỰ TÍNH LÃI LỖ", type="primary", use_container_width=True):
                total_cost = sim_vol * sim_price_in * 1000 
                total_rev = sim_vol * sim_price_target * 1000
                profit = total_rev - total_cost
                pct_change = (profit / total_cost) * 100
                st.divider()
                if profit > 0:
                    st.success(f"🎉 LÃI: +{profit:,.0f} Đ (+{pct_change:.2f}%)")
                elif profit < 0:
                    st.error(f"⚠️ LỖ: {profit:,.0f} Đ ({pct_change:.2f}%)")
                else:
                    st.warning("HÒA VỐN")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True) 
        
        # --- PHẦN 2: CỖ MÁY GIẢ LẬP TÍCH SẢN (DÀI HẠN - ĐƠN VỊ TRIỆU VNĐ) ---
        st.markdown('<div class="glass-box"><h4>💎 CỖ MÁY TÍCH SẢN LÃI KÉP</h4>', unsafe_allow_html=True)
        st.caption("Mô phỏng sức mạnh của thời gian và kỷ luật gom hàng (HPG, MBB...).")
        
        with st.form("long_term_form"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                initial_inv_m = st.number_input("Vốn ban đầu (Triệu VNĐ)", min_value=0.0, step=10.0, value=50.0, format="%.1f")
                monthly_inv_m = st.number_input("Góp mỗi tháng (Triệu VNĐ)", min_value=0.0, step=1.0, value=5.0, format="%.1f")
            with col_c2:
                cagr = st.slider("Lợi nhuận kỳ vọng/năm (%)", min_value=1.0, max_value=30.0, value=15.0, step=0.5)
                years = st.slider("Thời gian tích sản (Năm)", min_value=1, max_value=40, value=20)
            
            if st.form_submit_button("🔮 MÔ PHỎNG TƯƠNG LAI", type="primary", use_container_width=True):
                # Quy đổi Triệu VNĐ ra VNĐ để tính toán nội bộ
                initial_inv = initial_inv_m * 1000000
                monthly_inv = monthly_inv_m * 1000000

                years_list = list(range(1, years + 1))
                principal_list = []
                total_list = []
                
                current_total = initial_inv
                total_principal = initial_inv
                
                for y in years_list:
                    yearly_cont = monthly_inv * 12
                    total_principal += yearly_cont
                    current_total = (current_total + yearly_cont) * (1 + cagr/100)
                    
                    principal_list.append(total_principal)
                    total_list.append(current_total)
                    
                df_sim = pd.DataFrame({
                    "Năm": years_list,
                    "Vốn Gốc (Bỏ ra)": principal_list,
                    "Tổng Tài Sản": total_list
                }).set_index("Năm")
                
                final_principal = principal_list[-1]
                final_total = total_list[-1]
                profit_earned = final_total - final_principal
                
                st.divider()
                st.success(f"🎯 **KẾT QUẢ SAU {years} NĂM:**")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Tổng Vốn Đã Góp", f"{final_principal / 1e9:.2f} Tỷ")
                m2.metric("Lãi Sinh Ra", f"{profit_earned / 1e9:.2f} Tỷ")
                m3.metric("💰 TỔNG TÀI SẢN NAV", f"{final_total / 1e9:.2f} Tỷ")
                
                st.area_chart(df_sim, color=["#ff5f57", "#28c840"])
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PHẦN 3: SỔ TAY ĐIỆP VIÊN ---
    with c_tools_2:
        st.markdown('<div class="glass-box"><h4>📝 SỔ TAY CHIẾN LƯỢC</h4>', unsafe_allow_html=True)
        current_user = st.session_state.get('user_info', {}).get('username', '')
        saved_note = get_user_note(current_user) if 'get_user_note' in globals() else ""
        with st.form("note_form"):
            new_note = st.text_area("Ghi chú mã cần theo dõi:", value=saved_note, height=560)
            if st.form_submit_button("💾 LƯU GHI CHÚ", use_container_width=True):
                if 'save_user_note' in globals():
                    save_user_note(current_user, new_note)
                    st.success("Đã lưu!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.info("Chưa có DB để lưu, đây là bản preview.")
        st.markdown('</div>', unsafe_allow_html=True)
# ==============================================================================
# === TAB 5: TRÌNH DUYỆT NGHIÊN CỨU (ĐỘC LẬP) ===
# ==============================================================================
with main_tab5:
    st.markdown("""
    <div style="background-color:#222; padding:10px; border-radius: 10px 10px 0 0; display:flex; align-items:center;">
        <span style="color:#ff5f57; font-size:20px; margin-right:5px;">●</span>
        <span style="color:#febc2e; font-size:20px; margin-right:5px;">●</span>
        <span style="color:#28c840; font-size:20px; margin-right:15px;">●</span>
        <span style="color:white; font-weight:bold;">🌐 RESEARCH BROWSER CENTER</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Danh sách các trang web an toàn
    web_options = {
        "🔥 FireAnt (Dashboard)": "https://fireant.vn/top-symbols",
        "📰 CafeF (Thị trường)": "https://cafef.vn/thi-truong-chung-khoan.chn",
        "🏢 StockBiz (Tổng hợp)": "https://stockbiz.vn/",
        "💰 24H Money": "https://24hmoney.vn",
        "📈 Tin Nhanh CK": "https://tinnhanhchungkhoan.vn",
        "🔍 Yahoo Search (VN)": "https://vn.search.yahoo.com",
    }
    
    c_web_1, c_web_2 = st.columns([3, 4])
    
    with c_web_1:
        selected_web_name = st.selectbox("Chọn Kênh:", list(web_options.keys()), label_visibility="collapsed")
    
    target_url = ""
    
    if web_options[selected_web_name] == "custom":
        with c_web_2:
            target_url = st.text_input("Nhập Link:", placeholder="https://...", label_visibility="collapsed")
    else:
        target_url = web_options[selected_web_name]
        with c_web_2:
            st.caption(f"Đang tải: {selected_web_name}...")

    if target_url:
        # Nút cứu hộ luôn ở sẵn
        st.link_button(f"🚀 Mở {selected_web_name} ra Trình duyệt ngoài", target_url)
        
        try:
            # Tuyệt chiêu Lồng Kính Trắng (Ép nền trắng tuyệt đối, không ảnh hưởng widget khác)
            html_code = f"""
                <style>
                    body {{ margin: 0; background-color: white !important; }}
                    iframe {{ width: 100%; height: 950px; border: none; border-radius: 0 0 10px 10px; }}
                </style>
                <iframe src="{target_url}"></iframe>
            """
            components.html(html_code, height=950, scrolling=True)
        except Exception:
            st.error("Trang web này từ chối kết nối.")
# ==============================================================================
# ==============================================================================
# === TAB 6: BÁO CÁO TỔNG HỢP GIAO DỊCH CUỐI NGÀY (PRO VERSION) ===
# ==============================================================================
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time

# --- CÁC HÀM TOÁN HỌC TÍNH TOÁN CHỈ BÁO ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_mfi(high, low, close, volume, period=14):
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    delta = typical_price.diff()
    
    pos_flow = money_flow.where(delta > 0, 0).rolling(window=period).sum()
    neg_flow = money_flow.where(delta < 0, 0).rolling(window=period).sum()
    
    money_ratio = pos_flow / neg_flow.replace(0, np.nan)
    mfi = 100 - (100 / (1 + money_ratio))
    return mfi.fillna(50)

@st.cache_data(ttl=3600)
def scan_market_data():
    """Hàm quét thị trường và lọc tín hiệu"""
    symbols = ['HPG.VN', 'MBB.VN', 'VHM.VN', 'PLX.VN', 'SSI.VN', 'VND.VN', 'FPT.VN', 
               'MWG.VN', 'VCB.VN', 'CTG.VN', 'TCB.VN', 'VPB.VN', 'DIG.VN', 'DXG.VN', 
               'DGC.VN', 'GMD.VN', 'VCI.VN', 'PNJ.VN', 'VNM.VN', 'SAB.VN']
    
    results = {
        'breakout_vol': [], 
        'overbought': [],   
        'oversold': [],     
        'top_smg': [],
        'break_high': [],
        'break_low': []
    }
    
    end_date = datetime.date.today()
    # Kéo 150 ngày dương lịch để trừ hao T7, CN và Lễ Tết (đảm bảo đủ 60 phiên)
    start_date = end_date - datetime.timedelta(days=150) 
    
    data = yf.download(symbols, start=start_date, end=end_date, progress=False)
    
    if data.empty:
        return results

    for sym in symbols:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                close_p = data['Close'][sym].dropna()
                high_p = data['High'][sym].dropna()
                low_p = data['Low'][sym].dropna()
                vol = data['Volume'][sym].dropna()
            else:
                close_p = data['Close'].dropna()
                high_p = data['High'].dropna()
                low_p = data['Low'].dropna()
                vol = data['Volume'].dropna()

            # Phải có đủ 61 phiên mới tính được SMG 60 ngày
            if len(close_p) < 61: 
                continue
                
            current_price = close_p.iloc[-1]
            prev_price = close_p.iloc[-2]
            pct_change = ((current_price - prev_price) / prev_price) * 100
            
            # --- TÍNH TOÁN KHỐI LƯỢNG ---
            current_vol = vol.iloc[-1]
            ma20_vol = vol.rolling(window=20).mean().iloc[-1]
            vol_ratio = (current_vol / ma20_vol) * 100 if ma20_vol > 0 else 0
            
            # --- TÍNH TOÁN RSI & MFI ---
            rsi_14 = calculate_rsi(close_p, 14).iloc[-1]
            mfi_14 = calculate_mfi(high_p, low_p, close_p, vol, 14).iloc[-1]
            
            # --- TÍNH TOÁN ĐỈNH ĐÁY VÀ SMG ---
            price_60_days_ago = close_p.iloc[-60]
            smg_pct = ((current_price - price_60_days_ago) / price_60_days_ago) * 100
            
            high_60 = close_p.rolling(window=60).max().iloc[-2] 
            low_20 = close_p.rolling(window=20).min().iloc[-2]  
            
            clean_sym = sym.replace('.VN', '')
            
            # 1. Bùng nổ Dòng tiền
            if pct_change > 0 and vol_ratio > 150:
                text = f"🟢 **{clean_sym}**: Giá {current_price:.1f} (+{pct_change:.1f}%) | Vol: **{vol_ratio:.0f}%** MA20"
                results['breakout_vol'].append((vol_ratio, text))
                
            # 2. Quá mua / Quá bán (RSI + MFI)
            if rsi_14 > 70 or mfi_14 > 80:
                text = f"🔴 **{clean_sym}**: RSI {rsi_14:.0f} | MFI {mfi_14:.0f}"
                results['overbought'].append((rsi_14, text))
            elif rsi_14 < 30 or mfi_14 < 20:
                text = f"🟢 **{clean_sym}**: RSI {rsi_14:.0f} | MFI {mfi_14:.0f}"
                results['oversold'].append((rsi_14, text))
                
            # 3. SMG (Đà tăng 3 tháng)
            if smg_pct > 0:
                text = f"🚀 **{clean_sym}**: Tăng **+{smg_pct:.1f}%** (3T)"
                results['top_smg'].append((smg_pct, text))
                
            # 4. Phá vỡ nền giá
            if current_price > high_60:
                results['break_high'].append(f"🚀 **{clean_sym}**: Vượt đỉnh 3T ({current_price:.1f})")
            elif current_price < low_20:
                results['break_low'].append(f"📉 **{clean_sym}**: Thủng đáy 1T ({current_price:.1f})")
                
        except Exception:
            continue
            
    # --- SẮP XẾP KẾT QUẢ TỪ MẠNH ĐẾN YẾU ---
    results['breakout_vol'].sort(key=lambda x: x[0], reverse=True)
    results['overbought'].sort(key=lambda x: x[0], reverse=True)
    results['oversold'].sort(key=lambda x: x[0])
    results['top_smg'].sort(key=lambda x: x[0], reverse=True)
    
    return results

# ==============================================================================
# GIAO DIỆN HIỂN THỊ CỦA TAB 6
# ==============================================================================
with main_tab6:
    st.markdown("""
    <div style="background-color:#1e1e1e; padding:15px; border-radius: 10px; border-left: 5px solid #ffbc00; margin-bottom: 20px;">
        <h3 style="color:white; margin:0;">📡 RADAR QUÉT THỊ TRƯỜNG (PRO VERSION)</h3>
        <p style="color:#aaaaaa; margin:0;">Tích hợp: Lọc Kép (RSI/MFI) • Sức Mạnh Giá (SMG) • Cảnh báo Vượt đỉnh/Thủng đáy</p>
    </div>
    """, unsafe_allow_html=True)

    run_radar = st.button("🚀 KÍCH HOẠT RADAR TÌM SIÊU CỔ PHIẾU", type="primary", use_container_width=True)
    st.markdown("---")

    if run_radar:
        with st.spinner("⏳ Đang cào dữ liệu, đo MFI và xếp hạng Sức mạnh giá..."):
            scan_results = scan_market_data()
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.caption(f"🕒 *Dữ liệu chốt lúc: {current_time}*")
            
            col_rep1, col_rep2, col_rep3 = st.columns(3)

            # --- CỘT 1: DÒNG TIỀN ---
            with col_rep1:
                st.markdown('<div class="glass-box"><h4>✸ BÙNG NỔ DÒNG TIỀN</h4>', unsafe_allow_html=True)
                st.info("Vol đột biến > 150%. Xếp hạng từ cao xuống thấp.")
                if scan_results['breakout_vol']:
                    for _, item in scan_results['breakout_vol'][:7]: 
                        st.markdown(item)
                else:
                    st.write("- Trống -")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- CỘT 2: LỌC KÉP ---
            with col_rep2:
                st.markdown('<div class="glass-box"><h4>◬ CẢNH BÁO (RSI/MFI)</h4>', unsafe_allow_html=True)
                st.warning("Lọc nhiễu: RSI(14) kẹp cùng MFI(14).")
                
                st.markdown("**🔥 Quá Mua (Cẩn thận):**")
                if scan_results['overbought']:
                    for _, item in scan_results['overbought'][:5]:
                        st.markdown(item)
                else:
                    st.write("- Trống -")
                    
                st.markdown("**🧊 Quá Bán (Bắt đáy):**")
                if scan_results['oversold']:
                    for _, item in scan_results['oversold'][:5]:
                        st.markdown(item)
                else:
                    st.write("- Trống -")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- CỘT 3: SỨC MẠNH GIÁ & XU HƯỚNG ---
            with col_rep3:
                st.markdown('<div class="glass-box"><h4>🏆 SỨC MẠNH & XU HƯỚNG</h4>', unsafe_allow_html=True)
                
                # Tầng 1: Xếp hạng SMG
                st.markdown("**🔥 TOP SMG (Đà tăng 3 Tháng):**")
                if scan_results['top_smg']:
                    for idx, (_, item) in enumerate(scan_results['top_smg'][:5]):
                        st.markdown(f"**#{idx+1}** {item}")
                else:
                    st.write("- Trống -")
                
                st.markdown("---")
                
                # Tầng 2: Vượt Đỉnh / Thủng Đáy
                st.markdown("**🎯 PHÁ VỠ NỀN GIÁ:**")
                if scan_results['break_high']:
                    for item in scan_results['break_high']:
                        st.markdown(item)
                if scan_results['break_low']:
                    for item in scan_results['break_low']:
                        st.markdown(item)
                if not scan_results['break_high'] and not scan_results['break_low']:
                    st.write("- Không có mã phá nền -")
                    
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.success("✅ Thuật toán đã quét xong! Tín hiệu đã được phân loại và xếp hạng chuẩn xác.")
    else:
        st.info("👆 Sẵn sàng. Nhấn nút màu đỏ bên trên để khởi động Radar quét!")

# ==============================================================================
# === TAB 7: CỖ MÁY KIỂM ĐỊNH LỊCH SỬ (BACKTESTING ENGINE) ===
# ==============================================================================
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# --- HÀM TÍNH TOÁN ---
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

with main_tab7:
    st.markdown("""
    <div style="background-color:#1e1e1e; padding:15px; border-radius: 10px; border-left: 5px solid #ff3366; margin-bottom: 20px;">
        <h3 style="color:white; margin:0;">⏱️ CỖ MÁY KIỂM ĐỊNH LỊCH SỬ (BACKTESTING ENGINE)</h3>
        <p style="color:#aaaaaa; margin:0;">Dùng dữ liệu quá khứ để chứng minh thuật toán giao dịch của bạn có thực sự đẻ ra tiền hay không.</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================
    # 🟢 THANH LỊCH SỬ TÌM KIẾM THÔNG MINH (Nằm ngay trên Form)
    # ==========================================================
    # 0. Khởi tạo bộ nhớ tạm
    if 'backtest_symbol_fill' not in st.session_state:
        st.session_state['backtest_symbol_fill'] = "HPG"

    # 1. Kéo 5 mã tìm kiếm gần nhất từ Google Sheets
    current_user = st.session_state.get('username', 'admin')
    recent_searches = get_search_history(current_user, limit=5)
    
    # 2. Dàn hàng ngang các nút bấm (Tags)
    if recent_searches:
        st.write("🕒 **Lịch sử kiểm định gần đây:**")
        cols = st.columns(len(recent_searches) + 2)
        for i, sym in enumerate(recent_searches):
            # Khi User bấm vào tag này, lưu mã đó vào bộ nhớ tạm
            if cols[i].button(f"🏷️ {sym}", key=f"bt_hist_{sym}"):
                st.session_state['backtest_symbol_fill'] = sym

    # --- KHUNG NHẬP LIỆU (THÔNG SỐ CHIẾN THUẬT) ---
    st.markdown('<div class="glass-box"><h4>⚙️ THIẾT LẬP CHIẾN THUẬT (RSI REVERSION)</h4>', unsafe_allow_html=True)
    with st.form("backtest_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            # Lấy giá trị từ Lịch sử (nếu có) để điền tự động vào đây
            ticker = st.text_input("Mã Cổ Phiếu", value=st.session_state['backtest_symbol_fill']).upper()
        with c2:
            years_back = st.slider("Dữ liệu quá khứ (Năm)", 1, 5, 2)
        with c3:
            rsi_buy = st.number_input("RSI Bắt Đáy (Mua)", value=30, step=1)
        with c4:
            rsi_sell = st.number_input("RSI Chốt Lời (Bán)", value=70, step=1)
            
        run_backtest = st.form_submit_button("🚀 CHẠY KIỂM ĐỊNH (BACKTEST)", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- KHỐI XỬ LÝ TOÁN HỌC & DATA ANALYSIS ---
    if run_backtest:
        if ticker:
            # [CHIP THEO DÕI]: Lưu mã này lên Google Sheets khi bấm nút CHẠY!
            save_search_history(current_user, ticker)

        with st.spinner(f"⏳ Đang tải lịch sử {years_back} năm của {ticker} và mô phỏng giao dịch..."):
            symbol = f"{ticker}.VN"
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=years_back * 365)
            
            # Kéo dữ liệu
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if df.empty:
                st.error(f"❌ Không tìm thấy dữ liệu cho mã {ticker}. Vui lòng kiểm tra lại.")
            else:
                # --- ĐÃ VÁ LỖI YFINANCE MULTIINDEX TẠI ĐÂY ---
                if isinstance(df.columns, pd.MultiIndex):
                    temp_close = df['Close']
                    if isinstance(temp_close, pd.Series):
                        df = temp_close.to_frame(name='Close')
                    else:
                        df = temp_close.copy()
                        df.columns = ['Close']
                else:
                    df = df[['Close']].copy()
                    
                df = df.dropna()
                
                # 1. Tính toán RSI
                df['RSI'] = get_rsi(df['Close'], 14)
                
                # 2. Sinh Tín Hiệu (Signal Generation)
                df['Signal'] = np.nan
                df.loc[df['RSI'] < rsi_buy, 'Signal'] = 1  # Bắt đáy
                df.loc[df['RSI'] > rsi_sell, 'Signal'] = 0 # Chốt lời
                
                # Forward fill
                df['Position'] = df['Signal'].ffill().fillna(0)
                
                # 3. Tính toán Lợi nhuận (PnL Calculation)
                df['Market_Return'] = df['Close'].pct_change()
                # Shift(1) chống gian lận dữ liệu tương lai
                df['Strategy_Return'] = df['Market_Return'] * df['Position'].shift(1)
                
                # Tính Lãi Kép lũy kế
                df['Hold_Cum'] = (1 + df['Market_Return']).cumprod() * 100 
                df['Strat_Cum'] = (1 + df['Strategy_Return']).cumprod() * 100
                
                df = df.dropna()
                
                # --- XUẤT BÁO CÁO KẾT QUẢ ---
                final_hold = df['Hold_Cum'].iloc[-1] - 100
                final_strat = df['Strat_Cum'].iloc[-1] - 100
                
                st.markdown("---")
                st.success(f"✅ Đã kiểm định hoàn tất {len(df)} phiên giao dịch của **{ticker}**!")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Lợi nhuận Mua & Vứt đó (Buy & Hold)", f"{final_hold:.2f}%")
                m2.metric("Lợi nhuận Thuật Toán (Strategy)", f"{final_strat:.2f}%", 
                          delta=f"{final_strat - final_hold:.2f}% so với TT", 
                          delta_color="normal" if final_strat > final_hold else "inverse")
                
                trades_count = (df['Position'].diff() > 0).sum()
                m3.metric("Tổng Số Lệnh Giao Dịch", f"{trades_count} lệnh")
                
                st.markdown('<h4>📈 Biểu đồ So sánh Hiệu quả Đầu tư</h4>', unsafe_allow_html=True)
                chart_data = df[['Hold_Cum', 'Strat_Cum']].rename(
                    columns={"Hold_Cum": "Nắm giữ dài hạn", "Strat_Cum": "Đánh theo Thuật toán RSI"}
                )
                st.line_chart(chart_data, color=["#aaaaaa", "#ffbc00"])
                st.caption("💡 *Mẹo DA: Đường màu vàng (Thuật toán) nằm trên đường màu xám (Nắm giữ) tức là hệ thống đang đánh bại thị trường!*")          
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
