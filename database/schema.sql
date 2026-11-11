-- ==============================================================================
-- EMBARQUE AMAZÔNIA — HUB MULTIMODAL DE TRANSPORTES PARA A AMAZÔNIA LEGAL
-- PROJETO INTEGRADO II — CIÊNCIA DA COMPUTAÇÃO (CESUPA)
-- Esquema Físico Relacional
-- Dialeto do MVP Local: SQLite 3 (em desenvolvimento local)
-- Nota sobre datas relativas no seed.sql:
--   - O seed utiliza date('now', 'localtime', '-N days'), função específica do SQLite.
--   - Na migração para PostgreSQL 15+, substituir por: CURRENT_DATE - N
-- Migração PostgreSQL 15+ prevista para homologação:
--   - Trocar AUTOINCREMENT por BIGSERIAL ou GENERATED ALWAYS AS IDENTITY
--   - Trocar BOOLEAN DEFAULT 1/0 por BOOLEAN DEFAULT TRUE/FALSE
--   - Manter restrições CHECK e chaves estrangeiras relacionais
-- ==============================================================================

-- 1. TABELA DE MODAIS
CREATE TABLE IF NOT EXISTS modal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(30) UNIQUE NOT NULL,      -- 'barco_regional', 'voadeira', 'balsa_pequena', 'aviao_regional', etc.
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('fluvial', 'rodoviario', 'aereo')),
    velocidade_media_kmh NUMERIC(5,2),
    requer_registro_orgao BOOLEAN DEFAULT 1,
    descricao TEXT
);

-- 2. TABELA DE LOCALIDADES
CREATE TABLE IF NOT EXISTS localidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_ibge VARCHAR(7),
    codigo_iata VARCHAR(3),                  -- ex: 'BEL', 'MAO', 'STM' (Tela A05)
    nome VARCHAR(120) NOT NULL,
    uf CHAR(2) NOT NULL,
    tipo VARCHAR(30) DEFAULT 'municipio' CHECK (tipo IN ('municipio', 'polo_regional', 'porto', 'aeroporto', 'comunidade', 'terminal_rodoviario')),
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    e_polo_regional BOOLEAN DEFAULT 0,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DE OPERADORES DE TRANSPORTE
CREATE TABLE IF NOT EXISTS operador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social VARCHAR(150) NOT NULL,
    nome_fantasia VARCHAR(150),
    cnpj_cpf VARCHAR(18),
    tipo_operador VARCHAR(30) NOT NULL CHECK (tipo_operador IN ('empresa_regular', 'cooperativa', 'autonomo_associado', 'governamental')),
    telefone_contato VARCHAR(30),
    email_contato VARCHAR(120),
    cidade_base_id INTEGER REFERENCES localidade(id),
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. RELAÇÃO N:N OPERADOR_MODAL (Resolução do pós-mortem)
CREATE TABLE IF NOT EXISTS operador_modal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operador_id INTEGER NOT NULL REFERENCES operador(id) ON DELETE CASCADE,
    modal_id INTEGER NOT NULL REFERENCES modal(id) ON DELETE RESTRICT,
    numero_registro VARCHAR(60),
    orgao_emissor VARCHAR(30),               -- 'ANTAQ', 'ANTT', 'ANAC', 'CAPITANIA_MARINHA', 'MUNICIPAL'
    situacao_cadastral VARCHAR(20) DEFAULT 'regular',
    CONSTRAINT unq_operador_modal UNIQUE (operador_id, modal_id)
);

-- 5. TABELA DE TRECHOS (Arestas direcionadas do grafo de transportes)
CREATE TABLE IF NOT EXISTS trecho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem_id INTEGER NOT NULL REFERENCES localidade(id) ON DELETE RESTRICT,
    destino_id INTEGER NOT NULL REFERENCES localidade(id) ON DELETE RESTRICT,
    terminal_origem_nome VARCHAR(120),        -- ex: 'Porto de Belém', 'Aeroporto de Santarém'
    terminal_destino_nome VARCHAR(120),
    operador_id INTEGER NOT NULL REFERENCES operador(id) ON DELETE RESTRICT,
    modal_id INTEGER NOT NULL REFERENCES modal(id) ON DELETE RESTRICT,
    distancia_km NUMERIC(8,2),
    duracao_estimada_minutos INTEGER NOT NULL,  -- tempo de viagem em condições normais
    tarifa_base_reais NUMERIC(10,2) NOT NULL,   -- tarifa econômica básica
    tempo_conexao_espera_minutos INTEGER DEFAULT 45, -- tempo mínimo de espera/transbordo
    sentido VARCHAR(10) DEFAULT 'ida' CHECK (sentido IN ('ida', 'volta', 'circular')), -- Telas A02 e A03
    regime_hidrico_observacao TEXT,            -- 'Normal', 'Período de Vazante (sujeito a bancos de areia)', etc.
    fator_sazonal_opcional NUMERIC(3,2) DEFAULT 1.00,
    data_ultima_atualizacao DATE NOT NULL DEFAULT (CURRENT_DATE), -- Base para o cálculo de recência
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_origem_destino_distintos CHECK (origem_id <> destino_id)
);

-- 6. HORÁRIOS E DIAS DE OPERAÇÃO
CREATE TABLE IF NOT EXISTS horario_operacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trecho_id INTEGER NOT NULL REFERENCES trecho(id) ON DELETE CASCADE,
    hora_partida TIME NOT NULL,
    hora_chegada_estimada TIME,
    dias_semana_mask SMALLINT DEFAULT 127 CHECK (dias_semana_mask BETWEEN 1 AND 127), -- Bitmask: Seg=1, Ter=2, Qua=4, Qui=8, Sex=16, Sab=32, Dom=64
    frequencia_descricao VARCHAR(100),       -- ex: 'Diário', 'Quartas e Sextas-feiras', 'Saída 06:00'
    ativo BOOLEAN DEFAULT 1
);

-- 7. ACOMODAÇÕES E TARIFAS DIFERENCIADAS (Fluvial e Regimes)
CREATE TABLE IF NOT EXISTS acomodacao_trecho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trecho_id INTEGER NOT NULL REFERENCES trecho(id) ON DELETE CASCADE,
    tipo VARCHAR(40) NOT NULL CHECK (tipo IN ('rede', 'cadeira_inclinavel', 'camarote_duplo', 'camarote_quadruplo', 'suite', 'assento_padrao')),
    regime VARCHAR(20) DEFAULT 'fixo' CHECK (regime IN ('fixo', 'dinamico', 'sob_consulta')), -- Telas A03 e Modelo
    valor_total_reais NUMERIC(10,2) NOT NULL,
    descricao TEXT
);

-- ÍNDICES DE BUSCA
CREATE INDEX IF NOT EXISTS idx_trecho_origem_destino ON trecho(origem_id, destino_id);
CREATE INDEX IF NOT EXISTS idx_trecho_operador ON trecho(operador_id);
CREATE INDEX IF NOT EXISTS idx_trecho_atualizacao ON trecho(data_ultima_atualizacao);
