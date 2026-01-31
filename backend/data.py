import yfinance as yf
import pandas as pd
import pandas_ta as ta
from vnstock import stock_historical_data, quote

def get_vnindex_from_vnstock():
    """
    Hàm lấy VN-INDEX từ nguồn TCBS/SSI thông qua thư viện vnstock.
    Nguồn này cực khỏe, chấp cả Cloud Server.
    """
    try:
        # Lấy data VNINDEX
        df = stock_historical_data(symbol='VNINDEX', resolution='1D', type='index')
        
        if df is not None and not df.empty and len(df) >= 2:
            # Vnstock trả về cột: time, open, high, low, close, volume
            now = float(df['close'].iloc[-1])
            prev = float(df['close'].iloc[-2])
            change = now - prev
            pct = (change / prev) * 100
            
            return {
                "Name": "VN-INDEX",
                "Price": now,
                "Change": change,
                "Pct": pct,
                "Color": "#10b981" if change >= 0 else "#ef4444",
                "Status": "LIVE (VNSTOCK)"
            }
    except:
        pass # Nếu lỗi thì trả về None để Fallback xử lý
    return None

def get_market_indices():
    """Tổng hợp chỉ số: VN dùng Vnstock, Mỹ dùng Yahoo"""
    results = []
    
    # 1. ƯU TIÊN LẤY VN-INDEX TỪ VNSTOCK
    vn_data = get_vnindex_from_vnstock()
    if vn_data:
        results.append(vn_data)
    else:
        # Nếu Vnstock sập (hiếm), dùng ETF dự phòng
        try:
            etf = yf.Ticker("E1VFVN30.VN").history(period="5d")
            now = etf['Close'].iloc[-1]
            prev = etf['Close'].iloc[-2]
            results.append({
                "Name": "VN30 (ETF Proxy)", "Price": now, 
                "Change": now-prev, "Pct": (now-prev)/prev*100,
                "Color": "#10b981" if (now-prev)>=0 else "#ef4444", "Status": "LIVE (ETF)"
            })
        except:
            results.append({"Name": "VN-INDEX", "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})

    # 2. LẤY CÁC CHỈ SỐ KHÁC (Yahoo vẫn ngon cho hàng Mỹ)
    others = [
        {"name": "HNX-INDEX", "symbol": "^HASTC"}, # Thử lấy HNX
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"}
    ]
    
    for item in others:
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
            else:
                # Nếu HNX lỗi thì thôi, không hiện hoặc hiện Offline
                results.append({"Name": item["name"], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})
        except:
            results.append({"Name": item["name"], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})
            
    return results

def get_pro_data(tickers):
    """Lấy dữ liệu bảng giá (Sử dụng vnstock cho nhanh và chính xác hơn Yahoo)"""
    rows = []
    for t in tickers:
        try:
            # Dùng vnstock lấy giá realtime
            # Lưu ý: vnstock.quote trả về dữ liệu realtime cực nhanh
            df = stock_historical_data(symbol=t, resolution='1D', type='stock')
            
            if df is None or df.empty or len(df) < 50: continue
            
            # Xử lý chỉ báo bằng Pandas TA
            # Đổi tên cột cho khớp với thư viện ta: close -> Close
            df = df.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'})
            
            # Tính toán
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if sti is not None: df = df.join(sti)
            df.ta.rsi(length=14, append=True)
            df.ta.ema(length=34, append=True)
            
            now = df.iloc[-1]
            close = now['Close']
            
            # Supertrend check
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

def get_history_df(symbol):
    """Lấy lịch sử để vẽ chart"""
    # Dùng vnstock lấy data vẽ chart cực đẹp và đầy đủ
    try:
        df = stock_historical_data(symbol=symbol, resolution='1D', type='stock')
        df = df.rename(columns={'time':'Date', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'})
        df = df.set_index('Date')
        return df
    except:
        return pd.DataFrame()
