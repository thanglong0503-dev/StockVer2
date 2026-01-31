import pandas_ta as ta
import pandas as pd

def analyze_smart_v36(df):
    """V36.1 Logic: SuperTrend + RSI + EMA (International English)"""
    if df.empty or len(df) < 50: return None
    
    # 1. CALCULATE INDICATORS
    # Supertrend
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    if sti is not None: df = df.join(sti)
    
    # RSI & EMA
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=34, append=True)
    
    # Get latest candle
    now = df.iloc[-1]
    close = now['Close']
    
    # Find Supertrend column
    st_cols = [c for c in df.columns if 'SUPERT' in c]
    if not st_cols: return None
    supertrend = now[st_cols[0]]
    
    # 2. SCORING SYSTEM
    score = 5
    pros, cons = [], []
    
    # Rule 1: SuperTrend
    if close > supertrend: 
        score += 2
        pros.append("SuperTrend: BULLISH Trend")
    else: 
        score -= 2
        cons.append("SuperTrend: BEARISH Trend")
    
    # Rule 2: RSI
    rsi = now.get('RSI_14', 50)
    if rsi < 30: 
        score += 1
        pros.append(f"RSI ({rsi:.0f}): Oversold -> Potential Rebound")
    elif rsi > 70: 
        score -= 1
        cons.append(f"RSI ({rsi:.0f}): Overbought -> Correction Risk")
    
    # Rule 3: EMA34
    ema34 = now.get('EMA_34', 0)
    if close > ema34: 
        score += 1
        pros.append("Price above EMA34 (Good Short-term)")
    
    # Finalize
    final_score = max(0, min(10, score))
    
    # Classify Action
    action = "NEUTRAL"
    color = "#f59e0b" # Amber
    
    if final_score >= 8: action, color = "STRONG BUY", "#10b981" # Green
    elif final_score <= 3: action, color = "STRONG SELL", "#ef4444" # Red
    elif final_score >= 6: action, color = "BUY", "#3b82f6" # Blue
    elif final_score <= 4: action, color = "SELL", "#ef4444"
    
    return {
        "score": final_score, 
        "action": action, 
        "color": color,
        "pros": pros, 
        "cons": cons,
        "stop_loss": close * 0.93,
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
