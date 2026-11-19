import React from 'react';
import {
  corCategoriaModal,
  estiloSelo,
  formatarConexoes,
  formatarDuracao,
  formatarMoeda,
  formatarRecencia,
} from '../utils/format';
import './TelaComparar.css';

// Dados ilustrativos para testar a tela sem depender da API.
// Valores e selos conferidos em docs/escopo_requisitos.md.
// Acomodação específica das opções ainda não confirmada.
export const OPCOES_EXEMPLO = [
  {
    id: 'exemplo-a',
    nome: 'Opção A',
    modais: ['Barco regional'],
    preco_total: 350,
    duracao_total_minutos: 8400,
    numero_trechos: 1,
    numero_conexoes: 0,
    dias_desde_atualizacao: 3,
    acomodacao: null,
    selo: ['Menor custo'],
  },
  {
    id: 'exemplo-b',
    nome: 'Opção B',
    modais: ['Avião regional'],
    preco_total: 780,
    duracao_total_minutos: 135,
    numero_trechos: 1,
    numero_conexoes: 0,
    dias_desde_atualizacao: 0,
    acomodacao: null,
    selo: ['Menor tempo', 'Mais confiável'],
  },
  {
    id: 'exemplo-c',
    nome: 'Opção C',
    modais: ['Avião regional', 'Barco regional'],
    preco_total: 750,
    duracao_total_minutos: 2880,
    numero_trechos: 2,
    numero_conexoes: 1,
    dias_desde_atualizacao: 12,
    acomodacao: null,
    selo: [],
  },
];
function numeroValido(valor) {
  if (valor === null || valor === undefined || valor === '') {
    return null;
  }

  const numero = Number(valor);

  return Number.isFinite(numero) && numero >= 0 ? numero : null;
}

function menorValor(opcoes, campo) {
  const valores = opcoes
    .map((opcao) => numeroValido(opcao[campo]))
    .filter((valor) => valor !== null);

  return valores.length > 0 ? Math.min(...valores) : null;
}

export default function TelaComparar({
  opcoes,
  origem = 'Belém',
  destino = 'Manaus',
  onVoltar,
  onVerDetalhes,
}) {
const usandoFallback = !Array.isArray(opcoes) || opcoes.length === 0;

const opcoesExibidas = usandoFallback
  ? OPCOES_EXEMPLO
  : opcoes.slice(0, 3);

const usandoExemplos = opcoesExibidas.some((opcao) =>
  OPCOES_EXEMPLO.includes(opcao)
);

  const menores = {
    preco_total: menorValor(opcoesExibidas, 'preco_total'),
    duracao_total_minutos: menorValor(
      opcoesExibidas,
      'duracao_total_minutos'
    ),
    dias_desde_atualizacao: menorValor(
      opcoesExibidas,
      'dias_desde_atualizacao'
    ),
  };

  const linhas = [
    { campo: 'modais', titulo: 'Sequência de modais' },
    {
      campo: 'preco_total',
      titulo: 'Preço total',
      destaque: 'Menor preço',
    },
    {
      campo: 'duracao_total_minutos',
      titulo: 'Duração total',
      destaque: 'Menor duração',
    },
    { campo: 'numero_trechos', titulo: 'Trechos' },
    { campo: 'numero_conexoes', titulo: 'Conexões' },
    { campo: 'acomodacao', titulo: 'Acomodação' },
    {
      campo: 'dias_desde_atualizacao',
      titulo: 'Atualização',
      destaque: 'Mais recente',
    },
  ];

  function renderizarValor(opcao, campo) {
    if (campo === 'modais') {
      const modais = Array.isArray(opcao.modais) ? opcao.modais : [];

      return (
        <div className="comparar-modais">
          {modais.length === 0 && 'Não informado'}

          {modais.map((modal, indice) => (
            <React.Fragment key={`${modal}-${indice}`}>
              {indice > 0 && <span aria-label="depois">→</span>}

              <span
                className="comparar-modal"
                style={{ backgroundColor: corCategoriaModal(modal) }}
              >
                {modal}
              </span>
            </React.Fragment>
          ))}
        </div>
      );
    }

    if (campo === 'acomodacao') {
      return opcao.acomodacao || 'Não informada';
    }

    const valor = numeroValido(opcao[campo]);

    if (valor === null) return 'Não informado';

    switch (campo) {
      case 'preco_total':
        return formatarMoeda(valor);

      case 'duracao_total_minutos':
        return formatarDuracao(valor);

      case 'numero_conexoes':
        return formatarConexoes(valor);

      case 'dias_desde_atualizacao':
        return (
          <>
            <span>{formatarRecencia(valor)}</span>

            <div className="comparar-selos">
              {(Array.isArray(opcao.selo) ? opcao.selo : []).map(
                (selo, indice) => (
                  <span
                    key={`${selo}-${indice}`}
                    className="comparar-selo"
                    style={estiloSelo(selo)}
                  >
                    {selo}
                  </span>
                )
              )}
            </div>
          </>
        );

      default:
        return valor;
    }
  }

  return (
    <main className="app-container comparar-tela">
      <header className="app-header">
        <h1 className="app-title">Comparar opções</h1>
        <p className="app-subtitle">
          {origem} → {destino}
        </p>
      </header>

{usandoExemplos && (
  <div className="aviso-ilustrativo" role="note">
    Dados de exemplo ilustrativos. Preços e horários são estimativas.
    A acomodação das opções ainda aguarda confirmação.
  </div>
)}

      {opcoesExibidas.length < 2 ? (
        <p role="status">
          Selecione pelo menos duas opções para comparar.
        </p>
      ) : (
        <>
          <p className="comparar-instrucao">
            Compare as opções abaixo. Em telas pequenas, deslize a tabela
            para os lados.
          </p>

          <div
            className="comparar-rolagem"
            role="region"
            aria-label="Tabela de comparação de opções de viagem"
            tabIndex={0}
          >
            <table className="comparar-tabela">
              <caption className="comparar-legenda">
                Comparação de {opcoesExibidas.length} opções de viagem
              </caption>

              <thead>
                <tr>
                  <th scope="col">Informação</th>

                  {opcoesExibidas.map((opcao, indice) => (
                    <th key={opcao.id ?? indice} scope="col">
                      {opcao.nome || `Opção ${indice + 1}`}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {linhas.map((linha) => (
                  <tr key={linha.campo}>
                    <th scope="row">{linha.titulo}</th>

                    {opcoesExibidas.map((opcao, indice) => {
                      const valor = numeroValido(opcao[linha.campo]);

                      const melhor =
                        Boolean(linha.destaque) &&
                        valor !== null &&
                        valor === menores[linha.campo];

                      return (
                        <td
                          key={opcao.id ?? indice}
                          className={melhor ? 'comparar-melhor' : undefined}
                        >
                          {renderizarValor(opcao, linha.campo)}

                          {melhor && (
                            <span className="comparar-destaque">
                              {linha.destaque}
                            </span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}

                <tr>
                  <th scope="row">Detalhes</th>

                  {opcoesExibidas.map((opcao, indice) => (
                    <td key={opcao.id ?? indice}>
                      <button
                        type="button"
                        className="comparar-botao-detalhes"
                        disabled={typeof onVerDetalhes !== 'function'}
                        onClick={() => onVerDetalhes(opcao)}
                        aria-label={`Ver detalhes de ${
                          opcao.nome || `Opção ${indice + 1}`
                        }`}
                      >
                        Ver detalhes
                      </button>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}

      {typeof onVerDetalhes !== 'function' && (
        <p className="comparar-pendente" role="note">
          A abertura dos detalhes ainda não foi integrada à P06.
        </p>
      )}

      <button
        type="button"
        className="submit-btn"
        disabled={typeof onVoltar !== 'function'}
        onClick={onVoltar}
      >
        Voltar para resultados
      </button>
    </main>
  );
}