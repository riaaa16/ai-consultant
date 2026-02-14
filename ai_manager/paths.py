from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    # ai_manager/paths.py -> repo root
    return Path(__file__).resolve().parents[1]


def website_root() -> Path:
    return repo_root() / "website"


def content_root() -> Path:
    return website_root() / "content"


def backups_root() -> Path:
    return content_root() / ".backups"
