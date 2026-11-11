# EMBARQUE AMAZÔNIA — MAPEAMENTO TELAS × API (LACUNAS PARA A SEMANA 2)

Este documento mapeia, campo a campo, os dados e operações exigidos pelas **16 telas do protótipo no Figma (`P01–P10` e `A01–A06`)** frente ao estado real verificado em `11/11/2026` no código (`api/main.py`, `api/engine/route_engine.py`), no banco (`database/schema.sql`, `database/seed.sql`) e no contrato (`docs/openapi.yaml`).

> **Resumo das lacunas verificadas em execução:**
> 1. **Localidade e Modais:** `localidade.tipo` e `localidade.codigo_iata` existem no banco (0/7 possuem `latitude` e `longitude` preenchidas), mas ainda não saem em `GET /api/v1/localidades`; não existe endpoint `GET /api/v1/modais`.
> 2. **Trecho e Operador:** `hora_partida`, `hora_chegada_estimada`, `frequencia_descricao`, `dias_semana_mask`, `acomodacao_trecho` (`tipo`, `regime`, `valor_total_reais`), `regime_hidrico_observacao` e `operador.telefone_contato` (0/4 preenchidos no seed) existem no banco, mas não são serializados em `TrechoResponse`.
> 3. **Conexão intermodal:** `calcular_intervalo_conexao()` calcula os minutos de espera entre trechos no motor, mas esse valor não é retornado discriminadamente na resposta JSON de `OpcaoRota`.
> 4. **Rota e Contrato:** não existe cálculo de hora/data prevista de chegada da rota completa; `GET /api/v1/rotas/{id}` consta no `openapi.yaml` e não no `main.py`; o parâmetro `modais` no contrato não enumera formalmente os 10 códigos canônicos.
> 5. **Cadastro administrativo (A01–A06):** login (`bearerAuth`), CRUD de localidades, CRUD completo de operadores/trechos e gatilho de recarga idempotente do motor em memória após mutação constam apenas parcialmente no contrato (`GET/POST /trechos`, `POST /operadores`) e não existem no código Python.
> 6. **Uso Offline (P09):** depende exclusivamente do front-end (IndexedDB indexado pelo `id` determinístico `rota-t{ids}`), pois a API é stateless por requisição.

---

## 1. Fluxo do Passageiro (`P01` a `P10`)

| Tela | Campo / Funcionalidade Necessária | Existe hoje na API? | Onde está hoje | Endpoint ou Campo Proposto | Semana Prevista |
|---|---|---|---|---|---|
| **P01 — Home / Busca** | Catálogo / autocomplete de origem e destino | **Sim** | API (`GET /api/v1/localidades?busca=`) | Já atendido por `GET /api/v1/localidades` | Semana 1 (concluído) |
| **P01 — Home / Busca** | Disparo da busca por data e critério | **Sim** | API (`GET /api/v1/rotas`) | Já atendido por `GET /api/v1/rotas?origem=&destino=&data=&criterio=` | Semana 1 (concluído) |
| **P01 — Home / Busca** | Aba "Avisos" / alerta dinâmico de rios | **Não** | Protótipo Figma | Fora do MVP (apenas texto informativo estático no trecho) | Fora do MVP |
| **P02 — Seletor de Localidade** | `id`, `nome`, `uf`, `e_polo_regional` | **Sim** | API (`LocalidadeResponse`) | Já atendido por `GET /api/v1/localidades` | Semana 1 (concluído) |
| **P02 — Seletor de Localidade** | `tipo` (porto, polo_regional, município etc.) e `codigo_iata` | **Não** | Banco (`localidade.tipo`, `codigo_iata`) | Expor `tipo` e `codigo_iata` em `GET /api/v1/localidades` (`LocalidadeResponse`) | Semana 2 |
| **P02 — Seletor de Localidade** | Buscas recentes persistidas | **Não** | Front-end (não implementado) | Persistência local no navegador (`localStorage` / IndexedDB) | Semana 2 |
| **P03 — Filtros e Preferências** | Lista oficial dos 10 modais (`codigo`, `nome`, `categoria`) | **Não** | Banco (`tabela modal`) | Criar endpoint `GET /api/v1/modais` e enumerar os 10 códigos em `openapi.yaml` | Semana 2 |
| **P03 — Filtros e Preferências** | Filtragem da rota por critério e por código de modal | **Sim** | API (`criterio`, `modais`) e Motor | Já atendido por `GET /api/v1/rotas`; adicionar `enum`/lista dos 10 modais no `openapi.yaml` | Semana 1 (filtro) / Semana 2 (enum) |
| **P03 — Filtros e Preferências** | Filtro por conforto mínimo (rede / camarote) | **Não** | Banco (`acomodacao_trecho.tipo`) | Parâmetro opcional `acomodacao` em `GET /api/v1/rotas` | Semana 2 (se priorizado) |
| **P04 — Lista de Resultados** | `id`, `modais`, `preco_total`, `duracao_total_minutos`, `duracao_total_formatada`, `numero_trechos`, `numero_conexoes`, `selo`, `data_atualizacao_iso`, `dias_desde_atualizacao` | **Sim** | API (`OpcaoRotaResponse`) | Já atendido por `GET /api/v1/rotas` | Semana 1 (concluído) |
| **P04 — Lista de Resultados** | Horário previsto de chegada da rota completa | **Não** | Nenhum lugar | Calcular e expor `chegada_estimada` a partir de hora de saída + duração acumulada | Semana 2 |
| **P05 — Comparador de Rotas** | Atributos comparáveis lado a lado (`preco_total`, `duracao_total_minutos`, `numero_conexoes`, `modais`, `selo`, `dias_desde_atualizacao`) | **Sim** | API (`OpcaoRotaResponse`) | Já atendido pelo retorno de `GET /api/v1/rotas` no front-end | Semana 2 (UI em `web/`) |
| **P06 — Detalhe da Rota** | Consulta direta de uma rota pelo ID (`GET /api/v1/rotas/{id}`) | **Não** | Contrato (`openapi.yaml`), ausente em `main.py` | Implementar `GET /api/v1/rotas/{id}` decodificando IDs determinísticos `rota-t{ids}` | Semana 2 |
| **P06 — Detalhe da Rota** | Tempo de espera/conexão entre dois trechos (em minutos) | **Não** | Motor (`calcular_intervalo_conexao()`), descartado após soma | Expor `conexoes_minutos` (ou `tempo_espera_apos_minutos` por trecho) em `OpcaoRotaResponse` | Semana 2 |
| **P07 — Detalhe do Trecho** | `operador_nome`, `modal_nome`, `terminal_origem_nome`, `terminal_destino_nome`, `duracao_minutos`, `tarifa_reais`, `data_ultima_atualizacao` | **Sim** | API (`TrechoResponse`) | Já atendido dentro de `rotas[].trechos[]` | Semana 1 (concluído) |
| **P07 — Detalhe do Trecho** | Hora de saída (`hora_partida`), chegada (`hora_chegada_estimada`), frequência e dias (`dias_semana_mask`) | **Não** | Banco (`horario_operacao`) e Motor (lê apenas o 1º horário) | Expor array `horarios[]` com saída, chegada e dias decodificados em `TrechoResponse` | Semana 2 |
| **P07 — Detalhe do Trecho** | Acomodações disponíveis com tipo, `regime` e valor (`rede`, `camarote_duplo` etc.) | **Não** | Banco (`acomodacao_trecho`) | Expor lista `acomodacoes[]` em `TrechoResponse` | Semana 2 |
| **P07 — Detalhe do Trecho** | Observação de regime hídrico (`regime_hidrico_observacao`) | **Não** | Banco (`trecho`) e atributo no Motor | Expor campo `observacao_regime` em `TrechoResponse` | Semana 2 |
| **P07 — Detalhe do Trecho** | Telefone de contato do operador (`telefone_contato`) | **Não** | Banco (`operador.telefone_contato`, 0/4 preenchidos no seed) | Preencher exemplos no `seed.sql` e expor `operador_telefone` em `TrechoResponse` | Semana 2 |
| **P08 — Mapa da Rota** | Coordenadas geográficas (`latitude`, `longitude`) das localidades | **Não** | Coluna no Banco (`localidade`, 0/7 preenchidas no seed) | Popular coordenadas via fonte oficial (IBGE/OSM) e expor em `LocalidadeResponse` | Semana 2 |
| **P08 — Mapa da Rota** | Traçado vetorial com hidrografia amazônica | **Não** | Protótipo Figma | Fora do MVP (ou marcador simples ligando coordenadas das localidades) | Fora do MVP |
| **P09 — Rotas Salvas / Offline** | Persistência local e consulta offline sem rede | **Não** | Front-end (não implementado; `id` determinístico já existe na API) | Armazenamento no navegador via **IndexedDB** indexado por `OpcaoRota.id` (`rota-t{ids}`) | Semana 2 (`web/`) |
| **P10 — Estados do Sistema** | Estado vazio (`200`, `rotas: []`), erros (`404`, `422` `ErroPadrao`, `503`) | **Sim** | API (`main.py`) e UI inicial (`App.jsx`) | Já atendido na API; estender estados visuais dedicados em `web/` | Semana 1 (parcial) / Semana 2 |

---

## 2. Fluxo Administrativo e Cadastro (`A01` a `A06`)

| Tela | Campo / Funcionalidade Necessária | Existe hoje na API? | Onde está hoje | Endpoint ou Campo Proposto | Semana Prevista |
|---|---|---|---|---|---|
| **A01 — Login Administrativo** | Autenticação de operador/moderador com token JWT | **Não** | Contrato (`components.securitySchemes.bearerAuth`) | Criar `POST /api/v1/auth/login` e dependência JWT nas rotas `/trechos`, `/operadores` e `/localidades` | Semana 2 |
| **A02 — Painel de Trechos** | Listagem administrativa completa (`GET /api/v1/trechos` com filtro `operador_id`) | **Não** | Contrato (`openapi.yaml`), ausente em `main.py` | Implementar `GET /api/v1/trechos` retornando `TrechoDetalhado` (incl. `sentido`, horários e status) | Semana 2 |
| **A02 — Painel de Trechos** | Edição, desativação ou remoção de trecho | **Não** | Banco (`ativo`) | Criar `PUT /api/v1/trechos/{id}` e `PATCH /api/v1/trechos/{id}/status` | Semana 2 |
| **A03 — Cadastro de Trecho** | Inserção de novo trecho (`POST /api/v1/trechos`) + horários + acomodações (`regime`, `sentido`) | **Não** | Contrato (`POST /api/v1/trechos` parcial sem horários/acomodações), Banco | Implementar `POST /api/v1/trechos` expandido com `sentido`, `horarios` e `acomodacoes` | Semana 2 |
| **A04 — Cadastro de Operador** | Inserção de operador/cooperativa e vínculo N:N `operador_modal` (`POST /api/v1/operadores`) | **Não** | Contrato (`POST /api/v1/operadores` básico) e Banco (`operador_modal`) | Implementar `GET / POST /api/v1/operadores` com lista de `modais_operados` e `telefone_contato` | Semana 2 |
| **A04 — Cadastro de Operador** | Upload de documento comprovante de outorga | **Não** | Protótipo Figma | Fora do MVP (registrar apenas número/órgão emissor em `operador_modal`) | Fora do MVP |
| **A05 — Cadastro de Localidade** | Inserção e edição de localidade (`nome`, `uf`, `tipo`, `codigo_ibge`, `codigo_iata`, `latitude`, `longitude`) | **Não** | Banco (`tabela localidade`) | Criar `POST /api/v1/localidades` e `PUT /api/v1/localidades/{id}` protegidos por JWT | Semana 2 |
| **A05 — Cadastro de Localidade** | Vínculo / Ponto de Transbordo como entidade própria com distância | **Não** | Protótipo Figma | Fora do MVP (conexão representada pelo intervalo temporal entre trechos) | Fora do MVP |
| **A06 — Confirmação e Auditoria** | Recarga automática/idempotente do grafo em memória após gravação no SQLite | **Não** | Motor (`carregar_do_banco()` já é idempotente), sem chamada após escrita | Invocar `motor.carregar_do_banco(DB_PATH)` ao final de `POST/PUT` em trechos/localidades/operadores | Semana 2 |
