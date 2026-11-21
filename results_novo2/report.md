# XERJ Reader-1: relatório do benchmark

- Data: 2026-11-20 21:57
- Modo de tipos: automático (inferido da pergunta)
- Perguntas: 49 (42 com resposta no texto, 7 sem resposta no texto)

## Resultado sem barra de confiança

| Resultado | Qtde |
|---|---|
| Corretas | 13 |
| Erradas (valor incorreto) | 14 |
| Perdidas (recusou, mas a resposta existia) | 15 |
| Recusas corretas (ABSENT/UNKNOWN) | 6 |
| Alucinações (respondeu algo que não está no texto) | 1 |
| Erros de API | 0 |

## Varredura da barra `min_confidence`

Cobertura = perguntas respondíveis que receberam resposta. Precisão = respostas corretas entre as dadas. Falso positivo ABSENT = respondeu uma pergunta sem resposta no texto.

| Barra | Respondidas | Corretas | Erradas | Cobertura | Precisão | Falso positivo ABSENT |
|---|---|---|---|---|---|---|
| sem barra | 28 | 13 | 15 | 64% | 46% | 14% |
| > 0.5 | 28 | 13 | 15 | 64% | 46% | 14% |
| > 0.6 | 24 | 12 | 12 | 55% | 50% | 14% |
| > 0.7 | 23 | 12 | 11 | 55% | 52% | 0% |
| > 0.8 | 23 | 12 | 11 | 55% | 52% | 0% |
| > 0.9 | 19 | 11 | 8 | 45% | 58% | 0% |
| > 0.95 | 16 | 10 | 6 | 38% | 62% | 0% |
| > 0.99 | 9 | 6 | 3 | 21% | 67% | 0% |

Nenhuma das barras testadas eliminou todas as respostas erradas.

## Por categoria

| Categoria | N | Corretas | Erradas | Perdidas | Recusas corretas | Alucinações |
|---|---|---|---|---|---|---|
| absent | 7 | 0 | 0 | 0 | 6 | 1 |
| compute | 6 | 0 | 2 | 4 | 0 | 0 |
| conditional | 1 | 1 | 0 | 0 | 0 | 0 |
| count | 3 | 1 | 1 | 1 | 0 | 0 |
| date_format | 3 | 0 | 3 | 0 | 0 | 0 |
| extract | 20 | 10 | 7 | 3 | 0 | 0 |
| quoted_reply | 1 | 1 | 0 | 0 | 0 | 0 |
| ref_date | 3 | 0 | 1 | 2 | 0 | 0 |
| table | 3 | 0 | 0 | 3 | 0 | 0 |
| word_number | 1 | 0 | 0 | 1 | 0 | 0 |
| yesno | 1 | 0 | 0 | 1 | 0 | 0 |

## Por idioma

| Idioma | N | Acertos (corretas + recusas corretas) |
|---|---|---|
| en | 18 | 7 (39%) |
| pt | 31 | 12 (39%) |

## Integridade da evidência, custo e latência

- Evidência íntegra (`quote == document[start:end]`): 43/43 (100%)
- Tokens: 12324 de entrada, 576 de saída. Custo estimado: US$ 0.000123 (a US$ 0.01/1M de entrada)
- Latência do servidor por pergunta (ms): p50 143, p95 188
- Latência por chamada de lote (ms): p50 2499, p95 2628

## Falhas para revisar e reportar

| ID | Categoria | Resultado | Pergunta | Esperado | Obtido | Conf. | Programa | request_id |
|---|---|---|---|---|---|---|---|---|
| F02 | extract | wrong | Qual é o valor total a pagar? | 4417.97 | R$ 4.417,97 | 0.95 | “R$ 4.417,97” = R$ 4.417,97 | req_zsa65rketcbr8dak10rbse9c |
| F03 | date_format | wrong | Qual é a data de vencimento? | 2026-11-20 | 20/11/2026 | 0.89 | “20/11/2026” = 20/11/2026 | req_zsa65rketcbr8dak10rbse9c |
| F04 | date_format | wrong | Qual é a data de emissão? | 2026-11-05 | 05/11/2026 | 0.99 | KV("d1", "Data de emissão") = 05/11/2026 | req_zsa65rketcbr8dak10rbse9c |
| F05 | compute | missed | Quantos dias há entre a emissão e o vencimento? | 15 | UNSUPPORTED | 0.99 | SUB(DATE(“20/11/2026”, "auto"), DATE(“05/11/2026”, "auto")) → UNSUPPO… | req_zsa65rketcbr8dak10rbse9c |
| F06 | extract | missed | Qual é o número do pedido de compra? | PC-8841 | UNSUPPORTED | 0.70 | IN(“PC-8841”, "compras") → UNSUPPORTED (codelist compras) | req_zsa65rketcbr8dak10rbse9c |
| F07 | extract | wrong | Qual é o CNPJ do emitente? | 12.345.678/0001-90 | no | 0.53 | EQ(“12.345.678/0001-90”, LIT("Text", "12345678/0001-90")) = no | req_zsa65rketcbr8dak10rbse9c |
| F08 | compute | wrong | Qual é a diferença entre o subtotal e o total a pagar? | 232.53 | Total a pagar | 0.90 | ARGMIN(LIST(PAIR(“Subtotal”, MONEY(“R$ 4.650,50”, "auto")), PAIR(“Tot… | req_zsa65rketcbr8dak10rbse9c |
| F09 | yesno | missed | A fatura aceita pagamento por cartão de crédito? | no | ABSENT | 0.99 | DECLINE("ABSENT") → ABSENT (declined by the program) | req_zsa65rketcbr8dak10rbse9c |
| F12 | compute | missed | Qual é a soma dos itens de licença e suporte técnico? | 3850.50 | ABSENT | 0.99 | DECLINE("ABSENT") → ABSENT (declined by the program) | req_zsa65rketcbr8dak10rbse9c |
| L01 | count | wrong | How many ERROR lines are there? | 3 | 2 | 0.51 | AGG("COUNT", FILTER(LIST(“INFO”, “INFO”, “WARN”, “ERROR”, “ERROR”, “I… | req_r47ew9zrm3efv4ftm5xyd3ka |
| L03 | compute | missed | What was the longest request duration in ms? | 2210 | UNKNOWN | 0.57 | AGG("MAX", LIST(DUR(“1840ms”), DUR(“920ms”), DUR(“35ms”))) → UNKNOWN … | req_r47ew9zrm3efv4ftm5xyd3ka |
| L04 | extract | missed | What port does the application listen on? | 8080 | ABSENT | 0.99 | KV("d1", "Port") → ABSENT (no label 'Port') | req_r47ew9zrm3efv4ftm5xyd3ka |
| L05 | extract | wrong | What was the error message of the 502 on /api/v1/tests? | ~provider timeout | AiUnavailableException | 0.87 | “AiUnavailableException” = AiUnavailableException | req_r47ew9zrm3efv4ftm5xyd3ka |
| L07 | extract | wrong | Which IP address triggered the rate limit warning? | 10.0.0.7 | 7 | 0.92 | “7” = 7 | req_r47ew9zrm3efv4ftm5xyd3ka |
| L09 | count | missed | How many requests returned status 200? | 4 | UNSUPPORTED | 0.35 | AGG("COUNT", NUM(“200”, "auto")) → UNSUPPORTED (expected Set, got Num) | req_r47ew9zrm3efv4ftm5xyd3ka |
| E01 | ref_date | wrong | Qual é a data da reunião de alinhamento? | 2026-10-22 | dia 22 de outubro | 0.91 | “dia 22 de outubro” = dia 22 de outubro | req_nf3jmg48gf5vak5nxqcwv61w |
| E02 | ref_date | missed | Quantos dias separam o prazo do relatório preliminar do pra… | 14 | UNKNOWN | 0.62 | EQ(SUB(DATE(“13 de novembro”, "auto"), DATE(“30 de outubro”, "auto"))… | req_nf3jmg48gf5vak5nxqcwv61w |
| E03 | compute | wrong | Quanto do orçamento aprovado ainda não foi liberado? | 11500.00 | no | 0.54 | YN(false, “O orçamento aprovado é de R$ 18.00…is R$ 6.500,00 já foram… | req_nf3jmg48gf5vak5nxqcwv61w |
| E09 | ref_date | missed | Quantos dias faltam de hoje até o prazo do relatório prelim… | 16 | UNKNOWN | 0.82 | LE(SUB(DATE(“30 de outubro”, "auto"), DATE(“30 de outubro”, "auto")),… | req_nf3jmg48gf5vak5nxqcwv61w |
| C01 | extract | wrong | Qual é o valor mensal do contrato? | 7200.00 | yes | 1.00 | YN(true, “O valor mensal é de R$ 7.200,00, p…até o quinto dia útil de… | req_mj0sdbrba4qxfyaxk9k87400 |
| C02 | extract | wrong | Qual é a duração do contrato? | ~12 | yes | 0.97 | YN(true, “O contrato tem vigência de 12 mese…2026, renovável por igua… | req_mj0sdbrba4qxfyaxk9k87400 |
| C04 | word_number | missed | Qual é o valor da multa por rescisão sem aviso prévio, em r… | 14400.00 | ABSENT | 1.00 | DECLINE("ABSENT") → ABSENT (declined by the program) | req_mj0sdbrba4qxfyaxk9k87400 |
| C05 | extract | wrong | Por quantos anos vale a confidencialidade após o término? | 5 | 5 anos | 1.00 | “5 anos” = 5 anos | req_mj0sdbrba4qxfyaxk9k87400 |
| C07 | date_format | wrong | Qual é a data de início da vigência? | 2026-02-01 | 01/02/2026 | 1.00 | “01/02/2026” = 01/02/2026 | req_mj0sdbrba4qxfyaxk9k87400 |
| C09 | compute | missed | Qual é o valor total pago em 12 meses? | 86400.00 | ABSENT | 1.00 | DECLINE("ABSENT") → ABSENT (declined by the program) | req_mj0sdbrba4qxfyaxk9k87400 |
| R01 | table | missed | What is the default value of RATE_LIMIT_RPM? | 10 | ABSENT | 0.99 | KV("d1", "RATE_LIMIT_RPM") → ABSENT (no label 'RATE_LIMIT_RPM') | req_90rg8v2ben6mfjf4vbbg83x8 |
| R02 | table | missed | What is the default AI model? | llama-3.3-70b-versatile | ABSENT | 0.98 | KV("d1", "Default") → ABSENT (no label 'Default') | req_90rg8v2ben6mfjf4vbbg83x8 |
| R03 | extract | missed | Which HTTP status code means the provider failed? | 502 | UNSUPPORTED | 0.49 | NUM(“400”, "auto") → UNSUPPORTED (program returns Num, field is text) | req_90rg8v2ben6mfjf4vbbg83x8 |
| R07 | table | missed | What is the default port? | 8080 | ABSENT | 0.95 | KV("d1", "Port") → ABSENT (no label 'Port') | req_90rg8v2ben6mfjf4vbbg83x8 |
| R08 | absent | hallucination | Does the application support OAuth login? | ABSENT | no | 0.63 | IN(LIT("Text", "OAuth login"), EACH(ROWS(PARSE(“\| Variable \| Defaul… | req_90rg8v2ben6mfjf4vbbg83x8 |

Use o `request_id` ao reportar um problema ao fundador: ele localiza a chamada exata.
