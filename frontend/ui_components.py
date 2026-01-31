# frontend/ui_components.py
import streamlit as st

def load_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0f172a; color: white; }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px; padding: 20px; margin-bottom: 15px;
        }
        .big-text { font-size: 2rem; font-weight: bold; }
        .label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def card_metric(label, value, color="white"):
    st.markdown(f"""
    <div class="glass-card">
        <div class="label">{label}</div>
        <div class="big-text" style="color: {color}">{value}</div>
    </div>
    """, unsafe_allow_html=True)
