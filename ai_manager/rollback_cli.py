from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from .content_updater import ContentUpdateError, list_backups, restore_backup
from .git_ops import GitError, stage_commit_push
from .paths import repo_root


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Rollback website content from backups")
    parser.add_argument(
        "--file",
        required=True,
        choices=["site.json"],
        help="Target content file to restore",
    )
    parser.add_argument(
        "--backup",
        default=None,
        help="Backup filename to restore (default: latest)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups for --file and exit",
    )
    parser.add_argument("--git", action="store_true", help="git add/commit/push after restore")
    args = parser.parse_args(argv)

    try:
        if args.list:
            backups = list_backups(args.file)
            print(json.dumps({"file": args.file, "backups": backups}, indent=2), file=sys.stderr)
            return 0

        result = restore_backup(file_name=args.file, backup=args.backup)
        print(json.dumps(result, indent=2), file=sys.stderr)

        if args.git and result.get("status") == "ok":
            rel_path = f"website/content/{result['file']}"
            git_result = stage_commit_push(
                repo_root=str(repo_root()),
                paths=[rel_path],
                message=f"AI rollback: {result['file']}",
            )
            print(json.dumps({"git": git_result}, indent=2), file=sys.stderr)

        return 0

    except (ContentUpdateError, GitError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
