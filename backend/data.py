import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_vnindex_safe():
    """Hàm chuyên dụng để săn tìm VN-INDEX bằng mọi giá"""
    # Danh sách các mã dự phòng
    candidates = [
        "^VNINDEX",      # Mã chuẩn
        "VNINDEX.VN",    # Mã thay thế
        "E1VFVN30.VN"    # Quỹ ETF (Luôn hoạt động)
    ]
    
    for symbol in candidates:
        try:
            # Lấy data 1 tháng cho chắc ăn (tránh ngày lễ tết bị mất nến)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                # Nếu phải dùng ETF, ta chỉnh lại tên hiển thị chút cho đúng
                name = "VN-INDEX"
                if "E1VFVN30" in symbol:
                    name = "VN30 (ETF Proxy)"
                    
                return {
                    "Name": name, "Price": now, "Change": change, "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE"
                }
        except:
            continue # Thử mã tiếp theo
            
    # Nếu thử hết mà vẫn xịt (Rất hiếm)
    return {
        "Name": "VN-INDEX", "Price": 0.0, "Change": 0.0, "Pct": 0.0,
        "Color": "#64748b", "Status": "OFFLINE"
    }

def get_market_indices():
    """Lấy toàn bộ chỉ số thị trường"""
    results = []
    
    # 1. LẤY VN-INDEX (Ưu tiên số 1)
    vn_data = get_vnindex_safe()
    results.append(vn_data)
    
    # 2. LẤY CÁC CHỈ SỐ QUỐC TẾ KHÁC
    others = [
        {"name": "HNX-INDEX", "symbol": "^HASTC"}, # Nếu HNX lỗi cũng có thể áp dụng cách trên
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
                # Nếu lỗi thì trả về Offline
                results.append({
                    "Name": item["name"], "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                    "Color": "#64748b", "Status": "OFFLINE"
                })
        except:
            results.append({
                "Name": item["name"], "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })
            
    return results

def get_pro_data(tickers):
    """Lấy dữ liệu Radar bảng giá (Logic cũ giữ nguyên)"""
    symbols = [f"{t}.VN" for t in tickers]
    try:
        # Tải data
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                # Xử lý format MultiIndex của yfinance
                df = data[sym] if len(tickers) > 1 else data
                if df.empty or len(df) < 50: continue
                
                # Tính chỉ báo
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                if sti is not None: df = df.join(sti)
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=34, append=True)
                
                now = df.iloc[-1]
                close = now['Close']
                
                # Tìm cột Supertrend
                st_cols = [c for c in df.columns if 'SUPERT' in c]
                supertrend = now[st_cols[0]] if st_cols else close
                
                # Chấm điểm
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
                
                # Trend data
                trend_list = df['Close'].tail(30).tolist()
                trend_list = [float(x) for x in trend_list] # Fix lỗi chart

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
    """Lấy dữ liệu lịch sử để vẽ Chart"""
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
