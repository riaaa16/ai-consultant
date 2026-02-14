from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# `mcp dev` imports this file by path (no package context), so we must ensure the
# repo root is on sys.path before importing `ai_manager.*`.
_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from ai_manager.content_updater import ContentUpdateError, apply_update, restore_backup
from ai_manager.git_ops import GitError, stage_commit_push
from ai_manager.paths import repo_root


mcp = FastMCP("ai-consultant")


def _unwrap_inspector_args(arg: dict[str, Any]) -> dict[str, Any]:
    """The MCP Inspector sends arguments shaped like {"payload": {...}}.

    Our update/rollback tools conceptually accept the inner payload object.
    This helper makes both shapes work:
      - {"file": ..., "operation": ..., "content": ...}
      - {"payload": {"file": ..., "operation": ..., "content": ...}}
    """

    if not isinstance(arg, dict):
        return arg

    if "payload" in arg and "file" not in arg and len(arg.keys()) == 1:
        inner = arg.get("payload")
        if isinstance(inner, dict):
            return inner

    return arg


@mcp.tool()
def update_website_content(payload: dict[str, Any]) -> dict[str, Any]:
    """Safely update website content JSON.

    Payload format:
      {
                "file": "site.json",
        "operation": "replace" | "append" | "delete",
        "content": { ... }
      }

    Safety:
      - Only edits within website/content
      - Validates JSON schema before writing
      - Creates a backup before changes

    Git automation (optional):
      Set env AUTO_GIT_PUSH=1 to automatically git add/commit/push the changed file.
      Commit message uses AI update prefix.
    """

    try:
        result = apply_update(_unwrap_inspector_args(payload))
    except ContentUpdateError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {e}"}

    if os.getenv("AUTO_GIT_PUSH", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        try:
            rel_path = f"website/content/{result['file']}"
            git_result = stage_commit_push(
                repo_root=str(repo_root()),
                paths=[rel_path],
                message=f"AI update: {result['file']} ({result['operation']})",
            )
            result["git"] = git_result
        except GitError as e:
            result["git"] = {"status": "error", "error": str(e)}

    return result


@mcp.tool()
def rollback_website_content(payload: dict[str, Any]) -> dict[str, Any]:
    """Rollback a website content JSON file to a previous backup.

    Payload format:
      {
                "file": "site.json",
        "backup": "<backup filename>" (optional; restores latest if omitted)
      }

    Safety:
      - Only reads from website/content/.backups
      - Validates JSON schema before writing
      - Creates a backup of current content before restoring

    Git automation (optional):
      Set env AUTO_GIT_PUSH=1 to automatically git add/commit/push the restored file.
    """

    payload = _unwrap_inspector_args(payload)

    if not isinstance(payload, dict):
        return {"status": "error", "error": "Payload must be an object"}

    file_name = payload.get("file")
    backup = payload.get("backup")

    if file_name != "site.json":
        return {"status": "error", "error": "Invalid or unsupported file"}
    if backup is not None and not isinstance(backup, str):
        return {"status": "error", "error": "backup must be a string"}

    try:
        result = restore_backup(file_name=file_name, backup=backup)
    except ContentUpdateError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {e}"}

    if os.getenv("AUTO_GIT_PUSH", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        try:
            rel_path = f"website/content/{result['file']}"
            git_result = stage_commit_push(
                repo_root=str(repo_root()),
                paths=[rel_path],
                message=f"AI rollback: {result['file']}",
            )
            result["git"] = git_result
        except GitError as e:
            result["git"] = {"status": "error", "error": str(e)}

    return result


def main() -> None:
    # IMPORTANT: don't print to stdout in stdio mode.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
