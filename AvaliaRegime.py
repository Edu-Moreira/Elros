#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 22:51:54 2026

@author: eduardo
"""

import pandas as pd
import numpy as np
import yfinance as yf
from arch import arch_model

etf_dict = {

    # =========================
    # COMMODITIES
    # =========================
    "IAU": "GOLD",
    "SLV": "SILVER",
    "COMT": "BROAD_COMMODITIES",

    # =========================
    # EQUITY - US STYLE FACTORS
    # =========================
    "IVV": "US_BETA",
    "ITOT": "US_TOTAL",
    "IWB": "US_BROAD",

    "IVW": "US_GROWTH",
    "IWF": "US_GROWTH",
    "IVE": "US_VALUE",
    "IWD": "US_VALUE",

    "QUAL": "US_QUALITY",
    "MTUM": "US_MOMENTUM",
    "SIZE": "US_SIZE",
    "USMV": "US_LOW_VOL",
    "DGRO": "US_DIV_GROWTH",
    "DVY": "US_DIVIDEND",
    "HDV": "US_HIGH_DIV",

    # =========================
    # EQUITY - GLOBAL / DM / EM
    # =========================
    "ACWI": "GLOBAL_EQUITY",
    "URTH": "GLOBAL_EQUITY",
    "IOO": "GLOBAL_LARGE",

    "EFA": "DM_EQUITY",
    "IEFA": "DM_EQUITY",
    "IXUS": "GLOBAL_EX_US",
    "ACWX": "GLOBAL_EX_US",

    "IEMG": "EM_EQUITY",
    "EEM": "EM_EQUITY",

    # =========================
    # EQUITY - REGIONAL / COUNTRY
    # =========================
    "EWJ": "JAPAN",
    "EWG": "GERMANY",
    "EWU": "UK",
    "EWZ": "BRAZIL",
    "FXI": "CHINA_LARGE",
    "MCHI": "CHINA",
    "INDA": "INDIA",
    "EWA": "AUSTRALIA",
    "EWC": "CANADA",
    "EWL": "SWITZERLAND",
    "EWT": "TAIWAN",
    "EWY": "KOREA",
    "EWH": "HONG_KONG",
    "EWS": "SINGAPORE",
    "EZA": "SOUTH_AFRICA",
    "EWQ": "FRANCE",
    "EWI": "ITALY",
    "EWP": "SPAIN",
    "EWD": "SWEDEN",
    "EWN": "NETHERLANDS",
    "EWO": "AUSTRIA",
    "EWM": "MALAYSIA",
    "EWW": "MEXICO",
    "ECH": "CHILE",
    "EPU": "PERU",
    "EPOL": "POLAND",
    "EPHE": "PHILIPPINES",
    "EIDO": "INDONESIA",
    "EDEN": "DENMARK",
    "EIS": "ISRAEL",
    "TUR": "TURKEY",
    "THD": "THAILAND",
    "SMIN": "INDIA_SMALL_CAP",

    # =========================
    # EQUITY - SECTORS
    # =========================
    "IXN": "TECH_GLOBAL",
    "IYW": "TECH_US",
    "IGV": "SOFTWARE",
    "SOXX": "SEMIS",

    "IXC": "ENERGY_GLOBAL",
    "IYE": "ENERGY_US",
    "IEO": "OIL_GAS",

    "IXJ": "HEALTH_GLOBAL",
    "IYH": "HEALTH_US",
    "IHI": "MED_DEVICES",
    "IBB": "BIOTECH",

    "IYF": "FINANCIALS",
    "IXG": "GLOBAL_FINANCIALS",
    "EUFN": "EU_BANKS",

    "IYK": "CONSUMER_STAPLES",
    "IYC": "CONSUMER_DISC",

    "IYT": "TRANSPORT",
    "IYJ": "INDUSTRIALS",

    "IGF": "INFRASTRUCTURE",
    "IFRA": "US_INFRA",

    "ITB": "HOMEBUILDERS",
    "REET": "GLOBAL_REIT",
    "USRT": "US_REIT",
    "REM": "MORTGAGE_REIT",

    # =========================
    # THEMATIC
    # =========================
    "ICLN": "CLEAN_ENERGY",
    "IDRV": "AUTONOMOUS_EV",
    "IHAK": "CYBERSECURITY",
    "IDNA": "GENOMICS",
    "ARTY": "AI",
    "XT": "EXPONENTIAL_TECH",

    # =========================
    # ESG
    # =========================
    "ESGU": "US_ESG",
    "ESGD": "DM_ESG",
    "ESGE": "EM_ESG",
    "SUSA": "US_ESG",
    "SUSL": "US_ESG",
    "SUSC": "CREDIT_ESG",
    "CRBN": "LOW_CARBON",
    "SDG": "SUSTAINABILITY",

    # =========================
    # FIXED INCOME - CORE
    # =========================
    "AGG": "US_AGG",
    "IUSB": "US_TOTAL_BOND",
    "IAGG": "GLOBAL_AGG",
    "EAGG": "GLOBAL_AGG",

    # =========================
    # RATES
    # =========================
    "SHV": "CASH",
    "SGOV": "CASH",
    "SHY": "UST_1_3Y",
    "IEI": "UST_3_7Y",
    "IEF": "UST_7_10Y",
    "TLH": "UST_10_20Y",
    "TLT": "UST_20Y+",
    "GOVT": "UST_ALL",
    "GOVZ": "UST_LONG_ZERO",

    # =========================
    # CREDIT
    # =========================
    "LQD": "IG_CORP",
    "IGSB": "IG_SHORT",
    "IGLB": "IG_LONG",
    "QLTA": "IG_QUALITY",
    "USIG": "IG_CORP",

    "HYG": "HY_CORP",
    "SHYG": "HY_SHORT",
    "FALN": "FALLEN_ANGELS",

    # =========================
    # EM FIXED INCOME
    # =========================
    "EMB": "EM_HARD",
    "DVYE": "EM_DIVIDEND",
    "EMXC": "EM_EX_CHINA",

    # =========================
    # INFLATION / FLOATERS
    # =========================
    "TIP": "INFLATION",
    "STIP": "INFLATION_SHORT",
    "FLOT": "FLOATING_RATE",
    "TFLO": "FLOATING_RATE",

    # =========================
    # SECURITIZED
    # =========================
    "MBB": "MBS",

    # =========================
    # MULTI-ASSET
    # =========================
    "AOK": "ALLOCATION_CONSERVATIVE",
    "AOM": "ALLOCATION_MODERATE",
    "AOR": "ALLOCATION_GROWTH",
    "AOA": "ALLOCATION_AGGRESSIVE",

    # =========================
    # CRYPTO
    # =========================
    "IBIT": "BITCOIN",
    "ETHA": "ETHEREUM",

}

TICKERS = {"EWJ": "JAPAN",
"EWG": "GERMANY",
"EWU": "UK",
"IVV": "USA",
"EWZ": "BRAZIL",
"FXI": "CHINA_LARGE",
"MCHI": "CHINA",
"INDA": "INDIA",
"EWA": "AUSTRALIA",
"EWC": "CANADA",
"EWL": "SWITZERLAND",
"EWT": "TAIWAN",
"EWY": "KOREA",
"EWH": "HONG_KONG",
"EWS": "SINGAPORE",
"EZA": "SOUTH_AFRICA",
"EWQ": "FRANCE",
"EWI": "ITALY",
"EWP": "SPAIN",
"EWD": "SWEDEN",
"EWN": "NETHERLANDS",
"EWO": "AUSTRIA",
"EWM": "MALAYSIA",
"EWW": "MEXICO",
"ECH": "CHILE",
"EPU": "PERU",
"EPOL": "POLAND",
"EPHE": "PHILIPPINES",
"EIDO": "INDONESIA",
"EDEN": "DENMARK",
"EIS": "ISRAEL",
"TUR": "TURKEY",
"THD": "THAILAND"}

ativos = yf.download(list(etf_dict.keys()), period='5y')['Close']

retornos = ativos.pct_change().dropna()

retornos_long = retornos.melt(ignore_index = False)

modelos_garch = {}

for ativo in retornos.columns:

    df = retornos[ativo] * 100

    model = arch_model(df, vol='Garch', p=1, q=1)
    res = model.fit(disp="off")

    if res.convergence_flag != 0:
        continue

    omega = res.params['omega']
    alpha = res.params['alpha[1]']
    beta = res.params['beta[1]']

    # evitar explosão
    if (alpha + beta) >= 0.999:
        continue

    unc_vol = np.sqrt(omega / (1 - alpha - beta))
    unc_vol_annual = unc_vol * np.sqrt(252)

    modelos_garch[ativo] = {
        "unc_vol": unc_vol_annual,
        "cond_vol": res.conditional_volatility * np.sqrt(252)
    }

vol_cond = pd.DataFrame({
    ativo: modelos_garch[ativo]["cond_vol"]
    for ativo in modelos_garch
})

vol_cond.index = retornos.index

vol_unc = pd.Series({
    ativo: modelos_garch[ativo]["unc_vol"]
    for ativo in modelos_garch
})

delta = 0.15  # 15%

upper = vol_unc * (1 + delta)
lower = vol_unc * (1 - delta)

regime = pd.DataFrame(index=vol_cond.index, columns=vol_cond.columns)

regime = np.where(vol_cond.gt(upper, axis=1), "HIGH_VOL",
         np.where(vol_cond.lt(lower, axis=1), "LOW_VOL", "MID_VOL"))

regime = pd.DataFrame(regime, index=vol_cond.index, columns=vol_cond.columns)

regime_long = regime.reset_index().melt(id_vars="Date")
regime_long.columns = ["Date", "Ticker", "Regime"]

df_final = retornos_long.merge(regime_long, on=["Date", "Ticker"])