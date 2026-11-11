# EMBARQUE AMAZÔNIA — PROJETO INTEGRADO II
## Módulo 1: Escopo, Glossário, Dados de Exemplo e Kit de Estilo
**Responsável:** César Augusto Borges Ribeiro (Coordenação Geral)  
**Status:** Alinhado com a Base Executável (`seed.sql`) e API FastAPI  
**Data:** 11/11/2026  

---

### 1. DECLARAÇÃO DE ESCOPO DO PROJETO

#### 1.1 Objetivo do Produto
Projetar a arquitetura, o modelo de dados, o motor de roteamento e a interface do **Embarque Amazônia**, um hub digital multimodal de transportes para a Amazônia Legal, integrando os **10 modais canônicos** do projeto:
* **Fluvial:** Barco regional, Voadeira, Balsa pequena, Balsa grande
* **Rodoviário:** Carro, Ônibus, Moto-táxi
* **Aéreo:** Avião regional, Táxi aéreo, Helicóptero

O escopo compreende:
1. **Artigo Acadêmico:** Título, Resumo/Abstract, Introdução (Seção 1), Referências e Declaração de IA em [`docs/artigo.md`](artigo.md), com Seções 2 a 6 planejadas na etapa final.
2. **Protótipo e Implementação:** Protótipo das 16 telas no Figma (passageiro `360 × 800 px` e administrativo `1440 × 1024 px`), além da fundação técnica em código: banco relacional (`database/`), motor em grafo e API REST (`api/`), contrato OpenAPI (`docs/openapi.yaml`) e esqueleto inicial de busca web (`web/`).

#### 1.2 O que NÃO faz parte do MVP
- Reserva/venda de passagens ou integração com gateway de pagamento.
- Alertas dinâmicos em tempo real de cheias, vazantes ou cancelamentos.
- Bot de WhatsApp.
- Login ou conta de passageiro.
- Ponto de transbordo como entidade cadastral autônoma (a conexão é tratada pelo intervalo de tempo entre trechos).
- Fator numérico rígido multiplicador de seca (o regime hídrico é exibido como observação textual informativa).

---

### 2. GLOSSÁRIO TÉCNICO E REGIONAL PADRONIZADO

| Termo | Definição Padronizada | Exemplo de Aplicação |
|---|---|---|
| **Trecho (Leg)** | Segmento indivisível de deslocamento entre duas localidades consecutivas, operado por um modal e operador definidos. | *Aeroporto de Belém → Aeroporto de Santarém* (Avião regional). |
| **Rota Multimodal** | Cadeia composta por até 3 trechos conectados (podendo combinar modais distintos) entre origem e destino. | *Belém → Avião (Santarém) → Barco regional → Manaus*. |
| **Conexão / Transbordo** | Intervalo temporal entre a chegada de um trecho e a partida do subsequente (descartado se a partida for anterior à chegada). | *280 minutos em Santarém (chegada 09:20, partida do barco 14:00)*. |
| **Barco regional ("Gaiola")** | Embarcação longitudinal de madeira ou aço para transporte regular de passageiros em redes e camarotes. | *Linha Belém–Manaus*. |
| **Voadeira** | Lancha rápida com motor de popa utilizada em deslocamentos médios e vicinais. | *Trecho expresso Manaus–Tefé*. |
| **Balsa pequena / Balsa grande** | Embarcações para travessias locais ou transporte Ro-Ro de grande porte. | *Travessias regionais e veículos*. |
| **Acomodação (Rede / Camarote)** | Modalidade de hospedagem a bordo em viagens fluviais (rede em convés coletivo ou cabine privativa). | *Rede R$ 350,00 vs. Camarote duplo R$ 1.400,00*. |
| **Recência / Confiabilidade** | Métrica baseada nos dias decorridos desde `data_ultima_atualizacao`; acima de 30 dias recebe selo **Desatualizado**. | *Santarém/Tefé/Belém → Manaus com selo "Mais confiável" ou "Desatualizado"*. |

---

### 3. DADOS DE EXEMPLO CANÔNICOS (ILUSTRATIVOS — `database/seed.sql`)

> [!NOTE]
> Os valores abaixo são **dados de exemplo ilustrativos** para testes e demonstração (não são tarifas oficiais ou homologadas). São os mesmos dados populados por `database/seed.sql`.

* **Rota 1 — Belém → Manaus (data de viagem ilustrativa: sexta-feira `2026-11-20`):**
  * **Opção A (Barco regional — Amazon Star):** `8400 min` (`5 d 20 h`), `R$ 350,00`, saída quarta/sexta às 18:00, atualizado há 3 dias. *(Selo: Menor custo)*
  * **Opção B (Avião regional — Azul):** `135 min` (`2 h 15 min`), `R$ 780,00`, diário às 09:30, atualizado hoje. *(Selos: Menor tempo, Mais confiável)*
  * **Opção C (Combinada — Azul + Amazon Star via Santarém):** voo Belém → Santarém (`80 min`, chegada 09:20, `R$ 540,00`) + conexão de `280 min` + barco Santarém → Manaus (`2520 min`, partida 14:00, `R$ 210,00`). Total: **`2880 min` (`2 d`)**, **`R$ 750,00`**, `1` conexão, atualizado há 12 dias.
* **Rota 2 — Manaus → Tefé:**
  * **Voadeira (Piloto autônomo):** `660 min` (`11 h`), `R$ 320,00`, atualizado há 20 dias. *(Selo comparativo: Menor tempo)*
  * **Barco regional (Oliveira Navegações):** `2160 min` (`1 d 12 h`), `R$ 190,00`, atualizado há 5 dias. *(Selos comparativos: Menor custo, Mais confiável)*
* **Rota 3 — Cametá → Alenquer (Caso de borda sem rotas):**
  * Ambas as localidades existem no banco, mas não há caminho no grafo -> retorna `HTTP 200` com `total_opcoes: 0` e `rotas: []`.
* **Trechos de retorno e verificação no seed:**
  * **Voltas:** Manaus → Belém (avião `135 min` R$ 780,00; barco `5760 min` / `4 d` R$ 350,00) e Tefé → Manaus (voadeira `660 min` R$ 320,00; barco `2160 min` R$ 190,00).
  * **Opção única desatualizada:** Parintins → Manaus (`1080 min` / `18 h`, R$ 120,00, atualizado há 45 dias -> recebe apenas o selo `Desatualizado`, sem selos comparativos).
  * **Opção única atualizada:** Santarém → Manaus (`rota-t4`, `2520 min` / `1 d 18 h`, R$ 210,00 -> sem selos comparativos).

---

### 4. KIT DE ESTILO OFICIAL (DESIGN SYSTEM)

Aplicado no front-end `web/` e especificação dos protótipos:

* **Tipografia:** Fonte `Inter`.
* **Paleta Base e Estados:**
  * Primária: `#1B5E3F`
  * Secundária: `#1F6FB2`
  * Texto principal: `#1A1A1A`
  * Texto secundário: `#6B7280`
  * Borda: `#D1D5DB`
  * Fundo: `#F7F8F7`
  * Sucesso: `#2E7D32`
  * Alerta: `#F2A900`
  * Erro: `#C62828`
* **Categorias de Modal:**
  * Fluvial: `#1F6FB2`
  * Rodoviário: `#D9822B`
  * Aéreo: `#6A4C93`
* **Selos de Classificação:**
  * `Menor custo`: `#2E7D32` (texto claro `#FFFFFF`)
  * `Menor tempo`: `#1F6FB2` (texto claro `#FFFFFF`)
  * `Mais confiável`: `#00796B` (texto claro `#FFFFFF`)
  * `Desatualizado`: `#F2A900` (com **texto escuro** `#1A1A1A`)
* **Resoluções dos Frames:**
  * Mobile (Passageiro): `360 px` de largura (`360 × 800 px` no Figma).
  * Desktop (Administrativo): `1440 × 1024 px` no Figma.
