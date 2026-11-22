# Kit de benchmark para o XERJ Reader-1

Kit para testar o XERJ Reader-1 de forma sistemática, em vez de perguntar "no olho" no playground. Segue o método da própria
documentação ([Concepts](https://platform.xerj.ai/docs/concepts#how-to-choose-your-bar)): reunir perguntas com respostas
conhecidas (incluindo perguntas **sem** resposta no texto), rodar sem barra de confiança, comparar barras de `min_confidence`
e escolher a menor com erros aceitáveis.

> O script foi testado de ponta a ponta contra a API real na rodada de 49 perguntas (v1). A suíte `suite_pt` (v2) e o
> avaliador novo foram validados com respostas simuladas; os números reais só aparecem depois da sua primeira rodada.

## Conteúdo

```
xerj-benchmark/
├── xerj_bench.py            # harness (só biblioteca padrão do Python 3.9+)
├── compare.py               # compara duas rodadas (auto x tipado, estabilidade, antes/depois)
├── tools/
│   ├── build_suite_pt.py    # gera suite_pt/ calculando as respostas esperadas em código
│   └── redact.py            # anonimiza documentos reais antes de usá-los
├── suite/                   # v1: 49 perguntas (5 documentos), a base já rodada
├── suite_pt/                # v2, fase 1: 140 perguntas em português (11 documentos)
├── suite_real/              # seus documentos reais anonimizados (começa vazia)
└── results/                 # saída
```

## Privacidade (leia antes de rodar)

- Os documentos de `suite/` e `suite_pt/` são **fictícios**.
- O playground pode guardar e revisar o que você digita. A **API** processa em memória e não armazena, segundo a
  [página de privacidade](https://platform.xerj.ai/docs/privacy-security). É um compromisso do fornecedor, em preview e sem SLA
  nem certificação: para dados reais de terceiros, isso não basta.
- **Nunca** envie documentos de clientes, do empregador ou com dados pessoais. Para documentos reais, veja o roteiro abaixo.
- A chave fica só em variável de ambiente (`read -rs XERJ_API_KEY && export XERJ_API_KEY`). Nunca em arquivo, repositório ou chat.

## Fase 1: português

```bash
python3 xerj_bench.py --suite suite_pt --dry-run          # valida, sem gastar nada

python3 xerj_bench.py --suite suite_pt --out pt_auto      # tipos inferidos da pergunta
python3 xerj_bench.py --suite suite_pt --send-types --out pt_typed   # tipos explícitos

python3 compare.py pt_auto/results.csv pt_typed/results.csv --labels auto tipado
```

São 11 chamadas por rodada e poucos milhares de tokens: uma fração de centavo do crédito de US$ 1.

**Estabilidade.** Repita a mesma rodada 3 vezes e compare:

```bash
for i in 1 2 3; do python3 xerj_bench.py --suite suite_pt --send-types --out pt_typed_$i; done
python3 compare.py pt_typed_1/results.csv pt_typed_2/results.csv --labels r1 r2
python3 compare.py pt_typed_1/results.csv pt_typed_3/results.csv --labels r1 r3
```

Se as mesmas perguntas mudam de resposta entre rodadas idênticas, isso é um achado por si só.

### O que a `suite_pt` cobre

| Documento | Para que serve |
|---|---|
| fatura, e-mail, contrato (da v1) | Base comparável com a rodada anterior (ids F, E, C) |
| nota fiscal (DANFE) | Tabela de itens, CNPJ, ICMS, "valor da nota" contra "valor dos produtos" |
| boleto | Dois valores parecidos (documento e cobrado), juros com 3 casas decimais, prazos |
| holerite | Soma de proventos e descontos, líquido, percentuais sobre valores |
| extrato bancário | Valores negativos, saldo por data, totais de entradas e saídas, contagem |
| edital de licitação | Quantidades por extenso (500 e "quinhentas"), datas "02 de dezembro de 2026", prazos |
| ata de reunião | Duração entre horários, contagem de pessoas, datas por extenso, `ref_date` |
| contrato de aluguel | Multa em percentual, caução "3 (três) aluguéis", soma aluguel + condomínio |
| log em português | `ms` e `s` colados ao número, datas `dd/mm/aaaa`, rótulos `ERRO` e `AVISO` |

140 perguntas, 20 delas **sem resposta no texto** (14%). As respostas esperadas que dependem de conta são calculadas em
`tools/build_suite_pt.py`, não digitadas à mão. Para regerar: `python3 tools/build_suite_pt.py`.

### Como o avaliador classifica (mudou desde a v1)

Na v1, várias respostas com o conteúdo certo contaram como erro só porque vieram como texto (`R$ 4.417,97`, `20/11/2026`)
em vez de valor tipado. O avaliador agora separa:

| Resultado | Significado |
|---|---|
| `correct` | Valor tipado certo |
| `content_ok` | Conteúdo certo, mas sem valor tipado (problema de tipagem, não de leitura) |
| `wrong` | Valor incorreto |
| `missed` | Recusou, mas a resposta existia |
| `correct_decline` | Recusou uma pergunta sem resposta no texto |
| `hallucination` | Respondeu algo que não está no texto |

O `content_ok` só vale para `number`, `money`, `pct` e `date`, e só quando o texto da resposta contém **exatamente um**
número ou uma data (evita acerto por coincidência). O relatório mostra precisão **estrita** e **tolerante**, além de quantas
respostas erradas têm confiança >= 0,90, que nenhuma barra consegue filtrar.

## Documentos reais (com cuidado)

Documentos reais deixam o teste mais convincente, mas só entram na `suite_real/` se forem **públicos** ou **seus e anonimizados**.
Não sou advogado; dúvida de licença ou de LGPD, trate o documento como proibido.

**Boas fontes (públicas):**

| Fonte | O que oferece |
|---|---|
| Diário Oficial (União, estados, municípios) | Editais, extratos de contrato, portarias, atas |
| Portais de transparência e de compras públicas | Editais, atas de registro de preços, contratos |
| Demonstrações financeiras na CVM/B3 | Tabelas longas, valores em milhares, notas explicativas |
| Bulário eletrônico da Anvisa | Bulas: dosagens, contraindicações, tabelas |
| Termos de uso e políticas de privacidade | Cláusulas, prazos, condições |

Em geral, leis e atos oficiais não têm proteção de direito autoral (Lei 9.610, art. 8º), mas **público não é o mesmo que livre de
dados pessoais**: contratos e decisões costumam trazer CPF, endereços e nomes. Anonimize mesmo assim.

**Seus próprios documentos** (faturas, comprovantes, e-mails seus): serve, depois de anonimizar.
**Não use:** documentos de clientes, do empregador, de saúde ou de qualquer pessoa que não seja você.

**Roteiro:**

1. Converta para texto. PDF com texto: `pdftotext -layout arquivo.pdf saida.txt` (pacote `poppler-utils`), que roda local e não envia nada.
   PDF escaneado precisa de OCR antes (por exemplo `ocrmypdf`).
2. Anonimize: `python3 tools/redact.py saida.txt suite_real/docs/nome.txt --names "Nome 1,Nome 2"`.
   O script troca CPF, CNPJ, e-mail, telefone, CEP e chave de NF-e por valores falsos com o mesmo formato, e lista as linhas que
   ainda parecem conter dados pessoais. **Ele não é garantia.** Leia o arquivo inteiro e corrija à mão endereços, contas, RG, placas.
3. Escreva as perguntas em `suite_real/cases.csv` **olhando o documento original**, nunca a saída do próprio XERJ.
   Inclua perguntas cuja resposta não está no texto (cerca de 10 a 15% do total).
4. `python3 xerj_bench.py --suite suite_real --dry-run`, depois rode normalmente.
5. Mantenha `suite_real/` e `results*/` fora de repositórios públicos. Sugestão de `.gitignore`:

```
.env
suite_real/
results*/
pt_*/
```

## Plano de testes

1. **Playground (30 min):** exemplos prontos; teste a pergunta armadilha "Who is the CEO of Northwind Components?"
   (resposta correta: `not in the document`).
2. **Fase 1, português:** `suite_pt`, auto contra tipado, 3 repetições para estabilidade.
3. **Documentos reais em português** (`suite_real`), no mínimo 10 documentos de tipos diferentes.
4. **Fase 2, inglês:** uma suíte equivalente em inglês (mesmos tipos de documento, mesmas categorias), para comparar os dois
   idiomas com a mesma régua. Só depois dá para afirmar em qual idioma a ferramenta é mais forte.
5. **Estresse manual** (a documentação dá pistas):
   - Janela de **6.080 tokens** para documento + pergunta contra o texto que fala em documentos de até 1.000.000 de caracteres:
     teste 5 mil, 15 mil e 30 mil caracteres, em português e em inglês, e anote onde ocorre `document_too_long`.
   - Documentos acima de 16.000 caracteres seguem regras próprias (um por vez, `long_document_in_progress`, barra automática de 0,5).
   - Emoji, `\r\n` e tabelas desalinhadas (os offsets contam code points).
   - Perguntas ambíguas e conflitantes (`AMBIGUOUS`, `CONFLICT`), unidades misturadas (`UNIT_MISMATCH`), mais de 20 perguntas (`too_many_questions`).
   - Mesma chamada com o mesmo `Idempotency-Key` (deve cobrar só uma vez; confira em `/usage`).
6. **Outros endpoints:** [`/v1/extract`](https://platform.xerj.ai/docs/api-extract), [`/v1/convert`](https://platform.xerj.ai/docs/api-convert)
   e [`/v1/execute`](https://platform.xerj.ai/docs/api-execute).

## Como ler o relatório (`report.md`)

| Seção | O que mostra | O que fazer com ela |
|---|---|---|
| Resultado sem barra | Corretas, conteúdo certo sem tipo, erradas, perdidas, recusas, alucinações | Alucinação e erro com confiança alta são os mais graves |
| Varredura de `min_confidence` | Cobertura e precisão (estrita e tolerante) por barra | Escolha a menor barra cujos erros você aceita |
| Por tipo, categoria, documento e idioma | Onde a ferramenta acerta e erra | Mostra o padrão (datas por extenso, unidades, tabelas...) |
| Evidência | `quote == document[start:end]` | Abaixo de 100% é bug a reportar |
| Falhas | Lista com `request_id` | Cole direto no e-mail de feedback |

## Como estender a suíte

Edite o `cases.csv` (um caso por linha) e coloque os documentos em `docs/`.

| Coluna | Significado |
|---|---|
| `id` | Identificador único |
| `doc` | Nome do arquivo em `docs/` |
| `question` | Pergunta (até 300 caracteres) |
| `kind` | `text`, `number`, `money`, `date`, `time`, `duration`, `pct`, `yesno` ou `list`. Define a comparação e, com `--send-types`, o tipo enviado |
| `expected` | Valor esperado (regras abaixo). Vazio nos casos ABSENT |
| `expected_status` | `ANSWER` ou `ABSENT` (a resposta não está no texto) |
| `category` | Rótulo livre para o relatório |
| `lang` | `pt`, `en`... |
| `ref_date` | `YYYY-MM-DD`, opcional. Perguntas do mesmo documento com a mesma `ref_date` vão na mesma chamada |

Regras do campo `expected`:

- `number`: decimal com ponto (`4417.97`). `money`: `4417.97` ou `4417.97 BRL` (com moeda, a moeda também é conferida).
- `date`: `2026-11-20`. `yesno`: `yes` ou `no`. `list`: itens separados por `|`.
- `~texto`: aceita se o texto aparecer dentro da resposta.
- `a##b`: aceita qualquer uma das alternativas (por exemplo `14:30##14h30`).
- `pct`: aceita `2` ou `0.02` para 2%.

## Reportar os resultados

A mensagem do fundador pede: o que funcionou, o que quebrou e o que você gostaria que ele lesse a seguir. Use o `report.md`
(tabela de falhas com `request_id`, cobertura e precisão por barra, comparação auto contra tipado, estabilidade entre rodadas).
Anote também o problema de integração já encontrado: o `User-Agent` padrão do Python recebe `403 error code: 1010` do Cloudflare.
