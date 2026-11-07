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
    # BEGIN SOLUTION
    if k > n:
        raise ValueError("k > n")
    return 1.0 if n - c < k else 1.0 - comb(n - c, k) / comb(n, k)
    # END SOLUTION


def pass_pow_k(n: int, c: int, k: int) -> float:
    """P(all k attempts pass), unbiased estimate: C(c, k) / C(n, k)."""
    # TODO
    # BEGIN SOLUTION
    if k > n:
        raise ValueError("k > n")
    return comb(c, k) / comb(n, k)
    # END SOLUTION


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% confidence interval for a pass rate (Wilson score interval).

    centre = (p + z^2/(2n)) / (1 + z^2/n)
    half   = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n)
    """
    # TODO: return (centre - half, centre + half), clipped to [0, 1]. n == 0 -> (0.0, 1.0).
    # BEGIN SOLUTION
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)
    # END SOLUTION


def compare(a_pass: int, a_n: int, b_pass: int, b_n: int) -> str:
    """Is B really better than A? 'better', 'worse', or 'inconclusive' (the 95% intervals overlap).

    Overlapping intervals is a conservative rule of thumb, not a formal test,
    and that is the point: small eval sets rarely support strong claims.
    """
    # TODO
    # BEGIN SOLUTION
    a_lo, a_hi = wilson_interval(a_pass, a_n)
    b_lo, b_hi = wilson_interval(b_pass, b_n)
    if b_lo > a_hi:
        return "better"
    if b_hi < a_lo:
        return "worse"
    return "inconclusive"
    # END SOLUTION


def pairwise_judge(ask: Callable[[str, str], str], answer_a: str, answer_b: str) -> str:
    """Ask a judge to compare two answers in BOTH orders, to cancel position bias.

    ask(first, second) returns "first", "second" or "tie".
    Return "A", "B", or "tie" (also "tie" when the two orders disagree).
    """
    # TODO
    # BEGIN SOLUTION
    one = ask(answer_a, answer_b)               # A shown first
    two = ask(answer_b, answer_a)               # B shown first
    vote1 = {"first": "A", "second": "B"}.get(one, "tie")
    vote2 = {"first": "B", "second": "A"}.get(two, "tie")
    return vote1 if vote1 == vote2 else "tie"
    # END SOLUTION


def cohen_kappa(judge: list[bool], human: list[bool]) -> float:
    """Agreement between a model judge and human labels, corrected for chance.

    kappa = (p_observed - p_expected) / (1 - p_expected); 1.0 if p_expected == 1.
    p_expected = P(both true) + P(both false) under independence.
    """
    # TODO
    # BEGIN SOLUTION
    n = len(judge)
    po = sum(j == h for j, h in zip(judge, human)) / n
    pj, ph = sum(judge) / n, sum(human) / n
    pe = pj * ph + (1 - pj) * (1 - ph)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)
    # END SOLUTION
