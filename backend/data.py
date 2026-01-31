import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
from datetime import datetime

# ======================================================
# 1. HÀM GỌI API GỐC TCBS (KHÔNG CẦN THƯ VIỆN)
# ======================================================
def get_tcbs_data(ticker, type='stock'):
    """
    Gọi trực tiếp API của TCBS. 
    ticker: Mã CK (HPG, SSI) hoặc Chỉ số (VNINDEX)
    type: 'stock' hoặc 'index'
    """
    try:
        # Cấu hình thời gian: 365 ngày gần nhất
        now = int(time.time())
        start = now - (365 * 24 * 60 * 60)
        
        # URL API "Backdoor" của TCBS
        url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?ticker={ticker}&type={type}&resolution=D&from={start}&to={now}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        # Gọi API với timeout 10s
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        if 'data' in data and len(data['data']) > 0:
            df = pd.DataFrame(data['data'])
            # Đổi tên cột chuẩn
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume', 'tradingDate': 'Date'
            })
            # Xử lý ngày tháng
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            return df.sort_index()
            
    except Exception as e:
        # print(f"Error {ticker}: {e}")
        pass
    return pd.DataFrame()

# ======================================================
# 2. HÀM LẤY CHỈ SỐ VN-INDEX (AUTO FIX OFFLINE)
# ======================================================
def get_market_indices():
    results = []
    
    # --- A. VIỆT NAM (Nguồn TCBS) ---
    vn_targets = [
        {"name": "VN-INDEX", "symbol": "VNINDEX", "type": "index"},
        {"name": "VN30", "symbol": "VN30", "type": "index"},
        {"name": "HNX-INDEX", "symbol": "HNXIndex", "type": "index"}
    ]
    
    for item in vn_targets:
        df = get_tcbs_data(item['symbol'], item['type'])
        
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
            # Fallback ETF nếu TCBS nghẽn
            if item['name'] == "VN-INDEX":
                 try:
                    etf = yf.Ticker("E1VFVN30.VN").history(period="5d")
                    now = etf['Close'].iloc[-1]
                    prev = etf['Close'].iloc[-2]
                    results.append({
                        "Name": "VN-INDEX (ETF)", "Price": now, "Change": now-prev, "Pct": (now-prev)/prev*100,
                        "Color": "#10b981" if (now-prev)>=0 else "#ef4444", "Status": "LIVE (ETF)"
                    })
                 except: 
                    results.append({"Name": item['name'], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})
            else:
                results.append({"Name": item['name'], "Price": 0.0, "Change": 0.0, "Pct": 0.0, "Color": "#64748b", "Status": "OFFLINE"})

    # --- B. QUỐC TẾ (Nguồn Yahoo) ---
    us_targets = [
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"}
    ]
    for item in us_targets:
        try:
            t = yf.Ticker(item["symbol"])
            h = t.history(period="5d")
            if len(h) >= 2:
                now = h['Close'].iloc[-1]
                prev = h['Close'].iloc[-2]
                chg = now - prev
                pct = (chg/prev)*100
                results.append({"Name": item["name"], "Price": now, "Change": chg, "Pct": pct, "Color": "#10b981" if chg>=0 else "#ef4444", "Status": "LIVE"})
        except: pass
            
    return results

# ======================================================
# 3. HÀM QUÉT RADAR (BẢNG GIÁ)
# ======================================================
def get_pro_data(tickers):
    rows = []
    for t in tickers:
        try:
            # 1. Gọi TCBS (Nhanh, Chính xác)
            df = get_tcbs_data(t, type='stock')
            
            # 2. Backup bằng Yahoo nếu TCBS lỗi
            if df.empty: df = yf.Ticker(f"{t}.VN").history(period="1y")
            
            if df.empty or len(df) < 50: continue
            
            # Tính toán
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if sti is not None: df = df.join(sti)
            df.ta.rsi(length=14, append=True)
            df.ta.ema(length=34, append=True)
            
            now = df.iloc[-1]
            close = now['Close']
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
            # Score
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
            
            # Chart Data
            trend_list = df['Close'].tail(30).tolist()
            
            rows.append({
                "Symbol": t,
                "Price": close, # TCBS trả về VND chuẩn
                "Pct": (close - df['Close'].iloc[-2]) / df['Close'].iloc[-2],
                "Signal": action,
                "Score": final_score,
                "Trend": trend_list
            })
        except: continue
    return pd.DataFrame(rows)

# ======================================================
# 4. HÀM LẤY LỊCH SỬ CHO BIỂU ĐỒ
# ======================================================
def get_history_df(symbol):
    df = get_tcbs_data(symbol, type='stock')
    if df.empty: df = yf.Ticker(f"{symbol}.VN").history(period="2y")
    return df
