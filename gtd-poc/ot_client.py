"""Cliente mínimo de OpenTodo: MCP (lo que usa Claude) y REST (lo que hace la persona).

Sin dependencias: urllib de la biblioteca estándar.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


class OTError(RuntimeError):
    pass


class OT:
    def __init__(self, base: str, token: str):
        self.base = base.rstrip("/")
        self.token = token
        self._id = 0

    def _req(self, method: str, path: str, body=None, accept="application/json"):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", accept)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            raise OTError(f"{method} {path} -> {e.code}: {e.read()[:400]!r}") from None
        return json.loads(raw) if raw else None

    def rest(self, method: str, path: str, body=None):
        return self._req(method, path, body)

    def mcp(self, tool: str, args: dict | None = None) -> dict:
        self._id += 1
        msg = {"jsonrpc": "2.0", "id": self._id, "method": "tools/call",
               "params": {"name": tool, "arguments": args or {}}}
        out = self._req("POST", "/mcp", msg, accept="application/json, text/event-stream")
        if "error" in out:
            raise OTError(f"{tool}: {out['error']}")
        res = out["result"]
        if res.get("isError"):
            raise OTError(f"{tool}: {res['content'][0]['text'][:400]}")
        return res.get("structuredContent") or json.loads(res["content"][0]["text"])

    def all_tasks(self, **filters) -> list[dict]:
        """list_tasks paginado."""
        tasks, cursor = [], None
        while True:
            args = dict(filters, limit=200)
            if cursor:
                args["cursor"] = cursor
            page = self.mcp("list_tasks", args)
            tasks += page["tasks"]
            cursor = page.get("next_cursor")
            if not cursor:
                return tasks
