import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_market_indices():
    """
    Sử dụng các mã GLOBAL (Toàn cầu) để đảm bảo 100% có dữ liệu trên Streamlit Cloud.
    Thay VNINDEX bằng ETF VN30 (Biến động y hệt nhưng không bị chặn).
    """
    # Danh sách "Bất tử" (Luôn có data)
    targets = [
        {"name": "VN30 ETF", "symbol": "E1VFVN30.VN"}, # Đại diện VN-INDEX
        {"name": "BITCOIN", "symbol": "BTC-USD"},      # Crypto (Chạy 24/7)
        {"name": "GOLD", "symbol": "GC=F"},             # Vàng thế giới
        {"name": "DOW JONES", "symbol": "^DJI"}         # Mỹ
    ]
    
    results = []
    
    for item in targets:
        try:
            # Tải data (dùng period 5d)
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                # Format màu sắc
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
                # Trường hợp hiếm hoi ko có data thì trả về dữ liệu rỗng
                raise Exception("Empty Data")
                
        except:
            # Fallback cứng (để không bao giờ bị mất khung)
            results.append({
                "Name": item["name"],
                "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })
            
    return results

def get_pro_data(tickers):
    """
    Lấy dữ liệu cổ phiếu Việt Nam.
    Lưu ý: Nếu Yahoo chặn IP Cloud, hàm này có thể trả về rỗng.
    """
    symbols = [f"{t}.VN" for t in tickers]
    try:
        # Tải data batch
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        rows = []
        
        for t in tickers:
            sym = f"{t}.VN"
            try:
                # Xử lý MultiIndex
                df = data[sym] if len(tickers) > 1 else data
                
                # Kiểm tra độ dài dữ liệu
                if df.empty or len(df) < 5: 
                    # Thử tải lại lẻ từng mã nếu batch thất bại (Cơ chế Retry)
                    df = yf.Ticker(sym).history(period="1y")
                    if df.empty: continue

                # --- TÍNH TOÁN CHỈ BÁO ---
                # Supertrend
                try:
                    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                    if sti is not None: df = df.join(sti)
                except: pass # Bỏ qua nếu lỗi tính toán
                
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=34, append=True)
                
                now = df.iloc[-1]
                close = now['Close']
                
                # Tìm supertrend
                st_cols = [c for c in df.columns if 'SUPERT' in c]
                supertrend = now[st_cols[0]] if st_cols else close
                
                # Scoring
                score = 5
                if close > supertrend: score += 2
                if close > now.get('EMA_34', 0): score += 1
                
                final_score = max(0, min(10, score))
                
                # Signal
                action = "NEUTRAL"
                if final_score >= 8: action = "STRONG BUY"
                elif final_score <= 3: action = "SELL"
                
                # Trend Line (Fix lỗi float)
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
            except Exception as e:
                # print(f"Lỗi mã {t}: {e}") # Debug nếu cần
                continue
                
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
