"""
================================================================================
MODULE: backend/ai.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.4.1-AI-CROSSHAIR
DESCRIPTION: 
    Artificial Intelligence Engine.
    UPDATED: Added NEON CROSSHAIR (Spikelines) to the Prophet Forecast Chart.
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
    def __init__(self, df: pd.DataFrame, days: int = 30, simulations: int = 1000):
        self.df = df
        self.days = days
        self.simulations = simulations
        
    def run(self) -> Tuple[Optional[go.Figure], Optional[go.Figure], Dict]:
        if self.df.empty or len(self.df) < 30:
            return None, None, {}
            
        data = self.df['Close']
        returns = data.pct_change().dropna()
        mu = returns.mean() 
        sigma = returns.std() 
        last_price = data.iloc[-1]
        
        drift = mu - 0.5 * sigma**2
        Z = np.random.normal(0, 1, (self.days, self.simulations))
        daily_returns = np.exp(drift + sigma * Z)
        
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = last_price
        
        for t in range(1, self.days):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
            
        simulation_df = pd.DataFrame(price_paths)
        
        # Visualization
        dates = [datetime.now() + timedelta(days=i) for i in range(self.days)]
        fig = go.Figure()
        
        # 1. Hạt giá lịch sử
        recent_history = self.df.tail(30)
        fig.add_trace(go.Scatter(
            x=recent_history.index, y=recent_history['Close'],
            mode='markers+lines', 
            name='Lịch sử (30D)',
            line=dict(color='#00f3ff', width=2),
            marker=dict(color='#00f3ff', size=5, symbol='circle'),
            showlegend=False
        ))

        # 2. Các đường mô phỏng
        display_sims = min(50, self.simulations)
        for i in range(display_sims):
            fig.add_trace(go.Scatter(
                x=dates, y=simulation_df.iloc[:, i],
                mode='lines', line=dict(width=1, color='#64748b'), opacity=0.15,
                showlegend=False, hoverinfo='skip'
            ))
            
        # 3. Đường trung bình
        fig.add_trace(go.Scatter(
            x=dates, y=simulation_df.mean(axis=1),
            mode='lines', line=dict(color='#ff0055', width=4),
            name='Kỳ vọng (Mean)'
        ))
        
        # Layout Monte Carlo (Cũng thêm Crosshair luôn cho đồng bộ)
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
            
            # Crosshair Monte Carlo
            xaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)',
                showspikes=True, spikemode='across', spikesnap='cursor', 
                spikecolor='#00f3ff', spikethickness=1
            ),
            yaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right',
                showspikes=True, spikemode='across', spikesnap='cursor',
                spikecolor='#ff0055', spikethickness=1
            )
        )
        
        final_prices = simulation_df.iloc[-1]
        stats = {
            "mean": final_prices.mean(),
            "top_5": np.percentile(final_prices, 95),
            "bot_5": np.percentile(final_prices, 5),
            "prob_up": (final_prices > last_price).mean() * 100
        }
        
        fig_hist = px.histogram(final_prices, nbins=50, title="📊 PHÂN PHỐI XÁC SUẤT", color_discrete_sequence=['#00f3ff'])
        fig_hist.add_vline(x=last_price, line_dash="dash", line_color="#ff0055", annotation_text="Hiện tại")
        fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        
        return fig, fig_hist, stats

# ==============================================================================
# 2. PROPHET FORECASTING ENGINE
# ==============================================================================

class ProphetPredictor:
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
        
        # Model Config (Tắt Daily Seasonality để mượt)
        m = Prophet(
            daily_seasonality=False, 
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_mode='additive'
        )
        
        m.fit(df_p)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        # --- VẼ BIỂU ĐỒ ---
        fig = go.Figure()
        
        # 1. BIÊN ĐỘ RỦI RO (CLOUD)
        future_data = forecast[forecast['ds'] > df_p['ds'].iloc[-1]]
        fig.add_trace(go.Scatter(
            x=pd.concat([future_data['ds'], future_data['ds'][::-1]]),
            y=pd.concat([future_data['yhat_upper'], future_data['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(255, 0, 85, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Vùng Rủi Ro'
        ))

        # 2. LỊCH SỬ: ĐƯỜNG TREND (DƯỚI)
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='lines', 
            name='Trend Lịch Sử',
            line=dict(color='#0099aa', width=2),
            opacity=0.8
        ))
        
        # 3. LỊCH SỬ: HẠT DỮ LIỆU (TRÊN)
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='markers', 
            name='Dữ Liệu Thô',
            marker=dict(
                color='#00f3ff', # Cyan phát sáng
                size=4,
                line=dict(width=0)
            ),
            opacity=1.0
        ))
        
        # 4. DỰ BÁO TƯƠNG LAI (LINE ĐẬM)
        fig.add_trace(go.Scatter(
            x=future_data['ds'], y=future_data['yhat'],
            mode='lines', 
            name='AI DỰ BÁO',
            line=dict(color='#ff0055', width=4) # Neon Pink siêu đậm
        ))
        
        # --- CẤU HÌNH CROSSHAIR (ĐƯỜNG CHỈ CỘNG) Ở ĐÂY ---
        fig.update_layout(
            title=dict(text=f"🔮 AI PROPHET: DỰ BÁO {periods} NGÀY TỚI", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá dự kiến",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=40, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
            # Interactive Config
            dragmode='pan',
            
            # TRỤC X: Đường chỉ dọc màu Cyan (#00f3ff)
            xaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)',
                showspikes=True,        # Bật đường chỉ
                spikemode='across',     # Chạy hết biểu đồ
                spikesnap='cursor',     # Dính theo chuột
                showline=False,
                spikedash='solid',      # Nét liền
                spikecolor='#00f3ff',   # Màu Neon Cyan
                spikethickness=1
            ),
            
            # TRỤC Y: Đường chỉ ngang màu Pink (#ff0055)
            yaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)', 
                side='right',
                showspikes=True,        # Bật đường chỉ
                spikemode='across',
                spikesnap='cursor',
                showline=False,
                spikedash='dot',        # Nét đứt (cho khác trục X)
                spikecolor='#ff0055',   # Màu Neon Pink
                spikethickness=1
            )
        )
        
        return fig

# ==============================================================================
# WRAPPERS
# ==============================================================================
def run_monte_carlo(df: pd.DataFrame) -> Tuple:
    return MonteCarloSimulator(df).run()

def run_prophet_ai(df: pd.DataFrame) -> Optional[go.Figure]:
    return ProphetPredictor(df).predict()
