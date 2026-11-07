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
    raise NotImplementedError("Your code here: see the TODO above")


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
    raise NotImplementedError("Your code here: see the TODO above")


SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|SESSION|COOKIE|AUTH", re.I)


def scrub_env(env: dict[str, str] | None = None, keep: tuple[str, ...] = ("PATH", "LANG", "TZ")) -> dict[str, str]:
    """Build the environment for an agent's commands: an allow-list, never a deny-list.

    Return only the variables named in `keep`, and drop even those if their
    name looks like a secret. A deny-list misses the variable nobody thought of.
    """
    env = dict(os.environ if env is None else env)
    # TODO: keep only names in `keep` whose names do not match SECRET_NAME.
    raise NotImplementedError("Your code here: see the TODO above")


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
    raise NotImplementedError("Your code here: see the TODO above")
