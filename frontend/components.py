import streamlit as st
import plotly.graph_objects as go
import pandas_ta as ta

def render_score_card_v36(data):
    """Vẽ thẻ điểm số to đùng"""
    st.markdown(f"""
    <div style="background-color: #1f2937; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #374151; margin-bottom: 20px;">
        <h4 style="color: #9ca3af; margin: 0; font-size: 0.9rem; letter-spacing: 1px;">GÓC NHÌN KỸ THUẬT</h4>
        <div style="
            width: 90px; height: 90px; margin: 20px auto;
            border-radius: 50%; background: {data['color']};
            display: flex; align-items: center; justify-content: center;
            font-size: 3rem; font-weight: 900; color: white;
            box-shadow: 0 0 25px {data['color']};
        ">
            {data['score']}
        </div>
        <h1 style="color: {data['color']}; font-weight: 900; margin: 0; font-size: 2rem; text-transform: uppercase; text-shadow: 0 0 10px {data['color']};">
            {data['action']}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chart_v36(df, symbol):
    """Vẽ biểu đồ nến + Ichimoku"""
    if df.empty: return
    
    # Tính Ichimoku để vẽ
    ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
    if ichi is not None:
        df = df.join(ichi[0]) # ichi[0] chứa Tenkan, Kijun...
    
    fig = go.Figure()
    
    # 1. Nến Nhật
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
        name='Giá'
    ))
    
    # 2. Ichimoku (Tenkan & Kijun)
    # Kiểm tra xem cột có tồn tại không trước khi vẽ để tránh lỗi
    if 'ITS_9' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ITS_9'], line=dict(color='#22d3ee', width=1.5), name='Tenkan (Xanh)'))
    if 'IKS_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['IKS_26'], line=dict(color='#ef4444', width=1.5), name='Kijun (Đỏ)'))
    
    fig.update_layout(
        title=f"Biểu đồ kỹ thuật: {symbol}",
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)', # Nền trong suốt
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
