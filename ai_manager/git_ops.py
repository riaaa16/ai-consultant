from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Iterable

import requests


class GitError(RuntimeError):
    pass


def _run(repo_root: str, args: list[str]) -> str:
    try:
        proc = subprocess.run(
            args,
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise GitError((e.stderr or e.stdout or str(e)).strip()) from e

    return (proc.stdout or "").strip()


def stage_commit_push(*, repo_root: str, paths: Iterable[str], message: str) -> dict:
    paths = list(paths)
    if not paths:
        raise GitError("No paths provided to stage")

    _run(repo_root, ["git", "add", "--"] + paths)

    status = _run(repo_root, ["git", "status", "--porcelain"]) 
    if not status:
        return {"status": "noop", "detail": "No changes to commit"}

    _run(repo_root, ["git", "commit", "-m", message])
    _run(repo_root, ["git", "push"])

    deployment = confirm_pages_deploy()

    return {"status": "pushed", "deployment": deployment}


def confirm_pages_deploy() -> dict:
    """Best-effort confirmation of GitHub Pages deployment.

    Requires env:
      - GITHUB_TOKEN
      - GITHUB_REPO ("owner/repo")

    Returns a dict with status information; never raises unless requests itself fails unexpectedly.
    """

    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPO", "").strip()
    if not token or not repo or "/" not in repo:
        return {
            "status": "unknown",
            "detail": "Set GITHUB_TOKEN and GITHUB_REPO to check Pages build status",
        }

    owner, name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{name}/pages/builds/latest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        return {"status": "unknown", "detail": str(e)}

    if res.status_code == 200:
        data = res.json()
        return {
            "status": data.get("status") or "unknown",
            "updated_at": data.get("updated_at"),
            "url": data.get("url"),
        }

    return {"status": "unknown", "detail": f"HTTP {res.status_code}: {res.text[:200]}"}
