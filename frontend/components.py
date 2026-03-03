"""
================================================================================
MODULE: frontend/components.py
THEME: ULTRA CYBERPUNK HUD INTERFACE
VERSION: 40.6.0-GALAXY-ULTIMATE
DESCRIPTION: 
    - Visuals: Cyberpunk CSS, SVG Gauges, Neon Effects.
    - Logic: Smart Analysis Display (Hide Entry on Sell, 9 Fundamental Metrics).
    - Charts: Interactive Zoom/Pan + Neon Crosshair (Spikelines).
    - Galaxy: 3D Market Visualization based on Volume Explosion.
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px  # Cần cái này để vẽ Galaxy
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

        /* 2. HUD CARD CONTAINER (3D HOLOGRAPHIC EFFECT) */
        .hud-card {
            background: rgba(10, 15, 20, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            position: relative;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .hud-card:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: rgba(0, 243, 255, 0.5);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 243, 255, 0.2), inset 0 0 0 1px rgba(0, 243, 255, 0.1);
        }
        .hud-card::after {
            content: ""; position: absolute; top: 10px; bottom: 10px; left: 0; width: 3px;
            background: linear-gradient(to bottom, #00f3ff, transparent);
            border-radius: 0 4px 4px 0; opacity: 0.7;
        }

        /* 3. TEXT GLITCH EFFECT */
        .glitch-text { color: #fff; font-family: 'Rajdhani', sans-serif; font-weight: 800; position: relative; text-transform: uppercase; }
        
        /* 4. METRIC GRID */
        .cyber-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px; border-top: 1px solid #333; padding-top: 15px; }
        .cyber-metric { background: #0a0f14; padding: 8px; border: 1px solid #222; }
        .cyber-label { font-size: 10px; color: #00f3ff; text-transform: uppercase; letter-spacing: 1px; }
        .cyber-val { font-size: 16px; color: #fff; font-weight: 700; font-family: 'Rajdhani'; }

        /* 5. STATUS INDICATORS */
        .status-dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; box-shadow: 0 0 5px currentColor; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==============================================================================
# 2. SVG GENERATOR (VẼ ĐỒ HỌA BẰNG CODE)
# ==============================================================================
def create_svg_gauge(score, color):
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
        
        # [LOGIC] Ẩn số liệu khi Báo Bán (Entry=0)
        if tech['entry'] > 0:
            val_entry = f"{tech['entry']:,.0f}"
            val_target = f"{tech['target']:,.0f}"
            val_stop = f"{tech['stop']:,.0f}"
            style_target = "color:#00ff41;"
            style_stop = "color:#ff0055;"
        else:
            val_entry = "<span style='color:#666; font-weight:400'>---</span>"
            val_target = "<span style='color:#666; font-weight:400'>---</span>"
            val_stop = "<span style='color:#666; font-weight:400'>---</span>"
            style_target = "color:#666;"
            style_stop = "color:#666;"
        
        signals_html = ""
        for p in tech['pros'][:3]: signals_html += f'<div style="color:#00ff41; font-size:12px; margin-bottom:2px;">[+] {p}</div>'
        for c in tech['cons'][:2]: signals_html += f'<div style="color:#ff0055; font-size:12px; margin-bottom:2px;">[-] {c}</div>'
            
        html_tech = (f'<div class="hud-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><div class="glitch-text" style="font-size:14px; letter-spacing:2px; color:{tech_color};">TECHNICAL_SYS_V36</div><div style="font-size:32px; font-weight:900; color:#fff; font-family:Rajdhani; text-shadow:0 0 15px {tech_color};">{action_text}</div></div><div>{gauge_svg}</div></div><div class="cyber-grid"><div class="cyber-metric"><div class="cyber-label">ENTRY_ZONE</div><div class="cyber-val">{val_entry}</div></div><div class="cyber-metric"><div class="cyber-label">TARGET_LOCK</div><div class="cyber-val" style="{style_target}">{val_target}</div></div><div class="cyber-metric"><div class="cyber-label">STOP_LOSS</div><div class="cyber-val" style="{style_stop}">{val_stop}</div></div><div class="cyber-metric"><div class="cyber-label">ATR_VOLTY</div><div class="cyber-val">{tech.get("atr", 0):,.0f}</div></div></div><div style="margin-top:15px; background:rgba(0,0,0,0.5); padding:10px; border-left:2px solid {tech_color}; font-family:monospace;">{signals_html}</div></div>')
        st.markdown(html_tech, unsafe_allow_html=True)

    # --- RIGHT CARD: FUNDAMENTAL ---
    with c2:
        fund_color = fund['color']
        health_text = fund['health'].replace('💎','').replace('💪','').replace('⚠️','')
        
        score_val = 100 if "MẠNH" in health_text else (70 if "ỔN" in health_text else 30)
        bars_html = f'<div style="width:100%; height:6px; background:#222; margin-top:10px; border-radius:3px;"><div style="width:{score_val}%; height:100%; background:{fund_color}; box-shadow:0 0 10px {fund_color};"></div></div>'

        # [METRICS GRID]
        metrics = fund.get('metrics', {})
        metrics_html = '<div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-top:15px;">'
        
        display_keys = [
            ('Rev Growth', 'Tăng Trưởng DT'), ('NI Growth', 'Tăng Trưởng LN'), ('ROE', 'ROE'),
            ('Net Margin', 'Biên Lợi Nhuận'), ('Debt/Asset', 'Nợ/Tài Sản'), ('Current Ratio', 'Thanh Toán HH'),
            ('OCF', 'Dòng Tiền KD'), ('BEP', 'Sinh Lời CS'), ('Inv Turnover', 'Vòng Quay Kho')
        ]
        
        for key, label in display_keys:
            val = metrics.get(key, 'N/A')
            color_val = "#fff"
            if "Growth" in key: color_val = "#00ff41" if "-" not in str(val) else "#ff0055"
            if "OCF" in key: color_val = "#00ff41" if "-" not in str(val) else "#ff0055"
            # [FIXED HTML]
            metrics_html += f'<div style="background:rgba(255,255,255,0.05); padding:5px; border-radius:4px; text-align:center;"><div style="font-size:9px; color:#888;">{label}</div><div style="font-size:12px; font-weight:bold; color:{color_val}; font-family:Rajdhani;">{val}</div></div>'
            
        metrics_html += "</div>"

        fin_html = ""
        for d in fund['details'][:3]:
            color = "#ff0055" if any(x in d for x in ["cao", "Thấp", "giảm", "kém", "Âm"]) else "#00ff41"
            fin_html += f'<div style="display:flex; align-items:center; margin-bottom:2px;"><div class="status-dot" style="background:{color}; box-shadow:0 0 5px {color};"></div><div style="font-size:11px; color:#ddd;">{d}</div></div>'

        html_fund = (f'<div class="hud-card" style="border-right:2px solid {fund_color}; border-left:1px solid #333;"><div style="display:flex; justify-content:space-between; align-items:end;"><div><div class="glitch-text" style="font-size:14px; letter-spacing:2px; color:{fund_color};">FUNDAMENTAL_CORE</div><div style="font-size:28px; font-weight:900; color:#fff; font-family:Rajdhani;">{health_text}</div></div><div style="text-align:right;"><div class="cyber-label">MARKET_CAP</div><div style="font-size:18px; font-weight:700; color:#fff; font-family:Rajdhani;">{fund["market_cap"]/1e9:,.0f} B</div></div></div>{bars_html}{metrics_html}<div style="margin-top:15px; border-top:1px solid #333; padding-top:10px;">{fin_html}</div></div>')
        st.markdown(html_fund, unsafe_allow_html=True)

# ==============================================================================
# 5. ADVANCED CHARTING (INTERACTIVE ZOOM & PAN & CROSSHAIR)
# ==============================================================================
def render_interactive_chart(df, symbol):
    """
    Vẽ biểu đồ với khả năng Zoom/Pan + Crosshair (Spikelines) Neon.
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
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # 1. Main Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='PRICE', increasing_line_color='#00ff41', increasing_fillcolor='rgba(0,0,0,0)',
        decreasing_line_color='#ff0055', decreasing_fillcolor='#ff0055', line_width=1
    ), row=1, col=1)
    
    # 2. Ichimoku Cloud
    if 'ISA_9' in df.columns and 'ISB_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ISA_9'], line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ISB_26'], line=dict(color='rgba(0,0,0,0)'), fill='tonexty', fillcolor='rgba(0, 243, 255, 0.1)', showlegend=False, hoverinfo='skip'), row=1, col=1)

    # 3. Volume Bar
    colors = ['#003300' if r['Open'] < r['Close'] else '#330000' for i, r in df.iterrows()]
    edge_colors = ['#00ff41' if r['Open'] < r['Close'] else '#ff0055' for i, r in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], marker_color=colors, marker_line_color=edge_colors, 
        marker_line_width=1, name='VOL', opacity=0.8
    ), row=2, col=1)

    # 4. Styling & Interaction Config (FULL OPTION)
    fig.update_layout(
        template="plotly_dark", height=650, margin=dict(l=0, r=50, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False, hovermode="x unified",
        font=dict(family="Rajdhani", size=12, color="#aaa"), showlegend=False,
        dragmode='pan', 
        # *** NEON CROSSHAIR ***
        xaxis=dict(fixedrange=False, showgrid=True, gridwidth=1, gridcolor='rgba(0, 243, 255, 0.1)', zeroline=False, showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid', spikecolor='#00f3ff', spikethickness=1),
        yaxis=dict(fixedrange=False, showgrid=True, gridwidth=1, gridcolor='rgba(0, 243, 255, 0.1)', zeroline=False, side='right', showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='dot', spikecolor='#ff0055', spikethickness=1)
    )
    
    config = {'scrollZoom': True, 'displayModeBar': True, 'modeBarButtonsIfNeeded': False, 'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d']}
    st.plotly_chart(fig, use_container_width=True, config=config)

# ==============================================================================
# 6. MARKET GALAXY (LOGO EDITION - VOLUME EXPLOSION)
# ==============================================================================
def render_market_galaxy(df):
    """
    Vẽ biểu đồ Galaxy - BẢN LOGO TOP 50.
    - Hiển thị LOGO doanh nghiệp thay vì chấm tròn.
    - Kích thước Logo TO/NHỎ phụ thuộc vào VOLUME (Dòng tiền).
    - Giữ nguyên tính năng Zoom/Pan mượt mà.
    """
    if df.empty: return

    # 1. XỬ LÝ DỮ LIỆU
    # Tính toán tỷ lệ Volume để scale kích thước Logo
    if 'Vol_Ratio' not in df.columns: 
        mean_vol = df['Volume'].mean() if df['Volume'].mean() > 0 else 1
        df['Vol_Ratio'] = df['Volume'] / mean_vol

    # Lấy Top 50 mã mạnh nhất
    df_galaxy = df.sort_values(by='Vol_Ratio', ascending=False).head(50).copy()
    
    # Tạo thông tin Hover (Rê chuột vào khoảng trống quanh logo vẫn hiện số)
    df_galaxy['Hover_Info'] = df_galaxy.apply(lambda row: (
        f"<b>{row['Symbol']}</b><br>"
        f"💰 Giá: {row['Price']:.2f}<br>"
        f"📈 Change: {row['Pct']:.2f}%<br>"
        f"🦈 Vol Ratio: <b>{row['Vol_Ratio']:.1f}x</b>"
    ), axis=1)

    # 2. TẠO KHUNG BIỂU ĐỒ (Dùng Scatter ẩn để làm khung sườn)
    # Ta vẫn vẽ các chấm tròn nhưng cho độ trong suốt = 0 (Tàng hình)
    # Mục đích: Để Plotly tạo hệ trục tọa độ và tính năng Zoom/Pan
    fig = px.scatter(
        df_galaxy,
        x="Price",
        y="Pct",
        size="Vol_Ratio", # Vẫn giữ size để khung sườn chuẩn
        hover_name="Hover_Info",
        template="plotly_dark",
        height=600 # Tăng chiều cao xíu cho thoáng
    )

    # Ẩn hoàn toàn các chấm tròn (chỉ giữ lại khung và hover)
    fig.update_traces(marker=dict(opacity=0, line=dict(width=0)))

    # 3. CHÈN LOGO VÀO (Scale theo Volume)
    # Tính toán hệ số scale cho ảnh
    x_range = df_galaxy['Price'].max() - df_galaxy['Price'].min()
    y_range = df_galaxy['Pct'].max() - df_galaxy['Pct'].min()
    
    # Kích thước cơ sở (Base size)
    base_sizex = (x_range * 0.03) if x_range > 0 else 1.0
    base_sizey = (y_range * 0.06) if y_range > 0 else 0.5
    
    # Nguồn Logo (Simplize PNG trong suốt)
    logo_base_url = "https://cdn.simplize.vn/simplefi/company/logo/"

    for index, row in df_galaxy.iterrows():
        ticker = row['Symbol'].strip().upper()
        logo_url = f"{logo_base_url}{ticker}.png"
        
        # [QUAN TRỌNG] Logic phóng to Logo theo Volume
        # Vol_Ratio càng lớn -> Logo càng to
        # Ta dùng hàm log hoặc căn bậc 2 để tránh logo quá to che hết màn hình
        # Ở đây ta nhân thẳng tỷ lệ nhưng giới hạn lại một chút
        
        scale_factor = row['Vol_Ratio'] 
        # Kìm hãm bớt nếu scale quá lớn (chỉ cho max gấp 3 lần bình thường)
        if scale_factor > 3: scale_factor = 3
        if scale_factor < 0.8: scale_factor = 0.8 # Không cho bé quá
        
        final_sizex = base_sizex * scale_factor
        final_sizey = base_sizey * scale_factor

        # Thêm ảnh vào biểu đồ
        fig.add_layout_image(
            dict(
                source=logo_url,
                xref="x", yref="y",
                x=row['Price'],
                y=row['Pct'],
                sizex=final_sizex,
                sizey=final_sizey,
                xanchor="center", yanchor="middle",
                layer="above",
                opacity=0.95
            )
        )

    # 4. CẤU HÌNH TRỤC VÀ GIAO DIỆN
    fig.update_layout(
        title=dict(
            text="🌌 TOP 50 MARKET LOGOS (VOLUME SCALED)",
            font=dict(family="Rajdhani", size=18, color="#00f3ff")
        ),
        xaxis=dict(
            title="GIÁ (K)",
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            fixedrange=False # Cho phép Zoom
        ),
        yaxis=dict(
            title="% CHANGE",
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=True, 
            zerolinecolor='rgba(255,255,255,0.3)',
            fixedrange=False # Cho phép Zoom
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        dragmode='pan',
        hovermode='closest'
    )

    # 5. THANH CÔNG CỤ
    config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'responsive': True
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config, key="galaxy_logo_v50")
