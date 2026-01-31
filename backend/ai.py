"""
================================================================================
MODULE: backend/ai.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.3.2-PARTICLE-FX
DESCRIPTION: 
    Artificial Intelligence & Statistical Modeling Engine.
    UPDATED: Added Scatter Dots (Particles) to visualize raw data points.
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
        
        # 3. Visualization - Line Chart
        dates = [datetime.now() + timedelta(days=i) for i in range(self.days)]
        fig = go.Figure()
        
        # [NEW] Thêm các hạt giá lịch sử (30 ngày gần nhất) để tạo đà
        recent_history = self.df.tail(30)
        fig.add_trace(go.Scatter(
            x=recent_history.index, y=recent_history['Close'],
            mode='markers+lines', # Vừa đường vừa hạt
            name='Lịch sử gần đây',
            line=dict(color='#00f3ff', width=1),
            marker=dict(color='#00f3ff', size=4, opacity=0.8), # Hạt Cyan
            showlegend=False
        ))

        # Vẽ 50 đường mô phỏng mờ
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
            mode='lines', line=dict(color='#ff0055', width=3),
            name='Kỳ vọng (Mean)'
        ))
        
        # Layout
        fig.update_layout(
            title=dict(text=f"🌌 MONTE CARLO: {self.simulations} KỊCH BẢN", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=40, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            dragmode='pan',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right')
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
        fig_hist = px.histogram(final_prices, nbins=50, title="📊 PHÂN PHỐI XÁC SUẤT", color_discrete_sequence=['#00f3ff'])
        fig_hist.add_vline(x=last_price, line_dash="dash", line_color="#ff0055", annotation_text="Hiện tại")
        fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        
        return fig, fig_hist, stats

# ==============================================================================
# 2. PROPHET FORECASTING ENGINE
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
        
        # Model
        m = Prophet(
            daily_seasonality=False, # Tắt nhiễu
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_mode='additive'
        )
        
        m.fit(df_p)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        # Plotting Custom
        fig = go.Figure()
        
        # --- 1. DỮ LIỆU THỰC TẾ (HẠT/DOTS) ---
        # Đây là phần "Lão đại" yêu cầu: Các hạt chấm chấm thể hiện giá chạy
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='markers', # Chỉ vẽ hạt, không vẽ đường nối
            name='Dữ liệu thực',
            marker=dict(
                color='#00f3ff', # Màu Cyan Cyberpunk
                size=3,          # Kích thước hạt nhỏ vừa phải
                opacity=0.6      # Hơi trong suốt để nhìn mượt
            )
        ))
        
        # --- 2. ĐƯỜNG XU HƯỚNG LỊCH SỬ (LINE) ---
        # Vẽ thêm đường mờ bên dưới để thấy flow
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='lines', name='Trend Lịch sử',
            line=dict(color='#00f3ff', width=1),
            opacity=0.3,
            showlegend=False
        ))
        
        # --- 3. DỰ BÁO TƯƠNG LAI (LINE) ---
        future_data = forecast[forecast['ds'] > df_p['ds'].iloc[-1]]
        
        fig.add_trace(go.Scatter(
            x=future_data['ds'], y=future_data['yhat'],
            mode='lines', name='AI Dự báo',
            line=dict(color='#ff0055', width=3) # Màu Hồng Neon nổi bật
        ))
        
        # --- 4. BIÊN ĐỘ TIN CẬY (CLOUD) ---
        fig.add_trace(go.Scatter(
            x=pd.concat([future_data['ds'], future_data['ds'][::-1]]),
            y=pd.concat([future_data['yhat_upper'], future_data['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(255, 0, 85, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Vùng rủi ro'
        ))
        
        # Layout
        fig.update_layout(
            title=dict(text=f"🔮 AI PROPHET: DỰ BÁO {periods} NGÀY TỚI", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá dự kiến",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=40, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
            # Zoom/Pan Config
            dragmode='pan',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right')
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
