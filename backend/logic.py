# backend/logic.py
import yfinance as yf
import pandas_ta as ta
import pandas as pd

def get_stock_data_frame(symbol):
    try:
        # Lấy dữ liệu 1 năm
        df = yf.Ticker(f"{symbol}.VN").history(period="1y")
        if df.empty: return None
        
        # --- CÔNG THỨC V36.1 ---
        # 1. Supertrend
        sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
        if sti is not None: df = df.join(sti)
        
        # 2. Các chỉ báo khác
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=34, append=True)
        df.ta.atr(length=14, append=True)
        
        return df
    except: return None

def scoring_system(df):
    if df is None: return None
    now = df.iloc[-1]
    close = now['Close']
    
    # Tìm cột Supertrend (vì tên cột sinh động)
    st_cols = [c for c in df.columns if 'SUPERT' in c]
    supertrend = now[st_cols[0]] if st_cols else close
    rsi = now.get('RSI_14', 50)
    ema34 = now.get('EMA_34', 0)
    atr = now.get('ATRr_14', 0)
    
    score = 5
    reasons = []
    
    # Logic chấm điểm
    if close > supertrend: score += 2; reasons.append("✅ SuperTrend Báo Tăng")
    else: score -= 2; reasons.append("🔻 SuperTrend Báo Giảm")
    
    if rsi < 30: score += 1; reasons.append("✅ RSI Quá bán (Dễ hồi phục)")
    elif rsi > 70: score -= 1; reasons.append("⚠️ RSI Quá mua (Cẩn thận)")
    
    if close > ema34: score += 1; reasons.append("✅ Giá nằm trên EMA34")
    
    final_score = max(0, min(10, score))
    
    # Kết luận
    action = "QUAN SÁT"
    color = "yellow"
    if final_score >= 8: action, color = "MUA MẠNH", "green"
    elif final_score <= 3: action, color = "BÁN", "red"
    
    return {
        "price": close,
        "score": final_score,
        "action": action,
        "color": color,
        "reasons": reasons,
        "stop_loss": close - 2*atr,
        "take_profit": close + 3*atr
    }
