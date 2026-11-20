# Kit de benchmark para o XERJ Reader-1

Kit para testar o XERJ Reader-1 de forma sistemática, em vez de perguntar "no olho" no playground.
Segue o método recomendado pela própria documentação ([Concepts](https://platform.xerj.ai/docs/concepts#how-to-choose-your-bar)):
reunir perguntas com respostas conhecidas (incluindo perguntas **sem** resposta no texto), rodar sem barra de confiança,
comparar barras de `min_confidence` e escolher a menor com erros aceitáveis.

> O script foi testado de ponta a ponta apenas contra um servidor simulado local. Ainda não rodou contra a API real.
> Se algo falhar no primeiro uso, o problema mais provável é um detalhe do formato de resposta; veja `results/raw.jsonl`.

## Conteúdo

```
xerj-benchmark/
├── xerj_bench.py          # harness (só biblioteca padrão do Python 3.9+)
├── suite/
│   ├── cases.csv          # 49 perguntas com respostas esperadas
│   └── docs/              # 5 documentos: fatura, e-mail, contrato (pt-BR), log e README (en)
└── results/               # saída (raw.jsonl, results.csv, report.md)
```

## Privacidade (leia antes de rodar)

- Os documentos do kit são **fictícios ou sem dados sensíveis**. Mantenha assim ao criar os seus.
- O playground pode guardar e revisar o que você digita. A **API** processa em memória e não armazena, segundo a
  [página de privacidade](https://platform.xerj.ai/docs/privacy-security). Esse é um compromisso do fornecedor,
  em fase de preview e sem SLA nem certificação: não envie documentos de clientes ou dados pessoais reais.
- A chave fica só em variável de ambiente. Nunca em arquivo, repositório ou chat.

## Como rodar

```bash
# 1. gerar uma chave em https://platform.xerj.ai/keys (aparece uma única vez)
export XERJ_API_KEY="xerj_..."

# 2. validar a suíte sem gastar nada
python3 xerj_bench.py --dry-run

# 3. rodar com tipos automáticos (inferidos da pergunta)
python3 xerj_bench.py --out results_auto

# 4. rodar de novo com tipos explícitos e comparar
python3 xerj_bench.py --send-types --out results_typed
```

São 5 chamadas de API por rodada e cerca de 20 mil tokens de entrada, ou seja, uma fração de centavo do crédito de US$ 1.
O limite é de 60 requisições por minuto por conta, e o script já reenvia em 429/503 respeitando `retry-after`.

## Como ler o relatório (`report.md`)

| Seção | O que mostra | O que fazer com ela |
|---|---|---|
| Resultado sem barra | Corretas, erradas, perdidas, recusas corretas, alucinações | Alucinação (respondeu algo que não está no texto) é o erro mais grave |
| Varredura de `min_confidence` | Cobertura e precisão para cada barra | Escolha a menor barra cujas respostas erradas você aceita |
| Por categoria | Onde o modelo acerta e erra | Mostra o padrão: contas, datas, perguntas sem resposta etc. |
| Por idioma | pt-BR contra inglês | Dado valioso para o fundador, que provavelmente treinou mais em inglês |
| Evidência | `quote == document[start:end]` | Qualquer valor abaixo de 100% é bug a reportar |
| Falhas | Lista com `request_id` | Cole direto no e-mail de feedback |

## Plano de testes sugerido

1. **Playground (30 min):** rode os exemplos prontos e observe fórmula, citações e passos. Teste a pergunta armadilha
   "Who is the CEO of Northwind Components?", cuja resposta correta é `not in the document`.
2. **Benchmark base:** rode este kit com tipos automáticos e depois explícitos. Compare.
3. **Sua suíte:** copie `suite/` e acrescente 50 a 100 perguntas sobre documentos seus **sem dados sensíveis**
   (README e logs de projetos próprios, faturas suas com campos apagados, e-mails fictícios).
4. **Testes de estresse manuais** (a documentação dá pistas de onde procurar):
   - A página da API diz que documento e pergunta devem caber em uma **janela de 6.080 tokens**, mas a visão geral fala em
     documentos de até 1.000.000 de caracteres. Teste documentos de 5 mil, 15 mil e 30 mil caracteres, em português e em
     inglês (português usa mais tokens por caractere), e anote onde ocorre `document_too_long` ou perda de qualidade.
   - Documentos acima de 16.000 caracteres seguem regras próprias: sem fila de espera, só um por vez (`long_document_in_progress`)
     e barra automática de 0,5.
   - Emoji, `\r\n` e texto com tabelas desalinhadas (os offsets contam code points).
   - `ref_date`: documentos com datas sem ano e perguntas com "hoje".
   - Perguntas ambíguas e conflitantes (status `AMBIGUOUS` e `CONFLICT`).
   - Unidades e moedas misturadas (esperado `UNIT_MISMATCH`).
   - Mais de 20 perguntas por chamada (esperado `too_many_questions`).
   - Mesma chamada repetida com o mesmo `Idempotency-Key` (deve cobrar só uma vez; confira em `/usage`).
5. **Outros endpoints:** [`/v1/extract`](https://platform.xerj.ai/docs/api-extract) (vários campos de uma fatura de uma vez),
   [`/v1/convert`](https://platform.xerj.ai/docs/api-convert) (PDF e Word para texto; PDF escaneado precisa de OCR antes)
   e [`/v1/execute`](https://platform.xerj.ai/docs/api-execute) (reexecutar e editar um programa sem gastar tokens).

## Como estender a suíte

Edite `suite/cases.csv` (um caso por linha) e coloque os documentos em `suite/docs/`.

| Coluna | Significado |
|---|---|
| `id` | Identificador único |
| `doc` | Nome do arquivo em `suite/docs/` |
| `question` | Pergunta (até 300 caracteres) |
| `kind` | `text`, `number`, `money`, `date`, `time`, `duration`, `pct`, `yesno` ou `list`. Define como a resposta é comparada e, com `--send-types`, o tipo enviado |
| `expected` | Valor esperado. Veja as regras abaixo. Vazio nos casos ABSENT |
| `expected_status` | `ANSWER` ou `ABSENT` (a resposta não está no texto) |
| `category` | Rótulo livre para o relatório (extract, compute, absent...) |
| `lang` | `pt`, `en`... |
| `ref_date` | `YYYY-MM-DD`, opcional. Perguntas com a mesma `ref_date` e documento vão na mesma chamada |

Regras do campo `expected`:

- `number`: valor decimal com ponto (`4417.97`). `money`: `4417.97` ou `4417.97 BRL` (com moeda, a moeda também é conferida).
- `date`: `2026-11-20`. `yesno`: `yes` ou `no`. `list`: itens separados por `|`.
- `~texto`: aceita se o texto aparecer dentro da resposta (útil quando a resposta pode vir com palavras a mais).
- `a##b`: aceita qualquer uma das alternativas (por exemplo `14:30##14h30`).
- `pct`: aceita `2` ou `0.02` para 2%.

As respostas esperadas do kit foram calculadas e conferidas por mim com base nos textos; confira também antes de tirar conclusões
(por exemplo, F09 e E05 envolvem interpretação e podem ser discutíveis).

## Reportar os resultados

A mensagem do fundador pede três coisas: o que funcionou, o que quebrou e o que você gostaria que ele lesse a seguir.
Use o `report.md`: cole a tabela de falhas (com `request_id`), os números de cobertura e precisão por barra, e a comparação
pt-BR contra inglês. Sugestões do que ler a seguir: logs de aplicação, PDFs de notas fiscais (depois do `/convert`),
e-mails com respostas citadas e documentos em português com valores no formato `R$ 1.234,56`.
