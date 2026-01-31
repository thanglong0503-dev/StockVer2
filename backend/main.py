# backend/main.py
from fastapi import FastAPI
from logic import get_stock_data_frame, scoring_system

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend is running!"}

@app.get("/api/analyze/{symbol}")
def analyze(symbol: str):
    # 1. Lấy dữ liệu
    df = get_stock_data_frame(symbol.upper())
    if df is None:
        return {"error": "Không tìm thấy mã hoặc lỗi dữ liệu"}
    
    # 2. Tính toán
    result = scoring_system(df)
    
    # 3. Trả về JSON
    return result

# Chạy lệnh: uvicorn main:app --reload
