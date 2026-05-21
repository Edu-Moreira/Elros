import yfinance as yf
import pandas as pd
import os
import requests
from fredapi import Fred
from dotenv import load_dotenv
import config # Importa nosso novo config.py

load_dotenv()

def fetch_all_data():
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # 1. Preços do Universo SAA
    print(f"Baixando preços para: {len(config.INVESTABLE_UNIVERSE)} ativos...")
    prices = yf.download(config.INVESTABLE_UNIVERSE, period="10y")['Close']
    
    # Remove tickers que falharam (colunas com todos os valores NaN)
    prices = prices.dropna(axis=1, how='all')
    print(f"Sucesso: {len(prices.columns)} ativos baixados.")
    
    prices.to_csv(f"{config.OUTPUT_DIR}/prices.csv")
    
    # 2. Indicadores Macro do FRED
    api_key = os.getenv("FRED_API_KEY")
    if api_key:
        fred = Fred(api_key=api_key)
        macro_data = {}
        for name, series_id in config.FRED_INDICATORS.items():
            try:
                print(f"Baixando FRED: {name}")
                macro_data[name] = fred.get_series(series_id)
            except:
                pass
        df_macro = pd.DataFrame(macro_data).ffill()
        df_macro.to_csv(f"{config.OUTPUT_DIR}/macro_indicators.csv")
    # 3. Dados Brasileiros (IBOV, PTAX, CDI)
    print("Baixando dados brasileiros...")
    tickers_br = config.BR_BENCHMARKS
    raw_br = yf.download(list(tickers_br.values()), period="10y")['Close']
    
    # Mapeamento explícito para evitar erro de ordem alfabética
    br_data = pd.DataFrame(index=raw_br.index)
    for name, ticker in tickers_br.items():
        if ticker in raw_br.columns:
            br_data[name] = raw_br[ticker]
    
    # CDI via API do Banco Central (SGS)
    try:
        from datetime import datetime, timedelta
        data_fim = datetime.now().strftime("%d/%m/%Y")
        data_ini = (datetime.now() - timedelta(days=365*10)).strftime("%d/%m/%Y")
        url_cdi = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{config.CDI_SERIE}/dados?formato=json&dataInicial={data_ini}&dataFinal={data_fim}"
        cdi_json = requests.get(url_cdi).json()
        df_cdi = pd.DataFrame(cdi_json)
        df_cdi['data'] = pd.to_datetime(df_cdi['data'], dayfirst=True)
        df_cdi.set_index('data', inplace=True)
        # Limpeza: remover vírgulas se existirem
        df_cdi['valor'] = df_cdi['valor'].str.replace(',', '.').astype(float) / 100
        # Converter CDI diário para acumulado (Base 100 no início da série capturada)
        df_cdi['CDI_NAV'] = (1 + df_cdi['valor']).cumprod() * 100
        br_data = br_data.join(df_cdi['CDI_NAV']).ffill()
    except Exception as e:
        print(f"Erro ao baixar CDI: {e}")
        
    br_data.to_csv(f"{config.OUTPUT_DIR}/br_data.csv")

if __name__ == "__main__":
    fetch_all_data()
