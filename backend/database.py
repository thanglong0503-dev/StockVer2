import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import datetime
import yfinance as yf

# ==============================================================================
# 1. KẾT NỐI ĐỘNG CƠ GOOGLE SHEETS (DÙNG CACHE ĐỂ SIÊU TỐC)
# ==============================================================================
@st.cache_resource
def get_gspread_client():
    try:
        creds_json = st.secrets["GOOGLE_CREDENTIALS"]
        # Đọc JSON an toàn
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            creds_dict = creds_json
            
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"🚨 LỖI ĐỘNG CƠ GOOGLE SHEETS: {e}")
        return None

def get_sheet(sheet_name):
    """Hàm lấy trang tính cụ thể"""
    client = get_gspread_client()
    if client:
        try:
            db_name = st.secrets.get("SPREADSHEET_NAME", "Fincept_DB")
            sh = client.open(db_name)
            return sh.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"⚠️ Chưa có Trang tính tên '{sheet_name}'. Lão đại nhớ tạo trong file Sheets nhé!")
            return None
    return None

# ==============================================================================
# ==============================================================================
# 2. HỆ THỐNG XÁC THỰC TÀI KHOẢN (ĐỌC/GHI SHEET 'Users')
# ==============================================================================
def init_admin_account():
    pass

def register_user(username, password, name, email):
    sheet = get_sheet("Users")
    if not sheet: return False, "Lỗi kết nối CSDL."
    
    usernames = sheet.col_values(1)
    if username in usernames:
        return False, "⚠️ Tên đăng nhập đã tồn tại!"
        
    # Ghi nhận thời gian tạo tài khoản ngay lúc đăng ký
    reg_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Thêm reg_time vào cột thứ 6 (Last_Login)
    sheet.append_row([username, password, name, email, "user", reg_time])
    return True, "✅ Khởi tạo ID thành công!"

def login_user(username, password):
    # CỬA HẬU DÀNH CHO LÃO ĐẠI 
    if username == "admin" and password == "admin0503":
        return True, {"name": "SUPREME COMMANDER", "role": "admin"}

    sheet = get_sheet("Users")
    if not sheet: return False, {}
    
    records = sheet.get_all_records()
    for idx, row in enumerate(records):
        if str(row.get('Username', '')) == username and str(row.get('Password', '')) == password:
            
            # [CHIP THEO DÕI]: Cập nhật thời gian mỗi lần User đăng nhập thành công
            login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                # idx + 2: Vị trí hàng hiện tại của User trên Sheets
                # 6: Vị trí Cột 'Last_Login' (Cột F)
                sheet.update_cell(idx + 2, 6, login_time)
            except Exception as e:
                pass # Lỗi lặt vặt mạng mẽo bỏ qua, vẫn cho đăng nhập bình thường
                
            return True, {"name": row.get('Name', 'Agent'), "role": row.get('Role', 'user')}
            
    return False, {}

# ==============================================================================
# ==============================================================================
# 3. QUẢN LÝ DANH MỤC VÀ GIAO DỊCH (ĐỌC/GHI SHEET 'Transactions')
# ==============================================================================
def add_transaction(username, symbol, volume, price):
    sheet = get_sheet("Transactions")
    if not sheet: return False
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # [BẢN VÁ LỖI]: Ép cứng kiểu chuỗi (String) để Google Sheets KHÔNG ĐƯỢC tự định dạng
    vol_str = str(float(volume))
    price_str = str(float(price))
    
    # Dùng value_input_option='RAW' để cấm Google "lanh chanh" đổi dấu chấm thành dấu phẩy
    sheet.append_row(
        [username, symbol.upper(), vol_str, price_str, date_str], 
        value_input_option='RAW'
    )
    return True

def get_user_portfolio(username):
    sheet = get_sheet("Transactions")
    if not sheet: return pd.DataFrame()
    
    records = sheet.get_all_records()
    if not records: return pd.DataFrame()
    
    df = pd.DataFrame(records)
    # Lọc giao dịch của user hiện tại
    df = df[df['Username'] == username]
    if df.empty: return pd.DataFrame()
    
    # [BẢN VÁ LỖI]: Quét dọn sạch sẽ mọi dấu phẩy do Google tự sinh ra trước khi tính
    df['Volume'] = df['Volume'].astype(str).str.replace(',', '.').str.strip()
    df['Price'] = df['Price'].astype(str).str.replace(',', '.').str.strip()
    
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    
    df['Total_Cost'] = df['Volume'] * df['Price']
    
    portfolio = df.groupby('Symbol').agg(
        volume=('Volume', 'sum'),
        total_cost=('Total_Cost', 'sum')
    ).reset_index()
    
    # Lọc bỏ những mã đã bán hết (volume <= 0)
    portfolio = portfolio[portfolio['volume'] > 0].copy()
    if portfolio.empty: return pd.DataFrame()
    
    portfolio['price_avg'] = portfolio['total_cost'] / portfolio['volume']
    
    # Kéo giá thị trường realtime từ yfinance (đã chia 1000 để chuẩn hóa)
    market_prices = []
    for sym in portfolio['Symbol']:
        try:
            ticker = yf.Ticker(f"{sym}.VN")
            current_price = ticker.history(period="1d")['Close'].iloc[-1] / 1000.0
            market_prices.append(current_price)
        except Exception:
            market_prices.append(0.0)
            
    portfolio['market_price'] = market_prices
    portfolio['cost_value'] = portfolio['volume'] * portfolio['price_avg']
    portfolio['total_value'] = portfolio['volume'] * portfolio['market_price']
    portfolio['profit_loss'] = portfolio['total_value'] - portfolio['cost_value']
    portfolio['percent_pl'] = (portfolio['profit_loss'] / portfolio['cost_value']) * 100
    
    # Đổi tên cột cho khớp với App.py
    portfolio = portfolio.rename(columns={"Symbol": "symbol"})
    return portfolio

def delete_portfolio_stock(username, symbol):
    sheet = get_sheet("Transactions")
    if not sheet: return False
    
    # Lấy dữ liệu và tìm hàng cần xóa (chạy ngược từ dưới lên để không bị lệch index)
    records = sheet.get_all_records()
    for idx in range(len(records) - 1, -1, -1):
        if records[idx].get('Username') == username and records[idx].get('Symbol') == symbol:
            sheet.delete_rows(idx + 2)
    return True

# ==============================================================================
# 4. ADMIN HQ & GHI CHÚ
# ==============================================================================
def get_all_users_admin():
    sheet = get_sheet("Users")
    if not sheet: return pd.DataFrame()
    
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    # Ẩn cột mật khẩu khi admin xem
    if 'Password' in df.columns:
        df['Password'] = "******"
    return df

def delete_user_admin(username):
    # Xóa trong bảng Users
    user_sheet = get_sheet("Users")
    if user_sheet:
        u_records = user_sheet.get_all_records()
        for idx in range(len(u_records) - 1, -1, -1):
            if u_records[idx].get('Username') == username:
                user_sheet.delete_rows(idx + 2)
                
    # Xóa luôn tài sản của user đó trong bảng Transactions
    trans_sheet = get_sheet("Transactions")
    if trans_sheet:
        t_records = trans_sheet.get_all_records()
        for idx in range(len(t_records) - 1, -1, -1):
            if t_records[idx].get('Username') == username:
                trans_sheet.delete_rows(idx + 2)
    return True

# Tích hợp Hệ thống Ghi chú Đám mây (Đọc/Ghi Sheet 'Notes')
def save_user_note(username, note):
    sheet = get_sheet("Notes")
    if not sheet: return False
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = sheet.get_all_records()
    
    # Radar dò tìm xem Lão đại (hoặc user) đã có dòng ghi chú nào trong Sheets chưa
    cell_row = None
    for idx, row in enumerate(records):
        if str(row.get('Username', '')) == username:
            # Cộng 2 vì index của Python bắt đầu từ 0, và Dòng 1 là tiêu đề (Header)
            cell_row = idx + 2 
            break
            
    if cell_row:
        # Nếu đã có, thì GHI ĐÈ nội dung mới vào ô đó (Cột 2 là Note, Cột 3 là Thời gian)
        sheet.update_cell(cell_row, 2, note)
        sheet.update_cell(cell_row, 3, date_str)
    else:
        # Nếu chưa có, tạo hẳn một hàng mới tinh
        sheet.append_row([username, note, date_str], value_input_option='RAW')
        
    return True

def get_user_note(username):
    sheet = get_sheet("Notes")
    if not sheet: return ""
    
    records = sheet.get_all_records()
    for row in records:
        if str(row.get('Username', '')) == username:
            return str(row.get('Note_Content', ''))
            
    return ""
