"use strict";

// Everything shown here was written by an agent from data on scanned systems, so it is untrusted.
// Render it only through textContent (the el() helper); never use innerHTML.

const POLL_MS = 4000;
const MODES = ["discover", "recommend", "remediate", "respond"];
const CLOSED = new Set(["resolved", "accepted_risk"]);
let selected = null;
let showClosed = false;
let lastState = null;

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "class") node.className = value;
    else if (key === "onclick") node.addEventListener("click", value);
    else node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

const label = (value) => (value ? String(value).replace(/_/g, " ") : "—");
const token = () => sessionStorage.getItem("aiss-token");

function when(iso) {
  if (!iso) return "—";
  const seconds = Math.round((Date.now() - Date.parse(iso)) / 1000);
  if (Number.isNaN(seconds)) return iso;
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} h ago`;
  return new Date(iso).toLocaleString();
}

function badge(kind, value) {
  return el("span", { class: `badge ${kind}-${value || "none"}` }, label(value));
}

function counts(a, which = "open_counts") {
  return el("span", { class: "counts" },
    Object.entries(a[which]).filter(([, n]) => n > 0)
      .map(([p, n]) => el("span", { class: `badge priority-${p}` }, `${p} ${n}`)));
}

function renderList(state) {
  const nav = document.getElementById("assessments");
  nav.replaceChildren(el("h2", {}, "Assessments"));
  if (state.assessments.length === 0) {
    nav.append(el("p", { class: "muted" }, "No assessments yet. The dashboard is watching:"),
      el("ul", { class: "small mono sources" }, (state.sources || []).map((s) => el("li", {}, s))),
      el("p", { class: "muted small" }, "If an assessment is running but nothing shows here, ask the agent for "
        + "the path of its run folder and whether it has written any events."));
  }
  const byId = new Map(state.assessments.map((a) => [a.id, a]));
  const item = (a, child) => el("button", {
    class: `assessment${child ? " child" : ""}${a.id === selected ? " selected" : ""}`,
    onclick: () => select(a.id),
  },
  el("span", { class: "row" }, el("strong", {}, a.children.length ? `Run: ${a.target || a.id}` : a.skill || a.id),
    a.incident && a.incident.status !== "closed" ? badge("incident", a.incident.status) : null),
  a.children.length ? null : el("span", { class: "row muted" }, a.target || "unknown target"),
  el("span", { class: "row" }, a.completed ? badge("mode", "completed") : badge("mode", a.mode),
    counts(a, a.children.length ? "rollup_counts" : "open_counts")),
  a.completed ? null : statusLine(a, true),
  el("span", { class: "row muted small" }, `updated ${when(a.updated)}`));
  for (const a of state.assessments.filter((x) => !x.parent)) {
    nav.append(item(a, false));
    for (const id of a.children) nav.append(item(byId.get(id), true));
  }
  if (state.rejected.length) {
    nav.append(el("details", { class: "rejected" },
      el("summary", {}, `${state.rejected.length} rejected event(s)`),
      el("ul", {}, state.rejected.map((r) => el("li", {}, `${r.file}:${r.line}: ${r.reason}`)))));
  }
}

const WAITING = { user: "Waiting for you", background_task: "Background task running" };

function statusLine(a, compact) {
  if (!a.status) return null;
  const waiting = WAITING[a.status.waiting_on];
  return el("div", { class: `status-line${compact ? " small" : ""}${a.status.waiting_on === "user" ? " waiting-user" : ""}` },
    waiting ? el("span", { class: `badge wait-${a.status.waiting_on}` }, waiting) : null,
    ` ${a.status.activity} `, el("span", { class: "muted small" }, `(${when(a.status.time)})`));
}

function select(id) {
  selected = id;
  render(lastState);
}

function inventory(a) {
  if (a.assets.length === 0) return null;
  const covered = a.assets.filter((x) => x.coverage === "assessed").length;
  return [
    el("h3", {}, `Inventory (${covered} of ${a.assets.length} assessed)`),
    table(["Asset", "Kind", "Exposure", "Services", "Skill", "Coverage"],
      a.assets.map((x) => el("tr", { title: x.note || "" },
        el("td", {}, x.label || x.id, x.addresses ? el("div", { class: "small muted mono" }, x.addresses.join(", ")) : null),
        el("td", {}, x.kind || "—"), el("td", {}, badge("exposure", x.exposure)),
        el("td", { class: "small" }, x.services ? x.services.join("; ") : "—"),
        el("td", { class: "mono" }, x.skill || "—"),
        el("td", {}, x.assessment_id && lastState.assessments.some((c) => c.id === x.assessment_id)
          ? el("button", { class: "link", onclick: () => select(x.assessment_id) }, badge("coverage", x.coverage), " open →")
          : badge("coverage", x.coverage)))),
      ""),
  ];
}

function modeStrip(a) {
  return el("ol", { class: "modes" }, MODES.map((m) => el("li", {
    class: m === a.mode ? "current" : a.modes_visited.includes(m) ? "past" : "",
  }, label(m))));
}

function table(headers, rows, empty) {
  if (rows.length === 0) return el("p", { class: "muted" }, empty);
  return el("table", {}, el("thead", {}, el("tr", {}, headers.map((h) => el("th", {}, h)))),
    el("tbody", {}, rows));
}

function renderDetail(a) {
  const detail = document.getElementById("detail");
  if (!a) {
    detail.replaceChildren(el("p", { class: "muted" }, "Select an assessment."));
    return;
  }
  const findings = a.findings.filter((f) => showClosed || !CLOSED.has(f.state));
  const hidden = a.findings.length - findings.length;

  // replaceChildren() would print null/false as text, so drop empty optional sections first.
  detail.replaceChildren(...[
    el("h2", {}, a.skill || a.id, a.skill_version ? el("span", { class: "muted" }, ` v${a.skill_version}`) : null),
    el("p", { class: "muted" }, [a.target, a.scope, a.agent && `agent: ${a.agent}`, `started ${when(a.started)}`]
      .filter(Boolean).join(" · ")),
    a.incident && a.incident.status !== "closed" ? el("div", { class: "incident" },
      el("strong", {}, `Incident: ${label(a.incident.status)}`), a.incident.summary ? ` ${a.incident.summary}` : "",
      a.incident.containment ? el("ul", {}, a.incident.containment.map((c) => el("li", {}, c))) : null) : null,
    a.completed ? null : statusLine(a, false),
    a.parent ? el("p", {}, el("button", { class: "link", onclick: () => select(a.parent) }, "← back to run")) : null,
    a.children.length ? el("p", {}, "Open findings across this run: ", counts(a, "rollup_counts")) : null,
    a.completed ? el("div", { class: "completed" }, el("strong", {}, "Completed. "), a.summary || "") : modeStrip(a),
    inventory(a),

    el("h3", {}, "Domains"),
    a.domains.length ? el("div", { class: "domains" }, a.domains.map((d) => el("div", {
      class: `domain status-${d.status}`, title: d.note || "",
    }, el("strong", {}, d.domain), ` ${d.title || ""}`, el("br"), el("span", { class: "small" }, label(d.status)))))
      : el("p", { class: "muted" }, "No domain status reported yet."),

    el("h3", {}, "Findings ",
      el("label", { class: "small muted toggle" },
        Object.assign(el("input", { type: "checkbox" }), {
          checked: showClosed, onchange: (e) => { showClosed = e.target.checked; render(lastState); },
        }), ` show resolved/accepted${hidden ? ` (${hidden})` : ""}`)),
    table(["ID", "Priority", "Title", "Component", "Confidence", "State", "Class", "Updated"],
      findings.map((f) => el("tr", { title: f.summary || "" },
        el("td", { class: "mono" }, f.id), el("td", {}, badge("priority", f.priority)), el("td", {}, f.title || "—"),
        el("td", {}, f.component || "—"), el("td", {}, label(f.confidence)), el("td", {}, badge("state", f.state)),
        el("td", { class: "mono" }, f.operation_class || "—"), el("td", { class: "small" }, when(f.updated)))),
      "No findings reported yet."),

    el("h3", {}, "Changes"),
    table(["Time", "Finding", "Change", "Class", "Result", "Approved by"],
      a.changes.map((c) => el("tr", {},
        el("td", { class: "small" }, when(c.time)), el("td", { class: "mono" }, c.finding_id || "—"),
        el("td", {}, c.description), el("td", { class: "mono" }, c.operation_class), el("td", {}, badge("result", c.result)),
        el("td", {}, c.approved_by || "—"))),
      "No changes recorded."),
  ].flat().filter(Boolean));
}

function render(state) {
  if (!state) return;
  if (!state.assessments.some((a) => a.id === selected)) {
    selected = (state.assessments.find((a) => !a.parent) || state.assessments[0])?.id ?? null;
  }
  renderList(state);
  renderDetail(state.assessments.find((a) => a.id === selected));
}

function setStatus(text, ok) {
  const status = document.getElementById("status");
  status.textContent = text;
  status.className = `status ${ok ? "ok" : "error"}`;
}

function showLogin(message) {
  document.getElementById("app").hidden = true;
  document.getElementById("login").hidden = false;
  setStatus(message, false);
}

async function poll() {
  if (!token()) return showLogin("token needed");
  try {
    const response = await fetch("/api/state", { headers: { Authorization: `Bearer ${token()}` }, cache: "no-store" });
    if (response.status === 401) {
      sessionStorage.removeItem("aiss-token");
      return showLogin("token rejected");
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    lastState = await response.json();
    document.getElementById("login").hidden = true;
    document.getElementById("app").hidden = false;
    render(lastState);
    setStatus(`live · ${new Date().toLocaleTimeString()}`, true);
  } catch (err) {
    setStatus(`disconnected (${err.message})`, false);
  }
  setTimeout(poll, POLL_MS);
}

document.addEventListener("DOMContentLoaded", () => {
  // The startup URL carries the token in the fragment, which browsers never send to the server.
  const match = location.hash.match(/token=([^&]+)/);
  if (match) {
    sessionStorage.setItem("aiss-token", decodeURIComponent(match[1]));
    history.replaceState(null, "", location.pathname);
  }
  document.getElementById("login-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const value = document.getElementById("token-input").value.trim();
    if (value) {
      sessionStorage.setItem("aiss-token", value);
      document.getElementById("token-input").value = "";
      poll();
    }
  });
  poll();
});
