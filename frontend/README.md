# Frontend: Astro + Alpine.js + Tailwind + Chart.js

## Pré-requisitos

- [Node.js 22.12 ou superior](https://nodejs.org/) (exigido pelo Astro 6)

## Rodando localmente

Na raiz do repositório:

```bash
npm install
npm run install-fe
cp frontend/.env.example frontend/.env
npm run dev-fe
```

Abre em `http://localhost:4321`.

Se preferir rodar de dentro da pasta `frontend/`, use `npm install` e `npm run dev`.

## Variáveis de ambiente

A URL base da API vem da variável `PUBLIC_API_BASE`, definida no arquivo `.env`.
Se ela não existir, o projeto usa `http://localhost:8000`.

Variáveis com prefixo `PUBLIC_` ficam visíveis no navegador. Não coloque segredos nelas.

## Estrutura

- `src/pages/`: cada arquivo vira uma rota (`index.astro` é `/`, `dashboard.astro` é `/dashboard`).
- `src/layouts/`: estrutura base das páginas (head, header e footer).
- `src/components/`: componentes reutilizáveis.
- `src/lib/api.js`: funções que chamam a API backend.
- `src/styles/global.css`: importa o Tailwind.

## Lint e formatação

```bash
npm run lint
npm run format
```

O `lint` roda ESLint e Prettier em modo de checagem, igual ao CI. O `format` corrige o que der automaticamente.

## Build de produção

```bash
npm run build
```

Gera os arquivos estáticos em `dist/`. Dá pra conferir com `npm run preview`.

## Deploy na Vercel

Como o site é estático (`output: 'static'`, o padrão do Astro), a Vercel
detecta o framework Astro sozinha e faz o deploy sem precisar de adapter
nem de `vercel.json`.

**Opção 1: pelo dashboard**

1. Sobe esse projeto num repositório no GitHub.
2. Em vercel.com, "Add New Project" e importa o repositório.
3. A Vercel já detecta Astro e preenche tudo sozinha. É só clicar em Deploy.

**Opção 2: pela CLI**

```bash
npm i -g vercel
vercel
```
