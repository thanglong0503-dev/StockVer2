# backend/data.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

def get_pro_data(tickers):
    # Định dạng mã
    symbols = [f"{t}.VN" for t in tickers]
    try:
        # Lấy data 1 năm để đủ tính chỉ báo
        data = yf.download(symbols, period="1y", interval="1d", group_by='ticker', progress=False)
        
        rows = []
        for t in tickers:
            sym = f"{t}.VN"
            try:
                # Xử lý MultiIndex
                df = data[sym] if len(tickers) > 1 else data
                if df.empty or len(df) < 50: continue
                
                # --- 1. TÍNH CHỈ BÁO (CORE V36.1) ---
                # SuperTrend
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                # Ghép Supertrend vào DF
                df = df.join(sti)
                # Tìm tên cột Supertrend (vì nó sinh tên động dạng SUPERT_10_3.0)
                st_col = [c for c in df.columns if 'SUPERT' in c][0]
                
                # RSI & EMA
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema34 = ta.ema(df['Close'], length=34).iloc[-1]
                
                # --- 2. LOGIC CHẤM ĐIỂM ---
                close_now = float(df['Close'].iloc[-1])
                close_prev = float(df['Close'].iloc[-2])
                supertrend_val = df[st_col].iloc[-1]
                
                score = 5
                signal = "NEUTRAL"
                
                # Logic SuperTrend
                if close_now > supertrend_val: score += 2
                else: score -= 2
                
                # Logic RSI
                if rsi < 30: score += 1 # Quá bán (Bullish)
                elif rsi > 70: score -= 1 # Quá mua (Bearish)
                
                # Logic EMA
                if close_now > ema34: score += 1
                
                final_score = max(0, min(10, score))
                
                if final_score >= 8: signal = "STRONG BUY"
                elif final_score >= 6: signal = "BUY"
                elif final_score <= 2: signal = "STRONG SELL"
                elif final_score <= 4: signal = "SELL"
                
                # --- 3. CHUẨN BỊ DATA CHO TABLE ---
                # Fix lỗi chart: Chuyển Series thành List Float chuẩn Python
                trend_list = df['Close'].tail(30).tolist()
                trend_list = [float(x) for x in trend_list]

                rows.append({
                    "Symbol": t,
                    "Price": close_now / 1000.0,
                    "Change": (close_now - close_prev) / 1000.0,
                    "Pct": ((close_now - close_prev) / close_prev), # Để dạng số thập phân (0.015) để column_config format
                    "RSI": float(rsi),
                    "Signal": signal,
                    "Score": final_score, # Giữ nguyên thang 10
                    "Trend": trend_list 
                })
            except Exception as e:
                continue
                
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

def get_history_df(symbol):
    """Hàm lấy lịch sử để chạy AI"""
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
