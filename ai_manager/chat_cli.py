from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from .content_updater import ContentUpdateError, apply_update
from .git_ops import GitError, stage_commit_push
from .ollama_client import OllamaError, chat, extract_json_object
from .paths import repo_root


TOOL_SPEC = {
    "file": "site.json",
    "operation": "replace | append | delete",
    "content": "object"
}


def _build_prompt(user_instruction: str) -> str:
    return (
        "Convert the instruction into a website content update payload.\n"
        "Return ONLY JSON.\n\n"
        "Payload schema:\n"
        "{\n"
        "  \"file\": \"site.json\",\n"
        "  \"operation\": \"replace\" | \"append\" | \"delete\",\n"
        "  \"content\": { ... }\n"
        "}\n\n"
        "Operation notes:\n"
        "- replace: content is the full new JSON for site.json (keys: bio, services, projects, contact)\n"
        "- append/delete: use content with shape {\"section\": <bio|services|projects|contact>, \"data\": {...}}\n"
        "  - bio append: data may include summary/highlights arrays and/or name/title/location strings\n"
        "  - services/projects append: data may include intro string and must include services/projects array\n"
        "  - services/projects delete: data must include name (string) or names (string[])\n"
        "  - bio delete: data may include summary/highlights string[] to remove exact matches\n"
        "  - contact append: data is partial merge of string fields (email/linkedin/github/filloutEmbedUrl)\n"
        "  - contact delete: data keys are cleared to empty strings\n\n"
        f"Instruction: {user_instruction}\n"
    )


def _build_repair_prompt(*, user_instruction: str, bad_output: str) -> str:
    return (
        "You returned invalid JSON previously. Repair it.\n"
        "Return ONLY a single valid JSON object. No markdown, no prose.\n\n"
        "The JSON MUST match this payload schema exactly:\n"
        "{\n"
        "  \"file\": \"site.json\",\n"
        "  \"operation\": \"replace\" | \"append\" | \"delete\",\n"
        "  \"content\": { ... }\n"
        "}\n\n"
        "Reminder:\n"
        "- replace: content is the full new JSON for site.json (keys: bio, services, projects, contact)\n"
        "- append/delete: content has shape {\"section\": <bio|services|projects|contact>, \"data\": {...}}\n\n"
        f"Original instruction: {user_instruction}\n\n"
        "Bad output to repair (verbatim):\n"
        f"{bad_output}\n"
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Local AI website content manager")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1"))
    parser.add_argument("--host", default=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    parser.add_argument("--git", action="store_true", help="git add/commit/push content changes")
    parser.add_argument("--no-llm", action="store_true", help="paste payload JSON manually")
    args = parser.parse_args(argv)

    print("AI website manager (local). Type 'exit' to quit.", file=sys.stderr)

    while True:
        try:
            user = input("> ").strip()
        except EOFError:
            break

        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            break

        try:
            if args.no_llm:
                payload = json.loads(user)
            else:
                prompt = _build_prompt(user)
                raw = chat(prompt=prompt, model=args.model, host=args.host)
                try:
                    payload = extract_json_object(raw)
                except OllamaError:
                    print("Model output wasn't valid JSON; retrying once...", file=sys.stderr)
                    repair = _build_repair_prompt(user_instruction=user, bad_output=raw)
                    raw2 = chat(prompt=repair, model=args.model, host=args.host)
                    payload = extract_json_object(raw2)

            result = apply_update(payload)
            print(json.dumps(result, indent=2), file=sys.stderr)

            if args.git and result.get("status") == "ok":
                rel_path = f"website/content/{result['file']}"
                git_result = stage_commit_push(
                    repo_root=str(repo_root()),
                    paths=[rel_path],
                    message=f"AI update: {result['file']} ({result['operation']})",
                )
                print(json.dumps({"git": git_result}, indent=2), file=sys.stderr)

        except (ContentUpdateError, OllamaError, GitError, json.JSONDecodeError) as e:
            msg = str(e)
            print(f"Error: {msg}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
