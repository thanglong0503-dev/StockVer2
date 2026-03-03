"""
================================================================================
MODULE: backend/database.py
DESCRIPTION: Hệ thống quản lý User & Portfolio (Fix lỗi giá 0 bằng Backup YFinance).
================================================================================
"""
import json
import os
import pandas as pd
import yfinance as yf # [NEW] Gọi thêm đội đặc nhiệm YFinance
from datetime import datetime
from backend.data import get_pro_data

DB_FILE = "user_data.json"

# --- 1. HỆ THỐNG CƠ SỞ DỮ LIỆU ---
def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. QUẢN LÝ TÀI KHOẢN ---
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

# --- 3. QUẢN LÝ DANH MỤC (CÓ FIX GIÁ) ---
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

def get_realtime_price_backup(symbol):
    """
    Hàm cứu hộ: Lấy giá từ Yahoo Finance nếu nguồn chính bị lỗi.
    Input: 'MBB' -> Output: 27.05 (Đơn vị nghìn đồng)
    """
    try:
        # Thử thêm đuôi .VN nếu chưa có
        ticker = symbol if symbol.endswith(".VN") else f"{symbol}.VN"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            price_vnd = data['Close'].iloc[-1]
            # Yahoo trả về VND (VD: 27050), ta đổi sang nghìn (27.05) để khớp hệ thống
            return price_vnd / 1000
    except:
        pass
    return 0.0

def get_user_portfolio(username):
    """
    Lấy danh mục đầu tư & TÍNH TOÁN LÃI LỖ (CƠ CHẾ KÉP)
    """
    db = load_db()
    if username not in db: return pd.DataFrame()
    
    portfolio_list = db[username].get("portfolio", [])
    if not portfolio_list: return pd.DataFrame()
    
    df = pd.DataFrame(portfolio_list)
    
    # 1. Tính giá vốn trước (Luôn có)
    df['cost_value'] = df['price_avg'] * df['volume']
    
    # 2. Lấy giá thị trường từ nguồn Quét Nhanh (Radar)
    tickers = df['symbol'].unique().tolist()
    market_data = get_pro_data(tickers)
    
    # Map giá vào bảng (Nếu không có thì để 0)
    if not market_data.empty:
        price_map = dict(zip(market_data['Symbol'], market_data['Price']))
        df['market_price'] = df['symbol'].map(price_map).fillna(0)
    else:
        df['market_price'] = 0.0

    # 3. [FIX QUAN TRỌNG] VÒNG LẶP CỨU HỘ
    # Duyệt qua từng dòng, nếu giá vẫn bằng 0 -> Gọi Yahoo Finance cứu viện
    for index, row in df.iterrows():
        if row['market_price'] == 0 or pd.isna(row['market_price']):
            backup_price = get_realtime_price_backup(row['symbol'])
            if backup_price > 0:
                df.at[index, 'market_price'] = backup_price

    # 4. Tính toán Lãi/Lỗ
    # Nếu sau khi cứu viện mà giá vẫn = 0 (mã hủy niêm yết/sai mã) thì dùng giá vốn (coi như hòa vốn tạm thời)
    df['total_value'] = df.apply(lambda x: (x['market_price'] * x['volume']) if x['market_price'] > 0 else x['cost_value'], axis=1)
    
    df['profit_loss'] = df['total_value'] - df['cost_value']
    
    # Tính % lãi lỗ (xử lý chia cho 0)
    df['percent_pl'] = df.apply(lambda x: (x['profit_loss'] / x['cost_value'] * 100) if x['cost_value'] != 0 else 0, axis=1)
    
    return df
