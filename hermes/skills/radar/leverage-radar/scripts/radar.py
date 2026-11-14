#!/usr/bin/env python3
"""radar.py - deterministic engine of the Leverage Radar (stdlib only).

Everything mechanical lives here so the model only spends tokens on judgment:
ids, dedupe, batching, schema validation, counting, alerts, experiments,
evals and the HTML dashboard. Run it from the radar workspace (or pass --ws).

  ingest <export.zip>          WhatsApp export -> inbox/inbox.jsonl
  capture <url> [--note ..]    add one link (chat or scan); tells you if it was seen before
  next [-n 10] [--fetch]       next batch to judge, as JSON lines
  pending                      one stable line for `hermes cron --monitor-script`
  log [--json '{..}']          validate + append verdicts (stdin JSONL or --json); marks processed
  alerts                       rabbit holes, WIP, expired experiments, stalled radar; silent if none
  digest-data                  everything the weekly digest needs, as JSON
  exp list|open|close          experiments in experimentos.md (max 3 active)
  label <id> <VERDICT>         record your correction in evals/gold.jsonl
  gold-from-notes              weak labels from what you flagged ("Bible", "10/10", re-shared)
  eval [--gold F] [--compare A B]  verdicts vs your labels, or agreement between two runs
  dashboard [-o file.html]     self-contained HTML view of the radar
  self-test                    offline tests
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whatsapp_to_inbox as wa  # noqa: E402

VERDICTS = ("ADOPT", "TEST", "WATCH", "CANDIDATO", "DROP")
PASSING = {"ADOPT", "TEST", "WATCH", "CANDIDATO"}
FINAL = ("ADOPT", "TEST", "WATCH", "DROP")
LAYERS = ("identidad", "distribucion", "conversion", "aprendizaje", "orquestacion", "ninguna")
QUESTIONS = ("decision", "stack", "apuesta", "ninguna")
EVIDENCE = ("sin-fuente", "anecdota", "demo", "adopcion", "medido", "verificado")
STAGES = ("triage", "capture", "digest", "scan")
WIP_MAX = 3
RABBIT_MIN, RABBIT_DAYS = 5, 14
UMBRELLA_TAGS = {"agents-skills"}  # your home turf: too broad to call a rabbit hole


def today() -> dt.date:
    forced = os.environ.get("RADAR_TODAY")
    return dt.date.fromisoformat(forced) if forced else dt.date.today()


def _date(s: str | None) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(s)[:10]) if s else None
    except ValueError:
        return None


def item_id(url: str) -> str:
    return hashlib.sha1(wa.canonical_url(url).encode()).hexdigest()[:12]


# ------------------------------------------------------------- workspace ---

class WS:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.inbox_dir = self.root / "inbox"
        self.inbox = self.inbox_dir / "inbox.jsonl"
        self.capturas = self.inbox_dir / "capturas.jsonl"
        self.processed_file = self.inbox_dir / "processed.txt"
        self.log_file = self.root / "radar-log.jsonl"
        self.gold = self.root / "evals" / "gold.jsonl"
        self.experiments = self.root / "experimentos.md"
        self.digests = self.root / "digests"

    # -- io
    @staticmethod
    def read_jsonl(path: Path) -> list[dict]:
        rows: list[dict] = []
        if not path.exists():
            return rows
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"warning: {path.name}:{n} is not valid JSON, skipped", file=sys.stderr)
        return rows

    @staticmethod
    def append_jsonl(path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # -- views
    def items(self) -> dict[str, dict]:
        """Captures first (newest first), then the ranked WhatsApp inbox; deduped by id."""
        out: dict[str, dict] = {}
        for it in reversed(self.read_jsonl(self.capturas)):
            out.setdefault(it["id"], it)
        for it in self.read_jsonl(self.inbox):
            out.setdefault(it["id"], it)
        return out

    def processed(self) -> set[str]:
        if not self.processed_file.exists():
            return set()
        return set(self.processed_file.read_text(encoding="utf-8").split())

    def log(self) -> list[dict]:
        return self.read_jsonl(self.log_file)

    def latest(self, stage: str | None = None) -> dict[str, dict]:
        last: dict[str, dict] = {}
        for row in self.log():
            if stage is None or row.get("etapa") == stage:
                last[row["id"]] = row
        return last

    def pending(self) -> list[dict]:
        done = self.processed()
        return [it for iid, it in self.items().items() if iid not in done]


# ------------------------------------------------------------ experiments ---

EXP_HEAD = re.compile(r"^### (EXP-\d+)\s*·\s*(.+)$")


def _sections(text: str) -> dict[str, tuple[int, int]]:
    """'## Name' -> (start line, end line) of its body."""
    lines = text.splitlines()
    heads = [(i, l[3:].strip().lower()) for i, l in enumerate(lines) if l.startswith("## ")]
    out = {}
    for k, (i, name) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        out[name] = (i + 1, end)
    return out


def experiments(ws: WS) -> list[dict]:
    if not ws.experiments.exists():
        return []
    text = ws.experiments.read_text(encoding="utf-8")
    lines = text.splitlines()
    sec = _sections(text).get("activos")
    if not sec:
        return []
    out, cur = [], None
    for line in lines[sec[0]:sec[1]]:
        m = EXP_HEAD.match(line)
        if m:
            cur = {"id": m.group(1), "titulo": m.group(2).strip(), "lineas": []}
            out.append(cur)
        elif cur is not None:
            cur["lineas"].append(line)
    exps = []
    for e in out:
        body = "\n".join(e.pop("lineas"))
        if "<" in e["titulo"]:  # template placeholder
            continue
        corte = re.search(r"Fecha de corte:\s*(\d{4}-\d{2}-\d{2})", body)
        estado = re.search(r"Estado:\s*([^\n·]+)", body)
        cap = re.search(r"Capacidad:\s*([^\n]+)", body)
        origen = re.search(r"Origen:\s*([^\n]+)", body)
        e.update(corte=corte.group(1) if corte else None,
                 estado=(estado.group(1).strip() if estado else "pendiente"),
                 capacidad=cap.group(1).strip() if cap else None,
                 origen=origen.group(1).strip() if origen else None)
        exps.append(e)
    return exps


def exp_open(ws: WS, titulo: str, hipotesis: str, criterio: str, capacidad: str,
             corte: str | None, origen: str, timebox: str = "2 sesiones × 40 min") -> str:
    active = experiments(ws)
    if len(active) >= WIP_MAX:
        raise SystemExit(f"sin cupo: {len(active)}/{WIP_MAX} experimentos activos. Cerrá uno con `exp close`.")
    text = ws.experiments.read_text(encoding="utf-8") if ws.experiments.exists() else \
        "# Experimentos\n\n## Activos\n\n## Cerrados\n\n| id | fecha | resultado | aprendizaje (1 línea) |\n|---|---|---|---|\n"
    nums = [int(n) for line in text.splitlines() if "<" not in line
            for n in re.findall(r"EXP-(\d+)", line)] or [0]  # template placeholders don't count
    eid = f"EXP-{max(nums) + 1:03d}"
    corte = corte or (today() + dt.timedelta(days=14)).isoformat()
    block = (f"### {eid} · {titulo}\n\n- Capacidad: {capacidad}\n- Hipótesis: {hipotesis}\n"
             f"- Criterio de éxito: {criterio}\n- Timebox: {timebox} · Fecha de corte: {corte}\n"
             f"- Origen: {origen}\n- Estado: pendiente\n")
    lines = text.splitlines()
    sec = _sections(text).get("activos")
    if sec is None:
        lines += ["", "## Activos", "", *block.splitlines()]
    else:
        # drop template placeholder blocks, then insert at the end of the section
        start, end = sec
        body = lines[start:end]
        keep, skip = [], False
        for l in body:
            if l.startswith("### "):
                skip = "<" in l
            if not skip:
                keep.append(l)
        while keep and not keep[-1].strip():
            keep.pop()
        lines = lines[:start] + keep + ["", *block.splitlines(), ""] + lines[end:]
    ws.experiments.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return eid


def exp_close(ws: WS, eid: str, resultado: str, aprendizaje: str) -> None:
    resultado = resultado.upper()
    if resultado not in ("ADOPT", "DROP"):
        raise SystemExit("un experimento cierra con ADOPT o DROP")
    text = ws.experiments.read_text(encoding="utf-8")
    lines = text.splitlines()
    sec = _sections(text).get("activos")
    if not sec:
        raise SystemExit("no hay sección '## Activos'")
    start, end = sec
    i = next((k for k in range(start, end) if lines[k].startswith(f"### {eid} ")), None)
    if i is None:
        raise SystemExit(f"{eid} no está entre los activos")
    j = next((k for k in range(i + 1, end) if lines[k].startswith("### ")), end)
    titulo = EXP_HEAD.match(lines[i]).group(2).strip()
    del lines[i:j]
    text = "\n".join(lines)
    row = f"| {eid} · {titulo} | {today().isoformat()} | {resultado} | {aprendizaje.strip()} |"
    lines = text.splitlines()
    sec = _sections(text).get("cerrados")
    if sec is None:
        lines += ["", "## Cerrados", "", "| id | fecha | resultado | aprendizaje (1 línea) |", "|---|---|---|---|", row]
    else:
        start, end = sec
        last_table = max((k for k in range(start, end) if lines[k].startswith("|")), default=None)
        if last_table is None:
            lines[start:start] = ["", "| id | fecha | resultado | aprendizaje (1 línea) |", "|---|---|---|---|", row]
        else:
            lines.insert(last_table + 1, row)
    ws.experiments.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


# -------------------------------------------------------------- verdicts ---

def normalize(row: dict, ws: WS, items: dict[str, dict]) -> dict:
    r = dict(row)
    if r.get("url"):
        r["url"] = wa.canonical_url(r["url"])
        r.setdefault("id", item_id(r["url"]))
    it = items.get(r.get("id", ""), {})
    r.setdefault("url", it.get("url"))
    if not r.get("tags"):
        r["tags"] = it.get("tags") or wa.tags_for(" ".join(it.get("notes", [])) + " " + (r.get("url") or ""))
    r.setdefault("fecha", today().isoformat())
    for k in ("veredicto",):
        if isinstance(r.get(k), str):
            r[k] = r[k].strip().upper()
    for k in ("capa", "pregunta", "evidencia", "etapa", "durabilidad"):
        if isinstance(r.get(k), str):
            r[k] = r[k].strip().lower().replace("ó", "o").replace("á", "a").replace("é", "e").replace("í", "i")
    return r


def validate(r: dict) -> list[str]:
    e: list[str] = []
    rid = r.get("id") or r.get("url") or "?"
    v = r.get("veredicto")

    def need(field: str, why: str) -> None:
        if not str(r.get(field) or "").strip():
            e.append(f"{rid}: falta `{field}` ({why})")

    need("id", "o pasá `url`")
    if v not in VERDICTS:
        e.append(f"{rid}: veredicto {v!r} no es uno de {', '.join(VERDICTS)}")
    if r.get("etapa") not in STAGES:
        e.append(f"{rid}: etapa {r.get('etapa')!r} no es una de {', '.join(STAGES)}")
    if r.get("capa") not in LAYERS:
        e.append(f"{rid}: capa {r.get('capa')!r} no es una de {', '.join(LAYERS)}")
    if r.get("pregunta") not in QUESTIONS:
        e.append(f"{rid}: pregunta {r.get('pregunta')!r} no es una de {', '.join(QUESTIONS)}")
    need("por_que", "una línea")
    if v in PASSING:
        need("capacidad", "ubicala en el mapa de capacidades")
        need("proximo_paso", "un paso de ≤30 min")
        if r.get("evidencia") not in EVIDENCE:
            e.append(f"{rid}: evidencia {r.get('evidencia')!r} no es una de {', '.join(EVIDENCE)}")
        if r.get("pregunta") == "ninguna":
            e.append(f"{rid}: {v} con pregunta 'ninguna' es contradictorio: si ninguna da sí, es DROP")
        if r.get("capa") == "ninguna":
            e.append(f"{rid}: {v} sin capa: si no se puede ubicar en el mapa, es DROP")
    if v == "WATCH":
        need("revisar_si", "sin disparador concreto, WATCH es DROP")
    if v == "ADOPT" and r.get("evidencia") not in ("verificado", "medido"):
        e.append(f"{rid}: ADOPT requiere evidencia verificado o medido (tiene {r.get('evidencia')!r})")
    if v == "TEST" and r.get("evidencia") in ("sin-fuente", "anecdota"):
        e.append(f"{rid}: TEST requiere evidencia ≥ demo (tiene {r.get('evidencia')!r}); usá WATCH")
    if v == "CANDIDATO" and r.get("etapa") not in ("triage", "scan"):
        e.append(f"{rid}: CANDIDATO solo existe en triage o scan; en {r.get('etapa')} decidí ADOPT/TEST/WATCH/DROP")
    if r.get("evidencia") == "sin-fuente" and v in ("ADOPT", "TEST"):
        e.append(f"{rid}: sin fuente el máximo es WATCH")
    return e


def log_verdicts(ws: WS, rows: list[dict], force: bool = False) -> list[dict]:
    items = ws.items()
    rows = [normalize(r, ws, items) for r in rows]
    errors = [msg for r in rows for msg in validate(r)]
    new_tests = sum(r.get("veredicto") == "TEST" for r in rows)
    active = len(experiments(ws))
    if new_tests and active + new_tests > WIP_MAX and not force:
        errors.append(f"sin cupo para {new_tests} TEST: hay {active}/{WIP_MAX} experimentos activos. "
                      "Registralo como WATCH con revisar_si: 'cupo libre en experimentos' (o --force).")
    if errors:
        raise ValueError("\n".join(errors))
    ws.append_jsonl(ws.log_file, rows)
    done = ws.processed()
    new_ids = [r["id"] for r in rows if r["id"] not in done and r.get("etapa") != "digest"]
    if new_ids:
        ws.processed_file.parent.mkdir(parents=True, exist_ok=True)
        with open(ws.processed_file, "a", encoding="utf-8") as fh:
            fh.write("".join(f"{i}\n" for i in dict.fromkeys(new_ids)))
    return rows


# ---------------------------------------------------------------- alerts ---

def alerts(ws: WS) -> list[dict]:
    out: list[dict] = []
    now = today()
    items = ws.items()
    log = ws.log()
    # rabbit holes: many fresh links on one tag, no TEST/ADOPT on that tag lately
    fresh = Counter()
    for it in items.values():
        d = _date(it.get("first_seen"))
        if d and (now - d).days <= RABBIT_DAYS:
            fresh.update(it.get("tags", []))
    tried = {t for r in log if r.get("veredicto") in ("TEST", "ADOPT")
             and (d := _date(r.get("fecha"))) and (now - d).days <= 30 for t in r.get("tags", [])}
    for tag, n in fresh.most_common():
        if n >= RABBIT_MIN and tag not in tried and tag not in UMBRELLA_TAGS:
            out.append({"nivel": "serious", "tipo": "rabbit-hole", "texto":
                        f"Estás orbitando `{tag}`: {n} links en {RABBIT_DAYS} días y 0 pruebas. "
                        "Elegí 1 para TEST y hacé DROP del resto."})
    exps = experiments(ws)
    if len(exps) > WIP_MAX:
        out.append({"nivel": "critical", "tipo": "wip", "texto":
                    f"{len(exps)} experimentos activos (máx {WIP_MAX}). Cerrá antes de abrir otro."})
    for e in exps:
        c = _date(e.get("corte"))
        if c and c < now:
            out.append({"nivel": "warning", "tipo": "experimento-vencido", "texto":
                        f"{e['id']} ({e['titulo']}) venció el {c.isoformat()}: cerralo con ADOPT o DROP."})
    pend = len(ws.pending())
    last = max((d for r in log if (d := _date(r.get("fecha")))), default=None)
    if pend and (last is None or (now - last).days > 7):
        since = "nunca juzgó nada" if last is None else f"no juzga nada desde el {last.isoformat()}"
        out.append({"nivel": "critical", "tipo": "radar-parado", "texto":
                    f"El radar {since} y hay {pend} pendientes. ¿Corre `hermes gateway` y el cron de TRIAGE?"})
    stale = []
    for name in ("decisiones.md", "stack.md"):
        p = ws.root / name
        if p.exists():
            for m in re.finditer(r"^- (\d{4}-\d{2}-\d{2}) · (.+)$", p.read_text(encoding="utf-8"), re.M):
                d = _date(m.group(1))
                if d and (now - d).days > 14:
                    stale.append(m.group(2)[:60])
    if stale:
        out.append({"nivel": "warning", "tipo": "propuestas", "texto":
                    f"{len(stale)} propuesta(s) esperan tu sí hace más de 14 días: " + "; ".join(stale[:3])})
    return out


ICON = {"critical": "⛔", "serious": "⚠", "warning": "⏳", "good": "✓"}


# ----------------------------------------------------------------- digest ---

def iso_week(d: dt.date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-{w:02d}"


def digest_data(ws: WS) -> dict:
    now = today()
    log = ws.log()
    prev = sorted(ws.digests.glob("*.md")) if ws.digests.exists() else []
    last_digest_row = max((d for r in log if r.get("etapa") == "digest" and (d := _date(r.get("fecha")))), default=None)
    since = last_digest_row or (now - dt.timedelta(days=7))
    if prev and not last_digest_row:
        since = now - dt.timedelta(days=7)
    window = [r for r in log if (d := _date(r.get("fecha"))) and d >= since]
    decided = {r["id"] for r in log if r.get("etapa") == "digest"}
    latest = ws.latest()
    candidates = [r for r in latest.values() if r.get("veredicto") == "CANDIDATO" and r["id"] not in decided]
    capture_signals = [r for r in window if r.get("etapa") == "capture" and r.get("veredicto") in ("ADOPT", "TEST")]
    items = ws.items()
    for r in candidates:
        r["notas"] = items.get(r["id"], {}).get("notes", [])
    return {
        "semana": iso_week(now), "desde": since.isoformat(), "hasta": now.isoformat(),
        "revisados": sum(r.get("etapa") in ("triage", "capture", "scan") for r in window),
        "por_veredicto": dict(Counter(r.get("veredicto") for r in window)),
        "candidatos": candidates, "senales_capture": capture_signals,
        "experimentos": experiments(ws), "alertas": alerts(ws),
        "pendientes": len(ws.pending()),
        "archivo_digest": f"digests/{iso_week(now)}.md",
    }


# ------------------------------------------------------------------ evals ---

def _binary(v: str | None) -> str | None:
    return None if v is None else ("pasa" if v in PASSING else "drop")


def evaluate(gold: list[dict], preds: dict[str, dict]) -> dict:
    tp = fp = fn = tn = exact = exact_n = missing = 0
    confusion: dict[str, Counter] = defaultdict(Counter)
    misses = []
    for g in gold:
        gv = g["veredicto"]
        p = preds.get(g["id"])
        if p is None:
            missing += 1
            continue
        pv = p.get("veredicto")
        confusion[gv][pv] += 1
        gb, pb = _binary(gv), _binary(pv)
        tp += gb == "pasa" and pb == "pasa"
        fp += gb == "drop" and pb == "pasa"
        fn += gb == "pasa" and pb == "drop"
        tn += gb == "drop" and pb == "drop"
        weak = g.get("fuente") == "notas"
        if pv != "CANDIDATO" and not weak:
            exact_n += 1
            exact += pv == gv
        if gb != pb or (pv != "CANDIDATO" and pv != gv and not weak):
            misses.append({"id": g["id"], "url": g.get("url"), "esperado": gv, "radar": pv,
                           "por_que_radar": p.get("por_que"), "por_que_tuyo": g.get("por_que")})
    n = tp + fp + fn + tn
    return {
        "juzgados": n, "sin_juicio": missing,
        "filtro_acierto": round((tp + tn) / n, 3) if n else None,
        "precision_pasa": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall_pasa": round(tp / (tp + fn), 3) if tp + fn else None,
        "veredicto_exacto": round(exact / exact_n, 3) if exact_n else None,
        "matriz": {k: dict(v) for k, v in confusion.items()}, "desacuerdos": misses,
    }


def agreement(a: dict[str, dict], b: dict[str, dict]) -> dict:
    common = sorted(set(a) & set(b))
    if not common:
        return {"comunes": 0}
    bin_agree = sum(_binary(a[i].get("veredicto")) == _binary(b[i].get("veredicto")) for i in common)
    exact = sum(a[i].get("veredicto") == b[i].get("veredicto") for i in common)
    pa = sum(_binary(a[i].get("veredicto")) == "pasa" for i in common) / len(common)
    pb = sum(_binary(b[i].get("veredicto")) == "pasa" for i in common) / len(common)
    po = bin_agree / len(common)
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0
    diffs = [{"id": i, "url": a[i].get("url"), "A": a[i].get("veredicto"), "B": b[i].get("veredicto")}
             for i in common if _binary(a[i].get("veredicto")) != _binary(b[i].get("veredicto"))]
    return {"comunes": len(common), "acuerdo_filtro": round(po, 3), "acuerdo_exacto": round(exact / len(common), 3),
            "kappa_filtro": kappa, "desacuerdos_filtro": diffs}


def gold_from_notes(ws: WS) -> list[dict]:
    """Weak labels: what YOU flagged ("Bible", "10/10", "clave", "si o si"...) or saved more than
    once should pass the radar's filter. Measures recall only; regenerated on every call."""
    rows = []
    for it in ws.items().values():
        notes = " / ".join(it.get("notes", []))
        markers = [k for k in wa.PRIORITY_HIGH if wa._has(notes.lower(), k)]
        if markers or it.get("times_shared", 1) > 1:
            why = (f"lo marcaste '{markers[0]}'" if markers else f"lo guardaste {it['times_shared']} veces")
            rows.append({"id": it["id"], "url": it.get("url"), "veredicto": "WATCH", "fuente": "notas",
                         "por_que": f"etiqueta débil: {why}", "notas": notes[:120]})
    path = ws.root / "evals" / "gold-debil.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return rows


def latest_by_id(rows: list[dict], stage: str | None = None) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in rows:
        if stage is None or r.get("etapa") == stage:
            out[r["id"]] = r
    return out


# -------------------------------------------------------------- dashboard ---

CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--ink-3:#77766f;
--hair:#e6e5e0;--series:#2a78d6;--track:#f0efec;--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;--link:#1c5cab}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#f0efec;--ink-2:#c3c2b7;--ink-3:#9a998f;--hair:#2c2c2a;--series:#3987e5;--track:#262624;--link:#86b6ef}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink-2:#c3c2b7;--ink-3:#9a998f;
--hair:#2c2c2a;--series:#3987e5;--track:#262624;--link:#86b6ef}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:20px 16px 48px}h1{font-size:22px;margin:0 0 2px}h2{font-size:15px;margin:0 0 10px;color:var(--ink-2);font-weight:600}
.sub{color:var(--ink-3);font-size:13px;margin-bottom:18px}.grid{display:grid;gap:12px}.k{grid-template-columns:repeat(auto-fit,minmax(140px,1fr))}
.two{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}.card{background:var(--surface);border:1px solid var(--hair);border-radius:10px;padding:14px 16px;min-width:0}
.kpi .v{font-size:28px;font-weight:650;font-variant-numeric:tabular-nums}.kpi .l{color:var(--ink-2);font-size:13px}.kpi .h{color:var(--ink-3);font-size:12px}
section,.grid{margin-top:14px}.grid>section{margin-top:0}td:nth-child(-n+2){white-space:nowrap}.alert{display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-top:1px solid var(--hair)}.alert:first-of-type{border-top:0}
.dot{width:10px;height:10px;border-radius:50%;flex:0 0 10px;margin-top:6px}.lvl{font-size:12px;color:var(--ink-3);white-space:nowrap}
.sig{padding:10px 0;border-top:1px solid var(--hair)}.sig:first-of-type{border-top:0}.chip{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.04em;
padding:1px 7px;border-radius:999px;border:1px solid var(--hair);color:var(--ink);margin-right:6px}.meta{color:var(--ink-3);font-size:12px}
.why{margin:3px 0}.next{color:var(--ink-2);font-size:13px}a{color:var(--link);word-break:break-all}
.bar{display:grid;grid-template-columns:minmax(90px,150px) 1fr 44px;gap:8px;align-items:center;margin:5px 0;font-size:13px}
.bar .n{color:var(--ink-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.bar .t{position:relative;height:14px}
.bar .f{position:absolute;left:0;top:0;bottom:0;background:var(--series);border-radius:0 4px 4px 0;min-width:2px}
.bar .c{text-align:right;color:var(--ink-2);font-variant-numeric:tabular-nums}.bar:hover .f,.bar:focus .f{filter:brightness(1.12)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:6px 6px;border-top:1px solid var(--hair);vertical-align:top}
th{color:var(--ink-3);font-weight:600;border-top:0}.tbl{overflow-x:auto}.empty{color:var(--ink-3);font-size:13px}
#tip{position:fixed;pointer-events:none;background:var(--surface);color:var(--ink);border:1px solid var(--hair);border-radius:8px;padding:6px 9px;
font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.15);display:none;max-width:260px;z-index:9}
details summary{cursor:pointer;color:var(--ink-2);font-size:13px;margin-top:8px}
"""

TIP_JS = """
const tip=document.getElementById('tip');
document.querySelectorAll('[data-tip]').forEach(el=>{
 const show=e=>{tip.textContent=el.dataset.tip;tip.style.display='block';
  const r=el.getBoundingClientRect();const x=(e&&e.clientX)||r.left+r.width/2,y=(e&&e.clientY)||r.top;
  tip.style.left=Math.min(x+12,innerWidth-tip.offsetWidth-8)+'px';tip.style.top=Math.max(y-tip.offsetHeight-10,8)+'px'};
 el.addEventListener('mousemove',show);el.addEventListener('focus',()=>show());
 el.addEventListener('mouseleave',()=>tip.style.display='none');el.addEventListener('blur',()=>tip.style.display='none');});
"""


def _e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _link(url: str | None) -> str:
    if not url or not re.match(r"^https?://", url):
        return _e(url)
    short = re.sub(r"^https?://(www\.)?", "", url)[:70]
    return f'<a href="{_e(url)}" rel="noopener noreferrer" target="_blank">{_e(short)}</a>'


def _decisions(ws: WS) -> list[list[str]]:
    p = ws.root / "decisiones.md"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\|\s*D-\d+", line):
            cells = [re.sub(r"\*\*|`", "", c).strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and "<" not in cells[2]:
                rows.append([cells[0], cells[1], cells[2], cells[5]])
    return rows


def _bars(counts: list[tuple[str, int, str]]) -> str:
    if not counts:
        return '<p class="empty">Todavía no hay datos.</p>'
    top = max(n for _, n, _ in counts) or 1
    out = []
    for name, n, tip in counts:
        out.append(f'<div class="bar" tabindex="0" data-tip="{_e(tip)}"><span class="n">{_e(name)}</span>'
                   f'<span class="t"><span class="f" style="width:{100 * n / top:.1f}%"></span></span>'
                   f'<span class="c">{n}</span></div>')
    return "".join(out)


def dashboard(ws: WS) -> str:
    now = today()
    items = ws.items()
    log = ws.log()
    latest = ws.latest()
    done = ws.processed()
    pend = sum(1 for i in items if i not in done)
    recent = [r for r in latest.values() if (d := _date(r.get("fecha"))) and (now - d).days <= 30]
    signals = sorted((r for r in recent if r.get("veredicto") in ("ADOPT", "TEST", "CANDIDATO", "WATCH")),
                     key=lambda r: (("ADOPT", "TEST", "CANDIDATO", "WATCH").index(r["veredicto"]), r.get("fecha", "")))
    exps = experiments(ws)
    al = alerts(ws)
    vcount = Counter(r.get("veredicto") for r in latest.values())
    passed = sum(vcount[v] for v in PASSING)

    # themes: links per tag, with pass rate among judged
    tag_all, tag_judged, tag_pass = Counter(), Counter(), Counter()
    for iid, it in items.items():
        for t in it.get("tags", []):
            tag_all[t] += 1
            if iid in latest:
                tag_judged[t] += 1
                tag_pass[t] += latest[iid].get("veredicto") in PASSING
    themes = [(t, n, f"{t}: {n} links · {tag_judged[t]} juzgados · "
               + (f"{round(100 * tag_pass[t] / tag_judged[t])}% pasó el filtro" if tag_judged[t] else "sin juzgar"))
              for t, n in tag_all.most_common(12)]

    # sources: X accounts by links, with signal rate
    src_all, src_judged, src_pass = Counter(), Counter(), Counter()
    for iid, it in items.items():
        m = re.match(r"https://x\.com/([^/]+)/status/", it.get("url", ""))
        if m:
            a = "@" + m.group(1)
            src_all[a] += 1
            if iid in latest:
                src_judged[a] += 1
                src_pass[a] += latest[iid].get("veredicto") in PASSING
    sources = [(a, n, f"{a}: {n} links · " + (f"{src_pass[a]}/{src_judged[a]} con señal" if src_judged[a] else "sin juzgar"))
               for a, n in src_all.most_common(10)]

    def kpi(v, label, hint=""):
        return f'<div class="card kpi"><div class="v">{_e(v)}</div><div class="l">{_e(label)}</div><div class="h">{_e(hint)}</div></div>'

    k = "".join([
        kpi(pend, "pendientes", "en el inbox sin juzgar"),
        kpi(len(latest), "juzgados", f"{passed} pasaron el filtro"),
        kpi(vcount["ADOPT"] + vcount["TEST"], "señales", "ADOPT + TEST"),
        kpi(f"{len(exps)}/{WIP_MAX}", "experimentos", "activos (máx 3)"),
    ])
    alert_html = "".join(
        f'<div class="alert"><span class="dot" style="background:var(--{a["nivel"]})"></span>'
        f'<span class="lvl">{ICON.get(a["nivel"], "")} {_e(a["tipo"])}</span><span>{_e(a["texto"])}</span></div>' for a in al
    ) or '<p class="empty">✓ Sin alertas. Nada que corregir.</p>'
    sig_html = "".join(
        f'<div class="sig"><span class="chip">{_e(r["veredicto"])}</span><span class="meta">{_e(r.get("capa"))} / '
        f'{_e(r.get("capacidad"))} · evidencia {_e(r.get("evidencia"))} · {_e(r.get("fecha"))}</span>'
        f'<div class="why">{_e(r.get("por_que"))}</div><div class="next">→ {_e(r.get("proximo_paso"))}'
        + (f' · revisar si: {_e(r.get("revisar_si"))}' if r.get("revisar_si") else "")
        + f'</div><div class="meta">{_link(r.get("url"))}</div></div>' for r in signals[:15]
    ) or '<p class="empty">Ninguna señal en 30 días. El silencio también es un resultado.</p>'
    exp_html = "".join(
        f'<div class="sig"><span class="chip">{_e(e["id"])}</span><b>{_e(e["titulo"])}</b>'
        f'<div class="meta">{_e(e.get("capacidad"))} · corte {_e(e.get("corte"))}'
        + (f' · {(c - now).days} días' if (c := _date(e.get("corte"))) else "") + f' · {_e(e.get("estado"))}</div></div>'
        for e in exps
    ) or '<p class="empty">Sin experimentos activos.</p>'
    dec = _decisions(ws)
    dec_html = ("<div class='tbl'><table><tr><th>id</th><th>fecha</th><th>decisión</th><th>qué la revertiría</th></tr>"
                + "".join(f"<tr><td>{_e(a)}</td><td>{_e(b)}</td><td>{_e(c)}</td><td>{_e(d)}</td></tr>" for a, b, c, d in dec)
                + "</table></div>") if dec else '<p class="empty">Sin decisiones cargadas.</p>'
    funnel = [("guardados", len(items)), ("juzgados", len(latest)), ("pasaron el filtro", passed),
              ("TEST + ADOPT", vcount["TEST"] + vcount["ADOPT"])]
    funnel_html = _bars([(n, v, f"{n}: {v}") for n, v in funnel])
    vtable = "".join(f"<tr><td>{v}</td><td>{vcount.get(v, 0)}</td></tr>" for v in VERDICTS)

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Radar de Leverage</title><style>{CSS}</style></head><body><main>
<h1>Radar de Leverage</h1><div class="sub">{_e(now.isoformat())} · semana {_e(iso_week(now))} · avisa solo si algo cambia una decisión, mejora el stack o abre una apuesta</div>
<div class="grid k">{k}</div>
<section class="card"><h2>Alertas</h2>{alert_html}</section>
<div class="grid two"><section class="card"><h2>Señales (30 días)</h2>{sig_html}</section>
<section class="card"><h2>Experimentos activos</h2>{exp_html}</section></div>
<div class="grid two"><section class="card"><h2>Embudo</h2>{funnel_html}
<details><summary>Ver como tabla</summary><table><tr><th>veredicto</th><th>ítems</th></tr>{vtable}</table></details></section>
<section class="card"><h2>Temas que más guardás</h2>{_bars(themes)}</section></div>
<div class="grid two"><section class="card"><h2>Cuentas que más guardás</h2>{_bars(sources)}</section>
<section class="card"><h2>Decisiones vigentes</h2>{dec_html}</section></div>
</main><div id="tip" role="tooltip"></div><script>{TIP_JS}</script></body></html>"""


# ------------------------------------------------------------------- cli ---

def _rows_from(args) -> list[dict]:
    raw = args.json if args.json is not None else sys.stdin.read()
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        return json.loads(raw)
    return [json.loads(l) for l in raw.splitlines() if l.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ws", type=Path, default=Path(os.environ.get("RADAR_WS", ".")), help="radar workspace (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest"); p.add_argument("export", type=Path)
    p = sub.add_parser("capture"); p.add_argument("url"); p.add_argument("--note", default="")
    p.add_argument("--source", default="chat", choices=("chat", "scan"))
    p = sub.add_parser("next"); p.add_argument("-n", type=int, default=10); p.add_argument("--fetch", action="store_true")
    sub.add_parser("pending")
    p = sub.add_parser("log"); p.add_argument("--json"); p.add_argument("--force", action="store_true")
    p = sub.add_parser("alerts"); p.add_argument("--json", action="store_true")
    sub.add_parser("digest-data")
    p = sub.add_parser("exp"); es = p.add_subparsers(dest="exp_cmd", required=True)
    es.add_parser("list")
    o = es.add_parser("open"); o.add_argument("--titulo", required=True); o.add_argument("--hipotesis", required=True)
    o.add_argument("--criterio", required=True); o.add_argument("--capacidad", required=True)
    o.add_argument("--origen", required=True); o.add_argument("--corte"); o.add_argument("--timebox", default="2 sesiones × 40 min")
    c = es.add_parser("close"); c.add_argument("exp_id"); c.add_argument("resultado"); c.add_argument("aprendizaje")
    p = sub.add_parser("label"); p.add_argument("target", help="id or url"); p.add_argument("veredicto")
    p.add_argument("--por-que", default="")
    sub.add_parser("gold-from-notes", help="weak labels from your own notes (recall test)")
    p = sub.add_parser("eval"); p.add_argument("--etapa", choices=STAGES)
    p.add_argument("--gold", type=Path, help="labels file (default evals/gold.jsonl)")
    p.add_argument("--compare", nargs=2, type=Path, metavar=("LOG_A", "LOG_B")); p.add_argument("--json", action="store_true")
    p = sub.add_parser("dashboard"); p.add_argument("-o", "--out", type=Path)
    p = sub.add_parser("demo", help="create a synthetic workspace to try everything"); p.add_argument("dir", type=Path)
    sub.add_parser("self-test")
    a = ap.parse_args(argv)
    ws = WS(a.ws)

    if a.cmd == "self-test":
        return self_test()
    if a.cmd == "demo":
        if a.dir.exists() and any(a.dir.iterdir()):
            print(f"{a.dir} no está vacío; elegí una carpeta nueva", file=sys.stderr)
            return 1
        d = make_demo(a.dir)
        (d.root / "dashboard.html").write_text(dashboard(d), encoding="utf-8")
        print(f"demo lista en {d.root} · abrí {d.root / 'dashboard.html'}")
        return 0
    if a.cmd == "ingest":
        its, th = wa.ingest(a.export, ws.inbox_dir, ws.processed_file)
        new = [i for i in its if i.status == "new"]
        top = Counter(t for i in new for t in i.tags).most_common(5)
        print(f"{len(its)} links ({len(new)} nuevos), {len(th)} notas propias -> {ws.inbox_dir}")
        print("temas: " + ", ".join(f"{t} {n}" for t, n in top))
        print("compartidos más de una vez: " + str(sum(i.times_shared > 1 for i in its)))
        return 0
    if a.cmd == "capture":
        url = wa.canonical_url(a.url)
        iid = item_id(url)
        prev = ws.latest().get(iid)
        if iid in ws.items() or prev:
            print(json.dumps({"duplicado": True, "id": iid, "url": url, "ultimo_veredicto": prev}, ensure_ascii=False))
            return 0
        notes = [a.note] if a.note.strip() else []
        it = {"id": iid, "url": url, "source": a.source, "first_seen": dt.datetime.now().isoformat(timespec="seconds"),
              "last_seen": dt.datetime.now().isoformat(timespec="seconds"), "times_shared": 1, "notes": notes,
              "tags": wa.tags_for(" ".join(notes) + " " + url), "priority": wa.priority_for(" ".join(notes), 1), "status": "new"}
        it["layers"] = sorted({wa.LAYER[t] for t in it["tags"] if t in wa.LAYER})
        ws.append_jsonl(ws.capturas, [it])
        print(json.dumps({"duplicado": False, **it}, ensure_ascii=False))
        return 0
    if a.cmd == "next":
        batch = ws.pending()[: a.n]
        if a.fetch:
            import fetch_post
            for it in batch:
                try:
                    f = fetch_post.fetch(it["url"])
                    it["contenido"] = {k: v for k, v in f.items() if k != "url"}
                    if isinstance(it["contenido"].get("text"), str):
                        it["contenido"]["text"] = it["contenido"]["text"][:1500]
                except Exception as e:  # noqa: BLE001
                    it["contenido"] = {"ok": False, "error": str(e)}
        for it in batch:
            print(json.dumps({k: it.get(k) for k in ("id", "url", "notes", "tags", "layers", "priority", "times_shared",
                                                     "source", "first_seen", "contenido") if k in it}, ensure_ascii=False))
        print(f"# {len(batch)} de {len(ws.pending())} pendientes", file=sys.stderr)
        return 0
    if a.cmd == "pending":
        pend = ws.pending()
        print(f"pendientes={len(pend)}" + (f" primero={pend[0]['id']}" if pend else ""))
        return 0
    if a.cmd == "log":
        try:
            rows = log_verdicts(ws, _rows_from(a), force=a.force)
        except ValueError as e:
            print("NO SE REGISTRÓ NADA. Corregí y reenviá:\n" + str(e), file=sys.stderr)
            return 1
        c = Counter(r["veredicto"] for r in rows)
        print(f"registrados {len(rows)}: " + ", ".join(f"{k} {v}" for k, v in c.items()) + f" · pendientes {len(ws.pending())}")
        return 0
    if a.cmd == "alerts":
        al = alerts(ws)
        if a.json:
            print(json.dumps(al, ensure_ascii=False, indent=1))
        elif al:  # empty stdout = silent cron run
            print("Radar · alertas\n" + "\n".join(f"{ICON.get(x['nivel'], '')} {x['texto']}" for x in al))
        return 0
    if a.cmd == "digest-data":
        print(json.dumps(digest_data(ws), ensure_ascii=False, indent=1))
        return 0
    if a.cmd == "exp":
        if a.exp_cmd == "list":
            print(json.dumps(experiments(ws), ensure_ascii=False, indent=1))
        elif a.exp_cmd == "open":
            print(exp_open(ws, a.titulo, a.hipotesis, a.criterio, a.capacidad, a.corte, a.origen, a.timebox))
        else:
            exp_close(ws, a.exp_id, a.resultado, a.aprendizaje)
            print(f"{a.exp_id} cerrado: {a.resultado.upper()}")
        return 0
    if a.cmd == "label":
        v = a.veredicto.upper()
        if v not in FINAL:
            print(f"veredicto debe ser uno de {', '.join(FINAL)}", file=sys.stderr)
            return 1
        iid = item_id(a.target) if a.target.startswith("http") else a.target
        it = ws.items().get(iid, {})
        ws.append_jsonl(ws.gold, [{"id": iid, "url": it.get("url") or (a.target if a.target.startswith("http") else None),
                                   "veredicto": v, "por_que": a.por_que, "fecha": today().isoformat()}])
        print(f"etiqueta guardada: {iid} = {v} ({len(ws.read_jsonl(ws.gold))} en evals/gold.jsonl)")
        return 0
    if a.cmd == "eval":
        if a.compare:
            res = agreement(latest_by_id(WS.read_jsonl(a.compare[0]), a.etapa), latest_by_id(WS.read_jsonl(a.compare[1]), a.etapa))
        else:
            gold = list(latest_by_id(ws.read_jsonl(a.gold or ws.gold)).values())
            if not gold:
                print("No hay etiquetas. Usá `radar.py label <id> <VEREDICTO>` cuando corrijas al radar.", file=sys.stderr)
                return 1
            res = evaluate(gold, latest_by_id(ws.log(), a.etapa))
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            for k, v in res.items():
                if isinstance(v, list):
                    print(f"{k}: {len(v)}")
                    for d in v[:20]:
                        print("  - " + " · ".join(f"{kk}={vv}" for kk, vv in d.items() if vv))
                else:
                    print(f"{k}: {v}")
        return 0
    if a.cmd == "gold-from-notes":
        rows = gold_from_notes(ws)
        print(f"{len(rows)} etiquetas débiles -> evals/gold-debil.jsonl · medí con: radar.py eval --gold evals/gold-debil.jsonl")
        return 0
    if a.cmd == "dashboard":
        out = a.out or ws.root / "dashboard.html"
        out.write_text(dashboard(ws), encoding="utf-8")
        print(out)
        return 0
    return 1


# ------------------------------------------------------------------- demo ---

def make_demo(root: Path) -> WS:
    """Synthetic workspace (fake accounts and links) to see the dashboard before real data exists."""
    import random
    rnd = random.Random(7)
    ws = WS(root)
    ws.inbox_dir.mkdir(parents=True, exist_ok=True)
    now = today()
    themes = [("router-model", "nuevo router de modelos", 9), ("loop-engineering", "loop con verificador", 7),
              ("memory-knowledge", "obsidian para agentes", 6), ("content-video", "video con avatar", 6),
              ("search-geo", "geo para marcas", 4), ("evals-quality", "evals de agentes", 4),
              ("infra-vps", "vps barato", 3), ("growth-sales", "outreach con agentes", 3)]
    accounts = ["@cuenta_a", "@cuenta_b", "@cuenta_c", "@cuenta_d", "@cuenta_e", "@cuenta_f"]
    items, n = [], 0
    for tag, note, count in themes:
        for k in range(count):
            n += 1
            acc = accounts[(n * 7 + k) % len(accounts)][1:]
            url = f"https://x.com/{acc}/status/{1000 + n}"
            days = rnd.randint(0, 9) if tag == "router-model" else rnd.randint(3, 60)
            items.append({"id": item_id(url), "url": url, "source": "x", "notes": [note], "tags": [tag],
                          "layers": [wa.LAYER.get(tag, "orquestacion")], "times_shared": 1, "priority": "normal",
                          "first_seen": (now - dt.timedelta(days=days)).isoformat() + "T09:00:00", "status": "new"})
    WS.append_jsonl(ws.inbox, items)
    verdicts = []
    picks = {"loop-engineering": [("TEST", "orquestacion", "agent-loop-harness", "stack", "demo",
                                   "Verificador elegido antes de correr: reemplaza revisar a mano los PRs nocturnos",
                                   "Correr 1 tarea real con contrato + tests y medir intervenciones")],
             "evals-quality": [("ADOPT", "aprendizaje", "evals-calidad", "decision", "verificado",
                                "Golden set de 30 casos detectó 4 regresiones que no veíamos",
                                "Sumarlo al checklist de cada release")],
             "search-geo": [("WATCH", "distribucion", "search-visibility", "apuesta", "anecdota",
                             "Menciones de marca en foros parecen pesar en respuestas de IA",
                             "Medir menciones actuales de 1 cliente", "un estudio independiente lo replique")],
             "memory-knowledge": [("CANDIDATO", "orquestacion", "memory", "stack", "demo",
                                   "Plugin que deja a los agentes leer el vault sin sincronizar a mano",
                                   "Probar con 1 proyecto")]}
    for it in items:
        tag = it["tags"][0]
        if picks.get(tag):
            v, capa, cap, q, ev, why, nxt, *rev = picks[tag].pop()
            verdicts.append({"id": it["id"], "url": it["url"], "veredicto": v, "etapa": "capture" if v != "CANDIDATO" else "triage",
                             "capa": capa, "capacidad": cap, "pregunta": q, "evidencia": ev, "por_que": why,
                             "proximo_paso": nxt, "revisar_si": rev[0] if rev else None})
        elif rnd.random() < 0.6:
            verdicts.append({"id": it["id"], "url": it["url"], "veredicto": "DROP", "etapa": "triage", "capa": "ninguna",
                             "pregunta": "ninguna", "por_que": "Repite algo que ya está decidido"})
    log_verdicts(ws, verdicts, force=True)
    ws.experiments.write_text(
        "# Experimentos\n\n## Activos\n\n"
        f"### EXP-001 · Loop con verificador para tareas nocturnas\n\n- Capacidad: orquestacion / agent-loop-harness\n"
        f"- Hipótesis: con contrato + tests, menos intervenciones manuales\n- Criterio de éxito: ≤1 intervención por tarea\n"
        f"- Timebox: 2 sesiones × 40 min · Fecha de corte: {(now + dt.timedelta(days=6)).isoformat()}\n- Origen: demo\n- Estado: en curso\n\n"
        "## Cerrados\n\n| id | fecha | resultado | aprendizaje (1 línea) |\n|---|---|---|---|\n", encoding="utf-8")
    (root / "decisiones.md").write_text(
        "# Decisiones vigentes\n\n| id | fecha | decisión | por qué | evidencia | qué la revertiría |\n|---|---|---|---|---|---|\n"
        "| D-001 | 2026-08-02 | Modelo barato para el 80%, fuerte para el 20% | costo | sin-fuente | el barato genera más retrabajo del que ahorra |\n"
        "| D-002 | 2026-09-08 | Conocimiento en markdown + Git | simplicidad | sin-fuente | los agentes no pueden leer el vault |\n",
        encoding="utf-8")
    return ws


# ------------------------------------------------------------------ tests ---

def self_test() -> int:
    os.environ["RADAR_TODAY"] = "2026-11-14"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "inbox").mkdir()
        ws = WS(root)
        u1, u2, u3 = ("https://x.com/a/status/1?s=48", "https://github.com/o/r", "https://x.com/b/status/2")
        rows = []
        for i, (u, note, day) in enumerate([(u1, "Hermes loop", "2026-11-10"), (u2, "repo 10/10", "2026-11-11"),
                                            (u3, "", "2026-01-01")]):
            cu = wa.canonical_url(u)
            rows.append({"id": item_id(u), "url": cu, "notes": [note] if note else [], "tags": wa.tags_for(note + " " + cu),
                         "first_seen": f"{day}T10:00:00", "priority": "high", "status": "new", "source": "x"})
        WS.append_jsonl(ws.inbox, rows)
        assert len(ws.pending()) == 3
        # validation rejects contradictions and writes nothing
        bad = {"url": u1, "veredicto": "ADOPT", "etapa": "capture", "capa": "orquestacion", "pregunta": "stack",
               "capacidad": "memory", "evidencia": "anecdota", "por_que": "x", "proximo_paso": "y"}
        try:
            log_verdicts(ws, [bad])
            raise AssertionError("ADOPT with anecdota must fail")
        except ValueError as e:
            assert "ADOPT requiere" in str(e)
        assert not ws.log_file.exists()
        try:
            log_verdicts(ws, [{"url": u1, "veredicto": "WATCH", "etapa": "triage", "capa": "orquestacion",
                               "pregunta": "ninguna", "capacidad": "m", "evidencia": "demo", "por_que": "x", "proximo_paso": "y"}])
            raise AssertionError("WATCH needs revisar_si and a yes question")
        except ValueError as e:
            assert "revisar_si" in str(e) and "contradictorio" in str(e)
        ok = [{"url": u1, "veredicto": "candidato", "etapa": "triage", "capa": "Orquestación", "pregunta": "stack",
               "capacidad": "agent-loop-harness", "evidencia": "demo", "por_que": "loop externo", "proximo_paso": "probar"},
              {"id": item_id(u3), "veredicto": "DROP", "etapa": "triage", "capa": "ninguna", "pregunta": "ninguna",
               "por_que": "no sé para qué sirve"}]
        log_verdicts(ws, ok)
        assert len(ws.pending()) == 1 and ws.log()[0]["capa"] == "orquestacion" and ws.log()[0]["veredicto"] == "CANDIDATO"
        assert main(["--ws", tmp, "pending"]) == 0
        # digest data sees the candidate
        dd = digest_data(ws)
        assert [c["id"] for c in dd["candidatos"]] == [item_id(u1)] and dd["semana"] == "2026-46", dd
        # experiments: open up to 3, 4th refused, close moves to table
        ws.experiments.write_text("# Experimentos\n\n## Activos\n\n### EXP-001 · <título>\n\n- Estado: x\n\n"
                                  "## Cerrados\n\n| id | fecha | resultado | aprendizaje (1 línea) |\n|---|---|---|---|\n", encoding="utf-8")
        assert experiments(ws) == []
        ids = [exp_open(ws, f"t{i}", "h", "c", "cap", "2026-11-01" if i == 0 else None, "o") for i in range(3)]
        assert ids == ["EXP-001", "EXP-002", "EXP-003"], ids
        try:
            exp_open(ws, "t4", "h", "c", "cap", None, "o")
            raise AssertionError("WIP limit")
        except SystemExit as e:
            assert "sin cupo" in str(e)
        try:
            log_verdicts(ws, [{"url": u2, "veredicto": "TEST", "etapa": "capture", "capa": "orquestacion", "pregunta": "stack",
                               "capacidad": "c", "evidencia": "demo", "por_que": "x", "proximo_paso": "y"}])
            raise AssertionError("TEST without WIP room must fail")
        except ValueError as e:
            assert "sin cupo" in str(e)
        al = alerts(ws)
        assert any(x["tipo"] == "experimento-vencido" and "EXP-001" in x["texto"] for x in al), al
        exp_close(ws, "EXP-001", "drop", "no movió la aguja")
        assert [e["id"] for e in experiments(ws)] == ["EXP-002", "EXP-003"]
        assert "| EXP-001 · t0 | 2026-11-14 | DROP | no movió la aguja |" in ws.experiments.read_text(encoding="utf-8")
        # rabbit hole: 5 fresh links on one tag, none tried
        WS.append_jsonl(ws.capturas, [{"id": f"r{i}", "url": f"https://x.com/z/status/{i}", "tags": ["router-model"],
                                      "first_seen": "2026-11-12T09:00:00", "notes": ["Jev"]} for i in range(5)])
        assert any(x["tipo"] == "rabbit-hole" and "router-model" in x["texto"] for x in alerts(ws))
        # stalled radar
        os.environ["RADAR_TODAY"] = "2026-11-30"
        assert any(x["tipo"] == "radar-parado" for x in alerts(ws))
        os.environ["RADAR_TODAY"] = "2026-11-14"
        # evals
        gold = [{"id": item_id(u1), "veredicto": "TEST"}, {"id": item_id(u3), "veredicto": "DROP"},
                {"id": "nope", "veredicto": "DROP"}]
        res = evaluate(gold, ws.latest())
        assert res["filtro_acierto"] == 1.0 and res["sin_juicio"] == 1 and res["veredicto_exacto"] == 1.0, res
        a_run = {"x": {"veredicto": "DROP"}, "y": {"veredicto": "TEST"}, "z": {"veredicto": "WATCH"}}
        b_run = {"x": {"veredicto": "DROP"}, "y": {"veredicto": "CANDIDATO"}, "z": {"veredicto": "DROP"}}
        ag = agreement(a_run, b_run)
        assert ag["comunes"] == 3 and ag["acuerdo_filtro"] == round(2 / 3, 3) and len(ag["desacuerdos_filtro"]) == 1, ag
        weak = gold_from_notes(ws)
        assert [w["id"] for w in weak] == [item_id(u2)] and "10/10" in weak[0]["por_que"], weak
        res = evaluate(weak, ws.latest())
        assert res["sin_juicio"] == 1 and res["veredicto_exacto"] is None, res
        # capture dedupes and dashboard renders escaped HTML
        assert main(["--ws", tmp, "capture", u1, "--note", "<script>x</script>"]) == 0
        assert len(ws.read_jsonl(ws.capturas)) == 5  # duplicate not appended
        assert main(["--ws", tmp, "capture", "https://example.com/<b>", "--note", "<script>x</script>"]) == 0
        page = dashboard(ws)
        assert "<script>x</script>" not in page and "Radar de Leverage" in page and "EXP-002" in page
    print("self-test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
