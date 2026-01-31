import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. MONTE CARLO (Code cũ) ---
def run_monte_carlo(df, days=30, simulations=1000):
    if df.empty: return None, None, None
    
    # Tính toán thống kê
    data = df['Close']
    returns = data.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last_price = data.iloc[-1]
    
    # Chạy mô phỏng
    drift = mu - 0.5 * sigma**2
    Z = np.random.normal(0, 1, (days, simulations))
    daily_returns = np.exp(drift + sigma * Z)
    
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_price
    for t in range(1, days):
        price_paths[t] = price_paths[t-1] * daily_returns[t]
        
    simulation_df = pd.DataFrame(price_paths)
    
    # Vẽ Chart Đường (Line)
    fig = go.Figure()
    dates = [datetime.now() + timedelta(days=i) for i in range(days)]
    
    # Vẽ 50 đường mờ
    for i in range(min(50, simulations)):
        fig.add_trace(go.Scatter(x=dates, y=simulation_df.iloc[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
        
    # Đường trung bình
    fig.add_trace(go.Scatter(x=dates, y=simulation_df.mean(axis=1), mode='lines', line=dict(color='#22d3ee', width=4), name='Trung Bình'))
    
    fig.update_layout(title="🌌 Đa Vũ Trụ: 1000 Kịch Bản", template="plotly_dark", height=500, margin=dict(l=0,r=0,t=40,b=0))
    
    # Vẽ Chart Histogram (Phân phối)
    final_prices = simulation_df.iloc[-1]
    stats = { 
        "mean": final_prices.mean(), 
        "top_5": np.percentile(final_prices, 95), 
        "bot_5": np.percentile(final_prices, 5), 
        "prob_up": (final_prices > last_price).mean() * 100 
    }
    fig_hist = px.histogram(final_prices, nbins=50, title="📊 Phân Phối Giá Cuối Kỳ", template="plotly_dark")
    fig_hist.add_vline(x=last_price, line_dash="dash", line_color="red")
    
    return fig, fig_hist, stats

# --- 2. PROPHET AI (Code cũ) ---
def run_prophet_ai(df):
    try:
        from prophet import Prophet
        from prophet.plot import plot_plotly
        
        df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
        
        m = Prophet(daily_seasonality=True, yearly_seasonality=True)
        m.fit(df_p)
        future = m.make_future_dataframe(periods=60)
        forecast = m.predict(future)
        
        fig = plot_plotly(m, forecast)
        fig.update_layout(title="🔮 AI Prophet Dự Báo", template="plotly_dark", height=500)
        return fig
    except: return None
