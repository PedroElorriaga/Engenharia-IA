### Para executar o projeto, siga os passos abaixo:

Rodar o server FastAPI:

```bash
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

---

Rodar os testes unitários:
```bash
uv run python -m unittest discover -s 'e:\Projetos-code\JornadaPica\7-FASTAPI-LLM' -v
```

---

Para rodar pelo powershell sem esconder colunas, utilize o seguinte comando:
```bash
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8001/ask -ContentType 'application/json' -Body '{"question":"How do I reverse a list in Python?"}' | ConvertTo-Json
```
Percebe que adicionei esse **| ConvertTo-Json** no final do comando para formatar a saída como JSON no PowerShell.


### Explicando api com minhas palavras (Exercício de fixação):

1- Temos dois endpoints principais, o /health (Que verifica a saude da nossa IA, sempre retorna OK por questao de simplicidade) e o /ask (que de fato onde enviamos a requisicao, seguindo o contrato definido nos parametros de payload)

2- Ao fazer uma requisicao no metodo POST /ask, é inicializado um contador perf_counter() para mensurar a performance do tempo de inicio ate a resposta

3- chamamos o metodo para inicializar o modelo _call_model_with_retry, passando os parametros e o historico se existir (Sei que existe uma forma mais estruturada para manter o historico, utilizando checkpointer e tudo mais) com mais dois parametros padroes na funcao, como o timeout e o retries

4- Entao o modelo é iniciado, usamos o ChatOllama, onde passamos mais alguns parametros de inicializacao tambem

5- Guardamos em um variavel as mensagens estruturadas com suas roles (Human, Ai) e entao iteramos sob as tentativas, para que caso o sistema falhar ele nao fique em loop

6- Invokamos a llm ChatOllama passando as mensagens estruturadas e caso o tempo de execucao for maior que o timeout definido, nos retornamos um erro de timeout

7- Apos o retorno estruturamos a resposta com base no contrato do AskResponse que tambem definimos onde trazemos a resposta, o tempo de resposta e o modelo utilizado