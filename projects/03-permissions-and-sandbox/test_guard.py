import sys
"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
import pytest

from guard import Capabilities, PathDenied, Rule, check_write, decide, scrub_env, trifecta_report

RULES = [
    Rule("allow", "run_command", "python -m pytest*"),
    Rule("allow", "run_command", "git *"),
    Rule("deny", "run_command", "git push*"),
    Rule("ask", "run_command", "pip install*"),
    Rule("allow", "read_file"),
]


def test_deny_wins_over_allow_whatever_the_order():
    assert decide(RULES, "run_command", "git push origin main") == "deny"
    assert decide(list(reversed(RULES)), "run_command", "git push origin main") == "deny"
    assert decide(RULES, "run_command", "git status") == "allow"
    assert decide(RULES, "run_command", "pip install requests") == "ask"
    assert decide(RULES, "run_command", "make deploy") == "ask"  # default
    assert decide(RULES, "read_file", "src/app.py") == "allow"


def test_rules_are_tripwires_not_walls():
    """Command rules match text, so the same action written differently slips through.
    This test documents the limitation: it is why an OS sandbox must hold the line."""
    for sneaky in ("git -C . push origin main", "GIT_TRACE=1 git push", "sh -c 'git push'"):
        assert decide(RULES, "run_command", sneaky) != "deny"


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need admin rights on Windows")
def test_path_guard(tmp_path):
    (tmp_path / "src").mkdir()
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("x")
    (tmp_path / "src" / "evil").symlink_to(outside)
    w, p = ("src/*", "tests/*"), ("tests/test_existing.py",)
    assert check_write(tmp_path, "src/new.py", w, p).name == "new.py"
    for bad in ("../x.py", "/etc/passwd", "src/../../x.py", "src/evil", "config/app.toml", "tests/test_existing.py"):
        with pytest.raises(PathDenied) as err:
            check_write(tmp_path, bad, w, p)
        assert "Writable" in str(err.value), "the error must say where writing is allowed"


def test_env_is_an_allow_list():
    env = {"PATH": "/bin", "OPENAI_API_KEY": "sk-1", "GITHUB_TOKEN": "t", "AWS_SECRET_ACCESS_KEY": "s",
           "DATABASE_URL": "postgres://u:p@prod/db", "HOME": "/home/me", "TZ": "UTC"}
    out = scrub_env(env, keep=("PATH", "TZ", "GITHUB_TOKEN"))
    assert out == {"PATH": "/bin", "TZ": "UTC"}, "only allow-listed names, and never secret-looking ones"


def test_trifecta():
    assert trifecta_report(Capabilities(True, True, True)).startswith("LETHAL TRIFECTA")
    assert trifecta_report(Capabilities(True, True, False)) == "ok: private data, untrusted content present"
    assert trifecta_report(Capabilities(False, False, False)) == "ok: none present"
