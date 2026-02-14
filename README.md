# AI Consultant: Static Site + Local AI Manager

This repo contains:

- `website/`: a fully static portfolio site (GitHub Pages compatible)
- `ai_manager/`: a local Python app + MCP stdio server that can safely update `website/content/site.json`

For run instructions (local preview, CLI, MCP, rollback), see [RUNNING.md](RUNNING.md).

## Website

Single source of truth content lives in `website/content/site.json`.

The site renders content at runtime via `website/js/main.js`.

The top navbar is the primary section navigation. The left sidebar contains only the sticky contact card (Email / LinkedIn / GitHub).

### GitHub Pages deployment

This repo includes a GitHub Actions workflow that deploys the `website/` folder to GitHub Pages.

In your GitHub repo settings:

- Settings → Pages → **Build and deployment** → Source: **GitHub Actions**

After that, any push that changes `website/**` will redeploy automatically.

### Fillout contact form

Put your Fillout embed code snippet into `website/content/site.json` under `contact.filloutEmbedCode`.

Note: the sidebar “Email” button scrolls to the on-page contact form (it does not open a mail client).

### Updating content (no extra tools)

For the proof-of-concept and for beginner-friendly setup, you can update the site by editing `website/content/site.json` and pushing to GitHub. GitHub Pages will redeploy via GitHub Actions.

## Local AI manager

The local manager is optional. It can update `website/content/site.json` from natural language and can also auto-commit/push.

See [RUNNING.md](RUNNING.md) for installation and usage.
