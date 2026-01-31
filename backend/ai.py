import numpy as np
import pandas as pd
from datetime import datetime, timedelta
# Import Prophet ở đây (đặt trong try/except nếu sợ lỗi)
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except: 
    PROPHET_AVAILABLE = False

def run_monte_carlo_sim(df, days=30, simulations=1000):
    # (Copy logic tính toán Monte Carlo cũ vào đây)
    # Lưu ý: Chỉ trả về DataFrame kết quả, KHÔNG vẽ biểu đồ ở đây
    if df.empty: return None
    data = df['Close']
    returns = data.pct_change().dropna()
    mu = returns.mean(); sigma = returns.std(); last_price = data.iloc[-1]
    drift = mu - 0.5 * sigma**2
    Z = np.random.normal(0, 1, (days, simulations))
    daily_returns = np.exp(drift + sigma * Z)
    price_paths = np.zeros_like(daily_returns); price_paths[0] = last_price
    for t in range(1, days): price_paths[t] = price_paths[t-1] * daily_returns[t]
    return pd.DataFrame(price_paths)

def run_prophet_ai(df, periods=30):
    if not PROPHET_AVAILABLE: return None
    # (Copy logic Prophet cũ vào đây)
    df_p = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
    m = Prophet(daily_seasonality=True)
    m.fit(df_p)
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    return m, forecast # Trả về model và data dự báo
