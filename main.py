"""Root launcher for the EDC16C39 command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path

# Keep ``python main.py ...`` working directly from a source checkout. Tests
# and package consumers import ``edc16c39.cli`` and do not depend on this path.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from edc16c39.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
