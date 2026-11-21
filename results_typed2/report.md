# XERJ Reader-1: relatório do benchmark

- Data: 2026-11-20 22:22
- Modo de tipos: explícito (--send-types)
- Perguntas: 49 (42 com resposta no texto, 7 sem resposta no texto)

## Resultado sem barra de confiança

| Resultado | Qtde |
|---|---|
| Corretas | 25 |
| Erradas (valor incorreto) | 6 |
| Perdidas (recusou, mas a resposta existia) | 11 |
| Recusas corretas (ABSENT/UNKNOWN) | 5 |
| Alucinações (respondeu algo que não está no texto) | 2 |
| Erros de API | 0 |

## Varredura da barra `min_confidence`

Cobertura = perguntas respondíveis que receberam resposta. Precisão = respostas corretas entre as dadas. Falso positivo ABSENT = respondeu uma pergunta sem resposta no texto.

| Barra | Respondidas | Corretas | Erradas | Cobertura | Precisão | Falso positivo ABSENT |
|---|---|---|---|---|---|---|
| sem barra | 33 | 25 | 8 | 74% | 76% | 29% |
| > 0.5 | 32 | 25 | 7 | 71% | 78% | 29% |
| > 0.6 | 30 | 24 | 6 | 67% | 80% | 29% |
| > 0.7 | 29 | 24 | 5 | 67% | 83% | 14% |
| > 0.8 | 29 | 24 | 5 | 67% | 83% | 14% |
| > 0.9 | 25 | 22 | 3 | 60% | 88% | 0% |
| > 0.95 | 23 | 21 | 2 | 55% | 91% | 0% |
| > 0.99 | 13 | 13 | 0 | 31% | 100% | 0% |

Menor barra testada sem nenhuma resposta errada: **> 0.99** (cobertura 31%).

## Por categoria

| Categoria | N | Corretas | Erradas | Perdidas | Recusas corretas | Alucinações |
|---|---|---|---|---|---|---|
| absent | 7 | 0 | 0 | 0 | 5 | 2 |
| compute | 6 | 4 | 2 | 0 | 0 | 0 |
| conditional | 1 | 1 | 0 | 0 | 0 | 0 |
| count | 3 | 1 | 1 | 1 | 0 | 0 |
| date_format | 3 | 2 | 0 | 1 | 0 | 0 |
| extract | 20 | 15 | 2 | 3 | 0 | 0 |
| quoted_reply | 1 | 1 | 0 | 0 | 0 | 0 |
| ref_date | 3 | 0 | 0 | 3 | 0 | 0 |
| table | 3 | 0 | 0 | 3 | 0 | 0 |
| word_number | 1 | 0 | 1 | 0 | 0 | 0 |
| yesno | 1 | 1 | 0 | 0 | 0 | 0 |

## Por idioma

| Idioma | N | Acertos (corretas + recusas corretas) |
|---|---|---|
| en | 18 | 8 (44%) |
| pt | 31 | 22 (71%) |

## Integridade da evidência, custo e latência

- Evidência íntegra (`quote == document[start:end]`): 51/51 (100%)
- Tokens: 12324 de entrada, 615 de saída. Custo estimado: US$ 0.000123 (a US$ 0.01/1M de entrada)
- Latência do servidor por pergunta (ms): p50 106, p95 185
- Latência por chamada de lote (ms): p50 2283, p95 4168

## Falhas para revisar e reportar

| ID | Categoria | Resultado | Pergunta | Esperado | Obtido | Conf. | Programa | request_id |
|---|---|---|---|---|---|---|---|---|
| L01 | count | wrong | How many ERROR lines are there? | 3 | 2 | 0.51 | AGG("COUNT", FILTER(LIST(“INFO”, “INFO”, “WARN”, “ERROR”, “ERROR”, “I… | req_atz07aactkzrx8kkrr0crcj3 |
| L03 | compute | wrong | What was the longest request duration in ms? | 2210 | 1840 | 0.50 | AGG("MAX", LIST(NUM(“1840ms”, "auto"), NUM(“920ms”, "auto"), NUM(“35m… | req_atz07aactkzrx8kkrr0crcj3 |
| L04 | extract | missed | What port does the application listen on? | 8080 | ABSENT | 0.97 | NUM(KV("d1", "Port"), "auto") → ABSENT (no label 'Port') | req_atz07aactkzrx8kkrr0crcj3 |
| L05 | extract | wrong | What was the error message of the 502 on /api/v1/tests? | ~provider timeout | AiUnavailableException | 0.87 | “AiUnavailableException” = AiUnavailableException | req_atz07aactkzrx8kkrr0crcj3 |
| L07 | extract | wrong | Which IP address triggered the rate limit warning? | 10.0.0.7 | 7 | 0.92 | “7” = 7 | req_atz07aactkzrx8kkrr0crcj3 |
| L09 | count | missed | How many requests returned status 200? | 4 | UNSUPPORTED | 0.35 | AGG("COUNT", NUM(“200”, "auto")) → UNSUPPORTED (expected Set, got Num) | req_atz07aactkzrx8kkrr0crcj3 |
| E01 | ref_date | missed | Qual é a data da reunião de alinhamento? | 2026-10-22 | UNKNOWN | 0.99 | DATE(“22 de outubro”, "auto") → UNKNOWN (no date in '22 de outubro') | req_ftxyn9p3jnebeb9jghmg1wep |
| E02 | ref_date | missed | Quantos dias separam o prazo do relatório preliminar do pra… | 14 | UNKNOWN | 0.92 | SUB(DATE(“13 de novembro”, "auto"), DATE(“30 de outubro”, "auto")) → … | req_ftxyn9p3jnebeb9jghmg1wep |
| E03 | compute | wrong | Quanto do orçamento aprovado ainda não foi liberado? | 11500.00 | 6500.00 BRL | 0.99 | MONEY(“R$ 6.500,00”, "auto") = 6500.00 BRL | req_ftxyn9p3jnebeb9jghmg1wep |
| E09 | ref_date | missed | Quantos dias faltam de hoje até o prazo do relatório prelim… | 16 | UNKNOWN | 0.84 | SUB(DATE(“30 de outubro”, "auto"), LIT("Dur", "1", "days")) → UNKNOWN… | req_ftxyn9p3jnebeb9jghmg1wep |
| C03 | extract | missed | Qual é o prazo de aviso prévio para rescisão? | ~30 | UNKNOWN | 1.00 | DUR(“30 dias”) → UNKNOWN (no duration unit in '30 dias' (give the uni… | req_gbmp6msqkf7mehq1tb8da5bm |
| C04 | word_number | wrong | Qual é o valor da multa por rescisão sem aviso prévio, em r… | 14400.00 | 216000.00 BRL | 0.99 | MUL(MONEY(“R$ 7.200,00”, "auto"), NUM(“30 dias”, "auto")) = 216000.00… | req_gbmp6msqkf7mehq1tb8da5bm |
| C05 | extract | missed | Por quantos anos vale a confidencialidade após o término? | 5 | UNKNOWN | 0.92 | DUR(“5 anos”) → UNKNOWN (no duration unit in '5 anos' (give the unit … | req_gbmp6msqkf7mehq1tb8da5bm |
| C07 | date_format | missed | Qual é a data de início da vigência? | 2026-02-01 | AMBIGUOUS | 1.00 | DATE(“01/02/2026”, "auto") → AMBIGUOUS (1/2: day-month order not deci… | req_gbmp6msqkf7mehq1tb8da5bm |
| C08 | absent | hallucination | O contrato permite subcontratação? | ABSENT | no | 0.83 | YN(false, “Fica eleito o foro da comarca de São Luís - MA.”) = no | req_gbmp6msqkf7mehq1tb8da5bm |
| R01 | table | missed | What is the default value of RATE_LIMIT_RPM? | 10 | ABSENT | 0.99 | NUM(KV("d1", "RATE_LIMIT_RPM"), "auto") → ABSENT (no label 'RATE_LIMI… | req_md39h9ph22mfa2gg6nq9hsqq |
| R02 | table | missed | What is the default AI model? | llama-3.3-70b-versatile | ABSENT | 0.98 | KV("d1", "Default") → ABSENT (no label 'Default') | req_md39h9ph22mfa2gg6nq9hsqq |
| R07 | table | missed | What is the default port? | 8080 | ABSENT | 0.98 | NUM(KV("d1", "Port"), "auto") → ABSENT (no label 'Port') | req_md39h9ph22mfa2gg6nq9hsqq |
| R08 | absent | hallucination | Does the application support OAuth login? | ABSENT | no | 0.63 | IN(LIT("Text", "OAuth login"), EACH(ROWS(PARSE(“\| Variable \| Defaul… | req_md39h9ph22mfa2gg6nq9hsqq |

Use o `request_id` ao reportar um problema ao fundador: ele localiza a chamada exata.
