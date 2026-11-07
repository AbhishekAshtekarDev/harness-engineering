"""Project 03: permission rules, a path guard, secret scrubbing, and a trifecta check."""
from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Rule:
    effect: str      # "allow" | "ask" | "deny"
    tool: str        # glob on the tool name
    pattern: str = "*"  # glob on the subject (a path or a command)


def decide(rules: list[Rule], tool: str, subject: str, default: str = "ask") -> str:
    """Return "allow", "ask" or "deny".

    Precedence: any matching deny wins, then any matching ask, then allow.
    Rule order in the list must not matter.
    """
    # TODO: check deny rules, then ask rules, then allow rules; fall back to default.
    # BEGIN SOLUTION
    for effect in ("deny", "ask", "allow"):
        for r in rules:
            if r.effect == effect and fnmatch.fnmatchcase(tool, r.tool) and fnmatch.fnmatchcase(subject, r.pattern):
                return effect
    return default
    # END SOLUTION


class PathDenied(PermissionError):
    pass


def check_write(root: str | Path, relative: str, writable: tuple[str, ...], protected: tuple[str, ...] = ()) -> Path:
    """Return the resolved path if the agent may write it; raise PathDenied otherwise.

    Must refuse: absolute paths outside root, ../ escapes, symlinks that point
    outside root, protected files, and anything outside the writable globs.
    The error message must tell the agent where it *may* write.
    """
    # TODO: resolve root and (root / relative) with .resolve() (this follows symlinks and ../).
    # TODO: refuse targets that are not root itself or inside it.
    # TODO: compute the posix path relative to root; refuse protected matches first, then non-writable.
    # BEGIN SOLUTION
    base = Path(root).resolve()
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise PathDenied(f"'{relative}' is outside the workspace. Writable: {', '.join(writable)}")
    rel = target.relative_to(base).as_posix()
    if any(fnmatch.fnmatchcase(rel, p) for p in protected):
        raise PathDenied(f"'{rel}' is protected. Writable: {', '.join(writable)}")
    if not any(fnmatch.fnmatchcase(rel, p) for p in writable):
        raise PathDenied(f"'{rel}' is not writable. Writable: {', '.join(writable)}")
    return target
    # END SOLUTION


SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|SESSION|COOKIE|AUTH", re.I)


def scrub_env(env: dict[str, str] | None = None, keep: tuple[str, ...] = ("PATH", "LANG", "TZ")) -> dict[str, str]:
    """Build the environment for an agent's commands: an allow-list, never a deny-list.

    Return only the variables named in `keep`, and drop even those if their
    name looks like a secret. A deny-list misses the variable nobody thought of.
    """
    env = dict(os.environ if env is None else env)
    # TODO: keep only names in `keep` whose names do not match SECRET_NAME.
    # BEGIN SOLUTION
    return {k: v for k, v in env.items() if k in keep and not SECRET_NAME.search(k)}
    # END SOLUTION


@dataclass
class Capabilities:
    reads_private_data: bool      # source code with secrets, customer records, email...
    sees_untrusted_content: bool  # web pages, public issues, inbound email, third-party docs
    can_communicate_out: bool     # network, posting comments, sending email, opening URLs


def trifecta_report(c: Capabilities) -> str:
    """Name the legs present. All three together is Simon Willison's "lethal trifecta"."""
    legs = [name for name, on in (("private data", c.reads_private_data),
                                  ("untrusted content", c.sees_untrusted_content),
                                  ("external communication", c.can_communicate_out)) if on]
    # TODO: if all three legs are present return a message starting with "LETHAL TRIFECTA"
    #       that says to remove at least one leg; otherwise "ok: <legs> present" (or "ok: none").
    # BEGIN SOLUTION
    if len(legs) == 3:
        return ("LETHAL TRIFECTA: private data + untrusted content + external communication. "
                "Remove at least one leg (split the agent, close the network, or keep secrets out).")
    return f"ok: {', '.join(legs) or 'none'} present"
    # END SOLUTION
