import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_market_indices():
    """
    Lấy chỉ số thị trường.
    Mẹo: Dùng E1VFVN30.VN làm tham chiếu cho VN-Index vì Yahoo luôn có data mã này.
    """
    targets = [
        {"name": "VN30 (ETF)", "symbol": "E1VFVN30.VN"}, # Dùng ETF thay thế Index để luôn LIVE
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"},
        {"name": "S&P 500", "symbol": "^GSPC"} # Đổi HNX thành S&P 500 cho chuẩn quốc tế
    ]
    
    results = []
    
    for item in targets:
        try:
            # Tải data (dùng period 5d để chắc chắn có nến)
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                # Format giá cho đẹp (Nếu là Dow Jones thì để nguyên, VN thì chia 1000 nếu cần)
                price = now
                if item["name"] == "VN30 (ETF)":
                    price = price # Giữ nguyên giá ETF
                
                results.append({
                    "Name": item["name"],
                    "Price": price,
                    "Change": change,
                    "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444",
                    "Status": "LIVE"
                })
            else:
                raise Exception("No Data")
                
        except:
            # Fallback nếu vẫn lỗi
            results.append({
                "Name": item["name"],
                "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })
            
    return results

def get_pro_data(tickers):
    # (Giữ nguyên logic Radar 1000 dòng của bạn ở đây)
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
