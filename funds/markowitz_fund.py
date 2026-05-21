import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
import json
import os

def run_markowitz_optimization():
    if not os.path.exists("funds/output/prices.csv"):
        print("Erro: prices.csv não encontrado. Rode data_fetch.py primeiro.")
        return

    prices = pd.read_csv("funds/output/prices.csv", index_col=0, parse_dates=True)
    returns = prices.pct_change().dropna()
    
    # Definição de grupos para restrições
    EQUITY = ["ACWI", "IVV", "EFA", "IEMG"]
    FIXED = ["AGG", "LQD", "EMB", "TLT", "HYG"]
    ALTS = ["IAU", "COMT", "REET"]
    CASH = ["SHV"]
    
    tickers = list(prices.columns)
    n = len(tickers)
    
    # Datas de rebalanceamento (fim de mês)
    rebal_dates = returns.resample('M').last().index
    
    # Inicialização de resultados
    nav = pd.Series(100.0, index=returns.index)
    weights_history = {}
    current_weights = np.array([1.0/n] * n) # Start equally weighted
    
    # Loop de Backtest / Forward Run
    for i in range(len(rebal_dates)-1):
        date = rebal_dates[i]
        next_date = rebal_dates[i+1]
        
        # Janela de lookback (3 anos)
        lookback_start = date - pd.DateOffset(years=3)
        train_data = returns.loc[lookback_start:date]
        
        if len(train_data) < 252: continue # Mínimo 1 ano de dados
        
        # Estimação Robusta
        mu = train_data.mean() * 252
        cov = LedoitWolf().fit(train_data).covariance_ * 252
        
        # Função objetivo: Negativo do Sharpe
        def objective(w):
            p_ret = np.dot(w, mu)
            p_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
            return - (p_ret - 0.02) / p_vol # Rf = 2%
            
        # Restrições
        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}, # Soma 100%
            # Equity: 30% a 70%
            {'type': 'ineq', 'fun': lambda x: np.sum(x[[tickers.index(t) for t in EQUITY]]) - 0.3},
            {'type': 'ineq', 'fun': lambda x: 0.7 - np.sum(x[[tickers.index(t) for t in EQUITY]])},
            # Fixed Income: 20% a 60%
            {'type': 'ineq', 'fun': lambda x: np.sum(x[[tickers.index(t) for t in FIXED]]) - 0.2},
            {'type': 'ineq', 'fun': lambda x: 0.6 - np.sum(x[[tickers.index(t) for t in FIXED]])}
        ]
        
        # Limites Individuais (mín 1%, máx 30%)
        bounds = [(0.01, 0.30) for _ in range(n)]
        
        res = minimize(objective, current_weights, method='SLSQP', bounds=bounds, constraints=cons)
        
        if res.success:
            current_weights = res.x
            
        # Aplica retornos até o próximo rebal
        period_returns = returns.loc[date:next_date]
        for t_date, day_ret in period_returns.iterrows():
            if t_date == date: continue
            nav[t_date] = nav.asof(t_date - pd.Timedelta(days=1)) * (1 + np.dot(current_weights, day_ret))
            
        weights_history[date.strftime("%Y-%m-%d")] = {tickers[j]: float(current_weights[j]) for j in range(n)}

    # Salva resultados
    nav.to_csv("funds/output/markowitz_nav.csv")
    with open("funds/output/weights_markowitz.json", "w") as f:
        json.dump(weights_history, f)
        
    print("Fundo Markowitz processado com sucesso.")

if __name__ == "__main__":
    run_markowitz_optimization()
