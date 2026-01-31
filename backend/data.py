# backend/data.py
import yfinance as yf
import pandas as pd
import random

def get_market_data(tickers):
    # Định dạng lại mã cho Yahoo (thêm .VN)
    symbols = [f"{t}.VN" for t in tickers]
    
    try:
        # Tải data batch (nhanh hơn)
        data = yf.download(symbols, period="1mo", interval="1d", group_by='ticker', progress=False)
        
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                # Xử lý truy cập MultiIndex an toàn
                if len(tickers) > 1:
                    df_ticker = data[sym]
                else:
                    df_ticker = data
                
                # Lấy cột Close và drop NaN
                closes = df_ticker['Close'].dropna()
                
                if len(closes) < 2: continue
                
                # Tính toán giá
                current_price = float(closes.iloc[-1])
                prev_price = float(closes.iloc[-2])
                change = current_price - prev_price
                pct_change = (change / prev_price) * 100
                volume = int(df_ticker['Volume'].iloc[-1]) if 'Volume' in df_ticker.columns else 0

                # --- FIX LỖI SPARKLINE ---
                # Lấy 20 giá gần nhất, chuyển thành list float thuần túy
                trend_data = closes.tail(20).tolist()
                trend_data = [float(x) for x in trend_data] # Ép kiểu float lần nữa cho chắc

                rows.append({
                    "Symbol": t,
                    "Price": current_price / 1000.0, # Đơn vị nghìn đồng
                    "Change": change / 1000.0,
                    "Pct": pct_change,
                    "Volume": volume,
                    "Trend": trend_data, # List này sẽ vẽ biểu đồ
                })
            except Exception as e:
                print(f"Lỗi mã {t}: {e}")
                continue
                
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame()
