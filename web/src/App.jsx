import React, { useEffect, useState } from 'react';
import {
  corCategoriaModal,
  estiloSelo,
  formatarConexoes,
  formatarData,
  formatarDuracao,
  formatarMoeda,
  formatarRecencia,
} from './utils/format';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function App() {
  const [origem, setOrigem] = useState('Belém');
  const [destino, setDestino] = useState('Manaus');
  const [dataViagem, setDataViagem] = useState('2026-11-20');
  const [criterio, setCriterio] = useState('menor_tempo');
  const [sugestoesOrigem, setSugestoesOrigem] = useState([]);
  const [sugestoesDestino, setSugestoesDestino] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [expandidas, setExpandidas] = useState({});

  const carregarSugestoes = async (termo, setter) => {
    try {
      const q = termo && termo.trim() ? `?busca=${encodeURIComponent(termo.trim())}` : '';
      const res = await fetch(`${API_BASE}/localidades${q}`);
      if (!res.ok) return;
      const lista = await res.json();
      if (Array.isArray(lista)) {
        setter(lista);
      }
    } catch {
      // Autocomplete silencioso quando a API está indisponível
    }
  };

  useEffect(() => {
    carregarSugestoes('', setSugestoesOrigem);
    carregarSugestoes('', setSugestoesDestino);
  }, []);

  const handleOrigemChange = (valor) => {
    setOrigem(valor);
    carregarSugestoes(valor, setSugestoesOrigem);
  };

  const handleDestinoChange = (valor) => {
    setDestino(valor);
    carregarSugestoes(valor, setSugestoesDestino);
  };

  const alternarTrechos = (rotaId) => {
    setExpandidas((prev) => ({ ...prev, [rotaId]: !prev[rotaId] }));
  };

  const buscarRotas = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setErro(null);
    setExpandidas({});

    try {
      const params = new URLSearchParams({
        origem: origem.trim(),
        destino: destino.trim(),
        criterio,
      });
      if (dataViagem) {
        params.append('data', dataViagem);
      }

      const res = await fetch(`${API_BASE}/rotas?${params.toString()}`);
      let data = null;
      try {
        data = await res.json();
      } catch {
        data = null;
      }

      if (!res.ok) {
        setErro(data?.mensagem || 'Não foi possível consultar as rotas solicitadas.');
        setResultado(null);
      } else {
        setResultado(data);
      }
    } catch {
      setErro('Não foi possível conectar à API. Verifique se o servidor FastAPI está em execução em localhost:8000.');
      setResultado(null);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <main className="app-container">
      <header className="app-header">
        <h1 className="app-title">Embarque Amazônia</h1>
        <p className="app-subtitle">
          Busca multimodal de rotas na Amazônia Legal
        </p>
      </header>

      <div className="aviso-ilustrativo" role="note">
        Dados de exemplo ilustrativos. Preços e horários são estimativas.
      </div>

      <form onSubmit={buscarRotas} className="search-form">
        <div className="field-group">
          <label htmlFor="campo-origem" className="field-label">
            Origem
          </label>
          <input
            id="campo-origem"
            type="text"
            list="sugestoes-origem"
            className="field-input"
            value={origem}
            onChange={(e) => handleOrigemChange(e.target.value)}
            placeholder="Ex.: Belém"
            autoComplete="off"
            required
          />
          <datalist id="sugestoes-origem">
            {sugestoesOrigem.map((loc) => (
              <option key={loc.id} value={loc.nome} label={`${loc.nome} (${loc.uf})`} />
            ))}
          </datalist>
        </div>

        <div className="field-group">
          <label htmlFor="campo-destino" className="field-label">
            Destino
          </label>
          <input
            id="campo-destino"
            type="text"
            list="sugestoes-destino"
            className="field-input"
            value={destino}
            onChange={(e) => handleDestinoChange(e.target.value)}
            placeholder="Ex.: Manaus"
            autoComplete="off"
            required
          />
          <datalist id="sugestoes-destino">
            {sugestoesDestino.map((loc) => (
              <option key={loc.id} value={loc.nome} label={`${loc.nome} (${loc.uf})`} />
            ))}
          </datalist>
        </div>

        <div className="field-row">
          <div className="field-group">
            <label htmlFor="campo-data" className="field-label">
              Data
            </label>
            <input
              id="campo-data"
              type="date"
              className="field-input"
              value={dataViagem}
              onChange={(e) => setDataViagem(e.target.value)}
            />
          </div>

          <div className="field-group">
            <label htmlFor="campo-criterio" className="field-label">
              Critério
            </label>
            <select
              id="campo-criterio"
              className="field-input"
              value={criterio}
              onChange={(e) => setCriterio(e.target.value)}
            >
              <option value="menor_tempo">Menor tempo</option>
              <option value="menor_custo">Menor custo</option>
              <option value="mais_confiavel">Mais confiável</option>
            </select>
          </div>
        </div>

        <button type="submit" disabled={carregando} className="submit-btn">
          {carregando ? 'Buscando opções...' : 'Buscar rotas'}
        </button>
      </form>

      {carregando && (
        <div className="status-box status-loading" role="status">
          Consultando rotas multimodais disponíveis...
        </div>
      )}

      {erro && (
        <div className="status-box status-error" role="alert">
          {erro}
        </div>
      )}

      {!carregando && resultado && (
        <section aria-live="polite">
          <h2 className="results-title">
            {resultado.origem} → {resultado.destino} ({resultado.total_opcoes}{' '}
            {resultado.total_opcoes === 1 ? 'opção' : 'opções'})
          </h2>

          {resultado.rotas.length === 0 ? (
            <div className="status-box status-empty">
              Nenhuma rota encontrada para este itinerário na data selecionada.
            </div>
          ) : (
            <div className="cards-list">
              {resultado.rotas.map((rota) => {
                const aberta = Boolean(expandidas[rota.id]);
                const duracaoExibida = formatarDuracao(rota.duracao_total_minutos);
                const recenciaExibida = formatarRecencia(rota.dias_desde_atualizacao);
                const dataIsoFormatada = formatarData(rota.data_atualizacao_iso);

                return (
                  <article key={rota.id} className="route-card">
                    <div className="card-top">
                      <div className="modais-wrap">
                        {rota.modais.map((modalNome, idx) => (
                          <span
                            key={`${rota.id}-m-${idx}`}
                            className="modal-badge"
                            style={{ backgroundColor: corCategoriaModal(modalNome) }}
                          >
                            {modalNome}
                          </span>
                        ))}
                      </div>
                      <span className="card-price">
                        {formatarMoeda(rota.preco_total)}
                      </span>
                    </div>

                    <div className="card-meta">
                      <strong>{duracaoExibida}</strong> • {rota.numero_trechos}{' '}
                      {rota.numero_trechos === 1 ? 'trecho' : 'trechos'} •{' '}
                      {formatarConexoes(rota.numero_conexoes)}
                    </div>

                    {Array.isArray(rota.selo) && rota.selo.length > 0 && (
                      <div className="selos-wrap">
                        {rota.selo.map((s, idx) => (
                          <span
                            key={`${rota.id}-s-${idx}`}
                            className="selo-badge"
                            style={estiloSelo(s)}
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="card-footer">
                      <span className="recency-text">
                        {recenciaExibida}
                        {dataIsoFormatada ? ` (${dataIsoFormatada})` : ''}
                      </span>

                      <button
                        type="button"
                        className="toggle-btn"
                        aria-expanded={aberta}
                        onClick={() => alternarTrechos(rota.id)}
                      >
                        {aberta
                          ? 'Ocultar trechos'
                          : `Ver trechos (${rota.trechos?.length ?? rota.numero_trechos})`}
                      </button>
                    </div>

                    {aberta && Array.isArray(rota.trechos) && (
                      <div className="trechos-list">
                        {rota.trechos.map((tr, idx) => (
                          <div
                            key={`${rota.id}-tr-${tr.id}-${idx}`}
                            className="trecho-item"
                            style={{ borderLeftColor: corCategoriaModal(tr.modal_nome) }}
                          >
                            <div className="trecho-header">
                              {idx + 1}. {tr.origem_nome} → {tr.destino_nome} ({tr.modal_nome})
                            </div>
                            <div className="trecho-detail">
                              <strong>Operador:</strong> {tr.operador_nome}
                            </div>
                            <div className="trecho-detail">
                              <strong>Terminais:</strong>{' '}
                              {tr.terminal_origem_nome || 'Não informado'} →{' '}
                              {tr.terminal_destino_nome || 'Não informado'}
                            </div>
                            <div className="trecho-detail">
                              <strong>Duração:</strong> {formatarDuracao(tr.duracao_minutos)} •{' '}
                              <strong>Tarifa:</strong> {formatarMoeda(tr.tarifa_reais)}
                              {tr.data_ultima_atualizacao
                                ? ` • Base: ${formatarData(tr.data_ultima_atualizacao)}`
                                : ''}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
