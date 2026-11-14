#!/usr/bin/env python3
"""distill_sessions.py - find what repeats in your agent sessions (stdlib only, read-only).

Reads transcripts and prints *candidates* with evidence. It never writes skills,
rules or memory: the agent drafts them and the user approves.

Sources (auto-detected; pass --source to restrict):
  claude   ~/.claude/projects/**/*.jsonl              (Claude Code)
  codex    ~/.codex/sessions/**/*.jsonl               (Codex CLI rollouts; best effort)
  hermes   $HERMES_HOME/state.db                      (Hermes Agent, opened read-only)
  chatgpt  --path <conversations.json>                (ChatGPT / Claude.ai exports; best effort)

Signals:
  correcciones   the user correcting the agent ("no, …", "otra vez", "te dije", "again") -> rule
  pedidos        near-identical requests across sessions -> skill (a verb)
  errores        the same tool failure repeated -> rule or fix
Rule of 3: a cluster is promotable at >=3 occurrences; 2 is shown as "vigilar".

Usage:
  python3 distill_sessions.py --since 30 --out ~/radar/destilados/2026-11-14-candidatos.md
  python3 distill_sessions.py --source claude --json
  python3 distill_sessions.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# ------------------------------------------------------------- redaction ---

SECRET_PATTERNS = [
    (re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_\-]{16,}\b"), "<key>"),
    (re.compile(r"\b(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"), "<github-token>"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b"), "<slack-token>"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "<aws-key>"),
    (re.compile(r"(?i)\b(bearer|token|api[_-]?key|password|secret)\b\s*[:=]?\s*\S{8,}"), r"\1 <redacted>"),
    (re.compile(r"\b\d{6,}:[A-Za-z0-9_\-]{30,}\b"), "<bot-token>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"\+?\d[\d\s\-()]{8,}\d"), "<number>"),
    (re.compile(r"\b[A-Fa-f0-9]{32,}\b|\b[A-Za-z0-9+/]{40,}={0,2}"), "<blob>"),
]


def redact(text: str) -> str:
    for pat, rep in SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text


# ---------------------------------------------------------------- events ---

@dataclass
class Event:
    source: str
    session: str
    ts: dt.datetime | None
    kind: str          # prompt | tool_error
    text: str
    tool: str = ""


def _ts(v) -> dt.datetime | None:
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            return dt.datetime.fromtimestamp(v, dt.timezone.utc)
        return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (ValueError, OSError):
        return None


def _is_injected(text: str) -> bool:
    """Harness-injected user turns (reminders, command output) are not the human talking."""
    t = text.lstrip()
    return t.startswith("<") or t.startswith("[SYSTEM") or t.startswith("Caveat:") or not t


def read_claude(root: Path) -> list[Event]:
    out: list[Event] = []
    for f in root.glob("**/*.jsonl"):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = d.get("message") or {}
            sess = d.get("sessionId") or f.stem
            ts = _ts(d.get("timestamp"))
            content = msg.get("content")
            if d.get("type") == "user" and isinstance(content, str) and not d.get("isSidechain"):
                if not _is_injected(content):
                    out.append(Event("claude", sess, ts, "prompt", content))
            elif d.get("type") == "user" and isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "text" and not d.get("isSidechain") and not _is_injected(c.get("text", "")):
                        out.append(Event("claude", sess, ts, "prompt", c["text"]))
                    if c.get("type") == "tool_result" and c.get("is_error"):
                        body = c.get("content")
                        if isinstance(body, list):
                            body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                        out.append(Event("claude", sess, ts, "tool_error", str(body or ""), tool=""))
    return out


def read_codex(root: Path) -> list[Event]:
    out: list[Event] = []
    for f in root.glob("**/*.jsonl"):
        sess = f.stem
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = d.get("payload") or d
            ts = _ts(d.get("timestamp"))
            if p.get("type") == "user_message" and isinstance(p.get("message"), str):
                if not _is_injected(p["message"]):
                    out.append(Event("codex", sess, ts, "prompt", p["message"]))
            elif p.get("type") == "function_call_output":
                o = p.get("output")
                try:
                    o = json.loads(o) if isinstance(o, str) else o
                except json.JSONDecodeError:
                    pass
                code = (o.get("metadata") or {}).get("exit_code") if isinstance(o, dict) else None
                if code not in (None, 0):
                    out.append(Event("codex", sess, ts, "tool_error", str(o.get("output", ""))))
    return out


def read_hermes(db: Path) -> list[Event]:
    out: list[Event] = []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute("SELECT session_id, role, content, tool_name, timestamp FROM messages "
                           "WHERE role IN ('user','tool') AND content IS NOT NULL").fetchall()
    finally:
        con.close()
    for sess, role, content, tool, ts in rows:
        if role == "user" and not _is_injected(content):
            out.append(Event("hermes", sess, _ts(ts), "prompt", content))
        elif role == "tool" and re.search(r'"(error|is_error)"\s*:\s*(true|"[^"]+")|^Error|Traceback', content or ""):
            out.append(Event("hermes", sess, _ts(ts), "tool_error", content, tool=tool or ""))
    return out


def read_chat_export(path: Path) -> list[Event]:
    """ChatGPT conversations.json (mapping/nodes) or Claude.ai export (chat_messages)."""
    out: list[Event] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for conv in data if isinstance(data, list) else []:
        sess = str(conv.get("id") or conv.get("uuid") or conv.get("title"))
        for node in (conv.get("mapping") or {}).values():
            m = (node or {}).get("message") or {}
            if (m.get("author") or {}).get("role") == "user":
                parts = (m.get("content") or {}).get("parts") or []
                text = " ".join(p for p in parts if isinstance(p, str))
                if text.strip():
                    out.append(Event("chatgpt", sess, _ts(m.get("create_time")), "prompt", text))
        for m in conv.get("chat_messages") or []:
            if m.get("sender") == "human" and (m.get("text") or "").strip():
                out.append(Event("claude.ai", sess, _ts(m.get("created_at")), "prompt", m["text"]))
    return out


# ------------------------------------------------------------- clustering ---

STOP = set("""a al algo como con de del el ella en es esa ese eso esta este esto la las le lo los me mi mis
mas más no o para pero por que qué se si sí sin su sus te tu un una uno y ya the a an and are as at be but by
do for from have i if in is it of on or so that the this to we what with you your can please pls q x""".split())
CORRECTION = re.compile(
    r"^(no[,.!\s]|nop|mal\b|eso no|así no|asi no)|\b(otra vez|de nuevo|te dije|ya te dije|te pedí|te pedi|"
    r"no era|no es eso|revert|deshac|volvé atrás|volve atras|again|i said|i told you|that's not|that is not|"
    r"wrong|undo|you forgot|te olvidaste|olvidaste)\b", re.I)


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-záéíóúñü0-9]{3,}", text.lower())
    return {w for w in words if w not in STOP}


def cluster(events: list[Event], threshold: float) -> list[list[Event]]:
    groups: list[tuple[set[str], list[Event]]] = []
    for e in events:
        tk = tokens(e.text)
        if len(tk) < 2:
            continue
        best, score = None, 0.0
        for g in groups:
            inter = len(tk & g[0])
            j = inter / len(tk | g[0])
            if j > score:
                best, score = g, j
        if best is not None and score >= threshold:
            best[1].append(e)
            best[0].update(tk) if len(best[0]) < 40 else None
        else:
            groups.append((set(tk), [e]))
    return [g[1] for g in groups]


def error_signature(e: Event) -> str:
    first = next((l for l in e.text.splitlines() if l.strip()), "")[:160]
    first = re.sub(r"(/[\w.\-]+)+", "<path>", first)
    first = re.sub(r"\d+", "N", first)
    return f"{e.tool}: {first}".strip(": ")


def distill(events: list[Event], since: dt.datetime | None) -> dict:
    if since:
        events = [e for e in events if e.ts is None or e.ts >= since]
    prompts = [e for e in events if e.kind == "prompt"]
    corrections = [e for e in prompts if CORRECTION.search(e.text.strip()[:200])]
    requests = [e for e in prompts if e not in corrections and len(tokens(e.text)) >= 4]
    errors = [e for e in events if e.kind == "tool_error"]

    def pack(groups: list[list[Event]], tipo: str, destino: str, min_sessions: int = 1) -> list[dict]:
        out = []
        for g in groups:
            sessions = {e.session for e in g}
            if len(g) < 2 or len(sessions) < min_sessions:
                continue
            dates = sorted(e.ts.date().isoformat() for e in g if e.ts)
            common = set.intersection(*(tokens(e.text) for e in g)) if g else set()
            out.append({
                "tipo": tipo, "veces": len(g), "sesiones": len(sessions),
                "estado": "promover" if len(g) >= 3 else "vigilar",
                "destino": destino, "palabras_comunes": sorted(common)[:8],
                "desde": dates[0] if dates else None, "hasta": dates[-1] if dates else None,
                "fuentes": sorted({e.source for e in g}),
                "ejemplos": [redact(re.sub(r"\s+", " ", e.text.strip()))[:180] for e in g[:3]],
            })
        return sorted(out, key=lambda c: (-c["veces"], -c["sesiones"]))

    err_groups: dict[str, list[Event]] = defaultdict(list)
    for e in errors:
        err_groups[error_signature(e)].append(e)
    return {
        "generado": dt.datetime.now().isoformat(timespec="seconds"),
        "eventos": {"pedidos": len(prompts), "correcciones": len(corrections), "errores": len(errors),
                    "sesiones": len({e.session for e in events})},
        "correcciones": pack(cluster(corrections, 0.25), "regla", "AGENTS.md / CLAUDE.md del proyecto"),
        "pedidos": pack(cluster(requests, 0.45), "skill", "~/.hermes/skills/<categoria>/<verbo>/SKILL.md", min_sessions=2),
        "errores": pack(list(err_groups.values()), "regla", "AGENTS.md del proyecto o arreglo en el entorno"),
    }


def to_markdown(r: dict) -> str:
    ev = r["eventos"]
    lines = [f"# Candidatos para destilar ({r['generado'][:10]})", "",
             f"{ev['sesiones']} sesiones · {ev['pedidos']} pedidos · {ev['correcciones']} correcciones · {ev['errores']} errores de tools",
             "", "Regla de 3: `promover` = ≥3 apariciones. `vigilar` = 2. Nada se guarda sin tu aprobación.", ""]
    for key, title in (("correcciones", "Correcciones repetidas → regla de 1 línea"),
                       ("pedidos", "Pedidos repetidos → skill (verbo)"),
                       ("errores", "Errores repetidos → regla o arreglo")):
        lines += [f"## {title}", ""]
        if not r[key]:
            lines += ["Nada repetido.", ""]
        for c in r[key][:12]:
            lines.append(f"- **{c['estado']}** · {c['veces']}× en {c['sesiones']} sesión(es) · {c['desde']} → {c['hasta']} · "
                         f"{', '.join(c['fuentes'])} · palabras: {', '.join(c['palabras_comunes']) or '—'}")
            lines += [f"  - \"{x}\"" for x in c["ejemplos"]]
        lines.append("")
    return "\n".join(lines)


def default_sources() -> dict[str, Path]:
    home = Path.home()
    hermes_home = Path(os.environ.get("HERMES_HOME") or (
        Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / "hermes" if sys.platform == "win32" else home / ".hermes"))
    return {"claude": home / ".claude" / "projects", "codex": home / ".codex" / "sessions",
            "hermes": hermes_home / "state.db"}


def collect(sources: list[str], extra: list[Path]) -> list[Event]:
    found = default_sources()
    events: list[Event] = []
    readers = {"claude": read_claude, "codex": read_codex, "hermes": read_hermes}
    for name in sources:
        p = found[name]
        if p.exists():
            try:
                got = readers[name](p)
                events += got
                print(f"# {name}: {len(got)} eventos ({p})", file=sys.stderr)
            except (OSError, sqlite3.Error) as e:
                print(f"# {name}: no se pudo leer ({e})", file=sys.stderr)
        else:
            print(f"# {name}: no encontrado ({p})", file=sys.stderr)
    for p in extra:
        events += read_chat_export(p)
    return events


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        cc = t / "claude" / "proj"
        cc.mkdir(parents=True)
        lines = []
        for i, (s, txt) in enumerate([("s1", "no, otra vez usaste npm en vez de pnpm"), ("s2", "te dije que uses pnpm, no npm"),
                                      ("s3", "no! pnpm, no npm otra vez"), ("s1", "armá la landing de pricing para el cliente nuevo con tracking"),
                                      ("s2", "armá la landing de pricing para el cliente con tracking y formulario"),
                                      ("s3", "<system-reminder>ignored</system-reminder>")]):
            lines.append(json.dumps({"type": "user", "sessionId": s, "timestamp": f"2026-11-1{i}T10:00:00Z",
                                     "message": {"role": "user", "content": txt}}))
        lines.append(json.dumps({"type": "user", "sessionId": "s1", "timestamp": "2026-11-10T10:00:00Z",
                                 "message": {"content": [{"type": "tool_result", "is_error": True, "content": "Error: ENOENT /a/b.txt 12"}]}}))
        lines.append(json.dumps({"type": "user", "sessionId": "s2", "timestamp": "2026-11-11T10:00:00Z",
                                 "message": {"content": [{"type": "tool_result", "is_error": True, "content": "Error: ENOENT /c/d.txt 99"}]}}))
        (cc / "x.jsonl").write_text("\n".join(lines), encoding="utf-8")
        ev = read_claude(t / "claude")
        assert sum(e.kind == "prompt" for e in ev) == 5 and sum(e.kind == "tool_error" for e in ev) == 2, ev
        db = t / "state.db"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE messages (session_id TEXT, role TEXT, content TEXT, tool_name TEXT, timestamp REAL)")
        con.execute("INSERT INTO messages VALUES ('h1','user','otra vez mandaste el digest largo, máximo 5 señales',NULL,1763000000)")
        con.execute("INSERT INTO messages VALUES ('h1','tool','Traceback: boom','terminal',1763000001)")
        con.commit(); con.close()
        ev += read_hermes(db)
        cx = t / "codex"; cx.mkdir()
        (cx / "r.jsonl").write_text("\n".join([
            json.dumps({"timestamp": "2026-11-12T10:00:00Z", "type": "event_msg", "payload": {"type": "user_message", "message": "no, eso no: usá pnpm"}}),
            json.dumps({"type": "response_item", "payload": {"type": "function_call_output", "output": json.dumps({"output": "fail", "metadata": {"exit_code": 1}})}}),
        ]), encoding="utf-8")
        ev += read_codex(cx)
        r = distill(ev, None)
        top = r["correcciones"][0]
        assert top["veces"] >= 3 and top["estado"] == "promover" and "pnpm" in top["palabras_comunes"], r["correcciones"]
        assert r["pedidos"] and r["pedidos"][0]["sesiones"] == 2, r["pedidos"]
        assert r["errores"][0]["veces"] == 2, r["errores"]
        assert redact("token: ghp_abcdefghijklmnopqrstuvwxyz123456 mail a@b.co +54 9 11 5555 1234") .count("<") >= 3
        md = to_markdown(r)
        assert "promover" in md and "<system-reminder>" not in md
    print("self-test OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=int, default=30, help="días hacia atrás (0 = todo)")
    ap.add_argument("--source", action="append", choices=("claude", "codex", "hermes"))
    ap.add_argument("--path", action="append", type=Path, default=[], help="export de ChatGPT/Claude.ai (conversations.json)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.since) if a.since else None
    r = distill(collect(a.source or ["claude", "codex", "hermes"], a.path), since)
    text = json.dumps(r, ensure_ascii=False, indent=1) if a.json else to_markdown(r)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
        print(a.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
