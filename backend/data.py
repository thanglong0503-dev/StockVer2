import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests
from datetime import datetime
import time

# ==============================================================================
# 1. HỆ THỐNG CHỈ SỐ THỊ TRƯỜNG (MARKET INDICES)
# Chiến thuật: Dùng ETF VN30 đại diện cho VN-INDEX để tránh bị chặn IP trên Cloud
# ==============================================================================
def get_market_indices():
    """
    Lấy dữ liệu các chỉ số quan trọng:
    - VN30 ETF (Thay cho VN-INDEX để đảm bảo luôn Live)
    - US Market (Dow Jones, Nasdaq)
    - Commodities (Gold, Oil)
    - Crypto (Bitcoin)
    """
    targets = [
        {"name": "VN30 (ETF)", "symbol": "E1VFVN30.VN"}, # Proxy an toàn nhất
        {"name": "DOW JONES", "symbol": "^DJI"},
        {"name": "NASDAQ", "symbol": "^IXIC"},
        {"name": "GOLD", "symbol": "GC=F"},
        {"name": "BITCOIN", "symbol": "BTC-USD"}
    ]
    
    results = []
    
    for item in targets:
        try:
            # Lấy dữ liệu 5 ngày gần nhất
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                now = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = now - prev
                pct = (change / prev) * 100
                
                # Xác định màu sắc xu hướng
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
                raise Exception("No Data")
                
        except Exception:
            # Fallback an toàn để UI không bị vỡ
            results.append({
                "Name": item["name"],
                "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                "Color": "#64748b", "Status": "OFFLINE"
            })
            
    return results

# ==============================================================================
# 2. HỆ THỐNG TIN TỨC (NEWS AGGREGATOR)
# Sử dụng Google News RSS Feed (Nguồn tin cậy, không bị chặn)
# ==============================================================================
def get_stock_news_google(symbol):
    """
    Lấy tin tức tiếng Việt mới nhất về mã cổ phiếu từ Google News
    """
    try:
        # Query string tối ưu cho tin tức Việt Nam
        rss_url = f"https://news.google.com/rss/search?q=cổ+phiếu+{symbol}&hl=vi&gl=VN&ceid=VN:vi"
        
        # Parse RSS Feed
        feed = feedparser.parse(rss_url)
        news_list = []
        
        # Lấy 10 tin mới nhất
        for entry in feed.entries[:10]:
            published = entry.get('published', '')
            # Cắt chuỗi ngày tháng cho gọn (VD: Mon, 25 Dec 2025...)
            if len(published) > 16:
                published = published[:16]
                
            news_list.append({
                'title': entry.title,
                'link': entry.link,
                'published': published,
                'source': entry.source.title if 'source' in entry else 'Google News'
            })
            
        return news_list
    except Exception as e:
        # print(f"Lỗi lấy tin tức: {e}")
        return []

# ==============================================================================
# 3. HỆ THỐNG DỮ LIỆU CƠ BẢN (FUNDAMENTAL DEEP-DIVE)
# Lấy BCTC, Hồ sơ, Cổ tức
# ==============================================================================
def get_stock_data_full(symbol):
    """
    Lấy toàn bộ dữ liệu cơ bản của doanh nghiệp:
    1. Info (PE, PB, Market Cap, Mô tả...)
    2. Financials (KQKD, Cân đối kế toán, Dòng tiền)
    3. Dividends (Lịch sử trả cổ tức)
    """
    try:
        ticker = yf.Ticker(f"{symbol}.VN")
        
        # 1. Thông tin chung
        info = ticker.info
        
        # Fallback: Nếu Yahoo không trả về giá hiện tại trong info (thường xuyên bị),
        # ta lấy giá từ lịch sử phiên gần nhất để điền vào.
        if 'currentPrice' not in info or info['currentPrice'] is None:
            fast_hist = ticker.history(period='1d')
            if not fast_hist.empty:
                info['currentPrice'] = fast_hist['Close'].iloc[-1]
            else:
                info['currentPrice'] = 0

        # 2. Báo cáo tài chính (Lấy theo Quý)
        fin = ticker.quarterly_income_stmt      # Kết quả kinh doanh
        bal = ticker.quarterly_balance_sheet    # Cân đối kế toán
        cash = ticker.quarterly_cashflow        # Lưu chuyển tiền tệ
        
        # 3. Cổ tức & Chia tách
        divs = ticker.dividends
        splits = ticker.splits
        
        return info, fin, bal, cash, divs, splits
        
    except Exception as e:
        # Trả về dữ liệu rỗng nếu lỗi để app không crash
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.Series(), pd.Series()

# ==============================================================================
# 4. HỆ THỐNG MÁY QUÉT (RADAR SCANNER)
# Quét danh sách mã, tính chỉ báo nhanh để chấm điểm
# ==============================================================================
def get_pro_data(tickers):
    """
    Quét danh sách các mã cổ phiếu (Watchlist).
    Tính toán nhanh các chỉ báo: SuperTrend, RSI, EMA.
    Trả về DataFrame tổng hợp cho bảng Radar.
    """
    rows = []
    
    for t in tickers:
        try:
            symbol = f"{t}.VN"
            # Tải dữ liệu 1 năm để đủ tính EMA, RSI
            df = yf.Ticker(symbol).history(period="1y")
            
            if df.empty or len(df) < 50: continue
            
            # --- TÍNH CHỈ BÁO KỸ THUẬT (Technical Indicators) ---
            # 1. SuperTrend (Quan trọng nhất để xác định Trend)
            try:
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                if sti is not None: df = df.join(sti)
            except: pass
            
            # 2. RSI (14)
            df.ta.rsi(length=14, append=True)
            
            # 3. EMA (34) - Xu hướng ngắn hạn
            df.ta.ema(length=34, append=True)
            
            # Lấy nến mới nhất
            now = df.iloc[-1]
            close = now['Close']
            
            # --- LOGIC CHẤM ĐIỂM SƠ BỘ (SCORING) ---
            score = 5 # Điểm khởi đầu (Trung tính)
            
            # Tìm cột Supertrend (Vì tên cột sinh động dạng SUPERT_10_3.0)
            st_cols = [c for c in df.columns if 'SUPERT' in c]
            supertrend = now[st_cols[0]] if st_cols else close
            
            # Cộng trừ điểm
            if close > supertrend: score += 2 # Trend Tăng
            else: score -= 2                  # Trend Giảm
            
            ema34 = now.get('EMA_34', 0)
            if close > ema34: score += 1
            
            rsi = now.get('RSI_14', 50)
            if rsi < 30: score += 1      # Quá bán (Cơ hội)
            elif rsi > 70: score -= 1    # Quá mua (Rủi ro)
            
            final_score = max(0, min(10, score))
            
            # Dán nhãn tín hiệu
            signal = "NEUTRAL"
            if final_score >= 8: signal = "STRONG BUY"
            elif final_score >= 6: signal = "BUY"
            elif final_score <= 3: signal = "SELL"
            
            # Chuẩn bị dữ liệu vẽ Sparkline (Biểu đồ nhỏ trong bảng)
            trend_list = df['Close'].tail(30).tolist()
            
            rows.append({
                "Symbol": t,
                "Price": close / 1000.0, # Quy đổi ra đơn vị nghìn đồng
                "Pct": (close - df['Close'].iloc[-2]) / df['Close'].iloc[-2],
                "Signal": signal,
                "Score": final_score,
                "Trend": trend_list
            })
            
        except Exception:
            continue
            
    return pd.DataFrame(rows)

# ==============================================================================
# 5. DỮ LIỆU LỊCH SỬ CHO BIỂU ĐỒ (CHART DATA)
# ==============================================================================
def get_history_df(symbol):
    """
    Lấy dữ liệu lịch sử 2 năm để vẽ biểu đồ kỹ thuật chi tiết
    """
    try:
        df = yf.Ticker(f"{symbol}.VN").history(period="2y")
        return df
    except:
        return pd.DataFrame()
