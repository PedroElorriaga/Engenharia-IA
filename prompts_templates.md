### ChatPromptTemplate — O mais usado
- sempre que você tiver variáveis dinâmicas no prompt e quiser usá-lo em uma chain.

```
template = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de {dominio}. Responda em {idioma}."),
    ("human", "{pergunta}")
])

mensagens = template.invoke({
    "dominio": "finanças",
    "idioma": "português",
    "pergunta": "O que é CDI?"
})
```

### Message Objects — SystemMessage, HumanMessage, AIMessage
- objetos que representam cada mensagem do chat com papel definido (system, human, ai).

```
historico = [SystemMessage(content=SYSTEM_PROMPT)]

def chat(pergunta: str):
    historico.append(HumanMessage(content=pergunta))
    resposta = llm.invoke(historico)
    historico.append(AIMessage(content=resposta.content))
    return resposta.content
```


### Arvore de decisão

```
Tenho variáveis no prompt?
    ├── NÃO → Use Message Objects direto (SystemMessage, HumanMessage)
    └── SIM ↓
        │
        O system prompt tem variáveis?
        ├── SIM → SystemMessagePromptTemplate
        └── NÃO ↓
            │
            Tenho histórico de conversa?
            ├── SIM → ChatPromptTemplate + MessagesPlaceholder
            └── NÃO → ChatPromptTemplate.from_messages([("system","..."),("human","{var}")])
```