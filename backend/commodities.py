"""
================================================================================
MODULE: backend/commodities.py
DESCRIPTION: Crawler dữ liệu Vàng & Bạc Real-time (STRICT MODE + FORMATTING).
================================================================================
"""
import pandas as pd
import requests

def format_vnd_price(val):
    """
    Hàm trang điểm số liệu: 
    Input: 2999000 (int/str)
    Output: "2.999.000" (str chuẩn Việt Nam)
    """
    try:
        # Chuyển về số thực, định dạng có dấu phẩy (2,999,000), rồi đổi phẩy thành chấm
        return "{:,.0f}".format(float(val)).replace(",", ".")
    except:
        return val

def get_gold_price():
    """
    Crawl giá vàng SJC từ webgia.com.
    """
    url = "https://webgia.com/gia-vang/sjc/"
    try:
        dfs = pd.read_html(url, encoding='utf-8')
        if len(dfs) > 0:
            df = dfs[0]
            if 'Loại vàng' in df.columns:
                df_clean = df[['Loại vàng', 'Mua vào', 'Bán ra']].copy()
                
                # [LỌC RÁC]
                df_clean = df_clean[~df_clean['Mua vào'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                df_clean = df_clean[~df_clean['Bán ra'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                
                return df_clean
    except Exception:
        pass
    return pd.DataFrame()

def get_silver_price():
    """
    Crawl giá bạc Phú Quý + Format số đẹp.
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
                df = df[df['ĐƠN VỊ'].str.contains("Vnđ", na=False, case=False)]

                # [TRANG ĐIỂM SỐ LIỆU] Áp dụng hàm format cho 2 cột giá
                df['GIÁ MUA VÀO'] = df['GIÁ MUA VÀO'].apply(format_vnd_price)
                df['GIÁ BÁN RA'] = df['GIÁ BÁN RA'].apply(format_vnd_price)

                return df[['SẢN PHẨM', 'ĐƠN VỊ', 'GIÁ MUA VÀO', 'GIÁ BÁN RA']]
    except Exception:
        pass
        
    return pd.DataFrame()
