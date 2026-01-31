"""
================================================================================
MODULE: backend/stock_list.py
DESCRIPTION: 
    Database of Vietnamese Stocks categorized by Exchange.
    Filtered for liquidity to ensure optimal scanning speed.
================================================================================
"""

# 1. HOSE (Sở Giao dịch Chứng khoán TP.HCM) - ~300 mã tiêu biểu
HOSE = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG", 
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB", 
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
    "AAA", "APH", "ASM", "BCG", "BMI", "BMP", "BSI", "BWE", "CMG", "CII",
    "CRE", "CSV", "CTD", "CTR", "CTS", "DBC", "DCM", "DGC", "DGW", "DHA",
    "DIG", "DPM", "DRC", "DSE", "DXG", "EIB", "ELC", "EVE", "FCN", "FTS",
    "GEX", "GIL", "GMD", "HAH", "HAG", "HAX", "HCM", "HDC", "HDG", "HHS",
    "HHV", "HPX", "HSG", "HT1", "HVN", "IDI", "IJC", "IMP", "ITA", "KBC",
    "KDC", "KDH", "KHG", "KOS", "KSB", "LCG", "LPB", "LSS", "MSB", "MSH",
    "NAB", "NKG", "NLG", "NT2", "NVL", "OCB", "ORS", "PAN", "PC1", "PDR",
    "PET", "PHR", "PIM", "PNJ", "PTB", "PVD", "PVT", "REE", "SAM", "SBT",
    "SCS", "SHI", "SJS", "SKG", "SZC", "TCH", "TCM", "TCO", "TDC", "TEG",
    "TKA", "TLG", "TMS", "TNH", "TRC", "TV2", "VCG", "VCI", "VGC", "VHC",
    "VIX", "VND", "VNE", "VNG", "VOS", "VPG", "VPI", "VSC", "VSH", "VTO"
]

# 2. HNX (Sở Giao dịch Chứng khoán Hà Nội) - ~100 mã tiêu biểu
HNX = [
    "SHS", "CEO", "PVS", "IDC", "MBS", "HUT", "TNG", "VCS", "IDJ", "API",
    "APS", "L14", "VC3", "CSC", "VGS", "PVC", "PVB", "DDG", "AMV", "BVS",
    "CMS", "CTC", "DHT", "DXP", "GKM", "HEV", "HGV", "HOM", "IPA", "ITQ",
    "KLF", "LAS", "MST", "NTP", "NVB", "OCH", "PCG", "PLC", "PSI", "PVG",
    "S99", "SCG", "SD5", "SEB", "SHN", "SLS", "SZB", "TAR", "TC6", "TDN",
    "TIG", "TJC", "TKU", "TMB", "TTH", "TVC", "TVD", "TXM", "VCC", "VDL",
    "VHE", "VIG", "VKC", "VNR", "VSA", "VTV", "WCS"
]

# 3. UPCOM (Sàn giao dịch đại chúng) - ~100 mã tiêu biểu
UPCOM = [
    "BSR", "OIL", "VEA", "VGI", "MCH", "QNS", "ACV", "MML", "KLB", "ABB",
    "BVB", "C4G", "DDV", "DRI", "G36", "GE2", "HVF", "LTG", "MVC", "NTC",
    "PAS", "PGB", "PHP", "PVP", "SBS", "SGB", "SIP", "SSH", "STG", "TCI",
    "TID", "VGT", "VNA", "VNB", "VNP", "VOC", "VTP", "BAB", "BOT", "CEN",
    "CLX", "CMR", "DNL", "DS3", "DTK", "EVF", "GHC", "GIC", "HPP", "HTC",
    "HU4", "KDF", "KSH", "LMH", "MSR", "MTV", "NDN", "ODE", "PFL", "PJS",
    "PLA", "POS", "PPC", "PXT", "RIC", "SAS", "SGP", "SID", "SIV", "SKH",
    "SKV", "SWC", "TBD", "TIS", "TKG", "TND", "TTN", "TVN", "VCA", "VDN"
]

def get_full_market_list(exchange="HOSE"):
    if exchange == "HOSE": return HOSE
    if exchange == "HNX": return HNX
    if exchange == "UPCOM": return UPCOM
    return HOSE + HNX + UPCOM # ALL
