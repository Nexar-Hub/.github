#!/usr/bin/env python3
"""Prospect Theory calculator (Kahneman & Tversky 1979; Tversky & Kahneman 1992).

Stdlib only. Turns the two curves of the theory into numbers you can use to
compare product framings before you spend an experiment on them.

    v(x) = x^alpha                 if x >= 0   (gains: concave)
    v(x) = -lambda * (-x)^beta     if x <  0   (losses: convex, steeper)

    w(p) = p^g / (p^g + (1-p)^g)^(1/g)         (g = gamma for gains, delta for losses)

Defaults are the 1992 median estimates: alpha = beta = 0.88, lambda = 2.25,
gamma = 0.61, delta = 0.69.

CLI examples:
    python3 spread/tools/prospect_theory.py value 100 -100
    python3 spread/tools/prospect_theory.py weight 0.01 0.95
    python3 spread/tools/prospect_theory.py edit 40 40          # segregate or integrate?
    python3 spread/tools/prospect_theory.py frame 300           # gain frame vs loss frame
    python3 spread/tools/prospect_theory.py raffle --prize 1000 --prob 0.01 --sure 10
    python3 spread/tools/prospect_theory.py prospect 10:0.5,0:0.5 5:1
    python3 spread/tools/prospect_theory.py prospect -- -10:0.5,0:0.5 -5:1
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Params:
    alpha: float = 0.88  # curvature, gains
    beta: float = 0.88  # curvature, losses
    lam: float = 2.25  # loss aversion
    gamma: float = 0.61  # probability weighting, gains
    delta: float = 0.69  # probability weighting, losses


TK1992 = Params()


# --------------------------------------------------------------------------- #
# Curve 1: value function
# --------------------------------------------------------------------------- #
def value(x: float, p: Params = TK1992) -> float:
    """Subjective value of a change x relative to the reference point."""
    if x >= 0:
        return x ** p.alpha
    return -p.lam * ((-x) ** p.beta)


def inverse_value(v: float, p: Params = TK1992) -> float:
    """Money change that produces subjective value v (certainty equivalent)."""
    if v >= 0:
        return v ** (1.0 / p.alpha)
    return -((-v / p.lam) ** (1.0 / p.beta))


# --------------------------------------------------------------------------- #
# Curve 2: probability weighting
# --------------------------------------------------------------------------- #
def weight(prob: float, gain: bool = True, p: Params = TK1992) -> float:
    """Decision weight the mind assigns to an objective probability."""
    if not 0.0 <= prob <= 1.0:
        raise ValueError(f"probability out of range: {prob}")
    if prob in (0.0, 1.0):
        return prob
    g = p.gamma if gain else p.delta
    num = prob ** g
    return num / ((num + (1.0 - prob) ** g) ** (1.0 / g))


# --------------------------------------------------------------------------- #
# Prospects (cumulative prospect theory, rank-dependent weights)
# --------------------------------------------------------------------------- #
Outcome = tuple[float, float]  # (money change, probability)


def _merge(outcomes: Iterable[Outcome]) -> list[Outcome]:
    merged: dict[float, float] = {}
    for x, pr in outcomes:
        merged[x] = merged.get(x, 0.0) + pr
    total = sum(merged.values())
    if not math.isclose(total, 1.0, abs_tol=1e-6):
        raise ValueError(f"probabilities must sum to 1 (got {total:.6f})")
    return list(merged.items())


def prospect_value(outcomes: Iterable[Outcome], p: Params = TK1992) -> float:
    """CPT value of a gamble given as [(x, prob), ...]."""
    items = _merge(outcomes)
    total = 0.0

    gains = sorted((o for o in items if o[0] > 0), key=lambda o: o[0], reverse=True)
    cum = 0.0
    for x, pr in gains:  # best outcome first
        hi = weight(min(cum + pr, 1.0), True, p)
        lo = weight(cum, True, p)
        total += (hi - lo) * value(x, p)
        cum += pr

    losses = sorted((o for o in items if o[0] < 0), key=lambda o: o[0])
    cum = 0.0
    for x, pr in losses:  # worst outcome first
        hi = weight(min(cum + pr, 1.0), False, p)
        lo = weight(cum, False, p)
        total += (hi - lo) * value(x, p)
        cum += pr

    return total


def certainty_equivalent(outcomes: Iterable[Outcome], p: Params = TK1992) -> float:
    """Sure amount the person would treat as equal to the gamble."""
    return inverse_value(prospect_value(outcomes, p), p)


def expected_value(outcomes: Iterable[Outcome]) -> float:
    return sum(x * pr for x, pr in _merge(outcomes))


# --------------------------------------------------------------------------- #
# Product helpers
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class EditResult:
    amounts: tuple[float, ...]
    segregated: float  # sum of v(x_i): each event shown on its own
    integrated: float  # v(sum x_i): everything shown as one number
    recommendation: str  # what the value function says: segregate | integrate | indifferent
    heuristic: str  # what Thaler's (1985) rule says: segregate | integrate
    rule: str
    agrees: bool  # False -> the model and the heuristic disagree: treat as a test


def hedonic_edit(amounts: Sequence[float], p: Params = TK1992) -> EditResult:
    """Should these events be shown apart or together? (Thaler 1985).

    Note: with loss aversion (lambda = 2.25) the value function only backs the
    "silver lining" rule when the gain is tiny next to the loss (roughly
    loss/gain > (lambda*beta)^(1/(1-alpha)), ~300x with the 1992 parameters).
    Thaler's rule 4 rests on his survey evidence and on mental accounting, not
    on the curve alone, so the helper reports both and flags disagreement.
    """
    seg = sum(value(a, p) for a in amounts)
    integ = value(sum(amounts), p)
    if math.isclose(seg, integ, rel_tol=1e-9, abs_tol=1e-9):
        rec = "indifferent"
    else:
        rec = "segregate" if seg > integ else "integrate"

    gains = [a for a in amounts if a > 0]
    losses = [a for a in amounts if a < 0]
    if gains and not losses:
        heur, rule = "segregate", "Multiple gains: show them separately."
    elif losses and not gains:
        heur, rule = "integrate", "Multiple losses: bundle them into one number."
    elif sum(amounts) >= 0:
        heur, rule = "integrate", "Large gain + small loss: fold the loss into the gain (cancellation)."
    else:
        heur, rule = "segregate", "Small gain + large loss: show the gain separately (silver lining)."
    agrees = rec in (heur, "indifferent")
    return EditResult(tuple(amounts), seg, integ, rec, heur, rule, agrees)


@dataclass(frozen=True)
class FrameResult:
    amount: float
    gain_frame: float  # v(+x): "earn X"
    loss_frame: float  # |v(-x)|: "you are leaving X on the table"
    ratio: float


def frame_comparison(amount: float, p: Params = TK1992) -> FrameResult:
    """Felt intensity of the same number framed as a gain vs as a loss."""
    g = value(abs(amount), p)
    l = -value(-abs(amount), p)
    return FrameResult(abs(amount), g, l, l / g if g else float("inf"))


@dataclass(frozen=True)
class RaffleResult:
    prize: float
    prob: float
    expected_value: float  # what it actually costs per participant
    felt_value: float  # certainty equivalent per participant
    sure_reward: float | None  # a sure amount's CE is itself
    multiplier: float  # felt value / expected value


def raffle(prize: float, prob: float, sure: float | None = None,
           p: Params = TK1992) -> RaffleResult:
    """Compare a raffle ticket against a sure reward of similar cost."""
    ce = certainty_equivalent([(prize, prob), (0.0, 1.0 - prob)], p)
    ev = prize * prob
    return RaffleResult(prize, prob, ev, ce, sure, ce / ev if ev else float("inf"))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _parse_prospect(text: str) -> list[Outcome]:
    out: list[Outcome] = []
    for part in text.split(","):
        x, pr = part.split(":")
        out.append((float(x), float(pr)))
    return out


def _fmt(x: float) -> str:
    return f"{x:,.2f}"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--alpha", type=float, default=TK1992.alpha)
    ap.add_argument("--beta", type=float, default=TK1992.beta)
    ap.add_argument("--lam", type=float, default=TK1992.lam)
    ap.add_argument("--gamma", type=float, default=TK1992.gamma)
    ap.add_argument("--delta", type=float, default=TK1992.delta)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("value", help="v(x) for one or more changes")
    s.add_argument("x", type=float, nargs="+")

    s = sub.add_parser("weight", help="w(p) for one or more probabilities")
    s.add_argument("prob", type=float, nargs="+")

    s = sub.add_parser("edit", help="segregate vs integrate several amounts")
    s.add_argument("amounts", type=float, nargs="+")

    s = sub.add_parser("frame", help="gain frame vs loss frame for one amount")
    s.add_argument("amount", type=float)

    s = sub.add_parser("raffle", help="raffle prize vs sure reward")
    s.add_argument("--prize", type=float, required=True)
    s.add_argument("--prob", type=float, required=True)
    s.add_argument("--sure", type=float)

    s = sub.add_parser("prospect", help='CPT value of "x:p,x:p,..." (optionally vs a second one)',
                       description='Put "--" before prospects that start with a minus sign: '
                                   'prospect -- -10:0.5,0:0.5 -5:1')
    s.add_argument("prospects", nargs="+", metavar="PROSPECT")

    a = ap.parse_args(argv)
    prm = Params(a.alpha, a.beta, a.lam, a.gamma, a.delta)

    if a.cmd == "value":
        for x in a.x:
            print(f"v({_fmt(x)}) = {_fmt(value(x, prm))}")
    elif a.cmd == "weight":
        for pr in a.prob:
            print(f"p = {pr:.2%}  ->  w+(p) = {weight(pr, True, prm):.2%} (gains)"
                  f"   w-(p) = {weight(pr, False, prm):.2%} (losses)")
    elif a.cmd == "edit":
        r = hedonic_edit(a.amounts, prm)
        print(f"amounts      : {', '.join(_fmt(x) for x in r.amounts)}")
        print(f"separately   : {_fmt(r.segregated)}")
        print(f"together     : {_fmt(r.integrated)}")
        print(f"model says   : {r.recommendation.upper()}")
        print(f"Thaler rule  : {r.heuristic.upper()}  ({r.rule})")
        if not r.agrees:
            print("WARNING      : model and heuristic disagree with these parameters; "
                  "run it as an experiment, do not assume either.")
    elif a.cmd == "frame":
        r = frame_comparison(a.amount, prm)
        print(f"gain frame  'earn {_fmt(r.amount)}'            : {_fmt(r.gain_frame)}")
        print(f"loss frame  'leaving {_fmt(r.amount)} on the table': {_fmt(r.loss_frame)}")
        print(f"loss frame is {r.ratio:.2f}x as intense (model prediction, test it)")
    elif a.cmd == "raffle":
        r = raffle(a.prize, a.prob, a.sure, prm)
        print(f"prize {_fmt(r.prize)} at {r.prob:.2%}")
        print(f"expected value per participant : {_fmt(r.expected_value)}")
        print(f"felt value per participant (CE): {_fmt(r.felt_value)}"
              f"  ({r.multiplier:.1f}x expected value)")
        if r.sure_reward is not None:
            better = "raffle" if r.felt_value > r.sure_reward else "sure reward"
            print(f"sure reward {_fmt(r.sure_reward)}; model favors the {better}")
    elif a.cmd == "prospect":
        if len(a.prospects) > 2:
            ap.error("prospect takes one or two prospects")
        vals = []
        for label, text in zip("AB", a.prospects):
            o = _parse_prospect(text)
            v = prospect_value(o, prm)
            vals.append(v)
            print(f"{label}: EV {_fmt(expected_value(o))}  V {_fmt(v)}"
                  f"  CE {_fmt(certainty_equivalent(o, prm))}")
        if len(vals) == 2:
            print("model prefers", "A" if vals[0] > vals[1] else "B" if vals[1] > vals[0] else "neither")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
