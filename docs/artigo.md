# Embarque Amazônia: Arquitetura de Hub Multimodal para a Amazônia Legal

**Embarque Amazônia: Multimodal Hub Architecture for the Brazilian Legal Amazon**

---

### Autoria (Cópia Identificada)
* **César Augusto Borges Ribeiro** (`cesar24070011@aluno.cesupa.br`)
* **Fernando César Mourão Fonseca** (`fernando24070034@aluno.cesupa.br`)
* **Herbert Aciolly Leão de Jesus** (`herbert24070016@aluno.cesupa.br`)
* **Lucas Barros Mutran** (`lucas23070208@aluno.cesupa.br`)  
*Discentes do Bacharelado em Ciência da Computação, Centro Universitário do Estado do Pará (CESUPA)*  
*Belém, Pará, Brasil*

> [!NOTE]
> **Para a Cópia Anônima (Blind Review):** Os nomes, e-mails e a filiação institucional acima devem ser omitidos na submissão anônima, bem como os metadados de autoria do arquivo `.doc`.

---

## RESUMO

A mobilidade humana na Amazônia Legal é condicionada pela bacia hidrográfica, por trechos sem ligação rodoviária contínua e pela variação sazonal do nível dos rios. Deslocamentos intermunicipais frequentemente exigem a combinação de diferentes modais (barcos regionais, voadeiras, balsas, ônibus e aviação regional), expondo os passageiros a lacunas de informação sobre horários e tarifas. Este artigo apresenta a especificação funcional, a arquitetura de software e o Produto Mínimo Viável (MVP) do **Embarque Amazônia**, um hub digital para planejamento de rotas multimodais na região. Como não identificamos APIs públicas abertas para o transporte fluvial de passageiros, a solução combina um modelo relacional normalizado com um motor de roteamento em grafo orientado a conexões intermodais, contemplando dez modais regionais. O trabalho entrega um protótipo de dezesseis telas no Figma, o contrato OpenAPI 3.1, uma API REST em Python e FastAPI com três operações de consulta, uma aplicação web em React e Vite (telas P01, P03, P05, P06, P07 e modo de demonstração offline) e validação por 51 testes automatizados.

**Palavras-chave:** Hub Multimodal; Amazônia Legal; Navegação Interior; Roteamento em Grafos; OpenAPI.

---

## ABSTRACT

Human mobility in the Brazilian Legal Amazon depends on an extensive river network, incomplete road connectivity, and seasonal river-level changes. Intercity trips often require combining multiple transport modes (regional riverboats, fast motorboats, ferries, buses, and regional flights), leaving passengers with fragmented schedule and fare information. This paper presents the functional specification, software architecture, and Minimum Viable Product (MVP) of **Embarque Amazônia**, a multimodal transit hub designed for the region. Because we did not identify open public APIs for riverine passenger transport, the solution pairs a normalized relational schema with a graph-based routing engine supporting ten regional modes. We deliver a sixteen-screen Figma prototype, an OpenAPI 3.1 specification, a Python/FastAPI REST service exposing three passenger query endpoints, an integrated React/Vite web interface (screens P01, P03, P05, P06, P07, and an offline demonstration mode), and validation through 51 automated tests.

**Keywords:** Multimodal Transit; Amazon Basin; Inland Navigation; Graph Routing; OpenAPI.

---

## 1. INTRODUÇÃO

A Amazônia Legal abrange mais de cinco milhões de quilômetros quadrados, cerca de 59% do território brasileiro, com população distribuída ao longo de extensos eixos fluviais (IBGE, 2026; IPEA, 2021). Nessa região, a hidrografia atua como eixo estruturante para o transporte de pessoas e mercadorias (IPEA, 2021; CNT, 2024). Centenas de municípios dependem das calhas dos rios Amazonas, Solimões, Tapajós e Madeira para acessar serviços de saúde, educação e comércio.

Por causa dessa geografia, uma viagem entre o interior e um centro urbano raramente ocorre em um único modal. O passageiro costuma sair de uma comunidade em embarcação de pequeno porte (*voadeira*), fazer baldeação em porto para um barco regional de linha (*gaiola*) com acomodação em rede, seguir por via terrestre em moto-táxi ou ônibus e, em alguns casos, embarcar em voo regional (ANTAQ, 2026; ANAC, 2024).

A organização dessas viagens esbarra em quatro dificuldades práticas:
1. **Fragmentação de rotas:** falta uma plataforma única que reúna trajetos fluviais, rodoviários e aéreos em um mesmo itinerário.
2. **Sazonalidade hidrológica:** durante a estiagem (de agosto a novembro), bancos de areia e redução de calado aumentam o tempo de navegação, sem registro centralizado dessas alterações (SGB; ANA, 2026).
3. **Ausência de interfaces abertas:** diferentemente da aviação comercial, não identificamos APIs públicas abertas para o transporte fluvial de passageiros, setor em que a venda de bilhetes ainda se concentra nos terminais e cais.
4. **Conectividade intermitente:** a falta de sinal móvel em trechos fluviais longos exige que o sistema preveja consulta posterior a itinerários salvos no aparelho.

O **Embarque Amazônia** foi projetado para responder a esses problemas por meio de uma base de dados unificada, cadastro descentralizado de operadores e cálculo de rotas sob três critérios: menor tempo, menor custo e maior confiabilidade (medida pela recência dos dados).

O restante do artigo está organizado da seguinte forma: a Seção 2 detalha a metodologia e os dez modais regionais; a Seção 3 descreve a modelagem de dados e o contrato OpenAPI; a Seção 4 apresenta o projeto de interface; a Seção 5 explica o motor de roteamento em grafo; a Seção 6 reúne os testes e resultados; e a Seção 7 traz as considerações finais.

---

## 2. METODOLOGIA E CARACTERIZAÇÃO DOS MODAIS

### 2.1 Abordagem Metodológica

O projeto foi conduzido em quatro etapas sequenciais: levantamento das normas regulatórias e estudos de transporte na Região Norte; especificação de requisitos, glossário regional e prototipação das interfaces no Figma; modelagem relacional e definição do contrato OpenAPI 3.1 (*contract-first*); e implementação incremental do banco de dados, motor em grafo, API REST e aplicação web com verificação por testes automatizados.

No recorte do Produto Mínimo Viável (MVP), priorizamos a jornada principal do passageiro (busca de localidades, cálculo de rotas multimodais, filtros, comparação de opções e detalhamento de conexões e trechos). Funcionalidades transacionais, como compra de passagens, pagamentos e painel administrativo autenticado completo, foram reservadas para etapas futuras.

### 2.2 Os Dez Modais Regionais e Fontes Regulatórias

O domínio do sistema contempla dez modais canônicos divididos nas categorias `fluvial`, `rodoviario` e `aereo`, resumidos na Tabela 1.

| Categoria | Modal | Código no Sistema | Enquadramento Operacional e Regulatório |
|---|---|---|---|
| Fluvial | Barco regional | `barco_regional` | Navegação interior regular; ANTAQ (Res. nº 136–141/2026) |
| Fluvial | Voadeira | `voadeira` | Lancha rápida regional; ANTAQ (Res. nº 136–141/2026) |
| Fluvial | Balsa pequena | `balsa_pequena` | Travessia fluvial local; ANTAQ (Res. nº 136–141/2026) |
| Fluvial | Balsa grande | `balsa_grande` | Transporte misto e Ro-Ro; ANTAQ (Res. nº 136–141/2026) |
| Rodoviário | Ônibus | `onibus` | Transporte coletivo regular; ANTT (Res. nº 6.033/2023) |
| Rodoviário | Carro | `carro` | Transporte complementar intermunicipal |
| Rodoviário | Moto-táxi | `moto_taxi` | Ligação urbana de última milha (regulação municipal) |
| Aéreo | Avião regional | `aviao_regional` | Aviação regional; ANAC (RBAC nº 121 e nº 135) |
| Aéreo | Táxi aéreo | `taxi_aereo` | Fretamento aéreo regional; ANAC (RBAC nº 135) |
| Aéreo | Helicóptero | `helicoptero` | Acesso aéreo a áreas remotas; ANAC (RBAC nº 135) |

*Tabela 1: Caracterização dos dez modais canônicos do Embarque Amazônia.*

Na categoria `fluvial`, o modelo inclui *barco regional* (linhas regulares com acomodação em rede ou camarote), *voadeira* (lancha rápida com motor de popa para deslocamentos curtos e médios), *balsa pequena* e *balsa grande* (travessias locais e transporte misto). A regulação de outorgas, afretamento e direitos dos passageiros na navegação interior segue as Resoluções nº 136 a 141 da ANTAQ (2026), além de levantamentos do IPEA (2021) e da CNT (2024).

Na categoria `rodoviario`, entram *ônibus*, *carro* (lotação/transporte complementar) e *moto-táxi* (ligação de última milha entre portos, aeroportos e áreas urbanas). O transporte rodoviário interestadual regular de passageiros é regido pela Resolução nº 6.033 da ANTT (2023). Na categoria `aereo`, estão *avião regional*, *táxi aéreo* e *helicóptero*, cujas operações seguem os Regulamentos Brasileiros da Aviação Civil RBAC nº 121 (ANAC, 2023) e RBAC nº 135 (ANAC, 2024).

### 2.3 Sazonalidade Hidrológica e Lacuna de APIs Abertas

Embora existam painéis estatísticos e boletins hidrológicos periódicos para a Bacia Amazônica (SGB; ANA, 2026), não encontramos APIs públicas documentadas que forneçam horários, tarifas e vagas do transporte fluvial de passageiros em tempo real. Por essa razão, a arquitetura prevê um módulo de cadastro assistido para operadores e administradores (telas A01 a A06), registrando a data da última atualização (`data_ultima_atualizacao`) em cada trecho para indicar ao viajante o quão recente é a informação.

Para lidar com a variação dos rios sem introduzir estimativas arbitrárias, o MVP exibe apenas observações textuais no campo `regime_hidrico_observacao` do trecho. Decidimos não aplicar multiplicadores numéricos fixos de atraso sobre a duração da viagem enquanto não houver série histórica empírica para calibrá-los.

---

## 3. ARQUITETURA DE DADOS E CONTRATO DE API

### 3.1 Modelo Relacional e Persistência

A persistência foi estruturada em modelo relacional normalizado (`database/schema.sql`), rodando localmente em SQLite 3 para facilitar a execução em bancada e preparada para migração ao PostgreSQL 15+. O esquema reúne sete tabelas:

1. `modal`: armazena os dez modais (`codigo`, `nome`, `categoria`, `velocidade_media_kmh`).
2. `localidade`: cadastra municípios, polos regionais, portos, aeroportos, comunidades e terminais rodoviários, com `codigo_ibge`, `codigo_iata`, coordenadas geográficas e indicador `e_polo_regional`.
3. `operador`: registra empresas regulares, cooperativas, autônomos e operadores governamentais (`telefone_contato`, `email_contato`, `tipo_operador`).
4. `operador_modal`: resolve a relação N:N entre operadores e modais, guardando `numero_registro`, `orgao_emissor` (`ANTAQ`, `ANTT`, `ANAC`, `CAPITANIA_MARINHA` ou `MUNICIPAL`) e `situacao_cadastral`.
5. `trecho`: representa as arestas direcionadas do grafo (`origem_id`, `destino_id`, com restrição `CHECK (origem_id <> destino_id)`), terminais, `duracao_estimada_minutos`, `tarifa_base_reais`, `sentido` (`ida`, `volta` ou `circular`), `regime_hidrico_observacao` e `data_ultima_atualizacao`.
6. `horario_operacao`: vincula horários de partida e chegada estimada ao trecho, usando máscara de bits `dias_semana_mask` (de 1 a 127, cobrindo de segunda-feira=1 a domingo=64) e `frequencia_descricao`.
7. `acomodacao_trecho`: registra opções de acomodação (`rede`, `cadeira_inclinavel`, `camarote_duplo`, `camarote_quadruplo`, `suite` e `assento_padrao`) e seus regimes tarifários (`fixo`, `dinamico`, `sob_consulta`).

*(Inserir Figura 1: Diagrama Entidade-Relacionamento das sete tabelas e cardinalidades do Embarque Amazônia, gerado a partir de `docs/diagramas_database.md`, centralizado com legenda abaixo.)*

Para testes reproduzíveis, o script `database/init_db.py` recria o banco com caminhos relativos ao diretório do projeto e carrega `database/seed.sql` com 7 localidades, 10 modais, 4 operadores, 11 trechos ilustrativos (IDs 1 a 7 e retornos 9 a 12) e 4 acomodações. As datas de atualização são calculadas em relação ao dia de execução (`date('now', 'localtime', '-N days')`).

### 3.2 Contrato OpenAPI 3.1 e API REST

O contrato de comunicação entre frontend e backend foi definido previamente em `docs/openapi.yaml` segundo a **OpenAPI Specification v3.1.0** (OPENAPI INITIATIVE, 2021). Das seis operações descritas no contrato, o servidor FastAPI (`api/main.py`) implementa as três operações de consulta do passageiro:

* `GET /api/v1/localidades`: lista localidades com filtro `?busca=` insensível a acentos para alimentar o *autocomplete*.
* `GET /api/v1/rotas`: calcula e ordena opções entre `origem` e `destino`, aceitando parâmetros opcionais de `data` (`YYYY-MM-DD`), `criterio` (`menor_tempo`, `menor_custo` ou `mais_confiavel`) e `modais`.
* `GET /api/v1/rotas/{id}`: reconstrói os detalhes de uma rota pelo identificador determinístico (validado pela expressão regular `^rota-t\d+(-t\d+){0,2}$`), retornando horários de partida e chegada com deslocamento de dias (`chegada_dia_offset`), carimbo ISO (`chegada_estimada_iso`), intervalos de conexão (`intervalo_conexao_minutos`), acomodações e telefone do operador.

As três operações administrativas previstas (`POST/GET /api/v1/trechos` e `POST /api/v1/operadores`, com autenticação `bearerAuth`) ficaram planejadas para o módulo de gestão. Erros de validação e disponibilidade seguem o schema `ErroPadrao` nos códigos HTTP `422` (`PARAMETRO_INVALIDO`), `404` (`LOCALIDADE_NAO_ENCONTRADA` ou `ROTA_NAO_ENCONTRADA`) e `503` (`BANCO_INDISPONIVEL`).

---

## 4. PROJETO DE INTERFACE E EXPERIÊNCIA DO USUÁRIO

### 4.1 Prototipação Conceitual no Figma

O protótipo inicial foi desenhado no Figma com 16 telas divididas em dois fluxos. O fluxo do passageiro (`360 × 800 px`) abrange busca rápida (`P01`), seletor de localidade (`P02`), filtros e preferências (`P03`), lista de resultados (`P04`), comparador lado a lado (`P05`), detalhe da rota (`P06`), detalhe do trecho (`P07`), mapa (`P08`), rotas salvas offline (`P09`) e estados de vazio ou erro (`P10`). O fluxo administrativo (`1440 × 1024 px`) cobre login (`A01`), painel de trechos (`A02`), formulários de trecho (`A03`), operador (`A04`) e localidade (`A05`), e confirmação (`A06`).

### 4.2 Aplicação Web Mobile-First e Acessibilidade

No MVP implementado em React e Vite (`web/`), a navegação utiliza roteamento baseado em *hash* (`web/src/Navegacao.jsx`), ligando as telas funcionais diretamente à API REST:

* **`#/` (`App.jsx`, telas P01, P02, P04 e P10):** formulário de busca com sugestões de localidades (`SugestoesLocalidades.jsx`), seleção de data e critério, listagem de até cinco rotas, tratamento explícito de busca sem resultados (como Cametá para Alenquer) e barra de seleção para comparação (`BarraComparacao.jsx`).
* **`#/filtros` (`TelaFiltros.jsx`, tela P03):** escolha dos critérios de ordenação e seleção individual dos dez modais.
* **`#/comparar` (`TelaComparar.jsx`, tela P05):** comparação lado a lado de tarifa, duração total, número de conexões, modais e recência.
* **`#/rota/{id}` (`TelaDetalheRota.jsx`, tela P06):** linha do tempo vertical em lista ordenada (`<ol>`), destacando terminais, horários, intervalos de conexão e acomodações. Inclui a rota isolada `#/lab/p06` carregada a partir de dados locais (`rota1_opcao_c.js`) para demonstrações sem rede.
* **`#/trecho/{id}` (`TelaDetalheTrecho.jsx`, tela P07):** visão detalhada do trecho individual com frequência semanal, observação hídrica, acomodações e telefone de contato.

A interface usa fonte `Inter` com algarismos tabulares (`tabular-nums`) para alinhar valores monetários e horários, além de foco visível (`:focus-visible`) para navegação por teclado. As cores principais (`#1B5E3F` verde e `#1F6FB2` azul) e os selos (`Menor custo` em `#2E7D32`, `Menor tempo` em `#1F6FB2`, `Mais confiável` em `#00796B` e `Desatualizado` em `#F2A900` com texto `#1A1A1A`) seguem critérios de contraste das *Web Content Accessibility Guidelines* (WCAG) 2.1 (W3C, 2018).

*(Inserir Figura 2: Capturas da aplicação web em execução mostrando a busca de rotas P01/P04 e a linha do tempo multimodal P06 com conexão em Santarém, centralizadas com legenda abaixo.)*

---

## 5. IMPLEMENTAÇÃO DO MOTOR DE ROTEAMENTO

### 5.1 Modelagem em Grafo e Busca em Profundidade

Em alinhamento com modelagens de redes de transporte público baseadas em grafos (PEIXOTO et al., 2020), o motor (`api/engine/route_engine.py`) representa localidades como vértices e trechos ativos como arestas direcionadas em listas de adjacência. O método `carregar_do_banco()` limpa estruturas prévias antes de ler o SQLite, garantindo recarga idempotente.

Ao receber origem e destino (normalizados sem acentos), `buscar_rotas()` executa uma busca em profundidade (DFS) limitada a caminhos simples sem ciclos, com no máximo 3 trechos (até 2 conexões). Para cada trecho, o motor seleciona o primeiro horário ativo (`ORDER BY hora_partida ASC LIMIT 1`) em `horario_operacao` compatível com o dia da semana da data informada e com o filtro opcional de modais.

### 5.2 Validação Temporal, Critérios e Selos

Na passagem de um trecho para o seguinte, o algoritmo exige que a partida do segundo trecho ocorra no mesmo dia e em horário igual ou posterior à chegada do primeiro (`hora_partida >= hora_chegada`). O tempo de espera (`intervalo_conexao_minutos`) é somado à duração dos trechos para compor `duracao_total_minutos`.

Cada opção válida recebe um identificador determinístico baseado nos IDs de seus trechos (por exemplo, `rota-t3-t4`) e é ordenada pelo critério escolhido: `menor_tempo`, `menor_custo` ou `mais_confiavel` (menor número de dias desde a atualização mais antiga entre os trechos da rota). Após a ordenação, o resultado é limitado a 5 opções.

Os selos `Menor custo`, `Menor tempo` e `Mais confiável` são atribuídos apenas quando existem 2 ou mais opções na busca, evitando destacar uma única rota como "melhor" por falta de alternativa. O selo `Desatualizado` aparece sempre que algum trecho supera 30 dias sem atualização, inclusive em opção única. Na rota de detalhe (`obter_rota_por_ids()`), os selos reproduzem exatamente o cálculo obtido na busca completa do mesmo par origem e destino.

---

## 6. TESTES E RESULTADOS

A validação do MVP foi executada na branch principal (`main`) com Python 3.14.3, Node.js v24.19.0 e SQLite 3 inicializado via `database/init_db.py`.

### 6.1 Suíte de Testes Automatizados

Foram executados 51 testes automatizados, todos aprovados sem falhas. No backend em Python, `api/tests/test_route_engine.py` reúne 21 testes unitários do motor (cálculo de conexões, rejeição de conexões inválidas, casos canônicos, filtros por dia da semana e modal, recarga idempotente, limite de 5 opções, regra de selos e deslocamento de dias) e `api/tests/test_api.py` contém 22 testes de integração HTTP com `TestClient` (endpoints `/localidades`, `/rotas`, `/rotas/{id}`, respostas `422`, `404` e `503`, paridade de selos, tolerância a enriquecimento do banco e aderência ao `docs/openapi.yaml`). No frontend, `web/src/utils/timeline.test.js` e `web/src/utils/imunidade.test.js` executam 8 testes em `node --test` validando a linha do tempo, formatação de dias extras (`+1 dia`, `+2 dias`), os 280 minutos de conexão em Santarém e o funcionamento offline de `#/lab/p06`.

| Camada / Arquivo | Tecnologia | Quantidade | Escopo Verificado | Resultado |
|---|---|---:|---|---|
| Motor (`api/tests/test_route_engine.py`) | Python (`pytest`) | 21 | Grafo DFS, conexões, filtros, selos e recarga | 21 aprovados |
| API REST (`api/tests/test_api.py`) | Python (`TestClient`) | 22 | Endpoints, erros `422/404/503` e OpenAPI 3.1 | 22 aprovados |
| Linha do tempo (`web/src/utils/timeline.test.js`) | Node (`node --test`) | 4 | Offsets de dias e conexão de 280 min | 4 aprovados |
| Imunidade (`web/src/utils/imunidade.test.js`) | Node (`node --test`) | 4 | Dados legados, hash routing e modo `#/lab/p06` | 4 aprovados |
| **Total** | **Python + Node.js** | **51** | **Backend e Frontend integrados** | **51 aprovados** |

*Tabela 2: Resumo da suíte de testes automatizados do Embarque Amazônia.*

### 6.2 Verificação Integrada e Cenário Canônico

Em execução integrada no navegador Google Chrome com o servidor FastAPI ativo, a consulta **Belém → Manaus** (data ilustrativa sexta-feira `2026-11-20`) retornou as 3 opções esperadas:
1. **Opção B (`rota-t2`, Avião regional, Azul):** `2 h 15 min` (`135 min`), `R$ 780,00`, sem conexões, com selos `Menor tempo` e `Mais confiável`.
2. **Opção C (`rota-t3-t4`, Combinada Azul + Amazon Star):** voo Belém → Santarém (`08:00` às `09:20`, `R$ 540,00`), conexão de **280 min (`4 h 40 min`)** em Santarém e barco regional Santarém → Manaus (`14:00` às `08:00 +2 dias`, `R$ 210,00`), totalizando `2 d` (`2880 min`) e `R$ 750,00`.
3. **Opção A (`rota-t1`, Barco regional, Amazon Star):** `5 d 20 h` (`8400 min`), `R$ 350,00`, sem conexões, com selo `Menor custo`.

A navegação entre `#/`, `#/filtros` (P03), `#/comparar` (P05), `#/rota/rota-t3-t4` (P06), `#/trecho/3` (P07) e `#/lab/p06` funcionou sem erros de execução no console e sem barra de rolagem horizontal.

---

## 7. CONSIDERAÇÕES FINAIS

O **Embarque Amazônia** consolidou uma arquitetura funcional para consulta de rotas multimodais na Amazônia Legal, integrando banco relacional normalizado, contrato OpenAPI 3.1, motor em grafo, API FastAPI e interface React verificada por 51 testes automatizados.

Permanecem como limitações conhecidas do MVP: o uso de dados ilustrativos no banco local pela ausência de APIs públicas abertas no setor fluvial; a verificação do dia da semana aplicada apenas pela data de partida para todos os trechos; o cálculo de conexões restrito ao mesmo dia civil usando o primeiro horário ativo por trecho; a ausência de conversão entre fusos horários (como Belém UTC-3 e Manaus UTC-4); e a manutenção das telas administrativas (`A01–A06`), mapa interativo (`P08`) e armazenamento local em IndexedDB (`P09`) apenas no protótipo do Figma, contando no código apenas com a rota de demonstração offline.

Como trabalhos futuros, prevê-se a implementação das rotas administrativas autenticadas (`POST /api/v1/trechos` e `POST /api/v1/operadores`), a migração do SQLite local para PostgreSQL em homologação, a persistência offline em IndexedDB e a incorporação de séries históricas hidrológicas para calibrar estimativas sazonais.

---

## REFERÊNCIAS

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 121:** Requisitos operacionais: operações domésticas, de bandeira e suplementares. Brasília, DF: ANAC, 2023.

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 135:** Requisitos operacionais: operações de transporte aéreo público sob demanda e regular não agendado. Brasília, DF: ANAC, 2024.

AGÊNCIA NACIONAL DE TRANSPORTES AQUAVIÁRIOS (ANTAQ). **Resoluções nº 136 a 141, de 17 de agosto de 2026** (publicadas no Diário Oficial da União em 19 de agosto de 2026): Consolidam o marco regulatório da navegação interior, outorgas, afretamento e direitos dos passageiros. Brasília, DF: ANTAQ, 2026.

AGÊNCIA NACIONAL DE TRANSPORTES TERRESTRES (ANTT). **Resolução nº 6.033, de 14 de dezembro de 2023:** Marco Regulatório do Transporte Rodoviário Coletivo Interestadual de Passageiros. Brasília, DF: ANTT, 2023.

CONFEDERAÇÃO NACIONAL DO TRANSPORTE (CNT). **Pesquisa CNT de Navegação Interior 2024:** Panorama hidroviário e transporte de passageiros na Região Norte. Brasília, DF: CNT, 2024.

INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA (IBGE). **Amazônia Legal — Panorama territorial e demográfico.** Rio de Janeiro: IBGE, 2026. Disponível em: https://www.ibge.gov.br. Acesso em: nov. 2026.

INSTITUTO DE PESQUISA ECONÔMICA APLICADA (IPEA). **Transporte Fluvial de Passageiros na Amazônia: Desafios de Regulação, Infraestrutura e Acessibilidade Regional.** Brasília, DF: IPEA, 2021.

OPENAPI INITIATIVE. **OpenAPI Specification v3.1.0.** Linux Foundation, 2021. Disponível em: https://spec.openapis.org/oas/v3.1.0. Acesso em: nov. 2026.

PEIXOTO, Altieris Marcelino et al. Plataforma Computacional para Construção de um Banco de Dados de Grafo do Sistema de Transporte de Curitiba. In: **IV WORKSHOP DE COMPUTAÇÃO URBANA (CoUrb 2020)**. Anais [...]. Porto Alegre: Sociedade Brasileira de Computação (SBC), 2020. Disponível em: https://sol.sbc.org.br/index.php/courb/article/view/12358. Acesso em: nov. 2026.

SERVIÇO GEOLÓGICO DO BRASIL (SGB); AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (ANA). **Sistema de Alerta de Eventos Críticos (SACE) — Boletins de Monitoramento Hidrológico da Bacia Amazônica.** Brasília, DF: SGB/ANA, 2026. Disponível em: https://www.sgb.gov.br. Acesso em: nov. 2026.

WORLD WIDE WEB CONSORTIUM (W3C). **Web Content Accessibility Guidelines (WCAG) 2.1: W3C Recommendation.** 2018. Disponível em: https://www.w3.org/TR/WCAG21/. Acesso em: nov. 2026.

---

## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL GENERATIVA
*Conforme regulamentação acadêmica do CESUPA para uso de IA Generativa.*

* **Ferramenta Utilizada:** Antigravity AI / Large Language Models e agente de execução em repositório.
* **Finalidade e Escopo de Aplicação:** A IA generativa apoiou a geração e refatoração do motor de roteamento (`api/engine/route_engine.py`), do esquema SQL (`database/schema.sql` e `database/seed.sql`), do contrato OpenAPI (`docs/openapi.yaml`), das suítes de testes automatizados (`api/tests/` e `web/src/utils/*.test.js`), dos endpoints da API FastAPI (`api/main.py`) e da interface web (`web/`), além de auxiliar na estruturação, redação técnica e revisão normativa/ortográfica deste artigo. Um agente automatizado operou diretamente no repositório na edição de arquivos, execução de testes e verificação em navegador.
* **Autoria e Validação Discente:** Os discentes autores conceberam o escopo, definiram os requisitos e as regras de negócio da Amazônia Legal, parametrizaram os casos canônicos ilustrativos, auditaram a consistência entre banco, código e documentação e validaram funcionalmente todos os resultados nos testes automatizados, no servidor local e no navegador.
