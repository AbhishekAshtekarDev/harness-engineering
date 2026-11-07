"""Project 08: the arithmetic and judgment behind agent evals.

Agents are non-deterministic, so one run proves little. These functions turn
many runs into numbers you can trust, and tell you when you cannot.
"""
from __future__ import annotations

from math import comb, sqrt
from typing import Callable


def pass_at_k(n: int, c: int, k: int) -> float:
    """P(at least one of k attempts passes), unbiased estimate from n trials with c passes.

    Formula: 1 - C(n-c, k) / C(n, k)   (and 1.0 when n - c < k)
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def pass_pow_k(n: int, c: int, k: int) -> float:
    """P(all k attempts pass), unbiased estimate: C(c, k) / C(n, k)."""
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% confidence interval for a pass rate (Wilson score interval).

    centre = (p + z^2/(2n)) / (1 + z^2/n)
    half   = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n)
    """
    # TODO: return (centre - half, centre + half), clipped to [0, 1]. n == 0 -> (0.0, 1.0).
    raise NotImplementedError("Your code here: see the TODO above")


def compare(a_pass: int, a_n: int, b_pass: int, b_n: int) -> str:
    """Is B really better than A? 'better', 'worse', or 'inconclusive' (the 95% intervals overlap).

    Overlapping intervals is a conservative rule of thumb, not a formal test,
    and that is the point: small eval sets rarely support strong claims.
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def pairwise_judge(ask: Callable[[str, str], str], answer_a: str, answer_b: str) -> str:
    """Ask a judge to compare two answers in BOTH orders, to cancel position bias.

    ask(first, second) returns "first", "second" or "tie".
    Return "A", "B", or "tie" (also "tie" when the two orders disagree).
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def cohen_kappa(judge: list[bool], human: list[bool]) -> float:
    """Agreement between a model judge and human labels, corrected for chance.

    kappa = (p_observed - p_expected) / (1 - p_expected); 1.0 if p_expected == 1.
    p_expected = P(both true) + P(both false) under independence.
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")
