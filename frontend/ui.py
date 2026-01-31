"""
================================================================================
MODULE: frontend/ui.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.1.0-STABLE
DESCRIPTION: 
    User Interface Styling Engine.
    Injects professional CSS for a Bloomberg-like terminal experience.
    Features: Inter Font, Flat Design, Dark Mode Optimization.
================================================================================
"""

import streamlit as st
import streamlit.components.v1 as components

def load_hardcore_css():
    """
    Nạp CSS tùy chỉnh để biến đổi giao diện.
    Phong cách: Professional Fintech (Dark Theme).
    """
    st.markdown("""
    <style>
        /* 1. TYPOGRAPHY: INTER FONT (Chuẩn Quốc Tế) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* 2. GLOBAL THEME COLORS */
        :root {
            --bg-color: #0d1117;       /* Nền đen sâu */
            --card-bg: #161b22;        /* Nền card */
            --border-color: #30363d;   /* Viền xám tinh tế */
            --text-primary: #e6edf3;   /* Chữ trắng sáng */
            --text-secondary: #8b949e; /* Chữ xám mờ */
            --accent-blue: #2f81f7;    /* Xanh điểm nhấn */
            --success-green: #238636;  /* Xanh tăng giá */
            --danger-red: #da3633;     /* Đỏ giảm giá */
        }

        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
        }

        /* 3. HEADERS & TITLES */
        h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2 {
            color: var(--text-primary);
            font-weight: 700;
            letter-spacing: -0.5px;
            text-transform: none; /* Bỏ viết hoa toàn bộ cho đỡ gắt */
        }
        
        /* 4. PROFESSIONAL CARDS (Khung chứa dữ liệu) */
        .pro-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }

        /* 5. DATAFRAME (Bảng dữ liệu) */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            background-color: var(--bg-color);
            font-size: 13px;
        }
        
        /* 6. TABS (Thẻ chuyển tab) - Thiết kế phẳng */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: transparent;
            padding: 0 10px;
            border-bottom: 1px solid var(--border-color);
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: transparent;
            border: none;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 14px;
        }
        .stTabs [aria-selected="true"] {
            color: var(--accent-blue) !important;
            border-bottom: 2px solid var(--accent-blue) !important;
            font-weight: 600;
        }

        /* 7. INPUT FIELDS (Ô nhập liệu) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #0d1117 !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
            border-radius: 4px;
            font-size: 14px;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: none !important;
        }

        /* 8. BUTTONS (Nút bấm) */
        button[kind="primary"] {
            background-color: var(--accent-blue) !important;
            border: none;
            color: white !important;
            font-weight: 600;
            border-radius: 4px;
            transition: opacity 0.2s;
        }
        button[kind="primary"]:hover {
            opacity: 0.9;
        }
        
        /* 9. METRICS (Chỉ số) */
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 13px !important;
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
        }
        
        /* 10. SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #010409;
            border-right: 1px solid var(--border-color);
        }
    </style>
    """, unsafe_allow_html=True)

def render_clock_js():
    """
    Đồng hồ hiển thị thời gian thực (Server Time).
    Thiết kế: Số mỏng, màu xám trắng, chuẩn Enterprise.
    """
    components.html(
        """
        <div style="
            display: flex; 
            flex-direction: column; 
            align-items: flex-end; 
            justify-content: center;
            font-family: 'Inter', sans-serif; 
            padding-right: 5px;
            height: 100%;
        ">
            <div id="date" style="
                color: #8b949e; 
                font-size: 12px; 
                font-weight: 500; 
                text-transform: uppercase;
                margin-bottom: 2px;
            ">Loading...</div>
            <div id="clock" style="
                color: #e6edf3; 
                font-size: 20px; 
                font-weight: 600; 
                font-variant-numeric: tabular-nums;
                letter-spacing: 0.5px;
            ">00:00:00</div>
        </div>
        <script>
            function updateTime() {
                const now = new Date();
                const optionsDate = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
                // Định dạng giờ 24h chuẩn ISO
                document.getElementById('clock').innerText = now.toLocaleTimeString('en-GB', { hour12: false });
                document.getElementById('date').innerText = now.toLocaleDateString('en-US', optionsDate).toUpperCase();
            }
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        """,
        height=60
    )

def render_header():
    """Header ứng dụng tối giản, không icon thừa."""
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("""
        <div style="padding: 10px 0;">
            <div style="
                font-weight: 700; 
                font-size: 24px; 
                color: #e6edf3; 
                letter-spacing: -0.5px;
            ">
                THANG LONG <span style="color: #2f81f7; font-weight: 400;">TERMINAL</span>
            </div>
            <div style="
                color: #8b949e; 
                font-size: 12px; 
                font-weight: 400; 
                margin-top: 2px;
            ">
                Financial Market Intelligence System
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        render_clock_js()
