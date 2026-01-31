import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ==============================================================================
# 1. MONTE CARLO SIMULATION (ĐA VŨ TRỤ)
# Giả lập hàng nghìn kịch bản giá dựa trên chuyển động Brown hình học (GBM)
# ==============================================================================
def run_monte_carlo(df, days=30, simulations=1000):
    """
    Chạy mô phỏng Monte Carlo.
    - df: Dữ liệu lịch sử
    - days: Số ngày dự báo (mặc định 30 ngày)
    - simulations: Số lượng kịch bản (mặc định 1000 vũ trụ)
    """
    if df.empty or len(df) < 30: return None, None, None
    
    # 1. Tính toán tham số từ dữ liệu quá khứ
    data = df['Close']
    returns = data.pct_change().dropna()
    
    mu = returns.mean() # Lợi nhuận trung bình hàng ngày
    sigma = returns.std() # Độ lệch chuẩn (Biến động)
    last_price = data.iloc[-1]
    
    # 2. Công thức Geometric Brownian Motion (GBM)
    # Drift = mu - 0.5 * sigma^2
    drift = mu - 0.5 * sigma**2
    
    # Tạo ma trận ngẫu nhiên Z (Chuẩn hóa)
    Z = np.random.normal(0, 1, (days, simulations))
    
    # Tính lợi nhuận hàng ngày dự kiến
    daily_returns = np.exp(drift + sigma * Z)
    
    # 3. Tính đường đi của giá
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_price
    
    for t in range(1, days):
        price_paths[t] = price_paths[t-1] * daily_returns[t]
        
    simulation_df = pd.DataFrame(price_paths)
    
    # 4. Vẽ biểu đồ Đường (Line Chart) - Các kịch bản
    dates = [datetime.now() + timedelta(days=i) for i in range(days)]
    fig = go.Figure()
    
    # Vẽ 50 đường mờ đại diện (để không bị rối mắt)
    for i in range(min(50, simulations)):
        fig.add_trace(go.Scatter(
            x=dates, y=simulation_df.iloc[:, i],
            mode='lines',
            line=dict(width=1, color='#94a3b8'), # Màu xám nhạt
            opacity=0.2,
            showlegend=False,
            hoverinfo='skip'
        ))
        
    # Vẽ đường trung bình (Kỳ vọng)
    fig.add_trace(go.Scatter(
        x=dates, y=simulation_df.mean(axis=1),
        mode='lines',
        line=dict(color='#22d3ee', width=4), # Màu Cyan nổi bật
        name='Trung Bình (Kỳ vọng)'
    ))
    
    # Trang trí biểu đồ
    fig.update_layout(
        title=dict(text=f"🌌 Đa Vũ Trụ: {simulations} Kịch Bản Tương Lai", font=dict(color="white", size=20)),
        yaxis_title="Giá Dự Kiến",
        template="plotly_dark",
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # 5. Vẽ biểu đồ Phân phối (Histogram) - Xác suất giá cuối kỳ
    final_prices = simulation_df.iloc[-1]
    
    # Thống kê quan trọng
    stats = { 
        "mean": final_prices.mean(), 
        "top_5": np.percentile(final_prices, 95), # Kịch bản siêu tốt
        "bot_5": np.percentile(final_prices, 5),  # Kịch bản tồi tệ
        "prob_up": (final_prices > last_price).mean() * 100 # Xác suất tăng giá
    }
    
    fig_hist = px.histogram(
        final_prices, 
        nbins=50, 
        title="📊 Phân Phối Giá Cuối Kỳ (Xác Suất)",
        color_discrete_sequence=['#10b981'] # Màu xanh
    )
    
    # Kẻ vạch giá hiện tại
    fig_hist.add_vline(x=last_price, line_dash="dash", line_color="#ef4444", annotation_text="Giá Hiện Tại")
    
    fig_hist.update_layout(
        template="plotly_dark", 
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig, fig_hist, stats

# ==============================================================================
# 2. AI PROPHET FORECAST (FACEBOOK)
# Dự báo xu hướng dài hạn
# ==============================================================================
def run_prophet_ai(df, periods=60):
    """
    Chạy mô hình Prophet.
    - periods: Số ngày dự báo tương lai (mặc định 60 ngày)
    """
    try:
        from prophet import Prophet
    except ImportError:
        return None # Chưa cài thư viện thì trả về None
        
    if df.empty or len(df) < 60: return None

    # 1. Chuẩn bị dữ liệu chuẩn Prophet (ds, y)
    df_prophet = df.reset_index()[['Date', 'Close']].copy()
    df_prophet.columns = ['ds', 'y']
    # Loại bỏ múi giờ nếu có để tránh lỗi
    df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
    
    # 2. Cấu hình Model
    # Bật tính mùa vụ (Seasonality) để bắt sóng
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05 # Độ nhạy linh hoạt
    )
    
    m.fit(df_prophet)
    
    # 3. Dự báo
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    
    # 4. Vẽ Chart thủ công bằng Plotly (Cho đẹp hơn hàm có sẵn)
    fig = go.Figure()
    
    # Dữ liệu thực tế (Quá khứ)
    fig.add_trace(go.Scatter(
        x=df_prophet['ds'], y=df_prophet['y'],
        mode='lines', name='Thực tế',
        line=dict(color='#94a3b8', width=2)
    ))
    
    # Dữ liệu dự báo (Tương lai)
    future_data = forecast[forecast['ds'] > df_prophet['ds'].iloc[-1]]
    fig.add_trace(go.Scatter(
        x=future_data['ds'], y=future_data['yhat'],
        mode='lines', name='AI Dự Báo',
        line=dict(color='#f472b6', width=2, dash='dot') # Màu hồng, nét đứt
    ))
    
    # Dải tin cậy (Upper/Lower Bound) - Vùng mây
    fig.add_trace(go.Scatter(
        x=pd.concat([future_data['ds'], future_data['ds'][::-1]]),
        y=pd.concat([future_data['yhat_upper'], future_data['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(244, 114, 182, 0.1)', # Hồng nhạt trong suốt
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False,
        name='Biên độ dao động'
    ))

    fig.update_layout(
        title=dict(text="🔮 AI Tiên Tri: Xu Hướng 60 Ngày Tới", font=dict(size=20)),
        yaxis_title="Giá",
        template="plotly_dark",
        height=500,
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig
