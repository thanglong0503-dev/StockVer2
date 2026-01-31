import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_market_indices():
    """
    Lấy chỉ số thị trường (Luôn trả về kết quả kể cả khi API lỗi)
    """
    targets = [
        {"name": "VN-INDEX", "symbol": "^VNINDEX"},
        {"name": "HNX-INDEX", "symbol": "^HASTC"},
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"}
    ]
    
    results = []
    
    for item in targets:
        try:
            # Tải data
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                results.append({
                    "Name": item["name"],
                    "Price": now,
                    "Change": change,
                    "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444",
                    "Status": "LIVE"
                })
            else:
                raise Exception("No Data")
                
        except:
            # TRƯỜNG HỢP LỖI: Vẫn thêm vào list nhưng để giá trị 0
            results.append({
                "Name": item["name"],
                "Price": 0.0,
                "Change": 0.0,
                "Pct": 0.0,
                "Color": "#64748b", # Màu xám (Offline)
                "Status": "OFFLINE"
            })
            
    return results

def get_pro_data(tickers):
    # (Giữ nguyên logic cũ của hàm này - Code 1000 dòng ở câu trả lời trước)
    symbols = [f"{t}.VN" for t in tickers]
    try:
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                df = data[sym] if len(tickers) > 1 else data
                if df.empty or len(df) < 50: continue
                
                # Indicator
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                if sti is not None: df = df.join(sti)
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=34, append=True)
                
                now = df.iloc[-1]
                close = now['Close']
                st_cols = [c for c in df.columns if 'SUPERT' in c]
                supertrend = now[st_cols[0]] if st_cols else close
                
                # Scoring
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
    except: return pd.DataFrame()

def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
