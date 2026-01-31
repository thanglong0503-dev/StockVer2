"""
================================================================================
MODULE: frontend/components.py
PROJECT: THANG LONG TERMINAL
VERSION: 36.1.3-NO-INDENT-FIX
DESCRIPTION: 
    Using Single-line HTML strings to absolutely prevent Markdown code-block errors.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

# CSS CHUNG (Nạp 1 lần để dùng cho toàn file)
GLOBAL_CSS = """
<style>
.ticker-item {
    background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px;
    padding: 10px 12px; display: flex; flex-direction: column; justify-content: center; height: 70px;
}
.t-name { color: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
.t-val-row { display: flex; justify-content: space-between; align-items: baseline; }
.t-price { color: #e6edf3; font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
.t-change { font-size: 12px; font-weight: 500; margin-left: 8px; font-variant-numeric: tabular-nums; }
.up { color: #238636; } .down { color: #da3633; }
.pro-card { height: 100%; background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; }
.sub-card { background: #0d1117; border-radius: 4px; padding: 12px; border: 1px solid #30363d; }
.metric-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
.metric-row:last-child { margin-bottom: 0; }
.divider { width: 100%; height: 1px; background: #21262d; margin: 4px 0; }
</style>
"""

# ==============================================================================
# 1. MARKET TICKER BAR
# ==============================================================================
def render_market_overview(indices_data):
    if not indices_data: return
    
    # Inject CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    cols = st.columns(len(indices_data))
    
    for i, data in enumerate(indices_data):
        with cols[i]:
            if data.get('Status') == "LIVE":
                color_class = "up" if data['Change'] >= 0 else "down"
                sign = "+" if data['Change'] >= 0 else ""
                price_fmt = "{:,.2f}".format(data['Price'])
                
                # HTML VIẾT TRÊN 1 DÒNG (Không thể lỗi)
                html = f'<div class="ticker-item"><div class="t-name">{data["Name"]}</div><div class="t-val-row"><div class="t-price">{price_fmt}</div><div class="t-change {color_class}">{sign}{data["Pct"]:.2f}%</div></div></div>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                html = f'<div class="ticker-item" style="opacity: 0.5;"><div class="t-name">{data["Name"]}</div><div class="t-val-row"><div class="t-price" style="color:#8b949e;">---</div><div class="t-change" style="color:#8b949e;">OFFLINE</div></div></div>'
                st.markdown(html, unsafe_allow_html=True)

# ==============================================================================
# 2. ANALYSIS DASHBOARD
# ==============================================================================
def render_analysis_section(tech, fund):
    c1, c2 = st.columns(2)
    
    # --- TECHNICAL CARD ---
    with c1:
        score_color = "#238636" if tech['score'] >= 7 else "#da3633" if tech['score'] <= 3 else "#d29922"
        action_text = tech['action'].replace('💎','').replace('💪','').replace('⚠️','')
        
        # HTML DÒNG ĐƠN - Nối chuỗi
        html_tech = (
            f'<div class="pro-card" style="border-left: 4px solid {score_color};">'
            f'<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">'
            f'<div><div style="color: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase;">Technical Rating</div>'
            f'<div style="font-size: 28px; font-weight: 700; color: {score_color}; margin-top: 4px;">{action_text}</div></div>'
            f'<div style="text-align: right;"><div style="font-size: 32px; font-weight: 800; color: #e6edf3;">{tech["score"]}<span style="font-size: 14px; color: #8b949e;">/10</span></div></div></div>'
            f'<div class="sub-card">'
            f'<div class="metric-row"><span style="color: #8b949e;">Entry Price</span><span style="color: #e6edf3; font-weight: 600;">{tech["entry"]:,.0f}</span></div>'
            f'<div class="divider"></div>'
            f'<div class="metric-row"><span style="color: #da3633;">Stop Loss</span><span style="color: #da3633; font-weight: 600;">{tech["stop"]:,.0f}</span></div>'
            f'<div class="divider"></div>'
            f'<div class="metric-row"><span style="color: #238636;">Target Price</span><span style="color: #238636; font-weight: 600;">{tech["target"]:,.0f}</span></div>'
            f'</div></div>'
        )
        st.markdown(html_tech, unsafe_allow_html=True)
        
        with st.expander("View Technical Factors", expanded=False):
            for p in tech['pros']: st.success(p)
            for c in tech['cons']: st.warning(c)

    # --- FUNDAMENTAL CARD ---
    with c2:
        health_color = fund['color']
        health_text = fund['health'].replace('💎','').replace('💪','').replace('⚠️','')
        mkt_cap = fund['market_cap']/1e9
        
        html_fund = (
            f'<div class="pro-card" style="border-left: 4px solid {health_color};">'
            f'<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">'
            f'<div><div style="color: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase;">Fundamental Health</div>'
            f'<div style="font-size: 24px; font-weight: 700; color: {health_color}; margin-top: 4px;">{health_text}</div></div>'
            f'<div style="text-align: right;"><div style="color: #8b949e; font-size: 11px; font-weight: 600; text-transform: uppercase;">Market Cap</div>'
            f'<div style="font-size: 18px; font-weight: 600; color: #e6edf3;">{mkt_cap:,.0f} B</div></div></div>'
            f'<div style="margin-top: 10px;">'
            f'<div style="font-size: 13px; color: #8b949e; margin-bottom: 5px;">Analysis Summary</div>'
            f'<div style="font-size: 13px; color: #e6edf3; line-height: 1.5;">Financial health evaluation based on Valuation (P/E), Profitability (ROE), and recent Growth metrics.</div></div></div>'
        )
        st.markdown(html_fund, unsafe_allow_html=True)
        
        with st.expander("View Financial Metrics", expanded=True):
            for d in fund['details']:
                color = "#da3633" if any(x in d for x in ["cao", "Thấp", "giảm", "kém"]) else "#238636"
                st.markdown(f"<span style='color:{color}; font-size:13px;'>• {d}</span>", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERACTIVE CHART
# ==============================================================================
def render_interactive_chart(df, symbol):
    if df.empty: return

    try:
        if 'ITS_9' not in df.columns:
            ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
            if ichi is not None: df = df.join(ichi[0])
    except: pass

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
    
    # Nến
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC',
        increasing_line_color='#238636', increasing_fillcolor='#238636',
        decreasing_line_color='#da3633', decreasing_fillcolor='#da3633'
    ), row=1, col=1)
    
    # Ichimoku
    if 'ITS_9' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ITS_9'], line=dict(color='#2f81f7', width=1), name='Tenkan'), row=1, col=1)
    if 'IKS_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['IKS_26'], line=dict(color='#d29922', width=1), name='Kijun'), row=1, col=1)

    # Volume
    colors = ['#238636' if r['Open'] < r['Close'] else '#da3633' for i, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Vol'), row=2, col=1)

    fig.update_layout(
        template="plotly_dark", height=600, 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=40, t=20, b=0),
        font=dict(family="Inter", size=11),
        showlegend=False
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#21262d')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#21262d', side='right')
    
    st.plotly_chart(fig, use_container_width=True)
