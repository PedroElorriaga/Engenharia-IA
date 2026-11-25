- LLMs são não determinísticos: a mesma pergunta pode dar respostas diferentes.
- Ao mudar uma coisa (chunk_size, prompt, modelo, embedding), você melhora uma pergunta e piora outras 10 sem perceber.
- "Parece certo" não é número. Não dá para comparar versões, nem defender uma decisão numa entrevista.

![alt text](image.png)


#### Os três tipos de avaliador

| Tipo | Como funciona | Exemplo | Quando usar |
| :--- | :--- | :--- | :--- |
| **Baseado em código** | Regras determinísticas | "A resposta é JSON válido?", "contém o CPF mascarado?", "citou a fonte?" | Sempre que der. É barato e confiável |
| **LLM-as-judge** | Outro LLM dá nota seguindo uma rubrica | "A resposta está fiel aos documentos? Nota 1 a 5" | Qualidade semântica, que código não mede |
| **Humano** | Uma pessoa avalia | Especialista revisa 30 respostas | Para calibrar o juiz LLM e criar o gabarito |

---
#### As 4 métricas principais do RAGAS

| Métrica | Parte | Pergunta que ela responde | Precisa de gabarito? |
| :--- | :--- | :--- | :--- |
| **Context Precision** | Retrieval | Os chunks relevantes vieram no topo, ou vieram misturados com lixo? | Sim (ou não, na variante sem referência) |
| **Context Recall** | Retrieval | O retrieval trouxe tudo que era necessário para responder? | Sim |
| **Faithfulness** | Geração | Tudo que a resposta afirma está nos chunks? (detector de alucinação) | Não |
| **Answer/Response Relevancy** | Geração | A resposta responde à pergunta feita, ou enrola? | Não |
---


#### Como cada nota vira uma acao
| Nota baixa em... | Causa provável | O que mexer |
| :--- | :--- | :--- |
| **Context Precision** | Veio muito chunk irrelevante | Reranking, chunks mais focados, filtros de metadados |
| **Context Recall** | A informação existe, mas não foi buscada | Aumentar `n_results`, melhorar chunking, trocar embedding, hybrid search |
| **Faithfulness** | O LLM inventou além do contexto | Prompt mais restritivo ("responda só com base nos documentos"), temperatura menor |
| **Answer Relevancy** | A resposta foge do assunto | Ajustar o system prompt, pedir objetividade |


### Golden dataset
É o coração do eval: 50 a 100 perguntas com a resposta esperada, que você roda a cada mudança.

![alt text](image-1.png)

Como montar

- 1: Escreva umas 20 à mão lendo o regras-empresa-pedrinho.md. São as mais valiosas.
- 2: Gere o resto sinteticamente com o TestsetGenerator do RAGAS, que cria perguntas a partir dos seus documentos.
- 3: Revise tudo como humano. Pergunta sintética sem revisão vira gabarito errado.
- 4: Versione no Git (evals/golden_dataset.jsonl). O dataset evolui: todo bug encontrado em produção vira uma nova pergunta.

### LLM-as-Judge com rubrica

Para critérios que o RAGAS não cobre (tom, formato, política da empresa), você cria seu próprio juiz. O segredo é a rubrica: critérios explícitos, sem deixar o juiz "achar".

```
Você é um avaliador. Dê uma nota de 1 a 5 para a RESPOSTA do assistente da Pedrinhos Company.

5 - Correta, completa, baseada só nos documentos, cita a regra específica.
4 - Correta e baseada nos documentos, mas incompleta.
3 - Parcialmente correta, ou mistura informação não presente nos documentos.
2 - Majoritariamente incorreta ou evasiva.
1 - Incorreta, inventada, ou responde algo fora do escopo.

Se a pergunta NÃO tem resposta nos documentos, a nota 5 é dada apenas se o assistente disser que não sabe.

Responda em JSON: {"raciocinio": "...", "nota": <1-5>}
```

Armadilhas do juiz (caem em entrevista)
- Auto-preferência: um modelo tende a dar nota maior para textos dele mesmo. Use um juiz de outro modelo/família (ex.: gera com Gemini, julga com Claude ou GPT).
- Viés de verbosidade: juízes gostam de respostas longas. A rubrica precisa premiar precisão, não tamanho.
- Raciocínio antes da nota: pedir o raciocinio antes do número aumenta a consistência.
- Temperatura 0 no juiz.
- Calibração: avalie ~30 respostas você mesmo e compare com o juiz. Se ele concordar menos de ~80% com você, ajuste a rubrica. Um juiz não calibrado é só outro vibe check, com mais passos.

```
📚 Analogia: a prova com consulta

Imagine que seu RAG é um aluno fazendo uma prova com consulta ao livro.

O golden dataset é a prova com o gabarito. Sempre a mesma prova, para comparar o aluno de hoje com o de ontem.
Context Precision: o aluno abriu as páginas certas, ou perdeu tempo folheando capítulos que não tinham nada a ver?
Context Recall: ele achou todas as páginas necessárias, ou deixou de abrir uma que tinha metade da resposta?
Faithfulness: ele escreveu só o que estava no livro, ou "inventou" para parecer que sabia?
Answer Relevancy: ele respondeu a pergunta, ou escreveu uma redação bonita sobre outro assunto?
O LLM-as-judge é o professor corretor, e a rubrica é o critério de correção. Sem critério, cada professor dá uma nota diferente. E o professor não pode ser o próprio aluno, senão ele se dá 10.
A CI bloqueando o merge é a regra da escola: "tirou menos de 7, não passa de ano". Não importa se o aluno "parece inteligente" na conversa. Vale a nota.

E o melhor: se o aluno foi mal, você sabe exatamente por quê. Se abriu as páginas erradas, o problema é a busca. Se abriu as certas e mesmo assim errou, o problema é a escrita. É isso que separa "acho que melhorou" de "melhorou 12% no recall".
```