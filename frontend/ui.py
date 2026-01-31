# frontend/ui.py
import streamlit as st
from datetime import datetime

def load_hardcore_css():
    st.markdown("""
    <style>
        /* --- 1. FONTS & GLOBAL THEME --- */
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;600&display=swap');
        
        :root {
            --bg-color: #050505;
            --card-bg: #111827;
            --text-color: #e5e7eb;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --border-color: #374151;
        }

        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
        }

        /* --- 2. FIX LỖI TEXT INPUT & SELECTBOX (QUAN TRỌNG NHẤT) --- */
        /* Nền của ô nhập liệu và dropdown */
        .stSelectbox div[data-baseweb="select"] > div, 
        .stTextInput div[data-baseweb="base-input"] {
            background-color: #1f2937 !important;
            color: white !important;
            border-color: #4b5563 !important;
        }
        /* Màu chữ trong ô chọn */
        .stSelectbox div[data-baseweb="select"] span {
            color: white !important;
        }
        /* Icon mũi tên */
        .stSelectbox svg {
            fill: white !important;
        }
        /* Menu xổ xuống (Dropdown list) */
        ul[data-baseweb="menu"] {
            background-color: #1f2937 !important;
            border: 1px solid #374151 !important;
        }
        li[data-baseweb="option"] {
            color: white !important;
        }
        li[data-baseweb="option"]:hover, li[aria-selected="true"] {
            background-color: #374151 !important;
        }

        /* --- 3. FIX LỖI BUTTON --- */
        button[kind="secondary"] {
            background-color: #1f2937 !important;
            color: white !important;
            border: 1px solid #374151 !important;
        }
        button[kind="secondary"]:hover {
            border-color: var(--accent-cyan) !important;
            color: var(--accent-cyan) !important;
        }
        button[kind="primary"] {
            background: linear-gradient(90deg, #0891b2, #06b6d4) !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }

        /* --- 4. FIX LỖI BẢNG (DATAFRAME) --- */
        [data-testid="stDataFrame"] {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px;
        }
        [data-testid="stDataFrame"] * {
            color: #d1d5db !important; /* Màu chữ xám trắng */
            font-family: 'Inter', sans-serif !important;
        }
        /* Header của bảng */
        [data-testid="stDataFrame"] div[role="columnheader"] {
            background-color: #1f2937 !important;
            color: var(--accent-cyan) !important;
            font-weight: bold;
            text-transform: uppercase;
        }

        /* --- 5. COMPONENT STYLE --- */
        .glass-box {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(55, 65, 81, 0.5);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        }
        
        .header-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            background: -webkit-linear-gradient(0deg, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }

        .status-dot {
            height: 12px; width: 12px; 
            background-color: var(--accent-green); 
            border-radius: 50%; 
            display: inline-block;
            box-shadow: 0 0 10px var(--accent-green);
            margin-right: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #374151; margin-bottom: 30px;">
        <div>
            <div class="header-title">THANG LONG <span style="color: #06b6d4; -webkit-text-fill-color: #06b6d4;">TERMINAL V3</span></div>
            <div style="color: #9ca3af; font-family: 'Rajdhani'; font-size: 1.1rem; margin-top: 5px;">
                ADVANCED MARKET INTELLIGENCE SYSTEM
            </div>
        </div>
        <div style="text-align: right;">
            <div style="background: #1f2937; padding: 8px 16px; border-radius: 20px; border: 1px solid #374151;">
                <span class="status-dot"></span> 
                <span style="color: #e5e7eb; font-weight: 600; font-family: 'Rajdhani'; letter-spacing: 1px;">LIVE DATA: {now}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
