# frontend/ui.py
import streamlit as st
from datetime import datetime

def load_dnse_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif; background-color: #0b0e11; color: #e2e8f0;
        }
        header {visibility: hidden;}
        /* Top Navigation */
        .nav-container {
            display: flex; justify-content: space-between; align-items: center;
            background: #161b22; padding: 12px 20px; border-radius: 8px;
            border-bottom: 1px solid #2d3748; margin-bottom: 20px;
        }
        .brand { font-size: 1.2rem; font-weight: 800; color: white; }
        .brand span { color: #ef4444; }
        
        /* Tab Style */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [aria-selected="true"] { color: #ef4444 !important; border-bottom: 2px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown(f"""
    <div class="nav-container">
        <div class="brand">DNSE <span>AI</span></div>
        <div style="color: #94a3b8;">VN-INDEX Market Watch</div>
        <div style="color: white; font-weight: 600;">{datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_detail(stock_info):
    # Vẽ cái hộp chi tiết bên phải
    color = "#22c55e" if stock_info['%'] >= 0 else "#ef4444"
    st.markdown(f"""
    <div style="background: #161b22; border: 1px solid #2d3748; padding: 15px; border-radius: 8px; border-left: 4px solid {color};">
        <h2 style="margin:0; color:white;">{stock_info['Mã']}</h2>
        <div style="font-size: 1.8rem; font-weight: 800; color: {color}">{stock_info['Giá']:.2f}</div>
        <div style="color: {color}">{'▲' if stock_info['%'] >=0 else '▼'} {stock_info['%']:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
