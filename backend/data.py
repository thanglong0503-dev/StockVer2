import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
from datetime import datetime, timedelta

def get_index_from_dnse(symbol):
    """
    Hàm Hacker: Lấy dữ liệu trực tiếp từ API của DNSE (Entrade)
    Nguồn này cực nhanh, realtime và không bị chặn IP như Yahoo.
    Symbol: 'VNINDEX', 'HNX', 'VN30'
    """
    try:
        # Tính timestamp cho 5 ngày gần nhất
        end_time = int(time.time())
        start_time = int(end_time - 5 * 24 * 60 * 60) # 5 ngày trước
        
        # API Endpoint của DNSE (Công khai)
        url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol={symbol}&resolution=1D&from={start_time}&to={end_time}"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data and 't' in data and len(data['t']) >= 2:
            # Lấy 2 cây nến cuối cùng
            now = data['c'][-1]      # Giá đóng cửa mới nhất
            prev = data['c'][-2]     # Giá đóng cửa phiên trước
            change = now - prev
            pct = (change / prev) * 100
            
            # Đổi tên hiển thị cho đẹp
            display_name = symbol
            if symbol == "VNINDEX": display_name = "VN-INDEX"
            if symbol == "HNX": display_name = "HNX-INDEX"
            
            return {
                "Name": display_name,
                "Price": float(now),
                "Change": float(change),
                "Pct": float(pct),
                "Color": "#10b981" if change >= 0 else "#ef4444",
                "Status": "LIVE ⚡" # Đánh dấu nguồn xịn
            }
    except Exception as e:
        print(f"Lỗi lấy {symbol} từ DNSE: {e}")
        return None
    return None

def get_market_indices():
    """Tổng hợp chỉ số: VN lấy từ DNSE, Quốc tế lấy từ Yahoo"""
    results = []
    
    # 1. LẤY HÀNG VIỆT NAM (Dùng nguồn DNSE bao uy tín)
    vn_targets = ["VNINDEX", "VN30", "HNX"]
    
    for sym in vn_targets:
        res = get_index_from_dnse(sym)
        if res:
            results.append(res)
        else:
            # Fallback: Nếu DNSE sập (hiếm), trả về Offline
            results.append({
                "Name": sym, "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })

    # 2. LẤY HÀNG QUỐC TẾ (Dùng Yahoo vẫn ngon cho hàng Mỹ)
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
            pass # Bỏ qua nếu lỗi
            
    return results

# --- CÁC HÀM CŨ GIỮ NGUYÊN ---
def get_pro_data(tickers):
    # Logic Radar (Giữ nguyên code 1000 dòng ở câu trước)
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
