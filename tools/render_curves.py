#!/usr/bin/env python3
"""Renders the two Prospect Theory curves as static SVGs for the playbook.

    python3 tools/render_curves.py            # writes docs/prospect-theory/img/*.svg

The curves are computed from tools/prospect_theory.py, so if the parameters
change the charts stay honest. Light and dark styles are both embedded.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import prospect_theory as pt  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "prospect-theory", "img")
W, H = 720, 440
M = {"l": 64, "r": 32, "t": 84, "b": 56}

STYLE = """
  <style>
    svg { --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
          --grid:#e1e0d9; --axis:#c3c2b7; --gain:#2a78d6; --loss:#e34948; }
    @media (prefers-color-scheme: dark) {
      svg { --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#898781;
            --grid:#2c2c2a; --axis:#383835; --gain:#3987e5; --loss:#e66767; }
    }
    text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--ink2); }
    .bg { fill: var(--surface); }
    .title { font-size: 18px; font-weight: 600; fill: var(--ink); }
    .sub { font-size: 13px; }
    .tick { font-size: 11px; fill: var(--muted); font-variant-numeric: tabular-nums; }
    .lbl { font-size: 12.5px; }
    .lbl-strong { font-size: 12.5px; font-weight: 600; fill: var(--ink); }
    .grid { stroke: var(--grid); stroke-width: 1; }
    .axis { stroke: var(--axis); stroke-width: 1; }
    .gain { stroke: var(--gain); stroke-width: 2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
    .loss { stroke: var(--loss); stroke-width: 2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
    .ref { stroke: var(--muted); stroke-width: 2; fill: none; stroke-linecap: round; }
    .leader { stroke: var(--muted); stroke-width: 1; fill: none; }
    .dot-gain { fill: var(--gain); stroke: var(--surface); stroke-width: 2; }
    .dot-loss { fill: var(--loss); stroke: var(--surface); stroke-width: 2; }
    .dot-ref { fill: var(--ink); stroke: var(--surface); stroke-width: 2; }
    .key-gain { fill: var(--gain); } .key-loss { fill: var(--loss); } .key-ref { fill: var(--muted); }
  </style>"""


def _scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) * (r1 - r0) / (d1 - d0)


def _path(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def _num(x, decimals=0):
    s = f"{x:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")  # es-AR formatting


def _legend(items, x, y):
    out, cx = [], x
    for cls, label in items:
        out.append(f'<rect class="{cls}" x="{cx}" y="{y - 9}" width="14" height="4" rx="2"/>')
        out.append(f'<text class="lbl" x="{cx + 20}" y="{y - 4}">{label}</text>')
        cx += 28 + len(label) * 6.6
    return "\n  ".join(out)


def value_svg() -> str:
    x0, x1, y0, y1 = -100, 100, -140, 70
    sx = _scale(x0, x1, M["l"], W - M["r"])
    sy = _scale(y0, y1, H - M["b"], M["t"])
    gains = [(sx(x), sy(pt.value(x))) for x in [i / 2 for i in range(0, 201)]]
    losses = [(sx(-x), sy(pt.value(-x))) for x in [i / 2 for i in range(0, 201)]]

    grid = []
    for v in range(-120, 61, 30):
        grid.append(f'<line class="grid" x1="{M["l"]}" x2="{W - M["r"]}" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>')
        grid.append(f'<text class="tick" x="{M["l"] - 8}" y="{sy(v) + 4:.1f}" text-anchor="end">{_num(v)}</text>')
    for v in (-100, -50, 50, 100):  # 0 is the reference-point dot
        grid.append(f'<text class="tick" x="{sx(v):.1f}" y="{sy(0) + 16:.1f}" text-anchor="middle">{_num(v)}</text>')

    g100, l100 = pt.value(100), pt.value(-100)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Curva de valor de Prospect Theory</title>
  <desc id="d">Valor subjetivo de un cambio respecto del punto de referencia. Ganar 100 vale {_num(g100, 1)}; perder 100 vale {_num(l100, 1)}, unas {_num(-l100 / g100, 2)} veces más. Parámetros Tversky y Kahneman 1992.</desc>{STYLE}
  <rect class="bg" width="{W}" height="{H}" rx="8"/>
  <text class="title" x="{M["l"]}" y="30">Curva 1 · La curva de valor</text>
  <text class="sub" x="{M["l"]}" y="50">Valor subjetivo v(x) de un cambio x respecto del punto de referencia (α = β = 0,88, λ = 2,25)</text>
  {_legend([("key-gain", "Ganancias: cóncava"), ("key-loss", "Pérdidas: convexa y más empinada")], M["l"], 72)}
  {chr(10).join("  " + g for g in grid).strip()}
  <line class="axis" x1="{M["l"]}" x2="{W - M["r"]}" y1="{sy(0):.1f}" y2="{sy(0):.1f}"/>
  <line class="axis" x1="{sx(0):.1f}" x2="{sx(0):.1f}" y1="{M["t"]}" y2="{H - M["b"]}"/>
  <path class="loss" d="{_path(losses)}"/>
  <path class="gain" d="{_path(gains)}"/>
  <circle class="dot-ref" cx="{sx(0):.1f}" cy="{sy(0):.1f}" r="4.5"/>
  <text class="lbl-strong" x="{sx(0) + 10:.1f}" y="{sy(0) + 34:.1f}">Punto de referencia</text>
  <text class="lbl" x="{sx(0) + 10:.1f}" y="{sy(0) + 50:.1f}">donde la persona cree que está hoy</text>
  <circle class="dot-gain" cx="{sx(100):.1f}" cy="{sy(g100):.1f}" r="4.5"/>
  <text class="lbl-strong" x="{sx(100) - 10:.1f}" y="{sy(g100) - 12:.1f}" text-anchor="end">ganar 100 → {_num(g100, 1)}</text>
  <text class="lbl" x="{sx(100) - 10:.1f}" y="{sy(g100) + 46:.1f}" text-anchor="end">aversión al riesgo</text>
  <circle class="dot-loss" cx="{sx(-100):.1f}" cy="{sy(l100):.1f}" r="4.5"/>
  <text class="lbl-strong" x="{sx(-100) + 10:.1f}" y="{sy(l100) + 4:.1f}">perder 100 → {_num(l100, 1)}  (≈ {_num(-l100 / g100, 2)}×)</text>
  <text class="lbl" x="{sx(-100) + 10:.1f}" y="{sy(l100) - 14:.1f}">búsqueda de riesgo</text>
  <text class="tick" x="{W - M["r"]}" y="{H - 14}" text-anchor="end">Cambio en dinero (x)</text>
</svg>
"""


def weight_svg() -> str:
    sx = _scale(0, 1, M["l"], W - M["r"])
    sy = _scale(0, 1, H - M["b"], M["t"])
    ps = [i / 400 for i in range(0, 401)]
    curve = [(sx(p), sy(pt.weight(p))) for p in ps]
    grid = []
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        grid.append(f'<line class="grid" x1="{M["l"]}" x2="{W - M["r"]}" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>')
        grid.append(f'<text class="tick" x="{M["l"] - 8}" y="{sy(v) + 4:.1f}" text-anchor="end">{int(v * 100)} %</text>')
        grid.append(f'<text class="tick" x="{sx(v):.1f}" y="{H - M["b"] + 18}" text-anchor="middle">{int(v * 100)} %</text>')
    w01, w95 = pt.weight(0.01), pt.weight(0.95)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Curva de ponderación de probabilidades</title>
  <desc id="d">Peso de decisión w(p) frente a la probabilidad real p. Un 1 % se procesa como {_num(w01 * 100, 1)} % y un 95 % como {_num(w95 * 100, 1)} %. Parámetro gamma 0,61 (Tversky y Kahneman 1992).</desc>{STYLE}
  <rect class="bg" width="{W}" height="{H}" rx="8"/>
  <text class="title" x="{M["l"]}" y="30">Curva 2 · El peso de las probabilidades</text>
  <text class="sub" x="{M["l"]}" y="50">Peso de decisión w(p) que usamos al elegir, frente a la probabilidad real p (γ = 0,61)</text>
  {_legend([("key-gain", "Peso de decisión w(p)"), ("key-ref", "Sin distorsión: w(p) = p")], M["l"], 72)}
  {chr(10).join("  " + g for g in grid).strip()}
  <line class="axis" x1="{M["l"]}" x2="{W - M["r"]}" y1="{sy(0):.1f}" y2="{sy(0):.1f}"/>
  <path class="ref" d="M{sx(0):.1f},{sy(0):.1f} L{sx(1):.1f},{sy(1):.1f}"/>
  <path class="gain" d="{_path(curve)}"/>
  <path class="leader" d="M{sx(0.01) + 5:.1f},{sy(w01) + 2:.1f} L{sx(0.115):.1f},{sy(0.095) - 4:.1f}"/>
  <circle class="dot-gain" cx="{sx(0.01):.1f}" cy="{sy(w01):.1f}" r="4.5"/>
  <text class="lbl-strong" x="{sx(0.12):.1f}" y="{sy(0.095):.1f}">1 % real → {_num(w01 * 100, 1)} %</text>
  <text class="lbl" x="{sx(0.12):.1f}" y="{sy(0.095) + 16:.1f}">sobreestimamos lo improbable: lotería y seguros</text>
  <path class="leader" d="M{sx(0.95):.1f},{sy(w95) + 6:.1f} L{sx(0.95):.1f},{sy(0.47):.1f}"/>
  <circle class="dot-gain" cx="{sx(0.95):.1f}" cy="{sy(w95):.1f}" r="4.5"/>
  <text class="lbl-strong" x="{sx(0.95) - 8:.1f}" y="{sy(0.42):.1f}" text-anchor="end">95 % real → {_num(w95 * 100, 1)} %</text>
  <text class="lbl" x="{sx(0.95) - 8:.1f}" y="{sy(0.42) + 16:.1f}" text-anchor="end">subestimamos lo casi seguro</text>
  <text class="tick" x="{W - M["r"]}" y="{H - 14}" text-anchor="end">Probabilidad real (p)</text>
</svg>
"""


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("value-function.svg", value_svg()), ("probability-weighting.svg", weight_svg())):
        path = os.path.normpath(os.path.join(OUT, name))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("wrote", os.path.relpath(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
