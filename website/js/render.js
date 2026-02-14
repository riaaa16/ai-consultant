import { setHref, setText } from "./utils.js";

function clear(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

function el(tag, attrs = {}, text) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    node.setAttribute(k, String(v));
  }
  if (text != null) node.textContent = String(text);
  return node;
}

export function renderBio(bio) {
  setText("site-name", bio?.name ?? "AI Consulting");
  setText("bio-name", bio?.name ?? "Your Name");
  setText("bio-title", bio?.title ?? "AI Consultant");
  setText("bio-location", bio?.location ?? "");
  setText("footer-name", bio?.name ?? "AI Consulting");

  const summaryRoot = document.getElementById("bio-summary");
  if (summaryRoot) {
    clear(summaryRoot);
    const summary = Array.isArray(bio?.summary) ? bio.summary : [];
    for (const paragraph of summary) {
      summaryRoot.appendChild(el("p", { class: "muted" }, paragraph));
    }
  }

  const highlightsRoot = document.getElementById("bio-highlights");
  if (highlightsRoot) {
    clear(highlightsRoot);
    const highlights = Array.isArray(bio?.highlights) ? bio.highlights : [];
    for (const h of highlights) {
      highlightsRoot.appendChild(el("li", {}, h));
    }
  }
}

export function renderServices(services) {
  setText("services-intro", services?.intro ?? "");

  const root = document.getElementById("services-cards");
  if (!root) return;

  clear(root);
  const items = Array.isArray(services?.services) ? services.services : [];
  for (const item of items) {
    const card = el("article", { class: "card" });
    card.appendChild(el("h3", {}, item?.name ?? "Service"));
    if (item?.description) card.appendChild(el("p", { class: "muted" }, item.description));

    const bullets = Array.isArray(item?.bullets) ? item.bullets : [];
    if (bullets.length) {
      const ul = el("ul", { class: "muted" });
      for (const b of bullets) {
        ul.appendChild(el("li", {}, b));
      }
      card.appendChild(ul);
    }

    root.appendChild(card);
  }
}

export function renderProjects(projects) {
  setText("projects-intro", projects?.intro ?? "");

  const root = document.getElementById("projects-cards");
  if (!root) return;

  clear(root);
  const items = Array.isArray(projects?.projects) ? projects.projects : [];
  for (const p of items) {
    const card = el("article", { class: "card" });
    card.appendChild(el("h3", {}, p?.name ?? "Project"));

    const tech = Array.isArray(p?.tech) ? p.tech : [];
    if (tech.length) card.appendChild(el("div", { class: "meta" }, `Tech: ${tech.join(", ")}`));

    if (p?.description) card.appendChild(el("p", { class: "muted" }, p.description));

    const links = Array.isArray(p?.links) ? p.links : [];
    if (links.length) {
      const linkRow = el("div", { class: "muted" });
      for (const l of links) {
        const a = el(
          "a",
          { href: l?.url ?? "#", target: "_blank", rel: "noreferrer", style: "margin-right:12px" },
          l?.label ?? l?.url ?? "Link",
        );
        linkRow.appendChild(a);
      }
      card.appendChild(linkRow);
    }

    root.appendChild(card);
  }
}

export function renderContact(contact, bio) {
  // UX: sidebar email button should send users to the on-page contact form.
  setHref("contact-email", "#contact");
  setText("contact-email-text", contact?.email ?? "Contact form");

  setHref("contact-linkedin", contact?.linkedin ?? "");
  setText("contact-linkedin-text", "LinkedIn");

  setHref("contact-github", contact?.github ?? "");
  setText("contact-github-text", "GitHub");

  const embedCode = (contact?.filloutEmbedCode ?? "").trim();
  const embedUrl = (contact?.filloutEmbedUrl ?? "").trim();
  const iframe = document.getElementById("fillout-iframe");
  const embedRoot = document.getElementById("fillout-embed");
  const placeholder = document.getElementById("fillout-placeholder");

  function clear(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
  }

  function setEmbedHtml(container, html) {
    clear(container);
    const template = document.createElement("template");
    template.innerHTML = html;

    for (const node of Array.from(template.content.childNodes)) {
      if (node.nodeType === Node.ELEMENT_NODE && node.nodeName.toLowerCase() === "script") {
        const script = document.createElement("script");
        for (const attr of Array.from(node.attributes)) {
          script.setAttribute(attr.name, attr.value);
        }
        const text = node.textContent;
        if (text && text.trim()) script.text = text;
        container.appendChild(script);
      } else {
        container.appendChild(node.cloneNode(true));
      }
    }
  }

  if (iframe && placeholder && embedRoot) {
    if (embedCode) {
      setEmbedHtml(embedRoot, embedCode);
      embedRoot.classList.remove("hidden");
      iframe.classList.add("hidden");
      placeholder.classList.add("hidden");
    } else if (embedUrl) {
      iframe.src = embedUrl;
      iframe.classList.remove("hidden");
      embedRoot.classList.add("hidden");
      placeholder.classList.add("hidden");
    } else {
      iframe.classList.add("hidden");
      embedRoot.classList.add("hidden");
      placeholder.classList.remove("hidden");
    }
  }

  const name = bio?.name ?? "AI Consulting";
  const footerText = document.getElementById("footer-text");
  if (footerText) {
    footerText.setAttribute("aria-label", `Copyright ${name}`);
  }
}
