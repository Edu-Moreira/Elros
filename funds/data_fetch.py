import yfinance as yf
import pandas as pd
import os
from fredapi import Fred
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configurações
UNIVERSE = [
    "ACWI", "IVV", "EFA", "IEMG",  # Equity
    "AGG", "LQD", "EMB", "TLT", "HYG", # Fixed Income
    "IAU", "COMT", "REET", "SHV"    # Alts / Cash
]

FRED_SERIES = {
    "PMI": "IPMAN", # Proxy para atividade industrial
    "CPI": "CPIAUCSL", # Inflação Consumidor
    "VIX": "VIXCLS", # Volatilidade (Medo)
    "T10Y2Y": "T10Y2Y", # Curva de Juros
    "HY_SPREAD": "BAMLH0A0HYM2" # High Yield Spread
}

def fetch_prices():
    print(f"Baixando preços para o universo: {UNIVERSE}")
    data = yf.download(UNIVERSE, period="10y")['Close']
    data.to_csv("funds/output/prices.csv")
    print("Preços salvos em funds/output/prices.csv")
    return data

def fetch_macro(api_key):
    if not api_key:
        print("Aviso: FRED_API_KEY não encontrada. Pulando dados macro.")
        return None
    
    fred = Fred(api_key=api_key)
    macro_data = {}
    
    for name, series_id in FRED_SERIES.items():
        try:
            print(f"Baixando série FRED: {series_id} ({name})")
            s = fred.get_series(series_id)
            macro_data[name] = s
        except Exception as e:
            print(f"Erro ao baixar {series_id}: {e}")
            
    df_macro = pd.DataFrame(macro_data).ffill()
    df_macro.to_csv("funds/output/macro_indicators.csv")
    print("Indicadores macro salvos em funds/output/macro_indicators.csv")
    return df_macro

if __name__ == "__main__":
    os.makedirs("funds/output", exist_ok=True)
    fetch_prices()
    
    # Tenta pegar API Key do ambiente
    fred_key = os.getenv("FRED_API_KEY")
    fetch_macro(fred_key)
