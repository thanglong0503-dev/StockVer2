import pandas_ta as ta

def analyze_smart_v36(df):
    """Logic phân tích kỹ thuật chuẩn V36 (Code gốc của lão đại)"""
    if df.empty or len(df) < 50: return None
    
    # Tính chỉ báo
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    if sti is not None: df = df.join(sti)
    df.ta.ema(length=34, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    
    now = df.iloc[-1]
    close = now['Close']
    
    # Lấy giá trị
    st_col = [c for c in df.columns if 'SUPERT' in c][0]
    supertrend = now[st_col]
    bb_upper = now.get('BBU_20_2.0', 0)
    bb_lower = now.get('BBL_20_2.0', 0)
    bb_mid = now.get('BBM_20_2.0', close)
    bandwidth = (bb_upper - bb_lower) / bb_mid if bb_mid > 0 else 0
    
    score = 0; pros = []; cons = []
    
    # 1. Bollinger Bands
    if bandwidth < 0.10: 
        pros.append("⚡ Bollinger: Nút thắt cổ chai")
        if close > bb_upper: score += 2; pros.append("=> Breakout Lên!")
    
    # 2. Supertrend
    if close > supertrend: score += 2; pros.append("SuperTrend: BÁO TĂNG")
    else: score -= 2; cons.append("SuperTrend: BÁO GIẢM")
    
    # 3. RSI
    rsi = now.get('RSI_14', 50)
    if rsi < 30: score += 1; pros.append(f"RSI ({rsi:.0f}): Quá bán -> Dễ hồi")
    elif rsi > 70: score -= 1; cons.append(f"RSI ({rsi:.0f}): Quá mua -> Cẩn thận")
    
    # Tổng kết
    final_score = max(0, min(10, 5 + score))
    
    # Màu sắc và hành động
    action, zone_color = "QUAN SÁT", "#f59e0b" # Vàng
    if final_score >= 8: action, zone_color = "MUA MẠNH", "#10b981" # Xanh lá
    elif final_score <= 3: action, zone_color = "BÁN / CẮT LỖ", "#ef4444" # Đỏ
    
    return {
        "score": final_score, "action": action, "color": zone_color,
        "pros": pros, "cons": cons,
        "entry": close, "stop": close * 0.93, "target": close * 1.15
    }

def analyze_fundamental(info, fin):
    """Phân tích cơ bản (PE, ROE, Tăng trưởng)"""
    score = 0; details = []
    
    pe = info.get('trailingPE')
    roe = info.get('returnOnEquity')
    mkt_cap = info.get('marketCap', 0)
    
    # PE Logic
    if pe:
        if 0 < pe < 15: score += 2; details.append(f"P/E Hấp dẫn ({pe:.1f}x)")
        elif pe >= 15: details.append(f"⚠️ P/E Khá cao ({pe:.1f}x)")
    
    # ROE Logic
    if roe:
        if roe > 0.15: score += 2; details.append(f"ROE Xuất sắc ({roe*100:.1f}%)")
        elif roe > 0.10: score += 1; details.append(f"ROE Ổn định ({roe*100:.1f}%)")
    
    # Growth Logic (Từ BCTC)
    if not fin.empty:
        try:
            net_now = fin.iloc[0, 0] # Lợi nhuận quý gần nhất
            net_prev = fin.iloc[0, 1] # Quý trước
            growth = (net_now - net_prev) / abs(net_prev)
            if growth > 0.1: score += 2; details.append(f"🚀 LN Tăng trưởng ({growth:.1%})")
        except: pass

    # Xếp hạng
    health, color = "TRUNG BÌNH", "#f59e0b"
    if score >= 5: health, color = "KIM CƯƠNG 💎", "#10b981"
    elif score >= 3: health, color = "VỮNG MẠNH 💪", "#3b82f6"
    elif score < 3: health, color = "YẾU KÉM ⚠️", "#ef4444"
    
    return {"health": health, "color": color, "details": details, "market_cap": mkt_cap}
