"""
================================================================================
MODULE: backend/commodities.py
DESCRIPTION: Crawler dữ liệu Vàng & Bạc Real-time (STRICT MODE - NO FAKE DATA).
================================================================================
"""
import pandas as pd
import requests

def get_gold_price():
    """
    Crawl giá vàng SJC từ webgia.com.
    Nếu lỗi -> Trả về DataFrame rỗng (Không dùng backup ảo).
    """
    url = "https://webgia.com/gia-vang/sjc/"
    try:
        # Thử đọc bảng từ web
        dfs = pd.read_html(url, encoding='utf-8')
        if len(dfs) > 0:
            df = dfs[0]
            if 'Loại vàng' in df.columns:
                df_clean = df[['Loại vàng', 'Mua vào', 'Bán ra']].copy()
                
                # [LỌC RÁC] Loại bỏ các dòng quảng cáo
                df_clean = df_clean[~df_clean['Mua vào'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                df_clean = df_clean[~df_clean['Bán ra'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                
                return df_clean
                
    except Exception as e:
        pass # Gặp lỗi thì bỏ qua, xuống dòng dưới trả về rỗng
        
    # Trả về bảng rỗng nếu không lấy được dữ liệu thật
    return pd.DataFrame()

def get_silver_price():
    """
    Crawl giá bạc Phú Quý.
    Nếu lỗi -> Trả về DataFrame rỗng.
    """
    url = "https://giabac.phuquygroup.vn/"
    header = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=header, timeout=5)
        dfs = pd.read_html(response.text)
        if len(dfs) > 0:
            df = dfs[0]
            df.columns = [c.upper() for c in df.columns] 
            
            if "SẢN PHẨM" in df.columns:
                # [LỌC RÁC]
                df = df[df['SẢN PHẨM'] != "SẢN PHẨM"]
                df = df[df['ĐƠN VỊ'].notna()] 
                # Chỉ lấy dòng có đơn vị tiền tệ
                df = df[df['ĐƠN VỊ'].str.contains("Vnđ", na=False, case=False)]

                return df[['SẢN PHẨM', 'ĐƠN VỊ', 'GIÁ MUA VÀO', 'GIÁ BÁN RA']]
                
    except Exception as e:
        pass
        
    # Trả về bảng rỗng
    return pd.DataFrame()
