-- ==============================================================================
-- EMBARQUE AMAZÔNIA — SEED DE DADOS ILUSTRATIVOS CANÔNICOS
-- Alinhado rigorosamente ao Card 1 e Card 6 do Trello (Dados de Exemplo Padronizados)
-- Compatível com SQLite e PostgreSQL
-- ==============================================================================

-- 1. MODAIS
INSERT INTO modal (id, codigo, nome, categoria, velocidade_media_kmh, requer_registro_orgao, descricao) VALUES
(1, 'barco_linha', 'Barco Regional', 'fluvial', 18.0, 1, 'Embarcação longitudinal com conveses para rede e camarotes.'),
(2, 'voadeira', 'Voadeira expressa', 'fluvial', 35.0, 0, 'Lancha rápida vicinal ou piloto autônomo.'),
(3, 'ferry_boat', 'Ferry-Boat / Balsa', 'fluvial', 20.0, 1, 'Balsa para veículos e passageiros.'),
(4, 'onibus_intermunicipal', 'Ônibus Intermunicipal', 'rodoviario', 60.0, 1, 'Linha regular rodoviária.'),
(5, 'aviacao_regional', 'Avião regional', 'aereo', 450.0, 1, 'Aviação comercial e turboélices ligando polos e interior.');

-- 2. LOCALIDADES ILUSTRATIVAS (Card 1)
INSERT INTO localidade (id, codigo_ibge, nome, uf, e_polo_regional, ativo) VALUES
(1, '1501402', 'Belém', 'PA', 1, 1),
(2, '1302603', 'Manaus', 'AM', 1, 1),
(3, '1506807', 'Santarém', 'PA', 1, 1),
(4, '1304203', 'Tefé', 'AM', 1, 1),
(5, '1303403', 'Parintins', 'AM', 0, 1),
(6, '1502103', 'Cametá', 'PA', 0, 1),
(7, '1500404', 'Alenquer', 'PA', 0, 1);

-- 3. OPERADORES ILUSTRATIVOS (Card 1)
INSERT INTO operador (id, razao_social, nome_fantasia, tipo_operador, cidade_base_id) VALUES
(1, 'Amazon Star Navegações Ltda', 'Amazon Star', 'empresa_regular', 1),
(2, 'Azul Linhas Aéreas Brasileiras S.A.', 'Azul', 'empresa_regular', 1),
(3, 'Piloto Autônomo Colaborativo', 'Piloto autônomo (cadastro colaborativo)', 'autonomo_associado', 2),
(4, 'Oliveira Navegações da Amazônia', 'Oliveira Navegações', 'empresa_regular', 2);

-- 4. OPERADOR_MODAL
INSERT INTO operador_modal (operador_id, modal_id, numero_registro, orgao_emissor) VALUES
(1, 1, 'ANTAQ-REG-15098', 'ANTAQ'),
(2, 5, 'ANAC-RBAC121-AZU', 'ANAC'),
(3, 2, 'CAD-COLAB-9921', 'MUNICIPAL'),
(4, 1, 'ANTAQ-REG-13045', 'ANTAQ');

-- 5. TRECHOS DAS ROTAS CANÔNICAS (Card 1)
-- Data de referência: 20/11/2026

-- ROTA 1: Belém -> Manaus
-- Opção A: Barco regional Amazon Star (5d 20h = 8400 min, R$ 350,00, atualizado há 3 dias: 2026-11-03)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(1, 1, 2, 'Porto de Belém', 'Porto da Manaus Moderna', 1, 1, 8400, 350.00, 0, '2026-11-03', 'Escala em Santarém. Sujeito ao regime de águas.');

-- Opção B: Avião regional Azul (2h 15min = 135 min, R$ 780,00, atualizado hoje: 2026-11-06)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(2, 1, 2, 'Aeroporto Internacional de Belém', 'Aeroporto Eduardo Gomes', 2, 5, 135, 780.00, 0, '2026-11-06', 'Voo direto regular.');

-- Opção C (Combinada): 
-- Trecho 1: Avião Belém -> Santarém (1h 20min = 80 min, saída 08:00, chegada 09:20, R$ 540,00)
-- Conexão em Santarém calculada pelos horários: Saída 14:00 - Chegada 09:20 = 4h 40min = 280 min
-- Trecho 2: Barco Santarém -> Manaus (1d 18h = 2520 min, saída 14:00, R$ 210,00)
-- Total C: 80m + 280m + 2520m = 2880 min = 48h = 2 dias | Custo = R$ 750,00 | Atualizado há 12 dias (2026-10-25)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(3, 1, 3, 'Aeroporto de Belém', 'Aeroporto de Santarém', 2, 5, 80, 540.00, 280, '2026-10-25', 'Voo regional.');

INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(4, 3, 2, 'Porto de Santarém', 'Porto da Manaus Moderna', 1, 1, 2520, 210.00, 0, '2026-10-25', 'Barco de linha.');

-- ROTA 2: Manaus -> Tefé
-- Opção A: Voadeira expressa piloto autônomo (11h = 660 min, R$ 320,00, atualizado há 20 dias: 2026-10-17)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(5, 2, 4, 'Porto de Manaus', 'Porto Fluvial de Tefé', 3, 2, 660, 320.00, 0, '2026-10-17', 'Saída às 06:00. Cadastro colaborativo.');

-- Opção B: Barco regional Oliveira Navegações (1d 12h = 2160 min, R$ 190,00, atualizado há 5 dias: 2026-11-01)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(6, 2, 4, 'Porto da Manaus Moderna', 'Porto Fluvial de Tefé', 4, 1, 2160, 190.00, 0, '2026-11-01', 'Saída 17:00.');

-- Trecho de teste de desatualização (> 30 dias): Parintins -> Manaus (atualizado há 45 dias: 2026-09-22)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(7, 5, 2, 'Porto de Parintins', 'Porto da Manaus Moderna', 4, 1, 1080, 120.00, 0, '2026-09-22', 'Saída semanal.');

-- Trecho de teste para conexão impossível: Santarém -> Manaus que sai antes da chegada do voo (Saída 07:00)
INSERT INTO trecho (id, origem_id, destino_id, terminal_origem_nome, terminal_destino_nome, operador_id, modal_id, duracao_estimada_minutos, tarifa_base_reais, tempo_conexao_espera_minutos, data_ultima_atualizacao, regime_hidrico_observacao) VALUES
(8, 3, 2, 'Porto de Santarém', 'Porto da Manaus Moderna', 1, 1, 2520, 200.00, -1, '2026-10-25', 'Horário incompatível para conexão.');

-- 6. HORÁRIOS
INSERT INTO horario_operacao (trecho_id, hora_partida, hora_chegada_estimada, frequencia_descricao) VALUES
(1, '18:00:00', '10:00:00', 'Quartas e Sextas-feiras'),
(2, '09:30:00', '11:45:00', 'Diário'),
(3, '08:00:00', '09:20:00', 'Diário'),
(4, '14:00:00', '08:00:00', 'Terças e Quintas'),
(5, '06:00:00', '17:00:00', 'Segundas e Quintas'),
(6, '17:00:00', '05:00:00', 'Sextas-feiras'),
(7, '12:00:00', '06:00:00', 'Semanal'),
(8, '07:00:00', '01:00:00', 'Partida matinal incompatível');

-- 7. ACOMODAÇÕES
INSERT INTO acomodacao_trecho (trecho_id, tipo, valor_total_reais, descricao) VALUES
(1, 'rede', 350.00, 'Acomodação tradicional em rede'),
(1, 'camarote_duplo', 1400.00, 'Camarote privativo climatizado'),
(4, 'rede', 210.00, 'Acomodação em rede'),
(6, 'rede', 190.00, 'Passagem em rede');
