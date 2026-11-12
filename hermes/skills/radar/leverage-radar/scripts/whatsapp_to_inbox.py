#!/usr/bin/env python3
"""WhatsApp "saved links" chat -> Leverage Radar inbox.

Deterministic, stdlib-only. No network, no LLM. It does the boring part so the
agent only spends tokens on judgment.

Input : a WhatsApp export (.zip or _chat.txt), iOS or Android format.
Output: <out>/inbox.jsonl   one line per unique link (deduped, canonical URL)
        <out>/thoughts.jsonl your own notes without links (principles, ideas)
        <out>/inbox.md      human summary: counts, re-shared links, priorities

Re-running on a newer export is safe: items whose id is in --state
(processed ids, one per line) are marked "status": "done" instead of "new".

Usage:
  python3 whatsapp_to_inbox.py "WhatsApp Chat - Articles Twitter.zip" --out ~/.hermes/radar
  python3 whatsapp_to_inbox.py _chat.txt --out ./radar --state ./radar/processed.txt
  python3 whatsapp_to_inbox.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# ---------------------------------------------------------------- parsing ---

INVISIBLE = "‎‏‪‫‬‭‮﻿"
SPACES = "   "

# iOS:     [15/6/26, 10:21:41 a. m.] Name: text
# Android: 15/6/26, 10:21 a. m. - Name: text      (also 24h variants)
IOS_RE = re.compile(
    r"^\[(\d{1,2})/(\d{1,2})/(\d{2,4}),\s*(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap])?\.?\s*(?:m\.?)?\]\s*([^:]+?):\s?(.*)$",
    re.I,
)
ANDROID_RE = re.compile(
    r"^(\d{1,2})/(\d{1,2})/(\d{2,4}),?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap])?\.?\s*(?:m\.?)?\s+-\s+([^:]+?):\s?(.*)$",
    re.I,
)
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)
ATTACH_RE = re.compile(r"<(?:adjunto|attached):\s*([^>]+)>", re.I)
SYSTEM_HINTS = ("cifrados de extremo a extremo", "end-to-end encrypted", "creaste el grupo",
                "created group", "cambiaste el nombre", "changed the group name",
                "se editó este mensaje", "this message was edited")


@dataclass
class Message:
    ts: datetime
    sender: str
    text: str


def _clean(line: str) -> str:
    for ch in INVISIBLE:
        line = line.replace(ch, "")
    for ch in SPACES:
        line = line.replace(ch, " ")
    return line.rstrip("\r\n")


def _to_dt(d, mo, y, h, mi, s, ampm) -> datetime:
    y = int(y)
    y = y + 2000 if y < 100 else y
    h = int(h)
    if ampm:
        ampm = ampm.lower()
        if ampm == "p" and h != 12:
            h += 12
        if ampm == "a" and h == 12:
            h = 0
    return datetime(y, int(mo), int(d), h, int(mi), int(s or 0))


def parse_messages(raw: str) -> list[Message]:
    msgs: list[Message] = []
    for line in raw.splitlines():
        line = _clean(line)
        m = IOS_RE.match(line) or ANDROID_RE.match(line)
        if m:
            d, mo, y, h, mi, s, ampm, sender, text = m.groups()
            msgs.append(Message(_to_dt(d, mo, y, h, mi, s, ampm), sender.strip(), text))
        elif msgs:  # continuation of a multi-line message
            msgs[-1].text += "\n" + line
    return [m for m in msgs if not any(h in m.text.lower() for h in SYSTEM_HINTS) or URL_RE.search(m.text)]


def read_export(path: Path) -> str:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".txt")]
            if not names:
                sys.exit(f"no .txt chat file inside {path}")
            name = "_chat.txt" if "_chat.txt" in names else names[0]
            return io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace").read()
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------- canonical URL ---

DROP_PARAMS = {"s", "t", "a", "si", "igsh", "igshid", "ref", "ref_src", "utm_source", "utm_medium",
               "utm_campaign", "utm_content", "utm_term", "rcm", "fbclid", "gclid", "sharetype",
               "ogimg", "highlightedupdateurn", "highlightedupdatetype", "origin"}


def canonical_url(url: str) -> str:
    url = url.rstrip(".,;:!?")
    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.").removeprefix("mobile.")
    path = parts.path
    if host in {"twitter.com", "x.com"}:
        host = "x.com"
        m = re.match(r"^/([^/]+)/status/(\d+)", path)
        if m:  # drop /video/1, /photo/1 and the handle's case
            return f"https://x.com/{m.group(1).lower()}/status/{m.group(2)}"
    if host == "youtu.be":
        return f"https://youtube.com/watch?v={path.strip('/')}"
    query = [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in DROP_PARAMS]
    return urlunsplit(("https", host, path.rstrip("/") or "/", urlencode(query), ""))


def source_of(url: str) -> str:
    host = urlsplit(url).netloc
    if "x.com" in host:
        return "x"
    for key, name in (("instagram", "instagram"), ("youtube", "youtube"), ("github", "github"),
                      ("linkedin", "linkedin"), ("reddit", "reddit"), ("chatgpt", "ai-chat"),
                      ("claude.ai", "ai-chat"), ("kimi", "ai-chat"), ("drive.google", "drive")):
        if key in host:
            return name
    return "web"


# ------------------------------------------------------------- heuristics ---
# Cheap signals from YOUR note. They do not decide anything: they order the
# queue so the agent reads the most promising items first.

PRIORITY_HIGH = ("bible", "10/10", "si o si", "sí o sí", "clave", "usar ya", "bomba", "💣",
                 "this is the way", "usar todos los dias", "imprimir", "muy bueno", "buenardo",
                 "me cambia la vida", "la rompo", "aplica para todo", "esto para todo", "usar si o si",
                 "meterle", "recontra aplica", "epic", "crack", "darle mucho foco", "arrancar ya",
                 "usarlo ahora", "usar para todo")
PRIORITY_VERIFY = ("probar", "investigar", "chequear", "verlo", "ver", "sirve", "servira", "servirá",
                   "?", "sera", "será", "tendra sentido", "tendrá sentido", "q es esto")

# tag -> keywords (match on note + url, lowercase)
TAGS: dict[str, tuple[str, ...]] = {
    "hermes": ("hermes",),
    "router-model": ("jev", "clef", "treg"),
    "loop-engineering": ("loop", "/goal", "gauntlet", "babysit"),
    "harness": ("harness", "adx", "middleware"),
    "graph-engineering": ("graph",),
    "memory-knowledge": ("memory", "memoria", "obsidian", "obsidina", "second brain", "company brain",
                         "knowledge", "rag"),
    "context-tokens": ("context", "token", "gastar menos", "ahorrar", "headroom"),
    "local-models": ("local", "ollama", "gguf", "fine tune", "entrenar un modelo"),
    "infra-vps": ("vps", "mac mini", "docker", "kubernetes", "worktree", "healthcheck", "cli"),
    "agents-skills": ("agent", "skill", "subagent", "sub-agent", "mcp", "plugin", "automation",
                      "automatiza", "n8n", "orca", "codex", "claude"),
    "evals-quality": ("eval", "alucine", "review", "revision", "seguridad", "security", "hackeado",
                      "testear"),
    "search-geo": ("geo", "seo", "sem", "backlink"),
    "content-video": ("video", "rea", "ugc", "content", "slideshow", "avatar", "voice", "sound",
                      "elevenlabs", "higgsfield", "minimax", "viral", "edicion"),
    "design-motion-3d": ("design", "motion", "blender", "3d", "landing", "web insp", "shaders",
                         "scroll", "taste"),
    "growth-sales": ("ads", "meta ads", "outreach", "leads", "ventas", "crm", "gtm", "clay",
                     "maps", "distribution", "mkt", "marketing", "comunidad", "whatsapp"),
    "scraping-data": ("scrap", "crawler", "pdf", "extract", "data", "datas"),
    "jobs-income": ("labu", "laburo", "jobs", "job search", "pagarte", "consultor"),
    "grok": ("grok",),
}

# radar layer for each tag (the 5-layer growth map)
LAYER = {
    "content-video": "distribucion", "search-geo": "distribucion", "growth-sales": "conversion",
    "design-motion-3d": "identidad", "evals-quality": "aprendizaje", "memory-knowledge": "orquestacion",
    "hermes": "orquestacion", "router-model": "orquestacion", "loop-engineering": "orquestacion",
    "harness": "orquestacion", "graph-engineering": "orquestacion", "context-tokens": "orquestacion",
    "local-models": "orquestacion", "infra-vps": "orquestacion", "agents-skills": "orquestacion",
    "scraping-data": "aprendizaje", "jobs-income": "conversion", "grok": "orquestacion",
}


_KW_CACHE: dict[str, re.Pattern] = {}


def _has(text: str, kw: str) -> bool:
    """Keyword match with a left word boundary; short words (<=3) need both
    boundaries so 'rea' does not match 'crear' and 'geo' does not match 'geoign'."""
    pat = _KW_CACHE.get(kw)
    if pat is None:
        esc = re.escape(kw)
        left = r"(?<![a-z0-9áéíóúñ])" if kw[0].isalnum() else ""
        right = r"(?![a-z0-9áéíóúñ])" if len(kw) <= 3 and kw[-1].isalnum() else ""
        pat = _KW_CACHE[kw] = re.compile(left + esc + right)
    return bool(pat.search(text))


def tags_for(text: str) -> list[str]:
    low = text.lower()
    return [tag for tag, kws in TAGS.items() if any(_has(low, k) for k in kws)]


def priority_for(note: str, times_shared: int) -> str:
    low = note.lower()
    if times_shared > 1 or any(_has(low, k) for k in PRIORITY_HIGH):
        return "high"
    if any(_has(low, k) for k in PRIORITY_VERIFY):
        return "verify"
    return "normal" if note.strip() else "unlabeled"


def looks_private(text: str) -> bool:
    """Bare numbers (phones, codes, ids) never enter the inbox."""
    return bool(re.fullmatch(r"[\d\s\-+().]{7,}", text.strip()))


# ----------------------------------------------------------------- build ---

@dataclass
class Item:
    id: str
    url: str
    source: str
    first_seen: str
    last_seen: str
    times_shared: int = 1
    notes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    layers: list[str] = field(default_factory=list)
    priority: str = "unlabeled"
    status: str = "new"


def build(msgs: list[Message], done: set[str]) -> tuple[list[Item], list[dict]]:
    items: dict[str, Item] = {}
    thoughts: list[dict] = []
    for m in msgs:
        text = m.text.strip()
        if not text or looks_private(text):
            continue
        urls = URL_RE.findall(text)
        note = ATTACH_RE.sub("", URL_RE.sub("", text)).strip()
        note = re.sub(r"\n{3,}", "\n\n", note)
        if not urls:
            attach = ATTACH_RE.findall(text)
            if note or attach:
                thoughts.append({"ts": m.ts.isoformat(), "text": note,
                                 "attachments": [a.strip() for a in attach]})
            continue
        for raw in urls:
            url = canonical_url(raw)
            iid = hashlib.sha1(url.encode()).hexdigest()[:12]
            ts = m.ts.isoformat()
            if iid in items:
                it = items[iid]
                it.times_shared += 1
                it.last_seen = ts
            else:
                it = items[iid] = Item(iid, url, source_of(url), ts, ts)
            if note and note not in it.notes:
                it.notes.append(note)
    for it in items.values():
        joined = " ".join(it.notes)
        it.tags = tags_for(joined + " " + it.url) if joined else tags_for(it.url)
        it.layers = sorted({LAYER[t] for t in it.tags if t in LAYER})
        it.priority = priority_for(joined, it.times_shared)
        it.status = "done" if it.id in done else "new"
    order = {"high": 0, "verify": 1, "normal": 2, "unlabeled": 3}
    ranked = sorted(items.values(), key=lambda i: (order[i.priority], i.first_seen))
    return ranked, thoughts


def summary_md(items: list[Item], thoughts: list[dict]) -> str:
    tag_count = Counter(t for i in items for t in i.tags)
    pri_count = Counter(i.priority for i in items)
    src_count = Counter(i.source for i in items)
    new = [i for i in items if i.status == "new"]
    out = ["# Radar inbox", "",
           f"- unique links: **{len(items)}** ({len(new)} new)",
           f"- own notes without link: **{len(thoughts)}**",
           "- priority: " + ", ".join(f"{k} {v}" for k, v in pri_count.most_common()),
           "- source: " + ", ".join(f"{k} {v}" for k, v in src_count.most_common()), "",
           "## Themes you keep saving", "", "| tag | links |", "|---|---|"]
    out += [f"| {t} | {n} |" for t, n in tag_count.most_common()]
    authors = Counter(i.url.split("/")[3] for i in items if i.source == "x")
    if authors:
        out += ["", "## Accounts you save most (candidate trusted sources)", ""]
        out += [f"- @{a}: {n}" for a, n in authors.most_common(15)]
    reshared = [i for i in items if i.times_shared > 1]
    if reshared:
        out += ["", "## Shared more than once (strong signal)", ""]
        out += [f"- {i.url} x{i.times_shared} - {' / '.join(i.notes)[:90]}" for i in reshared]
    out += ["", "## Next batch (high priority, new)", ""]
    out += [f"- `{i.id}` {i.url} - {' / '.join(i.notes)[:90] or '(no note)'}"
            for i in new if i.priority == "high"][:30]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ main ---

SAMPLE = """[15/6/26, 10:21:41 a. m.] Ana: ‎Creaste el grupo "Links".
[15/6/26, 10:32:28 a. m.] Ana: https://x.com/Someone/status/111?s=48
[15/6/26, 10:48:17 a. m.] Ana: https://x.com/other/status/222/video/1?s=48

Modelo Local
[16/6/26, 9:19:12 p. m.] Ana: https://twitter.com/someone/status/111

Bible
[17/6/26, 8:00:00 a. m.] Ana: Capability First

Nunca investigar herramientas como objetivo.
[17/6/26, 8:01:00 a. m.] Ana: 5550001234
‎[17/6/26, 8:02:00 a. m.] Ana: No pasarme con las config ‎<adjunto: 0001-PHOTO.jpg>
[18/6/26, 12:19:22 a. m.] Ana: https://youtu.be/abc?si=zzz https://www.linkedin.com/posts/x?utm_medium=ios&rcm=SECRET

Hermes vps
"""


def self_test() -> None:
    items, thoughts = build(parse_messages(SAMPLE), done={"none"})
    by_url = {i.url: i for i in items}
    a = by_url["https://x.com/someone/status/111"]
    assert a.times_shared == 2 and a.priority == "high" and a.notes == ["Bible"], a
    b = by_url["https://x.com/other/status/222"]
    assert "local-models" in b.tags and b.layers == ["orquestacion"], b
    li = [u for u in by_url if "linkedin" in u][0]
    assert "rcm" not in li and "utm" not in li, li
    assert "https://youtube.com/watch?v=abc" in by_url
    assert by_url["https://youtube.com/watch?v=abc"].tags == ["hermes", "infra-vps"]
    texts = [t["text"] for t in thoughts]
    assert any(t.startswith("Capability First") for t in texts), texts
    assert not any("5550001234" in t for t in texts), "bare numbers must be dropped"
    assert any(t["attachments"] == ["0001-PHOTO.jpg"] for t in thoughts), thoughts
    assert len(items) == 4, [i.url for i in items]
    assert tags_for("hay que crear un area real") == [], "short keywords need word boundaries"
    assert tags_for("REA video") == ["content-video"]
    print("self-test OK:", len(items), "items,", len(thoughts), "thoughts")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", nargs="?", type=Path, help="WhatsApp .zip or _chat.txt")
    ap.add_argument("--out", type=Path, default=Path("radar"))
    ap.add_argument("--state", type=Path, help="file with processed item ids, one per line")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.export:
        ap.error("export path required")
    state = args.state or args.out / "processed.txt"
    done = set(state.read_text().split()) if state.exists() else set()
    items, thoughts = build(parse_messages(read_export(args.export)), done)
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "inbox.jsonl", "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it.__dict__, ensure_ascii=False) + "\n")
    with open(args.out / "thoughts.jsonl", "w", encoding="utf-8") as fh:
        for t in thoughts:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    (args.out / "inbox.md").write_text(summary_md(items, thoughts), encoding="utf-8")
    new = sum(i.status == "new" for i in items)
    print(f"{len(items)} links ({new} new), {len(thoughts)} notes -> {args.out}/")


if __name__ == "__main__":
    main()
