import streamlit as st
import plotly.graph_objects as go
from prophet.plot import plot_plotly
import streamlit.components.v1 as components

def load_css():
    st.markdown("""
    <style>
        .stApp {background-color: #0f172a; color: white;}
        .glass {background: rgba(30,41,59,0.7); border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155;}
        h1, h2, h3 {color: #f8fafc !important;}
    </style>
    """, unsafe_allow_html=True)

def render_kpi_cards(data):
    st.markdown(f"""
    <div class="glass" style="border-left: 5px solid {data['color']}">
        <h3>{data['action']} ({data['score']}/10)</h3>
        <h1 style="color:{data['color']}">{data['price']:,.0f} VND</h1>
    </div>
    """, unsafe_allow_html=True)

def render_chart_tradingview(symbol):
    # Hàm nhúng TradingView
    components.html(f"""
    <div class="tradingview-widget-container">
      <div id="tv_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
          "width": "100%", "height": 500, "symbol": "HOSE:{symbol}",
          "interval": "D", "timezone": "Asia/Ho_Chi_Minh", "theme": "dark",
          "style": "1", "container_id": "tv_chart"
      }});
      </script>
    </div>
    """, height=500)

def plot_monte_carlo(sim_df):
    if sim_df is None: return
    fig = go.Figure()
    # Vẽ 50 đường
    for i in range(min(50, sim_df.shape[1])):
        fig.add_trace(go.Scatter(y=sim_df.iloc[:, i], mode='lines', opacity=0.1, showlegend=False))
    fig.update_layout(title="Monte Carlo Simulation", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
