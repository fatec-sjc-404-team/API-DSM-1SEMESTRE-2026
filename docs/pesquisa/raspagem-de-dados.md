# raspagem de dados

**Data:** 2026-09-10
**Autor:** Isabela
**Participantes:**
**Facilitador:**

---
## **RASPAGEM DE DADOS**

### **Serasa • IBGE • Banco Central**

---

### **O que é raspagem de dados?**

Raspagem de dados, ou *Web Scraping*, é uma técnica usada para coletar informações automaticamente de páginas da internet. Em vez de uma pessoa copiar os dados manualmente, um programa acessa a página, encontra as informações desejadas e pode organizá-las para análise.

---

### **Como funciona?**

| Passo | Etapa | Descrição |
| :---: | :--- | :---|
| **01** | **Acessar** | O programa acessa a página ou fonte de dados. |
| **02** | **Ler** | Ele interpreta o conteúdo da página, geralmente em HTML. |
| **03** | **Localizar** | Encontra os elementos que contêm as informações desejadas. |
| **04** | **Extrair** | Retira os dados selecionados. |
| **05** | **Organizar** | Salva os dados para consulta, análise ou criação de gráficos. |

---

### **Para que serve?**

* Automatizar tarefas que seriam feitas manualmente.  
* Economizar tempo na coleta de informações.  
* Coletar grandes quantidades de dados.  
* Comparar informações de diferentes fontes.  
* Criar tabelas, gráficos e relatórios.  
* Apoiar pesquisas e análises.

---

### **Exemplos de fontes**

| Fonte | Descrição |
| :--- | :--- |
| **SERASA** | Informações relacionadas a crédito e situação financeira. Exige cuidado especial com dados pessoais, financeiros e com a LGPD. |
| **IBGE** | Dados estatísticos sobre o Brasil, como população, municípios, educação, trabalho e economia. |
| **BANCO CENTRAL** | Dados econômicos e financeiros, como taxas de juros, câmbio e indicadores. |
  **DATA_SENADO** |Dados abertos institucionais, projetos de lei, proposições e informações legislativas do Senado Federal.|

---

### **Exemplo prático**

Imagine que queremos acompanhar um indicador econômico público. Em vez de copiar os valores manualmente todos os dias, podemos automatizar a coleta e depois analisar os resultados.

* **Fonte oficial** → disponibiliza o dado.  
* **Programa** → acessa a fonte autorizada.  
* **Coleta** → obtém os valores.  
* **Organização** → salva em uma tabela.  
* **Análise** → cria um gráfico ou gera uma conclusão.

---

### **Raspagem de dados × API**

| RASPAGEM | API |
| :--- | :--- |
| Interpreta uma página para encontrar dados. | Permite acessar dados por uma interface estruturada. |
| Pode depender do formato do site. | Normalmente é criada para facilitar o acesso por sistemas. |
| Deve respeitar as regras da página. | Deve respeitar as regras e limites da API. |

---

### **Cuidados importantes** 

* Verificar se a coleta é permitida pela fonte.  
* Respeitar os termos de uso do site.  
* Respeitar a LGPD e a privacidade das pessoas.  
* Não coletar dados pessoais ou restritos de forma indevida.  
* Evitar excesso de requisições e sobrecarga do serviço.  
* Preferir APIs, arquivos e bases oficiais quando disponíveis.

---

### **Perguntas para revisar** 

* **O que é Web Scraping?**  
  Coleta automatizada de informações disponíveis em páginas da internet.

* **Para que serve?**  
   Para automatizar a coleta, economizar tempo e organizar dados para análise.

* **O que podemos encontrar no IBGE?**  
   Dados estatísticos como população, educação, trabalho e economia.

* **O que o Banco Central disponibiliza?**  
   Dados econômicos e financeiros, como juros, câmbio e indicadores.

* **Por que o Serasa exige cuidado?**  
   Porque podem existir informações pessoais e financeiras protegidas.

* **É sempre melhor fazer scraping?**  
  Não. Quando existe uma API ou base oficial adequada, ela normalmente deve ser priorizada.

---

### **Resumo para memorizar**

> **ACESSAR ➔ LOCALIZAR ➔ EXTRAIR ➔ ORGANIZAR ➔ ANALISAR**

A raspagem de dados automatiza a coleta de informações. Ela pode ser útil em pesquisas, análises e projetos, mas deve ser feita de forma responsável, respeitando a privacidade, a LGPD e as regras da fonte.