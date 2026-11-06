# 🗄️ Diagramas da Camada de Banco de Dados (`database/`)
**Projeto Integrado II • Embarque Amazônia (CESUPA)**

---

## 1. Diagrama Entidade-Relacionamento (ERD)

Este diagrama reflete fielmente o arquivo [`schema.sql`](file:///D:/Users/Kzar/Documents/Faculdade/Projeto%20Integrado%20II/database/schema.sql) normalizado:

```mermaid
erDiagram
    LOCALIDADE ||--o{ OPERADOR : "sedia (1:N)"
    LOCALIDADE ||--o{ TRECHO : "origem de (1:N)"
    LOCALIDADE ||--o{ TRECHO : "destino de (1:N)"

    OPERADOR ||--|{ OPERADOR_MODAL : "possui registros (1:N)"
    MODAL ||--|{ OPERADOR_MODAL : "autorizado para (1:N)"

    OPERADOR ||--o{ TRECHO : "opera (1:N)"
    MODAL ||--o{ TRECHO : "utilizado em (1:N)"

    TRECHO ||--o{ HORARIO_OPERACAO : "possui saídas (1:N)"
    TRECHO ||--o{ ACOMODACAO_TRECHO : "oferece classes (1:N)"

    LOCALIDADE {
        INTEGER id PK
        VARCHAR codigo_ibge
        VARCHAR nome
        CHAR uf
        NUMERIC latitude
        NUMERIC longitude
        BOOLEAN e_polo_regional
        BOOLEAN ativo
        TIMESTAMP criado_em
    }

    OPERADOR {
        INTEGER id PK
        VARCHAR razao_social
        VARCHAR nome_fantasia
        VARCHAR cnpj_cpf
        VARCHAR tipo_operador
        VARCHAR telefone_contato
        VARCHAR email_contato
        INTEGER cidade_base_id FK
        BOOLEAN ativo
        TIMESTAMP criado_em
    }

    MODAL {
        INTEGER id PK
        VARCHAR codigo UK
        VARCHAR nome
        VARCHAR categoria
        NUMERIC velocidade_media_kmh
        BOOLEAN requer_registro_orgao
        TEXT descricao
    }

    OPERADOR_MODAL {
        INTEGER id PK
        INTEGER operador_id FK
        INTEGER modal_id FK
        VARCHAR numero_registro
        VARCHAR orgao_emissor
        VARCHAR situacao_cadastral
    }

    TRECHO {
        INTEGER id PK
        INTEGER origem_id FK
        INTEGER destino_id FK
        VARCHAR terminal_origem_nome
        VARCHAR terminal_destino_nome
        INTEGER operador_id FK
        INTEGER modal_id FK
        NUMERIC distancia_km
        INTEGER duracao_estimada_minutos
        NUMERIC tarifa_base_reais
        INTEGER tempo_conexao_espera_minutos
        TEXT regime_hidrico_observacao
        NUMERIC fator_sazonal_opcional
        DATE data_ultima_atualizacao
        BOOLEAN ativo
        TIMESTAMP criado_em
    }

    HORARIO_OPERACAO {
        INTEGER id PK
        INTEGER trecho_id FK
        TIME hora_partida
        TIME hora_chegada_estimada
        SMALLINT dias_semana_mask
        VARCHAR frequencia_descricao
        BOOLEAN ativo
    }

    ACOMODACAO_TRECHO {
        INTEGER id PK
        INTEGER trecho_id FK
        VARCHAR tipo
        NUMERIC valor_total_reais
        TEXT descricao
    }
```

---

## 2. Diagrama de Topologia do Grafo e Rotas Canônicas

O arquivo [`seed.sql`](file:///D:/Users/Kzar/Documents/Faculdade/Projeto%20Integrado%20II/database/seed.sql) popula os nós e arestas que formam a malha de teste:

```mermaid
graph LR
    subgraph "Rota 1: Belém → Manaus"
        BEL("Belém (PA)")
        STM("Santarém (PA)")
        MAO("Manaus (AM)")

        BEL -->|"Barco regional<br/>5d 20h | R$ 350<br/>(Opção A: Menor custo)"| MAO
        BEL -->|"Avião regional<br/>2h 15min | R$ 780<br/>(Opção B: Menor tempo & Mais confiável)"| MAO
        BEL -->|"Voo regional<br/>1h 20m | R$ 540<br/>Chegada: 09:20"| STM
        STM -->|"Barco regional<br/>1d 18h | R$ 210<br/>Partida: 14:00"| MAO
    end

    subgraph "Rota 2: Manaus → Tefé"
        TEF("Tefé (AM)")
        MAO -->|"Voadeira expressa<br/>11h | R$ 320<br/>(Menor tempo)"| TEF
        MAO -->|"Barco regional<br/>1d 12h | R$ 190<br/>(Menor custo)"| TEF
    end

    subgraph "Rota 3: Caso de Borda (Sem Conexão)"
        CAM("Cametá (PA)")
        ALQ("Alenquer (PA)")
        CAM -.->|"Sem arestas viáveis no grafo<br/>(Retorna HTTP 404 ErroPadrao)"| ALQ
    end

    subgraph "Trecho de Teste de Desatualização"
        PIN("Parintins (AM)")
        PIN -->|"Barco regional<br/>Atualizado há 45 dias<br/>(Selo: Desatualizado)"| MAO
    end

    style BEL fill:#1F6FB2,stroke:#333,stroke-width:2px,color:#fff
    style MAO fill:#1B5E3F,stroke:#333,stroke-width:2px,color:#fff
    style STM fill:#00796B,stroke:#333,stroke-width:1px,color:#fff
    style TEF fill:#D9822B,stroke:#333,stroke-width:1px,color:#fff
    style CAM fill:#C62828,stroke:#333,stroke-width:1px,color:#fff
    style ALQ fill:#C62828,stroke:#333,stroke-width:1px,color:#fff
    style PIN fill:#F2A900,stroke:#333,stroke-width:1px,color:#000
```

---

## 3. Diagrama do Fluxo de Inicialização e Consumo dos Dados

Visualização de como [`init_db.py`](file:///D:/Users/Kzar/Documents/Faculdade/Projeto%20Integrado%20II/database/init_db.py) garante a integridade e alimenta a API e os testes:

```mermaid
flowchart TD
    S["schema.sql<br/>(Tabelas e Índices)"] --> INIT["init_db.py<br/>(Carga Relativa Portável)"]
    D["seed.sql<br/>(10 Modais Canônicos e Trechos)"] --> INIT
    INIT --> DB[("embarque.db<br/>(SQLite Local)")]

    DB -->|"carregar_do_banco()"| ENGINE["route_engine.py<br/>(Motor em Grafo)"]
    ENGINE --> TESTS["test_route_engine.py<br/>(8 Testes Unitários)"]
    ENGINE --> API["main.py<br/>(FastAPI REST API)"]
    API --> APITESTS["test_api.py<br/>(4 Testes de Integração)"]
    API --> SWAGGER["/docs<br/>(Swagger UI)"]

    style INIT fill:#1F6FB2,color:#fff
    style DB fill:#1B5E3F,color:#fff
    style ENGINE fill:#00796B,color:#fff
    style API fill:#D9822B,color:#fff
    style TESTS fill:#2E7D32,color:#fff
    style APITESTS fill:#2E7D32,color:#fff
```
