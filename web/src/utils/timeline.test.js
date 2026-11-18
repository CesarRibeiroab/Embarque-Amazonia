import test from 'node:test';
import assert from 'node:assert/strict';
import { formatarHorarioComDia, montarLinhaDoTempo } from './timeline.js';
import { rota1OpcaoC } from '../fixtures/rota1_opcao_c.js';

test('timeline: conexão de 280 min entre t3 e t4 na Rota 1 Opção C', () => {
  const itens = montarLinhaDoTempo(rota1OpcaoC);

  // 2 trechos + 1 conexão intercalada = 3 itens
  assert.equal(itens.length, 3);
  assert.equal(itens[0].tipo, 'trecho');
  assert.equal(itens[0].trecho.id, 3);

  assert.equal(itens[1].tipo, 'conexao');
  assert.equal(itens[1].local, 'Santarém');
  assert.equal(itens[1].minutos, 280);
  assert.equal(itens[1].horaChegada, '09:20');
  assert.equal(itens[1].horaPartidaProx, '14:00');
  assert.equal(itens[1].conexaoCurta, false);

  assert.equal(itens[2].tipo, 'trecho');
  assert.equal(itens[2].trecho.id, 4);
});

test('timeline: formatação de horário com offsets (+1 dia e +2 dias)', () => {
  // Offset +2 dias (chegada de t4)
  const chegadaT4 = formatarHorarioComDia(rota1OpcaoC.trechos[1].hora_chegada_estimada, rota1OpcaoC.trechos[1].chegada_dia_offset);
  assert.equal(chegadaT4, '08:00 (+2 dias)');

  // Offset 0 dias
  const partidaT3 = formatarHorarioComDia(rota1OpcaoC.trechos[0].hora_partida, rota1OpcaoC.trechos[0].partida_dia_offset);
  assert.equal(partidaT3, '08:00');

  // Offset +1 dia (singular)
  const diaMaisUm = formatarHorarioComDia('15:30', 1);
  assert.equal(diaMaisUm, '15:30 (+1 dia)');
});

test('timeline: rota de 1 trecho direto não deve possuir conexões', () => {
  const rotaDireta = {
    id: 'rota-t2',
    origem_nome: 'Belém',
    destino_nome: 'Manaus',
    trechos: [rota1OpcaoC.trechos[0]],
  };

  const itens = montarLinhaDoTempo(rotaDireta);
  assert.equal(itens.length, 1);
  assert.equal(itens[0].tipo, 'trecho');
  assert.equal(itens[0].trecho.id, 3);
});

test('timeline: tolera rota no formato antigo sem horários cadastrados', () => {
  const rotaLegada = {
    id: 'rota-legada',
    origem_nome: 'Origem',
    destino_nome: 'Destino',
    trechos: [
      {
        id: 10,
        origem_nome: 'Origem',
        destino_nome: 'Destino',
        modal_nome: 'Barco regional',
        duracao_minutos: 120,
        tarifa_reais: 50.0,
        // Sem hora_partida nem hora_chegada_estimada
      },
    ],
  };

  const itens = montarLinhaDoTempo(rotaLegada);
  assert.equal(itens.length, 1);
  assert.equal(itens[0].tipo, 'trecho');

  const textoPartida = formatarHorarioComDia(rotaLegada.trechos[0].hora_partida, null);
  assert.equal(textoPartida, 'Horário não informado');
});
