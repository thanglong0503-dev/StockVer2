import yfinance as yf
import pandas as pd
import pandas_ta as ta

# ======================================================
# 1. HÀM LẤY CHỈ SỐ THỊ TRƯỜNG (CHIẾN THUẬT ETF)
# ======================================================
def get_market_indices():
    """
    Dùng các mã GLOBAL (Quốc tế) để 100% tương thích với Streamlit Cloud.
    Thay vì cố lấy VNINDEX (bị chặn), ta lấy VN30 ETF.
    """
    targets = [
        # Dùng ETF VN30 đại diện cho thị trường VN (Yahoo không chặn mã này)
        {"name": "VN30 (ETF)", "symbol": "E1VFVN30.VN"}, 
        # Các chỉ số quốc tế
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "GOLD", "symbol": "GC=F"},
        {"name": "BITCOIN", "symbol": "BTC-USD"}
    ]
    
    results = []
    
    for item in targets:
        try:
            # Lấy đúng 5 ngày gần nhất
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                # Xác định màu sắc
                color = "#10b981" if change >= 0 else "#ef4444"
                
                results.append({
                    "Name": item["name"],
                    "Price": now,
                    "Change": change,
                    "Pct": pct,
                    "Color": color,
                    "Status": "LIVE"
                })
            else:
                # Nếu không có data (rất hiếm), trả về Offline
                raise Exception("No Data")
                
        except Exception:
            # Fallback an toàn để không bị lỗi giao diện
            results.append({
                "Name": item["name"],
                "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })
            
    return results

# ======================================================
# 2. HÀM LẤY BẢNG GIÁ CỔ PHIẾU (RADAR)
# ======================================================
def get_pro_data(tickers):
    """
    Lấy dữ liệu cổ phiếu từ Yahoo Finance.
    Yahoo thường không chặn các mã cổ phiếu cụ thể (HPG, SSI...)
    ngay cả khi chặn chỉ số index.
    """
    rows = []
    for t in tickers:
        try:
            symbol = f"{t}.VN"
            # Tải từng mã để an toàn hơn trên Cloud
            df = yf.Ticker(symbol).history(period="1y")
            
            if df.empty or len(df) < 50: continue
            
            # Tính toán chỉ báo
            # 1. Supertrend
            try:
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                if sti is not None: df = df.join(sti)
            except: pass
            
            # 2. RSI & EMA
            df.ta.rsi(length=14, append=True)
            df.ta.ema(length=34, append=True)
            
            # Lấy nến mới nhất
            now = df.iloc[-1]
            close = now['Close']
            
            # Logic chấm điểm
            score = 3
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
            if close > supertrend: score += 3
            if close > now.get('EMA_34', 0): score += 1
            rsi = now.get('RSI_14', 50)
            if 50 <= rsi <= 70: score += 1
            elif rsi < 30: score += 1
            
            final_score = max(0, min(10, score))
            
            # Dán nhãn hành động
            action = "NEUTRAL"
            if final_score >= 9: action = "STRONG BUY"
            elif final_score >= 7: action = "BUY"
            elif final_score <= 4: action = "SELL"
            
            # Dữ liệu vẽ chart mini
            trend_list = df['Close'].tail(30).tolist()
            trend_list = [float(x) for x in trend_list] # Ép kiểu float

            rows.append({
                "Symbol": t,
                "Price": close / 1000.0, # Chia 1000 để hiển thị gọn (VD: 20.5)
                "Pct": (close - df['Close'].iloc[-2]) / df['Close'].iloc[-2],
                "Signal": action,
                "Score": final_score,
                "Trend": trend_list
            })
        except: 
            continue
            
    return pd.DataFrame(rows)

# ======================================================
# 3. HÀM LẤY LỊCH SỬ VẼ CHART
# ======================================================
def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
