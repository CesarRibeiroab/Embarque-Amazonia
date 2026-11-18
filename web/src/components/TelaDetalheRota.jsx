import React, { useState, useEffect, useRef } from 'react';
import './TelaDetalheRota.css';
import {
  formatarMoeda,
  formatarDuracao,
  formatarData,
  formatarRecencia,
  formatarConexoes,
  corCategoriaModal,
  estiloSelo,
} from '../utils/format.js';
import { formatarHorarioComDia, montarLinhaDoTempo } from '../utils/timeline.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function TelaDetalheRota({
  rota,
  dataViagem,
  onVoltar,
  onAbrirTrecho,
}) {
  const [dadosRota, setDadosRota] = useState(rota || null);
  const [carregando, setCarregando] = useState(!rota);
  const [erro, setErro] = useState(null);
  const tentouCompletarRef = useRef(false);

  // Formata chegada prevista ISO (YYYY-MM-DDTHH:MM -> DD/MM/AAAA às HH:MM)
  function formatarChegadaPrevista(isoStr, chegadaHora, offset) {
    if (isoStr && typeof isoStr === 'string' && isoStr.includes('T')) {
      const [dataPart, horaPart] = isoStr.split('T');
      return `Chegada prevista: ${formatarData(dataPart)} às ${horaPart.slice(0, 5)}`;
    }
    if (chegadaHora) {
      return `Chegada prevista: ${formatarHorarioComDia(chegadaHora, offset)}`;
    }
    return null;
  }

  // Cor do modal respeitando categoria oficial ou inferência
  function obterCorModal(trecho) {
    if (trecho.modal_categoria === 'aereo') return '#6A4C93';
    if (trecho.modal_categoria === 'rodoviario') return '#D9822B';
    if (trecho.modal_categoria === 'fluvial') return '#1F6FB2';
    return corCategoriaModal(trecho.modal_nome);
  }

  // Efeito 1: Busca via API caso a rota venha vazia (deep link #/rota/<id>)
  useEffect(() => {
    if (rota) {
      setDadosRota(rota);
      setCarregando(false);
      return;
    }

    // Tenta extrair id e data do hash da URL (#/rota/<id>?data=...)
    const hash = window.location.hash || '';
    const match = hash.match(/#\/rota\/([^?]+)(?:\?data=([^&]+))?/);
    if (!match) {
      setErro('Nenhuma rota foi selecionada para exibição.');
      setCarregando(false);
      return;
    }

    const rotaId = match[1];
    const dataParam = match[2] || dataViagem || '';
    const url = `${API_BASE}/rotas/${rotaId}${dataParam ? `?data=${encodeURIComponent(dataParam)}` : ''}`;

    setCarregando(true);
    setErro(null);

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          return res.json().then((body) => {
            throw new Error(body.mensagem || `Erro ${res.status}: não foi possível carregar a rota.`);
          });
        }
        return res.json();
      })
      .then((data) => {
        setDadosRota(data);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message || 'Falha na comunicação com o servidor da API.');
        setCarregando(false);
      });
  }, [rota, dataViagem]);

  // Efeito 2: Se a rota já veio da prop mas sem horários detalhados (formato legado), tenta completar 1 vez
  useEffect(() => {
    if (!dadosRota || tentouCompletarRef.current || dadosRota._origemExemplo) {
      return;
    }

    const temHorariosDetalhados = dadosRota.trechos && dadosRota.trechos.some((t) => t.hora_partida);
    if (!temHorariosDetalhados && dadosRota.id) {
      tentouCompletarRef.current = true;
      const dataParam = dadosRota.data_viagem || dataViagem || '';
      const url = `${API_BASE}/rotas/${dadosRota.id}${dataParam ? `?data=${encodeURIComponent(dataParam)}` : ''}`;

      fetch(url)
        .then((res) => (res.ok ? res.json() : null))
        .then((dadosCompletos) => {
          if (dadosCompletos && dadosCompletos.trechos) {
            setDadosRota(dadosCompletos);
          }
        })
        .catch(() => {
          // Se falhar, mantém a rota que já possui sem quebrar a tela
        });
    }
  }, [dadosRota, dataViagem]);

  const handleVoltar = () => {
    if (onVoltar) {
      onVoltar();
    } else {
      window.location.hash = '#/';
    }
  };

  if (carregando) {
    return (
      <main className="detalhe-rota-container" aria-label="Detalhes da rota">
        <header className="detalhe-nav-header">
          <button type="button" className="btn-voltar" onClick={handleVoltar}>
            ← Resultados
          </button>
        </header>
        <div className="detalhe-estado-box">
          <p className="detalhe-estado-texto">Carregando detalhes da rota...</p>
        </div>
      </main>
    );
  }

  if (erro || !dadosRota) {
    return (
      <main className="detalhe-rota-container" aria-label="Detalhes da rota">
        <header className="detalhe-nav-header">
          <button type="button" className="btn-voltar" onClick={handleVoltar}>
            ← Voltar
          </button>
        </header>
        <div className="detalhe-estado-box">
          <p className="detalhe-estado-erro">{erro || 'Rota não localizada.'}</p>
          <button type="button" className="btn-voltar" onClick={handleVoltar}>
            Retornar à busca
          </button>
        </div>
      </main>
    );
  }

  const itensLinhaDoTempo = montarLinhaDoTempo(dadosRota);
  const dataExibicao = dadosRota.data_viagem || dataViagem;
  const textoChegada = formatarChegadaPrevista(
    dadosRota.chegada_estimada_iso,
    dadosRota.chegada_estimada,
    dadosRota.chegada_dia_offset
  );

  return (
    <main className="detalhe-rota-container" aria-label="Detalhes da rota">
      {/* Barra de Navegação */}
      <header className="detalhe-nav-header">
        <button
          type="button"
          className="btn-voltar"
          onClick={handleVoltar}
          aria-label="Voltar para a lista de resultados"
        >
          ← Resultados
        </button>
        {dadosRota._origemExemplo && (
          <span className="badge-exemplo-local" title="Dados carregados de fixture local">
            Exemplo local, sem API
          </span>
        )}
      </header>

      {/* Card Resumo do Cabeçalho */}
      <section className="detalhe-card-resumo" aria-label="Resumo da rota">
        <div className="resumo-titulo-bloco">
          <h1 className="resumo-rota-titulo">
            {dadosRota.origem_nome} → {dadosRota.destino_nome}
          </h1>
          <span className="resumo-preco">{formatarMoeda(dadosRota.preco_total)}</span>
        </div>

        <div className="resumo-metadados">
          {dataExibicao && (
            <span className="resumo-meta-item">
              📅 {formatarData(dataExibicao)}
            </span>
          )}
          <span className="resumo-meta-item">
            ⏱️ {formatarDuracao(dadosRota.duracao_total_minutos)}
          </span>
          <span className="resumo-meta-item">
            🔄 {dadosRota.numero_trechos} {dadosRota.numero_trechos === 1 ? 'trecho' : 'trechos'} · {formatarConexoes(dadosRota.numero_conexoes)}
          </span>
          <span className="resumo-meta-item">
            🕒 {formatarRecencia(dadosRota.dias_desde_atualizacao)}
          </span>
        </div>

        {textoChegada && (
          <div className="resumo-chegada-prevista">
            <strong>{textoChegada}</strong>
          </div>
        )}

        {Array.isArray(dadosRota.selo) && dadosRota.selo.length > 0 && (
          <div className="resumo-selos-container">
            {dadosRota.selo.map((s) => (
              <span key={s} className="selo-badge" style={estiloSelo(s)}>
                {s}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* Linha do Tempo Vertical */}
      <section className="timeline-secao" aria-label="Linha do tempo intermodal">
        <h2 className="timeline-titulo">Itinerário e Conexões</h2>
        <ol className="timeline-lista">
          {itensLinhaDoTempo.map((item, idx) => {
            if (item.tipo === 'conexao') {
              return (
                <li key={`conexao-${idx}`} className="conexao-item-li">
                  <div className="conexao-card">
                    <div className="conexao-topo">
                      <span>
                        Conexão em {item.local}: {formatarDuracao(item.minutos)}
                      </span>
                      {item.conexaoCurta && (
                        <span className="badge-conexao-curta">Conexão curta</span>
                      )}
                    </div>
                    {item.horaChegada && item.horaPartidaProx && (
                      <span className="conexao-horarios">
                        ({item.horaChegada} → {item.horaPartidaProx})
                      </span>
                    )}
                  </div>
                </li>
              );
            }

            const tr = item.trecho;
            const horaPartidaFormatada = formatarHorarioComDia(tr.hora_partida, tr.partida_dia_offset);
            const horaChegadaFormatada = formatarHorarioComDia(tr.hora_chegada_estimada, tr.chegada_dia_offset);
            const temHorarios = horaPartidaFormatada !== 'Horário não informado';
            const obsSazonal = tr.regime_hidrico_observacao || tr.observacao_regime;

            return (
              <li key={`trecho-${tr.id || idx}`} className="trecho-item-li">
                <button
                  type="button"
                  className="trecho-btn-card"
                  onClick={() => onAbrirTrecho && onAbrirTrecho(tr, dadosRota)}
                  aria-label={`Ver detalhes do trecho ${tr.origem_nome} para ${tr.destino_nome} via ${tr.modal_nome}`}
                >
                  <div className="trecho-header-row">
                    <span
                      className="trecho-modal-tag"
                      style={{ backgroundColor: obterCorModal(tr) }}
                    >
                      {tr.modal_nome}
                    </span>
                    <span className="trecho-operador">{tr.operador_nome}</span>
                  </div>

                  <div className="trecho-trajeto-row">
                    <span className="trecho-trajeto-nome">
                      {tr.origem_nome} → {tr.destino_nome}
                    </span>
                    {(tr.terminal_origem_nome || tr.terminal_destino_nome) && (
                      <span className="trecho-terminais">
                        {tr.terminal_origem_nome || 'Origem'} → {tr.terminal_destino_nome || 'Destino'}
                      </span>
                    )}
                  </div>

                  <div className="trecho-horarios-row">
                    {temHorarios ? (
                      <span>
                        Sai {horaPartidaFormatada} · Chega {horaChegadaFormatada}
                      </span>
                    ) : (
                      <span>Horário não informado</span>
                    )}
                  </div>

                  <div className="trecho-valores-row">
                    <span>Duração: {formatarDuracao(tr.duracao_minutos)}</span>
                    <span className="trecho-tarifa">{formatarMoeda(tr.tarifa_reais)}</span>
                  </div>

                  {obsSazonal && (
                    <div className="trecho-observacao-sazonal">
                      ⚠️ {obsSazonal}
                    </div>
                  )}
                </button>
              </li>
            );
          })}
        </ol>
      </section>

      {/* Rodapé Informativo */}
      <footer className="detalhe-rodape">
        <p className="detalhe-rodape-aviso">
          Preços e horários são estimativas. Confirme com o operador.
        </p>
        <p className="detalhe-rodape-aviso">
          Dados de exemplo ilustrativos para validação acadêmica do sistema.
        </p>
      </footer>
    </main>
  );
}
