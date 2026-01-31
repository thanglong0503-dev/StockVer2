import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
import json

# ======================================================
# 1. HÀM LẤY DATA "LẬU" TỪ TRADINGVIEW (DATA_FEED)
# ======================================================
def get_tv_data(symbol):
    """
    Lấy dữ liệu từ API ẩn của TradingView scanner.
    Nguồn này server quốc tế, ít khi chặn IP Cloud.
    Symbol: 'VNINDEX', 'HNXINDEX'
    """
    try:
        url = "https://scanner.tradingview.com/vietnam/scan"
        payload = {
            "symbols": {
                "tickers": [f"HOSE:{symbol}" if symbol == "VNINDEX" else f"HNX:{symbol}"],
                "query": {"types": []}
            },
            "columns": ["close", "change", "CryptoRating"]
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Gọi POST request
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        data = resp.json()
        
        if data and "data" in data:
            # TradingView trả về: [close, change, rating]
            item = data["data"][0]["d"]
            close = item[0]
            change = item[1]
            pct = (change / (close - change)) * 100
            
            return {
                "Name": "VN-INDEX" if "VN" in symbol else "HNX-INDEX",
                "Price": close,
                "Change": change,
                "Pct": pct,
                "Color": "#10b981" if change >= 0 else "#ef4444",
                "Status": "LIVE (TV)"
            }
    except Exception as e:
        # print(f"TV Error: {e}") 
        pass
    return None

# ======================================================
# 2. HÀM LẤY ETF DỰ PHÒNG (NẾU MẤT HẾT KẾT NỐI)
# ======================================================
def get_backup_etf():
    """Lấy ETF VN30 làm tham chiếu nếu VN-INDEX bị chặn"""
    try:
        etf = yf.Ticker("E1VFVN30.VN").history(period="5d")
        if len(etf) >= 2:
            now = etf['Close'].iloc[-1]
            prev = etf['Close'].iloc[-2]
            return {
                "Name": "VN-TREND (ETF)", # Đổi tên để người dùng hiểu đây là xu hướng
                "Price": now, # Giá này là 20k, ko phải 1200 điểm
                "Change": now - prev,
                "Pct": (now - prev)/prev * 100,
                "Color": "#10b981" if (now-prev) >= 0 else "#ef4444",
                "Status": "BACKUP"
            }
    except: return None

# ======================================================
# 3. HÀM TỔNG HỢP CHỈ SỐ
# ======================================================
def get_market_indices():
    results = []
    
    # --- A. LẤY VN-INDEX ---
    # Cách 1: Thử TradingView (Nguồn quốc tế)
    vn_data = get_tv_data("VNINDEX")
    
    # Cách 2: Nếu TV tạch, thử TCBS Direct (có thể bị chặn)
    if not vn_data:
        try:
            # Code TCBS rút gọn
            now = int(time.time())
            url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?ticker=VNINDEX&type=index&resolution=D&from={now-86400*5}&to={now}"
            data = requests.get(url, timeout=3).json()['data']
            last = data[-1]; prev = data[-2]
            vn_data = {
                "Name": "VN-INDEX", "Price": last['close'], "Change": last['close']-prev['close'],
                "Pct": (last['close']-prev['close'])/prev['close']*100,
                "Color": "#10b981" if last['close']>=prev['close'] else "#ef4444", "Status": "LIVE (TCBS)"
            }
        except: pass

    # Cách 3: Nếu tạch hết -> Dùng ETF Yahoo (Tuyệt chiêu cuối)
    if not vn_data:
        vn_data = get_backup_etf()

    # Thêm vào kết quả (Nếu vẫn None thì tạo Offline)
    if vn_data: results.append(vn_data)
    else: results.append({"Name": "VN-INDEX", "Price": 0, "Change": 0, "Pct": 0, "Color": "#64748b", "Status": "OFFLINE"})

    # --- B. LẤY HNX-INDEX ---
    hnx_data = get_tv_data("HNXINDEX")
    if hnx_data: results.append(hnx_data)
    else: results.append({"Name": "HNX-INDEX", "Price": 0, "Change": 0, "Pct": 0, "Color": "#64748b", "Status": "OFFLINE"})

    # --- C. QUỐC TẾ (YAHOO - LUÔN SỐNG) ---
    others = [
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "GOLD", "symbol": "GC=F"},
        {"name": "BITCOIN", "symbol": "BTC-USD"}
    ]
    for item in others:
        try:
            h = yf.Ticker(item['symbol']).history(period="5d")
            now = h['Close'].iloc[-1]; prev = h['Close'].iloc[-2]
            results.append({
                "Name": item['name'], "Price": now, "Change": now-prev, "Pct": (now-prev)/prev*100,
                "Color": "#10b981" if (now-prev)>=0 else "#ef4444", "Status": "LIVE"
            })
        except:
             results.append({"Name": item['name'], "Price": 0, "Change": 0, "Pct": 0, "Color": "#64748b", "Status": "OFFLINE"})
             
    return results

# ======================================================
# 4. HÀM BẢNG GIÁ (Cổ phiếu lẻ thì Yahoo vẫn lấy được)
# ======================================================
def get_pro_data(tickers):
    # Logic Radar giữ nguyên (Yahoo lấy cổ phiếu lẻ HPG, SSI ít khi bị chặn)
    symbols = [f"{t}.VN" for t in tickers]
    try:
        # Fallback cơ chế: Tải từng mã nếu tải gộp lỗi
        rows = []
        for t in tickers:
            try:
                # Ưu tiên Yahoo, vì TCBS API index chặn nhưng Stock API đôi khi thả
                df = yf.Ticker(f"{t}.VN").history(period="1y")
                
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
                rows.append({
                    "Symbol": t, "Price": close/1000.0, "Pct": (close-df['Close'].iloc[-2])/df['Close'].iloc[-2],
                    "Signal": action, "Score": final_score, "Trend": trend_list
                })
            except: continue
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
