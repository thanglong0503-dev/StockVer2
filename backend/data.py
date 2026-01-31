import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
import random

def get_index_realtime_vietnam(symbol_dnse, symbol_ssi, name):
    """
    Hàm lấy chỉ số Việt Nam đa nguồn (Multi-Source):
    1. Thử SSI (iBoard) - Nguồn xịn nhất.
    2. Nếu tạch, thử DNSE (Entrade).
    3. Nếu tạch tiếp, thử Yahoo.
    """
    # Header giả lập trình duyệt Chrome (Quan trọng để không bị chặn)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://iboard.ssi.com.vn/',
        'Accept': 'application/json'
    }
    
    current_time = int(time.time())
    start_time = current_time - (7 * 24 * 60 * 60) # 7 ngày trước

    # --- NGUỒN 1: SSI (iBoard) ---
    try:
        # SSI dùng mã: VNINDEX, VN30, HNXIndex
        url_ssi = f"https://iboard.ssi.com.vn/dchart/api/history?resolution=D&symbol={symbol_ssi}&from={start_time}&to={current_time}"
        res = requests.get(url_ssi, headers=headers, timeout=5)
        data = res.json()
        
        if data and 'c' in data and len(data['c']) >= 2:
            now = float(data['c'][-1])
            prev = float(data['c'][-2])
            change = now - prev
            pct = (change / prev) * 100
            
            return {
                "Name": name, "Price": now, "Change": change, "Pct": pct,
                "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE (SSI)"
            }
    except:
        pass # Lỗi thì lẳng lặng qua nguồn 2

    # --- NGUỒN 2: DNSE ---
    try:
        url_dnse = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol={symbol_dnse}&resolution=1D&from={start_time}&to={current_time}"
        res = requests.get(url_dnse, headers=headers, timeout=5)
        data = res.json()
        
        if data and 'c' in data and len(data['c']) >= 2:
            now = float(data['c'][-1])
            prev = float(data['c'][-2])
            change = now - prev
            pct = (change / prev) * 100
            
            return {
                "Name": name, "Price": now, "Change": change, "Pct": pct,
                "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE (DNSE)"
            }
    except:
        pass

    # --- NGUỒN 3: YAHOO (ETF DỰ PHÒNG) ---
    if name == "VN30" or name == "VN-INDEX":
        try:
            ticker = yf.Ticker("E1VFVN30.VN")
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                return {
                    "Name": name, "Price": now, "Change": change, "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE (ETF)"
                }
        except: pass

    # --- THẤT BẠI TOÀN TẬP ---
    return {
        "Name": name, "Price": 0.0, "Change": 0.0, "Pct": 0.0,
        "Color": "#64748b", "Status": "OFFLINE"
    }

def get_market_indices():
    """Tổng hợp chỉ số"""
    results = []
    
    # 1. VN-INDEX (SSI: VNINDEX | DNSE: VNINDEX)
    results.append(get_index_realtime_vietnam("VNINDEX", "VNINDEX", "VN-INDEX"))
    
    # 2. VN30 (SSI: VN30 | DNSE: VN30)
    results.append(get_index_realtime_vietnam("VN30", "VN30", "VN30"))
    
    # 3. HNX (SSI: HNXIndex | DNSE: HNX) -> Lưu ý mã SSI khác chút
    results.append(get_index_realtime_vietnam("HNX", "HNXIndex", "HNX-INDEX"))
    
    # 4. QUỐC TẾ (Yahoo vẫn ngon)
    try:
        dj = yf.Ticker("^DJI").history(period="5d")
        if len(dj) >= 2:
            now = dj['Close'].iloc[-1]
            prev = dj['Close'].iloc[-2]
            chg = now - prev
            pct = (chg/prev)*100
            results.append({"Name": "DOW JONES", "Price": now, "Change": chg, "Pct": pct, "Color": "#10b981" if chg>=0 else "#ef4444", "Status": "LIVE"})
        else:
            raise Exception("No Data")
    except:
        results.append({"Name": "DOW JONES", "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})

    return results

# --- GIỮ NGUYÊN CODE CŨ CỦA CÁC HÀM KHÁC ---
def get_pro_data(tickers):
    # Logic Radar 1000 dòng giữ nguyên...
    symbols = [f"{t}.VN" for t in tickers]
    try:
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                df = data[sym] if len(tickers) > 1 else data
                if df.empty or len(df) < 50: continue
                
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
    except: return pd.DataFrame()

def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
