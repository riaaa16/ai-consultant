from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from jsonschema import validate

from .paths import backups_root, content_root
from .schema_loader import load_schema


AllowedFile = Literal["site.json"]
Section = Literal["bio", "services", "projects", "contact"]
Operation = Literal["replace", "append", "delete"]


@dataclass(frozen=True)
class UpdatePayload:
    file: AllowedFile
    operation: Operation
    content: dict[str, Any]


class ContentUpdateError(RuntimeError):
    pass


def list_backups(file_name: AllowedFile) -> list[str]:
    """Return backup filenames (newest first) for a given content file."""

    root = backups_root()
    if not root.exists():
        return []
    backups = sorted(root.glob(f"{file_name}.*.bak"), reverse=True)
    return [b.name for b in backups]


def restore_backup(*, file_name: AllowedFile, backup: str | None = None) -> dict[str, Any]:
    """Restore a previous version of a content file from .backups.

    Args:
      file_name: the content file to restore.
      backup: optional backup filename (not a path). If omitted, restores the latest.

    Safety:
      - Only reads from website/content/.backups
      - Validates restored JSON against the file schema
      - Creates a backup of the current file before restoring
    """

    path = _allowed_path(file_name)
    if not path.exists():
        raise ContentUpdateError(f"Content file does not exist: {file_name}")

    available = list_backups(file_name)
    if not available:
        raise ContentUpdateError(f"No backups found for {file_name}")

    if backup is None:
        chosen = available[0]
    else:
        # Only allow backup file names, not arbitrary paths.
        if Path(backup).name != backup:
            raise ContentUpdateError("backup must be a filename, not a path")
        if not (backup.startswith(f"{file_name}.") and backup.endswith(".bak")):
            raise ContentUpdateError("backup filename does not match target file")
        if backup not in set(available):
            raise ContentUpdateError("backup not found")
        chosen = backup

    backup_path = (backups_root() / chosen).resolve()
    # Ensure resolved path still sits inside backups_root.
    root = backups_root().resolve()
    if backup_path != root and root not in backup_path.parents:
        raise ContentUpdateError("Refusing to access outside backups directory")

    restored = _read_json(backup_path)
    _validate(file_name, restored)

    current_backup = _backup_file(path)
    _write_json(path, restored)

    return {
        "status": "ok",
        "file": file_name,
        "restored_from": str(backup_path),
        "backup_of_current": str(current_backup),
    }


def _allowed_path(file_name: AllowedFile) -> Path:
    target = (content_root() / file_name).resolve()
    root = content_root().resolve()
    if target != root and root not in target.parents:
        raise ContentUpdateError("Refusing to access outside content directory")
    return target


def _schema_for(file_name: AllowedFile) -> dict:
    if file_name != "site.json":
        raise ContentUpdateError("Invalid or unsupported file")
    return load_schema("site.schema.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def _backup_file(path: Path) -> Path:
    backups_root().mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = backups_root() / f"{path.name}.{stamp}.bak"
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    return backup


def _validate(file_name: AllowedFile, data: dict[str, Any]) -> None:
    schema = _schema_for(file_name)
    validate(instance=data, schema=schema)


def _coerce_payload(payload: dict[str, Any]) -> UpdatePayload:
    if not isinstance(payload, dict):
        raise ContentUpdateError("Payload must be an object")

    allowed_keys = {"file", "operation", "content"}
    extra = set(payload.keys()) - allowed_keys
    if extra:
        raise ContentUpdateError(f"Unexpected payload keys: {sorted(extra)}")

    file_name = payload.get("file")
    operation = payload.get("operation")
    content = payload.get("content")

    if file_name != "site.json":
        raise ContentUpdateError("Invalid or unsupported file")
    if operation not in {"replace", "append", "delete"}:
        raise ContentUpdateError("Invalid operation")
    if not isinstance(content, dict):
        raise ContentUpdateError("content must be an object")

    return UpdatePayload(file=file_name, operation=operation, content=content)


def apply_update(payload: dict[str, Any]) -> dict[str, Any]:
    """Apply an update to a JSON content file under website/content.

    Expected payload shape:
      {
                "file": "site.json",
        "operation": "replace" | "append" | "delete",
        "content": { ... }
      }

    Returns a dict with details about what changed.
    """

    p = _coerce_payload(payload)
    path = _allowed_path(p.file)

    if not path.exists():
        raise ContentUpdateError(f"Content file does not exist: {p.file}")

    current = _read_json(path)
    _validate(p.file, current)

    updated = _apply_operation(file_name=p.file, operation=p.operation, current=current, patch=p.content)
    _validate(p.file, updated)

    backup = _backup_file(path)
    _write_json(path, updated)

    return {
        "status": "ok",
        "file": p.file,
        "operation": p.operation,
        "backup": str(backup),
    }


def _apply_operation(
    *,
    file_name: AllowedFile,
    operation: Operation,
    current: dict[str, Any],
    patch: dict[str, Any],
) -> dict[str, Any]:
    if operation == "replace":
        return patch

    if operation == "append":
        return _append(file_name=file_name, current=current, patch=patch)

    if operation == "delete":
        return _delete(file_name=file_name, current=current, patch=patch)

    raise ContentUpdateError("Unsupported operation")


def _append(*, file_name: AllowedFile, current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    if file_name != "site.json":
        raise ContentUpdateError("Invalid or unsupported file")

    updated = dict(current)
    section = patch.get("section")
    data = patch.get("data")
    if section not in {"bio", "services", "projects", "contact"}:
        raise ContentUpdateError("append requires 'section' (bio|services|projects|contact)")
    if not isinstance(data, dict):
        raise ContentUpdateError("append requires 'data' object")

    if section == "bio":
        bio = dict(updated.get("bio", {}))
        for key in ("summary", "highlights"):
            if key in data:
                if not isinstance(data[key], list):
                    raise ContentUpdateError(f"bio append requires '{key}' as array")
                bio[key] = list(bio.get(key, [])) + data[key]
        for key in ("name", "title", "location"):
            if key in data and isinstance(data[key], str):
                bio[key] = data[key]
        updated["bio"] = bio
        return updated

    if section in {"services", "projects"}:
        block = dict(updated.get(section, {}))
        array_key = "services" if section == "services" else "projects"

        if "intro" in data and isinstance(data["intro"], str):
            block["intro"] = data["intro"]

        if array_key not in data:
            raise ContentUpdateError(f"{section} append requires '{array_key}' array in data")
        if not isinstance(data[array_key], list):
            raise ContentUpdateError(f"'{array_key}' must be an array")

        block[array_key] = list(block.get(array_key, [])) + data[array_key]
        updated[section] = block
        return updated

    if section == "contact":
        contact = dict(updated.get("contact", {}))
        for key, value in data.items():
            if not isinstance(value, str):
                raise ContentUpdateError("contact fields must be strings")
            contact[key] = value
        updated["contact"] = contact
        return updated

    raise ContentUpdateError("append not supported")


def _delete(*, file_name: AllowedFile, current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    if file_name != "site.json":
        raise ContentUpdateError("Invalid or unsupported file")

    updated = dict(current)
    section = patch.get("section")
    data = patch.get("data")
    if section not in {"bio", "services", "projects", "contact"}:
        raise ContentUpdateError("delete requires 'section' (bio|services|projects|contact)")
    if not isinstance(data, dict):
        raise ContentUpdateError("delete requires 'data' object")

    if section in {"services", "projects"}:
        block = dict(updated.get(section, {}))
        array_key = "services" if section == "services" else "projects"

        names: list[str] = []
        if "name" in data and isinstance(data["name"], str):
            names = [data["name"]]
        elif "names" in data and isinstance(data["names"], list) and all(isinstance(n, str) for n in data["names"]):
            names = list(data["names"])
        else:
            raise ContentUpdateError("delete requires data.name (string) or data.names (string[])")

        items = list(block.get(array_key, []))
        block[array_key] = [item for item in items if not (isinstance(item, dict) and item.get("name") in set(names))]
        updated[section] = block
        return updated

    if section == "bio":
        bio = dict(updated.get("bio", {}))
        for key in ("summary", "highlights"):
            if key in data:
                if not isinstance(data[key], list) or not all(isinstance(s, str) for s in data[key]):
                    raise ContentUpdateError(f"bio delete requires data.{key} as string[]")
                existing = list(bio.get(key, []))
                bio[key] = [s for s in existing if s not in set(data[key])]
        updated["bio"] = bio
        return updated

    if section == "contact":
        contact = dict(updated.get("contact", {}))
        for key in data.keys():
            contact[key] = ""
        updated["contact"] = contact
        return updated

    raise ContentUpdateError("delete not supported")
