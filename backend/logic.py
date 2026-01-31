# --- Copy hàm analyze_smart từ bản cũ vào đây ---
def analyze_technical(df):
    if df is None: return None
    now = df.iloc[-1]
    close = now['Close']
    
    # Lấy tên cột SuperTrend động
    st_col = [c for c in df.columns if 'SUPERT' in c][0]
    supertrend = now[st_col]
    
    score = 5
    pros, cons = [], []
    
    # Logic chấm điểm (Rút gọn từ V36.1)
    if close > supertrend: score += 2; pros.append("SuperTrend Tăng")
    else: score -= 2; cons.append("SuperTrend Giảm")
    
    if now['RSI_14'] < 30: score += 1; pros.append("RSI Quá bán")
    
    final_score = max(0, min(10, score))
    action = "MUA" if final_score >= 8 else ("BÁN" if final_score <= 3 else "QUAN SÁT")
    color = "#10b981" if final_score >= 8 else ("#ef4444" if final_score <= 3 else "#f59e0b")
    
    return {
        "score": final_score, "action": action, "color": color,
        "pros": pros, "cons": cons,
        "price": close
    }
