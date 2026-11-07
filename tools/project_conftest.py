# Shared by every project. Each project's conftest.py imports this.
import os
import sys
from pathlib import Path


def use(project_dir: Path) -> None:
    """Put exercise/ (default) or solution/ (SOLUTION=1) first on the import path."""
    folder = "solution" if os.environ.get("SOLUTION") == "1" else "exercise"
    sys.path.insert(0, str(project_dir / folder))
    sys.path.insert(1, str(project_dir.parents[1] / "harnesslab"))
