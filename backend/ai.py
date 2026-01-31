# backend/ai.py
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
import streamlit as st

@st.cache_data(ttl=3600) # Cache 1 tiếng để đỡ load lại model
def run_prophet_engine(df, days=30):
    if df.empty: return None
    
    # Format data cho Prophet
    df_p = df.reset_index()[['Date', 'Close']]
    df_p.columns = ['ds', 'y']
    df_p['ds'] = df_p['ds'].dt.tz_localize(None)
    
    # Train Model
    m = Prophet(daily_seasonality=True, yearly_seasonality=True)
    m.fit(df_p)
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    
    return forecast

def run_monte_carlo_engine(df, days=30, sims=50): # Giảm sims xuống 50 cho nhẹ
    data = df['Close']
    returns = data.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last_price = data.iloc[-1]
    
    simulation_df = pd.DataFrame()
    
    for x in range(sims):
        price_list = [last_price]
        for _ in range(days):
            price_list.append(price_list[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal()))
        simulation_df[f"Sim {x}"] = price_list
        
    return simulation_df
