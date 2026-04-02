### O que são INSTRUCTOR e LANGCHAIN
É como se fosse uma ORM das LLMs, se quisermos trocar de modelo facilmente sem reescrever tudo
podemos usar o LANGCHAIN por exemplo que facilita a manipulação de LLMs

- Documentação para trabalhar com varios models no LANGCHAIN https://reference.langchain.com/python/integrations/overview

### O que são MULTI-TENANT
O termo Multi-tenancy é um conceito fundamental na arquitetura de software, especialmente em modelos SaaS.
Significa que seu servidor atende mais de uma pessoa ao mesmo tempo

Imagine um prédio de apartamentos (a infraestrutura/software).

- No modelo Single-tenant, cada cliente tem seu próprio prédio físico. É seguro, mas caro e difícil de manter 
(você precisa de um síndico e equipe de limpeza para cada prédio).
- No modelo Multi-tenant, todos os clientes (inquilinos) moram no mesmo prédio. Eles compartilham a mesma infraestrutura (água, luz, elevador), 
mas cada um tem a chave do seu próprio apartamento. Um vizinho não pode entrar na casa do outro.

As principais caracteristicas
- Instância Única: Uma única versão do software serve a múltiplos clientes.
- Isolamento de Dados: Embora usem o mesmo banco de dados, os dados do "Cliente A" são invisíveis para o "Cliente B".
- Escalabilidade: É muito mais barato e fácil atualizar o sistema para 1.000 clientes de uma vez do que atualizar 1.000 instâncias separadas.

### TOP K e TOP P
São parametros para controlar aleatoriedade, criatividade, e precisão.

- TOP K Se definir K=50, o modelo considerara apenas as 50 palavras mais provaveis da sua distribuição de probabilidade e sorteara uma entre elas.
- TOP P Se definir P=0.9, o modelo ordenara as palavras da mais provavel para a menos provavel e seleciona as principais palavras cuja soma de
probabilidade atinga 90%

Para respostas factuais e precisas use vlaores baixos K=20 e P=0.3 

Para respostas criativas use valores mais altos K=100 e P=0.9

### O que são CHAINS
São componentes fundamentais que permitem conectar varios elementos, como LLMs, prompts, ferramentas e parse de saida

```
chain = prompt | llm | parser
```

### O que é STREAMING
É uma tecnica que transmite dados, permitindo que o modelo envie a resposta gerada palavra por palavra ou token por token em tempo real