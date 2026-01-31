import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def run_monte_carlo_sim(df, days=30, simulations=100):
    """Mô phỏng Monte Carlo: Dự báo 100 kịch bản tương lai"""
    if df.empty: return None
    
    # Lấy giá đóng cửa
    data = df['Close']
    returns = data.pct_change().dropna()
    
    # Tính tham số
    mu = returns.mean()
    sigma = returns.std()
    last_price = data.iloc[-1]
    
    # Chạy mô phỏng
    simulation_df = pd.DataFrame()
    
    for x in range(simulations):
        price_list = [last_price]
        for _ in range(days):
            # Công thức chuyển động Brown hình học
            price = price_list[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal())
            price_list.append(price)
        simulation_df[f"Sim {x}"] = price_list
        
    return simulation_df
