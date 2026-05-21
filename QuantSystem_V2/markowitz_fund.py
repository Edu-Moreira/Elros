import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf
import json
import os
import config

def run_optimization():
    path_prices = f"{config.OUTPUT_DIR}/prices.csv"
    if not os.path.exists(path_prices): return
    
    prices = pd.read_csv(path_prices, index_col=0, parse_dates=True)
    returns = prices.pct_change().dropna()
    tickers = list(prices.columns)
    n = len(tickers)
    
    rebal_dates = returns.resample('ME').last().index
    nav = pd.Series(100.0, index=returns.index)
    weights_history = {}
    
    # Prepara limites a partir do config
    def get_bounds(ticker):
        return config.MARKOWITZ_LIMITS.get(ticker, config.MARKOWITZ_LIMITS["DEFAULT"])

    bounds = [get_bounds(t) for t in tickers]
    
    current_w = np.array([1.0/n] * n)

    for i in range(len(rebal_dates)-1):
        date = rebal_dates[i]
        next_date = rebal_dates[i+1]
        
        train_data = returns.loc[date - pd.DateOffset(years=3):date]
        if len(train_data) < 126: continue
        
        mu = train_data.mean() * 252
        cov = LedoitWolf().fit(train_data).covariance_ * 252
        
        def objective(w):
            p_ret = np.dot(w, mu)
            p_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
            return - (p_ret - 0.03) / p_vol # Rf 3%
            
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}]
        
        res = minimize(objective, current_w, method='SLSQP', bounds=bounds, constraints=cons)
        if res.success:
            current_w = res.x
            
        period_rets = returns.loc[date:next_date]
        for t_date, day_ret in period_rets.iterrows():
            if t_date == date: continue
            nav[t_date] = nav.asof(t_date - pd.Timedelta(days=1)) * (1 + np.dot(current_w, day_ret))
            
        weights_history[date.strftime("%Y-%m-%d")] = {tickers[j]: float(current_w[j]) for j in range(n)}

    nav.to_csv(f"{config.OUTPUT_DIR}/markowitz_v2_nav.csv")
    with open(f"{config.OUTPUT_DIR}/weights_markowitz_v2.json", "w") as f:
        json.dump(weights_history, f)
    print("Markowitz V2 concluído.")

if __name__ == "__main__":
    run_optimization()
