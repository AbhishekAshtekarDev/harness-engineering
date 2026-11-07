"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
import pytest

from evalkit import cohen_kappa, compare, pairwise_judge, pass_at_k, pass_pow_k, wilson_interval


def test_pass_at_k_vs_pass_pow_k():
    # Anthropic's example: 75% per trial -> about 42% that all 3 succeed
    assert pass_pow_k(100, 75, 3) == pytest.approx(0.75 ** 3, abs=0.01)
    assert pass_at_k(100, 75, 3) == pytest.approx(1 - 0.25 ** 3, abs=0.01)
    assert pass_at_k(5, 0, 2) == 0.0 and pass_pow_k(5, 5, 2) == 1.0
    assert pass_at_k(3, 2, 2) == 1.0  # with 1 failure among 3, any 2 include a pass
    with pytest.raises(ValueError):
        pass_at_k(2, 1, 3)


def test_wilson_interval_is_wide_for_small_samples():
    lo, hi = wilson_interval(8, 10)
    assert 0.48 < lo < 0.50 and 0.94 < hi < 0.96
    lo2, hi2 = wilson_interval(800, 1000)
    assert hi2 - lo2 < 0.06
    assert wilson_interval(0, 0) == (0.0, 1.0)


def test_compare_refuses_to_overclaim():
    assert compare(7, 10, 9, 10) == "inconclusive"   # 70% vs 90% on 10 tasks proves nothing
    assert compare(70, 100, 95, 100) == "better"
    assert compare(95, 100, 70, 100) == "worse"


def test_pairwise_judge_cancels_position_bias():
    always_first = lambda a, b: "first"                       # a judge with pure position bias
    assert pairwise_judge(always_first, "short", "long") == "tie"
    prefers_long = lambda a, b: "first" if len(a) > len(b) else "second"
    assert pairwise_judge(prefers_long, "short", "a much longer answer") == "B"


def test_cohen_kappa():
    human = [True, True, False, False, True, False, True, False]
    assert cohen_kappa(human, human) == 1.0
    assert cohen_kappa([True] * 8, human) == pytest.approx(0.0)  # always-PASS judge agrees 50% by chance
    assert cohen_kappa([not h for h in human], human) == pytest.approx(-1.0)
