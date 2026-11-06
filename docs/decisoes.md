# EMBARQUE AMAZÔNIA — DECISÕES TÉCNICAS E ROTEIRO DE ORIENTAÇÃO
**Documento Executivo de Alinhamento para Reunião com o Professor**  
**Projeto Integrado II • Ciência da Computação (CESUPA)**  
**Data:** 06/11/2026  
**Autores:** César Augusto Borges Ribeiro, Fernando César Mourão Fonseca, Herbert Aciolly Leão de Jesus, Lucas Barros Mutran  

---

## 1. PROPOSTAS DE DECISÃO TÉCNICA DO PRODUTO (PARA RATIFICAÇÃO COM O PROFESSOR)

> [!NOTE]
> As decisões abaixo constituem a recomendação técnica consensual do grupo (conforme Card 56 do Trello), aguardando ratificação formal das diretrizes da entrega final na orientação com o orientador.

### Decisão 1: Stack Tecnológica Unificada (Python / FastAPI)
- **Motivação:** O núcleo do projeto é o motor algorítmico de roteamento em grafos multimodais (`api/engine/route_engine.py`). Para eliminar divergências de linguagem entre motor e back-end, adotamos **Python com FastAPI** como back-end unificado.
- **Back-end:** Python 3.10+ / FastAPI, implementando os endpoints de consulta do contrato `docs/openapi.yaml` (`GET /localidades` e `GET /rotas`).
- **Banco de Dados:** SQLite em desenvolvimento local (gerado dinamicamente via `database/init_db.py`), com esquema `database/schema.sql` e seed `database/seed.sql` compatíveis com migração para **PostgreSQL** na fase de homologação.
- **Front-end Web/Mobile:** React + Vite configurado como PWA (service worker e IndexedDB para consulta de rotas salvas em modo offline).
- **Estrutura do Repositório (Mono-repo):** `/api`, `/web`, `/docs`, `/database`.

### Decisão 2: Escopo do MVP e Alinhamento com o Trello
- **O que ENTRA no MVP:**
  1. Catálogo e autocompletar de localidades atendidas (municípios e portos).
  2. Motor de busca multimodal em grafo com até 3 trechos por rota.
  3. Ordenação pelos 3 critérios: **Menor custo**, **Menor tempo** e **Mais confiável** (definido pela recência da atualização dos dados, onde dias desde a última atualização determinam a confiabilidade).
  4. Comparação de até 3 alternativas e detalhe de trecho.
  5. Salvar rota e consulta offline (P09) via IndexedDB.
  6. Painel administrativo descentralizado para cadastro de trechos por operadores locais (telas A01–A06).
  7. Observação textual sobre regime hídrico (cheia/vazante).
- **O que NÃO ENTRA no MVP (Conforme Card 56):**
  - Reserva/venda de passagens e gateway de pagamento.
  - Alertas dinâmicos de enchentes em tempo real e push notifications.
  - Bot de WhatsApp.
  - Login de passageiro.
  - Ponto de transbordo como entidade complexa de infraestrutura física (a conexão é tratada unicamente como intervalo de tempo de espera entre o desembarque de um trecho e o embarque no subsequente).
  - Fator numérico multiplicador de seca rígido (mantido como parâmetro opcional/configurável no algoritmo para evitar afirmações sem base hidrológica estrita).

### Decisão 3: Padrões de Dados e Selos Visuais (Alinhamento Card 1 do Trello)
- **Selos Padronizados:**
  - `Menor custo` (verde #2E7D32)
  - `Menor tempo` (azul #1F6FB2)
  - `Mais confiável` (verde-azulado #00796B)
  - `Desatualizado` (amarelo #F2A900 para dados com última atualização acima de 30 dias)
- **Conceito de Confiabilidade:** Quão recente é a data da última atualização dos dados cadastrados do trecho (`data_ultima_atualizacao`). Quanto mais recente, mais confiável a estimativa; dados com mais de 30 dias recebem o indicativo visual de desatualização.
- **Natureza dos Dados:** Os dados de teste são **dados de exemplo ilustrativos e canônicos**, situados dentro das faixas operacionais identificadas no levantamento, sem qualquer pretensão de representar tabelas comerciais vigentes de operadores.

### Decisão 4: Declaração Real de Uso de Inteligência Artificial Generativa
*Em estrito cumprimento à Resolução nº 001/2026 do CESUPA:*
- **Ferramenta Utilizada:** Antigravity AI / Large Language Models.
- **Atuação Efetiva da Ferramenta:** A IA atuou como aceleradora técnica de desenvolvimento de software: gerou o esqueleto inicial do contrato OpenAPI (`docs/openapi.yaml`), a estrutura base do script SQL (`schema.sql` e `seed.sql`), o algoritmo preliminar de busca em profundidade com poda (`api/engine/route_engine.py`), a suíte de testes unitários (`api/tests/test_route_engine.py`) e apoiou a revisão ortográfica e formatação ABNT da Introdução.
- **Atuação dos Discentes:** Concepção da arquitetura e dos requisitos, definição dos parâmetros e regras de negócio da Amazônia Legal, parametrização dos dados de teste, auditoria de consistência, correção manual das incongruências do motor e do banco, e validação funcional de todos os testes no terminal. Cada integrante domina a lógica do que foi construído em suas respectivas frentes.

---

## 2. ROTEIRO UNIFICADO DE APRESENTAÇÃO AO PROFESSOR (3 MINUTOS)

> [!TIP]
> **Postura na reunião:** Objetiva, honesta e técnica. O orientador já conhece o protótipo e a ideia; ele quer constatar o avanço de engenharia sem exageros factuais.

```
[0:00 - 0:45] CONTEXTUALIZAÇÃO DO AVANÇO
"Professor, nas orientações anteriores nós demonstramos o escopo conceitual e o protótipo
navegável no Figma. Nesta semana, focamos em construir a fundação de engenharia para
destravar o front-end e o back-end em paralelo: formalizamos o contrato da API, organizamos
o repositório em mono-repo, normalizamos o banco de dados e implementamos o motor de rotas
de referência com testes automatizados."

[0:45 - 1:45] CONTRATO E BANCO DE DADOS
"Desenvolvemos a especificação OpenAPI 3.1 no arquivo openapi.yaml, detalhando a busca
multimodal com os três critérios exigidos — Menor custo, Menor tempo e Mais confiável — e os
endpoints para alimentação cadastral pelos operadores.
No banco de dados (usando SQLite em desenvolvimento local e PostgreSQL previsto para a
homologação), cadastramos os 10 modais regionais e modelamos a relação N:N entre operadores
e modais e a data da última atualização dos trechos, essencial para calcular a confiabilidade."

[1:45 - 2:30] DEMONSTRAÇÃO DO MOTOR E TESTES (AO VIVO NO TERMINAL)
[Abrir o terminal e rodar: python api/tests/test_route_engine.py]
"O motor foi escrito em Python e consome diretamente a base de dados relacional.
Rodando a suíte com 8 testes automatizados:
- Na Rota 1 (Belém–Manaus), calcula as 3 opções (barco direto, avião direto e combinada via
  Santarém), calculando dinamicamente a conexão de 4h 40min e atribuindo os selos corretos.
- Na Rota 2 (Manaus–Tefé), compara voadeira expressa e barco regional.
- Na Rota 3 (Cametá–Alenquer), valida o retorno vazio para localidades sem malha conectada.
- Rejeita conexões com horários impossíveis e sinaliza trechos desatualizados há mais de 30 dias."

[2:30 - 3:00] ALINHAMENTO DAS DIRETRIZES DA ENTREGA FINAL
"Para consolidarmos o Marco 1, precisamos apenas registrar com o senhor as confirmações das
diretrizes da entrega final: prazo e horário limites oficiais, canal de submissão no AVA,
formato do artigo (.doc ou .docx) e como o senhor prefere que a declaração de uso de IA seja anexada."
```

---

## 3. BANCO DE PERGUNTAS E RESPOSTAS AUDITADO (SEM AFIRMAÇÕES ARRISCADAS)

### P1: "Vocês já têm uma API conectada a um serviço real de barcos na Amazônia?"
> **Resposta Honesta:** *"Não, professor. Em nosso levantamento técnico, **não identificamos APIs públicas abertas e documentadas** para a bilhetagem ou horários dos barcos regionais de linha. Por isso, a arquitetura do Embarque Amazônia contempla um painel de cadastro descentralizado (telas A01–A06), permitindo que empresas e cooperativas locais alimentem e mantenham suas rotas, enquanto modais regulares como a aviação podem consumir agregadores consolidados."*

### P2: "Como o algoritmo trata a seca dos rios e o atraso das viagens?"
> **Resposta Precisa:** *"No escopo do nosso MVP, o tratamento prioritário é a exibição de avisos informativos sobre o regime hídrico cadastrados no trecho (cheia ou vazante). Do ponto de vista algorítmico, incluímos um parâmetro configurável de acréscimo temporal na navegação fluvial, mas o tratamos como estimativa aproximada, pois a variação real de tempo depende da calha de cada rio e do calado da embarcação."*

### P3: "Por que desenvolver um motor próprio em vez de usar o Google Maps ou OSRM?"
> **Resposta Precisa:** *"Os provedores globais como Google Routes e OSRM são excelentes para redes viárias urbanas e rodovias pavimentadas, mas **não cobrem de forma integrada os barcos regionais da Amazônia, suas especificidades de acomodação (rede vs. camarote), os intervalos reais de transbordo nos cais e a grade de horários fluviais**. Nosso motor foi projetado especificamente para conectar modais heterogêneos onde o transporte hidroviário é o elo principal da viagem."*

### P4: "Como está estruturada a lista de referências do artigo?"
> **Resposta Transparente:** *"A Seção 1 do artigo já referencia formalmente as fontes estruturantes citadas no texto — incluindo relatórios do IPEA, ANTAQ, ANAC e dados setoriais da CNT. Temos uma lista expandida de referências bibliográficas mapeadas para os modais e a modelagem, as quais estão sendo conferidas uma a uma para inserção nas Seções 2 e 3 conforme os rascunhos forem integrados."*

### P5: "Como é calculada a confiabilidade de uma rota?"
> **Resposta Alinhada:** *"A confiabilidade no sistema reflete a **recência da atualização das informações** cadastradas. Trechos atualizados recentemente possuem confiabilidade máxima; rotas cujos trechos não recebem atualização há mais de 30 dias são sinalizadas visualmente com o selo 'Desatualizado', orientando o viajante a confirmar os horários antes do embarque."*

### P6: "Por que o Prism devolve a mesma rota se eu mudar os parâmetros no mock?"
> **Resposta Precisa:** *"O mock do Prism simula a interface HTTP e valida os tipos de dados do contrato OpenAPI para permitir que o front-end desenvolva seus componentes de tela sem esperar o back-end. Ele devolve o payload canônico documentado como exemplo estático. A lógica de busca dinâmica, grafo e ordenação por critérios está implementada no motor em Python (`api/engine/route_engine.py`), que demonstramos executando diretamente sobre a base de dados."*
