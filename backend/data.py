import yfinance as yf
import pandas as pd
import pandas_ta as ta
import os
from vnstock import stock_historical_data

# ==========================================
# 1. CẤU HÌNH API KEY VNSTOCK
# ==========================================
# Nạp key của lão đại vào biến môi trường để thư viện nhận diện
os.environ["VNSTOCK_API_KEY"] = "vnstock_531f35536e7875e4e18ac83136cdf114"

# ==========================================
# 2. HÀM WRAPPER (BỌC HÀM VNSTOCK)
# ==========================================
def get_vnstock_data(symbol, days=365, type='stock'):
    """
    Hàm lấy dữ liệu từ Vnstock và chuẩn hóa tên cột
    để khớp với hệ thống cũ (Open, Close, High, Low...)
    """
    try:
        # Lấy ngày bắt đầu và kết thúc
        end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Gọi thư viện vnstock
        # resolution='1D': Khung ngày
        # source='TCBS': Nguồn ổn định nhất
        df = stock_historical_data(symbol=symbol, 
                                   start_date=start_date, 
                                   end_date=end_date, 
                                   resolution='1D', 
                                   type=type, 
                                   source='TCBS')
        
        if df is None or df.empty:
            return pd.DataFrame()

        # Đổi tên cột cho chuẩn bài (vnstock trả về chữ thường)
        df = df.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low', 
            'close': 'Close', 'volume': 'Volume', 'time': 'Date'
        })
        
        # Set Index là Date
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        return df.sort_index()
        
    except Exception as e:
        # print(f"Lỗi tải {symbol}: {e}")
        return pd.DataFrame()

# ==========================================
# 3. LẤY CHỈ SỐ THỊ TRƯỜNG (VNINDEX)
# ==========================================
def get_market_indices():
    """Lấy VN-INDEX từ Vnstock, Quốc tế từ Yahoo"""
    results = []
    
    # --- A. HÀNG VIỆT NAM (Dùng Vnstock) ---
    vn_targets = [
        {"name": "VN-INDEX", "symbol": "VNINDEX", "type": "index"},
        {"name": "VN30", "symbol": "VN30", "type": "index"},
        {"name": "HNX-INDEX", "symbol": "HNX", "type": "index"}
    ]
    
    for item in vn_targets:
        df = get_vnstock_data(item['symbol'], days=10, type=item['type'])
        
        if not df.empty and len(df) >= 2:
            now = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            change = now - prev
            pct = (change / prev) * 100
            
            results.append({
                "Name": item['name'], 
                "Price": now, "Change": change, "Pct": pct,
                "Color": "#10b981" if change >= 0 else "#ef4444", 
                "Status": "LIVE"
            })
        else:
            # Fallback nếu Vnstock lỗi kết nối
            results.append({"Name": item['name'], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})

    # --- B. HÀNG QUỐC TẾ (Dùng Yahoo) ---
    us_targets = [
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"}
    ]
    
    for item in us_targets:
        try:
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                results.append({
                    "Name": item["name"], "Price": now, "Change": change, "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE"
                })
        except:
            results.append({"Name": item["name"], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})
            
    return results

# ==========================================
# 4. LẤY DATA BẢNG GIÁ (RADAR)
# ==========================================
def get_pro_data(tickers):
    """Radar quét mã (Dùng Vnstock)"""
    rows = []
    for t in tickers:
        try:
            # Gọi hàm wrapper ở trên
            df = get_vnstock_data(t, days=365, type='stock')
            
            if df.empty or len(df) < 50: continue
            
            # --- TÍNH TOÁN ---
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if sti is not None: df = df.join(sti)
            df.ta.rsi(length=14, append=True)
            df.ta.ema(length=34, append=True)
            
            now = df.iloc[-1]
            close = now['Close']
            
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
            score = 3
            if close > supertrend: score += 3
            if close > now.get('EMA_34', 0): score += 1
            rsi = now.get('RSI_14', 50)
            if 50 <= rsi <= 70: score += 1
            elif rsi < 30: score += 1
            elif rsi > 75: score -= 1
            
            final_score = max(0, min(10, score))
            action = "NEUTRAL"
            if final_score >= 9: action = "STRONG BUY"
            elif final_score >= 7: action = "BUY"
            elif final_score <= 4: action = "SELL"
            
            trend_list = df['Close'].tail(30).tolist()
            trend_list = [float(x) for x in trend_list]

            rows.append({
                "Symbol": t,
                "Price": close / 1000.0, 
                "Pct": (close - df['Close'].iloc[-2]) / df['Close'].iloc[-2],
                "Signal": action,
                "Score": final_score,
                "Trend": trend_list
            })
        except: continue
        
    return pd.DataFrame(rows)

# ==========================================
# 5. LẤY LỊCH SỬ VẼ CHART
# ==========================================
def get_history_df(symbol):
    """Vẽ chart dùng Vnstock"""
    return get_vnstock_data(symbol, days=730, type='stock')
