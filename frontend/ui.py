import streamlit as st
import streamlit.components.v1 as components

def load_hardcore_css():
    """
    Nạp CSS tùy chỉnh: Dark Mode, Font Rajdhani, Glassmorphism
    """
    st.markdown("""
    <style>
        /* 1. IMPORT FONT: Rajdhani (Tech) & Inter (Body) */
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');
        
        /* 2. GLOBAL THEME */
        .stApp {
            background-color: #050505; /* Đen sâu thẳm */
            color: #e5e7eb;
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, .stMetricLabel {
            font-family: 'Rajdhani', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 3. GLASS BOX (Hộp kính mờ) */
        .glass-box {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        /* 4. CUSTOM SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #4b5563; }

        /* 5. INPUTS & SELECTBOX */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: #111827 !important;
            border: 1px solid #374151 !important;
            color: #fff !important;
            border-radius: 6px;
        }

        /* 6. DATAFRAME (Bảng) */
        [data-testid="stDataFrame"] {
            border: 1px solid #374151;
            border-radius: 8px;
            background-color: #111827;
        }
        
        /* 7. METRIC CARD (Chỉ số) */
        [data-testid="stMetricValue"] {
            font-family: 'Rajdhani', sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
        }
        
        /* 8. TABS STYLE */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #111827;
            padding: 5px;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 5px;
            color: #9ca3af;
            font-family: 'Rajdhani';
            font-weight: 700;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0ea5e9 !important; /* Màu xanh Neon */
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_clock_js():
    """Đồng hồ JavaScript chạy mượt mà không cần reload Python"""
    components.html(
        """
        <div style="
            display: flex; flex-direction: column; align-items: flex-end; justify-content: center;
            font-family: 'Rajdhani', sans-serif; background: transparent;
            height: 70px; padding-right: 10px; overflow: hidden;
        ">
            <div id="date" style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; letter-spacing: 2px;">LOADING...</div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></div>
                <div id="clock" style="color: #fff; font-size: 2.2rem; font-weight: 800; line-height: 1;">00:00:00</div>
            </div>
        </div>
        <script>
            function updateTime() {
                const now = new Date();
                const time = now.toLocaleTimeString('en-US', {hour12: false});
                const date = now.toLocaleDateString('en-US', {weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'}).toUpperCase();
                document.getElementById('clock').innerText = time;
                document.getElementById('date').innerText = date;
            }
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        """,
        height=85
    )

def render_header():
    """Header chính của ứng dụng"""
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("""
        <div style="padding-top: 10px;">
            <div style="font-family: 'Rajdhani'; font-weight: 900; font-size: 2.8rem; color: white; letter-spacing: 2px; line-height: 1;">
                THANG LONG <span style="color:#0ea5e9; text-shadow: 0 0 20px rgba(14, 165, 233, 0.5);">TERMINAL</span>
            </div>
            <div style="color: #64748b; font-size: 0.85rem; letter-spacing: 4px; font-weight: 600; margin-left: 2px;">
                ADVANCED AI MARKET INTELLIGENCE V36.1
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        render_clock_js()
