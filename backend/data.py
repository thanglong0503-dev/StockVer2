# backend/data.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_market_indices():
    """Lấy chỉ số thị trường (Tải từng cái để tránh lỗi)"""
    indices = {
        "VN-INDEX": "^VNINDEX",
        "HNX-INDEX": "^HASTC", 
        "DOW JONES": "^DJI",
        "NASDAQ": "^IXIC"
    }
    
    data_list = []
    
    for name, ticker in indices.items():
        try:
            # Tải riêng từng mã, lấy 5 ngày để chắc chắn có dữ liệu
            df = yf.Ticker(ticker).history(period="5d")
            
            if len(df) >= 2:
                now = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                data_list.append({
                    "Name": name,
                    "Price": now,
                    "Change": change,
                    "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444"
                })
        except Exception as e:
            print(f"Lỗi tải {name}: {e}")
            continue
            
    return data_list

def get_pro_data(tickers):
    # (Giữ nguyên logic cũ của hàm này)
    symbols = [f"{t}.VN" for t in tickers]
    try:
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                df = data[sym] if len(tickers) > 1 else data
                if df.empty or len(df) < 50: continue
                
                # Tính chỉ báo
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                if sti is not None: df = df.join(sti)
                
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=34, append=True)
                
                now = df.iloc[-1]
                close = now['Close']
                st_cols = [c for c in df.columns if 'SUPERT' in c]
                supertrend = now[st_cols[0]] if st_cols else close
                
                # Chấm điểm
                score = 3
                pros, cons = [], []
                
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
                elif final_score <= 2: action = "STRONG SELL"
                elif final_score <= 4: action = "SELL"
                
                # Trend data
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
