"""
================================================================================
MODULE: backend/database.py
DESCRIPTION: Hệ thống quản lý User & Portfolio (Lưu trữ bằng JSON).
================================================================================
"""
import json
import os
import pandas as pd
from datetime import datetime
from backend.data import get_pro_data  # Dùng hàm này để lấy giá realtime

DB_FILE = "user_data.json"

# --- 1. HỆ THỐNG CƠ SỞ DỮ LIỆU ---
def load_db():
    """Đọc dữ liệu từ file JSON"""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    """Lưu dữ liệu vào file JSON"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. QUẢN LÝ TÀI KHOẢN (AUTH) ---
def register_user(username, password, full_name, email):
    db = load_db()
    if username in db:
        return False, "⚠️ Tên đăng nhập đã tồn tại!"
    
    db[username] = {
        "password": password,
        "profile": {
            "name": full_name,
            "email": email,
            "joined_date": datetime.now().strftime("%Y-%m-%d")
        },
        "portfolio": []  # Danh sách cổ phiếu đã mua
    }
    save_db(db)
    return True, "✅ Đăng ký thành công! Hãy đăng nhập."

def login_user(username, password):
    db = load_db()
    if username in db and db[username]["password"] == password:
        return True, db[username]["profile"]
    return False, None

# --- 3. QUẢN LÝ DANH MỤC (PORTFOLIO) ---
def add_transaction(username, symbol, volume, price_avg):
    """Thêm giao dịch mua vào sổ tay"""
    db = load_db()
    if username not in db: return False
    
    # Chuẩn hóa dữ liệu
    symbol = symbol.upper().strip()
    new_txn = {
        "symbol": symbol,
        "volume": int(volume),
        "price_avg": float(price_avg),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Kiểm tra xem mã này đã có trong danh mục chưa để gộp (tùy chọn)
    # Ở đây ta cứ thêm dòng mới cho đơn giản, sau này gộp sau
    db[username]["portfolio"].append(new_txn)
    save_db(db)
    return True

def get_user_portfolio(username):
    """
    Lấy danh mục đầu tư và TÍNH TOÁN LÃI LỖ REAL-TIME
    """
    db = load_db()
    if username not in db: return pd.DataFrame()
    
    portfolio_list = db[username].get("portfolio", [])
    if not portfolio_list: return pd.DataFrame()
    
    # Chuyển thành DataFrame
    df = pd.DataFrame(portfolio_list)
    
    # 1. Lấy danh sách các mã cổ phiếu trong ví
    tickers = df['symbol'].unique().tolist()
    
    # 2. Gọi hàm lấy giá thị trường (Real-time) từ backend cũ
    # Hàm get_pro_data trả về DataFrame có cột: Symbol, Price, Pct...
    market_data = get_pro_data(tickers)
    
    if market_data.empty:
        return df # Trả về bảng gốc nếu không lấy được giá thị trường
        
    # 3. Ghép giá thị trường vào bảng portfolio
    # Tạo từ điển giá: {'HPG': 26.5, 'FPT': 110.2...}
    price_map = dict(zip(market_data['Symbol'], market_data['Price']))
    
    # Map giá vào bảng
    df['market_price'] = df['symbol'].map(price_map).fillna(0) * 1000 # Lưu ý đơn vị (giả sử get_pro_data trả về nghìn đồng)
    
    # Nếu get_pro_data trả về đơn vị nghìn (VD: 26.5), mà giá vốn ta nhập là 26500
    # Ta cần check kỹ đơn vị. Thường get_pro_data trả về 26.5 (tức 26,500).
    # Để an toàn, ta quy ước Người dùng nhập giá vốn là 26.5 (nghìn đồng) cho đồng bộ.
    
    # TÍNH TOÁN LÃI LỖ
    # Giả sử giá nhập và giá thị trường đều đơn vị: Nghìn VND
    df['total_value'] = df['market_price'] * df['volume']
    df['cost_value'] = df['price_avg'] * df['volume']
    df['profit_loss'] = df['total_value'] - df['cost_value']
    df['percent_pl'] = (df['profit_loss'] / df['cost_value']) * 100
    
    return df
