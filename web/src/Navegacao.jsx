import React, { useState, useEffect, Suspense } from 'react';
import App from './App.jsx';
import TelaDetalheRota from './components/TelaDetalheRota.jsx';
import { rota1OpcaoC } from './fixtures/rota1_opcao_c.js';

// Descoberta dinâmica das telas dos colegas (Herbert, Lucas e Fernando) sem acoplamento estático
const modulosTelas = import.meta.glob([
  './components/TelaFiltros.jsx',
  './components/TelaComparar.jsx',
  './components/TelaDetalheTrecho.jsx',
]);

function carregarComponenteOpcional(caminho) {
  if (modulosTelas[caminho]) {
    return React.lazy(modulosTelas[caminho]);
  }
  return null;
}

const TelaFiltrosLazy = carregarComponenteOpcional('./components/TelaFiltros.jsx');
const TelaCompararLazy = carregarComponenteOpcional('./components/TelaComparar.jsx');
const TelaDetalheTrechoLazy = carregarComponenteOpcional('./components/TelaDetalheTrecho.jsx');

function TelaNaoIntegrada({ telaCodigo, descricao, onVoltar }) {
  return (
    <main className="detalhe-rota-container" style={{ padding: 20 }} aria-label={telaCodigo}>
      <header className="detalhe-nav-header">
        <button
          type="button"
          className="btn-voltar"
          onClick={onVoltar || (() => { window.location.hash = '#/'; })}
        >
          ← Voltar
        </button>
      </header>
      <div className="detalhe-estado-box" style={{ marginTop: 24, textAlign: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 18, color: 'var(--cor-texto)' }}>
          {telaCodigo} ainda não integrada
        </h2>
        <p style={{ margin: '8px 0 0', fontSize: 13, color: 'var(--cor-texto-sec)', lineHeight: 1.45 }}>
          {descricao || 'Este módulo do protótipo visual está planejado no escopo da equipe e será exibido automaticamente assim que o arquivo for adicionado ao repositório.'}
        </p>
      </div>
    </main>
  );
}

export default function Navegacao() {
  const [hash, setHash] = useState(() => window.location.hash || '#/');
  const [rotaAtual, setRotaAtual] = useState(null);
  const [dataViagemAtual, setDataViagemAtual] = useState('');
  const [trechoAtual, setTrechoAtual] = useState(null);

  useEffect(() => {
    function onHashChange() {
      setHash(window.location.hash || '#/');
    }
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleAbrirRota = (rota, dataViagem) => {
    setRotaAtual(rota);
    if (dataViagem) setDataViagemAtual(dataViagem);
    const dataParam = dataViagem ? `?data=${encodeURIComponent(dataViagem)}` : '';
    window.location.hash = `#/rota/${rota.id}${dataParam}`;
  };

  const handleAbrirTrecho = (trecho, rota) => {
    setTrechoAtual(trecho);
    if (rota) setRotaAtual(rota);
    window.location.hash = `#/trecho/${trecho.id}`;
  };

  const handleVoltarParaBusca = () => {
    window.location.hash = '#/';
  };

  const handleVoltarParaRota = () => {
    if (rotaAtual) {
      const dataParam = dataViagemAtual ? `?data=${encodeURIComponent(dataViagemAtual)}` : '';
      window.location.hash = `#/rota/${rotaAtual.id}${dataParam}`;
    } else {
      window.location.hash = '#/';
    }
  };

  // 1. Rota de Laboratório do P06 (com fixture local, independente da API)
  if (hash === '#/lab/p06') {
    return (
      <TelaDetalheRota
        rota={rota1OpcaoC}
        dataViagem="2026-11-20"
        onVoltar={handleVoltarParaBusca}
        onAbrirTrecho={handleAbrirTrecho}
      />
    );
  }

  // 2. Rota Detalhada do P06 por ID determinístico (#/rota/<id>?data=YYYY-MM-DD)
  if (hash.startsWith('#/rota/')) {
    // Extrai dataViagem da URL caso não esteja no estado
    const matchData = hash.match(/\?data=([^&]+)/);
    const dataUrl = matchData ? decodeURIComponent(matchData[1]) : dataViagemAtual;

    return (
      <TelaDetalheRota
        rota={rotaAtual}
        dataViagem={dataUrl}
        onVoltar={handleVoltarParaBusca}
        onAbrirTrecho={handleAbrirTrecho}
      />
    );
  }

  // 3. Rota P03 — Filtros e Preferências (Herbert)
  if (hash.startsWith('#/filtros')) {
    if (TelaFiltrosLazy) {
      return (
        <Suspense fallback={<div className="detalhe-estado-box">Carregando filtros...</div>}>
          <TelaFiltrosLazy
            onFechar={handleVoltarParaBusca}
            onAplicar={handleVoltarParaBusca}
          />
        </Suspense>
      );
    }
    return (
      <TelaNaoIntegrada
        telaCodigo="Tela P03 (Filtros e Preferências)"
        onVoltar={handleVoltarParaBusca}
      />
    );
  }

  // 4. Rota P05 — Comparador de Rotas (Lucas)
  if (hash.startsWith('#/comparar')) {
    if (TelaCompararLazy) {
      return (
        <Suspense fallback={<div className="detalhe-estado-box">Carregando comparador...</div>}>
          <TelaCompararLazy
            rotas={rotaAtual ? [rotaAtual] : []}
            dataViagem={dataViagemAtual}
            onVoltar={handleVoltarParaBusca}
            onVerDetalhes={handleAbrirRota}
          />
        </Suspense>
      );
    }
    return (
      <TelaNaoIntegrada
        telaCodigo="Tela P05 (Comparador de Rotas)"
        onVoltar={handleVoltarParaBusca}
      />
    );
  }

  // 5. Rota P07 — Detalhe do Trecho (Fernando)
  if (hash.startsWith('#/trecho/')) {
    if (TelaDetalheTrechoLazy) {
      return (
        <Suspense fallback={<div className="detalhe-estado-box">Carregando trecho...</div>}>
          <TelaDetalheTrechoLazy
            trecho={trechoAtual}
            rota={rotaAtual}
            dataViagem={dataViagemAtual}
            onVoltar={handleVoltarParaRota}
          />
        </Suspense>
      );
    }
    return (
      <TelaNaoIntegrada
        telaCodigo="Tela P07 (Detalhe do Trecho)"
        onVoltar={handleVoltarParaRota}
      />
    );
  }

  // Rota padrão: #/ (Busca e Listagem de Resultados)
  return <App onAbrirRota={handleAbrirRota} />;
}
