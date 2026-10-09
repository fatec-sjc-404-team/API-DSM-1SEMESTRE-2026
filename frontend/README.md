# Astro + Alpine.js + Chart.js

## Rodando localmente

```bash
npm install
npm run dev
```

Abre em `http://localhost:4321`.

## Build de produção

```bash
npm run build
```

Gera os arquivos estáticos em `dist/`. Dá pra conferir com `npm run preview`.

## Deploy na Vercel

Como o site é estático (`output: 'static'`, o padrão do Astro), a Vercel
detecta o framework Astro sozinha e faz o deploy sem precisar de adapter
nem de `vercel.json`.

**Opção 1 — pelo dashboard:**
1. Sobe esse projeto num repositório no GitHub.
2. Em vercel.com, "Add New Project" e importa o repositório.
3. A Vercel já detecta Astro e preenche tudo sozinha. É só clicar em Deploy.

**Opção 2 — pela CLI:**
```bash
npm i -g vercel
vercel
```

## Onde a API entra

A URL base da API fica em `src/lib/api.js`. Troca o valor de `API_BASE`
pela URL real antes de testar com dados de verdade.
