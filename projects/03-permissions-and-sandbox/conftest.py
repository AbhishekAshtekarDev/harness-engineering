import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from project_conftest import use  # noqa: E402

use(Path(__file__).resolve().parent)
