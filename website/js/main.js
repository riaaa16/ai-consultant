import { loadJson } from "./utils.js";
import { renderBio, renderServices, renderProjects, renderContact } from "./render.js";

const CONTENT_BASE = "./content";

async function main() {
  document.getElementById("year").textContent = String(new Date().getFullYear());

  const site = await loadJson(`${CONTENT_BASE}/site.json`);

  const bio = site?.bio ?? {};
  renderBio(bio);
  renderServices(site?.services ?? {});
  renderProjects(site?.projects ?? {});
  renderContact(site?.contact ?? {}, bio);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error("Failed to load site content", err);
});
