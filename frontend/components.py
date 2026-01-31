import streamlit as st
import plotly.graph_objects as go
import pandas_ta as ta

def render_market_overview(indices_data):
    """Vẽ thanh chỉ số thị trường (Xử lý trường hợp Offline)"""
    if not indices_data: return

    cols = st.columns(len(indices_data))
    
    for i, data in enumerate(indices_data):
        with cols[i]:
            if data['Status'] == "LIVE":
                arrow = "▲" if data['Change'] >= 0 else "▼"
                price_display = f"{data['Price']:,.2f}"
                change_display = f"{arrow} {data['Change']:,.2f} ({data['Pct']:+.2f}%)"
                color = data['Color']
            else:
                # Trường hợp không lấy được dữ liệu
                price_display = "---"
                change_display = "OFFLINE"
                color = "#64748b" # Xám

            st.markdown(f"""
            <div style="
                background-color: #111827; 
                border: 1px solid #374151; 
                border-radius: 8px; 
                padding: 15px; 
                margin-bottom: 10px;
                text-align: center;
            ">
                <div style="font-family: 'Rajdhani'; color: #9ca3af; font-size: 0.8rem; font-weight: 700; letter-spacing: 1px;">
                    {data['Name']}
                </div>
                <div style="font-family: 'Rajdhani'; font-size: 1.6rem; font-weight: 800; color: {color}; margin: 5px 0;">
                    {price_display}
                </div>
                <div style="font-family: 'Inter'; font-size: 0.8rem; color: {color}; font-weight: 600;">
                    {change_display}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_score_card_v36(data):
    # (Giữ nguyên code cũ)
    st.markdown(f"""
    <div style="background-color: #111827; border-radius: 15px; padding: 25px; text-align: center; border: 1px solid #374151; margin-bottom: 20px;">
        <h4 style="color: #9ca3af; margin: 0; font-size: 0.85rem; letter-spacing: 2px;">TECHNICAL RATING</h4>
        <div style="width: 100px; height: 100px; margin: 20px auto; border-radius: 50%; background: {data['color']}; display: flex; align-items: center; justify-content: center; font-size: 3.5rem; font-weight: 900; color: white; box-shadow: 0 0 30px {data['color']};">
            {data['score']}
        </div>
        <h1 style="color: {data['color']}; font-weight: 900; margin: 0; font-size: 2.2rem; text-transform: uppercase;">
            {data['action']}
        </h1>
    </div>
    """, unsafe_allow_html=True)

def render_interactive_chart(df, symbol):
    # (Giữ nguyên code cũ)
    if df.empty: return
    ichi = ta.ichimoku(df['High'], df['Low'], df['Close'])
    if ichi is not None: df = df.join(ichi[0])
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
    if 'ITS_9' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['ITS_9'], line=dict(color='#22d3ee', width=1), name='Tenkan'))
    if 'IKS_26' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['IKS_26'], line=dict(color='#ef4444', width=1), name='Kijun'))

    fig.update_layout(
        title=dict(text=f"{symbol} - TECHNICAL CHART", font=dict(family="Rajdhani", size=20, color="white")),
        template="plotly_dark", height=500, xaxis_rangeslider_visible=True,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10), hovermode="x unified", dragmode="pan"
    )
    st.plotly_chart(fig, use_container_width=True)
