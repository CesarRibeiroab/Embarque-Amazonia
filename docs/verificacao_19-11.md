# Registro de Verificação e Auditoria de Entrega (19/11/2026)

**Projeto:** Embarque Amazônia — Hub Multimodal de Transportes para a Amazônia Legal  
**Disciplina:** Projeto Integrado II — Bacharelado em Ciência da Computação (CESUPA)  
**Responsável:** César Augusto Borges Ribeiro  
**Data da Verificação:** 18/11/2026  
**Ambiente de Execução:**
* **Sistema Operacional:** Windows 11 Pro
* **Python:** 3.14.3
* **Pytest:** 9.1.1
* **Node.js:** v24.19.0
* **npm:** 11.17.0
* **Vite:** 5.4.21
* **Branch Git:** `feat/p06-detalhe-rota`

---

## 1. Resumo Executivo da Entrega

A meta estipulada para 19/11/2026 foi plenamente atingida sob o princípio de independência estrita ("Ninguém espera ninguém"):
1. O professor ou avaliador consegue, de forma autônoma e reproduzível a partir de um clone limpo:
   * Inicializar o banco de dados via script idempotente sem caminhos absolutos (`python database/init_db.py`).
   * Executar a suíte completa de **50 testes automatizados** (42 em Python e 8 em Node.js), todos passando com 100% de sucesso.
   * Iniciar a API FastAPI e consultar o novo endpoint `GET /api/v1/rotas/{id}`, obtendo o detalhe completo da **Rota 1 Opção C (Belém → Manaus, voo + conexão em Santarém + barco)** em `http://localhost:8000/api/v1/rotas/rota-t3-t4`.
   * Abrir a aplicação web e navegar pela tela **P06** (`TelaDetalheRota.jsx`) tanto em tempo real via API (`#/rota/rota-t3-t4?data=2026-11-20`) quanto em modo de demonstração/laboratório offline isolado (`#/lab/p06`), conferindo a linha do tempo vertical em viewport mobile (360px), a conexão de **280 minutos (4 h 40 min)** em Santarém e o detalhamento dos trechos.
2. Nenhum arquivo de colegas de equipe foi modificado indevidamente, e o front-end conta com fallback gracioso caso as demais telas ainda não estejam integradas.

---

## 2. Execução dos Comandos e Saídas Reais

### 2.1 Inicialização do Banco de Dados
**Comando executado:**
```bash
python database/init_db.py
```
**Saída real obtida:**
```text
Caminho do banco: D:\Users\Kzar\Documents\Faculdade\Projeto Integrado II\database\embarque.db
Banco anterior removido com sucesso.
Esquema criado com sucesso (schema.sql).
Dados iniciais inseridos com sucesso (seed.sql).

Resumo da carga:
- Localidades: 7
- Modais: 10
- Operadores: 4
- Trechos: 11
- Horários de operação: 11
- Acomodações cadastradas: 4

============================================================
BANCO DE DADOS RECRIADO E POPULADO COM SUCESSO!
============================================================
```

---

### 2.2 Suíte de Testes Automatizados em Python (API e Motor de Rotas)
**Comando executado:**
```bash
python -m pytest api/tests -v
```
**Saída real obtida:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: D:\Users\Kzar\Documents\Faculdade\Projeto Integrado II
plugins: anyio-4.16.0
collecting ... collected 42 items

api/tests/test_api.py::TesteFastAPIEndpoints::test_01_listar_localidades_endpoint PASSED [  2%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_02_buscar_rotas_belem_manaus PASSED [  4%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_03_buscar_rotas_com_filtro_modais PASSED [  7%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_04_buscar_rotas_sem_resultados_tela_p10a PASSED [  9%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_05_localidade_inexistente_erro_padrao_404 PASSED [ 11%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_06_busca_insensivel_a_acentuacao_e_rota_retorno PASSED [ 14%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_07_validacao_origem_igual_destino_422 PASSED [ 16%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_08_validacao_criterio_invalido_422 PASSED [ 19%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_09_validacao_formato_data_invalida_422 PASSED [ 21%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_10_filtro_data_viagem_sexta_vs_sabado PASSED [ 23%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_11_campos_iso_e_id_deterministico PASSED [ 26%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_12_parametro_ausente_422_erro_padrao_e_docs_ativos PASSED [ 28%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_13_autocomplete_localidades_busca_sem_acento PASSED [ 30%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_14_opcao_unica_sem_selos_comparativos PASSED [ 33%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_15_banco_ausente_retorna_503_nos_dois_endpoints PASSED [ 35%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_16_detalhe_rota_sete_casos_secao_4_5 PASSED [ 38%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_17_rotas_campos_novos_belem_manaus_2026_11_20 PASSED [ 40%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_18_selos_detalhe_iguais_a_busca PASSED [ 42%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_19_banco_ausente_retorna_503_detalhe_rota PASSED [ 45%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_20_a_prova_de_enriquecimento_do_seed PASSED [ 47%]
api/tests/test_api.py::TesteFastAPIEndpoints::test_21_validacao_contrato_openapi_rota_detalhe PASSED [ 50%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_01_conexao_calculada_dinamicamente PASSED [ 52%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_02_conexao_impossivel_rejeitada PASSED [ 54%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_03_rota_1_tres_opcoes_e_opcao_c_combinada PASSED [ 57%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_04_rota_1_opcao_b_recebe_ambos_os_selos PASSED [ 59%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_05_rota_1_criterio_menor_custo PASSED [ 61%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_06_rota_2_manaus_tefe_valores_canonicos PASSED [ 64%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_07_rota_3_sem_resultados PASSED [ 66%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_08_trecho_desatualizado_acima_de_30_dias PASSED [ 69%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_09_filtro_por_dia_da_semana PASSED [ 71%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_10_filtro_por_modais PASSED [ 73%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_11_origem_igual_destino_devolve_lista_vazia PASSED [ 76%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_12_recarga_do_banco_idempotente PASSED [ 78%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_13_id_deterministico_baseado_em_trechos PASSED [ 80%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_14_conexao_impossivel_descartada_fim_a_fim PASSED [ 83%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_15_opcao_unica_sem_selos_comparativos PASSED [ 85%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_16_data_referencia_sistema_e_sobrescrita PASSED [ 88%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_17_limite_cinco_opcoes_apos_ordenacao PASSED [ 90%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_18_horarios_e_offsets_secao_4_4 PASSED [ 92%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_19_propriedade_consistencia_todas_opcoes_seed PASSED [ 95%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_20_obter_rota_por_ids_casos_sucesso_e_falha PASSED [ 97%]
api/tests/test_route_engine.py::TesteMotorRoteamentoCompleto::test_21_trecho_sem_horario_em_memoria PASSED [100%]

============================= 42 passed in 0.85s ==============================
```

---

### 2.3 Suíte de Testes Unitários em Node.js (Front-End)
**Comando executado:**
```bash
cd web
npm test
```
**Saída real obtida:**
```text
> embarque-amazonia-web@0.1.0 test
> node --test

✔ imunidade 1: ausência de telas dos colegas não impede montagem nem quebra runtime (0.7845ms)
✔ imunidade 2: rota legada (versão 12/11) sem horários renderiza com fallbacks seguros (0.2921ms)
✔ imunidade 3: rota de laboratório (#/lab/p06) possui flag de exemplo local e dados completos (0.6617ms)
✔ imunidade 4: parsing seguro de hash com parâmetros de consulta (0.1818ms)
✔ timeline: conexão de 280 min entre t3 e t4 na Rota 1 Opção C (1.215ms)
✔ timeline: formatação de horário com offsets (+1 dia e +2 dias) (0.1759ms)
✔ timeline: rota de 1 trecho direto não deve possuir conexões (0.6485ms)
✔ timeline: tolera rota no formato antigo sem horários cadastrados (0.1612ms)
ℹ tests 8
ℹ suites 0
ℹ pass 8
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 90.3111
```

---

### 2.4 Compilação de Produção do Front-End (Vite Build)
**Comando executado:**
```bash
cd web
npm run build
```
**Saída real obtida:**
```text
> embarque-amazonia-web@0.1.0 build
> vite build

vite v5.4.21 building for production...
transforming...
✓ 37 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.70 kB │ gzip:  0.41 kB
dist/assets/index-CVrLux6l.css    8.58 kB │ gzip:  2.10 kB
dist/assets/index-S7cQ7XeE.js   162.06 kB │ gzip: 51.96 kB
✓ built in 627ms
```

---

## 3. Matriz de Aceitação Funcional

### 3.1 Seção 7.1 — Endpoints da API e Motor de Rotas (7 Cenários)

| # | Cenário / Requisição | Status Esperado | Status Real | Resultado Verificado |
|---|---|---|---|---|
| **1** | `GET /api/v1/rotas/rota-t3-t4` | `200 OK` | `200 OK` | Rota Belém → Manaus, 2 trechos (t3: aéreo Azul, t4: fluvial Amazon Star), conexão de 280 min (4 h 40 min) em Santarém, tarifa total R$ 1.050,00, duração total 2040 min (34 h). |
| **2** | `GET /api/v1/rotas/rota-t1` | `200 OK` | `200 OK` | Rota direta de 1 trecho (t1: fluvial Amazon Star Belém → Manaus), sem conexões (`numero_conexoes: 0`), tarifa R$ 350,00, duração 8400 min (5 d 20 h). |
| **3** | `GET /api/v1/rotas/rota-t999` | `404 Not Found` | `404 Not Found` | Corpo de resposta padronizado: `{"codigo": "ROTA_NAO_ENCONTRADA", "mensagem": "Rota com trecho(s) inexistente(s) ou descontinuada."}`. |
| **4** | `GET /api/v1/rotas/invalida` | `422 Unprocessable` | `422 Unprocessable` | Corpo de resposta padronizado: `{"codigo": "PARAMETRO_INVALIDO", "mensagem": "Identificador de rota fora do formato esperado (ex: 'rota-t3-t4')."}`. |
| **5** | `GET /api/v1/rotas/rota-t3-t4?data=2026-11-20` | `200 OK` | `200 OK` | Resposta enriquecida com `data_viagem: "2026-11-20"`, `chegada_estimada_iso: "2026-11-21T18:00"`, `hora_partida: "08:00"`, `hora_chegada_estimada: "18:00"` e `chegada_dia_offset: 1`. |
| **6** | `GET /api/v1/rotas/rota-t3-t4?data=data-invalida` | `422 Unprocessable` | `422 Unprocessable` | Corpo de resposta padronizado: `{"codigo": "PARAMETRO_INVALIDO", "mensagem": "Data de viagem inválida. Utilize o formato YYYY-MM-DD."}`. |
| **7** | Paridade de Selos (Detalhe vs Busca) | Idêntico | Idêntico | A lista de selos de `GET /api/v1/rotas/rota-t3-t4` espelha com 100% de paridade o cálculo relativo de selos da busca em `/api/v1/rotas?origem=Belém&destino=Manaus`. |

---

### 3.2 Seção 7.2 — Interface Web e Tela P06 (Front-End)

| Critério de Aceitação | Verificação Realizada | Status |
|---|---|---|
| **Layout Mobile 360px** | Estilos em `TelaDetalheRota.css` com `max-width: 480px`, `min-width: 320px`, padding responsivo e sem estouro horizontal em 360px. | **Aprovado** |
| **Linha do Tempo Vertical** | Renderizada em elemento semântico `<ol class="timeline-lista">`, com cartões de eventos (`timeline-card-trecho`) e nós de conexão destacados. | **Aprovado** |
| **Conexão em Santarém** | Chegada do voo às 09:20 e partida do barco às 14:00. Intervalo calculado em **280 minutos (4 h 40 min)**. Badge de aviso presente. | **Aprovado** |
| **Acomodações e Contato** | Card de trecho exibe categoria do modal, telefone de contato do operador e badge de acomodações (ex.: Rede R$ 250,00). | **Aprovado** |
| **Acessibilidade** | Horários marcados com tags `<time>`, botões de trecho navegáveis com labels acessíveis (`aria-label`). Sem botões órfãos. | **Aprovado** |
| **Roteamento e Fallback** | `Navegacao.jsx` resolve `#/`, `#/rota/:id` e `#/lab/p06`. Telas não integradas dos colegas exibem aviso descritivo sem quebrar a aplicação. | **Aprovado** |
| **Laboratório Offline (`#/lab/p06`)** | Funciona de forma 100% autônoma a partir de `rota1_opcao_c.js`, sem requisições de rede, exibindo badge informativo. | **Aprovado** |

---

### 3.3 Seção 7.3 — Verificações de Terminal e Higiene do Repositório

| Checagem | Comando de Verificação | Resultado | Status |
|---|---|---|---|
| **Caminhos absolutos** | Busca por caminhos no código-fonte | Nenhum caminho absoluto de usuário (`C:\Users\...` ou `D:\Users\...`) presente no código. Caminhos resolvidos relativamente via `pathlib.Path(__file__)`. | **Aprovado** |
| **Arquivos ignorados** | `git ls-files` inspecionado | Nenhum `.env`, `.db`, `node_modules/` ou `dist/` rastreado no repositório Git. | **Aprovado** |
| **Integridade dos colegas** | `git diff` contra arquivos de Fernando, Herbert e Lucas | 0 arquivos dos colegas alterados (`database/`, `TelaFiltros.jsx`, `TelaComparar.jsx`, `TelaDetalheTrecho.jsx`, `format.js`, `index.css` intocados). | **Aprovado** |
| **Protocolo de merge em `App.jsx`** | Inspeção do diff em `App.jsx` | Apenas dois pontos modificados: recepção de `onAbrirRota` nas props e botão "Ver detalhes da rota" fora do bloco de comparação. | **Aprovado** |

---

## 4. Auditoria de Dados e Notificação de Alinhamento (Santarém)

Durante a formalização do contrato e testes unitários de integração temporal, foi detectada uma divergência entre a descrição inicial do card do Trello e a base de dados populada por `database/seed.sql`:
* **Descrição inicial no Trello:** sugeria horários teóricos de voo chegando 07:50 e barco saindo 12:30.
* **Realidade no `seed.sql` (Fernando):**
  * Trecho 3 (Voo Azul Belém → Santarém): Partida `08:00`, Duração 80 min → Chegada às **`09:20`**.
  * Trecho 4 (Barco Amazon Star Santarém → Manaus): Partida às **`14:00`**, Duração 1680 min (28 h) → Chegada às `18:00` do dia seguinte (`+1 dia`).
  * **Intervalo de Conexão Real:** das 09:20 às 14:00 = **280 minutos (4 h 40 min)**.

Adotou-se rigorosamente a **realidade comprovada do banco de dados**, formalizando os 280 minutos no contrato OpenAPI (`docs/openapi.yaml`), nos testes automatizados, na fixture de laboratório e na documentação.

---

## 5. Limitações Registradas (MVP Semana 2)

1. **Validação do Dia da Semana:** O filtro por dia da semana é aplicado a todos os trechos tomando como base o dia da partida inicial.
2. **Cálculo de Conexão no Mesmo Dia:** O cálculo de intervalo de conexão assume partidas no mesmo dia de calendário civil.
3. **Seleção de Horário Único:** O motor extrai o primeiro horário ativo de cada trecho ordenado por `hora_partida`.
4. **Fuso Horário:** Os horários operam em horário local nominal, sem conversão automática de fusos (Belém UTC-3 e Manaus UTC-4).
5. **Timestamp ISO de Chegada:** O campo `chegada_estimada_iso` omite intencionalmente a terminação de fuso horário no MVP.
