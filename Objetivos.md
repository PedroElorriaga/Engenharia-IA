# As coisas devem ser feitas com Métodos Pedrinho
Aqui vou listar alguns pontos onde enxergo e vejo que as vagas pedem e eu não sei (Não precisa ser perfeito/dominar)

---
### Lista das coisas que acreditamos ser importantes aplicar um esforço de conhecimento
Para marcar como concluido, ao menos um projeto do assunto

- AWS (EC2, SQS, S3, DYNAMODB, etc...) [ ]
- RabbitMQ (Testar uso real/simulado) [ ]
- Uma linguagem mais voltada ao mercado de bancos (Kotlin, Go, Java) [ ]
- Redis (Testar uso real/simulado) [✅]
- System Design (Saber pelo menos explicar o motivo de escolher X ao invés de Y) [ ]
- Design Patterns (Saber o porque aplicar tal design) [ ]
- Testes Automatizados (Sabemos até o conceito, mas não sentimos confiança em desenvolver testes sem IA) [✅]
- Kubernets (Ja vimos muito isso em vagas, mas nunca estudamos) [ ]
- Terraform (Entender mais, aplicar ao menos em um projeto) [ ]
- DDD (Entender o real uso dele e porque) [ ]
- Evitar Race Conditions [ ]
- Como fazer POCS/MVP [✅]
- Observabilidade (Logs, Metrics, Tracing) [ ]
- Spec-Driven Development [ ]

Lembre-se, ja vimos diversos desses conceitos, mas agora queremos realmente nos tornar fora da curva
Não precisamos tentar provar nada a ninguem, é o Pedrinho pelo Pedrinho

### Coisas boas também que percebi que melhoramos em 6 meses
- Documentar projetos
- Tentar entender mais o que acontece por baixo dos panos das aplicações
- Entender mais sobre SQL
- Criar projetos e termina-los
- Subir projetos para produção
- Usar testes nos projetos, mesmo que com auxilio da IA, ainda sim é algo
- Sede por querer sempre evoluir

Obviamente não somos uma máquina para aprender tudo, há coisas que ficaram só no básico e ta tudo bem


### Key problems 

- Double Spend / Double Submit
- Race Conditions
- Idempotency
- Consistency

---

### OBJETIVO PRINCIPAL - Engenheiro de IA/Software em algum banco (Itau, Bradesco, Nubank, etc...)
Aqui listaremos o que fizemos e precisaremos fazer para atingir esse objetivo

- Entender como LLM (Large Language Models) funcionam de verdade [✅]
    - O que são TOKENS
    - O que é CONTEXT WINDOW
    - O que é TEMPERATURA
    - Role System
        - System Messages
        - User Messages
        - Assistant Messages

- Como construir LLM APIs (Anthropic, OpenAI) [✅]
    - Como fazer chamadas de API
    - Como manipular as respostas
    - Como Construir conversas multi-tenant
    - Como lidar com erros

- Prompt Engineering e Sctructured Outputs [✅]
    - Como escrever SYSTEM PROMPTS
    - Entender FUNCTION CALLING
    - aprender JSON MODE e STRUCTURED OUTPUTS

- RAG (Retrieval Argumented Generation) e Vector databases [✅]
    - Pinecone
    - Chroma

- Aprender frameworks de orquestração [✅]
    - LangChain
        - Orquestações de LLMs
        - Fazer Retries
        - Ter processos muilti-stage
        - Ter diferentes LLMs chat conversando entre elas

- LLMOPS e Deployment [✅]
    - Entender RATE LIMITING
    - Entender CACHING
    - Monitoramento
    - Administração

- Construir projetos reais [✅]
    - Ex: Contruir um RAG chat que possa responder sobre uma especifica area, Contrua um AI Agent como uma ferramenta

- System Design para esse contexto [ ]


New gaps

1. Evals com RAGAS       → resolve o "como sei que meu RAG funciona?"
2. AI Security           → diferencial enorme para bancos (LGPD)
3. Human-in-the-loop     → LangGraph já está no repo, é um passo natural
4. Advanced RAG          → reranking + hybrid search
5. System Design de IA   → seu próprio objetivo pendente
6. Fine-tuning           → mais longo prazo

Evals (1 a 2 semanas).
  Golden dataset de 50 a 100 perguntas com resposta esperada.
  RAGAS (faithfulness, context precision/recall) e um LLM-as-judge com rubrica.
  Rodando no GitHub Actions e bloqueando o merge se a métrica cair. Esse é o artefato que responde a pergunta 1.
  
Observabilidade (1 semana).
  Langfuse ou Phoenix (ambos têm opção self-hosted) com um trace por requisição.
  Custo, tokens, latência e versão do prompt em cada span.
  Um dashboard com custo por requisição e p95.
  Isso fecha uma pendência do seu checklist (logs, metrics, tracing) e responde a pergunta 3.
  
Custo e roteamento (1 semana).
  Com eval e tracing prontos, você consegue comparar modelos de verdade: roda o mesmo dataset em um modelo de fronteira e em um menor, e compara qualidade, custo e latência.
  Depois implementa um roteador simples (classificador de complexidade e fallback pro modelo maior).
  Adicione prompt caching e cache semântico no Redis, que você já sabe usar.
  Você sai com uma tabela de números reais, que vale mais que qualquer resposta teórica na entrevista (perguntas 2 e 4).
  
Advanced RAG. Hybrid search (BM25 mais vetor) e reranking, medindo o ganho no seu próprio eval. Assim você prova que a melhoria funcionou em vez de só afirmar.

Segurança e governança, o seu diferencial para banco.
  Mascaramento de PII (CPF, cartão) antes de enviar ao LLM.
  Defesa contra prompt injection.
  Log de auditoria.
  Human-in-the-loop com LangGraph para ações sensíveis.
  Citar LGPD aqui faz diferença em vaga bancária.
  
Fundamentos de backend que bancos cobram. Seus “Key problems” (idempotência, race conditions, double submit) são o que realmente separa candidato em banco. Sugestão: a mesma API FastAPI do capstone ganha uma fila (RabbitMQ ou SQS), chaves de idempotência e testes de concorrência. Isso mata vários itens do seu checklist num projeto só e conecta IA com a engenharia de software que a vaga pede.

Deploy. Dockerize, suba na AWS (EC2 ou ECS, S3, SQS) e, se der, descreva a infra com Terraform. Kubernetes eu deixaria por último: é cobrado em vagas, mas dificilmente é eliminatório para quem está entrando.