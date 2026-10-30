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

function counts(a) {
  return el("span", { class: "counts" },
    Object.entries(a.open_counts).filter(([, n]) => n > 0)
      .map(([p, n]) => el("span", { class: `badge priority-${p}` }, `${p} ${n}`)));
}

function renderList(state) {
  const nav = document.getElementById("assessments");
  nav.replaceChildren(el("h2", {}, "Assessments"));
  if (state.assessments.length === 0) {
    nav.append(el("p", { class: "muted" }, "No events yet. Agents write to the events folder or POST to /api/events."));
  }
  for (const a of state.assessments) {
    nav.append(el("button", {
      class: `assessment${a.id === selected ? " selected" : ""}`,
      onclick: () => { selected = a.id; render(lastState); },
    },
    el("span", { class: "row" }, el("strong", {}, a.skill || a.id), a.incident && a.incident.status !== "closed"
      ? badge("incident", a.incident.status) : null),
    el("span", { class: "row muted" }, a.target || "unknown target"),
    el("span", { class: "row" }, a.completed ? badge("mode", "completed") : badge("mode", a.mode), counts(a)),
    el("span", { class: "row muted small" }, `updated ${when(a.updated)}`)));
  }
  if (state.rejected.length) {
    nav.append(el("details", { class: "rejected" },
      el("summary", {}, `${state.rejected.length} rejected event(s)`),
      el("ul", {}, state.rejected.map((r) => el("li", {}, `${r.file}:${r.line}: ${r.reason}`)))));
  }
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

  detail.replaceChildren(
    el("h2", {}, a.skill || a.id, a.skill_version ? el("span", { class: "muted" }, ` v${a.skill_version}`) : null),
    el("p", { class: "muted" }, [a.target, a.scope, a.agent && `agent: ${a.agent}`, `started ${when(a.started)}`]
      .filter(Boolean).join(" · ")),
    a.incident && a.incident.status !== "closed" ? el("div", { class: "incident" },
      el("strong", {}, `Incident: ${label(a.incident.status)}`), a.incident.summary ? ` ${a.incident.summary}` : "",
      a.incident.containment ? el("ul", {}, a.incident.containment.map((c) => el("li", {}, c))) : null) : null,
    a.completed ? el("div", { class: "completed" }, el("strong", {}, "Completed. "), a.summary || "") : modeStrip(a),

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
  );
}

function render(state) {
  if (!state) return;
  if (!state.assessments.some((a) => a.id === selected)) selected = state.assessments[0]?.id ?? null;
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
