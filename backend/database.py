"""
================================================================================
MODULE: backend/database.py
DESCRIPTION: Quản lý User & Portfolio (BẢO MẬT CAO - CHỐNG CHIẾM QUYỀN ADMIN).
================================================================================
"""
import json
import os
import pandas as pd
import yfinance as yf
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

# [QUAN TRỌNG] TỰ ĐỘNG KHỞI TẠO ADMIN NẾU CHƯA CÓ
def init_admin_account():
    """
    Hàm này đảm bảo user 'admin' luôn tồn tại và thuộc về Lão Đại.
    Mật khẩu mặc định: 'ThangLongVip' (Ngài có thể đổi ở đây)
    """
    db = load_db()
    if "admin" not in db:
        # Tạo mới tài khoản trùm cuối
        db["admin"] = {
            "password": "ThangLongVip",  # <--- MẬT KHẨU CỦA NGÀI (Đổi tùy ý)
            "profile": {
                "name": "SUPREME COMMANDER",
                "email": "boss@thanglong.vn",
                "joined_date": "2026-01-01"
            },
            "portfolio": []
        }
        save_db(db)
        print(">>> ADMIN ACCOUNT CREATED SUCCESSFULLY.")

# --- 2. QUẢN LÝ TÀI KHOẢN ---
def register_user(username, password, full_name, email):
    # [CHỐT CHẶN 1] CẤM ĐĂNG KÝ TÊN NHẠY CẢM
    forbidden_names = ["admin", "administrator", "root", "system", "support", "mod"]
    
    if username.lower().strip() in forbidden_names:
        return False, "⛔ Tên này là TỐI MẬT (Reserved)! Không được phép đăng ký."

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
    # Kiểm tra khớp user và pass
    if username in db and db[username]["password"] == password:
        return True, db[username]["profile"]
    return False, None

# --- 3. QUẢN LÝ DANH MỤC (GIỮ NGUYÊN) ---
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
    try:
        ticker = symbol if symbol.endswith(".VN") else f"{symbol}.VN"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1] / 1000
    except: pass
    return 0.0

def get_user_portfolio(username):
    db = load_db()
    if username not in db: return pd.DataFrame()
    
    portfolio_list = db[username].get("portfolio", [])
    if not portfolio_list: return pd.DataFrame()
    
    df = pd.DataFrame(portfolio_list)
    df['cost_value'] = df['price_avg'] * df['volume']
    
    tickers = df['symbol'].unique().tolist()
    market_data = get_pro_data(tickers)
    
    if not market_data.empty:
        price_map = dict(zip(market_data['Symbol'], market_data['Price']))
        df['market_price'] = df['symbol'].map(price_map).fillna(0)
    else:
        df['market_price'] = 0.0

    for index, row in df.iterrows():
        if row['market_price'] == 0 or pd.isna(row['market_price']):
            backup_price = get_realtime_price_backup(row['symbol'])
            if backup_price > 0:
                df.at[index, 'market_price'] = backup_price

    df['total_value'] = df.apply(lambda x: (x['market_price'] * x['volume']) if x['market_price'] > 0 else x['cost_value'], axis=1)
    df['profit_loss'] = df['total_value'] - df['cost_value']
    df['percent_pl'] = df.apply(lambda x: (x['profit_loss'] / x['cost_value'] * 100) if x['cost_value'] != 0 else 0, axis=1)
    
    return df

# --- 4. ADMIN TOOLS ---
def get_all_users_admin():
    db = load_db()
    user_list = []
    for username, data in db.items():
        profile = data.get("profile", {})
        portfolio = data.get("portfolio", [])
        user_list.append({
            "Username": username,
            "Họ Tên": profile.get("name", "N/A"),
            "Email": profile.get("email", "N/A"),
            "Ngày Gia Nhập": profile.get("joined_date", "N/A"),
            "Số Lệnh": len(portfolio),
            "Pass": data.get("password", "***")
        })
    return pd.DataFrame(user_list)

def delete_user_admin(username_to_delete):
    db = load_db()
    if username_to_delete in db:
        del db[username_to_delete]
        save_db(db)
        return True
    return False

# [QUAN TRỌNG] Gọi hàm khởi tạo Admin ngay khi module được load
init_admin_account()
