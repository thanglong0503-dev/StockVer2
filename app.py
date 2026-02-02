"""
================================================================================
MODULE: app.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.6.0-PERFORMANCE-FIX-FULL
THEME: CYBERPUNK HUD
DESCRIPTION: 
    - Full Logic: Login -> Sidebar -> Radar (Cached) -> Analyst (Deep Dive).
    - Fixed: Radar does NOT re-scan when selecting a stock.
    - Features: AI Prophet Crosshair, Monte Carlo, Zoomable Charts.
================================================================================
"""
from backend.commodities import get_gold_price, get_silver_price
import streamlit as st
import sys
import os
import time
import pandas as pd
import streamlit.components.v1 as components
from frontend.components import render_market_galaxy
# ==============================================================================
# 1. SYSTEM CONFIGURATION
# ==============================================================================
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    layout="wide", 
    page_title="TL-TERMINAL V36.6", 
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
# 3. SECURE LOGIN LAYER
# ==============================================================================
def render_secure_login():
    """Màn hình đăng nhập Cyberpunk"""
    st.markdown("""
    <style>
        .login-box {
            max-width: 400px; margin: 100px auto; padding: 40px;
            background: rgba(0, 0, 0, 0.8); border: 1px solid #00f3ff;
            box-shadow: 0 0 50px rgba(0, 243, 255, 0.2); text-align: center; border-radius: 10px;
        }
        .login-title {
            font-family: 'Rajdhani', sans-serif; font-size: 32px; font-weight: 800; color: #fff;
            text-shadow: 0 0 10px #00f3ff; letter-spacing: 4px; margin-bottom: 20px;
        }
        .stTextInput input { text-align: center; color: #00f3ff !important; border-color: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box"><div class="login-title">SYSTEM ACCESS</div><div style="color: #555; font-size: 12px; margin-bottom: 20px;">RESTRICTED AREA // LEVEL 5 CLEARANCE</div></div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.form("login_form"):
            user = st.text_input("IDENTITY", placeholder="USER_ID")
            pwd = st.text_input("KEY_PHRASE", type="password", placeholder="ACCESS_CODE")
            if st.form_submit_button("INITIATE UPLINK", type="primary", use_container_width=True):
                time.sleep(0.3)
                if (user == "admin" and pwd == "admin123") or (user == "stock" and pwd == "stock123"):
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("⛔ ACCESS DENIED")

if not st.session_state['logged_in']:
    load_hardcore_css()
    render_secure_login()
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
    st.caption("SELECT EXCHANGE DATABASE:")
    c_hose, c_hnx, c_upcom = st.columns(3)
    
    # Các nút chọn sàn (Có Key để tránh lỗi Duplicate ID)
    if c_hose.button("HOSE", key="btn_hose", use_container_width=True):
        st.session_state['scan_list'] = ", ".join(get_full_market_list("HOSE"))
    if c_hnx.button("HNX", key="btn_hnx", use_container_width=True):
        st.session_state['scan_list'] = ", ".join(get_full_market_list("HNX"))
    if c_upcom.button("UPCOM", key="btn_upcom", use_container_width=True):
        st.session_state['scan_list'] = ", ".join(get_full_market_list("UPCOM"))
        
    user_tickers = st.text_area("WATCHLIST", value=st.session_state['scan_list'], height=150)
    count = len([x for x in user_tickers.split(',') if x.strip()])
    st.caption(f"TARGETS LOCKED: {count} SYMBOLS")
    
    if count > 50: st.warning("⚠️ High load! Scan may be slow.")

    # --- LOGIC QUÉT RADAR (FIXED) ---
    # Khi bấm nút này, dữ liệu sẽ được lưu vào Session State
    if st.button("EXECUTE SCAN", key="btn_scan", type="primary", use_container_width=True):
        ticker_list = [t.strip().upper() for t in user_tickers.split(',') if t.strip()]
        if ticker_list:
            with st.spinner("SCANNING SECTOR... (THIS MAY TAKE TIME)"):
                # Lưu kết quả vào biến toàn cục của phiên
                st.session_state['radar_data'] = get_pro_data(ticker_list) 
            st.success("SCAN COMPLETE.")
            time.sleep(0.5)
            st.rerun() # Reload để cập nhật giao diện
        
    st.divider()
    
    with st.expander("SYSTEM LOGS", expanded=True):
        st.markdown('<div style="font-family:monospace; font-size:10px; color:#555;">> SYSTEM_READY... OK<br>> DATABASE_LOADED... OK<br>> CACHE_CLEARED... OK</div>', unsafe_allow_html=True)

    if st.button("TERMINATE SESSION", key="btn_logout"):
        st.session_state['logged_in'] = False
        st.rerun()
# ... (Code cũ của nút TERMINATE SESSION)

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
# ... (Phần code cũ: render_market_overview(indices))

    # === [NEW] CYBER TICKER: DÒNG CHẢY DỮ LIỆU ===
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

# ... (Tiếp tục code cũ: st.markdown("<div style='height:20px'></div>"...))
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

col_radar, col_analyst = st.columns([1.5, 2.5])

# === LEFT PANE: RADAR (HIỂN THỊ TỪ BỘ NHỚ) ===
with col_radar:
    st.markdown('<div class="glass-box"><h4>📡 MARKET RADAR</h4>', unsafe_allow_html=True)
    
    df_radar = st.session_state['radar_data']
    
    if not df_radar.empty:
        # CHỈ LẤY NHỮNG CỘT CẦN THIẾT (Lọc bỏ rác ngay tại đây)
        # Sắp xếp lại thứ tự luôn cho đẹp
        df_display = df_radar[["Symbol", "Price", "Pct", "Signal", "Score", "Trend"]]

        st.dataframe(
            df_display,
            column_config={
                "Symbol": st.column_config.TextColumn("SYM", width="small", help="Mã cổ phiếu"),
                
                "Price": st.column_config.NumberColumn(
                    "PRICE", 
                    format="%.2f", # Hiển thị 2 số thập phân
                    width="small"
                ),
                
                "Pct": st.column_config.NumberColumn(
                    "%", 
                    format="%.2f %%", # Thêm dấu %
                    width="small"
                ),
                
                "Signal": st.column_config.TextColumn(
                    "ACTION", 
                    width="medium"
                ),
                
                "Score": st.column_config.ProgressColumn(
                    "POWER", 
                    format="%d/10", 
                    min_value=0, 
                    max_value=10,
                    width="medium"
                ),
                
                # [SỬA LẠI ĐOẠN NÀY]
                "Trend": st.column_config.LineChartColumn(
                    "MINI CHART",
                    width="large"
                    # ĐÃ XÓA: y_min=0 -> Để nó tự động Auto Scale theo sóng
                )
            },
            hide_index=True,
            use_container_width=True,
            height=400 # [GỢI Ý] Giảm chiều cao bảng xuống chút để nhường chỗ cho Galaxy
        )

        # ========================================================
        # 👉 DÁN ĐOẠN VŨ TRỤ DÒNG TIỀN VÀO ĐÂY (Ngay dưới bảng)
        # ========================================================
        st.markdown("---") # Đường kẻ ngang ngăn cách
        
        # Gọi hàm vẽ Galaxy (Truyền toàn bộ dữ liệu radar vào)
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
        
        # TAB 3: AI (Crosshair Neon + Dots)
        with t3:
            st.markdown("### 🔮 NEURAL NETWORK FORECAST")
            if st.button("INITIATE AI MODEL", key="btn_ai", type="primary"):
                with st.spinner("TRAINING NEURAL NETS..."):
                    fig_ai = run_prophet_ai(hist_df)
                    if fig_ai: 
                        st.plotly_chart(fig_ai, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
                    else: st.error("INSUFFICIENT DATA")
        
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

st.markdown('<div style="text-align:center; color:#444; font-size:10px; margin-top:50px;">THANG LONG TERMINAL SYSTEM V36.6 // ENCRYPTED</div>', unsafe_allow_html=True)
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
        color: #888;               /* Màu chữ xám mặc định */
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
