#!/usr/bin/env python3
"""contract.py - the judge of a goal contract is a script, not the agent's confidence.

  new <slug> [--dir runs]      create runs/AAAA-MM-DD-<slug>.md from the template
  verify <run.md> [--cwd DIR]  run every `command` listed under "## Evidencia requerida",
                               append a "## Verificación" block (PASS/FAIL + output tail)
                               and exit 0 only if all pass
  status <run.md>              last verification result, one line

Only lines shaped like "- `cmd`" inside the Evidencia section are executed. Anything
else there (screenshots, human review) is reported as NOT TESTED, never as PASS.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATE = """# Contrato: {slug}

## Objetivo (estado final observable)

## Evidencia requerida (verificador elegido ANTES de correr)
<!-- una línea por chequeo; las que tienen `comando` las corre contract.py verify -->
- `echo reemplazame por tests, typecheck o build`

## Restricciones
- scope:
- no tocar:
- sin push/merge/deploy sin aprobación
- rama/worktree:

## Presupuesto
- turnos o tiempo máx:
- costo máx:
- criterio de corte:

## Fuera de alcance

## Bitácora
"""

CMD_LINE = re.compile(r"^\s*-\s*`([^`]+)`\s*(.*)$")


def evidence_lines(text: str) -> list[str]:
    m = re.search(r"^## Evidencia requerida.*?$(.*?)(?=^## )", text, re.S | re.M)
    if not m:
        return []
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
    return [l for l in body.splitlines() if l.strip().startswith("-")]


def verify(run: Path, cwd: Path, timeout: int) -> tuple[bool, list[dict]]:
    text = run.read_text(encoding="utf-8")
    results = []
    for line in evidence_lines(text):
        m = CMD_LINE.match(line)
        if not m:
            results.append({"check": line.strip("- ").strip(), "estado": "NOT TESTED", "salida": "no es un comando"})
            continue
        cmd = m.group(1)
        try:
            p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            out = (p.stdout + p.stderr).strip().splitlines()[-6:]
            results.append({"check": cmd, "estado": "PASS" if p.returncode == 0 else "FAIL",
                            "codigo": p.returncode, "salida": "\n".join(out)})
        except subprocess.TimeoutExpired:
            results.append({"check": cmd, "estado": "FAIL", "codigo": None, "salida": f"timeout {timeout}s"})
    passed = bool(results) and all(r["estado"] == "PASS" for r in results)
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    block = [f"\n## Verificación {stamp}: {'PASS' if passed else 'FAIL'}\n"]
    for r in results:
        block.append(f"- **{r['estado']}** `{r['check']}`" + (f" (exit {r['codigo']})" if r.get("codigo") not in (None, 0) else ""))
        if r["estado"] != "PASS" and r.get("salida"):
            block.append("  ```\n" + "\n".join("  " + l for l in r["salida"].splitlines()) + "\n  ```")
    if not results:
        block.append("- **FAIL** no hay verificador: agregá líneas `- \\`comando\\`` en Evidencia requerida")
    with open(run, "a", encoding="utf-8") as fh:
        fh.write("\n".join(block) + "\n")
    return passed, results


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        run = d / "r.md"
        run.write_text(TEMPLATE.format(slug="t").replace("- `echo reemplazame por tests, typecheck o build`",
                                                          "- `true`\n- `sh -c 'echo boom; exit 3'`\n- screenshot de /pricing"), encoding="utf-8")
        ok, res = verify(run, d, 30)
        assert not ok and [r["estado"] for r in res] == ["PASS", "FAIL", "NOT TESTED"], res
        body = run.read_text(encoding="utf-8")
        assert "**FAIL** `sh -c 'echo boom; exit 3'` (exit 3)" in body and "boom" in body
        run.write_text(TEMPLATE.format(slug="t").replace("`echo reemplazame por tests, typecheck o build`", "`true`"), encoding="utf-8")
        assert verify(run, d, 30)[0]
        empty = d / "e.md"
        empty.write_text("## Evidencia requerida\n\n## Restricciones\n", encoding="utf-8")
        assert not verify(empty, d, 30)[0], "no verifier must never pass"
    print("self-test OK")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("slug"); p.add_argument("--dir", type=Path, default=Path("runs"))
    p = sub.add_parser("verify"); p.add_argument("run", type=Path); p.add_argument("--cwd", type=Path, default=Path("."))
    p.add_argument("--timeout", type=int, default=900)
    p = sub.add_parser("status"); p.add_argument("run", type=Path)
    sub.add_parser("self-test")
    a = ap.parse_args()
    if a.cmd == "self-test":
        self_test(); return 0
    if a.cmd == "new":
        slug = re.sub(r"[^a-z0-9-]+", "-", a.slug.lower()).strip("-")
        out = a.dir / f"{dt.date.today().isoformat()}-{slug}.md"
        if out.exists():
            print(f"ya existe: {out}", file=sys.stderr); return 1
        a.dir.mkdir(parents=True, exist_ok=True)
        out.write_text(TEMPLATE.format(slug=slug), encoding="utf-8")
        print(out); return 0
    if a.cmd == "verify":
        ok, res = verify(a.run, a.cwd, a.timeout)
        for r in res:
            print(f"{r['estado']:<10} {r['check']}")
        print("PASS" if ok else "FAIL")
        return 0 if ok else 1
    last = re.findall(r"^## Verificación (\S+): (PASS|FAIL)", a.run.read_text(encoding="utf-8"), re.M)
    print(f"{last[-1][1]} ({last[-1][0]})" if last else "sin verificar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
