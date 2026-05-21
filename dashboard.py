import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Elros Quant Funds", layout="wide")

st.title("🛡️ Elros Quantitative Funds Dashboard")
st.markdown("---")

def load_data():
    try:
        markowitz_nav = pd.read_csv("funds/output/markowitz_nav.csv", index_col=0, parse_dates=True)
        macro_nav = pd.read_csv("funds/output/macro_tilt_nav.csv", index_col=0, parse_dates=True)
        bench_nav = pd.read_csv("funds/output/benchmark_6040_nav.csv", index_col=0, parse_dates=True)
        
        with open("funds/output/weights_markowitz.json", "r") as f:
            weights_markowitz = json.load(f)
            
        with open("funds/output/history_macro.json", "r") as f:
            history_macro = json.load(f)
            
        return markowitz_nav, macro_nav, bench_nav, weights_markowitz, history_macro
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}. Certifique-se de ter rodado os scripts da pasta /funds.")
        return None, None, None, None, None

m_nav, mc_nav, b_nav, w_mark, h_macro = load_data()

if m_nav is not None:
    # 1. Resumo de Performance
    col1, col2, col3 = st.columns(3)
    
    def get_stats(nav_series):
        ret_total = (nav_series.iloc[-1] / nav_series.iloc[0]) - 1
        return f"{ret_total:.2%}"

    with col1:
        st.metric("Markowitz QF (Total Return)", get_stats(m_nav.iloc[:, 0]))
    with col2:
        st.metric("Macro Tilt QF (Total Return)", get_stats(mc_nav.iloc[:, 0]))
    with col3:
        st.metric("Bench 60/40 (Total Return)", get_stats(b_nav.iloc[:, 0]))

    st.markdown("### Performance Histórica (NAV)")
    
    # Unificar NAVs para o gráfico
    df_plot = pd.concat([m_nav, mc_nav, b_nav], axis=1)
    df_plot.columns = ["Markowitz QF", "Macro Tilt QF", "Benchmark 60/40"]
    
    fig = px.line(df_plot, labels={"value": "NAV (Base 100)", "Date": "Data"})
    fig.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # 2. Alocação Atual
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Alocação — Markowitz")
        latest_date = list(w_mark.keys())[-1]
        latest_w = w_mark[latest_date]
        df_w = pd.DataFrame(latest_w.items(), columns=["Ticker", "Weight"])
        fig_pie = px.pie(df_w, values="Weight", names="Ticker", hole=0.4)
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Alocação — Macro Tilt")
        latest_date_mc = list(h_macro.keys())[-1]
        latest_data_mc = h_macro[latest_date_mc]
        df_w_mc = pd.DataFrame(latest_data_mc["weights"].items(), columns=["Ticker", "Weight"])
        fig_pie_mc = px.pie(df_w_mc, values="Weight", names="Ticker", hole=0.4)
        fig_pie_mc.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie_mc, use_container_width=True)
        
        st.info(f"**Score Macro Atual:** {latest_data_mc['macro_score']:.2f}")
        st.info(f"**Tilt Aplicado:** {latest_data_mc['tilt']:.1%}")

else:
    st.warning("Aguardando geração dos primeiros dados históricos...")
