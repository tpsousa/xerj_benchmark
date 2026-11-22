# suite_real

Coloque aqui documentos reais ANONIMIZADOS (`docs/`) e as perguntas (`cases.csv`, mesmas colunas das outras suítes).

Antes de qualquer arquivo entrar nesta pasta:

1. Anonimize com `python3 tools/redact.py original.txt suite_real/docs/nome.txt --names "..."` e leia o resultado inteiro.
2. Escreva as perguntas e os valores esperados olhando o documento ORIGINAL, nunca a saída de uma ferramenta.
3. Rode `python3 xerj_bench.py --suite suite_real --dry-run` para validar.

Esta pasta não deve ir para um repositório público. Ela está no `.gitignore` sugerido no README principal.
