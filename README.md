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

```text
.
├── api/                          # API REST em Python / FastAPI e Motor de Rotas
│   ├── engine/
│   │   └── route_engine.py       # Motor de cálculo em grafo multimodal (máx. 3 trechos e 5 opções)
│   ├── tests/
│   │   ├── test_route_engine.py  # 17 testes unitários do motor
│   │   └── test_api.py           # 15 testes de integração HTTP com TestClient
│   ├── main.py                   # Endpoints de consulta (/api/v1/localidades e /api/v1/rotas)
│   └── requirements.txt          # Dependências com versões fixadas
├── database/                     # Modelagem de dados e scripts SQL
│   ├── schema.sql                # Esquema físico normalizado (SQLite local; PostgreSQL previsto)
│   ├── seed.sql                  # Seed ilustrativo (10 modais, 7 localidades, 11 trechos, datas relativas)
│   ├── init_db.py                # Apaga e recria embarque.db aplicando schema.sql e seed.sql
│   └── mostrar_dados.py          # Utilitário somente leitura para inspecionar localidades, trechos e acomodações
├── docs/                         # Documentação formal e especificações do projeto
│   ├── openapi.yaml              # Contrato OpenAPI 3.1 com exemplos canônicos (6 operações previstas)
│   ├── artigo.md                 # Texto acadêmico (Seção 1, Referências e Declaração de IA)
│   ├── decisoes.md               # Decisões de MVP, stack e roteiro de apresentação
│   ├── diagramas_database.md     # Diagramas Mermaid (ERD, topologia do seed e fluxo de dados)
│   ├── escopo_requisitos.md      # Escopo, glossário, dados de exemplo e kit de estilo
│   ├── inventario_telas.md       # Inventário das 16 telas (prototipadas no Figma) e estado atual
│   ├── telas_x_api.md            # Mapeamento de lacunas telas × API para a Semana 2
│   └── verificacao_12-11.md      # Registro de execução verificada em clone limpo
└── web/                          # Esqueleto web React + Vite (tela inicial de busca e resultados)
```

> [!NOTE]
> **Estratégia de Banco:** SQLite em desenvolvimento local; PostgreSQL 15+ previsto para homologação. O arquivo binário local (`database/embarque.db`) é gerado dinamicamente por `python database/init_db.py` e mantido fora do Git via `.gitignore`.
> **Natureza dos Dados:** Todos os horários, tarifas, operadores e rotas do `seed.sql` e dos exemplos são **dados ilustrativos** para validação do sistema.
> **Cobertura do Contrato:** O contrato `docs/openapi.yaml` documenta 6 operações; o servidor FastAPI implementa atualmente as **2 operações de consulta do passageiro** (`GET /api/v1/localidades` e `GET /api/v1/rotas`). As rotas administrativas (`/api/v1/trechos`, `/api/v1/operadores`) e `/api/v1/rotas/{id}` estão previstas para a Semana 2.

---

## 🚀 Como Executar o Projeto do Zero

### Pré-requisitos
* **Python 3.10+** (validado em **Python 3.14.3**)
* **Node.js 18+ / npm** (validado em **Node v24.19.0** e **npm 11.17.0**) para o front-end e Prism CLI

### 1. Inicializar a Base de Dados
Para apagar eventuais resquícios locais e recriar o banco SQLite com `schema.sql` e `seed.sql`:

```bash
python database/init_db.py
```
*Saída esperada:* `BANCO DE DADOS RECRIADO E POPULADO COM SUCESSO!` (**7 localidades, 10 modais, 11 trechos** — IDs canônicos 1–7 e retornos 9–12).

> [!IMPORTANT]
> Como `seed.sql` calcula `data_ultima_atualizacao` de forma relativa ao dia da criação (`date('now', 'localtime', '-N days')`), **execute `python database/init_db.py` novamente no dia da demonstração** para manter a recência alinhada com a data do sistema.

Para visualizar todas as localidades, trechos (com dias da semana por extenso e recência) e acomodações no terminal em modo somente leitura:

```bash
python database/mostrar_dados.py
```

### 2. Executar a Suíte de Testes Automatizados
O repositório possui **32 testes automatizados** no total (`17` no motor e `15` na API):

* **Testes do Motor de Rotas (17 testes):**
```bash
python api/tests/test_route_engine.py
```

* **Testes de Integração da API REST (15 testes):**
```bash
python api/tests/test_api.py
```

> *Nota sobre dependência de teste:* O `TestClient` do FastAPI/Starlette pode emitir `StarletteDeprecationWarning` sobre `httpx` vs `httpx2` em ambiente Python 3.14, sem impacto na execução ou asserções dos testes.

### 3. Executar o Servidor FastAPI
Na raiz do repositório:

```bash
uvicorn api.main:app --port 8000
```
Com o servidor ativo:
* **Swagger UI Interativa:** `http://localhost:8000/docs`
* **Busca de Rotas (Belém → Manaus, sexta 20/11/2026):** `http://localhost:8000/api/v1/rotas?origem=Belém&destino=Manaus&data=2026-11-20`
* **Catálogo / Autocomplete de Localidades:** `http://localhost:8000/api/v1/localidades?busca=bele`

### 4. Executar o Mock Server da API (Prism CLI)
Para testar respostas simuladas diretamente a partir do contrato `docs/openapi.yaml`:

```bash
npx @stoplight/prism-cli mock docs/openapi.yaml --port 4010
```
* **Localidades:** `http://127.0.0.1:4010/api/v1/localidades`
* **Rota 1 (Belém → Manaus):** enviar cabeçalho HTTP `Prefer: example=rota_1_belem_manaus` em `http://127.0.0.1:4010/api/v1/rotas?origem=Belém&destino=Manaus`
* **Rota 2 (Manaus → Tefé):** enviar cabeçalho HTTP `Prefer: example=rota_2_manaus_tefe` em `http://127.0.0.1:4010/api/v1/rotas?origem=Belém&destino=Manaus`

> [!WARNING]
> **Mock Estático:** O servidor Prism devolve **exemplos estáticos** pré-definidos no contrato OpenAPI. Alterar parâmetros na query string (`origem`, `destino`, `criterio`, `data`) **não altera** a resposta retornada pelo mock. O roteamento dinâmico é executado apenas pelo servidor FastAPI + `route_engine.py`.

### 5. Executar o Front-End Web (React + Vite)
O diretório `web/` contém atualmente **apenas uma tela inicial de busca e listagem de resultados** (com autocomplete por localidade, seletor de data e critério, formatação em pt-BR, selos visuais, recência em dias e expansão dos trechos retornados pela API):

```bash
cd web
npm install
npm run dev
```
Acesse no navegador em host local: `http://localhost:5173`.
Para apontar o front-end para outro endereço (como o Prism CLI na porta `4010`), defina `VITE_API_BASE_URL=http://127.0.0.1:4010/api/v1` em `web/.env` (padrão: `http://localhost:8000/api/v1`).

---

## 📜 Regras de Negócio e Limitações Conhecidas

### Regras implementadas
1. **Critérios de comparação:** `menor_tempo`, `menor_custo` e `mais_confiavel` (menor número de dias desde `data_ultima_atualizacao`), retornando **até 5 opções ordenadas**.
2. **Selos visuais:** `Menor custo`, `Menor tempo` e `Mais confiável` são atribuídos apenas quando existem **2 ou mais opções** na resposta. O selo `Desatualizado` é aplicado sempre que algum trecho superar **30 dias** sem atualização (mesmo em opção única).
3. **Validação temporal e erros:** Conexões onde a partida subsequente é anterior à chegada são descartadas. Parâmetros ausentes ou inválidos retornam HTTP `422` no schema `ErroPadrao` (`PARAMETRO_INVALIDO`); localidades inexistentes retornam `404` (`LOCALIDADE_NAO_ENCONTRADA`); ausência do banco retorna `503` (`BANCO_INDISPONIVEL`).

### Limitações conhecidas (MVP Semana 1)
* O dia da semana da `data` consultada é verificado em **todos os trechos** da rota usando a mesma data de partida.
* A conexão entre trechos é calculada apenas pela hora dentro do **mesmo dia** (`hora_partida - hora_chegada >= 0`), sem modelagem de pernoite/virada de dia em escala.
* O motor lê apenas o **primeiro horário ativo** (`ORDER BY hora_partida ASC LIMIT 1`) de cada trecho em `horario_operacao`.
* Não há conversão ou ajuste entre **fusos horários** (ex.: Belém em UTC-3 e Manaus em UTC-4).
* Não há telas P01–P10 nem A01–A06 implementadas em `web/` (existem apenas no protótipo do Figma), nem suporte offline, CRUD administrativo ou autenticação de usuário implementados no código atual.
