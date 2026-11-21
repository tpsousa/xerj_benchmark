#!/usr/bin/env python3
"""
xerj_bench.py - benchmark harness for XERJ Reader-1 (POST /v1/answers).

Reads a suite (suite/cases.csv + suite/docs/*.txt), asks every question through the
API (batched per document, up to 20 questions per call), scores the answers against
your expected values and writes:
  results/raw.jsonl     every request/response, for reproducibility and bug reports
  results/results.csv   one row per question
  results/report.md     summary, bar sweep, per-category table and failure list

Only the Python standard library is used. The API key is read from XERJ_API_KEY
and is never printed or written to disk.

Examples:
  python xerj_bench.py --dry-run                 # validate the suite, no network
  export XERJ_API_KEY="xerj_..."
  python xerj_bench.py                           # run with automatic type inference
  python xerj_bench.py --send-types --out results_typed   # same suite with explicit types
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

DEFAULT_BASE_URL = "https://platform.xerj.ai/v1"
MAX_QUESTIONS_PER_CALL = 20
MAX_QUESTION_CHARS = 300
KINDS = {"text", "number", "money", "date", "time", "duration", "pct", "yesno", "list"}
DEFAULT_BARS = "0.5,0.6,0.7,0.8,0.9,0.95,0.99"


# ----------------------------------------------------------------------------- suite

def load_suite(suite_dir: str):
    suite = Path(suite_dir)
    with open(suite / "cases.csv", encoding="utf-8", newline="") as f:
        cases = [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    docs = {}
    for c in cases:
        if c["doc"] not in docs:
            docs[c["doc"]] = (suite / "docs" / c["doc"]).read_text(encoding="utf-8")
    return cases, docs


def validate(cases, docs):
    problems, warnings, seen = [], [], set()
    for c in cases:
        cid = c["id"] or "<sem id>"
        if cid in seen:
            problems.append(f"{cid}: id duplicado")
        seen.add(cid)
        if not c["question"]:
            problems.append(f"{cid}: pergunta vazia")
        if len(c["question"]) > MAX_QUESTION_CHARS:
            problems.append(f"{cid}: pergunta com mais de {MAX_QUESTION_CHARS} caracteres")
        if c["kind"] not in KINDS:
            problems.append(f"{cid}: kind '{c['kind']}' invalido (use um de {sorted(KINDS)})")
        if c["expected_status"] not in ("ANSWER", "ABSENT"):
            problems.append(f"{cid}: expected_status deve ser ANSWER ou ABSENT")
        if c["expected_status"] == "ANSWER" and not c["expected"]:
            problems.append(f"{cid}: caso ANSWER sem valor esperado")
        if c["ref_date"]:
            try:
                datetime.strptime(c["ref_date"], "%Y-%m-%d")
            except ValueError:
                problems.append(f"{cid}: ref_date deve ser YYYY-MM-DD")
    for name, text in docs.items():
        if len(text) > 16000:
            warnings.append(f"{name}: {len(text)} caracteres (acima de 16.000 valem as regras de documento longo)")
        elif len(text) > 12000:
            warnings.append(f"{name}: {len(text)} caracteres; pode estourar a janela de 6.080 tokens do modelo")
    return problems, warnings


# ----------------------------------------------------------------------------- API

def call_api(base_url, key, payload, timeout=70, max_retries=5, user_agent="xerj-bench/1.1 (benchmark script)"):
    body = json.dumps(payload).encode("utf-8")
    idem = str(uuid.uuid4())  # same key on retries: a repeated call is read and billed once
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(
            base_url.rstrip("/") + "/answers", data=body, method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "Idempotency-Key": idem, "Accept": "application/json",
                     "User-Agent": user_agent})
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"ok": True, "data": data, "request_id": resp.headers.get("x-request-id"),
                        "wall_ms": int((time.perf_counter() - t0) * 1000),
                        "remaining": resp.headers.get("x-ratelimit-remaining-requests")}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            retry_after = e.headers.get("retry-after")
            if e.code in (429, 503) and attempt < max_retries:
                try:
                    wait = float(retry_after) if retry_after else 2 ** attempt
                except ValueError:
                    wait = 2 ** attempt
                time.sleep(min(wait, 60))
                continue
            return {"ok": False, "http": e.code, "error": raw[:500],
                    "request_id": e.headers.get("x-request-id"),
                    "wall_ms": int((time.perf_counter() - t0) * 1000)}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return {"ok": False, "http": None, "error": str(e), "request_id": None,
                    "wall_ms": int((time.perf_counter() - t0) * 1000)}


def question_obj(case, send_types):
    q = {"question": case["question"]}
    if send_types:
        q["type"] = case["kind"]
    return q


def run_suite(args, cases, docs, out_dir: Path):
    key = os.environ.get("XERJ_API_KEY")
    if not key:
        sys.exit("Defina XERJ_API_KEY no ambiente (export XERJ_API_KEY=...). Nao cole a chave em arquivos.")
    groups = defaultdict(list)
    for c in cases:
        groups[(c["doc"], c["ref_date"])].append(c)

    results, calls = {}, 0
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as raw:
        for (doc_name, ref_date), group in groups.items():
            for i in range(0, len(group), MAX_QUESTIONS_PER_CALL):
                chunk = group[i:i + MAX_QUESTIONS_PER_CALL]
                payload = {"document": docs[doc_name],
                           "questions": [question_obj(c, args.send_types) for c in chunk]}
                if ref_date:
                    payload["ref_date"] = ref_date
                out = call_api(args.base_url, key, payload, user_agent=args.user_agent)
                calls += 1
                status = "ok" if out["ok"] else f"ERRO {out.get('http')}"
                print(f"[{calls}] {doc_name} ({len(chunk)} perguntas): {status}, {out['wall_ms']} ms")
                if not out["ok"]:
                    print(f"    corpo do erro: {str(out.get('error'))[:300]}")
                    print(f"    request_id: {out.get('request_id')}")
                raw.write(json.dumps({
                    "doc": doc_name, "ref_date": ref_date, "ids": [c["id"] for c in chunk],
                    "request_id": out.get("request_id"), "ok": out["ok"], "http": out.get("http"),
                    "wall_ms": out["wall_ms"], "response": out.get("data"), "error": out.get("error"),
                }, ensure_ascii=False) + "\n")
                if out["ok"]:
                    items = out["data"].get("data") or []
                    for idx, c in enumerate(chunk):
                        item = items[idx] if idx < len(items) else None
                        results[c["id"]] = {"res": item, "request_id": out.get("request_id"),
                                            "wall_ms": out["wall_ms"],
                                            "error": None if item else "resposta sem item para esta pergunta"}
                else:
                    for c in chunk:
                        results[c["id"]] = {"res": None, "request_id": out.get("request_id"),
                                            "wall_ms": out["wall_ms"],
                                            "error": f"HTTP {out.get('http')}: {out.get('error')}"}
                if not out["ok"] and out.get("http") in (401, 402, 403) and calls == 1:
                    print("\nA primeira chamada falhou com erro de autenticacao/acesso. Abortando para nao repetir o erro.")
                    print("Veja o corpo do erro acima e a pagina https://platform.xerj.ai/docs/errors")
                    sys.exit(2)
                if args.delay:
                    time.sleep(args.delay)
    return results


# ----------------------------------------------------------------------------- scoring

def norm(s) -> str:
    return " ".join(str(s).casefold().split())


def match_one(kind, exp, res) -> bool:
    val, text = res.get("value"), res.get("value_text")
    shown = text if text is not None else val
    if exp.startswith("~"):                       # substring match
        return norm(exp[1:]) in norm(shown)
    try:
        if kind == "number":
            return Decimal(str(val)) == Decimal(exp)
        if kind == "pct":
            v, e = Decimal(str(val).rstrip("%")), Decimal(exp.rstrip("%"))
            return v == e or v == e / 100
        if kind == "money":
            parts = exp.split()
            amount = Decimal(parts[0])
            cur = parts[1].upper() if len(parts) > 1 else None
            if isinstance(val, dict):
                if Decimal(str(val.get("amount"))) != amount:
                    return False
                return cur is None or str(val.get("currency", "")).upper() == cur
            return Decimal(str(val)) == amount
        if kind == "date":
            return str(val)[:10] == exp
        if kind == "yesno":
            return bool(val) == (exp.lower() in ("yes", "true", "sim"))
    except (InvalidOperation, ValueError, TypeError):
        return False
    if kind == "list":
        items = val if isinstance(val, list) else []
        got = {norm(" ".join(map(str, i.values())) if isinstance(i, dict) else i) for i in items}
        return got == {norm(x) for x in exp.split("|")}
    return norm(exp) == norm(shown)


def matches(kind, expected, res) -> bool:
    return any(match_one(kind, alt.strip(), res) for alt in expected.split("##"))


def classify(case, res):
    if res is None:
        return "error"
    status = res.get("status")
    exp_answer = case["expected_status"] == "ANSWER"
    if status == "ANSWER":
        if not exp_answer:
            return "hallucination"
        return "correct" if matches(case["kind"], case["expected"], res) else "wrong"
    return "missed" if exp_answer else "correct_decline"


def evidence_check(doc_text, res):
    ev = (res or {}).get("evidence") or []
    ok = sum(1 for e in ev if doc_text[e["start"]:e["end"]] == e.get("quote"))
    return ok, len(ev)


def build_rows(cases, docs, results):
    rows = []
    for c in cases:
        r = results.get(c["id"], {})
        res = r.get("res")
        ok, n = evidence_check(docs[c["doc"]], res) if res else (0, 0)
        sym = (res or {}).get("symbolic") or {}
        usage = (res or {}).get("usage") or {}
        rows.append({
            "id": c["id"], "category": c["category"], "lang": c["lang"], "doc": c["doc"],
            "question": c["question"], "kind": c["kind"], "expected": c["expected"],
            "expected_status": c["expected_status"],
            "status": (res or {}).get("status", "ERROR"),
            "value_text": (res or {}).get("value_text"),
            "confidence": float((res or {}).get("confidence") or 0),
            "outcome": classify(c, res),
            "program": sym.get("program_compact"),
            "request_id": r.get("request_id"),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "ms_total": (sym.get("ms") or {}).get("total"),
            "wall_ms": r.get("wall_ms"),
            "evidence_ok": ok, "evidence_n": n,
            "error": r.get("error"),
        })
    return rows


def sweep(rows, bar):
    answerable = [r for r in rows if r["expected_status"] == "ANSWER"]
    absent = [r for r in rows if r["expected_status"] == "ABSENT"]
    answered = [r for r in rows if r["status"] == "ANSWER" and (bar is None or r["confidence"] > bar)]
    correct = [r for r in answered if r["outcome"] == "correct"]
    wrong = [r for r in answered if r["outcome"] in ("wrong", "hallucination")]
    cov = len([r for r in answered if r["expected_status"] == "ANSWER"]) / len(answerable) if answerable else 0
    prec = len(correct) / len(answered) if answered else 0
    fp = len([r for r in answered if r["expected_status"] == "ABSENT"]) / len(absent) if absent else 0
    return {"bar": bar, "answered": len(answered), "correct": len(correct), "wrong": len(wrong),
            "coverage": cov, "precision": prec, "absent_fp": fp}


def pctl(values, p):
    s = sorted(v for v in values if v is not None)
    if not s:
        return 0
    k = (len(s) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


# ----------------------------------------------------------------------------- report

def cell(x, n=70):
    s = " ".join(str(x if x is not None else "").split()).replace("|", "\\|")
    return s if len(s) <= n else s[:n - 1] + "…"


def build_report(rows, bars, args):
    L = []
    total = len(rows)
    answerable = [r for r in rows if r["expected_status"] == "ANSWER"]
    absent = [r for r in rows if r["expected_status"] == "ABSENT"]
    by = lambda o: [r for r in rows if r["outcome"] == o]
    L += [f"# XERJ Reader-1: relatório do benchmark", "",
          f"- Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
          f"- Modo de tipos: {'explícito (--send-types)' if args.send_types else 'automático (inferido da pergunta)'}",
          f"- Perguntas: {total} ({len(answerable)} com resposta no texto, {len(absent)} sem resposta no texto)", ""]

    L += ["## Resultado sem barra de confiança", "",
          "| Resultado | Qtde |", "|---|---|",
          f"| Corretas | {len(by('correct'))} |",
          f"| Erradas (valor incorreto) | {len(by('wrong'))} |",
          f"| Perdidas (recusou, mas a resposta existia) | {len(by('missed'))} |",
          f"| Recusas corretas (ABSENT/UNKNOWN) | {len(by('correct_decline'))} |",
          f"| Alucinações (respondeu algo que não está no texto) | {len(by('hallucination'))} |",
          f"| Erros de API | {len(by('error'))} |", ""]

    L += ["## Varredura da barra `min_confidence`", "",
          "Cobertura = perguntas respondíveis que receberam resposta. Precisão = respostas corretas entre as dadas. "
          "Falso positivo ABSENT = respondeu uma pergunta sem resposta no texto.", "",
          "| Barra | Respondidas | Corretas | Erradas | Cobertura | Precisão | Falso positivo ABSENT |",
          "|---|---|---|---|---|---|---|"]
    table = [sweep(rows, None)] + [sweep(rows, b) for b in bars]
    for s in table:
        label = "sem barra" if s["bar"] is None else f"> {s['bar']}"
        L.append(f"| {label} | {s['answered']} | {s['correct']} | {s['wrong']} | {s['coverage']:.0%} | "
                 f"{s['precision']:.0%} | {s['absent_fp']:.0%} |")
    clean = [s for s in table[1:] if s["wrong"] == 0 and s["answered"] > 0]
    L += ["", (f"Menor barra testada sem nenhuma resposta errada: **> {clean[0]['bar']}** "
               f"(cobertura {clean[0]['coverage']:.0%}).") if clean else
          "Nenhuma das barras testadas eliminou todas as respostas erradas.", ""]

    L += ["## Por categoria", "", "| Categoria | N | Corretas | Erradas | Perdidas | Recusas corretas | Alucinações |",
          "|---|---|---|---|---|---|---|"]
    cats = defaultdict(list)
    for r in rows:
        cats[r["category"]].append(r)
    for cat, rs in sorted(cats.items()):
        n = lambda o: len([r for r in rs if r["outcome"] == o])
        L.append(f"| {cat} | {len(rs)} | {n('correct')} | {n('wrong')} | {n('missed')} | {n('correct_decline')} | {n('hallucination')} |")

    L += ["", "## Por idioma", "", "| Idioma | N | Acertos (corretas + recusas corretas) |", "|---|---|---|"]
    langs = defaultdict(list)
    for r in rows:
        langs[r["lang"]].append(r)
    for lang, rs in sorted(langs.items()):
        good = len([r for r in rs if r["outcome"] in ("correct", "correct_decline")])
        L.append(f"| {lang} | {len(rs)} | {good} ({good / len(rs):.0%}) |")

    ev_ok = sum(r["evidence_ok"] for r in rows)
    ev_n = sum(r["evidence_n"] for r in rows)
    in_tok = sum(r["input_tokens"] for r in rows)
    out_tok = sum(r["output_tokens"] for r in rows)
    cost = in_tok * args.price_per_m / 1_000_000
    ms = [r["ms_total"] for r in rows]
    wall = sorted({(r["request_id"], r["wall_ms"]) for r in rows if r["wall_ms"] is not None})
    L += ["", "## Integridade da evidência, custo e latência", "",
          f"- Evidência íntegra (`quote == document[start:end]`): {ev_ok}/{ev_n}"
          + (f" ({ev_ok / ev_n:.0%})" if ev_n else ""),
          f"- Tokens: {in_tok} de entrada, {out_tok} de saída. Custo estimado: US$ {cost:.6f} (a US$ {args.price_per_m}/1M de entrada)",
          f"- Latência do servidor por pergunta (ms): p50 {pctl(ms, 50):.0f}, p95 {pctl(ms, 95):.0f}",
          f"- Latência por chamada de lote (ms): p50 {pctl([w for _, w in wall], 50):.0f}, p95 {pctl([w for _, w in wall], 95):.0f}", ""]

    bad = [r for r in rows if r["outcome"] in ("wrong", "hallucination", "missed", "error")]
    L += ["## Falhas para revisar e reportar", ""]
    if not bad:
        L += ["Nenhuma falha neste conjunto."]
    else:
        L += ["| ID | Categoria | Resultado | Pergunta | Esperado | Obtido | Conf. | Programa | request_id |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in bad:
            got = r["value_text"] if r["status"] == "ANSWER" else f"{r['status']}"
            L.append(f"| {r['id']} | {r['category']} | {r['outcome']} | {cell(r['question'], 60)} | "
                     f"{cell(r['expected'] or r['expected_status'], 30)} | {cell(got, 30)} | {r['confidence']:.2f} | "
                     f"{cell(r['program'] or r['error'], 70)} | {r['request_id'] or ''} |")
    L += ["", "Use o `request_id` ao reportar um problema ao fundador: ele localiza a chamada exata."]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Benchmark do XERJ Reader-1 (/v1/answers)")
    ap.add_argument("--suite", default="suite")
    ap.add_argument("--out", default="results")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--bars", default=DEFAULT_BARS, help="barras de min_confidence para a varredura")
    ap.add_argument("--send-types", action="store_true", help="enviar a coluna kind como `type` (tipo explícito)")
    ap.add_argument("--only-category", help="rodar só uma categoria")
    ap.add_argument("--limit", type=int, help="rodar só as N primeiras perguntas")
    ap.add_argument("--price-per-m", type=float, default=0.01, help="US$ por 1M tokens de entrada")
    ap.add_argument("--delay", type=float, default=0.0, help="pausa (s) entre chamadas")
    ap.add_argument("--user-agent", default="xerj-bench/1.1 (benchmark script)",
                    help="User-Agent enviado (o Cloudflare bloqueia o padrão do Python com erro 1010)")
    ap.add_argument("--dry-run", action="store_true", help="validar a suíte sem chamar a API")
    args = ap.parse_args()

    cases, docs = load_suite(args.suite)
    if args.only_category:
        cases = [c for c in cases if c["category"] == args.only_category]
    if args.limit:
        cases = cases[:args.limit]
    docs = {k: v for k, v in docs.items() if any(c["doc"] == k for c in cases)}

    problems, warnings = validate(cases, docs)
    for w in warnings:
        print("AVISO:", w)
    if problems:
        print("PROBLEMAS NA SUITE:")
        for p in problems:
            print(" -", p)
        sys.exit(1)

    n_calls = sum(-(-len(g) // MAX_QUESTIONS_PER_CALL)
                  for g in _group_sizes(cases))
    print(f"Suite valida: {len(cases)} perguntas, {len(docs)} documentos, {n_calls} chamadas de API.")
    if args.dry_run:
        return

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = run_suite(args, cases, docs, out_dir)
    rows = build_rows(cases, docs, results)

    with (out_dir / "results.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bars = [float(b) for b in args.bars.split(",") if b.strip()]
    report = build_report(rows, bars, args)
    (out_dir / "report.md").write_text(report, encoding="utf-8")

    s = sweep(rows, None)
    print(f"\nSem barra: cobertura {s['coverage']:.0%}, precisão {s['precision']:.0%}, "
          f"falso positivo em ABSENT {s['absent_fp']:.0%}")
    print(f"Relatório: {out_dir / 'report.md'}")


def _group_sizes(cases):
    groups = defaultdict(list)
    for c in cases:
        groups[(c["doc"], c["ref_date"])].append(c)
    return groups.values()


if __name__ == "__main__":
    main()