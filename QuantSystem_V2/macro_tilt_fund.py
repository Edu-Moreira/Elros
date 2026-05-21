import pandas as pd
import numpy as np
import json
import os
import config

def run_macro_v2():
    prices = pd.read_csv(f"{config.OUTPUT_DIR}/prices.csv", index_col=0, parse_dates=True)
    path_macro = f"{config.OUTPUT_DIR}/macro_indicators.csv"
    
    # Se não houver indicadores, usa pesos neutros (sem tilt)
    if not os.path.exists(path_macro):
        indicators = pd.DataFrame(index=prices.index)
    else:
        indicators = pd.read_csv(path_macro, index_col=0, parse_dates=True)
    
    returns = prices.pct_change().dropna()
    
    # Cálculo do Scorecard (Ranking histórico de 3 anos)
    if os.path.exists(path_macro):
        macro = pd.read_csv(path_macro, index_col=0, parse_dates=True)
        scores = pd.DataFrame(index=macro.index)
        scores['Growth'] = macro['PMI'].rolling(36).rank(pct=True).mul(2).sub(1)
        scores['Risk'] = macro['VIX'].rolling(36).rank(pct=True).mul(-2).add(1)
        scores['Credit'] = macro['HY_SPREAD'].rolling(36).rank(pct=True).mul(-2).add(1)
        total_score = scores.mean(axis=1).ffill().reindex(returns.index, method='ffill')
    else:
        total_score = pd.Series(0, index=returns.index)

    nav = pd.Series(100.0, index=returns.index)
    bench_nav = pd.Series(100.0, index=returns.index)
    
    rebal_dates = returns.resample('ME').last().index
    history = {}
    
    neutral_w = pd.Series(config.NEUTRAL_WEIGHTS)

    for i in range(len(rebal_dates)-1):
        date = rebal_dates[i]
        next_date = rebal_dates[i+1]
        
        score = total_score.asof(date)
        if pd.isna(score): score = 0
            
        # Determina Magnitude do Tilt (Max 10%)
        tilt_magnitude = np.clip(score * 0.20, -0.10, 0.10)
        
        # Ajusta Pesos Granulares
        current_w = neutral_w.copy()
        
        # Filtra tickers disponíveis para evitar KeyError
        avail_eq = [t for t in config.EQUITY_TICKERS if t in prices.columns]
        avail_fi = [t for t in config.FIXED_TICKERS if t in prices.columns]
        
        # Filtra o peso neutro para os disponíveis e normaliza
        neutral_avail = neutral_w.reindex(avail_eq + avail_fi).fillna(0)
        neutral_avail = neutral_avail / neutral_avail.sum()
        
        # Multiplicadores para manter proporção dentro da classe
        weight_eq_neutral = neutral_avail[avail_eq].sum()
        weight_fi_neutral = neutral_avail[avail_fi].sum()

        mult_eq = (weight_eq_neutral + tilt_magnitude) / weight_eq_neutral if weight_eq_neutral > 0 else 1
        mult_fi = (weight_fi_neutral - tilt_magnitude) / weight_fi_neutral if weight_fi_neutral > 0 else 1
        
        current_w = neutral_avail.copy()
        current_w[avail_eq] *= mult_eq
        current_w[avail_fi] *= mult_fi
        
        # Backtest do período
        period_rets = returns.loc[date:next_date]
        for t_date, day_ret in period_rets.iterrows():
            if t_date == date: continue
            
            nav[t_date] = nav.asof(t_date - pd.Timedelta(days=1)) * (1 + (current_w * day_ret).sum())
            bench_nav[t_date] = bench_nav.asof(t_date - pd.Timedelta(days=1)) * (1 + (neutral_w * day_ret).sum())
            
        history[date.strftime("%Y-%m-%d")] = {
            "macro_score": float(score),
            "tilt": float(tilt_magnitude),
            "weights": current_w.to_dict()
        }

    nav.to_csv(f"{config.OUTPUT_DIR}/macro_v2_nav.csv")
    bench_nav.to_csv(f"{config.OUTPUT_DIR}/benchmark_v2_nav.csv")
    with open(f"{config.OUTPUT_DIR}/history_macro_v2.json", "w") as f:
        json.dump(history, f)
    print("Macro Tilt V2 concluído.")

if __name__ == "__main__":
    import traceback
    try:
        run_macro_v2()
    except Exception as e:
        print(f"ERRO no Macro Tilt:\n{e}")
        traceback.print_exc()
        exit(1)
