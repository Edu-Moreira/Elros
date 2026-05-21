import pandas as pd
import numpy as np
import json
import os

def run_macro_tilt_fund():
    if not os.path.exists("funds/output/prices.csv") or not os.path.exists("funds/output/macro_indicators.csv"):
        print("Erro: Dados necessários não encontrados. Rode data_fetch.py.")
        return

    prices = pd.read_csv("funds/output/prices.csv", index_col=0, parse_dates=True)
    macro = pd.read_csv("funds/output/macro_indicators.csv", index_col=0, parse_dates=True)
    returns = prices.pct_change().dropna()
    
    # 1. Definir Carteira Neutra (Bench)
    # 60% ACWI, 40% AGG
    tickers = ["ACWI", "AGG"]
    neutral_weights = {"ACWI": 0.6, "AGG": 0.4}
    
    # 2. Calcular Scorecard Macro
    # Vamos normalizar os indicadores para escala [-1, 1] usando rolling rank
    scores = pd.DataFrame(index=macro.index)
    
    # Crescimento: PMI alto é bom
    scores['Growth'] = macro['PMI'].rolling(36).rank(pct=True).mul(2).sub(1)
    
    # Inflação: CPI alto é ruim para valuation (simplificado)
    scores['Inflation'] = macro['CPI'].pct_change(12).rolling(36).rank(pct=True).mul(-2).add(1)
    
    # Risco: VIX baixo é bom
    scores['Risk'] = macro['VIX'].rolling(36).rank(pct=True).mul(-2).add(1)
    
    # Curva: T10Y2Y positiva é expansão
    scores['Curve'] = macro['T10Y2Y'].rolling(36).rank(pct=True).mul(2).sub(1)
    
    # Spread: Baixo spread é otimismo
    scores['Credit'] = macro['HY_SPREAD'].rolling(36).rank(pct=True).mul(-2).add(1)
    
    total_score = scores.mean(axis=1).ffill().reindex(returns.index, method='ffill')
    
    # 3. Simulação
    nav = pd.Series(100.0, index=returns.index)
    bench_nav = pd.Series(100.0, index=returns.index)
    
    rebal_dates = returns.resample('M').last().index
    history = {}
    
    for i in range(len(rebal_dates)-1):
        date = rebal_dates[i]
        next_date = rebal_dates[i+1]
        
        current_score = total_score.asof(date)
        if pd.isna(current_score): current_score = 0
            
        # Determina o Tilt
        tilt = 0
        if current_score > 0.4: tilt = 0.10 # +10% em Ações
        elif current_score > 0.2: tilt = 0.05
        elif current_score < -0.4: tilt = -0.10 # -10% em Ações
        elif current_score < -0.2: tilt = -0.05
            
        eq_weight = 0.6 + tilt
        fi_weight = 0.4 - tilt
        
        weights = {"ACWI": eq_weight, "AGG": fi_weight}
        
        # Aplica retornos
        period_returns = returns.loc[date:next_date]
        for t_date, day_ret in period_returns.iterrows():
            if t_date == date: continue
            
            # Fundo
            ret_fundo = weights["ACWI"]*day_ret["ACWI"] + weights["AGG"]*day_ret["AGG"]
            nav[t_date] = nav.asof(t_date - pd.Timedelta(days=1)) * (1 + ret_fundo)
            
            # Benchmark (60/40 fixo)
            ret_bench = 0.6*day_ret["ACWI"] + 0.4*day_ret["AGG"]
            bench_nav[t_date] = bench_nav.asof(t_date - pd.Timedelta(days=1)) * (1 + ret_bench)
            
        history[date.strftime("%Y-%m-%d")] = {
            "weights": weights,
            "macro_score": float(current_score),
            "tilt": float(tilt)
        }

    # Salva resultados
    nav.to_csv("funds/output/macro_tilt_nav.csv")
    bench_nav.to_csv("funds/output/benchmark_6040_nav.csv")
    with open("funds/output/history_macro.json", "w") as f:
        json.dump(history, f)
        
    print("Fundo Macro Tilt processado com sucesso.")

if __name__ == "__main__":
    run_macro_tilt_fund()
