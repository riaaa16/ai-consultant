export async function loadJson(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} loading ${path}`);
  }
  return await res.json();
}

export function setText(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = value == null ? "" : String(value);
}

export function setLink(id, href, label) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!href) {
    el.textContent = "—";
    el.setAttribute("href", "#");
    el.setAttribute("aria-disabled", "true");
    return;
  }
  el.textContent = label ?? href;
  el.setAttribute("href", href);
  el.removeAttribute("aria-disabled");
}

export function setHref(id, href) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!href) {
    el.setAttribute("href", "#");
    el.setAttribute("aria-disabled", "true");
    return;
  }
  el.setAttribute("href", href);
  el.removeAttribute("aria-disabled");
}
