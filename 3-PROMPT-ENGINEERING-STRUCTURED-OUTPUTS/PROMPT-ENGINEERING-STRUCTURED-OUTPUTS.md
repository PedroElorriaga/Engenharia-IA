### O que é PROMPT e SYSTEM PROMPT
No contexto de **prompt**, é mais comum utilizar para instruções imediatas e especificas para IA em coisas mais genericas

Já o **System Prompt** é usado para definir o comportamento e persona da IA de forma consistente

Os fundamentos de configuração de um System Prompt:

- Persona
    - É o que define o papel, comportamento e identidade do modelo

- Contexto
    - Aqui vamos especificar o dominio do conhecimento, publico alvo e circunstancias da aplicação

- Objetivos
    - O que esse modelo deve fazer e as tarefas principais desse modelo

- Regras
    - São os limites e diretrizes

- Formato de saída
    - Que é como que as respostas devem ser estruturadas

- Exemplos
    - São as demonstrações de comportamento ideal, podemos fornecer exemplos de entrada e saída, que são chamadas de fill shots

### Function Calling
É a capacidade de um modelo interagir com ferramentas externas APIs, Bancos de dados, Funções em vez de apenas gerar textos

[Arquivo de estudos](Atividades\tool_calling_otavio.py)

**Alguns pontos para realmente entender as Function Calling(Ou Tool Calling)**
- Não é a IA quem chama a função, mas sim os DEVS

- Normalmente colocamos uma documentação nas funções que criamos para ajudar a IA a identificar qual ferramenta utilizar

### Structured Outputs
Existem 3 niveis de implementação de saidas estruturadas

- Prompt Engineering, onde você pede "Responda em JSON". Porém é instavél
    - ``` Extraia o nome e a idade do texto: 'O João tem 25 anos'. Responda apenas com um JSON no formato {"nome": string, "idade": number}. Não diga mais nada. ```

- Function Calling/Tool Use, o modelo decide chamar uma função e passa os argumentos em JSON. Muito mais confiável
    - ``` tools = [{
        "type": "function",
        "function": {
            "name": "cadastrar_usuario",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "idade": {"type": "integer"}
                },
                "required": ["nome", "idade"]
            }
        }
        }] 
        ```

- Constrained Decoding, o motor da IA (OpenAI ou LLMs locais por exemplo), restringe os tokens que o modelo pode gerar. Se o proximo caractere no esquema deve ser uma {, o modelo é proibido de gerar qualquer outra coisa. Isso garante 100% de conformidade
    - ```
        from pydantic import BaseModel

        class Usuario(BaseModel):
            nome: str
            idade: int

        # Na chamada da API (ex: OpenAI SDK)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": "O João tem 25 anos"}],
            response_format=Usuario, # Aqui a mágica acontece
        )

        user = completion.choices[0].message.parsed
        print(user.nome) # Saída garantida como string: "João"
        ```

### Few Shots
É uma tecnica que você fornece ao modelo alguns exemplos (os "Shots") de entrada e de saida, dentro do proprio prompt antes de fazer a pergunta

```
PROMPT_TEMPLATE = """
Extraia os dados do perfume seguindo o padrão:
{exemplo_1}
{exemplo_2}
Entrada: {nova_entrada}
Saída:
"""
```