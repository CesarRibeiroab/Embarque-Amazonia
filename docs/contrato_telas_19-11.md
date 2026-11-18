# CONTRATO DE DADOS E NAVEGAÇÃO DE TELAS — ENTREGA 19/11/2026
**Embarque Amazônia — Projeto Integrado II (CESUPA)**  
*Publicado por: César Augusto Borges Ribeiro (Coordenação / API / Motor / P06)*  
*Público-alvo: Todos os integrantes (César, Fernando, Herbert, Lucas)*

---

## 1. Princípio de Trabalho: Ninguém Espera Ninguém

Este documento estabelece o **contrato único e estável** entre a API e as interfaces web para a entrega de 19/11/2026. Todas as definições foram projetadas para garantir **independência total de desenvolvimento**:

1. **Campos 100% aditivos:** Nenhum campo existente em `GET /api/v1/rotas` foi removido ou renomeado.
2. **Resiliência a enriquecimento:** A API lê apenas colunas já existentes no banco (`operador.telefone_contato`, `acomodacao_trecho`, `horario_operacao.frequencia_descricao`, `trecho.regime_hidrico_observacao`, `modal.categoria`). Quando o Fernando enriquecer o `seed.sql`, nada quebra.
3. **Desacoplamento de Telas:** Cada componente de tela (`TelaDetalheRota`, `TelaFiltros`, `TelaComparar`, `TelaDetalheTrecho`) possui fallback interno e funciona isoladamente mesmo se a API estiver offline ou se outra tela não tiver sido entregue.
4. **Alinhamento do Exemplo Canônico:** O card do Trello mencionava "07:50 -> 12:30" para a conexão em Santarém; o valor oficial e verificado do banco/seed é **`09:20 → 14:00` (espera de 4 h 40 min = 280 min)**. Todos devem adotar essa referência.

---

## 2. Contrato de Dados da API REST

Os campos novos valem tanto para `GET /api/v1/rotas` quanto para `GET /api/v1/rotas/{id}`.

### 2.1 Em cada trecho (`TrechoResponse`)

| Campo | Tipo | Nullable | Significado / Formato |
|---|---|:---:|---|
| `modal_codigo` | `string` | Não | ex.: `"aviao_regional"`, `"barco_regional"`, `"voadeira"` |
| `modal_categoria` | `string` | Não | `"fluvial"`, `"rodoviario"` ou `"aereo"` (define a cor visual no P06) |
| `hora_partida` | `string` | Sim | `"HH:MM"` (ex.: `"08:00"`); `null` se o trecho não possui horário |
| `hora_chegada_estimada` | `string` | Sim | `"HH:MM"` (ex.: `"09:20"`); `null` se não possui horário |
| `partida_dia_offset` | `integer` | Sim | Dias decorridos desde a partida da rota (0 = mesmo dia da partida da rota) |
| `chegada_dia_offset` | `integer` | Sim | Dias decorridos até a chegada neste trecho (ex.: 2 = chegada 2 dias após a partida da rota) |
| `frequencia_descricao` | `string` | Sim | Texto cadastrado no banco (ex.: `"Diário"`, `"Terças, Quintas e Sextas-feiras"`) |
| `dias_semana_mask` | `integer` | Não | Bitmask: Seg=1, Ter=2, Qua=4, Qui=8, Sex=16, Sáb=32, Dom=64 (127 se não há restrição) |
| `acomodacoes` | `array` | Não | Lista de objetos: `[{"tipo": str, "regime": str, "valor_total_reais": float, "descricao": str}]` (vazio `[]` se não há) |
| `regime_hidrico_observacao` | `string` | Sim | Observação sazonal (ex.: `"Voo regional."`, `"Barco de linha."`) |
| `telefone_contato` | `string` | Sim | Telefone do operador (ex.: `"(91) 90000-0000"` ou `null`) |
| `intervalo_conexao_minutos` | `integer` | Sim | Minutos de espera **após** este trecho até o próximo; `null` no último trecho da rota |

### 2.2 Na rota (`OpcaoRotaResponse`)

| Campo | Tipo | Nullable | Significado / Formato |
|---|---|:---:|---|
| `data_viagem` | `string` | Sim | Data pretendida da viagem informada na consulta (`"YYYY-MM-DD"`) ou `null` |
| `hora_partida` | `string` | Sim | Horário de saída do 1º trecho (`"HH:MM"`) ou `null` |
| `chegada_estimada` | `string` | Sim | Horário de chegada do último trecho (`"HH:MM"`) ou `null` |
| `chegada_dia_offset` | `integer` | Sim | Quantidade de dias após a partida em que ocorre a chegada final |
| `chegada_estimada_iso` | `string` | Sim | `"YYYY-MM-DDTHH:MM"` (calculado **somente** quando `data_viagem` foi fornecida; sem fuso horário) |

### 2.3 Regras de Cálculo dos Horários e Offsets

Em minutos desde a meia-noite (00:00) do dia da partida da rota (`dia 0`):
- `partida_minutos[0]` = horário de saída do primeiro trecho.
- `chegada_minutos[i]` = `partida_minutos[i] + duracao_minutos[i]`.
- `partida_minutos[i+1]` = `chegada_minutos[i] + intervalo_conexao_minutos[i]`.
- Para cada trecho:
  - `hora = (minutos % 1440)` formatado como `HH:MM`.
  - `dia_offset = minutos // 1440`.
- **Intervalo de Conexão (`intervalo_conexao_minutos`):** Quando ambos os trechos possuem horário no mesmo dia e `hora_partida[i+1] >= hora_chegada[i]`, o intervalo é `hora_partida[i+1] - hora_chegada[i]`. Caso contrário, utiliza `tempo_conexao_espera_minutos` do trecho. Se `hora_partida[i+1] < hora_chegada[i]`, a conexão no mesmo dia é inválida/descartada.

### 2.4 Valores Canônicos Verificados (Belém → Manaus, 20/11/2026 - Sexta-feira)

| Rota | Preço | Duração | Selos | Trechos e Conexão |
|---|---|---|---|---|
| `rota-t2` | R$ 780,00 | 2 h 15 min (135 min) | Menor tempo, Mais confiável | t2 (Avião): 09:30 → 11:45, dia +0 |
| `rota-t3-t4` | R$ 750,00 | 2 d (2880 min) | *(nenhum)* | t3 (Avião): 08:00 → 09:20 (offset 0), **intervalo 280 min**;<br>t4 (Barco): 14:00 → **08:00 (offset +2)** |
| `rota-t1` | R$ 350,00 | 5 d 20 h (8400 min) | Menor custo | t1 (Barco): 18:00 → **14:00 (offset +6)** |

#### Exemplo JSON Canônico de `GET /api/v1/rotas/rota-t3-t4?data=2026-11-20`
```json
{
  "id": "rota-t3-t4",
  "origem_nome": "Belém",
  "destino_nome": "Manaus",
  "modais": ["Avião regional", "Barco regional"],
  "preco_total": 750.0,
  "duracao_total_minutos": 2880,
  "duracao_total_formatada": "2 d",
  "numero_trechos": 2,
  "numero_conexoes": 1,
  "selo": [],
  "dias_desde_atualizacao": 12,
  "data_atualizacao_iso": "2026-10-30",
  "data_viagem": "2026-11-20",
  "hora_partida": "08:00",
  "chegada_estimada": "08:00",
  "chegada_dia_offset": 2,
  "chegada_estimada_iso": "2026-11-22T08:00",
  "trechos": [
    {
      "id": 3,
      "origem_nome": "Belém",
      "destino_nome": "Santarém",
      "modal_nome": "Avião regional",
      "modal_codigo": "aviao_regional",
      "modal_categoria": "aereo",
      "operador_nome": "Azul",
      "terminal_origem_nome": "Aeroporto de Belém",
      "terminal_destino_nome": "Aeroporto de Santarém",
      "duracao_minutos": 80,
      "tarifa_reais": 540.0,
      "data_ultima_atualizacao": "2026-10-30",
      "hora_partida": "08:00",
      "hora_chegada_estimada": "09:20",
      "partida_dia_offset": 0,
      "chegada_dia_offset": 0,
      "frequencia_descricao": "Diário",
      "dias_semana_mask": 127,
      "acomodacoes": [],
      "regime_hidrico_observacao": "Voo regional.",
      "telefone_contato": null,
      "intervalo_conexao_minutos": 280
    },
    {
      "id": 4,
      "origem_nome": "Santarém",
      "destino_nome": "Manaus",
      "modal_nome": "Barco regional",
      "modal_codigo": "barco_regional",
      "modal_categoria": "fluvial",
      "operador_nome": "Amazon Star",
      "terminal_origem_nome": "Porto de Santarém",
      "terminal_destino_nome": "Porto da Manaus Moderna",
      "duracao_minutos": 2520,
      "tarifa_reais": 210.0,
      "data_ultima_atualizacao": "2026-10-30",
      "hora_partida": "14:00",
      "hora_chegada_estimada": "08:00",
      "partida_dia_offset": 0,
      "chegada_dia_offset": 2,
      "frequencia_descricao": "Terças, Quintas e Sextas-feiras",
      "dias_semana_mask": 26,
      "acomodacoes": [
        {
          "tipo": "rede",
          "regime": "fixo",
          "valor_total_reais": 210.0,
          "descricao": "Acomodação em rede"
        }
      ],
      "regime_hidrico_observacao": "Barco de linha.",
      "telefone_contato": null,
      "intervalo_conexao_minutos": null
    }
  ]
}
```

---

## 3. Especificação do Endpoint `GET /api/v1/rotas/{id}`

- **Caminho:** `/api/v1/rotas/{id}`
- **Parâmetros:**
  - `id` (path, string obrigatória): identificador determinístico no padrão `^rota-t\d+(-t\d+){0,2}$`.
  - `data` (query, string opcional): data pretendida no formato ISO (`YYYY-MM-DD`).
- **Respostas:**
  - `200 OK`: objeto `OpcaoRotaResponse`. Os selos comparativos (`Menor tempo`, `Menor custo`, `Mais confiável`) são calculados com base nas opções alternativas entre a mesma origem e destino na data informada, preservando paridade estrita com a listagem.
  - `404 Not Found` (`ErroPadrao`, código `ROTA_NAO_ENCONTRADA`): trecho inexistente; trechos que não se conectam (destino de um ≠ origem do próximo); ciclo/localidade repetida; conexão temporal inválida; ou trecho que não opera no dia da semana da data consultada ("A rota não opera na data informada.").
  - `422 Unprocessable Entity` (`ErroPadrao`, código `PARAMETRO_INVALIDO`): id fora do padrão `^rota-t\d+(-t\d+){0,2}$`, ou parâmetro `data` inválido.
  - `503 Service Unavailable` (`ErroPadrao`, código `BANCO_INDISPONIVEL`): base SQLite ausente.

---

## 4. Contrato de Navegação entre Telas (Front-End)

O roteamento é realizado via hash no navegador (`window.location.hash`), sem necessidade de bibliotecas externas.

### 4.1 Rotas por Hash

| Rota | Tela Correspondente | Parâmetros / Finalidade |
|---|---|---|
| `#/` | Busca e Resultados (`App.jsx`) | Tela principal de busca do passageiro |
| `#/filtros` | `TelaFiltros.jsx` (P03) | Customização de critérios e modais |
| `#/comparar` | `TelaComparar.jsx` (P05) | Comparação lado a lado de 2 a 3 rotas selecionadas |
| `#/rota/<id>?data=YYYY-MM-DD` | `TelaDetalheRota.jsx` (P06) | Detalhe completo da rota e linha do tempo intermodal |
| `#/trecho/<id>` | `TelaDetalheTrecho.jsx` (P07) | Detalhe isolado de um trecho (operador, acomodações) |
| `#/lab/p06` | `TelaDetalheRota.jsx` (P06) | Laboratório/teste isolado do P06 com fixture local (sem API) |

### 4.2 Props Recebidas por Cada Componente

| Componente | Responsável | Props Injetadas pelo `Navegacao.jsx` | Fallback Obrigatório |
|---|---|---|---|
| `App.jsx` (Busca) | Herbert | `onAbrirRota(rota, dataViagem)` *(opcional)* | Funciona normalmente se prop não for passada |
| `TelaFiltros.jsx` (P03) | Herbert | `filtros`, `onAplicar(filtros)`, `onFechar()` | Usa filtros padrão locais |
| `TelaComparar.jsx` (P05) | Lucas | `rotas`, `dataViagem`, `onVerDetalhes(rota)`, `onVoltar()` | Usa fixtures de comparação locais |
| `TelaDetalheRota.jsx` (P06) | César | `rota`, `dataViagem`, `onVoltar()`, `onAbrirTrecho(trecho, rota)` | Se `rota` vier sem horários, consulta `GET /rotas/{id}`; se offline, usa `rota1OpcaoC` fixture com selo de exemplo |
| `TelaDetalheTrecho.jsx` (P07) | Fernando | `trecho`, `rota`, `dataViagem`, `onVoltar()` | Exibe dados do trecho ou fixture local |

---

## 5. Resumo das Decisões de Alinhamento Técnico

1. **Nomes de campo padronizados com o Trello:** Adotados `intervalo_conexao_minutos`, `hora_partida`, `hora_chegada_estimada`, `frequencia_descricao`, `dias_semana_mask`, `acomodacoes`, `regime_hidrico_observacao` e `telefone_contato`.
2. **Formato de Horários:** `HH:MM` padronizado sem segundos.
3. **Data e Chegada ISO:** `data_viagem` no formato `YYYY-MM-DD` e `chegada_estimada_iso` no formato `YYYY-MM-DDTHH:MM`, sem manipulação de fuso horário (limitação registrada no MVP).
4. **Isolamento Modular:** O componente `Navegacao.jsx` realiza lazy loading tolerante (`React.lazy` + `import.meta.glob`). Se `TelaFiltros.jsx`, `TelaComparar.jsx` ou `TelaDetalheTrecho.jsx` ainda não estiverem criados na pasta `web/src/components/`, o sistema exibe um quadro informativo avisando que a tela ainda não foi integrada, sem interromper o restante da aplicação.
