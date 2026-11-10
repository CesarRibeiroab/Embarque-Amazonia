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
├── api/                  # API REST em Python / FastAPI e Motor de Rotas
│   ├── engine/           # Motor de cálculo em grafo ponderado multimodal
│   │   └── route_engine.py
│   ├── tests/            # Suítes de testes unitários e de integração
│   │   ├── test_route_engine.py  # 13 testes de aceitação do motor
│   │   └── test_api.py           # 11 testes dos endpoints HTTP com TestClient
│   ├── main.py           # Implementação dos endpoints da API (/localidades e /rotas)
│   └── requirements.txt  # Dependências com versões estritas fixadas
├── database/             # Modelagem de dados e scripts SQL
│   ├── schema.sql        # Esquema físico normalizado
│   ├── seed.sql          # Seed de dados canônicos ilustrativos (10 modais, Rotas 1, 2 e 3)
│   └── init_db.py        # Script de inicialização e carga automatizada da base
├── docs/                 # Documentação formal e especificações do projeto
│   ├── openapi.yaml      # Contrato formal da API em OpenAPI 3.1 com exemplos canônicos
│   ├── artigo.md         # Texto acadêmico (Resumo, Introdução, Referências e Declaração IA)
│   ├── decisoes.md       # Decisões técnicas de MVP, stack e roteiro de orientação
│   └── inventario_telas.md # Mapa de navegação e inventário funcional das 16 telas
└── web/                  # Front-end React + Vite PWA (esqueleto funcional com tela de busca)
```

> [!NOTE]
> **Estratégia de Banco:** SQLite em desenvolvimento local; PostgreSQL previsto para homologação e entrega final. O arquivo de banco binário local (`embarque.db`) é gerado dinamicamente a partir dos scripts `schema.sql` e `seed.sql` através do comando `python database/init_db.py`, sendo mantido fora do versionamento via `.gitignore`.
> **Contrato da API:** A fonte canônica da verdade para o contrato é a especificação formal `docs/openapi.yaml`, escrita antes da implementação para orientar simultaneamente o back-end e o front-end. O FastAPI implementa os endpoints de consulta do passageiro deste contrato, com os endpoints administrativos de cadastro previstos para a Semana 2.

---

## 🚀 Como Executar o Projeto do Zero

### Pré-requisitos
* **Python 3.10+** instalado no ambiente
* **Node.js 18+ / npx** (opcional, para o mock server do Prism)

### 1. Inicializar a Base de Dados
Para criar e popular o banco relacional SQLite local a partir do `schema.sql` e `seed.sql`:

```bash
python database/init_db.py
```
*Saída esperada:* `BANCO DE DADOS EXECUTADO COM SUCESSO! (7 localidades, 10 modais, 12 trechos)`.

> [!NOTE]
> O ambiente local utiliza SQLite para simplificar execução e testes do protótipo. A migração para PostgreSQL está prevista para o ambiente de homologação, com DDL documentado no cabeçalho de `database/schema.sql`.

### 2. Executar a Suíte de Testes Automatizados
O projeto conta com testes unitários cobrindo o motor de grafo e testes de integração dos endpoints HTTP (**24 testes ao todo**):

* **Testes do Motor de Rotas (13 testes):**
```bash
python api/tests/test_route_engine.py
```
*Saída esperada:* `Ran 13 tests in 0.020s - OK` (cobre conexões temporais, rejeição de horários impossíveis, rotas canônicas 1, 2 e 3, recência/selos, filtro de dias da semana, filtro de modais, origem igual a destino, idempotência de recarga e IDs determinísticos).

* **Testes de Integração da API REST (11 testes):**
```bash
python api/tests/test_api.py
```
*Saída esperada:* `Ran 11 tests in 0.200s - OK` (cobre listagem de localidades, busca multicritério, filtro de modais, rotas sem conexão com lista vazia 200 OK, erro 404 para localidade desconhecida, busca sem acentos, fluxo de retorno, validação 422 para parâmetros/datas/origem e persistência de IDs/datas ISO).

### 3. Executar o Servidor FastAPI
Para subir o servidor da API com recarregamento dinâmico:

```bash
uvicorn api.main:app --reload --port 8000
```
Com o servidor ativo:
* **Documentação Swagger UI Interativa:** `http://localhost:8000/docs`
* **Busca de Rotas (Exemplo Belém → Manaus):** `http://localhost:8000/api/v1/rotas?origem=Belém&destino=Manaus&criterio=menor_custo`
* **Catálogo de Localidades:** `http://localhost:8000/api/v1/localidades`

> [!NOTE]
> O FastAPI implementa os endpoints essenciais de consulta do passageiro (`/api/v1/localidades`, `/api/v1/rotas` com suporte a filtros de `modais`, ordenação por `criterio`, validação estrita de datas/parâmetros e busca sem acentos). O CRUD da área administrativa de cadastro (telas A01–A06) está planejado para o marco da Semana 2.

### 4. Executar o Mock Server da API (Prism CLI)
Caso deseje testar a simulação estática do contrato OpenAPI 3.1:

```bash
npx @stoplight/prism-cli mock docs/openapi.yaml --port 4010
```
* **Localidades no Mock:** `http://127.0.0.1:4010/api/v1/localidades`
* **Rotas Belém → Manaus no Mock:** `http://127.0.0.1:4010/api/v1/rotas?origem=Belém&destino=Manaus`

### 5. Executar a Aplicação Web PWA (React + Vite)
Para subir o esqueleto funcional da interface do passageiro (`web/`):

```bash
cd web
npm install
npm run dev
```
Acesse no navegador: `http://localhost:5173` (conectando-se automaticamente à API FastAPI em `localhost:8000` via CORS).

> [!TIP]
> O Prism CLI simula os payloads documentados no contrato OpenAPI para permitir que a equipe de front-end programe os componentes de interface antes da subida da API real. A computação algorítmica dinâmica reside no servidor FastAPI e no motor em Python.

---

## 📜 Regras de Negócio e Critérios Canônicos

1. **Menor tempo:** Rota com a menor duração total acumulada (deslocamento + intervalos de conexão).
2. **Menor custo:** Rota com a menor soma tarifária das passagens econômicas.
3. **Mais confiável:** Rota cujos trechos possuem a atualização mais recente (`data_ultima_atualizacao`). Trechos sem atualização há mais de 30 dias recebem o selo **Desatualizado**.
4. **Conexões Intermodais:** Calculadas dinamicamente com base nos horários de chegada e partida. Conexões onde a partida subsequente é anterior à chegada são descartadas como impossíveis.
