from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=32)
def load_schema(schema_name: str) -> dict:
    base = Path(__file__).resolve().parent / "schemas"
    path = base / schema_name
    return json.loads(path.read_text(encoding="utf-8"))
