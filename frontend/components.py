import streamlit as st
import plotly.graph_objects as go
import pandas_ta as ta

def render_score_card_v36(data):
    """Vẽ lại thẻ điểm số to đùng như ảnh cũ"""
    st.markdown(f"""
    <div style="background-color: #1f2937; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #374151; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <h4 style="color: #9ca3af; margin: 0; font-size: 0.9rem;">GÓC NHÌN KỸ THUẬT</h4>
        <div style="
            width: 80px; height: 80px; margin: 15px auto;
            border-radius: 50%; background: {data['color']};
            display: flex; align-items: center; justify-content: center;
            font-size: 2.5rem; font-weight: 900; color: white;
            box-shadow: 0 0 20px {data['color']};
        ">
            {data['score']}
        </div>
        <h2 style="color: {data['color']}; font-weight: 900; margin: 0; text-transform: uppercase;">{data['action']}</h2>
        <hr style="border-color: #374151; margin: 15px 0;">
        <div style="display: flex; justify-content: space-between;">
            <div><div style="font-size:0.8rem; color:#9ca3af">CẮT LỖ</div><div style="color:#ef4444; font-weight:bold">{data['stop_loss']:,.0f}</div></div>
            <div><div style="font-size:0.8rem; color:#9ca3af">MỤC TIÊU</div><div style="color:#10b981; font-weight:bold">{data['take_profit']:,.0f}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_fundamental_card(fund_data):
    """Vẽ lại bảng sức khỏe doanh nghiệp"""
    st.markdown(f"""
    <div style="background-color: #1f2937; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #374151; margin-bottom: 20px;">
        <h4 style="color: #9ca3af; margin: 0; font-size: 0.9rem;">SỨC KHỎE DOANH NGHIỆP</h4>
        <h2 style="color: {fund_data['health_color']}; font-weight: 900; margin: 10px 0;">{fund_data['health']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Các dòng checklist
    st.warning(f"⚠️ P/E: {fund_data['pe']}")
    st.success(f"✅ ROE: {fund_data['roe']}")
    st.success(f"✅ Vốn hóa: {fund_data['cap']}")
    st.success(f"🚀 {fund_data['growth']}")

def render_chart_v36(df, symbol):
    """Vẽ biểu đồ nến Ichimoku như bản cũ"""
    # Tính chỉ báo để vẽ
    ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'])[0]
    df = df.join(ichimoku)
    
    fig = go.Figure()
    # Nến Nhật
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Giá'))
    # Ichimoku
    fig.add_trace(go.Scatter(x=df.index, y=df[f'ITS_9'], line=dict(color='#22d3ee', width=1), name='Tenkan'))
    fig.add_trace(go.Scatter(x=df.index, y=df[f'IKS_26'], line=dict(color='#ef4444', width=1), name='Kijun'))
    
    fig.update_layout(
        title=f"Biểu đồ kỹ thuật {symbol}",
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
