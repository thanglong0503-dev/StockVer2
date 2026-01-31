# backend/data.py
import yfinance as yf
import pandas as pd

# Giữ nguyên các hàm cũ nếu muốn...

# --- THÊM HÀM MỚI NÀY ---
def get_batch_data(tickers):
    """Lấy dữ liệu nhiều mã cùng lúc để vẽ bảng giá"""
    symbols = [f"{t}.VN" for t in tickers]
    try:
        # Lấy data 1 tháng để vẽ biểu đồ nhỏ (sparkline)
        data = yf.download(symbols, period="1mo", interval="1d", group_by='ticker', progress=False)
        
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                # Xử lý format mới của yfinance
                df_one = data[sym] if len(tickers) > 1 else data
                closes = df_one['Close'].dropna()
                
                if len(closes) < 2: continue
                
                price_now = closes.iloc[-1]
                price_prev = closes.iloc[-2]
                change = price_now - price_prev
                pct = (change / price_prev) * 100
                
                rows.append({
                    "Mã": t,
                    "Giá": float(price_now) / 1000.0,
                    "Thay đổi": float(change) / 1000.0,
                    "%": float(pct),
                    "Khối Lượng": int(df_one['Volume'].iloc[-1] if 'Volume' in df_one.columns else 0),
                    "Xu hướng": closes.tail(20).tolist(), # Data vẽ biểu đồ
                })
            except: continue
        return pd.DataFrame(rows)
    except: return pd.DataFrame()
