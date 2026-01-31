"""
================================================================================
MODULE: backend/ai.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.3.1-AI-FIX
DESCRIPTION: 
    Artificial Intelligence & Statistical Modeling Engine.
    FIXED: 
    - Prophet: Removed daily_seasonality noise (Smoother lines).
    - Charts: Enabled Pan/Zoom interactions.
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
    """
    def __init__(self, df: pd.DataFrame, days: int = 30, simulations: int = 1000):
        self.df = df
        self.days = days
        self.simulations = simulations
        
    def run(self) -> Tuple[Optional[go.Figure], Optional[go.Figure], Dict]:
        if self.df.empty or len(self.df) < 30:
            return None, None, {}
            
        # 1. Tính tham số thống kê
        data = self.df['Close']
        returns = data.pct_change().dropna()
        
        mu = returns.mean() 
        sigma = returns.std() 
        last_price = data.iloc[-1]
        
        # 2. GBM Formula
        drift = mu - 0.5 * sigma**2
        Z = np.random.normal(0, 1, (self.days, self.simulations))
        daily_returns = np.exp(drift + sigma * Z)
        
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = last_price
        
        for t in range(1, self.days):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
            
        simulation_df = pd.DataFrame(price_paths)
        
        # 3. Visualization - Line Chart (FIXED INTERACTION)
        dates = [datetime.now() + timedelta(days=i) for i in range(self.days)]
        fig = go.Figure()
        
        # Vẽ 50 đường mờ
        display_sims = min(50, self.simulations)
        for i in range(display_sims):
            fig.add_trace(go.Scatter(
                x=dates, y=simulation_df.iloc[:, i],
                mode='lines', line=dict(width=1, color='#64748b'), opacity=0.1,
                showlegend=False, hoverinfo='skip'
            ))
            
        # Vẽ đường trung bình
        fig.add_trace(go.Scatter(
            x=dates, y=simulation_df.mean(axis=1),
            mode='lines', line=dict(color='#0ea5e9', width=3),
            name='Kỳ vọng (Mean)'
        ))
        
        # Layout chuẩn TradingView (Zoom/Pan)
        fig.update_layout(
            title=dict(text=f"🌌 MONTE CARLO: {self.simulations} KỊCH BẢN", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=40, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            dragmode='pan', # Cho phép kéo
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', fixedrange=False), # Cho phép Zoom X
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', fixedrange=False, side='right') # Cho phép Zoom Y
        )
        
        # 4. Stats
        final_prices = simulation_df.iloc[-1]
        stats = {
            "mean": final_prices.mean(),
            "top_5": np.percentile(final_prices, 95),
            "bot_5": np.percentile(final_prices, 5),
            "prob_up": (final_prices > last_price).mean() * 100
        }
        
        # Histogram
        fig_hist = px.histogram(final_prices, nbins=50, title="📊 PHÂN PHỐI XÁC SUẤT", color_discrete_sequence=['#10b981'])
        fig_hist.add_vline(x=last_price, line_dash="dash", line_color="#ef4444")
        fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        
        return fig, fig_hist, stats

# ==============================================================================
# 2. PROPHET FORECASTING ENGINE (FIXED SMOOTHNESS)
# ==============================================================================

class ProphetPredictor:
    """
    Wrapper class cho Facebook Prophet.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def predict(self, periods: int = 60) -> Optional[go.Figure]:
        try:
            from prophet import Prophet
        except ImportError: return None
            
        if self.df.empty or len(self.df) < 60: return None
        
        # Prepare Data
        df_p = self.df.reset_index()[['Date', 'Close']].copy()
        df_p.columns = ['ds', 'y']
        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
        
        # --- FIX QUAN TRỌNG: TẮT DAILY SEASONALITY ---
        # daily_seasonality=False: Loại bỏ nhiễu dao động trong ngày (nguyên nhân gây hình voằng vèo)
        # seasonality_mode='additive': Cộng dồn xu hướng, ổn định hơn cho chứng khoán VN
        m = Prophet(
            daily_seasonality=False,  # <--- FIX CHÍNH
            weekly_seasonality=True,  # Bắt sóng tuần
            yearly_seasonality=True,  # Bắt sóng năm
            changepoint_prior_scale=0.05,
            seasonality_mode='additive'
        )
        
        m.fit(df_p)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        # Plotting Custom
        fig = go.Figure()
        
        # 1. Dữ liệu Lịch sử (Màu xám)
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='lines', name='Lịch sử',
            line=dict(color='#64748b', width=1.5)
        ))
        
        # 2. Dữ liệu Dự báo (Màu hồng Neon)
        # Chỉ lấy phần tương lai để vẽ
        future_data = forecast[forecast['ds'] > df_p['ds'].iloc[-1]]
        
        fig.add_trace(go.Scatter(
            x=future_data['ds'], y=future_data['yhat'],
            mode='lines', name='AI Dự báo (Trend)',
            line=dict(color='#ff0055', width=2) # Màu Neon Pink rõ ràng
        ))
        
        # 3. Vùng tin cậy (Mây mờ) - Làm mượt
        fig.add_trace(go.Scatter(
            x=pd.concat([future_data['ds'], future_data['ds'][::-1]]),
            y=pd.concat([future_data['yhat_upper'], future_data['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(255, 0, 85, 0.1)', # Hồng nhạt trong suốt
            line=dict(color='rgba(255,255,255,0)'), # Không viền
            hoverinfo="skip",
            name='Biên độ rủi ro'
        ))
        
        # Layout Chuẩn TradingView (Zoom/Pan enabled)
        fig.update_layout(
            title=dict(text=f"🔮 AI PROPHET: DỰ BÁO {periods} NGÀY TỚI", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá dự kiến",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=40, t=50, b=20),
            
            # --- CẤU HÌNH TƯƠNG TÁC ---
            dragmode='pan', # Mặc định là kéo
            xaxis=dict(
                fixedrange=False, # Cho phép Zoom
                showgrid=True, gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                fixedrange=False, # Cho phép Zoom
                showgrid=True, gridcolor='rgba(255,255,255,0.1)', 
                side='right' # Giá bên phải
            )
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
