-- ==============================================================================
-- EMBARQUE AMAZÔNIA — SEED DE DADOS ILUSTRATIVOS CANÔNICOS
-- Alinhado rigorosamente aos 10 Modais Canônicos do Projeto (Glossário / Card 1 / Figma)
-- ==============================================================================

-- 1. OS 10 MODAIS CANÔNICOS DO PROJETO (Card 1 / Glossário / Figma / Artigo)
-- Categoria Fluvial: Barco regional, Voadeira, Balsa pequena, Balsa grande
-- Categoria Rodoviária: Carro, Ônibus, Moto-táxi
-- Categoria Aérea: Avião regional, Táxi aéreo, Helicóptero
INSERT INTO modal (id, codigo, nome, categoria, velocidade_media_kmh, requer_registro_orgao, descricao) VALUES
(1, 'barco_regional', 'Barco regional', 'fluvial', 18.0, 1, 'Embarcação longitudinal com conveses para rede e camarotes.'),
(2, 'voadeira', 'Voadeira', 'fluvial', 35.0, 0, 'Lancha rápida vicinal ou piloto autônomo com motor de popa.'),
(3, 'balsa_pequena', 'Balsa pequena', 'fluvial', 15.0, 1, 'Balsa para travessias curtas e rios vicinais.'),
(4, 'balsa_grande', 'Balsa grande', 'fluvial', 22.0, 1, 'Ferry-boat / Balsa Ro-Ro para grandes travessias de passageiros e veículos.'),
(5, 'carro', 'Carro', 'rodoviario', 70.0, 0, 'Transporte rodoviário particular ou fretado.'),
(6, 'onibus', 'Ônibus', 'rodoviario', 60.0, 1, 'Linha regular rodoviária intermunicipal ou interestadual.'),
(7, 'moto_taxi', 'Moto-táxi', 'rodoviario', 40.0, 0, 'Transporte urbano e transbordo rápido nos cais e atracadouros.'),
(8, 'aviao_regional', 'Avião regional', 'aereo', 450.0, 1, 'Aviação comercial regular e turboélices ligando polos e interior.'),
(9, 'taxi_aereo', 'Táxi aéreo', 'aereo', 280.0, 1, 'Aeronaves de pequeno porte sob demanda para pistas no interior.'),
(10, 'helicoptero', 'Helicóptero', 'aereo', 200.0, 1, 'Transporte aéreo especializado para áreas isoladas.');

-- 2. LOCALIDADES ILUSTRATIVAS (Card 1 e Telas A05)
INSERT INTO localidade (id, codigo_ibge, codigo_iata, nome, uf, tipo, e_polo_regional, ativo) VALUES
(1, '1501402', 'BEL', 'Belém', 'PA', 'polo_regional', 1, 1),
(2, '1302603', 'MAO', 'Manaus', 'AM', 'polo_regional', 1, 1),
(3, '1506807', 'STM', 'Santarém', 'PA', 'polo_regional', 1, 1),
(4, '1304203', 'TFF', 'Tefé', 'AM', 'municipio', 0, 1),
(5, '1303403', 'PIN', 'Parintins', 'AM', 'municipio', 0, 1),
(6, '1502103', NULL, 'Cametá', 'PA', 'municipio', 0, 1),
(7, '1500404', NULL, 'Alenquer', 'PA', 'municipio', 0, 1);

-- 3. OPERADORES ILUSTRATIVOS (Card 1)
INSERT INTO operador (id, razao_social, nome_fantasia, tipo_operador, cidade_base_id) VALUES
(1, 'Amazon Star Navegações Ltda', 'Amazon Star', 'empresa_regular', 1),
(2, 'Azul Linhas Aéreas Brasileiras S.A.', 'Azul', 'empresa_regular', 1),
(3, 'Piloto Autônomo Colaborativo', 'Piloto autônomo (cadastro colaborativo)', 'autonomo_associado', 2),
(4, 'Oliveira Navegações da Amazônia', 'Oliveira Navegações', 'empresa_regular', 2);

-- 4. OPERADOR_MODAL (Mapeamento N:N dos modais operados)
INSERT INTO operador_modal (operador_id, modal_id, numero_registro, orgao_emissor) VALUES
(1, 1, 'ANTAQ-REG-15098', 'ANTAQ'),
(2, 8, 'ANAC-RBAC121-AZU', 'ANAC'),
(3, 2, 'CAD-COLAB-9921', 'MUNICIPAL'),
(4, 1, 'ANTAQ-REG-13045', 'ANTAQ');

-- 5. TRECHOS DAS ROTAS CANÔNICAS (Card 1)
-- Data da viagem de teste canônica: 20/11/2026 (Sexta-feira)
-- Datas de atualização (data_ultima_atualizacao) relativas ao momento da execução do init_db.py
-- Nota sobre limitações operacionais: Fuso horário (Belém UTC-3 / Manaus UTC-4) e conexões consideradas no mesmo dia.

-- ROTA 1: Belém -> Manaus
-- Opção A: Barco regional Amazon Star (5d 20h = 8400 min, R$ 350,00, atualizado há 3 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(1, 1, 2, 'Porto de Belém', 'Porto da Manaus Moderna', 1, 1, 8400, 350.00, 0, 'ida', date('now', 'localtime', '-3 days'), 'Escala em Santarém. Sujeito ao regime de águas.');

-- Opção B: Avião regional Azul (2h 15min = 135 min, R$ 780,00, atualizado hoje)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(2, 1, 2, 'Aeroporto Internacional de Belém', 'Aeroporto Eduardo Gomes', 2, 8, 135, 780.00, 0, 'ida', date('now', 'localtime'), 'Voo direto regular.');

-- Opção C (Combinada): 
-- Trecho 1: Avião Belém -> Santarém (1h 20min = 80 min, saída 08:00, chegada 09:20, R$ 540,00)
-- Conexão em Santarém calculada pelos horários: Saída 14:00 - Chegada 09:20 = 4h 40min = 280 min
-- Trecho 2: Barco Santarém -> Manaus (1d 18h = 2520 min, saída 14:00, R$ 210,00)
-- Total C: 80m + 280m + 2520m = 2880 min = 48h = 2 dias | Custo = R$ 750,00 | Atualizado há 12 dias
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(3, 1, 3, 'Aeroporto de Belém', 'Aeroporto de Santarém', 2, 8, 80, 540.00, 280, 'ida', date('now', 'localtime', '-12 days'), 'Voo regional.');

INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(4, 3, 2, 'Porto de Santarém', 'Porto da Manaus Moderna', 1, 1, 2520, 210.00, 0, 'ida', date('now', 'localtime', '-12 days'), 'Barco de linha.');

-- ROTA 2: Manaus -> Tefé
-- Opção A: Voadeira expressa piloto autônomo (11h = 660 min, R$ 320,00, atualizado há 20 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(5, 2, 4, 'Porto de Manaus', 'Porto Fluvial de Tefé', 3, 2, 660, 320.00, 0, 'ida', date('now', 'localtime', '-20 days'), 'Saída às 06:00. Cadastro colaborativo.');

-- Opção B: Barco regional Oliveira Navegações (1d 12h = 2160 min, R$ 190,00, atualizado há 5 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(6, 2, 4, 'Porto da Manaus Moderna', 'Porto Fluvial de Tefé', 4, 1, 2160, 190.00, 0, 'ida', date('now', 'localtime', '-5 days'), 'Saída 17:00.');

-- Trecho de teste de desatualização (> 30 dias): Parintins -> Manaus (atualizado há 45 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(7, 5, 2, 'Porto de Parintins', 'Porto da Manaus Moderna', 4, 1, 1080, 120.00, 0, 'ida', date('now', 'localtime', '-45 days'), 'Saída semanal.');

-- TRECHOS DE RETORNO (Fluxo Inverso para testes de ida e volta - mantendo IDs 9 a 12)
-- Manaus -> Belém (Barco Regional Amazon Star na descida do rio: 4 dias = 96h = 5760 min, R$ 350,00, atualizado há 3 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(9, 2, 1, 'Porto da Manaus Moderna', 'Porto de Belém', 1, 1, 5760, 350.00, 0, 'volta', date('now', 'localtime', '-3 days'), 'Descida do rio Amazonas com escala em Santarém.');

-- Manaus -> Belém (Avião regional Azul, 135 min, R$ 780,00, atualizado hoje)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(10, 2, 1, 'Aeroporto Eduardo Gomes', 'Aeroporto Internacional de Belém', 2, 8, 135, 780.00, 0, 'volta', date('now', 'localtime'), 'Voo de retorno direto regular.');

-- Tefé -> Manaus (Voadeira expressa piloto autônomo, 660 min, R$ 320,00, atualizado há 20 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(11, 4, 2, 'Porto Fluvial de Tefé', 'Porto de Manaus', 3, 2, 660, 320.00, 0, 'volta', date('now', 'localtime', '-20 days'), 'Retorno Tefé-Manaus expressa.');

-- Tefé -> Manaus (Barco regional Oliveira Navegações, 2160 min, R$ 190,00, atualizado há 5 dias)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, sentido, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(12, 4, 2, 'Porto Fluvial de Tefé', 'Porto da Manaus Moderna', 4, 1, 2160, 190.00, 0, 'volta', date('now', 'localtime', '-5 days'), 'Retorno Tefé-Manaus de linha.');

-- 6. HORÁRIOS (com bitmask: Seg=1, Ter=2, Qua=4, Qui=8, Sex=16, Sab=32, Dom=64)
INSERT INTO horario_operacao (trecho_id, hora_partida, hora_chegada_estimada, dias_semana_mask, frequencia_descricao) VALUES
(1, '18:00:00', '14:00:00', 20, 'Quartas e Sextas-feiras'),
(2, '09:30:00', '11:45:00', 127, 'Diário'),
(3, '08:00:00', '09:20:00', 127, 'Diário'),
(4, '14:00:00', '08:00:00', 26, 'Terças, Quintas e Sextas-feiras'),
(5, '06:00:00', '17:00:00', 25, 'Segundas, Quintas e Sextas-feiras'),
(6, '17:00:00', '05:00:00', 16, 'Sextas-feiras'),
(7, '12:00:00', '06:00:00', 32, 'Semanal (Sábados)'),
(9, '18:00:00', '18:00:00', 20, 'Quartas e Sextas-feiras'),
(10, '14:00:00', '16:15:00', 127, 'Diário'),
(11, '06:00:00', '17:00:00', 25, 'Segundas, Quintas e Sextas-feiras'),
(12, '17:00:00', '05:00:00', 16, 'Sextas-feiras');

-- 7. ACOMODAÇÕES
INSERT INTO acomodacao_trecho (trecho_id, tipo, regime, valor_total_reais, descricao) VALUES
(1, 'rede', 'fixo', 350.00, 'Acomodação tradicional em rede'),
(1, 'camarote_duplo', 'fixo', 1400.00, 'Camarote privativo climatizado'),
(4, 'rede', 'fixo', 210.00, 'Acomodação em rede'),
(6, 'rede', 'fixo', 190.00, 'Passagem em rede'),
(9, 'rede', 'fixo', 350.00, 'Acomodação em rede'),
(12, 'rede', 'fixo', 190.00, 'Acomodação em rede');
