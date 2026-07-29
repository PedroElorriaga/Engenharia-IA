### Explicando o que é o CrewAI com minhas palavras (Exercício de fixação):
Pelo o que eu entendi, é uma plataforma que permite a criação de agentes de IA que podem interagir entre si e com o usuário. Esses agentes podem ser configurados para realizar tarefas específicas, responder perguntas, ou até mesmo colaborar em projetos complexos. A ideia é que cada agente tenha suas próprias habilidades e conhecimentos, e eles possam se comunicar para alcançar objetivos comuns.



### Explicando o projeto com minhas palavras (Exercício de fixação):
1- Criamos os agentes em agents.py, cada agente com sua funcao e objetivo (Podemos usar uma LLM diferente para cada agente tambem) e suas tools

2- Criamos as tarefas em tasks.py, para definir o que deve ser feito, qual resultado esperado e qual agente responsavel pela tarefa e a resposta de uma tarefa pode ser utilizada como contexto para uma outra tarefa

3- Juntamos tudo isso em uma equipe, o crew.py, onde inicializamos um objeto que ira atribuir oa agentes, as tarefas e outros atributos como por exemplo verbose = True, para imprimir o que o agente esta raciocinando

4- Por fim juntamos tudo isso na main e geramos um relatorio com o resultado final