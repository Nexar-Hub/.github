#!/usr/bin/env python3
"""Auditor de copy con Prospect Theory (ES/EN). Solo stdlib.

Recorre archivos de texto, UI, traducciones y templates y marca los lugares
donde la arquitectura de la decisión se puede mejorar según el playbook
(docs/prospect-theory/PLAYBOOK.md). Cada hallazgo es una HIPÓTESIS a testear,
no un error: el auditor arma la lista de qué probar y por qué.

Uso:
    python3 tools/copy_audit.py RUTA [RUTA ...]           # texto, un bloque por hallazgo
    python3 tools/copy_audit.py src/ --format md > audit.md
    python3 tools/copy_audit.py src/ --format json
    echo "Ganá 300 USD al año" | python3 tools/copy_audit.py -
    python3 tools/copy_audit.py src/ --only PT01,PT04 --strict   # exit 1 si hay hallazgos
    python3 tools/copy_audit.py --list-rules

Para silenciar una línea puntual, agregale el comentario:  prospect-audit: ignore
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Iterator, Sequence

PLAYBOOK = "docs/prospect-theory/PLAYBOOK.md"

TEXT_EXTENSIONS = {
    ".md", ".mdx", ".txt", ".html", ".htm", ".json", ".yml", ".yaml", ".js", ".jsx",
    ".ts", ".tsx", ".vue", ".svelte", ".astro", ".po", ".pot", ".strings", ".xml",
    ".csv", ".liquid", ".hbs", ".ejs", ".njk", ".php", ".erb", ".arb", ".xliff", ".xlf",
    ".properties", ".resx", ".rtf", ".tex",
}
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", ".next", ".nuxt", "vendor",
    "coverage", "__pycache__", ".venv", "venv", ".cache", ".turbo", ".vercel",
}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock"}
MAX_BYTES = 2_000_000
IGNORE_MARK = "prospect-audit: ignore"

F = re.IGNORECASE | re.UNICODE

# Montos, porcentajes o placeholders de monto en templates ({{fee}}, ${fee}, %s).
MONEY = re.compile(
    r"(?:US\$|R\$|\$|€|£)\s?\d"
    r"|\d[\d.,]*\s?(?:%|usd[ct]?|ars|eur|mxn|cop|clp|brl|pesos?|d[oó]lares|dollars?)\b"
    r"|\{\{\s*[\w.]+\s*\}\}|\$\{[\w.]+\}|\{[\w.]+\}|%[sd]|%\(\w+\)s",
    F,
)

COST_CATEGORIES: list[tuple[str, re.Pattern[str]]] = [
    ("comision", re.compile(r"\bcomisi[oó]n(?:es)?\b|\bcommissions?\b", F)),
    ("spread", re.compile(r"\bspreads?\b", F)),
    ("red", re.compile(
        r"\b(?:fee|costo|cargo|tarifa)s? (?:de|por) (?:la )?red\b|\bnetwork fees?\b"
        r"|\bgas fees?\b|\bfee de gas\b|\bcosto de gas\b", F)),
    ("servicio", re.compile(
        r"\b(?:fee|cargo|costo|tarifa)s? (?:de|por) (?:servicio|procesamiento|mantenimiento)\b"
        r"|\b(?:service|processing|maintenance|platform) fees?\b", F)),
    ("cambio", re.compile(
        r"\b(?:costo|cargo|comisi[oó]n|fee) (?:de|por) (?:conversi[oó]n|cambio)\b"
        r"|\b(?:fx|conversion|exchange) fees?\b", F)),
    ("generico", re.compile(
        r"\bfees?\b|\bcharges?\b(?<!in charge)|\btarifas?\b"
        r"|(?<!a )(?<!hace )(?<!hacer )(?<!hacerse )(?<!hago )\bcargos?\b", F)),
]

REBATE = re.compile(
    r"\bcash ?back\b|\breintegros?\b|\bbonificaci[oó]n(?:es)?\b|\brecompensas?\b"
    r"|\brewards?\b|\bdevoluci[oó]n\b|\brebates?\b", F)
NETTING = re.compile(
    r"\bdescuento (?:del|de tu|sobre (?:el|tu))\b|\bse (?:te )?descuentan?\b|\bdescontad[oa]s? de\b"
    r"|(?<!al )(?<!lo )(?<!a )\bmenos\b|\bneto\b|\bnetead[oa]\b|\bdeducted from\b|\bnet of\b"
    r"|\boff your (?:bill|fee|statement|charge)\b|\bminus\b"
    r"|\bapplied (?:to|against) your (?:bill|statement|fee|charge)\b"
    r"|\bse aplica(?:n)? (?:a|al|sobre) (?:tu|el) (?:cargo|resumen|factura|cuota)\b", F)

AGG_GAIN = re.compile(
    r"\b(?:ganaste|generaste|obtuviste|cobraste|rendiste|acumulaste|you(?:'ve| have)? earned"
    r"|you made)\b.{0,40}\b(?:mes|mensual(?:es)?|este a[nñ]o|en el a[nñ]o|acumulad[oa]s?|total"
    r"|month(?:ly)?|this year|year[- ]to[- ]date|ytd|so far)\b"
    r"|\b(?:rendimientos?|intereses|ganancias?|earnings|interest earned|returns)\s+"
    r"(?:del mes|mensual(?:es)?|acumulad[oa]s?|totales?|de este mes|this month|monthly"
    r"|accumulated|year[- ]to[- ]date|ytd)\b"
    r"|\bresumen mensual de (?:rendimientos|intereses|ganancias)\b|\bmonthly (?:earnings|interest|yield) (?:summary|report)\b",
    F)

GAIN_FRAME = re.compile(
    r"\b(?:gan[aá]|gan[aá]s|ganar[ií]as|pod[eé]s ganar|podr[ií]as ganar|empez[aá] a ganar"
    r"|gana|ganar hasta|ganate|earn|start earning|you(?:'ll| will| could| can) earn"
    r"|get up to|make up to)\b(?P<rest>.{0,50})", F)
GAIN_OBJECT = re.compile(
    r"rendimient|inter[eé]s|intereses|yield|apy|apr|tna|tea|\binterest\b|" + MONEY.pattern, F)

# Comparaciones de plata/tiempo contra el status quo: siempre se marcan.
STATUS_QUO = re.compile(
    r"\bm[aá]s (?:r[aá]pid[oa]s?|barat[oa]s?|econ[oó]mic[oa]s?)\b"
    r"|\b(?:faster|cheaper|more affordable|lower[- ]cost)\b"
    r"|\bahorr[aá]s?\b(?: hasta)? (?:un |el )?(?:\d|\$|us\$|usd)"
    r"|\bsave (?:up to |over )?(?:\d|\$|us\$|usd)", F)
# Comparaciones blandas: solo cuentan si hay contexto de inercia en la linea.
STATUS_QUO_SOFT = re.compile(
    r"\bm[aá]s (?:simples?|f[aá]cil(?:es)?|conveniente|segur[oa]s?)\b|\b(?:easier|simpler|safer)\b", F)
INERTIA_CONTEXT = re.compile(
    r"\bswift\b|\bwire\b|\bbanco\b|\bbank\b|\befectivo\b|\bcash\b(?! ?back)|\bremesa|\bremittance"
    r"|\btransferencia internacional\b|\bd[oó]lar(?:iz|es)|\bstablecoin|\busdt\b|\busdc\b|\bplazo fijo\b", F)

RAFFLE = re.compile(
    r"\bsorteos?\b|\bsorteamos\b|\bsortea\b|\braffles?\b|\bsweepstakes?\b|\bgiveaways?\b"
    r"|\bpremio mayor\b|\bjackpot\b|\bpozo\b", F)
SMALL_SURE = re.compile(
    r"\b(?:te regalamos|regalo de|bono de|bonus of|llevate|recib[ií]s|get|receive|you(?:'ll| will) get)\b"
    r".{0,25}(?:US\$|\$|€|usd\s?|ars\s?)\s?\d{1,3}(?![\d.,]*\d{3})\b", F)
PROMO_CONTEXT = re.compile(
    r"\breferid|\breferí|\binvit[aá]|\binvite|\brefer|\bpromo|\bbienvenida|\bwelcome|\bsign[- ]?up"
    r"|\bregistr|\bonboarding|\bprimer(?:a)? (?:dep[oó]sito|transferencia|compra)|\bfirst (?:deposit|transfer)", F)

FINE_PRINT = re.compile(
    r"\b(?:gratis|sin (?:costo|comisi[oó]n(?:es)?|cargo)s?|free|no fees?|zero fees?|0 ?%)\s?\*", F)


@dataclass(frozen=True)
class Rule:
    id: str
    slug: str
    lever: str
    title: str
    why: str
    suggestion: str
    anchor: str


RULES: dict[str, Rule] = {r.id: r for r in [
    Rule("PT01", "costos-desglosados", "Edición hedónica: juntá las pérdidas",
         "Costos desglosados en varias líneas",
         "La rama de pérdidas es convexa: tres cargos chicos duelen más que uno que suma lo mismo.",
         "Testeá mostrar comisión + spread + fee de red como un solo «Costo total» (con el detalle "
         "a un toque, nunca escondido).",
         "r2-juntá-las-pérdidas"),
    Rule("PT02", "beneficio-neteado", "Edición hedónica: ganancia chica separada (silver lining)",
         "Beneficio presentado como descuento de un cargo",
         "Thaler: una ganancia chica al lado de una pérdida grande se disfruta más sola. Ojo: con "
         "λ = 2,25 la curva sola lo respalda solo si la ganancia es ~300 veces menor que la pérdida; "
         "es la regla con evidencia más débil, testeala.",
         "Testeá comunicar el cashback/bonificación como evento propio (otro momento, otro mensaje), "
         "no como «menos» en el resumen del cargo.",
         "r4-ganancia-chica-al-lado-de-pérdida-grande-separala"),
    Rule("PT03", "ganancias-agregadas", "Edición hedónica: separá las ganancias",
         "Ganancias comprimidas en un acumulado",
         "v(40) + v(40) > v(80): cada actualización es una ganancia nueva desde un punto de referencia nuevo.",
         "Testeá mostrar el rendimiento diario (notificación/widget «hoy ganaste X») además del acumulado.",
         "r1-separá-las-ganancias"),
    Rule("PT04", "encuadre-ganancia", "Aversión a las pérdidas",
         "Oferta encuadrada como ganancia",
         "Mismo número, misma oferta: perder X pesa ~2,25 veces lo que ganar X (predicción del modelo).",
         "Testeá la versión pérdida: «Estás dejando sobre la mesa X por año», calculado con el saldo "
         "real del usuario.",
         "3-aversión-a-las-pérdidas-hablá-de-lo-que-están-perdiendo"),
    Rule("PT05", "status-quo-neutro", "Mover el punto de referencia",
         "Status quo tratado como punto cero («más rápido / más barato»)",
         "Parado en cero la curva es cóncava y el usuario rechaza el riesgo de cambiar. Si el status quo "
         "se lee como pérdida, la curva es convexa y probar algo nuevo se siente como recuperar.",
         "Testeá reencuadrar: «Hoy estás perdiendo X y N días en cada envío. Dejá de perderlo.» "
         "con números verificables.",
         "2-mové-el-punto-de-referencia-y-movés-la-actitud-frente-al-riesgo"),
    Rule("PT06", "sorteo", "Peso de probabilidades",
         "Sorteo / premio improbable",
         "Un 1 % se procesa como ~5,5 %: el premio grande e improbable le gana al incentivo chico y seguro.",
         "Priorizá el tamaño del premio sobre la cantidad de ganadores y verificá bases y condiciones "
         "y requisitos legales de la jurisdicción antes de publicar.",
         "4-los-sorteos-funcionan-por-la-curva-de-peso-de-probabilidades"),
    Rule("PT07", "incentivo-chico-seguro", "Peso de probabilidades",
         "Incentivo chico y seguro en promo/referidos",
         "Con el mismo costo esperado, un sorteo se siente ~3,7 veces su valor (1.000 al 1 % ≈ 37 seguros).",
         "Testeá reemplazar el bono fijo por un sorteo de igual costo esperado "
         "(python3 tools/prospect_theory.py raffle --prize P --prob p --sure S).",
         "4-los-sorteos-funcionan-por-la-curva-de-peso-de-probabilidades"),
    Rule("PT90", "letra-chica", "Límite ético",
         "«Gratis / sin comisión» con asterisco",
         "Integrar pérdidas es presentarlas juntas, no esconderlas. Un asterisco rompe confianza y "
         "puede romper la regulación.",
         "Verificá que la condición esté al lado, legible y en el mismo flujo; si no, cambiá el claim.",
         "límites-éticos-y-regulatorios"),
]}


@dataclass(frozen=True)
class Finding:
    rule: str
    slug: str
    lever: str
    title: str
    file: str
    line: int
    excerpt: str
    why: str
    suggestion: str
    playbook: str


def _excerpt(text: str, limit: int = 160) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    return t if len(t) <= limit else t[: limit - 1] + "…"


# Claves de JSON/YAML/properties ("checkout.fee": ..., fee_label: ...) no son copy.
KEY_PREFIX = re.compile(r'^\s*"[^"]*"\s*:\s*|^\s*[A-Za-z][\w-]*[._][\w.-]*\s*[:=]\s*')


def _content(line: str) -> str:
    return KEY_PREFIX.sub("", line, count=1)


def _cost_categories(line: str) -> set[str]:
    found: set[str] = set()
    rest = _content(line)
    for name, pat in COST_CATEGORIES:
        if pat.search(rest):
            found.add(name)
            rest = pat.sub(" ", rest)  # a specific phrase is not also a generic hit
    return found


LineCheck = Callable[[str], bool]


def _line_checks() -> dict[str, LineCheck]:
    def pt02(s: str) -> bool:
        return bool(REBATE.search(s) and NETTING.search(s))

    def pt04(s: str) -> bool:
        for m in GAIN_FRAME.finditer(s):
            if GAIN_OBJECT.search(m.group("rest") or ""):
                return True
        return False

    def pt05(s: str) -> bool:
        return bool(STATUS_QUO.search(s)
                    or (STATUS_QUO_SOFT.search(s) and INERTIA_CONTEXT.search(s)))

    def pt07(s: str) -> bool:
        return bool(SMALL_SURE.search(s) and PROMO_CONTEXT.search(s))

    return {
        "PT02": pt02,
        "PT03": lambda s: bool(AGG_GAIN.search(s)),
        "PT04": pt04,
        "PT05": pt05,
        "PT06": lambda s: bool(RAFFLE.search(s)),
        "PT07": pt07,
        "PT90": lambda s: bool(FINE_PRINT.search(s)),
    }


LINE_CHECKS = _line_checks()


def audit_text(text: str, path: str = "<stdin>", rules: Iterable[str] | None = None,
               window: int = 4) -> list[Finding]:
    active = set(rules) if rules else set(RULES)
    lines = text.splitlines()
    findings: list[Finding] = []

    def add(rule_id: str, idx: int, extra: str = "") -> None:
        r = RULES[rule_id]
        why = r.why + (f" [{extra}]" if extra else "")
        findings.append(Finding(r.id, r.slug, r.lever, r.title, path, idx + 1,
                                _excerpt(lines[idx]), why, r.suggestion,
                                f"{PLAYBOOK}#{r.anchor}"))

    ignored = {i for i, s in enumerate(lines) if IGNORE_MARK in s}

    # PT01 works on a sliding window: an itemised cost breakdown spans lines.
    if "PT01" in active:
        i = 0
        while i < len(lines):
            if i in ignored or not _cost_categories(lines[i]):
                i += 1
                continue
            span = range(i, min(i + window, len(lines)))
            cats: set[str] = set()
            for j in span:
                if j not in ignored:
                    cats |= _cost_categories(lines[j])
            has_amount = any(MONEY.search(_content(lines[j])) for j in span if j not in ignored)
            if len(cats) >= 2 and has_amount:
                add("PT01", i, "categorías: " + ", ".join(sorted(cats)))
                i += window
            else:
                i += 1

    for idx, s in enumerate(lines):
        if idx in ignored or len(s) > 2000:
            continue
        content = _content(s)
        for rule_id, check in LINE_CHECKS.items():
            if rule_id not in active or not check(content):
                continue
            extra = ""
            if rule_id == "PT05" and INERTIA_CONTEXT.search(content):
                extra = "contexto de inercia detectado: prioridad alta"
            add(rule_id, idx, extra)

    findings.sort(key=lambda f: (f.line, f.rule))
    return findings


def _is_minified(text: str) -> bool:
    lines = text.splitlines() or [""]
    return len(text) > 5000 and len(text) / len(lines) > 500


def iter_files(paths: Sequence[str]) -> Iterator[str]:
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                if name in SKIP_FILES or name.endswith((".min.js", ".min.css", ".map")):
                    continue
                if os.path.splitext(name)[1].lower() in TEXT_EXTENSIONS:
                    yield os.path.join(dirpath, name)


def read_text(path: str) -> str | None:
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    text = raw.decode("utf-8", errors="replace")
    return None if _is_minified(text) else text


def audit_paths(paths: Sequence[str], rules: Iterable[str] | None = None) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    scanned = 0
    for p in iter_files(paths):
        text = read_text(p)
        if text is None:
            continue
        scanned += 1
        findings.extend(audit_text(text, p, rules))
    return findings, scanned


def render_text(findings: list[Finding], scanned: int) -> str:
    out = [f"{f.file}:{f.line}: {f.rule} [{f.lever}] {f.title}\n    > {f.excerpt}\n"
           f"    por qué: {f.why}\n    acción : {f.suggestion}" for f in findings]
    out.append(f"\n{len(findings)} hipótesis en {scanned} archivo(s). Playbook: {PLAYBOOK}")
    return "\n".join(out)


def render_md(findings: list[Finding], scanned: int) -> str:
    out = ["# Auditoría Prospect Theory", "",
           f"{len(findings)} hipótesis en {scanned} archivo(s). Cada fila es algo para **testear**, "
           f"no un error. Marco: `{PLAYBOOK}`.", "",
           "| Regla | Palanca | Hallazgos |", "|---|---|---|"]
    by_rule: dict[str, list[Finding]] = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)
    for rid in sorted(by_rule):
        out.append(f"| {rid} {RULES[rid].title} | {RULES[rid].lever} | {len(by_rule[rid])} |")
    for rid in sorted(by_rule):
        r = RULES[rid]
        out += ["", f"## {rid} · {r.title}", "", f"**Por qué:** {r.why}", "",
                f"**Acción:** {r.suggestion}", ""]
        for f in by_rule[rid]:
            extra = f" _({f.why.split('[', 1)[1].rstrip(']')})_" if "[" in f.why else ""
            excerpt = f.excerpt.replace("|", "\\|")
            out.append(f"- `{f.file}:{f.line}` — {excerpt}{extra}")
    return "\n".join(out) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="archivos o carpetas; '-' lee stdin")
    ap.add_argument("--format", choices=("text", "md", "json"), default="text")
    ap.add_argument("--only", help="lista de reglas separadas por coma (ej. PT01,PT04)")
    ap.add_argument("--skip", help="reglas a ignorar, separadas por coma")
    ap.add_argument("--strict", action="store_true", help="exit 1 si hay hallazgos")
    ap.add_argument("--list-rules", action="store_true", help="lista las reglas y sale")
    a = ap.parse_args(argv)

    if a.list_rules:
        for r in RULES.values():
            print(f"{r.id}  {r.slug:24} {r.lever}")
        return 0
    if not a.paths:
        ap.error("indicá al menos un archivo o carpeta (o '-' para stdin)")

    rules = set(RULES)
    if a.only:
        rules = {x.strip().upper() for x in a.only.split(",")}
    if a.skip:
        rules -= {x.strip().upper() for x in a.skip.split(",")}
    unknown = rules - set(RULES)
    if unknown:
        ap.error(f"reglas desconocidas: {', '.join(sorted(unknown))}")

    if a.paths == ["-"]:
        findings, scanned = audit_text(sys.stdin.read(), "<stdin>", rules), 1
    else:
        findings, scanned = audit_paths(a.paths, rules)

    if a.format == "json":
        print(json.dumps({"scanned": scanned, "findings": [asdict(f) for f in findings]},
                         ensure_ascii=False, indent=2))
    elif a.format == "md":
        sys.stdout.write(render_md(findings, scanned))
    else:
        print(render_text(findings, scanned))
    return 1 if (a.strict and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
