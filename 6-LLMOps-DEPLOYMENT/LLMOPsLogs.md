### Rate Limiting
É o controle de quantas requisições um sistema aceita em um periodo de tempo

- Fixed Window: Exemplo, 100 requisições por minuto. O contador é resetado a cada minuto.
- Sliding Window: O contador é atualizado a cada requisição, e o tempo é contado a partir da última requisição.
- Token Bucket: Cada requisição consome um token, e os tokens são reabastecidos a uma taxa fixa ou um período de tempo.

### Cache
- Cache de resposta do LLM: Se o mesmo prompt aparecer de novo, devolve a resposta do cache, sem precisar chamar o LLM.
- Cache de embeddings: Se o mesmo texto for embeddado de novo, devolve o embedding do cache, sem precisar chamar o LLM.
- Cache de retrieval: Se o mesmo texto for buscado de novo, devolve o resultado do cache, sem precisar chamar o LLM.
- Cache de tools calling: Se a mesma ferramenta for chamada de novo, devolve o resultado do cache, sem precisar chamar a ferramenta.

Alguns TTLs recomendados:
- Clima: 5 a 10 minutos
- Cotação de moedas: 30 segundos a 1 minuto
- Dados cadastrais: 1 hora a 1 dia
- Embeddings: sem expiração, ou expiração longa (1 semana a 1 mês)
- Busca vetorial: sem expiração, ou expiração longa (1 semana a 1 mês)

### LangSmith
É usado para monitorar e rastrear as interações com o LLM, incluindo prompts, respostas, chamadas de ferramentas, etc. Ele pode ser integrado com o LangChain para coletar dados de forma automática.

Para configurar o LangSmith, é necessário definir as seguintes variáveis de ambiente:
- LANGSMITH_API_KEY: A chave de API para autenticação.
- LANGCHAIN_PROJECT: O nome do projeto para organizar os dados.
- LANGCHAIN_TRACING_V2: Habilita o tracing para coletar dados detalhados
- LANGSMITH_ENDPOINT: O endpoint da API do LangSmith (opcional, se estiver usando o endpoint padrão).

Com o LangSmith, é possível visualizar as interações em um dashboard, analisar o desempenho do modelo, identificar gargalos e otimizar as chamadas para o LLM.

### O que monitorar em sistemas LLMs
- Latência: Tempo de resposta por chamada (Detectar lentidão)
- Tokens consumidos: Quantidade de tokens usados por chamada (Controlar custos)
- Custo: $ por usuario | dia | feature (Controlar orçamento)
- Erros: Taxa de erros por tipo (Detectar falhas, saude do sistema)
- Qualidade: Feedback dos usuários, ou métricas de avaliação (model drift, satisfação do usuário)
- Cache hit rate: Taxa de acertos no cache (Otimizar performance e custos)


### Versionamento de Prompts
Usado para controlar as mudanças nos prompts, e garantir que as mudanças não quebrem o sistema. O LangSmith permite salvar e versionar os prompts, e recuperar versões anteriores quando necessário.

```
Criou/editou prompt
        ↓
  client.push_prompt()   →   LangSmith salva nova versão
        ↓
  client.pull_prompt()   →   Seu código usa o prompt versionado
```


### Visão geral de LLMOps

```
Usuário faz uma pergunta
        ↓
[Rate Limiter] → Bloqueado? → Retorna 429
        ↓ Permitido
[Cache] → Hit? → Retorna resposta instantânea
        ↓ Miss
[LLM Pipeline] → Executa RAG / Agent / Chain
        ↓
[Monitoramento] → Registra latência, tokens, custo
        ↓
[Cache] ← Salva resposta para próxima vez
        ↓
Resposta entregue ao usuário
```