#!/usr/bin/env python3
"""
analyze.py - análise cruzada de duas rodadas do benchmark (por exemplo auto x tipado).

Responde o que o report.md e o compare.py não mostram:
  - teto (melhor modo por pergunta) e modo HÍBRIDO calculado sem nova chamada à API
  - acertos por documento
  - perguntas erradas nos dois modos, agrupadas por documento
  - o que o modelo respondeu nas alucinações e nos erros de confiança alta
  - motivos das recusas (UNKNOWN, UNSUPPORTED...) mais frequentes
  - varredura de barra de confiança por modo

Uso:
  python3 tools/analyze.py pt_auto pt_typed
  python3 tools/analyze.py pt_auto pt_typed --auto-kinds date,duration
(aceita pastas com results.csv ou os próprios arquivos .csv)
"""
import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

GOOD = {"correct", "content_ok", "correct_decline"}


def load(path):
    p = Path(path)
    if p.is_dir():
        p = p / "results.csv"
    with open(p, encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def cut(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def reason(program):
    m = re.search(r"→\s*(.*)$", program or "")
    return re.sub(r"\d+", "N", m.group(1)) if m else ""


def sweep(rows, bar):
    ans_total = [r for r in rows if r["expected_status"] == "ANSWER"]
    answered = [r for r in rows if r["status"] == "ANSWER" and float(r["confidence"] or 0) > bar]
    correct = [r for r in answered if r["outcome"] in ("correct", "content_ok")]
    wrong = [r for r in answered if r["outcome"] in ("wrong", "hallucination")]
    cov = len([r for r in answered if r["expected_status"] == "ANSWER"]) / max(len(ans_total), 1)
    prec = len(correct) / max(len(answered), 1)
    return len(answered), len(wrong), cov, prec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("auto")
    ap.add_argument("typed")
    ap.add_argument("--auto-kinds", default="date,duration",
                    help="no modo híbrido, estes kinds usam o resultado do modo auto")
    args = ap.parse_args()
    a, b = load(args.auto), load(args.typed)
    ids = [i for i in a if i in b]
    n = len(ids)
    auto_kinds = {k.strip() for k in args.auto_kinds.split(",") if k.strip()}
    pct = lambda x: f"{x}/{n} ({x / n:.0%})"

    best = [i for i in ids if a[i]["outcome"] in GOOD or b[i]["outcome"] in GOOD]
    hybrid = {i: (a[i] if a[i]["kind"] in auto_kinds else b[i]) for i in ids}
    print("=== 1. Acertos tolerantes (inclui recusas corretas) ===")
    print(f"auto                : {pct(sum(a[i]['outcome'] in GOOD for i in ids))}")
    print(f"tipado              : {pct(sum(b[i]['outcome'] in GOOD for i in ids))}")
    print(f"teto (melhor modo)  : {pct(len(best))}   <- só alcançável se soubesse qual modo usar em cada pergunta")
    print(f"híbrido (auto p/ {','.join(sorted(auto_kinds))}, tipado no resto): "
          f"{pct(sum(hybrid[i]['outcome'] in GOOD for i in ids))}")
    hh = [i for i in ids if hybrid[i]["outcome"] == "hallucination"]
    print(f"alucinações híbrido : {len(hh)}")

    print("\n=== 2. Por documento (tolerante) ===")
    docs = defaultdict(list)
    for i in ids:
        docs[a[i]["doc"]].append(i)
    print(f"{'documento':22} {'N':>3} {'auto':>6} {'tipado':>7} {'melhor':>7} {'híbrido':>8}")
    for d, g in sorted(docs.items()):
        f = lambda m: sum(m[i]["outcome"] in GOOD for i in g)
        print(f"{d:22} {len(g):>3} {f(a):>6} {f(b):>7} {sum(i in best for i in g):>7} "
              f"{sum(hybrid[i]['outcome'] in GOOD for i in g):>8}")

    print("\n=== 3. Erradas nos DOIS modos, por documento ===")
    both = [i for i in ids if i not in best]
    print(f"total: {len(both)} de {n}")
    for d, g in sorted(docs.items()):
        bad = [i for i in g if i in both]
        if bad:
            print(f"  {d:22} {len(bad):>2}: " + ", ".join(f"{i}({a[i]['category']})" for i in bad))

    for label, d in (("auto", a), ("tipado", b)):
        print(f"\n=== 4. Alucinações no modo {label}: o que respondeu ===")
        for i in ids:
            r = d[i]
            if r["outcome"] == "hallucination":
                print(f"  {i:5} {cut(r['question'], 48):48} -> {cut(r['value_text'], 24):24} | {cut(r['program'], 70)}")
        print(f"--- erros com confiança >= 0,90 no modo {label}")
        for i in ids:
            r = d[i]
            if r["outcome"] in ("wrong", "hallucination") and float(r["confidence"] or 0) >= 0.9:
                print(f"  {i:5} esp.={cut(r['expected'] or r['expected_status'], 16):16} obt.={cut(r['value_text'], 22):22} "
                      f"conf={float(r['confidence']):.2f} | {cut(r['question'], 46)}")

    print("\n=== 5. Motivos mais frequentes das recusas ('missed') ===")
    for label, d in (("auto", a), ("tipado", b)):
        miss = [d[i] for i in ids if d[i]["outcome"] == "missed"]
        print(f"[{label}] status: {dict(Counter(r['status'] for r in miss))}")
        for why, c in Counter(reason(r["program"]) for r in miss).most_common(8):
            print(f"   {c:>3}x {cut(why, 95)}")

    print("\n=== 6. Barra de confiança (precisão tolerante entre as respostas dadas) ===")
    for label, d in (("auto", a), ("tipado", b)):
        rows = list(d.values())
        print(f"[{label}]  barra | respondidas | erradas | cobertura | precisão")
        for bar in (0.0, 0.5, 0.7, 0.9, 0.95, 0.99):
            ans, wr, cov, prec = sweep(rows, bar)
            print(f"        >{bar:<4} | {ans:>11} | {wr:>7} | {cov:>8.0%} | {prec:>7.0%}")


if __name__ == "__main__":
    main()
