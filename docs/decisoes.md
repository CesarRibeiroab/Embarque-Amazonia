# EMBARQUE AMAZÔNIA — DECISÕES TÉCNICAS E ROTEIRO DE ORIENTAÇÃO
**Documento Executivo de Alinhamento para Reunião com o Professor**  
**Projeto Integrado II • Ciência da Computação (CESUPA)**  
**Data:** 11/11/2026  
**Autores:** César Augusto Borges Ribeiro, Fernando César Mourão Fonseca, Herbert Aciolly Leão de Jesus, Lucas Barros Mutran  

---

## 1. PROPOSTAS DE DECISÃO TÉCNICA DO PRODUTO (PARA RATIFICAÇÃO COM O PROFESSOR)

> [!NOTE]
> As decisões abaixo consolidam a arquitetura adotada pela equipe na Semana 1 e os pontos abertos para ratificação com o orientador.

### Decisão 1: Stack Tecnológica Unificada (Python / FastAPI)
- **Motivação:** O núcleo do projeto é o motor algorítmico de roteamento em grafos multimodais (`api/engine/route_engine.py`). Para eliminar divergências de linguagem entre motor e servidor, adotamos **Python com FastAPI**.
- **Back-end:** Python 3.10+ (validado em 3.14.3) com FastAPI, implementando as **2 operações de consulta do passageiro** do contrato `docs/openapi.yaml` (`GET /api/v1/localidades` com autocomplete `?busca=` e `GET /api/v1/rotas` com critérios, filtro de modais e filtro de data). O CRUD administrativo e `/api/v1/rotas/{id}` ficam para a Semana 2.
- **Banco de Dados:** SQLite 3 em desenvolvimento local (recriado por `database/init_db.py` com datas relativas à execução via `date('now', 'localtime', '-N days')`), com migração prevista para PostgreSQL 15+ em homologação.
- **Front-end Web (`web/`):** React + Vite contendo atualmente uma **tela funcional inicial de busca e listagem de resultados** em layout mobile responsivo (largura de referência 360 px). As 16 telas completas (P01–P10 e A01–A06) e a camada offline em IndexedDB estão previstas para a Semana 2 (não há manifest nem service worker).
- **Estrutura do Repositório (Mono-repo):** `/api`, `/web`, `/docs`, `/database`.

### Decisão 2: Escopo do MVP e Limitações Reconhecidas
- **Dentro do MVP:**
  1. Catálogo e autocomplete de localidades atendidas (`GET /api/v1/localidades?busca=`).
  2. Motor em grafo limitado a até 3 trechos por rota, exibindo **até 5 opções ordenadas** após a ordenação.
  3. Três critérios de ordenação: **Menor tempo**, **Menor custo** e **Mais confiável** (recência em dias desde `data_ultima_atualizacao`), além de filtro por modal e data.
  4. Salvar rota e consulta offline (P09 em IndexedDB) e painel administrativo de cadastro (telas A01–A06) — planejados na etapa da Semana 2.
- **Fora do MVP:** reserva e pagamento de passagens, alertas hidrológicos em tempo real, bot de WhatsApp, login de passageiro, ponto de transbordo como entidade própria e fator numérico rígido de seca.
- **Limitações operacionais atuais (Semana 1):** validação de dia da semana aplicada pela data única de partida em todos os trechos da rota, conexões calculadas no mesmo dia sem virada de madrugada, leitura apenas do primeiro horário ativo por trecho e ausência de ajuste de fuso horário (Belém UTC-3 vs. Manaus UTC-4).

### Decisão 3: Padrões de Dados, Datas Relativas e Selos Visuais
- **Selos Padronizados:** `Menor custo` (`#2E7D32`), `Menor tempo` (`#1F6FB2`), `Mais confiável` (`#00796B`) e `Desatualizado` (`#F2A900` com texto escuro para trechos com mais de 30 dias). **Selos comparativos são atribuídos apenas quando existem 2 ou mais opções** na busca; opção única não recebe selo comparativo.
- **Data de referência e Seed Relativo:** Por padrão, o motor usa a data atual do sistema (`date.today()`), com suporte opcional à variável `DATA_REFERENCIA`. O `seed.sql` gera datas relativas à criação do banco, por isso `init_db.py` deve ser reexecutado no dia da demonstração.
- **Natureza dos Dados:** Os dados de exemplo no `seed.sql` e no contrato OpenAPI são **ilustrativos** para validação de engenharia, não representando tabelas oficiais de operadores.

### Decisão 4: Declaração Real de Uso de Inteligência Artificial Generativa
*Em cumprimento à regulamentação acadêmica do CESUPA para uso de IA Generativa:*
- **Ferramenta Utilizada:** Antigravity AI / Large Language Models e agente de execução em repositório.
- **Atuação Efetiva da Ferramenta:** A IA generativa gerou o motor de roteamento (`api/engine/route_engine.py`), o esquema SQL (`database/schema.sql` e `seed.sql`), o contrato OpenAPI (`docs/openapi.yaml`), as suítes de testes (`api/tests/`), os endpoints FastAPI (`api/main.py`) e o esqueleto inicial da busca web (`web/`), além de auxiliar na estruturação e revisão ortográfica/ABNT da Seção 1 do artigo. Um agente autônomo operou diretamente no repositório na edição de arquivos e commits Git.
- **Atuação dos Discentes:** Definição de escopo, requisitos e regras de negócio da Amazônia Legal, parametrização dos casos canônicos ilustrativos, auditoria de inconsistências entre código, banco e documentação, definição dos ajustes necessários e validação funcional das entregas no terminal.

---

## 2. ROTEIRO DE DEMONSTRAÇÃO DE 5 MINUTOS (12/11/2026)

> [!TIP]
> **Transparência desde o início:** informar logo ao abrir a fala o que **não** existe implementado nesta entrega (telas além da busca no `web/`, cadastro administrativo, login e uso offline).

```text
[0:00 - 0:45] CONTEXTO E ESCOPO HONESTO
- Apresentar a proposta multimodal e esclarecer que o protótipo das 16 telas está no Figma;
  nesta entrega da Semana 1, o repositório traz o banco, o motor em grafo, 2 das 6 operações da API
  e uma tela inicial funcional de busca e listagem em web/.

[0:45 - 1:45] TERMINAL EM CLONE LIMPO (BANCO + 32 TESTES)
- Executar `python database/init_db.py` (7 localidades, 10 modais, 11 trechos com datas relativas).
- Executar `python database/mostrar_dados.py` para inspecionar os dados no terminal.
- Executar `python api/tests/test_route_engine.py` (17 testes unitários) e
  `python api/tests/test_api.py` (15 testes de integração) = 32 testes passando.

[1:45 - 3:00] SWAGGER UI (http://localhost:8000/docs)
- Belém -> Manaus em 20/11/2026 (sexta): 3 opções com selos e conexão calculada em 280 min;
- Mesma busca no sábado 21/11/2026: apenas o voo diário (`rota-t2`);
- Volta Manaus -> Belém (`rota-t10` e `rota-t9`); Cametá -> Alenquer (HTTP 200, lista vazia);
- Caso de erro HTTP 422 padronizado em ErroPadrao (ex.: destino ausente ou origem = destino).

[3:00 - 4:00] FRONT-END MOBILE 360 px (http://localhost:5173)
- Executar busca Belém -> Manaus em 20/11/2026 mostrando autocomplete (?busca=bel),
  preços em R$, selos coloridos, recência em dias, conexões e expansão dos trechos.

[4:00 - 4:30] PRISM CLI ESTÁTICO E PLANO DA SEMANA 2
- Demonstrar mock estático (http://127.0.0.1:4010) com `Prefer: example=rota_1_belem_manaus` e
  `example=rota_2_manaus_tefe` (exemplos estáticos do contrato).
- Mostrar `docs/telas_x_api.md` como mapa de lacunas para a Semana 2 e o plano do artigo
  (Seções 2 a 6 em 19/11).
```

---

## 3. BANCO DE PERGUNTAS E RESPOSTAS (AUDITADO)

### P1: "Vocês já têm uma API conectada a um serviço real de barcos na Amazônia?"
> *"Não, professor. Até o momento não identificamos APIs públicas abertas documentadas para a bilhetagem ou horários de barcos regionais de linha, e o contato direto com operadores privados (iBarco/Navega Norte) ficou como trabalho futuro / limitação. Por isso, a arquitetura contempla o painel de cadastro descentralizado (A01–A06), previsto para a Semana 2."*

### P2: "Como o algoritmo trata a seca dos rios e atrasos?"
> *"No MVP, exibimos apenas observações textuais informativas sobre regime hídrico cadastradas no trecho. Decidimos não aplicar um fator numérico fixo de atraso sobre a duração sem base hidrológica empírica para não fabricar estimativas imprecisas."*

### P3: "Por que o Prism devolve sempre a mesma resposta quando trocamos os parâmetros?"
> *"Porque o Prism funciona como mock estático do contrato OpenAPI (`docs/openapi.yaml`), respondendo exemplos fixos selecionados pelo cabeçalho `Prefer`. Toda a lógica dinâmica em grafo está no FastAPI + `route_engine.py`."*

### P4: "Como é calculada a confiabilidade?"
> *"Pela recência em dias desde `data_ultima_atualizacao` até a data de referência. Quanto menor o número de dias, mais confiável. Se houver 2 ou mais opções, a mais recente recebe `Mais confiável`; qualquer trecho acima de 30 dias recebe o selo `Desatualizado` (mesmo isolado)."*
