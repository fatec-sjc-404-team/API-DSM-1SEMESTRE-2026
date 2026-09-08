# ADR: Definição do projeto

**Data:** 2026-09-08

**Autor:** Khalil

**Status:** Proposto

---
# Nosso Projeto

## Objetivo

O nosso objetivo é criar um site que ajude a identificar regiões onde as pessoas precisam de crédito, mas não conseguem acesso aos bancos tradicionais.

Para isso, vamos utilizar dados públicos de:

- Banco Central (BCB/BACEN)
- IBGE
- Serasa

A partir desses dados, vamos calcular um **Score de Oportunidade** para cada região, buscando identificar locais com maior necessidade e potencial de acesso a crédito.

---

## Google Colab

O **Google Colab** será utilizado como ambiente para:

- Baixar os dados das fontes públicas;
- Fazer a raspagem de dados (*web scraping*);
- Realizar o tratamento e a análise dos dados;
- Criar gráficos e visualizações;
- Testar os códigos de análise.

---

## Site

Para o desenvolvimento do site, vamos utilizar:

- **HTML** para estruturar as páginas;
- **CSS** para estilização e responsividade;
- **Python** para a lógica da aplicação;
- **Flask** para integrar o Python com o HTML/CSS.

As telas do site serão:

- Simples;
- Bonitas;
- Fáceis de utilizar;
- Responsivas para celular e computador.

### Flask

O Flask será responsável por conectar o código Python às páginas HTML e aos arquivos CSS, permitindo transformar o projeto em um site funcional acessível pelo navegador.

---

## Back-end

O back-end será desenvolvido utilizando **Python + Flask**.

A lógica inicialmente será simples, tendo como principais funções:

- Receber os dados necessários;
- Processar as informações;
- Aplicar os filtros;
- Calcular ou apresentar o Score de Oportunidade;
- Exibir os resultados nas páginas do site.

---

## Banco de Dados

Vamos utilizar **SQL** para criar um banco de dados simples.

O banco de dados terá como objetivo principal armazenar:

- Comentários dos jornalistas sobre as matérias;
- Feedbacks deixados pelos jornalistas;
- Filtros utilizados no sistema.

Não teremos estruturas complexas de banco de dados nesta primeira etapa.

---

## Login

Inicialmente, **não será implementado sistema de login**.

A ideia é simplificar a entrega e concentrar os esforços nas funcionalidades mais importantes do projeto.

O login poderá ser implementado posteriormente, caso todas as funcionalidades principais estejam concluídas e ainda haja tempo disponível.

---

# Definição do Produto — Sprint 1

## Tarefas da Primeira Entrega

### 1. Diretriz e Protótipo

**Responsável:** Iago

Definir a diretriz do produto e criar o **protótipo navegável da primeira Sprint**.

**Entregas:**

- Definição da proposta do produto;
- Estrutura das principais telas;
- Fluxo de navegação;
- Protótipo navegável.

---

### 2. Raspagem de Dados

**Responsável:** Isabela

Estudar e documentar como funcionará a **raspagem de dados (*web scraping*)**.

**Entregas:**

- Estudo das técnicas de raspagem;
- Identificação das fontes que poderão ser utilizadas;
- Documentação do processo;
- Definição de como os dados serão coletados.

---

### 3. Mapeamento IBGE / BCB / BACEN

**Responsável:** Khalil

Analisar e mapear quais dados são disponibilizados pelas fontes:

- IBGE;
- BCB;
- BACEN.

**Entregas:**

- Identificação das bases de dados;
- Levantamento das informações disponíveis;
- Identificação dos dados relevantes para o projeto;
- Documentação das fontes;
- Avaliação de como esses dados poderão ser utilizados no Score de Oportunidade.

---

### 4. Catalogação Serasa

**Responsável:** Fernando Gomes

Pesquisar as informações disponibilizadas pela **Serasa** e trazer um exemplo de catalogação de dados baseado nas fontes encontradas.

**Entregas:**

- Pesquisa das fontes de dados;
- Identificação das informações disponíveis;
- Exemplo de catalogação;
- Documentação das informações relevantes para o projeto.

---

### 5. Google Colab

**Responsável:** Fernando Ferreira

Estudar o funcionamento do **Google Colab** e preparar o ambiente de desenvolvimento em nuvem.

**Entregas:**

- Configuração do ambiente;
- Testes de execução de código;
- Organização inicial do notebook;
- Preparação do ambiente para análise dos dados.

---

### 6. Gráficos no Jupyter / Colab

**Responsável:** Rafael

Estudar a criação de gráficos utilizando **Jupyter Notebook / Google Colab** e pesquisar outras ferramentas de visualização de dados.

**Entregas:**

- Estudo das bibliotecas de gráficos;
- Criação de gráficos de teste;
- Pesquisa de ferramentas alternativas de visualização;
- Identificação das melhores opções para o projeto.

---

### 7. Análise do Projeto 3-ADS

**Responsável:** Pedro

Analisar a API do projeto **Herança (3-ADS)** e entender como era realizada a manipulação dos dados.

**Entregas:**

- Análise da API;
- Entendimento da estrutura utilizada;
- Identificação das formas de manipulação dos dados;
- Documentação do que pode ser aproveitado como referência para o novo projeto.

---

### 8. Implementação do Banco de Dados

Criar uma estrutura simples de banco de dados para armazenar os **feedbacks dos jornalistas sobre as matérias** e os **filtros utilizados no sistema**.

**Entregas:**

- Criação do banco de dados;
- Criação das tabelas necessárias;
- Estrutura para armazenar os feedbacks;
- Estrutura para armazenar os filtros;
- Testes de inserção e consulta dos dados.

---