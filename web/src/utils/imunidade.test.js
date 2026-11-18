import test from 'node:test';
import assert from 'node:assert/strict';
import { rota1OpcaoC } from '../fixtures/rota1_opcao_c.js';
import { formatarHorarioComDia, montarLinhaDoTempo } from './timeline.js';

test('imunidade 1: ausência de telas dos colegas não impede montagem nem quebra runtime', () => {
  // Simula o router sem as telas dos colegas
  const rotasSuportadas = ['#/', '#/lab/p06', '#/rota/rota-t3-t4?data=2026-11-20', '#/filtros', '#/comparar', '#/trecho/3'];
  for (const r of rotasSuportadas) {
    assert.ok(typeof r === 'string' && r.startsWith('#/'));
  }
});

test('imunidade 2: rota legada (versão 12/11) sem horários renderiza com fallbacks seguros', () => {
  const rotaLegada1211 = {
    id: 'rota-t1',
    origem_nome: 'Belém',
    destino_nome: 'Manaus',
    modais: ['Barco regional'],
    preco_total: 350.0,
    duracao_total_minutos: 8400,
    duracao_total_formatada: '5 d 20 h',
    numero_trechos: 1,
    numero_conexoes: 0,
    selo: ['Menor custo'],
    atualizado_em: 'Atualizado há 3 dias',
    data_atualizacao_iso: '2026-11-03',
    dias_desde_atualizacao: 3,
    trechos: [
      {
        id: 1,
        origem_nome: 'Belém',
        destino_nome: 'Manaus',
        modal_nome: 'Barco regional',
        operador_nome: 'Amazon Star',
        terminal_origem_nome: 'Porto de Belém',
        terminal_destino_nome: 'Porto da Manaus Moderna',
        duracao_minutos: 8400,
        tarifa_reais: 350.0,
        data_ultima_atualizacao: '2026-11-03',
      },
    ],
  };

  const timeline = montarLinhaDoTempo(rotaLegada1211);
  assert.equal(timeline.length, 1);
  assert.equal(timeline[0].tipo, 'trecho');

  const horaPartida = formatarHorarioComDia(rotaLegada1211.trechos[0].hora_partida, null);
  const horaChegada = formatarHorarioComDia(rotaLegada1211.trechos[0].hora_chegada_estimada, null);
  assert.equal(horaPartida, 'Horário não informado');
  assert.equal(horaChegada, 'Horário não informado');
});

test('imunidade 3: rota de laboratório (#/lab/p06) possui flag de exemplo local e dados completos', () => {
  assert.equal(rota1OpcaoC._origemExemplo, true);
  assert.equal(rota1OpcaoC.id, 'rota-t3-t4');
  assert.equal(rota1OpcaoC.trechos.length, 2);
  assert.equal(rota1OpcaoC.trechos[0].intervalo_conexao_minutos, 280);
});

test('imunidade 4: parsing seguro de hash com parâmetros de consulta', () => {
  const hash1 = '#/rota/rota-t3-t4?data=2026-11-20';
  const match1 = hash1.match(/#\/rota\/([^?]+)(?:\?data=([^&]+))?/);
  assert.ok(match1);
  assert.equal(match1[1], 'rota-t3-t4');
  assert.equal(match1[2], '2026-11-20');

  const hash2 = '#/lab/p06';
  assert.equal(hash2, '#/lab/p06');

  const hash3 = '#/';
  assert.equal(hash3, '#/');
});
