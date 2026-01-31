import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

# ==============================================================================
# 1. THANH CHỈ SỐ THỊ TRƯỜNG (MARKET OVERVIEW)
# ==============================================================================
def render_market_overview(indices_data):
    if not indices_data: return

    # CSS viết sát lề để tránh lỗi hiển thị code block
    st.markdown("""
<style>
.market-card {
    background-color: #111827; 
    border: 1px solid #374151; 
    border-radius: 8px; 
    padding: 12px; 
    text-align: center;
    transition: transform 0.2s;
}
.market-card:hover { border-color: #0ea5e9; transform: translateY(-2px); }
.idx-name { color: #9ca3af; font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; }
.idx-price { font-family: 'Rajdhani'; font-size: 1.4rem; font-weight: 800; margin: 4px 0; }
.idx-change { font-family: 'Inter'; font-size: 0.8rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

    cols = st.columns(len(indices_data))
    
    for i, data in enumerate(indices_data):
        with cols[i]:
            status = data.get('Status', 'LIVE')
            if status == "LIVE":
                color = data['Color']
                arrow = "▲" if data['Change'] >= 0 else "▼"
                price_fmt = "{:,.2f}".format(data['Price'])
                change_fmt = f"{arrow} {data['Change']:,.2f} ({data['Pct']:+.2f}%)"
                
                # HTML sát lề
                st.markdown(f"""
<div class="market-card">
    <div class="idx-name">{data['Name']}</div>
    <div class="idx-price" style="color: {color}; text-shadow: 0 0 10px {color}40;">{price_fmt}</div>
    <div class="idx-change" style="color: {color};">{change_fmt}</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="market-card" style="opacity: 0.6;">
    <div class="idx-name">{data['Name']}</div>
    <div class="idx-price" style="color: #64748b;">---</div>
    <div class="idx-change" style="color: #64748b;">OFFLINE</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BỘ THẺ PHÂN TÍCH KÉP (FIX LỖI HIỂN THỊ HTML)
# ==============================================================================
def render_analysis_section(tech, fund):
    c1, c2 = st.columns(2)
    
    # --- THẺ 1: KỸ THUẬT ---
    with c1:
        # Quan trọng: Đoạn HTML này phải nằm sát lề trái, không được thụt vào!
        st.markdown(f"""
<div style="background-color: #1f2937; border-radius: 12px; padding: 20px; border: 1px solid #374151; border-left: 5px solid {tech['color']}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); height: 100%;">
    <h4 style="color:#9ca3af; margin:0; font-size:0.9rem; letter-spacing:1px;">🔭 KỸ THUẬT (V36.1)</h4>
    <div style="display:inline-flex; align-items:center; justify-content:center; width: 80px; height: 80px; border-radius: 50%; background: {tech['color']}; color: white; font-family: 'Rajdhani'; font-size: 2.5rem; font-weight: 800; margin: 15px 0; box-shadow: 0 0 20px {tech['color']}60;">
        {tech['score']}
    </div>
    <h2 style="color:{tech['color']}; margin:0; font-size:1.8rem; font-weight:900;">
        {tech['action']}
    </h2>
    <hr style="border-color: #374151; margin: 15px 0;">
    <div style="display:flex; justify-content:space-between; font-family:'Rajdhani';">
        <div><div style="color:#9ca3af; font-size:0.8rem;">ENTRY</div><div style="color:white; font-weight:700; font-size:1.1rem;">{tech['entry']:,.0f}</div></div>
        <div><div style="color:#ef4444; font-size:0.8rem;">STOPLOSS</div><div style="color:#ef4444; font-weight:700; font-size:1.1rem;">{tech['stop']:,.0f}</div></div>
        <div><div style="color:#10b981; font-size:0.8rem;">TARGET</div><div style="color:#10b981; font-weight:700; font-size:1.1rem;">{tech['target']:,.0f}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        with st.expander("🔍 Chi tiết Kỹ Thuật", expanded=False):
            for p in tech['pros']: st.success(f"✅ {p}")
            for c in tech['cons']: st.error(f"⚠️ {c}")

    # --- THẺ 2: CƠ BẢN ---
    with c2:
        st.markdown(f"""
<div style="background-color: #1f2937; border-radius: 12px; padding: 20px; border: 1px solid #374151; border-left: 5px solid {fund['color']}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
    <div>
        <h4 style="color:#9ca3af; margin:0; font-size:0.9rem; letter-spacing:1px;">🏢 CƠ BẢN (FUNDAMENTAL)</h4>
        <div style="margin: 20px 0;">
            <h2 style="color:{fund['color']}; margin:0; font-size:2rem; font-weight:900; line-height:1.2;">{fund['health']}</h2>
        </div>
    </div>
    <div>
        <hr style="border-color: #374151; margin: 15px 0;">
        <div style="color: #cbd5e1; font-weight: 500;">
            Vốn hóa: <span style="color:white; font-weight:700;">{fund['market_cap']/1e9:,.0f} Tỷ</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        with st.expander("🔍 Chi tiết Cơ Bản", expanded=True):
            for d in fund['details']:
                if "cao" in d or "Thấp" in d or "giảm" in d or "kém" in d or "Kém" in d:
                    st.warning(f"⚠️ {d}")
                else:
                    st.success(f"✅ {d}")

# ==============================================================================
# 3. BIỂU ĐỒ TƯƠNG TÁC
# ==============================================================================
def render_interactive_chart(df, symbol):
    if df.empty:
        st.warning("Chưa có dữ liệu biểu đồ.")
        return

    try:
        if 'ITS_9' not in df.columns:
            ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
            if ichi is not None: df = df.join(ichi[0])
    except: pass

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)

    if 'ITS_9' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ITS_9'], line=dict(color='#22d3ee', width=1), name='Tenkan'), row=1, col=1)
    if 'IKS_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['IKS_26'], line=dict(color='#ef4444', width=1), name='Kijun'), row=1, col=1)

    colors = ['#10b981' if row['Open'] < row['Close'] else '#ef4444' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

    fig.update_layout(
        title=dict(text=f"{symbol} - TECHNICAL CHART", font=dict(family="Rajdhani", size=20, color="white")),
        template="plotly_dark", height=600, xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10), dragmode="pan"
    )
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.05), row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)
