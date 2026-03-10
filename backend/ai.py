"""
================================================================================
MODULE: backend/ai.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.8.0-BLUE-RIVER-FIX
DESCRIPTION: 
    - Artificial Intelligence Engine.
    - Features: Monte Carlo Simulation & Prophet Forecasting.
    - Style: Blue River (Smooth Line + Tiny Dots) on Dark Mode.
================================================================================
"""
import zlib
import base64
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import io # THÊM VÀO ĐỂ XỬ LÝ NÉN JSON MƯỢT MÀ

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
            
        # 3. Đường trung bình (Đổi sang màu xanh cho đồng bộ nếu muốn, hoặc giữ đỏ)
        fig.add_trace(go.Scatter(
            x=dates, y=simulation_df.mean(axis=1),
            mode='lines', line=dict(color='#ff0055', width=2),
            name='Kỳ vọng (Mean)'
        ))
        
        # Layout Monte Carlo
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
        
    # [ĐÃ UPDATE]: Trả về 2 món - Bức tranh (Figure) và Bản vẽ Kỹ thuật (DataFrame)
    def predict(self, periods: int = 60) -> Tuple[Optional[go.Figure], Optional[pd.DataFrame]]:
        try:
            from prophet import Prophet
        except ImportError: return None, None
            
        if self.df.empty or len(self.df) < 60: return None, None
        
        # Prepare Data
        df_p = self.df.reset_index()[['Date', 'Close']].copy()
        df_p.columns = ['ds', 'y']
        df_p['ds'] = df_p['ds'].dt.tz_localize(None)
        
        # Model Config
        m = Prophet(
            daily_seasonality=True, 
            weekly_seasonality=False,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_mode='additive'
        )
        
        m.fit(df_p)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        # --- VẼ BIỂU ĐỒ (STYLE: BLUE RIVER) ---
        fig = go.Figure()
        
        # 1. VÙNG RỦI RO (CLOUD) - Vẽ toàn bộ
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
            y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 180, 216, 0.2)', # Xanh dương nhạt mờ ảo
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Biên độ dao động'
        ))

        # 2. ĐƯỜNG CHỈ XUYÊN SUỐT (AI TREND LINE - YHAT)
        # Vẽ một đường mượt mà từ quá khứ đến tương lai
        fig.add_trace(go.Scatter(
            x=forecast['ds'], y=forecast['yhat'],
            mode='lines', 
            name='AI Trend Line',
            # Màu xanh dương đậm, nét liền mạch, xuyên suốt
            line=dict(color='#0077b6', width=2.5) 
        ))
        
        # 3. HẠT BỤI DỮ LIỆU (REAL DATA DOTS)
        # Dữ liệu thực tế dạng chấm
        fig.add_trace(go.Scatter(
            x=df_p['ds'], y=df_p['y'],
            mode='markers', 
            name='Giá thực tế',
            marker=dict(
                color='#48cae4', # Cyan sáng
                size=3,          # Chấm nhỏ li ti
                line=dict(width=0.5, color='white') # Viền trắng mỏng
            ),
            opacity=0.9
        ))
        
        # --- CẤU HÌNH GIAO DIỆN ---
        fig.update_layout(
            title=dict(text=f"🔮 AI PROPHET: DỰ BÁO {periods} NGÀY TỚI", font=dict(family="Rajdhani", size=18)),
            yaxis_title="Giá",
            template="plotly_dark",
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=40, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
            dragmode='pan',
            
            # Crosshair (Đường chỉ chữ thập)
            xaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)',
                showspikes=True, spikemode='across', spikesnap='cursor',
                showline=False, spikedash='solid', spikecolor='#00f3ff', spikethickness=1
            ),
            yaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right',
                showspikes=True, spikemode='across', spikesnap='cursor',
                showline=False, spikedash='dot', spikecolor='#00f3ff', spikethickness=1
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # [ĐÃ UPDATE]: Nhả cả hình ảnh và bộ số liệu để nén JSON
        return fig, forecast

# ==============================================================================
# WRAPPERS VÀ HÀM TÁI TẠO ĐỒ THỊ SIÊU TỐC TỪ ĐÁM MÂY
# ==============================================================================
def run_monte_carlo(df: pd.DataFrame) -> Tuple:
    return MonteCarloSimulator(df).run()

def run_prophet_ai(df: pd.DataFrame, periods: int = 60) -> Tuple[Optional[go.Figure], Optional[pd.DataFrame]]:
    # Truyền tham số periods vào bên trong
    return ProphetPredictor(df).predict(periods=periods)

def rebuild_prophet_chart_from_json(json_data: str, symbol: str) -> go.Figure:
    """Giải nén cục data Base64 từ Mây và vẽ lại đồ thị trong 0.1 giây"""
    # GIẢI NÉN DỮ LIỆU
    try:
        # Giải mã Base64 và bung nén Zlib
        decompressed_str = zlib.decompress(base64.b64decode(json_data)).decode('utf-8')
    except Exception:
        # Đề phòng ngài đang lưu cục JSON cũ chưa nén, hệ thống tự động fallback
        decompressed_str = json_data
        
    # Đọc lại thành DataFrame
    df_forecast = pd.read_json(io.StringIO(decompressed_str), orient='records')
    
    fig = go.Figure()
    
    # 1. Vẽ lại VÙNG RỦI RO (CLOUD)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_forecast['ds'], df_forecast['ds'][::-1]]),
        y=pd.concat([df_forecast['yhat_upper'], df_forecast['yhat_lower'][::-1]]),
        fill='toself', fillcolor='rgba(0, 180, 216, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", name='Biên độ dao động'
    ))

    # 2. Vẽ lại ĐƯỜNG CHỈ XUYÊN SUỐT (AI TREND LINE)
    fig.add_trace(go.Scatter(
        x=df_forecast['ds'], y=df_forecast['yhat'],
        mode='lines', name='AI Trend Line',
        line=dict(color='#0077b6', width=2.5) 
    ))
    
    # Ép lại form dáng chuẩn Blue River
    fig.update_layout(
        title=dict(text=f"📂 THƯ VIỆN ĐÁM MÂY: DỰ BÁO {symbol}", font=dict(family="Rajdhani", size=18)),
        yaxis_title="Giá", template="plotly_dark", height=500, hovermode="x unified",
        margin=dict(l=20, r=40, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        dragmode='pan',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right')
    )
    
    return fig
