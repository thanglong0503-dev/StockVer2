import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests

# --- 1. HÀM LẤY TIN TỨC GOOGLE (Code cũ của bạn) ---
def get_stock_news_google(symbol):
    try:
        # URL RSS Google News tiếng Việt
        rss_url = f"https://news.google.com/rss/search?q=cổ+phiếu+{symbol}&hl=vi&gl=VN&ceid=VN:vi"
        feed = feedparser.parse(rss_url)
        news_list = []
        for e in feed.entries[:10]:
            news_list.append({
                'title': e.title,
                'link': e.link,
                'published': e.get('published', '')[:16] # Lấy ngày tháng
            })
        return news_list
    except: return []

# --- 2. HÀM LẤY DỮ LIỆU TỔNG HỢP (Code cũ tách nhỏ) ---
def get_stock_data_full(symbol):
    """Lấy BCTC, Hồ sơ, Cổ tức từ Yahoo"""
    try:
        stock = yf.Ticker(f"{symbol}.VN")
        
        # Lấy thông tin cơ bản
        info = stock.info
        
        # Lấy BCTC Quý
        fin = stock.quarterly_financials
        bal = stock.quarterly_balance_sheet
        cash = stock.quarterly_cashflow
        
        # Lấy cổ tức
        divs = stock.dividends
        splits = stock.splits
        
        return info, fin, bal, cash, divs, splits
    except:
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.Series(), pd.Series()

# --- 3. HÀM INDICATOR (Giữ nguyên cho Radar) ---
def get_pro_data(tickers):
    rows = []
    for t in tickers:
        try:
            df = yf.Ticker(f"{t}.VN").history(period="1y")
            if df.empty or len(df) < 50: continue
            
            # Tính chỉ báo cơ bản
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if sti is not None: df = df.join(sti)
            df.ta.rsi(length=14, append=True)
            
            now = df.iloc[-1]
            close = now['Close']
            
            # Chấm điểm nhanh
            score = 5
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
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
