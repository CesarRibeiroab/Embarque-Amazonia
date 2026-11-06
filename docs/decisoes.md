# EMBARQUE AMAZÔNIA — DECISÕES TÉCNICAS E ROTEIRO DE ORIENTAÇÃO
**Documento Executivo de Alinhamento para Reunião com o Professor**  
**Projeto Integrado II • Ciência da Computação (CESUPA)**  
**Data:** 06/11/2026  
**Autores:** César Augusto Borges Ribeiro, Fernando César Mourão Fonseca, Herbert Aciolly Leão de Jesus, Lucas Barros Mutran  

---

## 1. PROPOSTAS DE DECISÃO TÉCNICA DO PRODUTO (PARA RATIFICAÇÃO COM PROFESSOR)

> [!NOTE]
> As decisões abaixo constituem a recomendação técnica consensual do grupo (conforme Card 56 do Trello), aguardando ratificação formal das regras da entrega final na orientação com o orientador (Card 55).

### Decisão 1: Stack Tecnológica Unificada (Python / FastAPI)
- **Motivação:** O núcleo do projeto é o motor algorítmico de roteamento em grafos multimodais (`engine/route_engine.py`). Para eliminar divergências de linguagem entre motor e back-end, adotamos **Python com FastAPI** como back-end unificado.
- **Back-end:** Python 3.10+ / FastAPI, implementando estritamente o contrato `openapi.yaml`.
- **Banco de Dados:** PostgreSQL 15+ estruturado via `database/schema.sql` e populado por `database/seed.sql` (ou SQLite em modo de contingência local).
- **Front-end Web/Mobile:** React + Vite configurado como PWA (service worker e IndexedDB para consulta de rotas salvas em modo offline).
- **Orquestração:** `docker-compose.yml` subindo banco e API localmente.
- **Estrutura do Repositório (Mono-repo):** `/api`, `/web`, `/docs`, `/database`.

### Decisão 2: Escopo do MVP e Alinhamento com o Trello
- **O que ENTRA no MVP:**
  1. Catálogo e autocompletar de localidades atendidas (municípios e portos).
  2. Motor de busca multimodal em grafo com até 3 trechos por rota.
  3. Ordenação pelos 3 critérios: **Menor Custo**, **Menor Tempo** e **Mais Confiável** (definido pela recência da atualização dos dados, onde dias desde a última atualização determinam a confiabilidade).
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
- **Atuação Efetiva da Ferramenta:** A IA atuou como aceleradora técnica de desenvolvimento de software: gerou o esqueleto inicial do contrato OpenAPI (`openapi.yaml`), a estrutura base do script SQL (`schema.sql` e `seed.sql`), o algoritmo preliminar de busca em profundidade com poda (`route_engine.py`), a suíte de testes unitários (`test_route_engine.py`) e apoiou a revisão ortográfica e formatação ABNT da Introdução.
- **Atuação dos Discentes:** Concepção da arquitetura e dos requisitos, definição dos parâmetros e regras de negócio da Amazônia Legal, parametrização dos dados de teste, auditoria de consistência, correção manual das incongruências do motor e do banco, e validação funcional de todos os testes no terminal. Cada integrante domina a lógica do que foi construído em suas respectivas frentes.

---

## 2. ROTEIRO UNIFICADO DE APRESENTAÇÃO AO PROFESSOR (3 MINUTOS)

> [!TIP]
> **Postura na reunião:** Objetiva, honesta e técnica. O orientador já conhece o protótipo e a ideia; ele quer constatar o avanço de engenharia sem exageros factuais.

```
[0:00 - 0:45] CONTEXTUALIZAÇÃO DO AVANÇO
"Professor, nas orientações anteriores nós demonstramos o escopo conceitual e o protótipo
navegável no Figma. Nesta semana, focamos em construir a fundação de engenharia para
destravar o front-end e o back-end em paralelo: formalizamos o contrato da API, normalizamos
o banco de dados e implementamos o motor de rotas de referência com testes automatizados."

[0:45 - 1:45] CONTRATO E BANCO DE DADOS
"Desenvolvemos a especificação OpenAPI 3.1 no arquivo openapi.yaml, detalhando a busca
multimodal com os três critérios exigidos — menor custo, menor tempo e mais confiável — e os
endpoints para alimentação cadastral pelos operadores.
No banco (schema.sql), modelamos a relação N:N entre operadores e modais e a data da última
atualização dos trechos, essencial para calcular a confiabilidade dos dados."

[1:45 - 2:30] DEMONSTRAÇÃO DO MOTOR E TESTES (AO VIVO NO TERMINAL)
[Abrir o terminal e rodar: python engine/test_route_engine.py]
"O motor foi escrito em Python com busca em grafo ponderado. Rodando a suíte de testes:
- Na Rota 1 (Belém–Manaus), ele calcula e compara as 3 alternativas (barco direto, avião direto
  e a rota combinada via Santarém), atribuindo os selos corretos de menor custo, menor tempo
  e mais confiável de acordo com a recência.
- Na Rota 2 (Manaus–Tefé), compara voadeira e barco regional.
- Na Rota 3 (Cametá–Alenquer), valida a resposta para localidades sem malha conectada."

[2:30 - 3:00] ALINHAMENTO DAS REGRAS DA ENTREGA FINAL
"Para consolidar o Marco 1, precisamos apenas registrar com o senhor as confirmações do
Card 55: data e horário limites da entrega final, canal de submissão no AVA, formato do artigo
(.doc ou .docx) e como o senhor prefere que a declaração de uso de IA seja anexada."
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
> **Resposta Alinhada:** *"A confiabilidade no sistema reflete a **recência da atualização das informações** cadastradas. Trechos atualizados recentemente possuem confiabilidade máxima; rotas cujos trechos não recebem atualização há mais de 30 dias são sinalizadas visualmente como 'Desatualizadas', orientando o viajante a confirmar os horários antes do embarque."*
