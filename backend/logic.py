import pandas_ta as ta
import pandas as pd

def analyze_smart_v36(df):
    """
    T.M.V Logic (Trend - Momentum - Volume)
    International Standard Scoring System (0-10)
    """
    if df.empty or len(df) < 50: return None
    
    # --- 1. CALCULATE INDICATORS ---
    # Supertrend
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    if sti is not None: df = df.join(sti)
    
    # RSI, EMA, ATR
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=34, append=True)
    df.ta.ema(length=89, append=True) # Thêm đường trung hạn
    
    # Volume SMA
    vol_sma = df['Volume'].rolling(window=20).mean()
    
    # Get latest candle data
    now = df.iloc[-1]
    close = now['Close']
    vol_now = now['Volume']
    vol_avg = vol_sma.iloc[-1]
    
    # Find Supertrend column
    st_cols = [c for c in df.columns if 'SUPERT' in c]
    if not st_cols: return None
    supertrend = now[st_cols[0]]
    
    # --- 2. SCORING ENGINE (BASE 3 POINTS) ---
    score = 3 
    pros, cons = [], []
    
    # LAYER 1: TREND (The King)
    if close > supertrend: 
        score += 3 # SuperTrend quan trọng nhất
        pros.append("SuperTrend: BULLISH")
    else: 
        cons.append("SuperTrend: BEARISH")
        
    if close > now.get('EMA_34', 0): 
        score += 1
        pros.append("Price > EMA34 (Short-term Uptrend)")
        
    if close > now.get('EMA_89', 0): 
        score += 1
        pros.append("Price > EMA89 (Mid-term Support)")

    # LAYER 2: MOMENTUM (The Engine)
    rsi = now.get('RSI_14', 50)
    if 50 <= rsi <= 70:
        score += 1
        pros.append(f"RSI {rsi:.0f}: Strong Bullish Zone")
    elif rsi < 30:
        score += 1
        pros.append(f"RSI {rsi:.0f}: Oversold (Dip Buy Opportunity)")
    elif rsi > 75:
        score -= 1
        cons.append(f"RSI {rsi:.0f}: Overbought (Risk of correction)")
        
    # LAYER 3: VOLUME (The Fuel)
    if vol_now > vol_avg:
        score += 1
        pros.append("Volume > Avg 20 Days (High Demand)")
    elif vol_now < vol_avg * 0.5:
        cons.append("Low Volume (Weak Interest)")
    
    # --- 3. FINALIZE ---
    final_score = max(0, min(10, score))
    
    # Classify Action (International Standard)
    action = "NEUTRAL"
    color = "#64748b" # Slate (Grey)
    
    if final_score >= 9: action, color = "STRONG BUY", "#22c55e"    # Neon Green
    elif final_score >= 7: action, color = "BUY", "#3b82f6"           # Blue
    elif final_score <= 2: action, color = "STRONG SELL", "#ef4444"   # Red
    elif final_score <= 4: action, color = "SELL", "#f97316"          # Orange
    else: action, color = "NEUTRAL", "#eab308"                        # Yellow
    
    return {
        "score": final_score, 
        "action": action, 
        "color": color,
        "pros": pros, 
        "cons": cons,
        "stop_loss": close * 0.95,
        "take_profit": close * 1.15
    }

def analyze_fundamental_fake(symbol):
    """Mock Fundamental Data (English)"""
    return {
        "health": "EXCELLENT 💎", 
        "health_color": "#3b82f6", 
        "pe": "14.5x", 
        "roe": "18.2%", 
        "growth": "+25% YoY"
    }
