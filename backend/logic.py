import pandas_ta as ta
import pandas as pd

def analyze_smart_v36(df):
    """Logic chấm điểm cũ của V36.1"""
    if df.empty or len(df) < 50: return None
    now = df.iloc[-1]
    close = now['Close']
    
    # Tính toán lại chỉ báo nếu chưa có
    if 'RSI_14' not in df.columns: df.ta.rsi(length=14, append=True)
    if 'EMA_34' not in df.columns: df.ta.ema(length=34, append=True)
    
    # Supertrend
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    df = df.join(sti)
    st_col = [c for c in df.columns if 'SUPERT' in c][0]
    supertrend = df[st_col].iloc[-1]

    # Logic chấm điểm
    score = 0
    pros, cons = [], []
    
    # 1. Trend
    if close > supertrend: score += 2; pros.append("SuperTrend: BÁO TĂNG")
    else: score -= 2; cons.append("SuperTrend: BÁO GIẢM")
    
    # 2. RSI
    rsi = df['RSI_14'].iloc[-1]
    if rsi < 30: score += 1; pros.append(f"RSI ({rsi:.0f}): Quá bán")
    elif rsi > 70: score -= 1; cons.append(f"RSI ({rsi:.0f}): Quá mua")
    
    # 3. EMA
    ema34 = df['EMA_34'].iloc[-1]
    if close > ema34: score += 1; pros.append("Giá trên EMA34 (Xu hướng ngắn hạn Tốt)")
    
    final_score = max(0, min(10, 5 + score)) # Điểm gốc là 5
    
    # Phân loại
    action, color = "QUAN SÁT", "#f59e0b"
    if final_score >= 8: action, color = "MUA MẠNH", "#10b981"
    elif final_score >= 6: action, color = "MUA THĂM DÒ", "#3b82f6"
    elif final_score <= 3: action, color = "BÁN / CẮT LỖ", "#ef4444"
    
    return {
        "score": final_score, "action": action, "color": color,
        "pros": pros, "cons": cons,
        "stop_loss": close * 0.93, "take_profit": close * 1.1
    }

def analyze_fundamental_fake(symbol):
    """Giả lập phân tích cơ bản (Vì API free không lấy được BCTC chi tiết)"""
    # Logic này mô phỏng lại cái bảng xanh/đỏ trong ảnh bạn gửi
    return {
        "pe": "15.2x (Khá cao)", "pe_color": "warning",
        "roe": "12.1% (Ổn định)", "roe_color": "success",
        "cap": "205,703 tỷ", "cap_color": "success",
        "growth": "LN Tăng trưởng 27.3%", "growth_color": "success",
        "health": "VỮNG MẠNH 💪", "health_color": "#3b82f6"
    }
