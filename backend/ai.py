"""
================================================================================
MODULE: backend/ai.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.1.0-STABLE
DESCRIPTION: 
    Artificial Intelligence & Statistical Modeling Engine.
    Features:
    - Monte Carlo Simulation with VaR (Value at Risk) calculation.
    - Facebook Prophet for Time-series forecasting.
================================================================================
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict

# ==============================================================================
# 1. MONTE CARLO SIMULATION ENGINE
# ==============================================================================

class MonteCarloSimulator:
    """
    Mô phỏng biến động giá tương lai bằng phương pháp Geometric Brownian Motion (GBM).
    Tích hợp tính toán rủi ro (VaR).
    """
    def __init__(self, df: pd.DataFrame, days: int = 30, simulations: int = 1000):
        self.df = df
        self.days = days
        self.simulations = simulations
        
    def run(self) -> Tuple[Optional[go.Figure], Optional[go.Figure], Dict]:
        """
        Thực hiện mô phỏng.
        
        Returns:
            - Fig Line Chart (Các đường đi của giá)
            - Fig Histogram (Phân phối xác suất)
            - Stats Dict (Thống kê chi tiết)
        """
        if self.df.empty or len(self.df) < 30:
            return None, None, {}
            
        # 1. Tính tham số thống kê từ lịch sử
        data = self.df['Close']
        returns = data.pct_change().dropna()
        
        mu = returns.mean() # Lợi nhuận kỳ vọng hàng ngày
        sigma = returns.std() # Độ biến động (Volatility)
        last_price = data.iloc[-1]
        
        # 2. Geometric Brownian Motion Formula
        # Drift = mu - 0.5 * sigma^2
        drift = mu - 0.5 * sigma**2
        
        # Tạo ma trận ngẫu nhiên Z (Phân phối chuẩn)
        # Shape: (days, simulations)
        Z = np.random.normal(0, 1, (self.days, self.simulations))
        
        # Tính Daily Returns dự kiến
        daily_returns = np.exp(drift + sigma * Z)
        
        # Tính Price Paths (Cộng dồn)
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = last_price
        
        for t in range(1, self.days):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
            
        simulation_df = pd.DataFrame(price_paths)
        
        # 3. Visualization - Line Chart
        dates = [datetime.now() + timedelta(days=i) for i in range(self.days)]
        fig = go.Figure()
        
        # Vẽ 100 đường mờ đại diện (Vẽ hết 1000 sẽ nặng trình duyệt)
        display_sims = min(100, self.simulations)
        for i in range(display_sims):
            fig.add_trace(go.Scatter(
                x=dates, y=simulation_df.iloc[:, i],
                mode='lines',
                line=dict(width=1, color='#64748b'),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
            
        # Vẽ đường trung bình (Mean Path)
        mean_path = simulation_df.mean(axis=1)
        fig.add_trace(go.Scatter(
            x=dates, y=mean_path,
            mode='lines',
            line=dict(color='#0ea5e9', width=3),
            name='Kỳ vọng (Mean)'
        ))
        
        # Vẽ vùng tin cậy 95% (Confidence Interval)
        upper_bound = simulation_df.quantile(0.95, axis=1)
        lower_bound = simulation_df.quantile(0.05, axis=1)
        
        # Layout
        fig.update_layout(
            title=dict(text=f"🌌 MONTE CARLO: {self.simulations} SIMULATIONS", font=dict(family="Inter", size=18)),
            xaxis_title="Thời gian",
            yaxis_title="Giá dự kiến",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 4. Statistics & Histogram
        final_prices = simulation_df.iloc[-1]
        
        # Tính Value at Risk (VaR) 95%
        # Tức là: Có 95% xác suất giá sẽ KHÔNG giảm quá mức này
        var_95 = np.percentile(final_prices, 5)
        
        stats = {
            "mean": final_prices.mean(),
            "top_5": np.percentile(final_prices, 95), # Best Case
            "bot_5": var_95,                          # Worst Case (VaR)
            "prob_up": (final_prices > last_price).mean() * 100,
            "max_gain": (final_prices.max() - last_price) / last_price * 100,
            "max_loss": (final_prices.min() - last_price) / last_price * 100
        }
        
        # Histogram
        fig_hist = px.histogram(
            final_prices, 
            nbins=50, 
            title="📊 Phân phối xác suất giá cuối kỳ",
            color_discrete_sequence=['#10b981']
        )
        fig_hist.add_vline(x=last_price, line_dash="dash", line_color="#ef4444", annotation_text="Hiện tại")
        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False
        )
        
        return fig, fig_hist, stats

# ==============================================================================
# 2. PROPHET FORECASTING ENGINE
# ==============================================================================

class ProphetPredictor:
    """
    Wrapper class cho Facebook Prophet.
    Dự báo chuỗi thời gian (Time-series) với khả năng bắt sóng mùa vụ.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def predict(self, periods: int = 60) -> Optional[go.Figure]:
        """
        Chạy dự báo.
        """
        try:
            from prophet import Prophet
        except ImportError:
            return None
            
        if self.df.empty or len(self.df) < 60: return None
        
        # Prepare Data
        df_p = self.df.reset_index()[['Date', 'Close']].copy()
        df_p.columns = ['ds', 'y']
        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
        
        # Init Model (Tuning nhẹ)
        m = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05, # Linh hoạt vừa phải
            seasonality_mode='multiplicative' # Mô hình nhân (biến động tăng theo giá)
        )
        
        m.fit(df_p)
        
        # Forecast
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        # Plotting (Custom Plotly)
        fig = go.Figure()
        
        # Historical Data
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='lines', name='Lịch sử',
            line=dict(color='#94a3b8', width=1.5)
        ))
        
        # Forecast Data
        future_data = forecast[forecast['ds'] > df_p['ds'].iloc[-1]]
        fig.add_trace(go.Scatter(
            x=future_data['ds'], y=future_data['yhat'],
            mode='lines', name='AI Dự báo',
            line=dict(color='#f472b6', width=2)
        ))
        
        # Uncertainty Interval (Mây rủi ro)
        fig.add_trace(go.Scatter(
            x=pd.concat([future_data['ds'], future_data['ds'][::-1]]),
            y=pd.concat([future_data['yhat_upper'], future_data['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(244, 114, 182, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Biên độ tin cậy'
        ))
        
        fig.update_layout(
            title=dict(text=f"🔮 AI PROPHET: DỰ BÁO {periods} NGÀY TỚI", font=dict(family="Inter", size=18)),
            yaxis_title="Giá",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig

# ==============================================================================
# 3. WRAPPER FUNCTIONS
# ==============================================================================

def run_monte_carlo(df: pd.DataFrame) -> Tuple:
    simulator = MonteCarloSimulator(df)
    return simulator.run()

def run_prophet_ai(df: pd.DataFrame) -> Optional[go.Figure]:
    predictor = ProphetPredictor(df)
    return predictor.predict()
