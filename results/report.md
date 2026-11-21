# XERJ Reader-1: relatório do benchmark

- Data: 2026-11-20 21:04
- Modo de tipos: automático (inferido da pergunta)
- Perguntas: 49 (42 com resposta no texto, 7 sem resposta no texto)

## Resultado sem barra de confiança

| Resultado | Qtde |
|---|---|
| Corretas | 0 |
| Erradas (valor incorreto) | 0 |
| Perdidas (recusou, mas a resposta existia) | 0 |
| Recusas corretas (ABSENT/UNKNOWN) | 0 |
| Alucinações (respondeu algo que não está no texto) | 0 |
| Erros de API | 49 |

## Varredura da barra `min_confidence`

Cobertura = perguntas respondíveis que receberam resposta. Precisão = respostas corretas entre as dadas. Falso positivo ABSENT = respondeu uma pergunta sem resposta no texto.

| Barra | Respondidas | Corretas | Erradas | Cobertura | Precisão | Falso positivo ABSENT |
|---|---|---|---|---|---|---|
| sem barra | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.5 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.6 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.7 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.8 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.9 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.95 | 0 | 0 | 0 | 0% | 0% | 0% |
| > 0.99 | 0 | 0 | 0 | 0% | 0% | 0% |

Nenhuma das barras testadas eliminou todas as respostas erradas.

## Por categoria

| Categoria | N | Corretas | Erradas | Perdidas | Recusas corretas | Alucinações |
|---|---|---|---|---|---|---|
| absent | 7 | 0 | 0 | 0 | 0 | 0 |
| compute | 6 | 0 | 0 | 0 | 0 | 0 |
| conditional | 1 | 0 | 0 | 0 | 0 | 0 |
| count | 3 | 0 | 0 | 0 | 0 | 0 |
| date_format | 3 | 0 | 0 | 0 | 0 | 0 |
| extract | 20 | 0 | 0 | 0 | 0 | 0 |
| quoted_reply | 1 | 0 | 0 | 0 | 0 | 0 |
| ref_date | 3 | 0 | 0 | 0 | 0 | 0 |
| table | 3 | 0 | 0 | 0 | 0 | 0 |
| word_number | 1 | 0 | 0 | 0 | 0 | 0 |
| yesno | 1 | 0 | 0 | 0 | 0 | 0 |

## Por idioma

| Idioma | N | Acertos (corretas + recusas corretas) |
|---|---|---|
| en | 18 | 0 (0%) |
| pt | 31 | 0 (0%) |

## Integridade da evidência, custo e latência

- Evidência íntegra (`quote == document[start:end]`): 0/0
- Tokens: 0 de entrada, 0 de saída. Custo estimado: US$ 0.000000 (a US$ 0.01/1M de entrada)
- Latência do servidor por pergunta (ms): p50 0, p95 0
- Latência por chamada de lote (ms): p50 242, p95 354

## Falhas para revisar e reportar

| ID | Categoria | Resultado | Pergunta | Esperado | Obtido | Conf. | Programa | request_id |
|---|---|---|---|---|---|---|---|---|
| F01 | extract | error | Qual é o número da fatura? | 2026-00731 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F02 | extract | error | Qual é o valor total a pagar? | 4417.97 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F03 | date_format | error | Qual é a data de vencimento? | 2026-11-20 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F04 | date_format | error | Qual é a data de emissão? | 2026-11-05 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F05 | compute | error | Quantos dias há entre a emissão e o vencimento? | 15 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F06 | extract | error | Qual é o número do pedido de compra? | PC-8841 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F07 | extract | error | Qual é o CNPJ do emitente? | 12.345.678/0001-90 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F08 | compute | error | Qual é a diferença entre o subtotal e o total a pagar? | 232.53 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F09 | yesno | error | A fatura aceita pagamento por cartão de crédito? | no | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F10 | absent | error | Quem é o diretor financeiro do cliente? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F11 | extract | error | Qual é o percentual da multa por atraso? | 2 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| F12 | compute | error | Qual é a soma dos itens de licença e suporte técnico? | 3850.50 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L01 | count | error | How many ERROR lines are there? | 3 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L02 | extract | error | At what time did the first ERROR occur? | 09:17:55##9:17:55 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L03 | compute | error | What was the longest request duration in ms? | 2210 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L04 | extract | error | What port does the application listen on? | 8080 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L05 | extract | error | What was the error message of the 502 on /api/v1/tests? | ~provider timeout | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L06 | extract | error | At what time was the invalid api key error fixed? | 09:24##09:24:00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L07 | extract | error | Which IP address triggered the rate limit warning? | 10.0.0.7 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L08 | absent | error | Who deployed the fix? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| L09 | count | error | How many requests returned status 200? | 4 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E01 | ref_date | error | Qual é a data da reunião de alinhamento? | 2026-10-22 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E02 | ref_date | error | Quantos dias separam o prazo do relatório preliminar do pra… | 14 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E03 | compute | error | Quanto do orçamento aprovado ainda não foi liberado? | 11500.00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E04 | extract | error | Em que sala será a reunião? | ~3 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E05 | conditional | error | Quem vai apresentar os resultados? | Marcos | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E06 | extract | error | A que horas começa a reunião? | 14:30##14h30##14:30:00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E07 | quoted_reply | error | Quem sugeriu marcar a reunião na quarta-feira? | Thiago | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E08 | absent | error | Qual é o telefone da Carla? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| E09 | ref_date | error | Quantos dias faltam de hoje até o prazo do relatório prelim… | 16 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C01 | extract | error | Qual é o valor mensal do contrato? | 7200.00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C02 | extract | error | Qual é a duração do contrato? | ~12 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C03 | extract | error | Qual é o prazo de aviso prévio para rescisão? | ~30 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C04 | word_number | error | Qual é o valor da multa por rescisão sem aviso prévio, em r… | 14400.00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C05 | extract | error | Por quantos anos vale a confidencialidade após o término? | 5 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C06 | extract | error | Qual é o foro eleito? | ~São Luís | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C07 | date_format | error | Qual é a data de início da vigência? | 2026-02-01 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C08 | absent | error | O contrato permite subcontratação? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C09 | compute | error | Qual é o valor total pago em 12 meses? | 86400.00 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| C10 | absent | error | Qual é o nome da CONTRATANTE? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R01 | table | error | What is the default value of RATE_LIMIT_RPM? | 10 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R02 | table | error | What is the default AI model? | llama-3.3-70b-versatile | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R03 | extract | error | Which HTTP status code means the provider failed? | 502 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R04 | extract | error | What is the maximum number of characters accepted per reque… | 8000 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R05 | extract | error | Which license does the application use? | MIT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R06 | count | error | How many variables are listed in the table? | 5 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R07 | table | error | What is the default port? | 8080 | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R08 | absent | error | Does the application support OAuth login? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |
| R09 | absent | error | Who maintains the project? | ABSENT | ERROR | 0.00 | HTTP 403: error code: 1010 |  |

Use o `request_id` ao reportar um problema ao fundador: ele localiza a chamada exata.
