import pandas_ta as ta
import pandas as pd
import numpy as np

# ==============================================================================
# 1. PHÂN TÍCH KỸ THUẬT (TECHNICAL ANALYSIS V36.1)
# ==============================================================================
def analyze_smart_v36(df):
    """
    Bộ logic chấm điểm kỹ thuật V36.1 Ultimate.
    Kết hợp: SuperTrend + Bollinger Bands + RSI + MACD + EMA System.
    Trả về: Điểm số (0-10), Hành động, Màu sắc, Lý do (Pros/Cons).
    """
    # Kiểm tra dữ liệu đầu vào
    if df.empty or len(df) < 50: return None
    
    # --- A. TÍNH TOÁN CHỈ BÁO (CALCULATE INDICATORS) ---
    
    # 1. Supertrend (Trend Following)
    # Length=10, Multiplier=3 (Cấu hình chuẩn)
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    if sti is not None: df = df.join(sti)
    
    # 2. Bollinger Bands (Volatility)
    df.ta.bbands(length=20, std=2, append=True)
    
    # 3. RSI (Momentum)
    df.ta.rsi(length=14, append=True)
    
    # 4. MACD (Trend Reversal)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # 5. EMA (Moving Averages)
    df.ta.ema(length=34, append=True)
    df.ta.ema(length=89, append=True)
    
    # 6. Volume SMA (Dòng tiền)
    # Tính trung bình Volume 20 phiên để so sánh
    vol_sma = df['Volume'].rolling(window=20).mean()
    
    # --- B. LẤY DỮ LIỆU NẾN HIỆN TẠI (LATEST CANDLE) ---
    now = df.iloc[-1]
    prev = df.iloc[-2]
    close = now['Close']
    
    # Lấy tên cột động (Do thư viện pandas_ta sinh ra)
    # Supertrend
    st_col = [c for c in df.columns if 'SUPERT' in c][0]
    supertrend = now[st_col]
    
    # Bollinger Bands
    bb_upper = now.get('BBU_20_2.0', 0)
    bb_lower = now.get('BBL_20_2.0', 0)
    bb_mid = now.get('BBM_20_2.0', close)
    
    # RSI & MACD
    rsi = now.get('RSI_14', 50)
    macd = now.get('MACD_12_26_9', 0)
    macd_signal = now.get('MACDs_12_26_9', 0)
    
    # EMA
    ema34 = now.get('EMA_34', 0)
    ema89 = now.get('EMA_89', 0)
    
    # --- C. HỆ THỐNG CHẤM ĐIỂM (SCORING ENGINE) ---
    score = 0
    pros = [] # Điểm cộng (Lý do mua)
    cons = [] # Điểm trừ (Lý do bán/cẩn trọng)
    
    # 1. Logic SuperTrend (Quan trọng nhất: +/- 2 điểm)
    if close > supertrend:
        score += 2
        pros.append("SuperTrend: Xu hướng TĂNG (Bullish)")
    else:
        score -= 2
        cons.append("SuperTrend: Xu hướng GIẢM (Bearish)")
        
    # 2. Logic Bollinger Bands (Squeeze & Breakout)
    bandwidth = (bb_upper - bb_lower) / bb_mid if bb_mid > 0 else 0
    
    if bandwidth < 0.10: # Dưới 10% là thắt nút cổ chai
        pros.append("⚡ BB: Nút thắt cổ chai (Sắp biến động mạnh)")
        if close > bb_upper:
            score += 2
            pros.append("=> BREAKOUT: Giá phá dải trên (Mua ngay)")
        elif close < bb_lower:
            score -= 2
            cons.append("=> BREAKDOWN: Giá thủng dải dưới (Bán gấp)")
    else:
        # Nếu không thắt nút, chỉ xét vị thế
        if close > bb_mid: score += 0.5
        else: score -= 0.5
            
    # 3. Logic RSI (Quá mua/Quá bán)
    if 50 <= rsi <= 70:
        score += 1
        pros.append(f"RSI ({rsi:.0f}): Vùng tăng giá mạnh")
    elif rsi < 30:
        score += 1
        pros.append(f"RSI ({rsi:.0f}): Quá bán (Oversold) -> Dễ hồi phục")
    elif rsi > 75:
        score -= 1
        cons.append(f"RSI ({rsi:.0f}): Quá mua (Overbought) -> Cẩn thận chỉnh")
        
    # 4. Logic MACD (Giao cắt vàng)
    if macd > macd_signal:
        score += 1
        # Nếu mới cắt lên trong vòng 2 phiên gần đây
        prev_macd = prev.get('MACD_12_26_9', 0)
        prev_signal = prev.get('MACDs_12_26_9', 0)
        if prev_macd <= prev_signal:
            pros.append("MACD: Cắt lên đường tín hiệu (Golden Cross)")
    else:
        score -= 1
        
    # 5. Logic EMA (Trend dài hạn)
    if close > ema34 and ema34 > ema89:
        score += 1
        pros.append("EMA: Giá nằm trên EMA34 & EMA89 (Uptrend bền)")
    elif close < ema89:
        score -= 1
        cons.append("EMA: Giá nằm dưới EMA89 (Downtrend trung hạn)")

    # 6. Logic Dòng tiền (Volume)
    vol_current = now['Volume']
    vol_avg_val = vol_sma.iloc[-1] if not vol_sma.empty else vol_current
    
    if vol_current > 1.3 * vol_avg_val and close > prev['Close']:
        score += 1
        pros.append("Volume: Nổ Vôn (Tiền vào mạnh)")
    
    # --- D. TỔNG KẾT & KHUYẾN NGHỊ ---
    # Chuẩn hóa điểm về thang 10 (Base = 5)
    final_score = 5 + score
    final_score = max(0, min(10, final_score))
    
    # Phân loại hành động
    action = "QUAN SÁT"
    color = "#f59e0b" # Vàng (Neutral)
    
    if final_score >= 8: 
        action = "MUA MẠNH 💎"
        color = "#10b981" # Xanh lá
    elif final_score >= 6:
        action = "MUA THĂM DÒ"
        color = "#3b82f6" # Xanh dương
    elif final_score <= 3:
        action = "BÁN / CẮT LỖ"
        color = "#ef4444" # Đỏ
        
    # Tính toán Entry/Stop/Target gợi ý
    stop_loss = close * 0.93   # Cắt lỗ 7%
    take_profit = close * 1.15 # Chốt lời 15%
    
    return {
        "score": final_score,
        "action": action,
        "color": color,
        "pros": pros,
        "cons": cons,
        "entry": close,
        "stop": stop_loss,
        "target": take_profit
    }

# ==============================================================================
# 2. PHÂN TÍCH CƠ BẢN (FUNDAMENTAL ANALYSIS)
# ==============================================================================
def analyze_fundamental(info, fin):
    """
    Phân tích sức khỏe doanh nghiệp dựa trên:
    - Định giá: P/E, P/B
    - Hiệu quả: ROE
    - Tăng trưởng: Net Income Growth (so với quý trước)
    """
    score = 0
    details = []
    
    # 1. Lấy dữ liệu (xử lý None nếu Yahoo lỗi)
    pe = info.get('trailingPE')
    pb = info.get('priceToBook')
    roe = info.get('returnOnEquity')
    mkt_cap = info.get('marketCap', 0)
    
    # 2. Đánh giá P/E (Định giá)
    if pe:
        if 0 < pe < 15:
            score += 2
            details.append(f"P/E Hấp dẫn ({pe:.1f}x) - Rẻ hơn trung bình")
        elif pe > 25:
            score -= 1
            details.append(f"⚠️ P/E Khá cao ({pe:.1f}x)")
        else:
            details.append(f"P/E Hợp lý ({pe:.1f}x)")
            
    # 3. Đánh giá ROE (Hiệu quả sử dụng vốn)
    if roe:
        roe_pct = roe * 100
        if roe_pct > 15:
            score += 2
            details.append(f"ROE Xuất sắc ({roe_pct:.1f}%) - Sinh lời tốt")
        elif roe_pct > 10:
            score += 1
            details.append(f"ROE Ổn định ({roe_pct:.1f}%)")
        else:
            details.append(f"⚠️ ROE Thấp ({roe_pct:.1f}%)")
            
    # 4. Đánh giá P/B
    if pb and pb < 1.5:
        score += 1
        details.append(f"P/B Thấp ({pb:.1f}x) - Tài sản an toàn")
        
    # 5. Đánh giá Tăng trưởng (Growth) từ BCTC Quý
    if not fin.empty and len(fin.columns) >= 2:
        try:
            # Lấy lợi nhuận sau thuế (Net Income)
            # Yahoo thường trả về hàng 'Net Income' hoặc tương tự
            # Ta lấy hàng đầu tiên (Quý gần nhất) và hàng thứ 2 (Quý trước)
            net_income_now = fin.iloc[0, 0] 
            net_income_prev = fin.iloc[0, 4] # So với cùng kỳ năm trước (thường là cột 4)
            
            # Nếu ko so được cùng kỳ thì so quý liền kề (cột 1)
            if pd.isna(net_income_prev):
                net_income_prev = fin.iloc[0, 1]
                label = "quý trước"
            else:
                label = "cùng kỳ"
            
            if net_income_prev != 0:
                growth = (net_income_now - net_income_prev) / abs(net_income_prev)
                if growth > 0.15: # Tăng trưởng > 15%
                    score += 2
                    details.append(f"🚀 LN Tăng trưởng mạnh ({growth:.1%}) so với {label}")
                elif growth < -0.10: # Giảm > 10%
                    score -= 1
                    details.append(f"⚠️ LN Suy giảm ({growth:.1%}) so với {label}")
        except:
            pass

    # 6. Xếp hạng Sức khỏe
    # Thang điểm cơ bản (Max khoảng 7-8)
    health = "TRUNG BÌNH"
    color = "#f59e0b" # Vàng
    
    if score >= 5:
        health = "KIM CƯƠNG 💎"
        color = "#10b981" # Xanh
    elif score >= 3:
        health = "VỮNG MẠNH 💪"
        color = "#3b82f6" # Blue
    elif score < 2:
        health = "YẾU KÉM ⚠️"
        color = "#ef4444" # Đỏ
        
    return {
        "health": health,
        "color": color,
        "details": details,
        "market_cap": mkt_cap
    }
