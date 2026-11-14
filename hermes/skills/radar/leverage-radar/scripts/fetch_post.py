#!/usr/bin/env python3
"""Fetch the text behind a radar link without a browser (stdlib only).

Cheap first attempt so the agent only opens a browser when this fails.
  x.com/<user>/status/<id> -> api.fxtwitter.com JSON, fallback publish.twitter.com oEmbed
  github.com/<owner>/<repo> -> api.github.com metadata (stars, last push, license) + README head
  anything else             -> {"ok": false}: use Hermes' web/browser tools instead

Prints one JSON object per URL. Never logs in, never sends cookies or tokens.

Usage:
  python3 fetch_post.py https://x.com/user/status/123 https://github.com/owner/repo
  python3 fetch_post.py --self-test
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from typing import Any

UA = "radar-fetch/1.0 (+personal research tool)"
TIMEOUT = 20
MAX_TEXT = 6000


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, */*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def _strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def _collect_text(node: Any, out: list[str]) -> None:
    """Pull every 'text'/'title'/'preview_text' string out of nested JSON (X Articles)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in {"text", "title", "preview_text"} and isinstance(v, str) and v.strip():
                out.append(v.strip())
            else:
                _collect_text(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_text(v, out)


# ---------------------------------------------------------------- parsers ---

def parse_fxtwitter(data: dict) -> dict:
    t = data.get("tweet") or {}
    parts = [t.get("text") or ""]
    if t.get("article"):
        art: list[str] = []
        _collect_text(t["article"], art)
        parts.append("\n".join(dict.fromkeys(art)))
    quote = (t.get("quote") or {}).get("text")
    return {
        "ok": bool(t),
        "via": "fxtwitter",
        "author": (t.get("author") or {}).get("screen_name"),
        "date": t.get("created_at"),
        "text": "\n\n".join(p for p in parts if p)[:MAX_TEXT],
        "quoted": quote,
        "metrics": {k: t.get(k) for k in ("likes", "retweets", "replies", "views", "bookmarks") if k in t},
    }


def parse_oembed(data: dict) -> dict:
    block = data.get("html") or ""
    m = re.search(r"<p[^>]*>(.*?)</p>", block, flags=re.S)
    return {
        "ok": bool(m),
        "via": "oembed",
        "author": (data.get("author_url") or "").rstrip("/").rsplit("/", 1)[-1] or None,
        "text": _strip_html(m.group(1))[:MAX_TEXT] if m else "",
        "note": "oEmbed only returns the first post; long X Articles need a browser",
    }


def parse_github(meta: dict, readme: str) -> dict:
    return {
        "ok": bool(meta) or bool(readme),
        "via": "github",
        "description": meta.get("description"),
        "stars": meta.get("stargazers_count"),
        "forks": meta.get("forks_count"),
        "open_issues": meta.get("open_issues_count"),
        "last_push": meta.get("pushed_at"),
        "created": meta.get("created_at"),
        "license": (meta.get("license") or {}).get("spdx_id"),
        "archived": meta.get("archived"),
        "language": meta.get("language"),
        "text": readme[:MAX_TEXT],
    }


# ---------------------------------------------------------------- fetchers ---

def fetch(url: str) -> dict:
    out: dict = {"url": url}
    m = re.match(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/([^/]+)/status/(\d+)", url)
    if m:
        user, sid = m.groups()
        try:
            out.update(parse_fxtwitter(json.loads(_get(f"https://api.fxtwitter.com/{user}/status/{sid}"))))
            if out.get("ok"):
                return out
        except Exception as e:  # noqa: BLE001 - report and fall back
            out["fxtwitter_error"] = str(e)
        try:
            q = urllib.request.quote(f"https://x.com/{user}/status/{sid}", safe="")
            out.update(parse_oembed(json.loads(_get(f"https://publish.twitter.com/oembed?url={q}&omit_script=1"))))
        except Exception as e:  # noqa: BLE001
            out.update({"ok": False, "oembed_error": str(e)})
        return out
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+)", url)
    if m:
        owner, repo = m.group(1), m.group(2).removesuffix(".git")
        meta: dict = {}
        readme = ""
        try:
            meta = json.loads(_get(f"https://api.github.com/repos/{owner}/{repo}"))
        except Exception as e:  # noqa: BLE001
            out["api_error"] = str(e)
        try:
            readme = _get(f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md").decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            out["readme_error"] = str(e)
        out.update(parse_github(meta, readme))
        return out
    out.update({"ok": False, "via": None, "hint": "not supported here: use web_extract or the browser"})
    return out


def self_test() -> None:
    fx = {"tweet": {"text": "hola", "author": {"screen_name": "a"}, "likes": 3,
                    "article": {"title": "T", "content": {"blocks": [{"text": "p1"}, {"text": "p2"}]}},
                    "quote": {"text": "q"}}}
    r = parse_fxtwitter(fx)
    assert r["ok"] and r["author"] == "a" and "p2" in r["text"] and r["quoted"] == "q", r
    oe = {"author_url": "https://twitter.com/bob", "html": '<blockquote><p lang="es">uno<br>dos &amp; tres</p>&mdash; Bob</blockquote>'}
    r = parse_oembed(oe)
    assert r["ok"] and r["author"] == "bob" and r["text"] == "uno\ndos & tres", r
    r = parse_github({"stargazers_count": 10, "license": {"spdx_id": "MIT"}, "pushed_at": "2026-11-01"}, "# Repo")
    assert r["stars"] == 10 and r["license"] == "MIT" and r["text"] == "# Repo", r
    assert fetch("https://example.com/x")["ok"] is False
    print("self-test OK")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["--self-test"]:
        self_test() if args else sys.exit(__doc__)
    else:
        for u in args:
            print(json.dumps(fetch(u), ensure_ascii=False))
