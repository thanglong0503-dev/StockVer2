import streamlit as st
import sys
import os
import plotly.express as px

# 1. SETUP
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
st.set_page_config(layout="wide", page_title="Thang Long Terminal", page_icon="🐲")

# 2. IMPORT
try:
    from backend.data import get_pro_data, get_history_df, get_market_indices, get_financial_report, get_stock_news, get_company_profile, get_dividend_history
    from backend.ai import run_monte_carlo_sim
    from backend.logic import analyze_smart_v36
    from frontend.ui import load_hardcore_css, render_header
    from frontend.components import render_score_card_v36, render_interactive_chart, render_market_overview
except ImportError as e:
    st.error(f"System Error: {e}")
    st.stop()

# 3. UI LOAD
load_hardcore_css()
render_header() 

# 4. MARKET BAR
with st.spinner("Connecting Global Markets..."):
    market_data = get_market_indices()
    render_market_overview(market_data)

st.markdown("---")

# 5. MAIN
WATCHLIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX"]
col_radar, col_analyst = st.columns([1.5, 2.5])

# --- LEFT: RADAR ---
with col_radar:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Rajdhani; margin-top:0;">📡 MARKET RADAR</h3>', unsafe_allow_html=True)
    
    with st.spinner("Scanning..."):
        df_radar = get_pro_data(WATCHLIST)
        
    if not df_radar.empty:
        st.dataframe(
            df_radar,
            column_config={
                "Symbol": st.column_config.TextColumn("Ticker"),
                "Price": st.column_config.NumberColumn("Price (K)", format="%.2f"),
                "Pct": st.column_config.NumberColumn("%", format="%.2f %%"),
                "Signal": st.column_config.TextColumn("Signal"),
                "Score": st.column_config.ProgressColumn("Power", format="%d/10", min_value=0, max_value=10),
                "Trend": st.column_config.LineChartColumn("Trend"),
            },
            hide_index=True, use_container_width=True, height=600
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: ANALYST CENTER ---
with col_analyst:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    
    if not df_radar.empty:
        # Chọn mã
        selected = st.selectbox("SELECT ASSET:", df_radar['Symbol'], label_visibility="collapsed")
        st.markdown(f"<h1 style='font-family:Rajdhani; color:#06b6d4; margin-top:-10px;'>{selected} - ANALYST CENTER</h1>", unsafe_allow_html=True)
        
        # Lấy data
        hist_df = get_history_df(selected)
        
        # TABS CHỨC NĂNG
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 BIỂU ĐỒ & SĂN NẾN", "🌌 ĐA VŨ TRỤ", "💰 TÀI CHÍNH", "📰 TIN TỨC", "🏢 HỒ SƠ", "🎁 CỔ TỨC"
        ])
        
        # TAB 1: BIỂU ĐỒ (LOGIC CŨ)
        with tab1:
            tech_result = analyze_smart_v36(hist_df)
            if tech_result:
                c1, c2 = st.columns([1, 1.5])
                with c1: render_score_card_v36(tech_result)
                with c2:
                    st.success(f"✅ POSITIVE: {', '.join(tech_result['pros'])}")
                    if tech_result['cons']: st.error(f"⚠️ WARNING: {', '.join(tech_result['cons'])}")
                render_interactive_chart(hist_df, selected)

        # TAB 2: MONTE CARLO
        with tab2:
            st.markdown("### 🔮 DỰ BÁO ĐA VŨ TRỤ (100 KỊCH BẢN)")
            if st.button("CHẠY GIẢ LẬP", type="primary"):
                mc_df = run_monte_carlo_sim(hist_df)
                if mc_df is not None:
                    fig = px.line(mc_df, title=f"Monte Carlo Simulation: {selected} (30 Days)", template="plotly_dark")
                    fig.update_traces(line=dict(width=1), opacity=0.3) # Làm mờ các đường
                    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

        # TAB 3: TÀI CHÍNH (NEW)
        with tab3:
            st.markdown("### 📜 BÁO CÁO TÀI CHÍNH (QUÝ)")
            type_report = st.radio("Loại báo cáo:", ["Kết Quả Kinh Doanh", "Cân Đối Kế Toán", "Lưu Chuyển Tiền Tệ"], horizontal=True)
            
            map_type = {
                "Kết Quả Kinh Doanh": "incomestatement",
                "Cân Đối Kế Toán": "balancesheet",
                "Lưu Chuyển Tiền Tệ": "cashflow"
            }
            
            with st.spinner("Đang tải dữ liệu từ TCBS..."):
                df_fin = get_financial_report(selected, map_type[type_report])
                if not df_fin.empty:
                    st.dataframe(df_fin, use_container_width=True)
                else:
                    st.warning("Chưa có dữ liệu báo cáo.")

        # TAB 4: TIN TỨC (NEW)
        with tab4:
            st.markdown("### 📰 TIN TỨC MỚI NHẤT")
            news_list = get_stock_news(selected)
            if news_list:
                for news in news_list:
                    # Render tin tức đẹp
                    title = news.get('title', 'No Title')
                    date = news.get('publishDate', '')[:10]
                    link = f"https://tcinvest.tcbs.com.vn/tc-price/symbol-info/{selected}?t=news" # Link tạm về TCBS
                    st.markdown(f"""
                    <div style="background:#111827; padding:10px; border-radius:8px; margin-bottom:8px; border-left: 3px solid #06b6d4;">
                        <a href="{link}" target="_blank" style="text-decoration:none; color:white; font-weight:bold;">{title}</a>
                        <div style="color:#94a3b8; font-size:0.8rem;">📅 {date}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Không có tin tức mới.")

        # TAB 5: HỒ SƠ (NEW)
        with tab5:
            profile = get_company_profile(selected)
            if profile:
                st.markdown(f"### {profile.get('shortName', selected)}")
                st.info(f"**Ngành:** {profile.get('industryName', 'N/A')}")
                st.write(profile.get('overview', 'Chưa có mô tả.'))
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Vốn hóa", f"{profile.get('marketCap', 0)/1e9:,.0f} Tỷ")
                c2.metric("P/E", f"{profile.get('pe', 0):.2f}")
                c3.metric("P/B", f"{profile.get('pb', 0):.2f}")

        # TAB 6: CỔ TỨC (NEW)
        with tab6:
            st.markdown("### 🎁 LỊCH SỬ CỔ TỨC")
            df_div = get_dividend_history(selected)
            if not df_div.empty:
                # Chọn cột cần hiển thị
                cols_show = ['exerciseDate', 'cashYear', 'cashDividendPercentage', 'issueMethod']
                # Đổi tên cho đẹp
                df_div = df_div.rename(columns={
                    'exerciseDate': 'Ngày GDKHQ', 
                    'cashYear': 'Năm', 
                    'cashDividendPercentage': 'Tỉ lệ (%)',
                    'issueMethod': 'Loại'
                })
                st.dataframe(df_div[['Ngày GDKHQ', 'Năm', 'Tỉ lệ (%)', 'Loại']], use_container_width=True)
            else:
                st.info("Chưa có dữ liệu cổ tức.")

    st.markdown('</div>', unsafe_allow_html=True)
