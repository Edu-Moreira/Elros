"use client";

import React, { useEffect, useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, Activity, PieChart as PieIcon, ShieldCheck, Globe, DollarSign, RefreshCw } from 'lucide-react';
// @ts-ignore
import * as Papa from 'papaparse';

export default function Dashboard() {
  const [rawData, setRawData] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [currency, setCurrency] = useState<'USD' | 'BRL'>('USD');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAll() {
      try {
        const [m_res, mc_res, b_res, br_res] = await Promise.all([
          fetch('/data/markowitz_v2_nav.csv').then(r => r.text()),
          fetch('/data/macro_v2_nav.csv').then(r => r.text()),
          fetch('/data/benchmark_v2_nav.csv').then(r => r.text()),
          fetch('/data/br_data.csv').then(r => r.text())
        ]);

        const m = Papa.parse(m_res, { header: true }).data;
        const mc = Papa.parse(mc_res, { header: true }).data;
        const b = Papa.parse(b_res, { header: true }).data;
        const br = Papa.parse(br_res, { header: true }).data;

        setRawData({ m, mc, b, br });
        processData(currency, { m, mc, b, br });
        setLoading(false);
      } catch (e) {
        console.error(e);
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  const processData = (curr: 'USD' | 'BRL', sets: any) => {
    if (!sets) return;
    const { m, mc, b, br } = sets;

    // Encontrar data de início real dos fundos (onde m != 100)
    const firstValidIdx = m.findIndex((row: any) => parseFloat(Object.values(row)[1] as string) !== 100);
    const startIdx = firstValidIdx === -1 ? 0 : firstValidIdx;
    
    const slice_m = m.slice(startIdx);
    const slice_mc = mc.slice(startIdx);
    const slice_b = b.slice(startIdx);
    const slice_br = br.filter((r: any) => r.Date >= slice_m[0].Date);

    const merged = slice_m.map((row: any, i: number) => {
      const date = row.Date;
      const nav_m = parseFloat(Object.values(row)[1] as string);
      const nav_mc = parseFloat(Object.values(slice_mc[i] || {})[1] as string) || 100;
      const nav_b = parseFloat(Object.values(slice_b[i] || {})[1] as string) || 100;
      
      const br_row = slice_br.find((r: any) => r.Date === date) || slice_br[i] || {};
      const ptax = parseFloat(br_row.PTAX) || 5.0;
      const ibov = parseFloat(br_row.IBOV) || 100000;
      const cdi = parseFloat(br_row.CDI_NAV) || 100;

      const ptax_start = parseFloat(slice_br[0]?.PTAX) || ptax;
      const ibov_start = parseFloat(slice_br[0]?.IBOV) || ibov;
      const cdi_start = parseFloat(slice_br[0]?.CDI_NAV) || cdi;

      if (curr === 'BRL') {
        return {
          date,
          markowitz: (nav_m * ptax / ptax_start),
          macro: (nav_mc * ptax / ptax_start),
          bench: (nav_b * ptax / ptax_start),
          ibovespa: (ibov / ibov_start) * 100,
          cdi: (cdi / cdi_start) * 100
        };
      } else {
        return {
          date,
          markowitz: nav_m,
          macro: nav_mc,
          bench: nav_b,
          ibovespa: (ibov / ptax) / (ibov_start / ptax_start) * 100,
          cdi: (cdi / ptax) / (cdi_start / ptax_start) * 100
        };
      }
    });

    setChartData(merged.filter(d => d.date));
  };

  const handleCurrencyChange = (c: 'USD' | 'BRL') => {
    setCurrency(c);
    processData(c, rawData);
  };

  if (loading) return <div className="dashboard-container">Sincronizando dados globais...</div>;

  const latest = chartData[chartData.length - 1] || {};

  return (
    <div className="dashboard-container">
      <nav style={{ display: 'flex', gap: '2rem', marginBottom: '3rem', borderBottom: '1px solid var(--card-border)', paddingBottom: '1rem' }}>
        <button onClick={() => setActiveTab('dashboard')} className="nav-link" style={{ background: 'none', border: 'none', color: activeTab === 'dashboard' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'dashboard' ? 'bold' : 'normal' }}>📊 Dashboard</button>
        <button onClick={() => setActiveTab('markowitz')} className="nav-link" style={{ background: 'none', border: 'none', color: activeTab === 'markowitz' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'markowitz' ? 'bold' : 'normal' }}>📈 Markowitz</button>
        <button onClick={() => setActiveTab('macro')} className="nav-link" style={{ background: 'none', border: 'none', color: activeTab === 'macro' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'macro' ? 'bold' : 'normal' }}>🌍 Macro Tilt</button>
      </nav>

      {activeTab === 'dashboard' && (
        <>
          <header className="header">
            <div>
              <h1>Elros Dashboard</h1>
              <p style={{ color: 'var(--muted)' }}>Evolução Patrimonial Normalizada em 100</p>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button 
                onClick={() => handleCurrencyChange('USD')}
                style={{ padding: '0.5rem 1rem', borderRadius: '0.5rem', border: '1px solid var(--card-border)', cursor: 'pointer', background: currency === 'USD' ? 'var(--primary)' : 'transparent' }}
              >USD</button>
              <button 
                onClick={() => handleCurrencyChange('BRL')}
                style={{ padding: '0.5rem 1rem', borderRadius: '0.5rem', border: '1px solid var(--card-border)', cursor: 'pointer', background: currency === 'BRL' ? 'var(--primary)' : 'transparent' }}
              >BRL</button>
            </div>
          </header>

          <div className="grid">
            <div className="card">
              <p style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>MARKOWITZ V2</p>
              <div className="metric-value">{(latest.markowitz || 100).toFixed(2)}</div>
            </div>
            <div className="card">
              <p style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>IBOVESPA ({currency})</p>
              <div className="metric-value">{(latest.ibovespa || 100).toFixed(2)}</div>
            </div>
            <div className="card">
              <p style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>CDI ({currency})</p>
              <div className="metric-value">{(latest.cdi || 100).toFixed(2)}</div>
            </div>
          </div>

          <div className="chart-container">
            <div style={{ width: '100%', height: 450 }}>
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2e" vertical={false} />
                  <XAxis dataKey="date" stroke="#71717a" minTickGap={50} />
                  <YAxis stroke="#71717a" domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ background: '#141417', border: '1px solid #2a2a2e' }} />
                  <Legend />
                  <Line type="monotone" dataKey="markowitz" name="Markowitz" stroke="#6366f1" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="macro" name="Macro Tilt" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="ibovespa" name="IBOV" stroke="#ef4444" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="cdi" name="CDI" stroke="#ffffff" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {activeTab === 'markowitz' && (
        <div className="card" style={{ padding: '3rem' }}>
          <h1 style={{ color: 'var(--primary)' }}>Markowitz QF</h1>
          <p style={{ marginTop: '1rem', lineHeight: '1.8' }}>A tese foca na maximização do Retorno Ajustado ao Risco (Sharpe). O portfólio é rebalanceado mensalmente buscando a Fronteira Eficiente, com restrições rígidas de diversificação em 24 ativos globais.</p>
        </div>
      )}
      
      {activeTab === 'macro' && (
        <div className="card" style={{ padding: '3rem' }}>
          <h1 style={{ color: 'var(--secondary)' }}>Macro Tilt QF</h1>
          <p style={{ marginTop: '1rem', lineHeight: '1.8' }}>A tese foca na captura de Alpha através de Regimes Econômicos. O fundo ajusta a exposição em ativos de risco dependendo de indicadores como PMI, VIX e Curva de Juros.</p>
        </div>
      )}
    </div>
  );
}
