# Embarque Amazônia: Arquitetura de Hub Multimodal para a Amazônia Legal

**Embarque Amazônia: Multimodal Hub Architecture for the Brazilian Legal Amazon**

---

### Autoria (Cópia Identificada)
* **César Augusto Borges Ribeiro**
* **Fernando César Mourão Fonseca**
* **Herbert Aciolly Leão de Jesus**
* **Lucas Barros Mutran**  
*Discentes do Bacharelado em Ciência da Computação — Centro Universitário do Estado do Pará (CESUPA)*  
*Belém, Pará, Brasil*

> [!NOTE]
> **Para a Cópia Anônima (Blind Review):** Os nomes e a filiação institucional acima devem ser omitidos na submissão anônima, mantendo título, resumo e corpo textual conforme as diretrizes da disciplina.

---

## RESUMO

A mobilidade humana na Amazônia Legal é condicionada por densa bacia hidrográfica, lacunas na malha rodoviária e severa sazonalidade hidrológica. Deslocamentos intermunicipais frequentemente exigem a combinação desarticulada de múltiplos modais — barcos regionais, voadeiras, balsas, ônibus e aviação regional —, submetendo passageiros a forte assimetria de informação. Este artigo propõe a especificação funcional, a arquitetura de software e o protótipo do **Embarque Amazônia**, concebido como hub integrador multimodal de transportes para a região. A proposta fundamenta-se na caracterização de dez modais regionais — considerando que não identificamos APIs públicas abertas para o setor fluvial — e na proposição de uma arquitetura relacional orientada a grafos ponderados de conexão intermodal. São apresentados um protótipo de dezesseis telas em fluxo mobile e desktop, um contrato de API REST em OpenAPI 3.1 e uma implementação inicial funcional do motor de roteamento e da busca web. A iniciativa busca fornecer bases de engenharia de software para o planejamento integrado de itinerários na região amazônica.

**Palavras-chave:** Hub Multimodal; Amazônia Legal; Navegação Interior; Engenharia de Requisitos; Roteamento em Grafos.

---

## ABSTRACT

Human mobility in the Brazilian Legal Amazon is constrained by an extensive hydrographic network, critical gaps in road infrastructure, and severe hydrological seasonality. Regional transit often mandates the fragmented chaining of disparate travel modes — including traditional riverboats, fast motorboats, roll-on/roll-off ferries, intercity coaches, and regional aviation — imposing significant informational asymmetry on passengers. This paper proposes the functional specification, software architecture, and prototype of **Embarque Amazônia**, a digital multimodal transit hub platform designed for the region. The proposal is grounded in the profiling of ten regional transit modes — given that no open public application programming interfaces (APIs) were identified for the riverine passenger sector — and a relational data architecture tailored for weighted intermodal graph routing. We present a sixteen-screen Figma prototype across mobile and desktop workflows, an OpenAPI 3.1 contract, and an initial working implementation of the routing engine and web search interface. This work establishes software engineering foundations to support integrated itinerary planning across Amazonian routes.

**Keywords:** Multimodal Transit; Amazon Basin; Inland Navigation; Requirements Engineering; Graph Routing.

---

## 1. INTRODUÇÃO

A Região Amazônica brasileira abrange mais de cinco milhões de quilômetros quadrados (cerca de 59% do território nacional) e apresenta ampla dispersão populacional ao longo de extensos eixos hidrográficos (IBGE; IPEA, 2021). Ao contrário das regiões Sul e Sudeste, cuja conectividade logística baseia-se fundamentalmente em malhas rodoviárias integradas, o transporte na Amazônia Legal tem a hidrografia como eixo estruturante de circulação de pessoas e mercadorias (IPEA, 2021; CNT, 2024). Centenas de municípios dependem prioritariamente de hidrovias navegáveis — como as calhas dos rios Amazonas, Solimões, Tapajós e Madeira — para acesso a serviços essenciais de saúde, educação e comércio.

Nesse contexto, o deslocamento raramente se concretiza por meio de um modal único. Uma viagem típica entre o interior e um centro urbano exige cadeias intermodais: o usuário parte de uma comunidade em embarcação vicinal de pequeno porte (*voadeira*), realiza baldeação em porto fluvial para barco regional de linha (*gaiola*) com acomodação em rede, efetua conexão terrestre — por moto-táxi ou ônibus coletivo — e, eventualmente, embarca em voo regular ou regional (ANTAQ, 2026; ANAC, 2024).

Contudo, essa mobilidade enfrenta gargalos crônicos decorrentes da assimetria informacional:
1. **Inexistência de roteamento integrado:** Não há plataformas que agreguem sob o mesmo modelo de itinerário o transporte fluvial tradicional, rodoviário e aéreo, impondo planejamento empírico aos viajantes.
2. **Severa sazonalidade hidrológica:** No período de estiagem (agosto a novembro, acompanhado em boletins hidrológicos anuais na Bacia Amazônica), o surgimento de bancos de areia e o rebaixamento de calado ampliam os tempos de percurso fluvial, sem mecanismos digitais centralizados que sinalizem tais variações (SGB; ANA, 2026).
3. **Carência de interfaces abertas identificadas:** Enquanto a aviação comercial adota padrões consolidados de distribuição eletrônica, não identificamos APIs públicas abertas para o setor fluvial de passageiros, onde predomina a bilhetagem física nos terminais e cais.
4. **Desafios de conectividade:** A instabilidade ou ausência de sinal móvel (3G/4G) ao longo de vastos trechos fluviais motiva requisitos futuros de consulta com armazenamento local de itinerários salvos.

Diante desse cenário, este trabalho propõe o projeto e a construção inicial do **Embarque Amazônia**, um hub multimodal adaptado à Amazônia Legal. O objetivo central consiste em modelar trajetos heterogêneos, estruturar o cadastro descentralizado de operadores e calcular itinerários sob múltiplos critérios — menor custo, menor tempo e mais confiável (mensurado pela recência dos dados).

O artigo organiza-se a partir de uma abordagem metodológica em etapas: caracteriza dez modais regionais e analisa limitações de integração de dados; propõe uma arquitetura de dados relacional normalizada com suporte a relações N:N entre operadores e modais; e detalha um protótipo de dezesseis telas e implementação parcial da busca voltados à usabilidade regional. O restante do trabalho estrutura-se em: Metodologia e Modais (§2), APIs e Modelo de Dados (§3), Projeto de Interface (§4), Implementação do Motor (§5), Testes e Resultados (§6) e Considerações Finais (§7).

---

## REFERÊNCIAS

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 121:** Requisitos operacionais: operações domésticas, de bandeira e suplementares. Brasília, DF: ANAC, 2023.

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 135:** Requisitos operacionais: operações de transporte aéreo público sob demanda e regular não agendado. Brasília, DF: ANAC, 2024.

AGÊNCIA NACIONAL DE TRANSPORTES AQUAVIÁRIOS (ANTAQ). **Resoluções nº 136 a 141, de 17 de agosto de 2026** (publicadas no Diário Oficial da União em 19 de agosto de 2026): Consolidam o marco regulatório da navegação interior, outorgas, afretamento e direitos dos passageiros. Brasília, DF: ANTAQ, 2026.

AGÊNCIA NACIONAL DE TRANSPORTES TERRESTRES (ANTT). **Resolução nº 6.033, de 14 de dezembro de 2023:** Marco Regulatório do Transporte Rodoviário Coletivo Interestadual de Passageiros. Brasília, DF: ANTT, 2023.

CONFEDERAÇÃO NACIONAL DO TRANSPORTE (CNT). **Pesquisa CNT de Navegação Interior 2024:** Panorama hidroviário e transporte de passageiros na Região Norte. Brasília, DF: CNT, 2024.

INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA (IBGE). **Amazônia Legal — Panorama territorial e demográfico.** Rio de Janeiro: IBGE. Disponível em: https://www.ibge.gov.br. Acesso em: nov. 2026.

INSTITUTO DE PESQUISA ECONÔMICA APLICADA (IPEA). **Transporte Fluvial de Passageiros na Amazônia: Desafios de Regulação, Infraestrutura e Acessibilidade Regional.** Brasília, DF: IPEA, 2021.

SERVIÇO GEOLÓGICO DO BRASIL (SGB); AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (ANA). **Sistema de Alerta de Eventos Críticos (SACE) — Boletins de Monitoramento Hidrológico da Bacia Amazônica.** Brasília, DF: SGB/ANA, 2026. Disponível em: https://www.sgb.gov.br.

---

## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL GENERATIVA
*Conforme regulamentação acadêmica do CESUPA para uso de IA Generativa.*

* **Ferramenta Utilizada:** Antigravity AI / Large Language Models e agente de execução em repositório.
* **Finalidade e Escopo de Aplicação:** A IA generativa gerou o motor de roteamento (`api/engine/route_engine.py`), o esquema SQL (`database/schema.sql` e `database/seed.sql`), o contrato OpenAPI (`docs/openapi.yaml`), as suítes de testes automatizados (`api/tests/`), os endpoints da API FastAPI (`api/main.py`) e o esqueleto inicial da busca web (`web/`), além de apoiar a estruturação e revisão ortográfica/ABNT da Seção 1. Um agente automatizado operou diretamente o repositório na edição de arquivos e commits no Git.
* **Autoria e Validação Discente:** Os discentes autores conceberam o escopo, definiram os requisitos e as regras de negócio da Amazônia Legal, parametrizaram os casos canônicos ilustrativos, auditaram a consistência entre banco, código e documentação e validaram funcionalmente os resultados nos testes automatizados e execuções em terminal.
