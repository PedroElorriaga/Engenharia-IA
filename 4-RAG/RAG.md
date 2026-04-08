### Token Hogging
Refere-se a utilização desproporcional e muitas vezes, insuficiente de recursos de computação, seja em redes de blockchain ou IA, consumindo grande quantidade de tokens de forma desnecessaria 

- Exemplo: Um usuário decide colar o texto inteiro da Wikipedia em seu chat

Termos importantes:
- RPM (Requests per minute)
- RPD (Requests per day)
- TPM (Tokens per minute)
- TPD (Tokens per day)
- IPM (Image per minute)

### RAG (Retrieval Argumented Generation)
Você está aumentando a geração de texto do LLM com informações recuperadas de uma base de conhecimento. É a solução para o maior problema dos LLMs eles não sabem o que acontece depois do treinamento deles e não conhecem seus dados privados

Exemplo de problema que o RAG resolve:
- 500 PDFs de contratos jurídicos

- Um Manual tecnico de 1000 páginas

- Documentações internas que nenhum LLM tem acesso

Com RAG nos armazeariamos tudo em um Vector DB, quando o usuário pergunta algo, o sistema busca apenas 3 ou 4 paragrafos main relevantes e os injeta no prompt, o LLM responde com base nesses parágrafos, assim conseguimos ter respostas mais precisas e atualizadas, sem precisar treinar o modelo do zero

### Vector Databases
Bancos de dados especializados em armazenar e buscar vetores numericos por similaridade, não por igualdade exata como o SQL faria.

Um Embedding é o processo de transformar dados (texto, imagens, etc) em vetores numéricos. Esses vetores capturam o significado semântico dos dados, permitindo que sejam comparados por similaridade.

Exemplo: 
```
    Cachorro -> [-0.81] 
    Canino -> [-0.79]
```

A palavra 1 e 2 tem vetores parecidos com palavras diferentes ?
- Porque o modelo de embedding foi treinado para capturar significado

A distancia entre vetores é calculada por Cosine Similarity

```
1.0 -> Vetores idênticos
0.0 -> Vetores perpendiculares (sem relação)
-1.0 -> Vetores opostos
```