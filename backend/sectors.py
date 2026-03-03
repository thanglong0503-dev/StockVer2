"""
================================================================================
MODULE: backend/sectors.py (Thay thế stock_list.py)
DESCRIPTION: Danh sách mã cổ phiếu theo Sàn và theo Nhóm Ngành.
================================================================================
"""

# --- 1. DANH SÁCH THEO SÀN ---
HOSE_LIST = ["HPG", "SSI", "FPT", "MWG", "VCB", "STB", "DIG", "NVL", "PDR", "VIX", "DGC", "VND", "VHM", "VIC", "VRE", "MSN", "GAS", "POW", "BID", "CTG", "TCB", "MBB", "ACB", "VPB", "HDB", "TPB", "VIB", "SSB", "OCB", "MSB", "LPB", "EIB", "SHB", "GVR", "PLX", "SAB", "VJC", "VNM", "BVH"]
HNX_LIST = ["SHS", "PVS", "IDC", "MBS", "CEO", "HUT", "VCG", "VGS", "TNG", "PVC", "PVB", "LAS", "DDG", "BVS"]
UPCOM_LIST = ["BSR", "OIL", "VEA", "QNS", "MCH", "VTP", "VGI", "ACV", "MVN", "G36", "C4G", "SBS", "ABB"]

# --- 2. DANH SÁCH THEO NGÀNH ---
SECTOR_DICT = {
    "🏦 NGÂN HÀNG (BANKS)": ["VCB", "BID", "CTG", "TCB", "MBB", "ACB", "VPB", "HDB", "TPB", "VIB", "STB", "SHB", "LPB", "OCB", "MSB", "EIB", "SSB"],
    "🏡 BẤT ĐỘNG SẢN (REAL ESTATE)": ["VHM", "VIC", "VRE", "NVL", "PDR", "DIG", "CEO", "DXG", "KDH", "NLG", "HDC", "HDG", "TCH", "KHG", "CRE"],
    "📈 CHỨNG KHOÁN (SECURITIES)": ["SSI", "VND", "VCI", "HCM", "SHS", "MBS", "VIX", "FTS", "BSI", "CTS", "AGR", "ORS", "BVS"],
    "🏗️ THÉP (STEEL)": ["HPG", "HSG", "NKG", "VSN", "TLH", "POM", "VGS"],
    "🛢️ DẦU KHÍ (OIL & GAS)": ["GAS", "PLX", "BSR", "OIL", "PVS", "PVD", "PVT", "PVB", "PVC", "CNG"],
    "🐟 THỦY SẢN (SEAFOOD)": ["VHC", "ANV", "IDI", "CMX", "FMC", "ACL"],
    "🛒 BÁN LẺ (RETAIL)": ["MWG", "PNJ", "FRT", "DGW", "PET", "MSN"],
    "🏭 KHU CÔNG NGHIỆP": ["GVR", "KBC", "IDC", "SZC", "VGC", "ITA", "PHR"],
    "⚡ ĐIỆN & NĂNG LƯỢNG": ["POW", "REE", "NT2", "GEG", "PC1", "HDG", "BCG"],
    "✈️ VẬN TẢI & CẢNG": ["GMD", "HHV", "VJC", "HVN", "ACV", "SCS", "VOS", "HAH"],
    "💻 CÔNG NGHỆ (TECH)": ["FPT", "CMG", "ELC", "ITD", "VGI", "VTP"]
}

def get_full_market_list(exchange="HOSE"):
    if exchange == "HOSE": return HOSE_LIST
    elif exchange == "HNX": return HNX_LIST
    elif exchange == "UPCOM": return UPCOM_LIST
    return []

def get_sector_list_data(sector_name):
    return SECTOR_DICT.get(sector_name, [])

def get_all_sector_names():
    return list(SECTOR_DICT.keys())
