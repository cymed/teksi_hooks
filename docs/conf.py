from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_ROOT),
)


project = "teksi-hooks"
author = "TEKSI"
copyright = "2026, TEKSI"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]

templates_path = [
    "_templates",
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "alabaster"

autodoc_typehints = "description"
autodoc_member_order = "bysource"