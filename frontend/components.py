import streamlit as st
import plotly.graph_objects as go
import pandas_ta as ta

# --- CSS CHO CARD (QUAN TRỌNG) ---
def load_card_css():
    st.markdown("""
    <style>
    .rec-card {
        background-color: #1f2937; border-radius: 12px; padding: 20px; 
        text-align: center; margin-bottom: 20px; border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .score-circle {
        display: inline-block; width: 80px; height: 80px; line-height: 80px; 
        border-radius: 50%; font-size: 32px; font-weight: 900; color: white; 
        margin: 15px 0; box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. VẼ 2 CARD PHÂN TÍCH (NHƯ ẢNH) ---
def render_analysis_section(tech, fund):
    load_card_css()
    c1, c2 = st.columns(2)
    
    # CARD KỸ THUẬT (TRÁI)
    with c1:
        st.markdown(f"""
        <div class="rec-card" style="border-left: 5px solid {tech['color']};">
            <h4 style="color:#9ca3af; margin:0; font-size:0.9rem;">🔭 GÓC NHÌN KỸ THUẬT</h4>
            <div class="score-circle" style="background:{tech['color']}; box-shadow: 0 0 15px {tech['color']};">
                {tech['score']}
            </div>
            <h2 style="color:{tech['color']}; font-weight:900; margin:0; font-size:2rem; text-transform:uppercase;">
                {tech['action']}
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Chi tiết giá
        k1, k2, k3 = st.columns(3)
        k1.metric("💰 Giá", f"{tech['entry']:,.0f}")
        k2.metric("🛑 Cắt Lỗ", f"{tech['stop']:,.0f}", delta_color="inverse")
        k3.metric("🎯 Mục Tiêu", f"{tech['target']:,.0f}")

        with st.expander("🔍 Chi tiết Kỹ Thuật", expanded=True):
            for p in tech['pros']: st.success(p)
            for c in tech['cons']: st.warning(c)

    # CARD CƠ BẢN (PHẢI)
    with c2:
        st.markdown(f"""
        <div class="rec-card" style="border-left: 5px solid {fund['color']};">
            <h4 style="color:#9ca3af; margin:0; font-size:0.9rem;">🏢 SỨC KHỎE DOANH NGHIỆP</h4>
            <div style="height: 80px; display: flex; align-items: center; justify-content: center; margin: 15px 0;">
                <h2 style="color:{fund['color']}; font-weight:900; font-size:2rem; margin:0;">
                    {fund['health']}
                </h2>
            </div>
             <h4 style="color:#9ca3af; margin:0; font-size:0.8rem; visibility:hidden">Placeholder</h4>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 Chi tiết Cơ Bản (BCTC Quý)", expanded=True):
            for d in fund['details']: 
                if "cao" in d or "Thấp" in d: st.warning(d)
                else: st.success(d)
            if fund['market_cap'] > 0:
                st.info(f"Vốn hóa: {fund['market_cap']/1e9:,.0f} Tỷ")

# --- 2. CÁC HÀM CŨ (GIỮ NGUYÊN) ---
def render_market_overview(indices_data):
    if not indices_data: return
    cols = st.columns(len(indices_data))
    for i, data in enumerate(indices_data):
        with cols[i]:
            color = data['Color']
            price_fmt = "{:,.2f}".format(data['Price'])
            st.markdown(f"""
            <div style="background:#111827; border:1px solid #374151; border-radius:8px; padding:10px; text-align:center;">
                <div style="color:#9ca3af; font-size:0.75rem; font-weight:700;">{data['Name']}</div>
                <div style="font-size:1.2rem; font-weight:800; color:{color}; margin:2px 0;">{price_fmt}</div>
                <div style="font-size:0.75rem; color:{color}; font-weight:600;">{data['Pct']:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

def render_interactive_chart(df, symbol):
    # Logic vẽ chart cũ
    if df.empty: return
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=f"{symbol} Chart", template="plotly_dark", height=500, xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)
