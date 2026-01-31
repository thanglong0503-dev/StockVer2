import pandas_ta as ta
import pandas as pd

def analyze_smart_v36(df):
    """Logic chấm điểm V36.1: SuperTrend + RSI + EMA"""
    if df.empty or len(df) < 50: return None
    
    # 1. TÍNH CHỈ BÁO
    # Supertrend (Quan trọng nhất)
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    # Nếu thư viện trả về kết quả, nối vào DF
    if sti is not None: df = df.join(sti)
    
    # RSI & EMA
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=34, append=True)
    
    # Lấy nến mới nhất
    now = df.iloc[-1]
    close = now['Close']
    
    # Tìm tên cột Supertrend (Vì nó sinh tên động dạng SUPERT_10_3.0)
    st_cols = [c for c in df.columns if 'SUPERT' in c]
    if not st_cols: return None # Phòng hờ lỗi
    supertrend = now[st_cols[0]]
    
    # 2. CHẤM ĐIỂM
    score = 5 # Điểm gốc
    pros, cons = [], []
    
    # Rule 1: SuperTrend
    if close > supertrend: 
        score += 2
        pros.append("SuperTrend: BÁO TĂNG (Bullish)")
    else: 
        score -= 2
        cons.append("SuperTrend: BÁO GIẢM (Bearish)")
    
    # Rule 2: RSI
    rsi = now.get('RSI_14', 50)
    if rsi < 30: 
        score += 1
        pros.append(f"RSI ({rsi:.0f}): Quá bán -> Dễ hồi phục")
    elif rsi > 70: 
        score -= 1
        cons.append(f"RSI ({rsi:.0f}): Quá mua -> Cẩn thận chỉnh")
    
    # Rule 3: EMA34 (Xu hướng trung hạn)
    ema34 = now.get('EMA_34', 0)
    if close > ema34: 
        score += 1
        pros.append("Giá nằm trên EMA34")
    
    # Tổng kết
    final_score = max(0, min(10, score))
    
    # Phân loại màu sắc & hành động
    action = "QUAN SÁT"
    color = "#f59e0b" # Vàng (Neutral)
    
    if final_score >= 8: action, color = "MUA MẠNH", "#10b981" # Xanh (Buy)
    elif final_score <= 3: action, color = "BÁN / CẮT LỖ", "#ef4444" # Đỏ (Sell)
    
    return {
        "score": final_score, 
        "action": action, 
        "color": color,
        "pros": pros, 
        "cons": cons,
        "stop_loss": close * 0.93,   # Cắt lỗ 7%
        "take_profit": close * 1.15  # Chốt lời 15%
    }

def analyze_fundamental_fake(symbol):
    """Giả lập số liệu cơ bản để hiển thị cho đẹp"""
    return {
        "health": "VỮNG MẠNH 💪", 
        "health_color": "#3b82f6", # Xanh dương
        "pe": "14.5x", 
        "roe": "18.2%", 
        "growth": "25%"
    }
