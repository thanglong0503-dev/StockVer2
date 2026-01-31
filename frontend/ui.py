# frontend/ui.py
import streamlit as st
from datetime import datetime

def load_hardcore_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;600&display=swap');
        
        /* --- GLOBAL FIX --- */
        .stApp { background-color: #050505; }
        
        /* --- 1. FIX SELECTBOX & INPUT (KHU VỰC KHOANH ĐỎ) --- */
        /* Nền Input */
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextInput div[data-baseweb="base-input"],
        .stNumberInput div[data-baseweb="base-input"] {
            background-color: #1f2937 !important;
            border: 1px solid #4b5563 !important;
            color: #ffffff !important;
            border-radius: 8px;
        }
        /* Chữ bên trong Input */
        input[type="text"], input[type="number"] {
            color: #ffffff !important;
            font-weight: 600;
        }
        /* Dropdown Menu */
        ul[data-baseweb="menu"] {
            background-color: #111827 !important;
            border: 1px solid #06b6d4 !important;
        }
        li[data-baseweb="option"] {
            color: #e5e7eb !important;
        }
        
        /* --- 2. FIX BUTTONS (NÚT BẤM) --- */
        /* Nút chính (Primary) - Màu xanh Neon */
        button[kind="primary"] {
            background: linear-gradient(90deg, #06b6d4, #3b82f6) !important;
            border: none !important;
            color: white !important;
            font-family: 'Rajdhani', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
            transition: all 0.3s ease;
        }
        button[kind="primary"]:hover {
            box-shadow: 0 0 25px rgba(6, 182, 212, 0.7);
            transform: scale(1.02);
        }
        
        /* Nút phụ (Secondary) - Viền kính */
        button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid #4b5563 !important;
            color: #9ca3af !important;
            font-family: 'Rajdhani', sans-serif !important;
        }
        button[kind="secondary"]:hover {
            border-color: #06b6d4 !important;
            color: #06b6d4 !important;
        }

        /* --- 3. FIX DATAFRAME (BẢNG GIÁ) --- */
        [data-testid="stDataFrame"] {
            background-color: #111827 !important;
            border: 1px solid #374151;
            border-radius: 10px;
        }
        
        /* --- 4. COMPONENT: GLASS BOX --- */
        .glass-box {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        }
        
        .header-glow {
            font-family: 'Rajdhani', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            color: white;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.6);
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 30px 0;">
        <div>
            <div class="header-glow">THANG LONG <span style="color:#06b6d4">TERMINAL</span></div>
            <div style="color: #94a3b8; font-size: 0.9rem; letter-spacing: 2px;">ADVANCED AI TRADING SYSTEM</div>
        </div>
        <div style="text-align: right; background: #1f2937; padding: 8px 15px; border-radius: 20px; border: 1px solid #374151;">
            <span style="color:#10b981">●</span> LIVE: <span style="font-family:'Rajdhani'; font-weight:700; color:white;">{now}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
