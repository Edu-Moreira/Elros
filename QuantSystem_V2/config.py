# QuantSystem V2 - Configurações Centrais

# 1. UNIVERSO INVESTÍVEL (Baseado no SAA.py)
# ETFs de Países (Decomposição ACWI) + ETFs de Fatores de Renda Fixa (Decomposição AGG/AGGG)
INVESTABLE_UNIVERSE = [
    # Equity - Países Principais
    "IVV", "EWJ", "EWU", "EWG", "EWQ", "EWC", "EWA", "EWL", "EWN", "EWT", "EWY", "FXI", "INDY", 
    # Fixed Income - Fatores
    "SHY", "IEF", "TLT", "IGSB", "LQD", "IGLB", "EMB", "CEMB", "HYG", "TIP", "SHV"
]

EQUITY_TICKERS = ["IVV", "EWJ", "EWU", "EWG", "EWQ", "EWC", "EWA", "EWL", "EWN", "EWT", "EWY", "FXI", "INDY"]
FIXED_TICKERS = ["SHY", "IEF", "TLT", "IGSB", "LQD", "IGLB", "EMB", "CEMB", "HYG", "TIP", "SHV"]

# 2. CARTEIRA NEUTRA (Target 60/40 ACWI/AGG decomposta)
# Valores aproximados baseados na concentração típica desses benchmarks
NEUTRAL_WEIGHTS = {
    # Equity (Total ~60%)
    "IVV": 0.380,  # USA (~63% de 60%)
    "EWJ": 0.035,  # Japan
    "EWU": 0.025,  # UK
    "EWG": 0.015,  # Germany
    "EWQ": 0.015,  # France
    "EWC": 0.020,  # Canada
    "EWA": 0.015,  # Australia
    "EWL": 0.015,  # Switzerland
    "EWN": 0.010,  # Netherlands
    "EWT": 0.020,  # Taiwan
    "EWY": 0.015,  # Korea
    "FXI": 0.020,  # China
    "INDY": 0.015, # India
    
    # Fixed Income (Total ~40%)
    "SHY": 0.050,  # ST Treasuries
    "IEF": 0.100,  # MT Treasuries
    "TLT": 0.050,  # LT Treasuries
    "IGSB": 0.050, # IG Corp ST
    "LQD": 0.080,  # IG Corp MT
    "EMB": 0.030,  # EM Debt
    "HYG": 0.030,  # High Yield
    "TIP": 0.010,  # Inflation
}

# 3. LIMITES MARKOWITZ (Min, Max) por ativo
MARKOWITZ_LIMITS = {
    "DEFAULT": (0.00, 0.10), # No máximo 10% por ativo padrão
    "IVV": (0.20, 0.50),     # IVV deve estar entre 20% e 50% (âncora)
    "IEF": (0.05, 0.20),     # IEF entre 5% e 20%
}

# 4. CONFIGURAÇÕES MACRO
FRED_INDICATORS = {
    "PMI": "IPMAN",
    "CPI": "CPIAUCSL",
    "VIX": "VIXCLS",
    "T10Y2Y": "T10Y2Y",
    "HY_SPREAD": "BAMLH0A0HYM2"
}

# 6. BR BENCHMARKS
BR_BENCHMARKS = {
    "IBOV": "^BVSP",
    "PTAX": "USDBRL=X"
}
CDI_SERIE = 12 # Código SGS Banco Central

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
