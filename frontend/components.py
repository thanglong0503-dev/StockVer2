import streamlit as st
import plotly.graph_objects as go
import pandas_ta as ta

def render_score_card_v36(data):
    st.markdown(f"""
    <div style="background-color: #111827; border-radius: 15px; padding: 25px; text-align: center; border: 1px solid #374151; margin-bottom: 20px;">
        <h4 style="color: #9ca3af; margin: 0; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase;">Technical Rating</h4>
        <div style="
            width: 100px; height: 100px; margin: 20px auto;
            border-radius: 50%; background: {data['color']};
            display: flex; align-items: center; justify-content: center;
            font-size: 3.5rem; font-weight: 900; color: white;
            box-shadow: 0 0 30px {data['color']};
        ">
            {data['score']}
        </div>
        <h1 style="color: {data['color']}; font-weight: 900; margin: 0; font-size: 2.2rem; text-transform: uppercase; text-shadow: 0 0 15px {data['color']};">
            {data['action']}
        </h1>
    </div>
    """, unsafe_allow_html=True)

def render_interactive_chart(df, symbol):
    """Biểu đồ Interactive: Zoom, Pan, Range Slider"""
    if df.empty: return
    
    # Tính Ichimoku
    ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
    if ichi is not None: df = df.join(ichi[0])
    
    fig = go.Figure()
    
    # 1. Nến Nhật
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price'
    ))
    
    # 2. Ichimoku Clouds (Chỉ vẽ Tenkan/Kijun cho gọn, đỡ rối)
    if 'ITS_9' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ITS_9'], line=dict(color='#22d3ee', width=1.5), name='Tenkan'))
    if 'IKS_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['IKS_26'], line=dict(color='#ef4444', width=1.5), name='Kijun'))

    # 3. Cấu hình Zoom/Pan (Quan trọng)
    fig.update_layout(
        title=dict(text=f"{symbol} - TECHNICAL CHART", font=dict(family="Rajdhani", size=24, color="white")),
        template="plotly_dark",
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True), # THANH KÉO BÊN DƯỚI
            type="date"
        ),
        yaxis=dict(fixedrange=False), # Cho phép kéo trục Y
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        dragmode="pan" # Mặc định là chế độ Kéo thả
    )
    st.plotly_chart(fig, use_container_width=True)
