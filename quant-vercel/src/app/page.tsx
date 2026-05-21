"use client";

import React, { useEffect, useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar
} from 'recharts';
import { TrendingUp, Activity, PieChart as PieIcon, ShieldCheck, ClipboardList, Globe } from 'lucide-react';
import Papa from 'papaparse';

export default function Dashboard() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    async function loadData() {
      try {
        const [m_res, mc_res, b_res] = await Promise.all([
          fetch('/data/markowitz_v2_nav.csv').then(r => r.text()),
          fetch('/data/macro_v2_nav.csv').then(r => r.text()),
          fetch('/data/benchmark_v2_nav.csv').then(r => r.text())
        ]);

        const m_parsed = Papa.parse(m_res, { header: true }).data;
        const mc_parsed = Papa.parse(mc_res, { header: true }).data;
        const b_parsed = Papa.parse(b_res, { header: true }).data;

        const merged: any[] = [];
        const entries = Math.min(m_parsed.length, mc_parsed.length, b_parsed.length);
        
        for (let i = 0; i < entries; i++) {
          const m: any = m_parsed[i];
          const mc: any = mc_parsed[i];
          const b: any = b_parsed[i];
          if (m.Date) {
            merged.push({
              date: m.Date,
              markowitz: parseFloat(Object.values(m)[1] as string),
              macro: parseFloat(Object.values(mc)[1] as string),
              bench: parseFloat(Object.values(b)[1] as string)
            });
          }
        }
        setData(merged.filter(d => !isNaN(d.markowitz)));
        setLoading(false);
      } catch (e) {
        console.error("Error loading data", e);
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div className="dashboard-container">Carregando dados...</div>;

  const latest = data[data.length - 1] || {};

  return (
    <div className="dashboard-container">
      <nav style={{ display: 'flex', gap: '2rem', marginBottom: '3rem', borderBottom: '1px solid var(--card-border)', paddingBottom: '1rem' }}>
        <button onClick={() => setActiveTab('dashboard')} className="nav-link" style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTab === 'dashboard' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'dashboard' ? 'bold' : 'normal' }}>📊 Dashboard</button>
        <button onClick={() => setActiveTab('markowitz')} className="nav-link" style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTab === 'markowitz' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'markowitz' ? 'bold' : 'normal' }}>📈 Markowitz Pitch</button>
        <button onClick={() => setActiveTab('macro')} className="nav-link" style={{ background: 'none', border: 'none', cursor: 'pointer', color: activeTab === 'macro' ? 'var(--primary)' : 'var(--muted)', fontWeight: activeTab === 'macro' ? 'bold' : 'normal' }}>🌍 Macro Tilt Pitch</button>
      </nav>

      {activeTab === 'dashboard' && (
        <>
          <header className="header">
            <div>
              <h1>Elros Quant V2</h1>
              <p style={{ color: 'var(--muted)' }}>Performance em Tempo Real</p>
            </div>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <ShieldCheck color="var(--secondary)" />
              <span>Vercel Live</span>
            </div>
          </header>

          <div className="grid">
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <TrendingUp size={20} color="var(--primary)" />
                <span>Markowitz V2</span>
              </div>
              <div className="metric-value">{(latest.markowitz || 100).toFixed(2)}</div>
              <p style={{ color: 'var(--muted)' }}>NAV Base 100</p>
            </div>

            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Activity size={20} color="var(--secondary)" />
                <span>Macro Tilt V2</span>
              </div>
              <div className="metric-value">{(latest.macro || 100).toFixed(2)}</div>
              <p style={{ color: 'var(--muted)' }}>NAV Base 100</p>
            </div>

            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <PieIcon size={20} color="var(--accent)" />
                <span>Bench 60/40</span>
              </div>
              <div className="metric-value">{(latest.bench || 100).toFixed(2)}</div>
              <p style={{ color: 'var(--muted)' }}>NAV Base 100</p>
            </div>
          </div>

          <div className="chart-container">
            <h3>Performance Comparativa (USD)</h3>
            <div style={{ width: '100%', height: 400, marginTop: '2rem' }}>
              <ResponsiveContainer>
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2e" vertical={false} />
                  <XAxis dataKey="date" stroke="#71717a" tick={{fontSize: 12}} />
                  <YAxis stroke="#71717a" domain={['auto', 'auto']} tick={{fontSize: 12}} />
                  <Tooltip contentStyle={{ background: '#141417', border: '1px solid #2a2a2e' }} />
                  <Legend verticalAlign="top"/>
                  <Line type="monotone" dataKey="markowitz" name="Markowitz" stroke="#6366f1" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="macro" name="Macro Tilt" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="bench" name="Bench Neutro" stroke="#f59e0b" strokeWidth={1.5} dashArray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {activeTab === 'markowitz' && (
        <div className="card" style={{ padding: '3rem' }}>
          <h1 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>📈 Markowitz Quantitative Fund</h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--muted)', marginBottom: '2rem' }}>Otimização de Fronteira Eficiente</p>
          <div style={{ lineHeight: '1.8', color: '#d1d1d6' }}>
            <h3 style={{ color: 'white', marginTop: '1.5rem' }}>A Tese</h3>
            <p>O Markowitz QF utiliza a Teoria Moderna de Portfólio para encontrar a alocação de risco ideal. Utilizamos o estimador Ledoit-Wolf para garantir que a matriz de covariância seja robusta a ruídos estatísticos.</p>
            
            <h3 style={{ color: 'white', marginTop: '1.5rem' }}>Estratégia</h3>
            <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem' }}>
              <li>Universo Granular: 24 ETFs de países e fatores.</li>
              <li>Rebalanceamento Mensal Sistemático.</li>
              <li>Maximização do Sharpe Ratio com restrições institucionais.</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'macro' && (
        <div className="card" style={{ padding: '3rem' }}>
          <h1 style={{ color: 'var(--secondary)', marginBottom: '1rem' }}>🌍 Macro Tilt Quantitative Fund</h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--muted)', marginBottom: '2rem' }}>Alocação Adaptativa a Ciclos</p>
          <div style={{ lineHeight: '1.8', color: '#d1d1d6' }}>
            <h3 style={{ color: 'white', marginTop: '1.5rem' }}>A Tese</h3>
            <p>O Macro Tilt QF foca no Gerenciamento de Beta. Ele identifica se o regime econômico global é de expansão ou contração e ajusta o nível de exposição em ativos de risco (Ações) vs Ativos de Proteção (Bonds).</p>
            
            <h3 style={{ color: 'white', marginTop: '1.5rem' }}>Indicadores Monitorados</h3>
            <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem' }}>
              <li>Crescimento: PMI Industrial Global.</li>
              <li>Sentimento: VIX (Volatilidade Implícita).</li>
              <li>Moeda e Juros: Diferencial de taxas e inflação.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
