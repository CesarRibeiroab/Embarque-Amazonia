/**
 * Fixture de exemplo da Rota 1 Opção C (Belém -> Manaus via Santarém).
 * Utilizada para visualização no laboratório (#/lab/p06) e como fallback de desenvolvimento.
 * Dados canônicos ilustrativos de teste (não oficiais).
 */
export const rota1OpcaoC = {
  id: "rota-t3-t4",
  origem_nome: "Belém",
  destino_nome: "Manaus",
  modais: ["Avião regional", "Barco regional"],
  preco_total: 750.0,
  duracao_total_minutos: 2880,
  duracao_total_formatada: "2 d",
  numero_trechos: 2,
  numero_conexoes: 1,
  selo: [],
  dias_desde_atualizacao: 12,
  data_atualizacao_iso: "2026-10-30",
  data_viagem: "2026-11-20",
  hora_partida: "08:00",
  chegada_estimada: "08:00",
  chegada_dia_offset: 2,
  chegada_estimada_iso: "2026-11-22T08:00",
  _origemExemplo: true, // Identificador de fixture local (sem API)
  trechos: [
    {
      id: 3,
      origem_nome: "Belém",
      destino_nome: "Santarém",
      modal_nome: "Avião regional",
      modal_codigo: "aviao_regional",
      modal_categoria: "aereo",
      operador_nome: "Azul",
      terminal_origem_nome: "Aeroporto de Belém",
      terminal_destino_nome: "Aeroporto de Santarém",
      duracao_minutos: 80,
      tarifa_reais: 540.0,
      hora_partida: "08:00",
      hora_chegada_estimada: "09:20",
      partida_dia_offset: 0,
      chegada_dia_offset: 0,
      frequencia_descricao: "Diário",
      dias_semana_mask: 127,
      acomodacoes: [],
      regime_hidrico_observacao: "Voo regional.",
      telefone_contato: null,
      intervalo_conexao_minutos: 280,
      data_ultima_atualizacao: "2026-10-30"
    },
    {
      id: 4,
      origem_nome: "Santarém",
      destino_nome: "Manaus",
      modal_nome: "Barco regional",
      modal_codigo: "barco_regional",
      modal_categoria: "fluvial",
      operador_nome: "Amazon Star",
      terminal_origem_nome: "Porto de Santarém",
      terminal_destino_nome: "Porto da Manaus Moderna",
      duracao_minutos: 2520,
      tarifa_reais: 210.0,
      hora_partida: "14:00",
      hora_chegada_estimada: "08:00",
      partida_dia_offset: 0,
      chegada_dia_offset: 2,
      frequencia_descricao: "Terças, Quintas e Sextas-feiras",
      dias_semana_mask: 26,
      acomodacoes: [
        {
          tipo: "rede",
          regime: "fixo",
          valor_total_reais: 210.0,
          descricao: "Acomodação em rede"
        }
      ],
      regime_hidrico_observacao: "Barco de linha.",
      telefone_contato: null,
      intervalo_conexao_minutos: null,
      data_ultima_atualizacao: "2026-10-30"
    }
  ]
};
