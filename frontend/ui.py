import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def load_hardcore_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;600&display=swap');
        
        .stApp { background-color: #050505; color: #e5e7eb; font-family: 'Inter', sans-serif; }
        
        /* FIX INPUTS & TABLES */
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextInput div[data-baseweb="base-input"] {
            background-color: #111827 !important;
            border: 1px solid #374151 !important;
            color: #ffffff !important;
        }
        [data-testid="stDataFrame"] { background-color: #111827 !important; border-radius: 10px; }
        
        /* GLASS BOX */
        .glass-box {
            background: rgba(17, 24, 39, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_realtime_clock():
    """Đồng hồ JavaScript chạy real-time không cần reload Python"""
    components.html(
        """
        <div style="
            display: flex; justify-content: flex-end; align-items: center;
            font-family: 'Rajdhani', sans-serif; color: #e5e7eb;
            background-color: #050505; padding: 10px;
        ">
            <div style="text-align: right;">
                <div id="date" style="font-size: 0.9rem; color: #94a3b8; letter-spacing: 1px;">LOADING DATE...</div>
                <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px;">
                    <div style="width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981;"></div>
                    <div id="clock" style="font-size: 2.2rem; font-weight: 700; color: white; line-height: 1;">00:00:00</div>
                </div>
            </div>
        </div>

        <script>
            function updateClock() {
                const now = new Date();
                // Format Time: HH:MM:SS
                const timeString = now.toLocaleTimeString('en-US', { hour12: false });
                // Format Date: Mon, Jan 01 2026
                const dateOptions = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
                const dateString = now.toLocaleDateString('en-US', dateOptions).toUpperCase();

                document.getElementById('clock').innerHTML = timeString;
                document.getElementById('date').innerHTML = dateString;
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        """,
        height=80, # Chiều cao vừa đủ cho đồng hồ
    )

def render_header():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("""
        <div style="padding-top: 10px;">
            <div style="font-family: 'Rajdhani'; font-weight: 800; font-size: 2.5rem; color: white; letter-spacing: 2px;">
                THANG LONG <span style="color:#06b6d4">TERMINAL</span>
            </div>
            <div style="color: #94a3b8; font-size: 0.8rem; letter-spacing: 3px; text-transform: uppercase;">
                Advanced AI Market Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        render_realtime_clock()
