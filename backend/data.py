# backend/data.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_pro_data(tickers):
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
                if df.empty: continue
                
                # --- 1. TÍNH CHỈ BÁO (ALGO V36.1) ---
                # SuperTrend
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                df = df.join(sti)
                st_col = [c for c in df.columns if 'SUPERT' in c][0]
                
                # RSI & EMA
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema34 = ta.ema(df['Close'], length=34).iloc[-1]
                
                # --- 2. LOGIC CHẤM ĐIỂM ---
                close = df['Close'].iloc[-1]
                supertrend = df[st_col].iloc[-1]
                
                score = 5
                signal = "NEUTRAL"
                
                if close > supertrend: score += 2
                else: score -= 2
                
                if rsi < 30: score += 1 # Quá bán (Bullish)
                elif rsi > 70: score -= 1 # Quá mua (Bearish)
                
                if close > ema34: score += 1
                
                final_score = max(0, min(10, score))
                if final_score >= 7: signal = "STRONG BUY"
                elif final_score <= 3: signal = "SELL"
                
                # --- 3. ĐÓNG GÓI DATA ---
                rows.append({
                    "Symbol": t,
                    "Price": float(close) / 1000.0,
                    "Change": float(close - df['Close'].iloc[-2]) / 1000.0,
                    "Pct": float((close - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100),
                    "RSI": float(rsi),
                    "Signal": signal,
                    "Score": final_score,
                    "Trend": df['Close'].tail(30).tolist() # Để vẽ chart
                })
            except: continue
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

def get_history_df(symbol):
    """Hàm lấy lịch sử để chạy AI"""
    return yf.Ticker(f"{symbol}.VN").history(period="2y")
