"""
================================================================================
MODULE: backend/database.py
DESCRIPTION: Hệ thống quản lý User & Portfolio (Fix lỗi KeyError).
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
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    """Lưu dữ liệu vào file JSON"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. QUẢN LÝ TÀI KHOẢN (AUTH) ---
def register_user(username, password, full_name, email):
    db = load_db()
    if username in db: return False, "⚠️ Tên đăng nhập đã tồn tại!"
    
    db[username] = {
        "password": password,
        "profile": {"name": full_name, "email": email, "joined_date": datetime.now().strftime("%Y-%m-%d")},
        "portfolio": [] 
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
    db = load_db()
    if username not in db: return False
    
    new_txn = {
        "symbol": symbol.upper().strip(),
        "volume": int(volume),
        "price_avg": float(price_avg),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    db[username]["portfolio"].append(new_txn)
    save_db(db)
    return True

def get_user_portfolio(username):
    """
    Lấy danh mục đầu tư và TÍNH TOÁN LÃI LỖ REAL-TIME (SAFE MODE)
    """
    db = load_db()
    if username not in db: return pd.DataFrame()
    
    portfolio_list = db[username].get("portfolio", [])
    if not portfolio_list: return pd.DataFrame()
    
    # Chuyển thành DataFrame
    df = pd.DataFrame(portfolio_list)
    
    # [FIX QUAN TRỌNG]: TÍNH GIÁ VỐN NGAY LẬP TỨC (Không phụ thuộc Market Data)
    # Giá vốn = Giá TB * Khối lượng
    df['cost_value'] = df['price_avg'] * df['volume']
    
    # Khởi tạo sẵn các cột khác với giá trị 0 để tránh KeyError
    df['market_price'] = 0.0
    df['total_value'] = 0.0
    df['profit_loss'] = 0.0
    df['percent_pl'] = 0.0
    
    # 1. Lấy giá thị trường
    tickers = df['symbol'].unique().tolist()
    market_data = get_pro_data(tickers)
    
    # Nếu không lấy được giá thị trường (trả về rỗng), ta trả về DF đã có cột cost_value
    if market_data.empty:
        return df 
        
    # 2. Ghép giá thị trường
    price_map = dict(zip(market_data['Symbol'], market_data['Price']))
    
    # Map giá vào bảng (Giữ nguyên đơn vị nghìn đồng để đồng bộ với input user)
    df['market_price'] = df['symbol'].map(price_map).fillna(0)
    
    # 3. Tính toán Lãi/Lỗ (Chỉ tính cho mã nào lấy được giá > 0)
    # Nếu giá thị trường = 0 (lỗi), thì coi như chưa có lãi lỗ
    df['total_value'] = df.apply(lambda x: (x['market_price'] * x['volume']) if x['market_price'] > 0 else x['cost_value'], axis=1)
    
    df['profit_loss'] = df['total_value'] - df['cost_value']
    
    # Tính phần trăm (Tránh chia cho 0)
    df['percent_pl'] = df.apply(lambda x: (x['profit_loss'] / x['cost_value'] * 100) if x['cost_value'] != 0 else 0, axis=1)
    
    return df
