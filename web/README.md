# Embarque Amazônia — Front-End PWA (React + Vite)

Este diretório contém a aplicação web do passageiro desenvolvida com **React 18** e empacotada com **Vite**.

## Responsáveis
* **Herbert Aciolly:** Telas P01–P04 (Home, Localidades, Filtros e Lista de Resultados) e Design System.
* **Lucas Mutran:** Telas P05–P10 (Comparação de opções, Detalhes, Mapa, Rotas salvas e Modo Offline).

## Como Executar Localmente

### 1. Instalar as dependências
```bash
npm install
```

### 2. Iniciar o servidor de desenvolvimento
```bash
npm run dev
```
Acesse no navegador: `http://localhost:5173`

## Integração com a API
Por padrão, a aplicação se conecta à API local do FastAPI em:
`http://localhost:8000/api/v1`

Caso queira apontar para o mock do Prism CLI ou outro endpoint, crie um arquivo `.env` na pasta `web/` com:
```env
VITE_API_BASE_URL=http://127.0.0.1:4010/api/v1
```
