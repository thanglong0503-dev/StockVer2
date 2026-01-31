# frontend/app.py
import streamlit as st
import requests
from ui_components import load_css, card_metric
import streamlit.components.v1 as components

# Cấu hình
st.set_page_config(layout="wide", page_title="Stock V2 Split", page_icon="⚡")
load_css() # Load giao diện đẹp

# Sidebar
st.sidebar.title("⚡ STOCK V2")
symbol = st.sidebar.text_input("Nhập mã CP:", "HPG").upper()
btn_analyze = st.sidebar.button("🚀 Phân Tích")

# URL của Backend (Mặc định chạy localhost port 8000)
BACKEND_URL = "http://127.0.0.1:8000"

if btn_analyze:
    with st.spinner(f"Đang gọi Server phân tích {symbol}..."):
        try:
            # GỌI API SANG BACKEND
            response = requests.get(f"{BACKEND_URL}/api/analyze/{symbol}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    st.error(data["error"])
                else:
                    # HIỂN THỊ KẾT QUẢ
                    st.title(f"Kết quả phân tích: {symbol}")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: card_metric("Điểm số", f"{data['score']}/10", "#22d3ee")
                    with c2: card_metric("Hành động", data['action'], data['color']) # Màu từ backend trả về
                    with c3: card_metric("Giá hiện tại", f"{data['price']:,.0f}")
                    with c4: card_metric("Mục tiêu", f"{data['take_profit']:,.0f}", "#10b981")

                    # Chi tiết & Biểu đồ
                    col_left, col_right = st.columns([1, 2])
                    
                    with col_left:
                        st.markdown('<div class="glass-card"><h3>📝 Lý do</h3>', unsafe_allow_html=True)
                        for r in data['reasons']:
                            st.write(r)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with col_right:
                        # Nhúng TradingView
                        components.html(f"""
                        <div class="tradingview-widget-container">
                          <div id="tv_chart"></div>
                          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                          <script type="text/javascript">
                          new TradingView.widget({{
                              "width": "100%", "height": 400, "symbol": "HOSE:{symbol}",
                              "interval": "D", "timezone": "Asia/Ho_Chi_Minh", "theme": "dark",
                              "container_id": "tv_chart"
                          }});
                          </script>
                        </div>
                        """, height=400)

            else:
                st.error("Không kết nối được với Backend!")
                
        except Exception as e:
            st.error(f"Lỗi kết nối: {e}")
            st.info("💡 Bạn đã chạy lệnh 'uvicorn main:app' ở folder backend chưa?")
else:
    st.info("👈 Nhập mã và bấm nút để gọi Server Backend xử lý.")
