# Embarque Amazônia — Front-End Web (React + Vite)

Este diretório contém uma **tela funcional inicial de busca e listagem de rotas** desenvolvida em React 18 com Vite para demonstrar o consumo da API REST (`GET /api/v1/localidades` e `GET /api/v1/rotas`).

> **Escopo atual (Semana 2 — 19/11):** Estão integradas e funcionais as 4 novas telas do fluxo do passageiro: **P03** (Critérios e Filtros Avançados), **P04** (Busca e Listagem de Opções com seleção comparativa), **P05** (Comparador de até 3 Opções lado a lado), **P06** (Detalhe da Rota com linha do tempo vertical e cálculo de conexões) e **P07** (Detalhe do Trecho com acomodações Rede/Camarote, aviso sazonal de vazante e contato), coordenadas via Hash Router em `Navegacao.jsx`. As telas P08 (mapa interativo), P09 (offline com IndexedDB) e o painel administrativo (A01–A06) estão programados para a Semana 3 (26/11).

## Como executar localmente

1. Instale as dependências:
   ```bash
   npm install
   ```
2. Gere o bundle de produção (opcional para validação):
   ```bash
   npm run build
   ```
3. Inicie o servidor de desenvolvimento em acesso local (`http://localhost:5173`):
   ```bash
   npm run dev
   ```

## Variável de ambiente (`VITE_API_BASE_URL`)

Por padrão, a interface consulta a API FastAPI em `http://localhost:8000/api/v1`.
Para apontar para outro endereço (como o mock estático do Prism CLI na porta `4010`), crie `web/.env` com:

```env
VITE_API_BASE_URL=http://127.0.0.1:4010/api/v1
```

## Segurança de dependências (`npm audit`)

A execução de `npm audit` reporta 2 vulnerabilidades no ecossistema de desenvolvimento (`esbuild <=0.24.2` — GHSA-67mh-4wv8-2f99, severidade moderada — e `vite <=6.4.3`, severidade alta em cadeia de desenvolvimento). Não há correção não-quebrante sem `--force` (a correção automática exige atualização para `vite@8.x`, mudança com quebra de compatibilidade).

Por se tratar de dependência exclusiva de build/dev-server e por o `vite.config.js` restringir o servidor a `host: 'localhost'`, o apontamento é tratado nesta entrega como **risco aceito (afeta só o servidor de desenvolvimento)**.
