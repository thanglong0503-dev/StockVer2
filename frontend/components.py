"""
================================================================================
MODULE: frontend/components.py
THEME: ULTRA CYBERPUNK HUD INTERFACE
VERSION: 36.3.0-INTERACTIVE-FIX
DESCRIPTION: 
    Render complex HUD elements using embedded CSS animations and SVG generation.
    UPDATED: Enabled Scroll Zoom & Pan Dragging for Charts (TradingView Style).
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
import numpy as np

# ==============================================================================
# 1. CORE VISUAL ENGINE (CSS ANIMATIONS & EFFECTS)
# ==============================================================================
def inject_cyber_effects():
    """
    Tiêm vào trang web các hiệu ứng chuyển động phức tạp.
    """
    css = """
    <style>
        /* 1. SCROLLBAR HACK */
        ::-webkit-scrollbar { width: 6px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #00f3ff; border-radius: 0px; }

        /* 2. HUD CARD CONTAINER */
        .hud-card {
            background: rgba(5, 10, 15, 0.9);
            border: 1px solid #333;
            border-left: 2px solid #00f3ff;
            border-right: 2px solid #ff0055;
            position: relative;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .hud-card:hover {
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.2);
            border-color: #fff;
        }

        /* 3. SCANNING LINE ANIMATION */
        .hud-card::after {
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 5px;
            background: rgba(0, 243, 255, 0.3);
            box-shadow: 0 0 10px #00f3ff;
            animation: scan 4s linear infinite;
            opacity: 0.3;
            pointer-events: none;
        }
        @keyframes scan {
            0% { top: -10%; }
            100% { top: 110%; }
        }

        /* 4. TEXT GLITCH EFFECT */
        .glitch-text {
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 800;
            position: relative;
            text-transform: uppercase;
        }
        
        /* 5. METRIC GRID */
        .cyber-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
            border-top: 1px solid #333;
            padding-top: 15px;
        }
        .cyber-metric {
            background: #0a0f14;
            padding: 8px;
            border: 1px solid #222;
        }
        .cyber-label { font-size: 10px; color: #00f3ff; text-transform: uppercase; letter-spacing: 1px; }
        .cyber-val { font-size: 16px; color: #fff; font-weight: 700; font-family: 'Rajdhani'; }

        /* 6. STATUS INDICATORS */
        .status-dot {
            height: 8px; width: 8px;
            background-color: #333;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            box-shadow: 0 0 5px currentColor;
        }
        .status-dot.active { animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==============================================================================
# 2. SVG GENERATOR (VẼ ĐỒ HỌA BẰNG CODE)
# ==============================================================================
def create_svg_gauge(score, color):
    """
    Tạo mã SVG để vẽ đồng hồ đo sức mạnh.
    """
    percentage = max(0, min(10, score)) / 10
    rotation = -90 + (percentage * 180)
    
    svg = f"""
    <svg width="120" height="70" viewBox="0 0 120 70">
        <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="#222" stroke-width="10" stroke-linecap="round"/>
        <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round" 
              stroke-dasharray="157" stroke-dashoffset="{157 * (1 - percentage)}" 
              style="transition: stroke-dashoffset 1s ease-out;"/>
        <g transform="translate(60, 60) rotate({rotation})">
            <path d="M -5 0 L 0 -50 L 5 0 Z" fill="#fff" />
            <circle cx="0" cy="0" r="5" fill="#fff"/>
        </g>
        <text x="60" y="50" text-anchor="middle" fill="#fff" font-family="Rajdhani" font-weight="bold" font-size="20">{score}</text>
    </svg>
    """
    return svg.replace('\n', ' ')

# ==============================================================================
# 3. MARKET TICKER (THANH CHỈ SỐ NEON)
# ==============================================================================
def render_market_overview(indices_data):
    if not indices_data: return
    inject_cyber_effects()
    
    cols = st.columns(len(indices_data))
    
    for i, data in enumerate(indices_data):
        with cols[i]:
            status_color = "#00f3ff" 
            if data['Change'] >= 0: status_color = "#00ff41" 
            else: status_color = "#ff0055" 
            
            arrow = "▲" if data['Change'] >= 0 else "▼"
            
            html = (
                f'<div style="background:linear-gradient(180deg, rgba(0,0,0,0), rgba(0,243,255,0.05)); border:1px solid #222; border-bottom: 2px solid {status_color}; padding:10px; text-align:center;">'
                f'<div style="font-size:10px; color:#888; text-transform:uppercase; letter-spacing:2px;">{data["Name"]}</div>'
                f'<div style="font-size:20px; font-weight:800; color:#fff; font-family:Rajdhani; text-shadow:0 0 10px {status_color}; margin: 5px 0;">{data["Price"]:,.2f}</div>'
                f'<div style="font-size:12px; color:{status_color}; font-weight:600;">{arrow} {abs(data["Change"]):,.2f} ({data["Pct"]:.2f}%)</div>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

# ==============================================================================
# 4. CYBERPUNK DASHBOARD (TRUNG TÂM PHÂN TÍCH)
# ==============================================================================
def render_analysis_section(tech, fund):
    c1, c2 = st.columns(2)
    
    # --- LEFT CARD: TECHNICAL ---
    with c1:
        tech_color = tech['color']
        action_text = tech['action'].replace('💎','').replace('💪','').replace('⚠️','')
        gauge_svg = create_svg_gauge(tech['score'], tech_color)
        
        signals_html = ""
        for p in tech['pros'][:3]:
            signals_html += f'<div style="color:#00ff41; font-size:12px; margin-bottom:2px;">[+] {p}</div>'
        for c in tech['cons'][:2]:
            signals_html += f'<div style="color:#ff0055; font-size:12px; margin-bottom:2px;">[-] {c}</div>'
            
        html_tech = (
            f'<div class="hud-card">'
            f'  <div style="display:flex; justify-content:space-between; align-items:center;">'
            f'      <div>'
            f'          <div class="glitch-text" style="font-size:14px; letter-spacing:2px; color:{tech_color};">TECHNICAL_SYS_V36</div>'
            f'          <div style="font-size:32px; font-weight:900; color:#fff; font-family:Rajdhani; text-shadow:0 0 15px {tech_color};">{action_text}</div>'
            f'      </div>'
            f'      <div>{gauge_svg}</div>'
            f'  </div>'
            f'  <div class="cyber-grid">'
            f'      <div class="cyber-metric"><div class="cyber-label">ENTRY_ZONE</div><div class="cyber-val">{tech["entry"]:,.0f}</div></div>'
            f'      <div class="cyber-metric"><div class="cyber-label">TARGET_LOCK</div><div class="cyber-val" style="color:#00ff41;">{tech["target"]:,.0f}</div></div>'
            f'      <div class="cyber-metric"><div class="cyber-label">STOP_LOSS</div><div class="cyber-val" style="color:#ff0055;">{tech["stop"]:,.0f}</div></div>'
            f'      <div class="cyber-metric"><div class="cyber-label">ATR_VOLTY</div><div class="cyber-val">{tech.get("atr", 0):,.0f}</div></div>'
            f'  </div>'
            f'  <div style="margin-top:15px; background:rgba(0,0,0,0.5); padding:10px; border-left:2px solid {tech_color}; font-family:monospace;">'
            f'      {signals_html}'
            f'  </div>'
            f'</div>'
        )
        st.markdown(html_tech, unsafe_allow_html=True)

    # --- RIGHT CARD: FUNDAMENTAL ---
    with c2:
        fund_color = fund['color']
        health_text = fund['health'].replace('💎','').replace('💪','').replace('⚠️','')
        
        score_val = 100 if "KIM" in health_text else (70 if "VỮNG" in health_text else 30)
        bars_html = f'<div style="width:100%; height:6px; background:#222; margin-top:10px; border-radius:3px;"><div style="width:{score_val}%; height:100%; background:{fund_color}; box-shadow:0 0 10px {fund_color};"></div></div>'

        fin_html = ""
        for d in fund['details']:
            color = "#ff0055" if any(x in d for x in ["cao", "Thấp", "giảm", "kém"]) else "#00ff41"
            fin_html += f'<div style="display:flex; align-items:center; margin-bottom:4px;"><div class="status-dot" style="background:{color}; box-shadow:0 0 5px {color};"></div><div style="font-size:12px; color:#ddd;">{d}</div></div>'

        html_fund = (
            f'<div class="hud-card" style="border-right:2px solid {fund_color}; border-left:1px solid #333;">'
            f'  <div style="display:flex; justify-content:space-between; align-items:end;">'
            f'      <div>'
            f'          <div class="glitch-text" style="font-size:14px; letter-spacing:2px; color:{fund_color};">FUNDAMENTAL_CORE</div>'
            f'          <div style="font-size:28px; font-weight:900; color:#fff; font-family:Rajdhani;">{health_text}</div>'
            f'      </div>'
            f'      <div style="text-align:right;">'
            f'          <div class="cyber-label">MARKET_CAP</div>'
            f'          <div style="font-size:18px; font-weight:700; color:#fff; font-family:Rajdhani;">{fund["market_cap"]/1e9:,.0f} B</div>'
            f'      </div>'
            f'  </div>'
            f'  {bars_html}'
            f'  <div style="margin-top:20px;">'
            f'      <div class="cyber-label" style="margin-bottom:10px; border-bottom:1px solid #333;">SYSTEM_DIAGNOSTICS</div>'
            f'      {fin_html}'
            f'  </div>'
            f'</div>'
        )
        st.markdown(html_fund, unsafe_allow_html=True)

# ==============================================================================
# 5. ADVANCED CHARTING (INTERACTIVE ZOOM & PAN)
# ==============================================================================
def render_interactive_chart(df, symbol):
    """
    Vẽ biểu đồ với khả năng Zoom/Pan mượt mà như TradingView.
    """
    if df.empty:
        st.error("NO DATA SIGNAL RECEIVED.")
        return

    try:
        if 'ITS_9' not in df.columns:
            ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
            if ichi is not None: df = df.join(ichi[0])
    except: pass

    # Layout: Giá (70%) + Volume (30%)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.7, 0.3]
    )
    
    # 1. Main Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='PRICE',
        increasing_line_color='#00ff41', increasing_fillcolor='rgba(0,0,0,0)',
        decreasing_line_color='#ff0055', decreasing_fillcolor='#ff0055',
        line_width=1
    ), row=1, col=1)
    
    # 2. Ichimoku Cloud
    if 'ISA_9' in df.columns and 'ISB_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ISA_9'], line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ISB_26'], line=dict(color='rgba(0,0,0,0)'), fill='tonexty', fillcolor='rgba(0, 243, 255, 0.1)', showlegend=False, hoverinfo='skip'), row=1, col=1)

    # 3. Volume Bar
    colors = ['#003300' if r['Open'] < r['Close'] else '#330000' for i, r in df.iterrows()]
    edge_colors = ['#00ff41' if r['Open'] < r['Close'] else '#ff0055' for i, r in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], 
        marker_color=colors, marker_line_color=edge_colors, marker_line_width=1,
        name='VOL', opacity=0.8
    ), row=2, col=1)

    # 4. Styling & Interaction Config
    fig.update_layout(
        template="plotly_dark",
        height=650,
        margin=dict(l=0, r=50, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False, # Tắt cái thanh trượt to đùng ở dưới
        hovermode="x unified",
        font=dict(family="Rajdhani", size=12, color="#aaa"),
        showlegend=False,
        
        # *** KEY CONFIGURATION FOR SMOOTH PAN/ZOOM ***
        dragmode='pan', # Mặc định là bàn tay để kéo (Pan)
        xaxis=dict(
            fixedrange=False, # Cho phép zoom trục X
            showgrid=True, gridwidth=1, gridcolor='rgba(0, 243, 255, 0.1)', zeroline=False
        ),
        yaxis=dict(
            fixedrange=False, # Cho phép zoom trục Y
            showgrid=True, gridwidth=1, gridcolor='rgba(0, 243, 255, 0.1)', zeroline=False, side='right'
        )
    )
    
    # Config object cho Plotly (Quan trọng!)
    config = {
        'scrollZoom': True,        # Cho phép lăn chuột để Zoom
        'displayModeBar': True,    # Hiện thanh công cụ nhỏ
        'modeBarButtonsIfNeeded': False,
        'displaylogo': False,      # Ẩn logo Plotly
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'] # Bỏ mấy nút ko cần
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config)
