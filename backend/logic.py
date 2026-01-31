"""
================================================================================
MODULE: backend/logic.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 40.0.0-ULTIMATE-LOGIC
DESCRIPTION: 
    - Technical Analysis: Multi-indicator (SuperTrend, Ichimoku, RSI...).
      *UPDATE*: Auto-hide Entry/Target when signal is SELL.
    - Fundamental Analysis: Deep Dive into 9 Financial Health Metrics.
      *UPDATE*: Full analysis of Profitability, Solvency, and Growth.
================================================================================
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Tuple, Optional

# ==============================================================================
# 1. TECHNICAL ANALYSIS ENGINE (BỘ MÁY KỸ THUẬT)
# ==============================================================================

class TechnicalAnalyzer:
    """
    Class chuyên dụng để phân tích kỹ thuật sâu.
    Tích hợp: SuperTrend, Ichimoku, Bollinger Bands, RSI, EMA.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.latest = df.iloc[-1] if not df.empty else None

    def validate(self) -> bool:
        """Kiểm tra dữ liệu đầu vào có đủ 50 nến không."""
        return self.df is not None and not self.df.empty and len(self.df) >= 50

    def add_indicators(self) -> pd.DataFrame:
        """Tính toán và nạp chỉ báo vào DataFrame."""
        if not self.validate(): return self.df
        
        # 1. Trend Indicators
        # SuperTrend (10, 3)
        sti = ta.supertrend(self.df['High'], self.df['Low'], self.df['Close'], length=10, multiplier=3)
        if sti is not None: self.df = self.df.join(sti)
        
        # EMA
        self.df.ta.ema(length=34, append=True)
        self.df.ta.ema(length=89, append=True)
        self.df.ta.ema(length=200, append=True)

        # Ichimoku Cloud
        ichimoku = ta.ichimoku(self.df['High'], self.df['Low'], self.df['Close'], tenkan=9, kijun=26, senkou=52)
        if ichimoku is not None: self.df = self.df.join(ichimoku[0])

        # 2. Volatility & Momentum
        self.df.ta.bbands(length=20, std=2, append=True)
        self.df.ta.atr(length=14, append=True)
        self.df.ta.rsi(length=14, append=True)
        
        # Update latest row
        self.latest = self.df.iloc[-1]
        return self.df

    def analyze(self) -> Dict:
        """
        Chấm điểm kỹ thuật (0-10) và đưa ra hành động Mua/Bán.
        """
        if not self.validate(): return {}
        if 'RSI_14' not in self.df.columns: self.add_indicators()
            
        score = 0
        pros = []
        cons = []
        close = self.latest['Close']
        
        # --- A. SCORING LOGIC ---
        
        # 1. SuperTrend (Quan trọng nhất: +/- 2 điểm)
        st_col = [c for c in self.df.columns if 'SUPERT' in c]
        if st_col:
            if close > self.latest[st_col[0]]: 
                score += 2; pros.append("SuperTrend: Uptrend (Tăng)")
            else: 
                score -= 2; cons.append("SuperTrend: Downtrend (Giảm)")
                
        # 2. EMA (Trend dài hạn: +/- 1 điểm)
        ema34 = self.latest.get('EMA_34', 0)
        ema89 = self.latest.get('EMA_89', 0)
        ema200 = self.latest.get('EMA_200', 0)
        
        if close > ema34 > ema89: score += 1; pros.append("EMA: Xếp lớp tăng giá đẹp")
        if close < ema200: score -= 1; cons.append("EMA: Giá dưới MA200 (Dài hạn xấu)")
            
        # 3. Ichimoku (+1 điểm)
        span_a = self.latest.get('ISA_9', 0)
        span_b = self.latest.get('ISB_26', 0)
        if close > span_a and close > span_b: score += 1; pros.append("Ichimoku: Giá nằm trên Mây")
            
        # 4. RSI (+/- 1 điểm)
        rsi = self.latest.get('RSI_14', 50)
        if 50 <= rsi <= 70: score += 0.5
        elif rsi < 30: score += 1.5; pros.append("RSI: Quá bán (Dễ có nhịp hồi)")
        elif rsi > 75: score -= 1.0; cons.append("RSI: Quá mua (Cẩn trọng chỉnh)")
            
        # 5. Bollinger Bands (+2 điểm nếu Breakout)
        bb_upper = self.latest.get('BBU_20_2.0', 0)
        if close > bb_upper: score += 2; pros.append("Bollinger: Breakout dải trên (Tiền vào)")
            
        # --- B. CLASSIFICATION ---
        final_score = max(0, min(10, 5 + score)) # Base score = 5
        
        # Tính toán Entry/Stop/Target theo ATR
        atr = self.latest.get('ATRr_14', close * 0.02)
        entry_price = close
        stop_loss = close - (2 * atr)
        take_profit = close + (4 * atr)

        action = "QUAN SÁT"
        color = "#fcee0a" # Vàng

        if final_score >= 8:
            action = "MUA MẠNH 💎"; color = "#00ff41" # Xanh Matrix
        elif final_score >= 6:
            action = "MUA (BUY)"; color = "#00f3ff" # Xanh Cyan
        elif final_score <= 4:
            action = "BÁN / CẮT LỖ"; color = "#ff0055" # Đỏ
            # [LOGIC MỚI] Nếu báo Bán, reset các mốc về 0 để ẩn đi
            entry_price = 0
            stop_loss = 0
            take_profit = 0
            
        return {
            "score": final_score,
            "action": action,
            "color": color,
            "pros": pros,
            "cons": cons,
            "entry": entry_price,
            "stop": stop_loss,
            "target": take_profit,
            "atr": atr
        }

# ==============================================================================
# 2. FUNDAMENTAL ANALYSIS ENGINE (BỘ MÁY PHÂN TÍCH CƠ BẢN - 9 CHỈ SỐ)
# ==============================================================================

class FundamentalAnalyzer:
    """
    Class phân tích sức khỏe tài chính dựa trên 9 tiêu chí cốt lõi.
    """
    def __init__(self, info: Dict, fin: pd.DataFrame, bal: pd.DataFrame, cash: pd.DataFrame):
        self.info = info
        self.fin = fin   # Income Statement
        self.bal = bal   # Balance Sheet
        self.cash = cash # Cash Flow
        
    def get_val(self, df, row_names, col_idx=0):
        """Hàm an toàn lấy dữ liệu từ BCTC (vì tên dòng có thể thay đổi)."""
        if df.empty: return 0.0
        for name in row_names:
            if name in df.index:
                try:
                    val = df.loc[name].iloc[col_idx]
                    return float(val) if val is not None else 0.0
                except: return 0.0
        return 0.0

    def analyze(self) -> Dict:
        score = 0
        details = []
        metrics = {} # Dict chứa 9 chỉ số để hiển thị Grid
        
        # --- NHÓM 1: SỨC SINH LỜI (PROFITABILITY) ---
        
        # 1. ROE
        roe = self.info.get('returnOnEquity', 0) or 0
        metrics['ROE'] = f"{roe*100:.1f}%"
        if roe > 0.20: score += 2; details.append(f"ROE Siêu việt ({roe*100:.1f}%)")
        elif roe > 0.15: score += 1
        elif roe < 0.05: score -= 1; details.append("⚠️ ROE Quá thấp")
        
        # 2. Net Margin
        rev = self.get_val(self.fin, ['Total Revenue', 'Operating Revenue'], 0)
        ni = self.get_val(self.fin, ['Net Income', 'Net Income Common Stockholders'], 0)
        nm = (ni / rev) if rev else 0
        metrics['Net Margin'] = f"{nm*100:.1f}%"
        if nm > 0.15: score += 1
        elif nm < 0.02: score -= 1
        
        # 3. BEP (EBIT / Assets)
        ebit = self.get_val(self.fin, ['EBIT', 'Operating Income', 'Pretax Income'], 0)
        assets = self.get_val(self.bal, ['Total Assets'], 0)
        bep = (ebit / assets) if assets else 0
        metrics['BEP'] = f"{bep*100:.1f}%"
        if bep > 0.1: score += 1
        
        # --- NHÓM 2: SỨC KHỎE TÀI CHÍNH (SOLVENCY) ---
        
        # 4. Debt/Asset
        liab = self.get_val(self.bal, ['Total Liabilities Net Minority Interest', 'Total Liabilities'], 0)
        da = (liab / assets) if assets else 0
        metrics['Debt/Asset'] = f"{da:.2f}"
        
        sector = self.info.get('sector', '')
        if 'Financial' in sector: # Bank/Chứng khoán nợ cao là bt
            if da > 0.95: score -= 1; details.append("⚠️ Đòn bẩy quá cao")
        else:
            if da < 0.6: score += 1
            elif da > 0.8: score -= 1; details.append("⚠️ Nợ vay rủi ro")
            
        # 5. Current Ratio
        curr_asset = self.get_val(self.bal, ['Current Assets', 'Total Current Assets'], 0)
        curr_liab = self.get_val(self.bal, ['Current Liabilities', 'Total Current Liabilities'], 0)
        cr = (curr_asset / curr_liab) if curr_liab else 0
        metrics['Current Ratio'] = f"{cr:.2f}"
        if cr > 1.2: score += 1
        elif cr < 0.9: score -= 1; details.append("⚠️ Áp lực thanh khoản ngắn hạn")
        
        # 6. Operating Cash Flow (OCF)
        ocf = self.get_val(self.cash, ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'], 0)
        metrics['OCF'] = f"{ocf/1e9:,.0f}B"
        if ocf > 0: score += 1; details.append("Dòng tiền KD Dương (+)")
        else: score -= 1; details.append("⚠️ Dòng tiền KD Âm (-)")
        
        # --- NHÓM 3: TĂNG TRƯỞNG & HIỆU QUẢ (GROWTH) ---
        
        # 7. Revenue Growth (YoY)
        rev_prev = self.get_val(self.fin, ['Total Revenue', 'Operating Revenue'], 4) # Cùng kỳ năm ngoái
        rev_g = ((rev - rev_prev) / rev_prev) if rev_prev else 0
        metrics['Rev Growth'] = f"{rev_g*100:.1f}%"
        if rev_g > 0.15: score += 1; details.append(f"Tăng trưởng DT tốt ({rev_g:.1%})")
        
        # 8. Inventory Turnover
        inv = self.get_val(self.bal, ['Inventory'], 0)
        cogs = self.get_val(self.fin, ['Cost Of Revenue', 'Cost of Goods Sold'], 0)
        inv_turn = (cogs / inv) if inv else 0
        metrics['Inv Turnover'] = f"{inv_turn:.1f}x" if inv else "N/A"
        if inv > 0 and inv_turn > 4: score += 1
        
        # 9. NI Growth (YoY)
        ni_prev = self.get_val(self.fin, ['Net Income', 'Net Income Common Stockholders'], 4)
        ni_g = ((ni - ni_prev) / abs(ni_prev)) if ni_prev else 0
        metrics['NI Growth'] = f"{ni_g*100:.1f}%"
        if ni_g > 0.15: score += 1
        elif ni_g < -0.1: score -= 1; details.append("⚠️ Lợi nhuận suy giảm")

        # --- TỔNG KẾT ---
        final_health = "TRUNG BÌNH"
        color = "#fcee0a"
        if score >= 6: final_health = "VỮNG MẠNH 💪"; color = "#00ff41"
        elif score >= 3: final_health = "ỔN ĐỊNH"; color = "#00f3ff"
        else: final_health = "YẾU KÉM ⚠️"; color = "#ff0055"
        
        return {
            "health": final_health,
            "color": color,
            "details": details,
            "market_cap": self.info.get('marketCap', 0),
            "metrics": metrics # Bảng 9 chỉ số
        }

# ==============================================================================
# 3. WRAPPER FUNCTIONS (Hàm bọc gọi từ App)
# ==============================================================================

def analyze_smart_v36(df: pd.DataFrame) -> Optional[Dict]:
    analyzer = TechnicalAnalyzer(df)
    return analyzer.analyze()

def analyze_fundamental_full(info, fin, bal, cash) -> Dict:
    """Wrapper mới: Nhận đủ 4 tham số cho Logic V40."""
    analyzer = FundamentalAnalyzer(info, fin, bal, cash)
    return analyzer.analyze()

# Giữ hàm cũ để tránh lỗi import (nhưng trả về default)
def analyze_fundamental(info: Dict, fin: pd.DataFrame) -> Dict:
    return {"health": "N/A", "color": "#888", "details": [], "market_cap": 0, "metrics": {}}
