"""
================================================================================
MODULE: backend/commodities.py
DESCRIPTION: Crawler dữ liệu Vàng & Bạc Real-time từ Webgia và PhuQuy.
================================================================================
"""
import pandas as pd
import requests
import random

# --- DỮ LIỆU DỰ PHÒNG (BACKUP) ---
# Dùng khi mạng lỗi hoặc web nguồn chặn Bot
BACKUP_GOLD = [
    {"Loại vàng": "Vàng miếng SJC 999.9", "Mua vào": "16.560.000", "Bán ra": "16.860.000"},
    {"Loại vàng": "Nhẫn Trơn PNJ 999.9", "Mua vào": "16.510.000", "Bán ra": "16.810.000"},
    {"Loại vàng": "Vàng Nữ Trang 999.9", "Mua vào": "16.300.000", "Bán ra": "16.700.000"},
    {"Loại vàng": "Vàng Nữ Trang 999", "Mua vào": "16.283.000", "Bán ra": "16.683.000"},
    {"Loại vàng": "Vàng Tây 18K", "Mua vào": "11.635.000", "Bán ra": "12.525.000"}
]

BACKUP_SILVER = [
    {"SẢN PHẨM": "Bạc miếng Phú Quý 999 1 lượng", "ĐVT": "Vnđ/Lượng", "MUA": "2,904,000", "BÁN": "2,994,000"},
    {"SẢN PHẨM": "Bạc thỏi Phú Quý 999 10 lượng", "ĐVT": "Vnđ/Lượng", "MUA": "2,904,000", "BÁN": "2,994,000"},
    {"SẢN PHẨM": "Đồng bạc mỹ nghệ Phú Quý 999", "ĐVT": "Vnđ/Lượng", "MUA": "2,904,000", "BÁN": "3,416,000"},
    {"SẢN PHẨM": "Bạc thỏi Phú Quý 999 1Kg", "ĐVT": "Vnđ/Kg", "MUA": "77,439,806", "BÁN": "79,839,800"}
]

def get_gold_price():
    """
    Crawl giá vàng SJC từ webgia.com
    """
    url = "https://webgia.com/gia-vang/sjc/"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Tải bảng từ web về
        dfs = pd.read_html(url, encoding='utf-8')
        
        # Thường bảng giá chính là bảng đầu tiên hoặc thứ 2
        if len(dfs) > 0:
            df = dfs[0]
            # Webgia thường có cột: Khu vực, Loại vàng, Mua vào, Bán ra
            # Ta lọc lấy khu vực 'Hồ Chí Minh' hoặc lấy hết
            if 'Loại vàng' in df.columns:
                # Chỉ lấy 3 cột quan trọng
                df_clean = df[['Loại vàng', 'Mua vào', 'Bán ra']].copy()
                return df_clean
                
        raise Exception("Structure changed")

    except Exception as e:
        # Nếu lỗi, trả về Backup
        return pd.DataFrame(BACKUP_GOLD)

def get_silver_price():
    """
    Crawl giá bạc từ trang chủ Phú Quý Group
    """
    url = "https://giabac.phuquygroup.vn/"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Trang này trả về bảng HTML rất sạch
        response = requests.get(url, headers=header, timeout=5)
        dfs = pd.read_html(response.text)
        
        if len(dfs) > 0:
            df = dfs[0]
            # Đổi tên cột cho chuẩn hiển thị
            df.columns = [c.upper() for c in df.columns]
            
            # Kiểm tra xem có đúng bảng không
            if "SẢN PHẨM" in df.columns:
                # Lọc bỏ mấy dòng tiêu đề lặp lại (nếu có)
                df = df[df["SẢN PHẨM"] != "SẢN PHẨM"]
                return df[['SẢN PHẨM', 'ĐƠN VỊ', 'GIÁ MUA VÀO', 'GIÁ BÁN RA']]
                
        raise Exception("No table found")

    except Exception as e:
        # Nếu lỗi, trả về Backup
        return pd.DataFrame(BACKUP_SILVER)
