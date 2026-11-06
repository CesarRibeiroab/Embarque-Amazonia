# Embarque Amazônia — Hub Multimodal de Transportes para a Amazônia Legal

Plataforma digital para planejamento, roteamento e comparação de trajetos multimodais na Amazônia Legal, integrando transporte fluvial (barcos regionais, voadeiras, balsas), rodoviário e aéreo regional.

Desenvolvido no âmbito do **Projeto Integrado II** — Bacharelado em Ciência da Computação, **CESUPA** (Centro Universitário do Estado do Pará).

---

## 👥 Equipe do Projeto

* **César Augusto Borges Ribeiro** — Coordenação geral, contrato OpenAPI, motor de rotas e artigo
* **Fernando César Mourão Fonseca** — Modelagem relacional, banco SQL, área de cadastro e resumo
* **Herbert Aciolly Leão de Jesus** — Design system, interface mobile do passageiro (P01–P04) e plano de testes
* **Lucas Barros Mutran** — Interface de comparação/offline (P05–P10) e seções metodológicas do artigo

---

## 🏗️ Estrutura do Repositório (Mono-repo)

```
.
├── api/                  # Motor de rotas e back-end em Python (FastAPI previsto)
│   ├── engine/           # Motor de cálculo em grafo ponderado multimodal
│   │   └── route_engine.py
│   ├── tests/            # Suíte de testes unitários de aceitação (8 testes)
│   │   └── test_route_engine.py
│   ├── main.py           # Implementação inicial dos endpoints da API
│   └── requirements.txt  # Dependências do back-end Python
├── database/             # Modelagem de dados e scripts SQL
│   ├── schema.sql        # Esquema físico normalizado
│   ├── seed.sql          # Seed de dados canônicos ilustrativos (10 modais, Rotas 1, 2 e 3)
│   └── init_db.py        # Script de inicialização e carga automatizada do SQLite local
├── docs/                 # Documentação formal e especificações do projeto
│   ├── openapi.yaml      # Contrato formal da API em OpenAPI 3.1 com exemplos canônicos
│   ├── artigo.md         # Texto acadêmico (Resumo, Introdução, Referências e Declaração IA)
│   ├── decisoes.md       # Decisões técnicas de MVP, stack e roteiro de orientação
│   └── inventario_telas.md # Mapa de navegação e inventário funcional das 16 telas
└── web/                  # Front-end React + Vite PWA (em desenvolvimento)
```

> [!NOTE]
> O arquivo de banco binário local (`embarque.db`) é gerado dinamicamente a partir dos scripts `schema.sql` e `seed.sql` através do comando `python database/init_db.py`, sendo mantido fora do versionamento via `.gitignore`.
> **Estratégia de Banco:** SQLite em desenvolvimento local; PostgreSQL previsto para homologação e entrega final.

---

## 🚀 Como Executar o Projeto do Zero

### Pré-requisitos
* **Python 3.10+** instalado no ambiente
* **Node.js 18+ / npx** (opcional, para o mock server do Prism)

### 1. Inicializar a Base de Dados
O projeto utiliza uma fonte única de dados canônica. Para criar e popular o banco SQLite a partir do `schema.sql` e `seed.sql`:

```bash
python database/init_db.py
```
*Saída esperada:* `BANCO DE DADOS EXECUTADO COM SUCESSO! (7 localidades, 10 modais, 8 trechos)`.

### 2. Executar a Suíte de Testes do Motor de Rotas
O motor de rotas lê diretamente os dados do banco e avalia os critérios de **Menor custo**, **Menor tempo** e **Mais confiável** (por recência):

```bash
python api/tests/test_route_engine.py
```
*Saída esperada:*
```
test_01_conexao_calculada_dinamicamente ... ok
test_02_conexao_impossivel_rejeitada ... ok
test_03_rota_1_tres_opcoes_e_opcao_c_combinada ... ok
test_04_rota_1_opcao_b_recebe_ambos_os_selos ... ok
test_05_rota_1_criterio_menor_custo ... ok
test_06_rota_2_manaus_tefe_valores_canonicos ... ok
test_07_rota_3_sem_resultados ... ok
test_08_trecho_desatualizado_acima_de_30_dias ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.012s - OK
```

### 3. Executar o Mock Server da API (Prism CLI)
Para subir um servidor de mock local com base no contrato OpenAPI 3.1:

```bash
npx @stoplight/prism-cli mock docs/openapi.yaml --port 4010
```
Com o mock em execução, faça requisições no navegador ou terminal:
* **Localidades:** `http://127.0.0.1:4010/localidades`
* **Rotas Belém → Manaus:** `http://127.0.0.1:4010/rotas?origem=Belém&destino=Manaus`

> [!TIP]
> O Prism CLI simula o tráfego HTTP estático documentado no contrato para destravar o desenvolvimento do front-end. O cálculo dinâmico de rotas reside no motor em Python (`api/engine/route_engine.py`).

---

## 📜 Regras de Negócio e Critérios Canônicos

1. **Menor tempo:** Rota com a menor duração total acumulada (deslocamento + intervalos de conexão).
2. **Menor custo:** Rota com a menor soma tarifária das passagens econômicas.
3. **Mais confiável:** Rota cujos trechos possuem a atualização mais recente (`data_ultima_atualizacao`). Trechos sem atualização há mais de 30 dias recebem o selo **Desatualizado**.
4. **Conexões Intermodais:** Calculadas dinamicamente com base nos horários de chegada e partida. Conexões onde a partida subsequente é anterior à chegada são descartadas como impossíveis.
