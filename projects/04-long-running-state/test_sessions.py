"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
import json

import pytest

from sessions import (Briefing, checkpoint, complete_feature, guard_feature_list, initialize, rollback,
                      start_session)

FEATURES = ["add(a, b) returns the sum", "sub(a, b) returns the difference", "mul(a, b) returns the product"]
IMPLS = {"F001": "def add(a, b):\n    return a + b\n", "F002": "def sub(a, b):\n    return a - b\n",
         "F003": "def mul(a, b):\n    return a * b\n"}


def project_with_calc(tmp_path):
    (tmp_path / "calc.py").write_text("", encoding="utf-8")
    initialize(tmp_path, FEATURES)
    return tmp_path


def make_verify(project):
    def verify(fid):
        ns = {}
        try:
            exec((project / "calc.py").read_text(encoding="utf-8"), ns)
            return {"F001": lambda: ns["add"](2, 3) == 5, "F002": lambda: ns["sub"](5, 3) == 2,
                    "F003": lambda: ns["mul"](2, 3) == 6}[fid]()
        except Exception:
            return False
    return verify


def smoke(project):
    def check():
        try:
            compile((project / "calc.py").read_text(encoding="utf-8"), "calc.py", "exec")
            return True
        except SyntaxError:
            return False
    return check


def test_initializer_runs_once(tmp_path):
    p = project_with_calc(tmp_path)
    items = json.loads((p / ".agent" / "feature_list.json").read_text(encoding="utf-8"))
    assert [f["id"] for f in items] == ["F001", "F002", "F003"] and not any(f["passes"] for f in items)
    with pytest.raises(RuntimeError):
        initialize(p, FEATURES)


def test_a_feature_passes_only_after_verification(tmp_path):
    p = project_with_calc(tmp_path)
    verify = make_verify(p)
    assert complete_feature(p, "F001", verify, "claimed done without code") is False
    (p / "calc.py").write_text(IMPLS["F001"], encoding="utf-8")
    assert complete_feature(p, "F001", verify, "implemented add") is True
    b = start_session(p, smoke(p))
    assert isinstance(b, Briefing) and b.done == 1 and b.next_feature["id"] == "F002"
    assert "FAILING" in b.recent_progress and "F001 passing" in b.last_checkpoint


def test_crash_mid_feature_is_detected_and_rolled_back(tmp_path):
    p = project_with_calc(tmp_path)
    verify = make_verify(p)
    (p / "calc.py").write_text(IMPLS["F001"], encoding="utf-8")
    assert complete_feature(p, "F001", verify, "add")
    # session 2 crashes halfway through writing sub():
    (p / "calc.py").write_text(IMPLS["F001"] + "def sub(a, b)\n    return a -", encoding="utf-8")
    b = start_session(p, smoke(p), verify)
    assert not b.smoke_ok and any("roll back" in w for w in b.warnings)
    rollback(p, 2)  # checkpoint 2 = "F001 passing"
    b = start_session(p, smoke(p), verify)
    assert b.smoke_ok and b.warnings == [] and b.next_feature["id"] == "F002"


def test_records_that_lie_are_caught(tmp_path):
    p = project_with_calc(tmp_path)
    data = json.loads((p / ".agent" / "feature_list.json").read_text(encoding="utf-8"))
    data[2]["passes"] = True  # someone (or some agent) edited the file by hand
    (p / ".agent" / "feature_list.json").write_text(json.dumps(data), encoding="utf-8")
    b = start_session(p, smoke(p), make_verify(p))
    assert any("F003" in w for w in b.warnings)


def test_feature_list_rewrites_are_guarded():
    old = [{"id": "F001", "description": "a", "passes": False}]
    guard_feature_list(old, [{"id": "F001", "description": "a", "passes": True}])
    with pytest.raises(ValueError):
        guard_feature_list(old, [{"id": "F001", "description": "easier version", "passes": True}])
    with pytest.raises(ValueError):
        guard_feature_list(old, [])


def test_checkpoint_numbers_increase(tmp_path):
    p = project_with_calc(tmp_path)
    assert checkpoint(p, "manual") == 2
