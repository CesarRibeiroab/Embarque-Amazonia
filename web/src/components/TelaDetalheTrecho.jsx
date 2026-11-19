import React, { useState } from 'react';
import {
  corCategoriaModal,
  estiloSelo,
  formatarData,
  formatarDiasSemana,
  formatarDuracao,
  formatarHora,
  formatarMoeda,
  formatarRecencia,
} from '../utils/format';

/**
 * Dados Canônicos de Fallback:
 * Trecho 2 da Rota 1 C (Barco Regional Santarém -> Manaus operado por Amazon Star)
 * Usado para desenvolvimento e renderização isolada da Tela P07.
 */
export const TRECHO_CANONICO_SANT_MAO = {
  id: 4,
  origem_nome: 'Santarém',
  origem_uf: 'PA',
  destino_nome: 'Manaus',
  destino_uf: 'AM',
  modal_nome: 'Barco regional',
  modal_codigo: 'barco_regional',
  operador_nome: 'Amazon Star',
  operador_telefone: '(91) 90000-0000',
  terminal_origem_nome: 'Porto de Santarém',
  terminal_destino_nome: 'Porto da Manaus Moderna',
  duracao_minutos: 2520, // 42h = 1d 18h
  tarifa_reais: 210.0,
  data_ultima_atualizacao: '2026-11-07',
  hora_partida: '14:00:00',
  hora_chegada_estimada: '08:00:00',
  dias_semana_mask: 26, // Ter (2) + Qui (8) + Sex (16) = Ter, Qui e Sex
  frequencia_descricao: 'Terças, Quintas e Sextas-feiras',
  observacao_regime: 'Na vazante, a viagem pode durar mais decorrente do surgimento de bancos de areia e redução do calado no leito do Rio Amazonas.',
  fonte_dado: 'ANTAQ / Cadastro Operacional Regional',
  selo_confiabilidade: 'Mais confiável',
  acomodacoes: [
    {
      tipo: 'rede',
      regime: 'fixo',
      valor_total_reais: 210.0,
      descricao: 'Acomodação tradicional em rede no convés coletivo ventilado (levar rede própria).'
    },
    {
      tipo: 'camarote_duplo',
      regime: 'fixo',
      valor_total_reais: 900.0,
      descricao: 'Cabine privativa climatizada com beliche para 2 pessoas e tomada individual.'
    }
  ]
};

function formatarTituloAcomodacao(tipo = '') {
  switch (tipo.toLowerCase()) {
    case 'rede':
      return 'Rede';
    case 'camarote_duplo':
      return 'Camarote duplo';
    case 'camarote_quadruplo':
      return 'Camarote quádruplo';
    case 'suite':
      return 'Suíte privativa';
    case 'cadeira_inclinavel':
      return 'Cadeira inclinável';
    case 'assento_padrao':
      return 'Assento padrão';
    default:
      return tipo ? tipo.replace(/_/g, ' ') : 'Acomodação regular';
  }
}

export default function TelaDetalheTrecho({ trecho, onVoltar }) {
  const [copiado, setCopiado] = useState(false);

  // Fallback imediato no trecho canônico Santarém -> Manaus
  const t = trecho || TRECHO_CANONICO_SANT_MAO;

  const modalNome = t.modal_nome || TRECHO_CANONICO_SANT_MAO.modal_nome;
  const operadorNome = t.operador_nome || TRECHO_CANONICO_SANT_MAO.operador_nome;
  const operadorTelefone = t.operador_telefone || '(91) 90000-0000';
  const origemNome = t.origem_nome || TRECHO_CANONICO_SANT_MAO.origem_nome;
  const destinoNome = t.destino_nome || TRECHO_CANONICO_SANT_MAO.destino_nome;
  const terminalOrigem = t.terminal_origem_nome || 'Terminal de embarque regional';
  const terminalDestino = t.terminal_destino_nome || 'Terminal de desembarque regional';
  const duracaoMin = t.duracao_minutos ?? TRECHO_CANONICO_SANT_MAO.duracao_minutos;
  const horaPartida = formatarHora(t.hora_partida || TRECHO_CANONICO_SANT_MAO.hora_partida);
  const horaChegada = formatarHora(t.hora_chegada_estimada || t.hora_chegada || TRECHO_CANONICO_SANT_MAO.hora_chegada_estimada);
  const mask = t.dias_semana_mask ?? TRECHO_CANONICO_SANT_MAO.dias_semana_mask;
  const diasTexto = formatarDiasSemana(mask);
  const frequenciaDescricao = t.frequencia_descricao || TRECHO_CANONICO_SANT_MAO.frequencia_descricao;
  const obsRegime = t.observacao_regime || t.regime_hidrico_observacao || TRECHO_CANONICO_SANT_MAO.observacao_regime;
  const fonteDado = t.fonte_dado || 'ANTAQ / Cadastro Operacional Regional';
  const dataAtualizacao = t.data_ultima_atualizacao || TRECHO_CANONICO_SANT_MAO.data_ultima_atualizacao;
  const corModal = corCategoriaModal(modalNome);

  // Acomodações: se o trecho fornecido possuir acomodações, usa-as; caso contrário, providencia fallback canônico
  let listaAcomodacoes = Array.isArray(t.acomodacoes) && t.acomodacoes.length > 0
    ? t.acomodacoes
    : null;

  if (!listaAcomodacoes) {
    if (modalNome.toLowerCase().includes('barco')) {
      listaAcomodacoes = [
        {
          tipo: 'rede',
          regime: 'fixo',
          valor_total_reais: t.tarifa_reais || 210.0,
          descricao: 'Acomodação tradicional em rede no convés coletivo (levar rede própria).'
        },
        {
          tipo: 'camarote_duplo',
          regime: 'fixo',
          valor_total_reais: t.tarifa_reais === 210 ? 900.0 : (t.tarifa_reais * 3.5),
          descricao: 'Camarote duplo climatizado privativo.'
        }
      ];
    } else {
      listaAcomodacoes = [
        {
          tipo: 'assento_padrao',
          regime: 'fixo',
          valor_total_reais: t.tarifa_reais || 0,
          descricao: 'Assento individual padrão regular.'
        }
      ];
    }
  }

  // Cálculo de recência e selo
  let diasDesde = t.dias_desde_atualizacao;
  if (diasDesde === undefined && dataAtualizacao) {
    try {
      const dt = new Date(dataAtualizacao);
      const hoje = new Date();
      diasDesde = Math.max(0, Math.floor((hoje - dt) / (1000 * 60 * 60 * 24)));
    } catch {
      diasDesde = 12;
    }
  }

  const seloNome = t.selo_confiabilidade || (diasDesde > 30 ? 'Desatualizado' : 'Mais confiável');

  const copiarContato = () => {
    navigator.clipboard?.writeText(operadorTelefone);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2500);
  };

  return (
    <div className="p07-container" data-testid="tela-p07">
      {/* Barra de Navegação Superior / Voltar */}
      <div className="p07-nav-bar">
        {onVoltar ? (
          <button
            type="button"
            className="p07-voltar-btn"
            onClick={onVoltar}
            aria-label="Voltar para a lista de rotas"
          >
            ← Voltar para a rota
          </button>
        ) : (
          <span className="p07-tag-modo">Desenvolvimento Isolado</span>
        )}
        <span className="p07-screen-badge">Tela P07 • Detalhe do Trecho</span>
      </div>

      {/* Cabeçalho do Trecho */}
      <header className="p07-header-card">
        <div className="p07-badges-top">
          <span
            className="p07-modal-badge"
            style={{ backgroundColor: corModal }}
          >
            {modalNome}
          </span>
          <span className="p07-operador-badge">
            Operador: <strong>{operadorNome}</strong>
          </span>
        </div>

        <h2 className="p07-itinerario-title">
          {origemNome} <span className="p07-arrow">→</span> {destinoNome}
        </h2>

        <div className="p07-terminais-row">
          <div className="p07-terminal-item">
            <span className="p07-terminal-label">Embarque:</span>
            <span className="p07-terminal-nome">{terminalOrigem}</span>
          </div>
          <div className="p07-terminal-item">
            <span className="p07-terminal-label">Desembarque:</span>
            <span className="p07-terminal-nome">{terminalDestino}</span>
          </div>
        </div>
      </header>

      {/* Bloco de Horários, Duração e Frequência Bitmask */}
      <section className="p07-section-card" aria-labelledby="sec-horarios">
        <h3 id="sec-horarios" className="p07-section-title">
          Horários e Frequência
        </h3>

        <div className="p07-horarios-grid">
          <div className="p07-horario-box">
            <span className="p07-horario-label">Partida</span>
            <strong className="p07-horario-hora">{horaPartida}</strong>
            <span className="p07-horario-sub">{origemNome}</span>
          </div>

          <div className="p07-duracao-box">
            <span className="p07-duracao-tempo">{formatarDuracao(duracaoMin)}</span>
            <span className="p07-duracao-linha">━━━━━━━━►</span>
            <span className="p07-duracao-minutos">({duracaoMin.toLocaleString('pt-BR')} min)</span>
          </div>

          <div className="p07-horario-box">
            <span className="p07-horario-label">Chegada estimada</span>
            <strong className="p07-horario-hora">{horaChegada}</strong>
            <span className="p07-horario-sub">{destinoNome}</span>
          </div>
        </div>

        <div className="p07-dias-wrap">
          <div className="p07-dias-header">
            <span className="p07-dias-rotulo">Dias de Operação:</span>
            <span className="p07-dias-valor">{diasTexto}</span>
          </div>
          {frequenciaDescricao && frequenciaDescricao !== diasTexto && (
            <div className="p07-frequencia-desc">
              Frequência informada: <em>{frequenciaDescricao}</em>
            </div>
          )}
          <div className="p07-bitmask-chips">
            {[
              { bit: 1, label: 'Seg' },
              { bit: 2, label: 'Ter' },
              { bit: 4, label: 'Qua' },
              { bit: 8, label: 'Qui' },
              { bit: 16, label: 'Sex' },
              { bit: 32, label: 'Sáb' },
              { bit: 64, label: 'Dom' },
            ].map((d) => {
              const ativo = (Number(mask) & d.bit) !== 0;
              return (
                <span
                  key={d.bit}
                  className={`p07-chip-dia ${ativo ? 'ativo' : 'inativo'}`}
                  title={`${d.label}: ${ativo ? 'Opera' : 'Não opera'}`}
                >
                  {d.label}
                </span>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tabela de Preços por Acomodação */}
      <section className="p07-section-card" aria-labelledby="sec-acomodacoes">
        <div className="p07-section-header-row">
          <h3 id="sec-acomodacoes" className="p07-section-title">
            Acomodações e Tarifas
          </h3>
          <span className="p07-regime-pill">Regime Fixo</span>
        </div>

        <div className="p07-table-responsive">
          <table className="p07-acomodacoes-table">
            <thead>
              <tr>
                <th scope="col">Categoria</th>
                <th scope="col">Detalhes</th>
                <th scope="col" className="text-right">Tarifa</th>
              </tr>
            </thead>
            <tbody>
              {listaAcomodacoes.map((ac, idx) => (
                <tr key={`${ac.tipo}-${idx}`} className="p07-acomodacao-row">
                  <td className="p07-acomodacao-nome">
                    <strong>{formatarTituloAcomodacao(ac.tipo)}</strong>
                    <span className="p07-acomodacao-regime-tag">
                      {ac.regime === 'fixo' ? 'Tarifa fixa' : ac.regime}
                    </span>
                  </td>
                  <td className="p07-acomodacao-desc">
                    {ac.descricao || 'Conforme disponibilidade de vagas a bordo.'}
                  </td>
                  <td className="p07-acomodacao-preco text-right">
                    <strong>{formatarMoeda(ac.valor_total_reais)}</strong>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Bloco de Sazonalidade Hídrica */}
      <section className="p07-sazonalidade-card" aria-labelledby="sec-sazonalidade">
        <div className="p07-sazonalidade-header">
          <span className="p07-icone-rio" aria-hidden="true">🌊</span>
          <h3 id="sec-sazonalidade" className="p07-sazonalidade-title">
            Sazonalidade e Regime Hídrico
          </h3>
        </div>

        <div className="p07-sazonalidade-corpo">
          <div className="p07-sazonalidade-alerta">
            <strong>Aviso dos Rios:</strong> "Na vazante, a viagem pode durar mais"
          </div>
          <p className="p07-sazonalidade-texto">
            {obsRegime}
          </p>
          <div className="p07-sazonalidade-nota">
            * No período de estiagem (vazante), a formação de bancos de areia e redução da calha exige velocidade reduzida nas passagens críticas.
          </div>
        </div>
      </section>

      {/* Bloco de Confiabilidade, Recência e Fonte dos Dados */}
      <section className="p07-confiabilidade-card">
        <div className="p07-confiabilidade-top">
          <span className="p07-meta-label">Fonte oficial do dado:</span>
          <span className="p07-meta-valor">{fonteDado}</span>
        </div>

        <div className="p07-confiabilidade-bottom">
          <div className="p07-recencia-info">
            <span className="p07-recencia-txt">{formatarRecencia(diasDesde)}</span>
            {dataAtualizacao && (
              <span className="p07-data-base">({formatarData(dataAtualizacao)})</span>
            )}
          </div>

          <span
            className="p07-selo-badge"
            style={estiloSelo(seloNome)}
          >
            {seloNome}
          </span>
        </div>
      </section>

      {/* Bloco de Contato do Operador (Exemplo Ilustrativo) */}
      <section className="p07-contato-card" aria-labelledby="sec-contato">
        <div className="p07-contato-info">
          <span className="p07-contato-aviso-tag">Exemplo Ilustrativo</span>
          <h3 id="sec-contato" className="p07-contato-operador">
            Contato com {operadorNome}
          </h3>
          <p className="p07-contato-sub">
            Número cadastrado para consulta de vagas e confirmação de partida:
          </p>
        </div>

        <div className="p07-contato-acoes">
          <a
            href={`tel:${operadorTelefone.replace(/\D/g, '')}`}
            className="p07-btn-ligar"
            title="Ligar para o operador"
          >
            📞 {operadorTelefone}
          </a>

          <button
            type="button"
            className="p07-btn-copiar"
            onClick={copiarContato}
            aria-label="Copiar número do operador"
          >
            {copiado ? '✓ Copiado!' : 'Copiar'}
          </button>
        </div>
        <div className="p07-contato-disclaimer">
          Dado ilustrativo simulado para a disciplina de Projeto Integrado II. Não efetua cobrança real.
        </div>
      </section>
    </div>
  );
}
