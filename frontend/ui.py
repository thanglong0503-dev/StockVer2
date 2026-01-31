# frontend/ui.py
import streamlit as st
from datetime import datetime

def load_custom_css():
    st.markdown("""
    <style>
        /* 1. IMPORT FONT 'Rajdhani' (Font kỹ thuật số cực ngầu) */
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        /* 2. FORCE DARK MODE & GLOBAL THEME */
        .stApp {
            background-color: #050505; /* Đen sâu thẳm */
            background-image: radial-gradient(circle at 50% 0%, #111827 0%, #050505 70%);
            font-family: 'Inter', sans-serif;
            color: #e5e7eb;
        }
        
        /* 3. HEADER ẨN MẶC ĐỊNH */
        header[data-testid="stHeader"] {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 3rem;}

        /* 4. CUSTOM COMPONENTS - "THANG LONG IDENTITY" */
        
        /* Box hiệu ứng kính (Glassmorphism) */
        .glass-box {
            background: rgba(20, 20, 30, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }

        /* Top Bar */
        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px;
            background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
            border-bottom: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .logo { 
            font-family: 'Rajdhani', sans-serif; 
            font-size: 1.8rem; font-weight: 800; 
            color: #fff; text-transform: uppercase; letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }
        .logo span { color: #38bdf8; } /* Màu xanh Neon đặc trưng */

        /* Metric Value Styles */
        .metric-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
        .metric-val { font-family: 'Rajdhani', sans-serif; font-size: 2rem; font-weight: 700; color: #f8fafc; }
        .up { color: #22c55e; text-shadow: 0 0 10px rgba(34, 197, 94, 0.3); } /* Xanh lá phát sáng */
        .down { color: #ef4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3); } /* Đỏ phát sáng */
        
        /* 5. FIX TABLE & SPARKLINE */
        [data-testid="stDataFrame"] { border: none !important; }
        [data-testid="stDataFrame"] div[role="row"] {
            background-color: transparent !important;
            border-bottom: 1px solid #1e293b;
        }
        [data-testid="stDataFrame"] div[role="row"]:hover {
            background-color: #1e293b !important;
        }
        /* Chỉnh màu tiêu đề bảng */
        [data-testid="stDataFrame"] div[role="columnheader"] {
            color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="top-bar">
        <div class="logo">THANG LONG <span>TERMINAL</span></div>
        <div style="font-family: 'Rajdhani'; font-size: 1.2rem; color: #94a3b8;">
            LIVE MARKET DATA <span style="color:#22c55e; margin: 0 10px;">●</span> {now}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label, value, change, is_up):
    color_class = "up" if is_up else "down"
    arrow = "▲" if is_up else "▼"
    st.markdown(f"""
    <div class="glass-box" style="padding: 15px; border-top: 3px solid {'#22c55e' if is_up else '#ef4444'}">
        <div class="metric-label">{label}</div>
        <div class="metric-val">{value}</div>
        <div class="{color_class}" style="font-weight: 600; font-size: 1rem;">
            {arrow} {change}
        </div>
    </div>
    """, unsafe_allow_html=True)
