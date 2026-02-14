# Running & Updating

This repo is designed to work in two ways:

1) **Beginner mode (no extra tooling):** edit content in `website/content/site.json`, push to GitHub, and GitHub Pages redeploys.
2) **Local AI manager mode:** run the Python tools to update `site.json` via chat/MCP, optionally auto-commit + push.

## Website (local preview)

From the repo root:

- `venv/Scripts/python.exe -m http.server 8000 --directory website`

Then open:

- `http://localhost:8000`

If the page doesn’t reflect recent changes, do a hard refresh (`Ctrl+F5`).

## Update content (no extra tools)

- Edit `website/content/site.json`
- Commit + push
- GitHub Pages will redeploy (when Pages is set to **GitHub Actions**)

### Fillout embed

Fillout provides an embed snippet (often a `<div ...></div><script ...></script>` pair). Put that snippet in:

- `website/content/site.json` → `contact.filloutEmbedCode`

UX note: the sidebar “Email” button scrolls to the on-page Contact section (Fillout form) instead of using `mailto:`.

## Local AI manager

### Prereqs

- Python 3.10+
- (Optional) Ollama running locally
- Git configured for pushing to your GitHub repo

### Install

Using a venv (Windows):

- `python -m venv venv`
- `venv/Scripts/python.exe -m pip install -r requirements.txt`

Copy env template:

- `copy .env.example .env`

### Run chat CLI

Uses Ollama by default if it’s running:

- `venv/Scripts/python.exe -m ai_manager.chat_cli`

Also commit + push after each successful update:

- `venv/Scripts/python.exe -m ai_manager.chat_cli --git`

Manual payload mode (no LLM):

- `venv/Scripts/python.exe -m ai_manager.chat_cli --no-llm`

### Run MCP server (stdio)

- `venv/Scripts/python.exe -u -m ai_manager.mcp_server`

### Test MCP tools with the MCP Inspector (recommended)

This launches your MCP server and opens the Inspector UI so you can click-run tool calls.

The Inspector uses `uv` under the hood to manage running the server. If you get `uv is not recognized`, install it into your venv:

- `venv/Scripts/python.exe -m pip install uv`

**PowerShell / CMD (Windows):**

- (Recommended) activate the venv so `uv` is on PATH:
  - PowerShell: `venv\Scripts\Activate.ps1`
  - CMD: `venv\Scripts\activate.bat`

- `venv\Scripts\mcp.exe dev ai_manager\mcp_server.py:mcp`

**Git Bash (MINGW64):**

- Run this exact command (no backslashes):

```sh
source venv/Scripts/activate
./venv/Scripts/mcp.exe dev ai_manager/mcp_server.py:mcp
```

Why this matters: in Git Bash, `\` can be treated as an escape, so `venv\Scripts\mcp.exe` may turn into `venvScriptsmcp.exe` and fail.

If you see something like `.[mcp.exe](http://_vscodecontentref_/...)` in your terminal, you pasted a VS Code markdown link by accident — delete it and paste/type the raw command above.

Tools provided:

- `update_website_content(payload)`
- `rollback_website_content(payload)`

#### Example payloads

Append a bio highlight:

```json
{
  "file": "site.json",
  "operation": "append",
  "content": {
    "section": "bio",
    "data": {"highlights": ["Specialize in RAG systems"]}
  }
}
```

Delete a project by name:

```json
{
  "file": "site.json",
  "operation": "delete",
  "content": {
    "section": "projects",
    "data": {"name": "Ops Automation Agent"}
  }
}
```

Rollback to a specific backup:

```json
{
  "file": "site.json",
  "backup": "site.json.20260213T120102Z.bak"
}
```

### Rollback CLI

List backups:

- `venv/Scripts/python.exe -m ai_manager.rollback_cli --file site.json --list`

Restore latest backup:

- `venv/Scripts/python.exe -m ai_manager.rollback_cli --file site.json`

Restore a specific backup:

- `venv/Scripts/python.exe -m ai_manager.rollback_cli --file site.json --backup site.json.20260213T120102Z.bak`

## Optional: GitHub Pages deploy status check

If you set:

- `GITHUB_TOKEN`
- `GITHUB_REPO=owner/repo`

Then after `git push`, the manager will attempt to query the latest Pages build via GitHub API.
