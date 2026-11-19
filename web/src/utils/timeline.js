/**
 * Utilitários para formatação e montagem da linha do tempo intermodal (Tela P06).
 */

/**
 * Formata um horário ("HH:MM") adicionando sufixo de offset de dias quando aplicável.
 * Exemplo: ("08:00", 2) -> "08:00 (+2 dias)"; ("08:00", 1) -> "08:00 (+1 dia)"; ("08:00", 0) -> "08:00".
 * Tolera rotas no formato antigo: se horaStr for nulo ou vazio, retorna "Horário não informado".
 */
export function formatarHorarioComDia(horaStr, diaOffset) {
  if (!horaStr || typeof horaStr !== 'string' || horaStr.trim() === '' || horaStr.trim() === '00:00:00') {
    return 'Horário não informado';
  }

  const horaFormatada = horaStr.trim().slice(0, 5);
  const offset = Number(diaOffset);

  if (Number.isFinite(offset) && offset > 0) {
    if (offset === 1) {
      return `${horaFormatada} (+1 dia)`;
    }
    return `${horaFormatada} (+${offset} dias)`;
  }

  return horaFormatada;
}

/**
 * Monta a lista sequencial de itens para exibição na linha do tempo vertical da rota.
 * Cada elemento retornado é do tipo 'trecho' ou 'conexao'.
 * O local da conexão é exatamente o destino_nome do trecho anterior.
 */
export function montarLinhaDoTempo(rota) {
  if (!rota || !Array.isArray(rota.trechos) || rota.trechos.length === 0) {
    return [];
  }

  const itens = [];
  const total = rota.trechos.length;

  for (let i = 0; i < total; i++) {
    const tr = rota.trechos[i];
    itens.push({
      tipo: 'trecho',
      indice: i + 1,
      trecho: tr,
    });

    // Se houver trecho seguinte, intercala bloco de conexão
    if (i < total - 1) {
      const proxTr = rota.trechos[i + 1];
      const minutosEspera = tr.intervalo_conexao_minutos != null
        ? Number(tr.intervalo_conexao_minutos)
        : (tr.tempo_conexao_espera_minutos != null ? Number(tr.tempo_conexao_espera_minutos) : 0);

      const horaChegada = tr.hora_chegada_estimada ? tr.hora_chegada_estimada.slice(0, 5) : null;
      const horaPartidaProx = proxTr.hora_partida ? proxTr.hora_partida.slice(0, 5) : null;

      itens.push({
        tipo: 'conexao',
        local: tr.destino_nome,
        terminal: tr.terminal_destino_nome || proxTr.terminal_origem_nome || '',
        minutos: minutosEspera,
        horaChegada,
        horaPartidaProx,
        conexaoCurta: minutosEspera > 0 && minutosEspera < 45,
        trechoAnterior: tr,
        proximoTrecho: proxTr,
      });
    }
  }

  return itens;
}
