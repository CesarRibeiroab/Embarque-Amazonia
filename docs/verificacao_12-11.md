# Registro de Verificação em Clone Limpo (Preparação 12/11/2026)

* **Data da verificação executada:** `11/11/2026` (20:48–20:50 BRT, commit base verificado: `58f30c0`)
* **Ambiente utilizado:** Windows (`PowerShell`), clone limpo em diretório temporário (`%TEMP%\pi2_t9_clean`)
* **Versões verificadas:**
  * **Python:** `Python 3.14.3`
  * **Node.js:** `v24.19.0`
  * **npm:** `11.17.0`

---

## 1. Instalação Limpa e Inicialização do Banco (`init_db.py`)

Comandos executados no clone limpo:
```powershell
git clone <repositorio> $env:TEMP\pi2_t9_clean
cd $env:TEMP\pi2_t9_clean
python -m venv .venv
.\.venv\Scripts\pip install -r api/requirements.txt
.\.venv\Scripts\python.exe database/init_db.py
```

Dependências instaladas no `.venv`: `fastapi-0.162.5`, `uvicorn-0.54.0`, `pydantic-2.14.3`, `httpx-0.28.1`, `pytest-9.2.0`, `pyyaml-6.0.3`, `starlette-1.10.0`.

Saída real de `python database/init_db.py`:
```text
BANCO DE DADOS RECRIADO E POPULADO COM SUCESSO!
Registros carregados da base (datas relativas à execução de hoje):
  - Localidades: 7
  - Modais (Domínio Regional): 10 (todos os 10 modais cadastrados)
  - Trechos: 11 (IDs canônicos 1-7 e retornos 9-12)

Modais cadastrados:
  [1] Barco regional (fluvial) - código: barco_regional
  [2] Voadeira (fluvial) - código: voadeira
  [3] Balsa pequena (fluvial) - código: balsa_pequena
  [4] Balsa grande (fluvial) - código: balsa_grande
  [5] Carro (rodoviario) - código: carro
  [6] Ônibus (rodoviario) - código: onibus
  [7] Moto-táxi (rodoviario) - código: moto_taxi
  [8] Avião regional (aereo) - código: aviao_regional
  [9] Táxi aéreo (aereo) - código: taxi_aereo
  [10] Helicóptero (aereo) - código: helicoptero
```

---

## 2. Inspeção Somente Leitura (`mostrar_dados.py`)

Comando:
```powershell
.\.venv\Scripts\python.exe database/mostrar_dados.py
```

Saída real:
```text
=== EMBARQUE AMAZÔNIA — DADOS DO BANCO (Referência: 2026-11-11) ===

--- LOCALIDADES (7) ---
  [1] Belém (PA) | tipo: polo_regional | IATA: BEL
  [2] Manaus (AM) | tipo: polo_regional | IATA: MAO
  [3] Santarém (PA) | tipo: polo_regional | IATA: STM
  [4] Tefé (AM) | tipo: municipio | IATA: TFF
  [5] Parintins (AM) | tipo: municipio | IATA: PIN
  [6] Cametá (PA) | tipo: municipio | IATA: -
  [7] Alenquer (PA) | tipo: municipio | IATA: -

--- TRECHOS (11) ---
  [T01] Belém -> Manaus | Barco regional (Amazon Star) | 5 d 20 h | R$ 350,00 | 18:00->14:00 | Dias: Quarta-feira, Sexta-feira | atualizado há 3 dias (2026-11-08)
  [T02] Belém -> Manaus | Avião regional (Azul) | 2 h 15 min | R$ 780,00 | 09:30->11:45 | Dias: Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo (Diário) | atualizado hoje (2026-11-11)
  [T03] Belém -> Santarém | Avião regional (Azul) | 1 h 20 min | R$ 540,00 | 08:00->09:20 | Dias: Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo (Diário) | atualizado há 12 dias (2026-10-30)
  [T04] Santarém -> Manaus | Barco regional (Amazon Star) | 1 d 18 h | R$ 210,00 | 14:00->08:00 | Dias: Terça-feira, Quinta-feira, Sexta-feira | atualizado há 12 dias (2026-10-30)
  [T05] Manaus -> Tefé | Voadeira (Piloto autônomo (cadastro colaborativo)) | 11 h | R$ 320,00 | 06:00->17:00 | Dias: Segunda-feira, Quinta-feira, Sexta-feira | atualizado há 20 dias (2026-10-22)
  [T06] Manaus -> Tefé | Barco regional (Oliveira Navegações) | 1 d 12 h | R$ 190,00 | 17:00->05:00 | Dias: Sexta-feira | atualizado há 5 dias (2026-11-06)
  [T07] Parintins -> Manaus | Barco regional (Oliveira Navegações) | 18 h | R$ 120,00 | 12:00->06:00 | Dias: Sábado | atualizado há 45 dias (2026-09-27)
  [T09] Manaus -> Belém | Barco regional (Amazon Star) | 4 d | R$ 350,00 | 18:00->18:00 | Dias: Quarta-feira, Sexta-feira | atualizado há 3 dias (2026-11-08)
  [T10] Manaus -> Belém | Avião regional (Azul) | 2 h 15 min | R$ 780,00 | 14:00->16:15 | Dias: Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo (Diário) | atualizado hoje (2026-11-11)
  [T11] Tefé -> Manaus | Voadeira (Piloto autônomo (cadastro colaborativo)) | 11 h | R$ 320,00 | 06:00->17:00 | Dias: Segunda-feira, Quinta-feira, Sexta-feira | atualizado há 20 dias (2026-10-22)
  [T12] Tefé -> Manaus | Barco regional (Oliveira Navegações) | 1 d 12 h | R$ 190,00 | 17:00->05:00 | Dias: Sexta-feira | atualizado há 5 dias (2026-11-06)

--- ACOMODAÇÕES (6) ---
  [A01] Trecho T01 (Belém -> Manaus) | tipo: rede | regime: fixo | R$ 350,00 | Acomodação tradicional em rede
  [A02] Trecho T01 (Belém -> Manaus) | tipo: camarote_duplo | regime: fixo | R$ 1.400,00 | Camarote privativo climatizado
  [A03] Trecho T04 (Santarém -> Manaus) | tipo: rede | regime: fixo | R$ 210,00 | Acomodação em rede
  [A04] Trecho T06 (Manaus -> Tefé) | tipo: rede | regime: fixo | R$ 190,00 | Passagem em rede
  [A05] Trecho T09 (Manaus -> Belém) | tipo: rede | regime: fixo | R$ 350,00 | Acomodação em rede
  [A06] Trecho T12 (Tefé -> Manaus) | tipo: rede | regime: fixo | R$ 190,00 | Acomodação em rede
```

---

## 3. Suítes de Testes Automatizados (32 testes)

### `api/tests/test_route_engine.py` (`Ran 17 tests in 0.018s — OK`)
```text
test_01_conexao_calculada_dinamicamente ... ok
test_02_conexao_impossivel_rejeitada ... ok
test_03_rota_1_tres_opcoes_e_opcao_c_combinada ... ok
test_04_rota_1_opcao_b_recebe_ambos_os_selos ... ok
test_05_rota_1_criterio_menor_custo ... ok
test_06_rota_2_manaus_tefe_valores_canonicos ... ok
test_07_rota_3_sem_resultados ... ok
test_08_trecho_desatualizado_acima_de_30_dias ... ok
test_09_filtro_por_dia_da_semana ... ok
test_10_filtro_por_modais ... ok
test_11_origem_igual_destino_devolve_lista_vazia ... ok
test_12_recarga_do_banco_idempotente ... ok
test_13_id_deterministico_baseado_em_trechos ... ok
test_14_conexao_impossivel_descartada_fim_a_fim ... ok
test_15_opcao_unica_sem_selos_comparativos ... ok
test_16_data_referencia_sistema_e_sobrescrita ... ok
test_17_limite_cinco_opcoes_apos_ordenacao ... ok

Ran 17 tests in 0.018s - OK
```

### `api/tests/test_api.py` (`Ran 15 tests in 0.141s — OK`)
> *Aviso conhecido:* `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` (emitido pelo `fastapi.testclient`, sem falha de asserção).

```text
test_01_listar_localidades_endpoint ... ok
test_02_buscar_rotas_belem_manaus ... ok
test_03_buscar_rotas_com_filtro_modais ... ok
test_04_buscar_rotas_sem_resultados_tela_p10a ... ok
test_05_localidade_inexistente_erro_padrao_404 ... ok
test_06_busca_insensivel_a_acentuacao_e_rota_retorno ... ok
test_07_validacao_origem_igual_destino_422 ... ok
test_08_validacao_criterio_invalido_422 ... ok
test_09_validacao_formato_data_invalida_422 ... ok
test_10_filtro_data_viagem_sexta_vs_sabado ... ok
test_11_campos_iso_e_id_deterministico ... ok
test_12_parametro_ausente_422_erro_padrao_e_docs_ativos ... ok
test_13_autocomplete_localidades_busca_sem_acento ... ok
test_14_opcao_unica_sem_selos_comparativos ... ok
test_15_banco_ausente_retorna_503_nos_dois_endpoints ... ok

Ran 15 tests in 0.141s - OK
```

---

## 4. Os 15 Cenários da API REST (Seção 5.1 em `uvicorn api.main:app --port 8000`)

Todos executados contra `http://127.0.0.1:8000`:

```text
Cenario 01 | HTTP 200 | total_opcoes=3 | criterio=menor_tempo | rotas=[{'id': 'rota-t2', 'preco': 780.0, 'duracao': '2 h 15 min', 'conexoes': 0, 'selos': ['Menor tempo', 'Mais confiável'], 'dias': 0}, {'id': 'rota-t3-t4', 'preco': 750.0, 'duracao': '2 d', 'conexoes': 1, 'selos': [], 'dias': 12}, {'id': 'rota-t1', 'preco': 350.0, 'duracao': '5 d 20 h', 'conexoes': 0, 'selos': ['Menor custo'], 'dias': 3}]
Cenario 02 | HTTP 200 | total_opcoes=3 | criterio=menor_custo | rotas=[{'id': 'rota-t1', 'preco': 350.0, 'duracao': '5 d 20 h', 'conexoes': 0, 'selos': ['Menor custo'], 'dias': 3}, {'id': 'rota-t3-t4', 'preco': 750.0, 'duracao': '2 d', 'conexoes': 1, 'selos': [], 'dias': 12}, {'id': 'rota-t2', 'preco': 780.0, 'duracao': '2 h 15 min', 'conexoes': 0, 'selos': ['Menor tempo', 'Mais confiável'], 'dias': 0}]
Cenario 03 | HTTP 200 | total_opcoes=1 | criterio=menor_tempo | rotas=[{'id': 'rota-t2', 'preco': 780.0, 'duracao': '2 h 15 min', 'conexoes': 0, 'selos': [], 'dias': 0}]
Cenario 04 | HTTP 200 | total_opcoes=1 | criterio=menor_tempo | rotas=[{'id': 'rota-t2', 'preco': 780.0, 'duracao': '2 h 15 min', 'conexoes': 0, 'selos': [], 'dias': 0}]
Cenario 05 | HTTP 200 | total_opcoes=2 | criterio=menor_tempo | rotas=[{'id': 'rota-t10', 'preco': 780.0, 'duracao': '2 h 15 min', 'conexoes': 0, 'selos': ['Menor tempo', 'Mais confiável'], 'dias': 0}, {'id': 'rota-t9', 'preco': 350.0, 'duracao': '4 d', 'conexoes': 0, 'selos': ['Menor custo'], 'dias': 3}]
Cenario 06 | HTTP 200 | total_opcoes=2 | criterio=menor_tempo | rotas=[{'id': 'rota-t5', 'preco': 320.0, 'duracao': '11 h', 'conexoes': 0, 'selos': ['Menor tempo'], 'dias': 20}, {'id': 'rota-t6', 'preco': 190.0, 'duracao': '1 d 12 h', 'conexoes': 0, 'selos': ['Menor custo', 'Mais confiável'], 'dias': 5}]
Cenario 07 | HTTP 200 | total_opcoes=0 | criterio=menor_tempo | rotas=[]
Cenario 08 | HTTP 200 | total_opcoes=1 | criterio=menor_tempo | rotas=[{'id': 'rota-t7', 'preco': 120.0, 'duracao': '18 h', 'conexoes': 0, 'selos': ['Desatualizado'], 'dias': 45}]
Cenario 09 | HTTP 200 | total_opcoes=1 | criterio=menor_tempo | rotas=[{'id': 'rota-t4', 'preco': 210.0, 'duracao': '1 d 18 h', 'conexoes': 0, 'selos': [], 'dias': 12}]
Cenario 10 | HTTP 422 | body={"codigo": "PARAMETRO_INVALIDO", "mensagem": "Origem e destino não podem ser a mesma localidade."}
Cenario 11 | HTTP 422 | body={"codigo": "PARAMETRO_INVALIDO", "mensagem": "Critério 'banana' inválido. Valores permitidos: mais_confiavel, menor_custo, menor_tempo."}
Cenario 12 | HTTP 422 | body={"codigo": "PARAMETRO_INVALIDO", "mensagem": "Formato de data '20/11/2026' inválido. Utilize o padrão ISO YYYY-MM-DD (ex: 2026-11-20)."}
Cenario 13 | HTTP 422 | body={"codigo": "PARAMETRO_INVALIDO", "mensagem": "Parâmetro inválido ou ausente: destino: Field required"}
Cenario 14 | HTTP 404 | body={"codigo": "LOCALIDADE_NAO_ENCONTRADA", "mensagem": "Origem ou destino não localizados na malha de transporte."}
Cenario 15 | HTTP 200 | count=1 | nomes=['Belém']
Extra /docs | HTTP 200
Extra /openapi.json | HTTP 200
```

---

## 5. Front-End (`web/`), Build, Auditoria (`npm audit`) e Prism CLI

### `npm install`, `npm run build` e `npm run dev`
```text
added 63 packages, and audited 64 packages in 6s
2 vulnerabilities (1 moderate, 1 high)

vite v5.4.21 building for production...
transforming...
✓ 32 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.72 kB │ gzip:  0.42 kB
dist/assets/index-CIbzZ4YJ.css    3.99 kB │ gzip:  1.25 kB
dist/assets/index-CSjB5VMs.js   150.04 kB │ gzip: 48.53 kB
✓ built in 1.53s

Vite dev http://localhost:5173/ -> HTTP 200, bytes=875 (Local: http://localhost:5173/)
```

### `npm audit` (Risco aceito documentado em `web/README.md`)
```text
esbuild  <=0.24.2
Severity: moderate
esbuild enables any website to send any requests to the development server and read the response - https://github.com/advisories/GHSA-67mh-4wv8-2f99
fix available via `npm audit fix --force`
Will install vite@8.3.8, which is a breaking change
node_modules/esbuild
  vite  <=6.4.3
  Depends on vulnerable versions of esbuild
  node_modules/vite

2 vulnerabilities (1 moderate, 1 high)
```

### Prism CLI Mock (`npx @stoplight/prism-cli mock docs/openapi.yaml --port 4010`)
```text
Prism /api/v1/localidades -> HTTP 200, count=7
Prism Prefer example=rota_1_belem_manaus -> HTTP 200, Belém->Manaus, total_opcoes=3, ids=['rota-t2', 'rota-t3-t4', 'rota-t1']
Prism Prefer example=rota_2_manaus_tefe -> HTTP 200, Manaus->Tefé, total_opcoes=2, ids=['rota-t5', 'rota-t6']
```

---

## 6. Itens "não executado" e Motivos

* **Inspeção visual em navegador real em modo dispositivo (360 px) (Seção 5.2):** **não executado** — o servidor MCP `chrome_devtools` falhou ao conectar ao Chrome por ausência do arquivo `DevToolsActivePort` (`chrome://inspect/#remote-debugging` desabilitado no ambiente local). Os utilitários de formatação (`web/src/utils/format.js`) foram validados em Node.js e o servidor `vite` respondeu HTTP `200` em `http://localhost:5173/`.
* **Renderização visual dos diagramas Mermaid (`docs/diagramas_database.md`):** **diagramas não renderizados** em renderizador visual/CLI neste terminal (não há ferramenta CLI de renderização Mermaid instalada no ambiente).
