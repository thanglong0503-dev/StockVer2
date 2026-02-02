"""
================================================================================
MODULE: backend/commodities.py
DESCRIPTION: Crawler dữ liệu Vàng & Bạc Real-time (ĐÃ CÓ BỘ LỌC RÁC SẠCH SẼ).
================================================================================
"""
import pandas as pd
import requests

# --- DỮ LIỆU DỰ PHÒNG (BACKUP) ---
BACKUP_GOLD = [
    {"Loại vàng": "Vàng miếng SJC 999.9", "Mua vào": "16.560.000", "Bán ra": "16.860.000"},
    {"Loại vàng": "Nhẫn Trơn PNJ 999.9", "Mua vào": "16.510.000", "Bán ra": "16.810.000"},
    {"Loại vàng": "Vàng Nữ Trang 999.9", "Mua vào": "16.300.000", "Bán ra": "16.700.000"}
]

BACKUP_SILVER = [
    {"SẢN PHẨM": "Bạc miếng Phú Quý 999 1 lượng", "ĐVT": "Vnđ/Lượng", "MUA": "2,904,000", "BÁN": "2,994,000"},
    {"SẢN PHẨM": "Bạc thỏi Phú Quý 999 10 lượng", "ĐVT": "Vnđ/Lượng", "MUA": "2,904,000", "BÁN": "2,994,000"}
]

def get_gold_price():
    """Crawl giá vàng SJC từ webgia.com và LỌC SẠCH RÁC"""
    url = "https://webgia.com/gia-vang/sjc/"
    try:
        dfs = pd.read_html(url, encoding='utf-8')
        if len(dfs) > 0:
            df = dfs[0]
            if 'Loại vàng' in df.columns:
                df_clean = df[['Loại vàng', 'Mua vào', 'Bán ra']].copy()
                
                # [LỌC RÁC] Loại bỏ các dòng chứa chữ "web", "xem", "liên hệ"
                # Chuyển cột giá sang chuỗi để tìm kiếm
                df_clean = df_clean[~df_clean['Mua vào'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                df_clean = df_clean[~df_clean['Bán ra'].astype(str).str.contains("web|xem|liên hệ", case=False, na=False)]
                
                return df_clean
        raise Exception("Structure changed")
    except Exception:
        return pd.DataFrame(BACKUP_GOLD)

def get_silver_price():
    """Crawl giá bạc Phú Quý và LỌC TIÊU ĐỀ THỪA"""
    url = "https://giabac.phuquygroup.vn/"
    header = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=header, timeout=5)
        dfs = pd.read_html(response.text)
        if len(dfs) > 0:
            df = dfs[0]
            df.columns = [c.upper() for c in df.columns] # Viết hoa tên cột
            
            if "SẢN PHẨM" in df.columns:
                # [LỌC RÁC] Bỏ những dòng mà cột ĐƠN VỊ bị trống (thường là tiêu đề nhóm)
                # Hoặc cột SẢN PHẨM lặp lại chữ "SẢN PHẨM"
                df = df[df['SẢN PHẨM'] != "SẢN PHẨM"]
                df = df[df['ĐƠN VỊ'].notna()] 
                
                # Bỏ các dòng tiêu đề nhóm (Ví dụ: "BẠC THƯƠNG HIỆU PHÚ QUÝ")
                # Đặc điểm: Dòng tiêu đề thường không có giá tiền cụ thể hoặc định dạng khác
                # Cách đơn giản: Chỉ lấy dòng có ĐVT là 'Vnđ/Lượng' hoặc 'Vnđ/Kg'
                df = df[df['ĐƠN VỊ'].str.contains("Vnđ", na=False, case=False)]

                return df[['SẢN PHẨM', 'ĐƠN VỊ', 'GIÁ MUA VÀO', 'GIÁ BÁN RA']]
        raise Exception("No table found")
    except Exception:
        return pd.DataFrame(BACKUP_SILVER)
