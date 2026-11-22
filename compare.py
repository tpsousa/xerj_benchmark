#!/usr/bin/env python3
"""
compare.py - compara duas rodadas do benchmark (results.csv).

Serve para três coisas:
  1. auto contra tipos explícitos (mesma suíte, --send-types);
  2. estabilidade: a MESMA rodada repetida deve dar o MESMO resultado;
  3. antes/depois de uma mudança do fornecedor (nova versão do modelo).

Uso:
  python3 compare.py results_novo2/results.csv results_typed2/results.csv
  python3 compare.py rodada1/results.csv rodada2/results.csv --labels "rodada 1" "rodada 2"
"""
import argparse
import csv
from collections import Counter

GOOD = {"correct", "content_ok", "correct_decline"}


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--labels", nargs=2, default=["A", "B"])
    args = ap.parse_args()
    la, lb = args.labels
    a, b = load(args.a), load(args.b)
    ids = [i for i in a if i in b]
    if not ids:
        raise SystemExit("Nenhum id em comum entre os dois arquivos.")

    same_outcome = [i for i in ids if a[i]["outcome"] == b[i]["outcome"]]
    same_value = [i for i in ids if a[i]["value_text"] == b[i]["value_text"] and a[i]["status"] == b[i]["status"]]
    print(f"Perguntas em comum: {len(ids)}")
    print(f"Mesmo veredito nas duas rodadas : {len(same_outcome)} ({len(same_outcome) / len(ids):.0%})")
    print(f"Mesma resposta (status + valor) : {len(same_value)} ({len(same_value) / len(ids):.0%})")
    print(f"Acertos tolerantes {la}: {sum(a[i]['outcome'] in GOOD for i in ids)}/{len(ids)}")
    print(f"Acertos tolerantes {lb}: {sum(b[i]['outcome'] in GOOD for i in ids)}/{len(ids)}")
    print(f"Alucinações {la}: {sum(a[i]['outcome'] == 'hallucination' for i in ids)} | "
          f"{lb}: {sum(b[i]['outcome'] == 'hallucination' for i in ids)}")

    improved = [i for i in ids if a[i]["outcome"] not in GOOD and b[i]["outcome"] in GOOD]
    worse = [i for i in ids if a[i]["outcome"] in GOOD and b[i]["outcome"] not in GOOD]
    print(f"\nMelhoraram em {lb}: {len(improved)} | Pioraram em {lb}: {len(worse)}")
    for tag, group in (("MELHOROU", improved), ("PIOROU  ", worse)):
        for i in group:
            print(f"  {tag} {i:5} {a[i]['outcome']:>16} -> {b[i]['outcome']:<16} | "
                  f"{(b[i]['value_text'] or b[i]['status'])[:40]:40} | {(b[i]['program'] or '')[:60]}")

    flips = [i for i in ids if a[i]["outcome"] != b[i]["outcome"] and i not in improved and i not in worse]
    if flips:
        print(f"\nMudaram de veredito sem mudar de lado (certo/errado): {len(flips)}")
        for i in flips:
            print(f"  {i:5} {a[i]['outcome']} -> {b[i]['outcome']}")

    print("\nPor categoria (acertos tolerantes):")
    cats = Counter(a[i]["category"] for i in ids)
    for cat in sorted(cats):
        cid = [i for i in ids if a[i]["category"] == cat]
        ga = sum(a[i]["outcome"] in GOOD for i in cid)
        gb = sum(b[i]["outcome"] in GOOD for i in cid)
        print(f"  {cat:15} {la}: {ga:3}/{len(cid):<3} {lb}: {gb:3}/{len(cid):<3}")


if __name__ == "__main__":
    main()
