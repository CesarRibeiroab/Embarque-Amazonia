# Embarque Amazônia — Front-End Web (React + Vite)

Este diretório contém uma **tela funcional inicial de busca e listagem de rotas** desenvolvida em React 18 com Vite para demonstrar o consumo da API REST (`GET /api/v1/localidades` e `GET /api/v1/rotas`).

> **Escopo atual (Semana 1):** Apenas o fluxo de busca por origem/destino, data e critério com exibição de opções, selos, recência e trechos expansíveis está implementado aqui. As demais telas planejadas do sistema (P01–P10 e A01–A06) existem no momento apenas como protótipo de design no Figma (não implementadas em código e sem suporte offline/manifest/service worker).

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
