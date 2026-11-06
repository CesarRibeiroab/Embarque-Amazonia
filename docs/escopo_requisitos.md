# EMBARQUE AMAZÔNIA — PROJETO INTEGRADO II
## Módulo 1: Escopo, Glossário, Dados de Exemplo e Kit de Estilo
**Responsável:** César Augusto Borges Ribeiro (Coordenação Geral)  
**Card Trello de Referência:** [https://trello.com/c/SO834QEo](https://trello.com/c/SO834QEo)  
**Status:** Fechado e Padronizado para o Time (César, Fernando, Hebert, Lucas)  
**Data:** 28/10/2026  

---

### 1. DECLARAÇÃO DE ESCOPO DO PROJETO

#### 1.1 Objetivo do Produto (Entrega Parcial)
Projetar a experiência de usuário e a especificação funcional de um **Hub Digital Multimodal de Transportes para a Amazônia Legal**, integrando modais fluviais (barcos regionais, voadeiras, lanchas rápidas e balsas), rodoviários (ônibus interestaduais e intermunicipais) e aéreos (aviação regular e regional). 

Nesta etapa parcial, o escopo compreende:
1. **Artigo Acadêmico:** Estruturação formal de Título, Resumo/Abstract (Fernando) e Introdução/Proposta (César), além de Referências normatizadas.
2. **Prototipação de Telas de Alta/Média Fidelidade no Figma:** 16 telas navegáveis divididas entre fluxo do passageiro (mobile 360×800) e fluxo administrativo/cadastro (desktop 1440×1024).

#### 1.2 Limites de Escopo (O que NÃO faz parte desta entrega)
- Não contempla implementação de código back-end ou front-end em produção.
- Não contempla transações financeiras reais ou gateway de pagamento integrado (o sistema nesta fase atua como planejador, agregador e roteador informativo).
- Não serão feitas medições de desempenho de software finalizado, mantendo todo o discurso do artigo e das apresentações em tom de **proposta e especificação de engenharia de requisitos**.

---

### 2. GLOSSÁRIO TÉCNICO E REGIONAL PADRONIZADO

Para assegurar consistência semântica entre o artigo, as telas do Figma e o modelo de dados:

| Termo | Definição Padronizada | Exemplo de Aplicação |
|---|---|---|
| **Trecho (Leg)** | Segmento indivisível de deslocamento entre dois pontos físicos consecutivos, operado por um modal específico e um operador definido. | *Porto de Belém → Terminal Hidroviário de Soure* (Fluvial, Balsa). |
| **Rota Multimodal** | Cadeia composta por dois ou mais trechos concatenados, frequentemente de modais distintos, que conecta a origem ao destino final do viajante. | *Comunidade Rio Preto → Voadeira → Óbidos → Barco Regional → Santarém → Voo Azul → Belém*. |
| **Ponto de Transbordo** | Local físico e infraestrutura onde o usuário encerra um trecho em determinado modal e se desloca para iniciar o próximo (conexão intermodal). | *Desembarque no Porto de Santarém e deslocamento para o Terminal Rodoviário*. |
| **Tempo de Conexão** | Intervalo mínimo necessário de espera entre o horário estimado de chegada de um trecho e o horário de partida do trecho subsequente. | *120 minutos entre a atracação da balsa e a decolagem no aeroporto regional*. |
| **Barco Regional ("Gaiola")** | Embarcação de madeira ou aço com dois a três conveses, operando linhas fluviais regulares longitudinais com acomodação em rede e camarotes. | *Viagem Manaus–Santarém–Belém*. |
| **Voadeira / "Ajato"** | Lancha rápida de alumínio ou fibra, com motor de popa potente, utilizada para transporte vicinal rápido e táxi fluvial entre comunidades e sedes. | *Trecho Breves → Furo do Tajapuru*. |
| **Ferry-Boat / Ro-Ro** | Embarcação de grande calado projetada para transporte conjunto de veículos (Roll-on/Roll-off), carga pesada e passageiros. | *Linha Belém–Camará (Ilha do Marajó)*. |
| **Acomodação em Rede** | Regime de viagem fluvial onde o passageiro arma seu próprio leito de descanso no convés coletivo da embarcação. | *Opção econômica tradicional em viagens fluviais*. |
| **Camarote / Suíte** | Cabine fechada privativa dotada de leitos (beliches), tranca e, em geral, climatização por ar-condicionado. | *Acomodação privativa com custo substancialmente superior*. |
| **Sazonalidade Hidrológica** | Regime periódico de variação do nível das águas (Cheia / Inverno Amazônico vs. Vazante / Seca), que determina calado, acessibilidade e duração das viagens. | *Na vazante extrema de setembro a novembro, trechos no Solimões aumentam a duração em até 35%*. |
| **Sob Demanda** | Serviços que não possuem grade horária diária predeterminada, partindo mediante lotação mínima ou fretamento contratado. | *Voadeiras comunitárias e táxis fluviais*. |

---

### 3. CONJUNTO DE DADOS DE EXEMPLO (CONFERIDOS)

Todos os integrantes (Hebert, Lucas e Fernando) **devem utilizar estritamente estes dados** nos protótipos para garantir que os valores, durações e somas coincidam perfeitamente entre P04 (Resultados), P05 (Comparar), P06 (Detalhes), P09 (Salvas) e A02 (Painel).

#### Rota A: Origem: Breves (Marajó/PA) → Destino: Belém (PA)
- **Opção 1 — Mais Rápida (Multimodal: Lancha + Rodoviário via Camará):**
  - Trecho 1: Lancha rápida *Expresso Marajó* (Breves → Camará). Duração: 2h 45min. Tarifa: R$ 85,00.
  - Conexão: Transbordo no Terminal Fluvial de Camará. Tempo de conexão: 35 min.
  - Trecho 2: Ferry-Boat *Henvil Transportes* (Camará → Terminal Icoaraci/Belém). Duração: 2h 30min. Tarifa: R$ 45,00.
  - Trecho 3: Ônibus urbano/Integração (Icoaraci → Centro de Belém). Duração: 50 min. Tarifa: R$ 5,00.
  - **Totais:** Duração Total: **6h 40min** | Custo Total: **R$ 135,00** | Transbordos: 2 | Modais: 3.
- **Opção 2 — Econômica Direta (Barco Regional de Linha):**
  - Trecho Único: Barco *Amazon Star* (Porto de Breves → Terminal Hidroviário de Belém).
  - Acomodação: Rede.
  - **Totais:** Duração Total: **12h 00min** | Custo Total: **R$ 70,00** | Transbordos: 0 | Modais: 1.

#### Rota B: Origem: Santarém (PA) → Destino: Manaus (AM)
- **Opção 1 — Econômica Fluvial (Barco Regional de Linha):**
  - Trecho Único: N/M *Santarém Star* (Porto de Santarém → Porto de Manaus Moderna).
  - Acomodação Rede: R$ 220,00 | Acomodação Camarote Duplo: R$ 980,00.
  - Duração: **34h 00min** (subindo o Rio Amazonas).
  - Alerta de Sazonalidade: *Aviso de Vazante: tempo de viagem sujeito a variação de +4h devido a bancos de areia*.
- **Opção 2 — Voo Comercial Direto:**
  - Trecho Único: Voo *Azul Conecta / Azul Linhas Aéreas* (STM → MAO).
  - Duração de Voo: **1h 15min** | Custo: **R$ 540,00** (tarifa básica com bagagem de mão).
  - Transbordos: 0.

#### Rota C: Origem: Comunidade Arapixuna → Destino: Óbidos (PA)
- **Trecho Único (Transporte Ribeirinho Vicinal):**
  - Operador: Associação de Pilotos Fluviais de Arapixuna.
  - Modal: Voadeira / Bote a motor (sob demanda / saídas às 06:30 e 13:00).
  - Duração: **45min** | Custo: **R$ 25,00** (pagamento em dinheiro ou Pix).
  - Status: *Sem conectividade de dados durante a travessia (armazenamento offline necessário)*.

---

### 4. KIT DE ESTILO CONSOLIDADO (DESIGN SYSTEM FOUNDATIONS)

Para garantir identidade visual coesa entre os 4 membros da equipe antes mesmo da publicação dos componentes compartilhados por Hebert no Marco 2:

#### 4.1 Paleta de Cores (WCAG AA Compliant)
- **Cor Primária (Identidade Amazônica / Rios):** `#005F73` (Azul Petróleo / Rio Profundo)
  - Uso: Barras de navegação, cabeçalhos, botões primários de ação (Buscar, Confirmar).
- **Cor Secundária (Terra / Floresta):** `#0A9396` (Ciano Amazônico / Águas Claras)
  - Uso: Destaques de filtros ativos, tags de modais fluviais, ícones selecionados.
- **Cor de Acento (Atenção / Alerta Sazonal):** `#EE9B00` (Âmbar Amazônico)
  - Uso: Alertas de seca/cheia, avisos de atraso, selo de conexão curta (<45 min).
- **Cor de Destaque / Alerta Crítico:** `#AE2012` (Vermelho Queimado)
  - Uso: Trecho intrafegável, cancelamento de saída, erro de formulário.
- **Cores Neutras e Fundo:**
  - Superfície Principal (Background): `#F8F9FA` (Cinza Gelo Quase Branco).
  - Superfície de Cartões (Cards): `#FFFFFF` (Branco Puro com sombra suave `0px 2px 8px rgba(0,0,0,0.06)`).
  - Texto Principal (High Contrast): `#1D2D44` (Azul Escuro Grafite).
  - Texto Secundário (Metadados/Legendas): `#6C757D` (Cinza Médio).
  - Bordas e Divisores: `#E9ECEF`.

#### 4.2 Tipografia (Compatibilidade com Template de Artigo e UI)
- **Títulos e Cabeçalhos:** *Calibri Light* ou *Segoe UI Semibold* (Mobile: 18px–22px | Desktop: 24px–32px).
- **Corpo de Texto e Parágrafos:** *Calibri* ou *Segoe UI Regular* (Mobile: 14px–16px | Desktop: 14px–16px).
- **Metadados, Badges e Preços:** *Segoe UI Medium/Bold* ou *Calibri Bold* (12px para badges, 18px bold para preços).

#### 4.3 Elementos e Badges de Modais
- Cada modal deve exibir um ícone e etiqueta com cor padronizada:
  - 🚢 **Fluvial (Barco/Balsa):** Fundo `#E0F2F1`, Texto `#00695C`.
  - 🚤 **Voadeira / Rápido:** Fundo `#E1F5FE`, Texto `#0277BD`.
  - 🚌 **Rodoviário (Ônibus):** Fundo `#FFF3E0`, Texto `#E65100`.
  - ✈️ **Aéreo (Avião/Táxi Aéreo):** Fundo `#EDE7F6`, Texto `#4527A0`.
  - 🏍️ **Moto-Táxi / Transfer:** Fundo `#FBE9E7`, Texto `#D84315`.

#### 4.4 Dimensões Oficiais dos Frames no Figma
- **Interface Passageiro (Hebert e Lucas):** Mobile Android padrão `360 × 800 px`.
- **Interface Cadastro/Admin (Fernando):** Desktop padrão `1440 × 1024 px`.

