# Estudo do Flask

**Data:** 2026-09-10

**Autor:** Pedro Henrique Cabral Leite

**Status:** Em aberto

---

## O que é o Flask

O Flask é um micro-framework para Python usado para criar aplicações web e APIs para o back-end. 

Ele é chamado de "micro" não porque é limitado, mas porque ele não vem com um monte de coisas pré-instaladas que a gente não vai usar. Ele entrega só o básico para subir um servidor e criar as rotas (URLs), deixando a gente livre para escolher as ferramentas e bibliotecas que o projeto realmente precisar.

---

## Como e por que usar no nosso projeto

> Criação de APIs leves
O Flask permite criar rotas (GET, POST) em poucas linhas para responder requisições e devolver respostas em formato JSON, ligando o back-end com o front-end.

> Fácil de aprender e mexer
A sintaxe é bem direta para quem já conhece o básico de Python. Não precisa aprender uma estrutura gigante ou cheia de regras logo de início, o que ajuda todo mundo do grupo a entender o código.

> Integração com a análise de dados
Como as análises e tratamentos de dados do time estão sendo feitos em Python (no Colab e Jupyter), fica muito fácil importar esses scripts e modelos diretamente dentro das rotas do Flask.

> Flexibilidade de organização
Dá para começar com um arquivo só para testar as primeiras rotas e depois organizar em pastas separadas conforme o projeto for crescendo.

---

## Exemplo simples de rota

Um exemplo básico de como o Flask funciona para criar uma rota que responde JSON:

```python
from flask import Flask, jsonify

app = Flask(__name__)

# Rota de teste para ver se o servidor está funcionando
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"mensagem": "Servidor Flask rodando certinho!"})

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Bibliotecas que podemos usar junto

* **Flask-CORS:** Necessário para permitir que o front-end acesse as rotas do Flask sem bloqueios de segurança do navegador.
* **Pandas:** Para ler e manipular os dados que serão entregues pelas rotas.
* **Requests:** Caso a gente precise consumir dados de alguma outra API externa.

---

## Pontos de atenção

> Não vem com banco de dados pronto
Ao contrário de frameworks maiores como o Django, o Flask não vem com banco ou telas administrativas prontas. Se o projeto precisar salvar dados em banco, teremos que instalar e configurar uma biblioteca à parte (como SQLAlchemy ou SQLite nativo).

> Organização por conta do time
Como ele não impõe um padrão fixo de pastas, a gente precisa combinar entre a equipe como vamos organizar os arquivos para não virar bagunça depois.