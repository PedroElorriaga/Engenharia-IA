### Orquestração de LLMs
Orquestração é o processo de coordenar e gerenciar múltiplos componentes ou serviços para alcançar um objetivo específico. No contexto de LLMs, isso envolve a integração de diferentes modelos, APIs, bancos de dados e outros serviços para criar uma aplicação funcional e eficiente.

### Sequential Chain
É quando a saída de um LLM vira a entrada do proximo

```
Entrada -> LLM1 -> Saida1 -> LLM2 -> Saida2 -> LLM3 -> Saida3
```

Imagine um time de especialistas, onde cada um faz uma parte do trabalho ates de passar para o proximo

exemplos:

- 1: Podemos usar um modelo que é mais barato para extração de dados (GPT-3.5)
- 2: Um modelo mais potente na analise de dados (GPT-4)
- 3: Um modelo especializado em escrita criativa para gerar um texto mais fluida e natural (Claude)


### Chain
É quando temos uma cadeia de LLMs, mas eles podem conversar entre si, ou seja, não é necessário que a saída de um seja a entrada do outro, eles podem compartilhar informações e trabalhar juntos para resolver um problema.

```
# Só prompt + llm (retorna AIMessage)
chain = prompt | llm

# Prompt + llm + parser (retorna string pura)
chain = prompt | llm | StrOutputParser()

# Invocação
resposta = chain.invoke({"pergunta": "Qual a capital da França?"})
```

### Retries
Os erros mais comuns em LLMs são:

- Timeouts
- Erros de conexão
- Erros de API (ex: limite de tokens, erros de autenticação, etc)

os retries server para fazer algumas tentaivas antes de lançar o erro

No Langchain temos um metodo que é responsável por fazer isso, que é o with_retry()


### O que é um Pipeline multi-stage
É quando temos multiplas etapas de processamento

```
Sequential chain a -> b -> c

Parallel chain a -> b + c -> d (multistage-parallel.py)

Conditional chain a -> se x faz b -> senão faz c (multistage-conditional.py)
```

Em parallel chain executamos dois ou mais processos simultaneamente, sendo mais rapido que sequential chain

E quando usar cada um ?

- Serie, etapas que dependem uma da outra

- Paralelo, analises independentes da mesma entrada

- Condicional, diferentes inputs que precisam de tratamentos diferentes


### LangGraph
O LangGraph é uma biblioteca de orquestração de LLMs que permite criar grafos de processamento, onde cada node é uma função que pode ser um LLM, um parser, ou qualquer outra função Python. Ele suporta diferentes tipos de grafos, como sequenciais, paralelos e condicionais, e também tem suporte para retries e monitoramento.

- Nodes: Funções que executam uma ação, podem chamar uma LLM ou só rodar uma função Python

- Edges: Determinam qual node sera executado em seguida. Podem ser condicionais, apontando para diferentes nodes dependendo de uma condição