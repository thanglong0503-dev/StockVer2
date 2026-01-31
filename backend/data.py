import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests

# --- 1. LẤY CHỈ SỐ QUAN TRỌNG (FULL) ---
def get_market_indices():
    """Lấy danh sách chỉ số đầy đủ: VN, Mỹ, Vàng, Coin"""
    targets = [
        {"name": "VN30 ETF", "symbol": "E1VFVN30.VN"}, # Đại diện VN-Index
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"},         # Thêm Nasdaq
        {"name": "GOLD", "symbol": "GC=F"},             # Thêm Vàng
        {"name": "BITCOIN", "symbol": "BTC-USD"}       # Thêm Bitcoin
    ]
    results = []
    for item in targets:
        try:
            t = yf.Ticker(item["symbol"])
            h = t.history(period="5d")
            if len(h) >= 2:
                now = h['Close'].iloc[-1]
                prev = h['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                results.append({
                    "Name": item["name"], "Price": now, "Change": change, "Pct": pct,
                    "Color": "#10b981" if change >= 0 else "#ef4444", "Status": "LIVE"
                })
        except:
            results.append({"Name": item["name"], "Price": 0, "Change": 0, "Pct": 0, "Color": "#64748b", "Status": "OFFLINE"})
    return results

# --- 2. LẤY TIN TỨC GOOGLE ---
def get_stock_news_google(symbol):
    try:
        rss_url = f"https://news.google.com/rss/search?q=cổ+phiếu+{symbol}&hl=vi&gl=VN&ceid=VN:vi"
        feed = feedparser.parse(rss_url)
        return [{'title': e.title, 'link': e.link, 'published': e.get('published', '')[:16]} for e in feed.entries[:10]]
    except: return []

# --- 3. LẤY FULL DATA (BCTC + INFO) ---
def get_stock_data_full(symbol):
    try:
        stock = yf.Ticker(f"{symbol}.VN")
        info = stock.info
        fin = stock.quarterly_financials
        bal = stock.quarterly_balance_sheet
        divs = stock.dividends
        
        # Fallback giá hiện tại nếu info lỗi
        if 'currentPrice' not in info:
             h = stock.history(period='1d')
             if not h.empty: info['currentPrice'] = h['Close'].iloc[-1]
             
        return info, fin, bal, divs
    except: return {}, pd.DataFrame(), pd.DataFrame(), pd.Series()

# --- 4. RADAR & HISTORY ---
def get_pro_data(tickers):
    rows = []
    for t in tickers:
        try:
            df = yf.Ticker(f"{t}.VN").history(period="1y")
            if df.empty or len(df) < 50: continue
            
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if sti is not None: df = df.join(sti)
            df.ta.rsi(length=14, append=True)
            
            now = df.iloc[-1]
            close = now['Close']
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
            score = 5
            if close > supertrend: score += 2
            else: score -= 2
            
            rows.append({
                "Symbol": t, "Price": close/1000.0, 
                "Pct": (close-df['Close'].iloc[-2])/df['Close'].iloc[-2],
                "Signal": "BUY" if score >= 7 else "SELL", 
                "Score": max(0, min(10, score)),
                "Trend": df['Close'].tail(30).tolist()
            })
        except: continue
    return pd.DataFrame(rows)

def get_history_df(symbol):
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
