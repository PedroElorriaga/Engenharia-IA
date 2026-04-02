### O que são LLMs ?
São sistemas de inteligência artificial treinados com volumes massivos de dados textuais para entender, gerar e processar linguagem humana natural

Principais LLMs

- GPT-5/GPT-4o (OpenAI)
- Gemini (Google)
- Claude 3 (Anthropic)

### O que são TOKENS ?
As LLMs não leem palavras, elas leem pedaços de textos.
1 TOKEN pode representar uma palavra inteira, parte de uma palavra ou até mesmo um único caractere

- Site para ver o consumo de um prompt https://platform.openai.com/tokenizer

### O que são CONTEXT WINDOW ?
É a memoria de curto prazo, se a janela de contexto é de 8K tokens e o dialogo com a IA chega a 9K tokens,
o modelo começara a esquecer o inicio da conversa

### O que é TEMPERATURA ?
É o parametro que controla a aleatoriedade da resposta

Perto do 0 ele é menos criativo, ou seja, mais perto dos fatos
proximo a 1.0 ele é mais criativo, podendo alucinar mais

### O que são ROLE SYSTEM ?
Para que o modelo entenda o contexto de uma conversa, usamos alguns parametros

- System Message: O manual de instruções, o que o modelo pode ou não fazer 

```
{"role": "system", "content": (
    "Você é um assistente de bem-estar de nome Namu Assistent. Responda somente com JSON válido, sem markdown, "
    "sem explicações extras e sem texto fora do objeto JSON. "
    "O JSON deve seguir exatamente este formato: "
    '{"activities":[{"name":"string","description":"string","duration":30,"category":"string"}],'
    '"reasoning":"string","precautions":"string"}. '
    "Gere atividades seguras, realistas e adequadas ao perfil informado."
    "Gere ao menos duas atividades, mas não mais do que quatro. "
)}
```

- User Message: O que o usuario digita

```
{"role": "user", "content": {
    "system_message": "Gerar recomendação personalizada de bem-estar.",
    "perfil_usuario": user_profile,
    "additional_info": additional_info or "Não informado",
}}
```

- Assistent Message: As respostas anteriores do modelo, uma especie de historico do modelo

```
{
    role": "assistent", "content": "Ola pedrinho, como posso te ajudar ?"
}
```

