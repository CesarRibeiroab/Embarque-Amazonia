# Embarque Amazônia: Proposta de Arquitetura de Informação e Hub Digital Multimodal para Integração do Transporte de Passageiros na Amazônia Legal

**Embarque Amazônia: An Information Architecture and Digital Multimodal Hub Proposal for Passenger Transport Integration in the Brazilian Legal Amazon**

---

### Versão Identificada (Para Submissão Regular)
* **César Augusto Borges Ribeiro** — cesar24070011@aluno.cesupa.br
* **Fernando César Mourão Fonseca** — fernando24070034@aluno.cesupa.br
* **Herbert Aciolly Leão de Jesus** — herbert24070016@aluno.cesupa.br
* **Lucas Barros Mutran** — lucas23070208@aluno.cesupa.br  
*Discentes do Bacharelado em Ciência da Computação — Centro Universitário do Estado do Pará (CESUPA)*  
*Belém, Pará, Brasil*

> [!NOTE]
> **Para a Cópia Anônima (Blind Review):** Os nomes, e-mails e afiliações institucionais acima devem ser integralmente omitidos, mantendo apenas o título, resumo e corpo textual conforme as diretrizes do edital.

---

## RESUMO

A mobilidade humana na Amazônia Legal é condicionada por densa bacia hidrográfica, lacunas na malha rodoviária e severa sazonalidade hidrológica. Deslocamentos intermunicipais frequentemente exigem a combinação desarticulada de múltiplos modais — barcos regionais, voadeiras, balsas, ônibus e aviação regional —, submetendo passageiros a forte assimetria de informação. Este artigo propõe a especificação funcional e a modelagem do **Embarque Amazônia**, plataforma digital concebida como hub integrador multimodal de transportes para a região. A proposta fundamenta-se na caracterização de dez modais regionais, no diagnóstico da escassez de APIs públicas abertas no setor fluvial e na proposição de uma arquitetura relacional orientada a grafos ponderados de conexão intermodal. São apresentadas diretrizes de experiência de usuário (UX) estruturadas em fluxo mobile para passageiros — com ênfase em tolerância a falhas e consulta offline — e fluxo desktop para alimentação cadastral descentralizada por operadores locais. A iniciativa busca preencher uma lacuna na infraestrutura digital amazônica, fornecendo bases de engenharia de software para o planejamento eficiente de itinerários.

**Palavras-chave:** Hub Multimodal; Amazônia Legal; Navegação Interior; Engenharia de Requisitos; Prototipação de Software.

---

## ABSTRACT

Human mobility in the Brazilian Legal Amazon is constrained by an extensive hydrographic network, critical gaps in road infrastructure, and severe hydrological seasonality. Regional transit often mandates the fragmented chaining of disparate travel modes — including traditional riverboats, fast motorboats, roll-on/roll-off ferries, intercity coaches, and regional aviation — imposing significant informational asymmetry on passengers. This paper proposes the functional specification and conceptual modeling of **Embarque Amazônia**, a digital multimodal transit hub platform designed for the region. The proposal is grounded in the operational profiling of ten regional transit modes, an audit revealing the lack of public application programming interfaces (APIs) across the riverine sector, and a relational data architecture tailored for weighted intermodal graph routing. We detail user experience (UX) guidelines structured across a mobile interface for travelers — prioritizing offline resilience — and a desktop portal for municipal operators and transport cooperatives. This work addresses a persistent deficit in Amazonian digital infrastructure, establishing software engineering foundations to optimize route planning.

**Keywords:** Multimodal Transit; Amazon Basin; Inland Navigation; Requirements Engineering; Software Prototyping.

---

## 1. INTRODUÇÃO

A Região Amazônica brasileira abrange mais de cinco milhões de quilômetros quadrados e abriga cerca de trinta milhões de habitantes. Ao contrário das regiões Sul e Sudeste, cuja conectividade logística baseia-se fundamentalmente em malhas rodoviárias integradas, o transporte na Amazônia Legal tem a hidrografia como eixo estruturante de circulação de pessoas e mercadorias (IPEA, 2021; CNT, 2024). Centenas de municípios dependem prioritariamente de hidrovias navegáveis — como as calhas dos rios Amazonas, Solimões, Tapajós e Madeira — para acesso a serviços essenciais de saúde, educação e comércio.

Nesse contexto, o deslocamento raramente se concretiza por meio de um modal único. Uma viagem típica entre o interior e um centro urbano exige cadeias intermodais: o usuário parte de uma comunidade em embarcação vicinal de pequeno porte (*voadeira*), realiza baldeação em porto fluvial para barco regional de linha (*gaiola*) com acomodação em rede, efetua conexão terrestre — por moto-táxi ou ônibus coletivo — e, eventualmente, embarca em voo regular ou regional (ANTAQ, 2026; ANAC, 2024).

Contudo, essa mobilidade enfrenta gargalos crônicos decorrentes da assimetria informacional:
1. **Inexistência de roteamento integrado:** Não há plataformas que agreguem sob o mesmo modelo de itinerário o transporte fluvial tradicional, rodoviário e aéreo, impondo planejamento empírico aos viajantes.
2. **Severa sazonalidade hidrológica:** No período de estiagem (agosto a novembro), o surgimento de bancos de areia e o rebaixamento de calado ampliam os tempos de percurso fluvial, sem mecanismos digitais centralizados que alertem sobre tais variações.
3. **Escassez de dados abertos e APIs:** Enquanto a aviação comercial disponibiliza interfaces estruturadas, o transporte fluvial opera sob bilhetagem física nos cais, carecendo de APIs públicas abertas de horários e tarifas.
4. **Desafios de conectividade:** A ausência de sinal móvel (3G/4G) ao longo de vastos trechos dos rios demanda soluções com suporte nativo ao funcionamento *offline-first*.

Diante desse cenário, este trabalho propõe o projeto e a especificação de software do **Embarque Amazônia**, um hub multimodal adaptado à Amazônia Legal. O objetivo central consiste em modelar trajetos heterogêneos, consolidar dados de operadores e cooperativas via painel cadastral e calcular itinerários otimizados sob múltiplos critérios — menor custo, menor tempo e mais confiável (mensurado pela recência dos dados).

O artigo desenvolve uma abordagem metodológica tripartite: caracteriza dez modais regionais e audita APIs de transporte; propõe uma arquitetura de dados relacional normalizada com suporte a relações N:N entre operadores e modais; e detalha o projeto de interface de dezesseis telas navegáveis voltadas à usabilidade regional e operação offline. O restante do texto estrutura-se em: Metodologia e Modais (§2), APIs e Modelo de Dados (§3), Projeto de Interface (§4), Implementação do Motor (§5), Testes e Resultados (§6) e Considerações Finais (§7).

---

## REFERÊNCIAS

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 121:** Requisitos operacionais: operações domésticas, de bandeira e suplementares. Brasília, DF: ANAC, 2023.

AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). **Regulamento Brasileiro da Aviação Civil – RBAC nº 135:** Requisitos operacionais: operações de transporte aéreo público sob demanda e regular não agendado. Brasília, DF: ANAC, 2024.

AGÊNCIA NACIONAL DE TRANSPORTES AQUAVIÁRIOS (ANTAQ). **Resoluções nº 136 a 141 de 19 de agosto de 2026:** Regulamentam a prestação de serviços de navegação interior longitudinal de passageiros. Brasília, DF: ANTAQ, 2026.

AGÊNCIA NACIONAL DE TRANSPORTES TERRESTRES (ANTT). **Resolução nº 6.033, de 14 de dezembro de 2023:** Marco Regulatório do Transporte Rodoviário Coletivo Interestadual de Passageiros. Brasília, DF: ANTT, 2023.

CONFEDERAÇÃO NACIONAL DO TRANSPORTE (CNT). **Pesquisa CNT de Navegação Interior 2024:** Panorama hidroviário e transporte de passageiros na Região Norte. Brasília, DF: CNT, 2024.

INSTITUTO DE PESQUISA ECONÔMICA APLICADA (IPEA). **Transporte Fluvial de Passageiros na Amazônia: Desafios de Regulação, Infraestrutura e Acessibilidade Regional.** Brasília, DF: IPEA, 2021.

---

## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL GENERATIVA
*Conforme Resolução nº 001/2026 do Colegiado de Ciência da Computação do CESUPA.*

* **Ferramenta Utilizada:** Antigravity AI / Large Language Model (2026).
* **Finalidade e Escopo de Aplicação:** Apoio à síntese de requisitos, geração inicial de esqueletos de código e documentação (OpenAPI e SQL), elaboração de casos de teste automatizados e suporte à revisão ortográfica e adequação ABNT.
* **Autoria e Validação Discente:** A concepção do escopo, modelagem do domínio amazônico, levantamento factual de modais, correção manual dos algoritmos de busca e validação integral dos testes foram de responsabilidade exclusiva dos discentes autores.
