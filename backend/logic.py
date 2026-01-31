"""
================================================================================
MODULE: backend/logic.py
PROJECT: THANG LONG TERMINAL (ENTERPRISE EDITION)
VERSION: 36.1.0-STABLE
DESCRIPTION: 
    Advanced Analysis Engine.
    Contains classes for Technical Analysis (Multi-indicator) and 
    Fundamental Analysis (Financial Health Scoring).
================================================================================
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Tuple, Optional

# ==============================================================================
# 1. TECHNICAL ANALYSIS ENGINE (BỘ MÁY PHÂN TÍCH KỸ THUẬT)
# ==============================================================================

class TechnicalAnalyzer:
    """
    Class chuyên dụng để phân tích kỹ thuật sâu.
    Tích hợp: SuperTrend, Ichimoku, Bollinger Bands, RSI, MACD, ADX, Stochastic.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.latest = df.iloc[-1] if not df.empty else None
        self.prev = df.iloc[-2] if not df.empty and len(df) > 1 else None

    def validate(self) -> bool:
        """Kiểm tra dữ liệu đầu vào có đủ để phân tích không."""
        return self.df is not None and not self.df.empty and len(self.df) >= 50

    def add_indicators(self) -> pd.DataFrame:
        """
        Tính toán và nạp tất cả chỉ báo vào DataFrame.
        Sử dụng thư viện pandas_ta tối ưu hiệu năng.
        """
        if not self.validate(): return self.df

        # 1. Trend Indicators
        # SuperTrend (10, 3)
        sti = ta.supertrend(self.df['High'], self.df['Low'], self.df['Close'], length=10, multiplier=3)
        if sti is not None: self.df = self.df.join(sti)
        
        # EMAs (Exponential Moving Average)
        self.df.ta.ema(length=34, append=True) # Ngắn hạn
        self.df.ta.ema(length=89, append=True) # Trung hạn
        self.df.ta.ema(length=200, append=True) # Dài hạn (Trend chính)

        # Ichimoku Cloud
        ichimoku = ta.ichimoku(self.df['High'], self.df['Low'], self.df['Close'], tenkan=9, kijun=26, senkou=52)
        if ichimoku is not None:
            self.df = self.df.join(ichimoku[0]) # Join Tenkan, Kijun, SpanA, SpanB

        # 2. Volatility Indicators
        # Bollinger Bands (20, 2)
        self.df.ta.bbands(length=20, std=2, append=True)
        
        # ATR (Average True Range) - Dùng để tính Stoploss
        self.df.ta.atr(length=14, append=True)

        # 3. Momentum Indicators
        # RSI (Relative Strength Index)
        self.df.ta.rsi(length=14, append=True)
        
        # MACD (Moving Average Convergence Divergence)
        self.df.ta.macd(fast=12, slow=26, signal=9, append=True)
        
        # Stochastic Oscillator
        self.df.ta.stoch(high=self.df['High'], low=self.df['Low'], close=self.df['Close'], k=14, d=3, append=True)

        # ADX (Average Directional Index) - Đo sức mạnh xu hướng
        self.df.ta.adx(length=14, append=True)
        
        # Cập nhật lại latest data sau khi thêm cột
        self.latest = self.df.iloc[-1]
        self.prev = self.df.iloc[-2]
        
        return self.df

    def analyze(self) -> Dict:
        if not self.validate(): return {}
        if 'RSI_14' not in self.df.columns: self.add_indicators()
            
        score = 0
        pros = []
        cons = []
        close = self.latest['Close']
        
        # --- 1. TÍNH ĐIỂM (SCORING) ---
        # SuperTrend
        st_col = [c for c in self.df.columns if 'SUPERT' in c]
        if st_col:
            if close > self.latest[st_col[0]]: score += 2; pros.append("SuperTrend: Báo TĂNG (Uptrend)")
            else: score -= 2; cons.append("SuperTrend: Báo GIẢM (Downtrend)")
                
        # EMA
        ema34 = self.latest.get('EMA_34', 0)
        ema89 = self.latest.get('EMA_89', 0)
        if close > ema34 > ema89: score += 1; pros.append("EMA: Giá trên MA ngắn hạn")
        if close < self.latest.get('EMA_200', 0): score -= 1; cons.append("EMA: Dưới MA200 (Dài hạn xấu)")
            
        # Ichimoku
        span_a = self.latest.get('ISA_9', 0)
        span_b = self.latest.get('ISB_26', 0)
        if close > span_a and close > span_b: score += 1; pros.append("Ichimoku: Giá nằm trên Mây")
            
        # RSI
        rsi = self.latest.get('RSI_14', 50)
        if 50 <= rsi <= 70: score += 1
        elif rsi < 30: score += 1.5; pros.append("RSI: Quá bán (Dễ hồi phục)")
        elif rsi > 75: score -= 1; cons.append("RSI: Quá mua (Cẩn trọng)")
            
        # Bollinger
        bb_upper = self.latest.get('BBU_20_2.0', 0)
        if close > bb_upper: score += 2; pros.append("Bollinger: Breakout dải trên")
            
        # --- 2. TỔNG HỢP KẾT QUẢ ---
        final_score = max(0, min(10, 5 + score))
        
        # Mặc định tính toán Entry/Stop/Target
        atr = self.latest.get('ATRr_14', close * 0.02)
        entry_price = close
        stop_loss = close - (2 * atr)
        take_profit = close + (4 * atr)

        # Mặc định là QUAN SÁT
        action = "QUAN SÁT"
        color = "#fcee0a" 

        # Phân loại tín hiệu
        if final_score >= 8:
            action = "MUA MẠNH 💎"
            color = "#00ff41"
        elif final_score >= 6:
            action = "MUA (BUY)"
            color = "#00f3ff"
        elif final_score <= 4:
            # === [ĐOẠN QUAN TRỌNG NHẤT] ===
            action = "BÁN / CẮT LỖ"
            color = "#ff0055"
            # ÉP VỀ 0 ĐỂ FRONTEND ẨN ĐI
            entry_price = 0
            stop_loss = 0
            take_profit = 0
            # ===============================
            
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
# 2. FUNDAMENTAL ANALYSIS ENGINE (BỘ MÁY PHÂN TÍCH CƠ BẢN)
# ==============================================================================

class FundamentalAnalyzer:
    """
    Class chuyên dụng phân tích sức khỏe tài chính.
    Dựa trên dữ liệu: Info, BCTC Quý.
    """
    def __init__(self, info: Dict, financials: pd.DataFrame):
        self.info = info
        self.fin = financials # Income Statement
        
    def analyze(self) -> Dict:
        """
        Chấm điểm sức khỏe doanh nghiệp (F-Score simplified).
        """
        score = 0
        details = []
        
        # Lấy dữ liệu an toàn
        pe = self.info.get('trailingPE')
        pb = self.info.get('priceToBook')
        roe = self.info.get('returnOnEquity')
        peg = self.info.get('pegRatio')
        mkt_cap = self.info.get('marketCap', 0)
        
        # 1. VALUATION (Định giá)
        if pe:
            if 0 < pe < 12:
                score += 2
                details.append(f"P/E Hấp dẫn ({pe:.1f}x) - Rẻ")
            elif 12 <= pe <= 20:
                score += 1
                details.append(f"P/E Hợp lý ({pe:.1f}x)")
            else:
                score -= 1
                details.append(f"⚠️ P/E Cao ({pe:.1f}x)")
        
        if pb and pb < 1.5:
            score += 1
            details.append(f"P/B Thấp ({pb:.1f}x) - Tài sản an toàn")
            
        # 2. PROFITABILITY (Khả năng sinh lời)
        if roe:
            roe_pct = roe * 100
            if roe_pct > 15:
                score += 2
                details.append(f"ROE Xuất sắc ({roe_pct:.1f}%)")
            elif roe_pct < 5:
                score -= 1
                details.append(f"⚠️ ROE Quá thấp ({roe_pct:.1f}%)")
                
        # 3. GROWTH (Tăng trưởng - Từ BCTC)
        if not self.fin.empty and len(self.fin.columns) >= 2:
            try:
                # So sánh Lợi nhuận sau thuế quý gần nhất vs cùng kỳ
                net_income_now = self.fin.iloc[0, 0] # Hàng Net Income, Cột mới nhất
                
                # Cố gắng tìm cột cùng kỳ năm ngoái (thường là cột thứ 4 index=4, nếu có 5 cột)
                # Nếu không có đủ 5 cột thì so với quý trước (cột 1)
                idx_prev = 4 if len(self.fin.columns) >= 5 else 1
                net_income_prev = self.fin.iloc[0, idx_prev]
                
                period_label = "cùng kỳ" if idx_prev == 4 else "quý trước"
                
                if net_income_prev and net_income_prev != 0:
                    growth = (net_income_now - net_income_prev) / abs(net_income_prev)
                    if growth > 0.15:
                        score += 2
                        details.append(f"🚀 Tăng trưởng mạnh ({growth:.1%}) so với {period_label}")
                    elif growth < -0.10:
                        score -= 1
                        details.append(f"⚠️ Suy giảm ({growth:.1%}) so với {period_label}")
            except Exception as e:
                # details.append(f"Lỗi tính tăng trưởng: {str(e)}")
                pass

        # Xếp hạng
        health = "TRUNG BÌNH"
        color = "#f59e0b" # Vàng
        
        if score >= 6:
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

# ==============================================================================
# 3. WRAPPER FUNCTIONS (Hàm bọc để gọi từ bên ngoài)
# ==============================================================================

def analyze_smart_v36(df: pd.DataFrame) -> Optional[Dict]:
    """Hàm wrapper cho TechnicalAnalyzer"""
    analyzer = TechnicalAnalyzer(df)
    return analyzer.analyze()

def analyze_fundamental(info: Dict, fin: pd.DataFrame) -> Dict:
    """Hàm wrapper cho FundamentalAnalyzer"""
    analyzer = FundamentalAnalyzer(info, fin)
    return analyzer.analyze()
