#!/usr/bin/env python3
"""
redact.py - anonimiza um documento de texto ANTES de usá-lo em testes.

Troca CPF, CNPJ, e-mails, telefones, CEP e chaves de NF-e por valores falsos que
PRESERVAM O FORMATO (assim o teste continua realista). O mesmo valor original vira
sempre o mesmo valor falso dentro do documento. Nomes de pessoas não são detectáveis
automaticamente: informe-os em --names.

ATENÇÃO: a anonimização automática NÃO é garantia. Leia o resultado inteiro antes de usar.
Dados que o script não reconhece (endereços, números de conta e agência, nomes de empresas,
placas, RG, datas de nascimento, linha digitável de boleto) precisam ser revisados à mão.
Nenhum arquivo com o mapeamento original -> falso é gravado.

Uso:
  python3 tools/redact.py original.txt saida.txt --names "João da Silva,Maria Souza"
"""
import argparse
import random
import re
import sys
from pathlib import Path

PATTERNS = [
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("CNPJ", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")),
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("telefone", re.compile(r"(?:\(\d{2}\)|\b\d{2})\s?9?\d{4}-\d{4}\b")),
    ("CEP", re.compile(r"\b\d{5}-\d{3}\b")),
    ("chave NF-e", re.compile(r"\b(?:\d{4}\s?){10}\d{4}\b")),
]
SUSPECT = re.compile(r"\b(CPF|RG|CNH|Ag[eê]ncia|Conta|PIX|Chave|Passaporte|Nascimento|Endere[cç]o|Rua|Av\.|Avenida)\b",
                     re.IGNORECASE)


def fake_like(value, rng):
    """Troca cada dígito por outro, mantendo pontuação e tamanho."""
    return "".join(str(rng.randint(0, 9)) if ch.isdigit() else ch for ch in value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--names", default="", help='nomes separados por vírgula: "Ana Lima,Bruno Costa"')
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    text = Path(args.entrada).read_text(encoding="utf-8")
    rng = random.Random(args.seed)
    seen, counts = {}, {}

    def make_sub(label):
        def sub(m):
            orig = m.group(0)
            if orig not in seen:
                if label == "e-mail":
                    seen[orig] = f"pessoa{len(seen) + 1}@exemplo.com"
                else:
                    seen[orig] = fake_like(orig, rng)
            counts[label] = counts.get(label, 0) + 1
            return seen[orig]
        return sub

    for label, pat in PATTERNS:
        text = pat.sub(make_sub(label), text)

    names = [n.strip() for n in args.names.split(",") if n.strip()]
    for idx, name in enumerate(names):
        replacement = f"Pessoa {chr(65 + idx % 26)}"
        text, n = re.subn(re.escape(name), replacement, text, flags=re.IGNORECASE)
        counts[f"nome '{name}'"] = n

    Path(args.saida).write_text(text, encoding="utf-8")
    print("Substituições feitas:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    if not counts:
        print("  nenhuma")

    print("\nREVISE À MÃO. Trechos que ainda podem conter dados pessoais:")
    found = 0
    for no, line in enumerate(text.splitlines(), 1):
        long_digits = re.search(r"\d{9,}", re.sub(r"[\s.\-/]", "", line))
        if SUSPECT.search(line) or long_digits:
            print(f"  linha {no}: {line.strip()[:110]}")
            found += 1
    if not found:
        print("  nada suspeito encontrado (isso não é garantia)")
    print(f"\nArquivo gravado em {args.saida}. Leia-o inteiro antes de usar.")


if __name__ == "__main__":
    sys.exit(main())
