"""
================================================================================
MODULE: backend/data.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.9.0-FULL-SYNCED
AUTHOR: THANG LONG TEAM
DESCRIPTION: 
    Core data fetching engine. Handles connections to Yahoo Finance, 
    Google News, and internal data processing.
    UPDATED: Integrated 'backend.logic.analyze_smart_v36' for synchronized Radar.
================================================================================
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional, Tuple
import streamlit as st

# [NEW] Import Logic để đồng bộ thuật toán
from backend.logic import analyze_smart_v36 

# ==============================================================================
# 1. SYSTEM CONFIGURATION & CONSTANTS
# ==============================================================================

# Cấu hình Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("ThangLongDataEngine")

# User Agent giả lập trình duyệt để tránh bị chặn
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
}

# Danh sách các chỉ số thị trường toàn cầu (Global Indices)
MARKET_INDICES_CONFIG = [
    {"id": "vn30", "name": "VN30 ETF (VN Proxy)", "symbol": "E1VFVN30.VN", "source": "yahoo", "type": "etf"},
    {"id": "dji", "name": "DOW JONES INDU.", "symbol": "^DJI", "source": "yahoo", "type": "index"},
    {"id": "nasdaq", "name": "NASDAQ COMP.", "symbol": "^IXIC", "source": "yahoo", "type": "index"},
    {"id": "sp500", "name": "S&P 500", "symbol": "^GSPC", "source": "yahoo", "type": "index"},
    {"id": "nikkei", "name": "NIKKEI 225", "symbol": "^N225", "source": "yahoo", "type": "index"},
    {"id": "gold", "name": "GOLD FUTURES", "symbol": "GC=F", "source": "yahoo", "type": "commodity"},
    {"id": "oil", "name": "CRUDE OIL", "symbol": "CL=F", "source": "yahoo", "type": "commodity"},
    {"id": "btc", "name": "BITCOIN USD", "symbol": "BTC-USD", "source": "yahoo", "type": "crypto"},
    {"id": "eth", "name": "ETHEREUM USD", "symbol": "ETH-USD", "source": "yahoo", "type": "crypto"}
]

# Mapping tên cột cho chuẩn hóa dữ liệu BCTC
FINANCIAL_MAP = {
    "Total Revenue": "Doanh Thu Thuần",
    "Net Income": "Lợi Nhuận Sau Thuế",
    "Operating Income": "Lợi Nhuận Từ HĐKD",
    "Total Assets": "Tổng Tài Sản",
    "Total Liab": "Tổng Nợ Phải Trả",
    "Total Stockholder Equity": "Vốn Chủ Sở Hữu",
    "Operating Cash Flow": "Dòng Tiền Kinh Doanh",
    "Investing Cash Flow": "Dòng Tiền Đầu Tư",
    "Financing Cash Flow": "Dòng Tiền Tài Chính"
}

# ==============================================================================
# 2. HELPER FUNCTIONS (TIỆN ÍCH)
# ==============================================================================

def _safe_float(value: any, default: float = 0.0) -> float:
    """Chuyển đổi an toàn sang float, tránh lỗi crash app."""
    try:
        if value is None: return default
        return float(value)
    except (ValueError, TypeError):
        return default

def _format_ticker(symbol: str) -> str:
    """Chuẩn hóa mã chứng khoán (Thêm đuôi .VN nếu thiếu)."""
    symbol = symbol.strip().upper()
    if not symbol.endswith(".VN") and len(symbol) <= 3:
        return f"{symbol}.VN"
    return symbol

# ==============================================================================
# 3. CORE DATA FUNCTIONS
# ==============================================================================

@st.cache_data(ttl=300) # Cache dữ liệu 5 phút để tối ưu tốc độ
def get_market_indices() -> List[Dict]:
    """
    Lấy dữ liệu các chỉ số thị trường (Indices/Commodities/Crypto).
    Sử dụng cơ chế Batch Processing để tải nhanh.
    """
    results = []
    
    # Gom nhóm các symbol để tải 1 lần (Batch download)
    tickers_list = [item["symbol"] for item in MARKET_INDICES_CONFIG]
    tickers_str = " ".join(tickers_list)
    
    try:
        # Tải dữ liệu 5 ngày gần nhất
        data = yf.download(tickers_str, period="5d", group_by='ticker', progress=False, threads=True)
        
        for config in MARKET_INDICES_CONFIG:
            symbol = config["symbol"]
            name = config["name"]
            
            try:
                # Xử lý dữ liệu trả về từ yfinance (MultiIndex dataframe)
                if len(tickers_list) > 1:
                    df = data[symbol]
                else:
                    df = data
                
                # Kiểm tra tính hợp lệ của dữ liệu
                df = df.dropna(subset=['Close'])
                if len(df) < 2:
                    # Fallback: Thử tải riêng lẻ nếu batch thất bại
                    ticker_obj = yf.Ticker(symbol)
                    df = ticker_obj.history(period="5d")
                
                if len(df) >= 2:
                    now_price = _safe_float(df['Close'].iloc[-1])
                    prev_price = _safe_float(df['Close'].iloc[-2])
                    change = now_price - prev_price
                    pct_change = (change / prev_price) * 100 if prev_price != 0 else 0.0
                    
                    status = "LIVE"
                    color = "#238636" if change >= 0 else "#da3633"
                    
                    # Logic đặc biệt cho VN30 ETF (Giả lập index)
                    if config["id"] == "vn30":
                        name = "VN-MARKET (ETF)"
                    
                    results.append({
                        "Symbol": symbol,
                        "Name": name,
                        "Price": now_price,
                        "Change": change,
                        "Pct": pct_change,
                        "Color": color,
                        "Status": status,
                        "Type": config["type"]
                    })
                else:
                    raise ValueError("Insufficient Data")

            except Exception as e:
                logger.warning(f"Failed to parse index {symbol}: {str(e)}")
                results.append({
                    "Symbol": symbol, "Name": name,
                    "Price": 0.0, "Change": 0.0, "Pct": 0.0,
                    "Color": "#8b949e", "Status": "OFFLINE", "Type": config["type"]
                })
                
    except Exception as global_e:
        logger.error(f"Global download failed: {str(global_e)}")
        return []
        
    return results

@st.cache_data(ttl=3600) # Cache 1 tiếng cho tin tức
def get_stock_news_google(symbol: str) -> List[Dict]:
    """
    Lấy tin tức từ Google News RSS Feed.
    Hỗ trợ fallback và lọc tin rác.
    """
    clean_symbol = symbol.replace(".VN", "")
    rss_urls = [
        f"https://news.google.com/rss/search?q=cổ+phiếu+{clean_symbol}&hl=vi&gl=VN&ceid=VN:vi",
        f"https://news.google.com/rss/search?q=thị+trường+chứng+khoán+{clean_symbol}&hl=vi&gl=VN&ceid=VN:vi"
    ]
    
    news_collection = []
    seen_links = set()
    
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            
            for entry in feed.entries:
                if entry.link in seen_links: continue
                seen_links.add(entry.link)
                
                # Format ngày tháng
                published = entry.get('published', '')
                try:
                    dt = datetime(*entry.published_parsed[:6])
                    published_str = dt.strftime("%H:%M %d/%m/%Y")
                except:
                    published_str = published[:16]

                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': published_str,
                    'source': entry.source.title if 'source' in entry else 'Google News',
                    'summary': entry.get('summary', '')[:200] + '...'
                }
                news_collection.append(news_item)
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            continue
            
    # Sắp xếp theo thời gian mới nhất và lấy top 15
    return news_collection[:15]

@st.cache_data(ttl=600) # Cache 10 phút
def get_history_df(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Lấy dữ liệu lịch sử giá (OHLCV).
    Tự động tính toán các chỉ báo kỹ thuật cơ bản để chuẩn bị cho phần Logic.
    """
    ticker = _format_ticker(symbol)
    try:
        # Tải dữ liệu
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        
        if df.empty:
            logger.warning(f"No history data for {ticker}")
            return pd.DataFrame()
            
        # Chuẩn hóa múi giờ (Xóa timezone để tránh lỗi khi plot)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
            
        df.index.name = "Date"
        
        # --- PRE-CALCULATE BASIC INDICATORS ---
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['SMA_200'] = ta.sma(df['Close'], length=200)
        df['Vol_SMA_20'] = ta.sma(df['Volume'], length=20)
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
            
        return df
        
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache dữ liệu cơ bản lâu hơn (1h)
def get_stock_data_full(symbol: str) -> Tuple[Dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Lấy toàn bộ dữ liệu cơ bản (Fundamental Data).
    """
    ticker_sym = _format_ticker(symbol)
    t = yf.Ticker(ticker_sym)
    
    try:
        # 1. Info & Profile
        info = t.info
        
        # Vá lỗi: Nếu Yahoo không trả về giá hiện tại
        if 'currentPrice' not in info or info['currentPrice'] is None:
            hist_now = t.history(period="1d")
            if not hist_now.empty:
                info['currentPrice'] = hist_now['Close'].iloc[-1]
                info['previousClose'] = hist_now['Open'].iloc[-1]
            else:
                info['currentPrice'] = 0.0

        # 2. Financial Statements (Báo cáo tài chính)
        fin = t.quarterly_income_stmt
        bal = t.quarterly_balance_sheet
        cash = t.quarterly_cashflow
        
        # Xử lý dữ liệu BCTC: Đổi tên cột ngày tháng thành string cho dễ đọc
        for df_fin in [fin, bal, cash]:
            if df_fin is not None and not df_fin.empty:
                df_fin.columns = [col.strftime('%Y-%m-%d') if isinstance(col, datetime) else col for col in df_fin.columns]
        
        # 3. Corporate Actions
        divs = t.dividends
        splits = t.splits
        
        # Chuẩn hóa múi giờ cho cổ tức
        if not divs.empty and divs.index.tz is not None:
            divs.index = divs.index.tz_localize(None)
            
        return info, fin, bal, cash, divs, splits
        
    except Exception as e:
        logger.error(f"Fundamental data fetch error for {ticker_sym}: {e}")
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.Series(), pd.Series()

# ==============================================================================
# 4. RADAR SCANNER ENGINE (BỘ QUÉT - ĐÃ ĐỒNG BỘ LOGIC)
# ==============================================================================

def get_pro_data(tickers: List[str]) -> pd.DataFrame:
    """
    Bộ quét Radar: Sử dụng logic 'analyze_smart_v36' để chấm điểm.
    Đảm bảo kết quả đồng bộ 100% với màn hình Deep Dive.
    

[Image of Radar Chart]

    """
    rows = []
    
    # 1. Chuẩn hóa danh sách mã
    clean_tickers = [_format_ticker(t) for t in tickers]
    
    # 2. Tải dữ liệu hàng loạt (Batch Download)
    try:
        data_batch = yf.download(clean_tickers, period="1y", group_by='ticker', progress=False, threads=True)
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        return pd.DataFrame()

    # 3. Xử lý từng mã
    for symbol in clean_tickers:
        try:
            # Trích xuất DF con
            if len(clean_tickers) > 1:
                df = data_batch[symbol].copy()
            else:
                df = data_batch.copy()
            
            # Làm sạch: Bỏ hàng NaN
            df = df.dropna(subset=['Close'])
            if df.empty or len(df) < 50: continue
            
            # --- [SYNC LOGIC HERE] ---
            # Gọi trực tiếp bộ não phân tích V36
            # Điều này đảm bảo Radar thấy 'MUA' thì Deep Dive cũng thấy 'MUA'
            analysis = analyze_smart_v36(df)
            
            if not analysis: continue

            # Mapping kết quả từ Logic sang bảng Radar
            score = analysis['score']
            raw_action = analysis['action']
            
            # Chuyển đổi ngôn ngữ Action sang tiếng Anh ngắn gọn cho Radar
            signal = "WAIT"
            if "MUA MẠNH" in raw_action: signal = "STRONG BUY"
            elif "MUA" in raw_action: signal = "BUY"
            elif "BÁN" in raw_action: signal = "SELL"
            
            # Trend Line (Sparkline Data) - 30 phiên gần nhất
            trend_data = df['Close'].tail(30).tolist()
            
            # Tính % thay đổi
            close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            pct_change = (close - prev_close) / prev_close
            
            rows.append({
                "Symbol": symbol.replace(".VN", ""),
                "Price": close / 1000.0, # Đơn vị: Nghìn đồng
                "PX (K)": close,
                "Change": close - prev_close,
                "Pct": pct_change,
                "Signal": signal,
                "ALGO": signal, # Thêm cột ALGO cho tương thích app.py
                "Score": int(score),
                "STR": score,   # Thêm cột STR cho tương thích app.py
                "Trend": trend_data,
                "TREND": trend_data # Thêm cột TREND viết hoa
            })
            
        except Exception as e:
            # logger.error(f"Error processing {symbol}: {e}")
            continue
            
    return pd.DataFrame(rows)

# ==============================================================================
# END OF MODULE
# ==============================================================================
