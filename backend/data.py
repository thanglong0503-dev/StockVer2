import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser

# --- Copy hàm load_data_final từ bản cũ vào đây ---
# Emo đã rút gọn lại để bạn dễ hình dung, bạn có thể paste code cũ đè lên
def get_stock_data(symbol, period="1y"):
    try:
        df = yf.Ticker(f"{symbol}.VN").history(period=period)
        if df.empty: return None
        
        # Tính toán các chỉ báo cơ bản để dùng chung
        df.ta.supertrend(length=10, multiplier=3, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=34, append=True)
        df.ta.ema(length=89, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        
        # Ichimoku
        ichi = ta.ichimoku(df['High'], df['Low'], df['Close'], tenkan=9, kijun=26, senkou=52)
        if ichi is not None: df = pd.concat([df, ichi[0]], axis=1)
        
        return df
    except: return None

def get_news(symbol):
    try:
        rss_url = f"https://news.google.com/rss/search?q=cổ+phiếu+{symbol}&hl=vi&gl=VN&ceid=VN:vi"
        feed = feedparser.parse(rss_url)
        return [{'title': e.title, 'link': e.link, 'published': e.get('published','')[:16]} for e in feed.entries[:5]]
    except: return []
