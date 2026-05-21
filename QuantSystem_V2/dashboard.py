import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import config
from datetime import datetime

st.set_page_config(page_title="Elros Quant V2", layout="wide")

# --- NAVEGAÇÃO ---
st.sidebar.title("🧙‍♂️ Elros Quant System")
page = st.sidebar.selectbox("Navegação", ["📊 Dashboard", "📈 Pitch: Markowitz QF", "🌍 Pitch: Macro Tilt QF"])

def load_v2_data():
    try:
        def read_clean(name):
            df = pd.read_csv(f"{config.OUTPUT_DIR}/{name}", index_col=0, parse_dates=True)
            df.index = df.index.tz_localize(None)
            return df.ffill().bfill()
        m_nav = read_clean("markowitz_v2_nav.csv")
        mc_nav = read_clean("macro_v2_nav.csv")
        b_nav = read_clean("benchmark_v2_nav.csv")
        br_data = read_clean("br_data.csv")
        with open(f"{config.OUTPUT_DIR}/weights_markowitz_v2.json", "r") as f: w_mark = json.load(f)
        with open(f"{config.OUTPUT_DIR}/history_macro_v2.json", "r") as f: h_macro = json.load(f)
        return m_nav, mc_nav, b_nav, br_data, w_mark, h_macro
    except:
        return None, None, None, None, None, None

m_nav, mc_nav, b_nav, br_data, w_mark, h_macro = load_v2_data()

# =================================================================
# PÁGINA: DASHBOARD
# =================================================================
if page == "📊 Dashboard":
    if m_nav is not None:
        real_start_date = m_nav[m_nav.iloc[:,0] != 100.0].index.min()
        if pd.isna(real_start_date): real_start_date = m_nav.index[0]
        
        currency = st.sidebar.radio("💰 Moeda", ["USD", "BRL"])
        
        # Filtros
        m_curr = m_nav[m_nav.index >= real_start_date]
        mc_curr = mc_nav[mc_nav.index >= real_start_date]
        b_curr = b_nav[b_nav.index >= real_start_date]
        br_curr = br_data[br_data.index >= real_start_date]
        ptax = br_curr['PTAX']

        def to_100(series): return (series / series.iloc[0]) * 100

        if currency == "BRL":
            plot_m = to_100(m_curr.iloc[:, 0] * ptax)
            plot_mc = to_100(mc_curr.iloc[:, 0] * ptax)
            plot_b = to_100(b_curr.iloc[:, 0] * ptax)
            plot_ibov = to_100(br_curr['IBOV'])
            plot_cdi = to_100(br_curr['CDI_NAV'])
        else:
            plot_m = to_100(m_curr.iloc[:, 0])
            plot_mc = to_100(mc_curr.iloc[:, 0])
            plot_b = to_100(b_curr.iloc[:, 0])
            plot_ibov = to_100(br_curr['IBOV'] / ptax)
            plot_cdi = to_100(br_curr['CDI_NAV'] / ptax)

        all_navs = pd.DataFrame({
            "Markowitz V2": plot_m, "Macro Tilt V2": plot_mc, 
            "Bench Neutral (60/40)": plot_b, "IBOVESPA": plot_ibov, "CDI": plot_cdi
        }).ffill().bfill()

        st.title(f"📊 Dashboard Quantitativo")
        st.caption(f"Visualização em {currency} | Início em {real_start_date.strftime('%d/%m/%Y')}")

        selected = st.multiselect("Comparativo", all_navs.columns.tolist(), default=["Markowitz V2", "IBOVESPA"])
        if selected:
            st.plotly_chart(px.line(all_navs[selected]).update_layout(template="plotly_dark", hovermode="x unified"), use_container_width=True)

        st.markdown("### 📅 Rentabilidade Mensal")
        target = st.selectbox("Ativo para análise", all_navs.columns)
        if target:
            s = all_navs[target]
            m_series = s.resample('ME').last()
            m_rets = m_series.pct_change().dropna()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Retorno Acumulado", f"{(s.iloc[-1]/100-1):.1%}")
            c2.metric("Sharpe Ratio", f"{(m_rets.mean()*12 - 0.05)/(m_rets.std()*12**0.5):.2f}")
            c3.metric("Drawdown Máximo", f"{(s/s.cummax()-1).min():.1%}")

            df_h = m_rets.to_frame(name='r')
            df_h['Ano'], df_h['Mês'] = df_h.index.year, df_h.index.month
            tb = df_h.pivot(index='Ano', columns='Mês', values='r')
            tb.columns = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][:len(tb.columns)]
            tb['Total'] = (1+tb).prod(axis=1)-1
            st.dataframe(tb.style.format("{:.2%}")
                         .background_gradient(cmap='RdYlGn', axis=None, low=0.4, high=0.4)
                         .highlight_null(color='transparent'), use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 Alocação Atual por Ativo")
        latest_date = list(w_mark.keys())[-1]
        df_w = pd.DataFrame(w_mark[latest_date].items(), columns=["Ativo", "Peso"]).sort_values("Peso", ascending=False)
        st.plotly_chart(px.bar(df_w, x="Ativo", y="Peso", color="Peso", color_continuous_scale="Viridis"), use_container_width=True)

    else:
        st.info("Execute 'python QuantSystem_V2/run_all.py' para gerar os dados.")

# =================================================================
# PÁGINA: PITCH MARKOWITZ
# =================================================================
elif page == "📈 Pitch: Markowitz QF":
    st.title("📈 Markowitz Quantitative Fund (MQF)")
    st.subheader("Otimização de Fronteira Eficiente com Restrições Institucionais")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### A Tese
        O **Markowitz QF** é fundamentado na Teoria Moderna de Portfólio (MPT). O objetivo não é apenas encontrar os ativos com maior retorno, mas sim a combinação de ativos que oferece o **maior retorno para cada unidade de risco (Sharpe Ratio)**.
        
        ### Diferenciais Estratégicos
        1. **Estimação Robusta**: Utilizamos o estimador *Ledoit-Wolf Shrinkage* para a matriz de covariância, reduzindo ruídos estatísticos e evitando que o modelo se torne sensível demais a outliers históricos.
        2. **Universo Granular (24 ativos)**: Diferente de fundos globais genéricos, operamos na granularidade de países (EUA, Japão, China, Índia, Europa) e fatores de renda fixa (Treasuries por duração, IG Corp, EM Debt).
        3. **Gestão de Restrições**: 
           - **Individual**: Nenhum ativo (exceto IVV) pode exceder 10%, forçando a diversificação.
           - **Classe**: Mantemos um equilíbrio estrutural entre Equity e Fixed Income, garantindo que o fundo nunca se torne "monolítico".
        
        ### Para quem é este fundo?
        Para investidores que buscam a "alocação matemática ideal", sem vieses emocionais, focando em diversificação global sistemática.
        """)
    with col2:
        st.info("**Objetivo:** Maximização do Sharpe Ratio")
        st.info("**Rebalanceamento:** Mensal")
        st.info("**Universo:** 24 ETFs Globais")
        st.success("**Benchmark Alvo:** Global 60/40")

# =================================================================
# PÁGINA: PITCH MACRO TILT
# =================================================================
elif page == "🌍 Pitch: Macro Tilt QF":
    st.title("🌍 Macro Tilt Quantitative Fund (MTQF)")
    st.subheader("Alocação Adaptativa baseada em Regimes Econômicos")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### A Tese
        O mercado financeiro não é estático; ele se move em ciclos. O **Macro Tilt QF** parte de uma carteira neutra (60% ações / 40% renda fixa) e aplica "tilts" (desvios) baseados na saúde da economia global.
        
        ### Como funciona o Scorecard Macro?
        O fundo monitora 5 dimensões críticas em tempo real:
        - **Crescimento (PMI)**: Atividade industrial e surpresas econômicas.
        - **Inflação (CPI)**: Pressão de preços e seu impacto nos valuations.
        - **Risco (VIX)**: O "termômetro do medo" dos investidores.
        - **Curva de Juros (T10Y2Y)**: Expectativas de recessão ou expansão.
        - **Crédito (HY Spreads)**: Percepção de risco de default no mercado corporativo.
        
        ### Dinâmica de Alocação
        - **Regime Bullish (Score > 0)**: O fundo aumenta a exposição em ações (overweight), capturando momentos de expansão.
        - **Regime Bearish (Score < 0)**: O fundo se protege aumentando a renda fixa (flight to quality), mitigando drawdowns em crises.
        
        ### Para quem é este fundo?
        Para investidores que acreditam que a gestão ativa da exposição ao risco (Beta Management) é a chave para sobreviver a ciclos de mercado e capturar alpha macroeconômico.
        """)
    with col2:
        st.info("**Objetivo:** Retorno absoluto e proteção de capital")
        st.info("**Mecanismo:** Scorecard Multidimensional")
        st.info("**Base:** Carteira Neutra Granular")
        st.success("**Tilt Máximo:** +/- 10% por classe")
