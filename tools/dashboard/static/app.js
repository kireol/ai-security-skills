"use strict";

// Everything shown here was written by an agent from data on scanned systems, so it is untrusted.
// Render it only through textContent (the el() helper); never use innerHTML.

const POLL_MS = 4000;
const MODES = ["discover", "recommend", "remediate", "respond"];
const CLOSED = new Set(["resolved", "accepted_risk"]);
let selected = null;
let showClosed = false;
let lastState = null;
let tab = "overview";       // for runs: "overview" or "kickoff"
let kickoffDirty = false;   // unsaved edits in the kick-off form; don't re-render over them
let kickoffMessage = null;  // {text, ok} after saving

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "class") node.className = value;
    else if (key === "onclick") node.addEventListener("click", value);
    else if (key === "onsubmit") node.addEventListener("submit", value);
    else if (key === "oninput") node.addEventListener("input", value);
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
  if (id !== selected) {
    tab = "overview";
    kickoffDirty = false;
    kickoffMessage = null;
  }
  selected = id;
  render(lastState);
}

// Redraw now, even if focus is in the kick-off form (render() skips the form while someone is typing).
function redraw() {
  if (document.activeElement) document.activeElement.blur();
  render(lastState);
}

const isRun = (a) => a.skill === "full-assessment" && !a.parent;
const kickoffAnswered = (a) => Boolean(a.kickoff.discovery_level);

function tabs(a) {
  const button = (name, text) => el("button", {
    class: `tab${tab === name ? " current" : ""}`,
    onclick: () => { tab = name; kickoffDirty = false; kickoffMessage = null; render(lastState); },
  }, text);
  return el("div", { class: "tabs", role: "tablist" }, button("overview", "Overview"),
    button("kickoff", kickoffAnswered(a) ? "Kick-off settings" : "Kick-off settings (needs answers)"));
}

function answeredBy(answer) {
  if (!answer) return "Not answered yet";
  const where = answer.source === "dashboard" ? "Set in the dashboard" : "Answered in the chat";
  return `${where}, ${when(answer.time)}`;
}

const ACCESS = { local: "This computer only", lan: "Devices on your local network (LAN)" };

function kickoffForm(a) {
  const fields = lastState.kickoff_fields || [];
  const locked = a.completed;
  const rows = fields.map((f) => {
    const answer = a.kickoff[f.key];
    const current = answer ? answer.value : "";
    if (f.key === "dashboard") {
      // How this dashboard is reachable is set when it starts, so show it rather than offer to change it.
      return el("div", { class: "field" }, el("label", {}, f.question),
        el("div", {}, `Running now: ${ACCESS[lastState.dashboard_access] || "unknown"}`),
        el("div", { class: "small muted" }, answer ? `Kick-off answer: ${(f.choices.find(([v]) => v === answer.value) || [, answer.value])[1]}. ` : "",
          "To change who can view it, stop the dashboard (scripts/assess.sh --stop) and start it again."));
    }
    const mark = () => { kickoffDirty = true; kickoffMessage = null; };
    let input;
    if (f.choices) {
      input = el("select", { name: f.key, oninput: mark },
        el("option", { value: "" }, "— not answered —"),
        f.choices.map(([value, text]) => el("option", { value }, text)));
      input.value = current;
    } else {
      const long = ["known_systems", "access_available", "in_scope", "out_of_scope", "fragile_devices"].includes(f.key);
      input = el(long ? "textarea" : "input", { name: f.key, placeholder: f.hint || "", oninput: mark,
        ...(long ? { rows: "2" } : { type: "text" }) });
      input.value = current;
    }
    return el("div", { class: "field" }, el("label", { for: `kickoff-${f.key}` }, f.question),
      Object.assign(input, { id: `kickoff-${f.key}` }),
      el("div", { class: "small muted" }, answeredBy(answer)));
  });

  async function save(e) {
    e.preventDefault();
    const answers = {};
    for (const f of fields) {
      const input = e.target.elements[f.key];
      if (!input) continue;
      const before = a.kickoff[f.key] ? a.kickoff[f.key].value : "";
      const value = input.value.trim();
      if (value !== before && value !== "") answers[f.key] = value;
    }
    if (Object.keys(answers).length === 0) {
      kickoffMessage = { text: "Nothing changed.", ok: true };
      kickoffDirty = false;
      return redraw();
    }
    try {
      const response = await fetch("/api/kickoff", {
        method: "POST", cache: "no-store",
        headers: { Authorization: `Bearer ${token()}`, "Content-Type": "application/json" },
        body: JSON.stringify({ assessment_id: a.id, answers }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
      kickoffDirty = false;
      kickoffMessage = { text: "Saved. Tell the agent you've answered in the dashboard; it also re-reads these "
        + "answers at every checkpoint, and confirms them with you before it starts.", ok: true };
      if (document.activeElement) document.activeElement.blur();
      refresh();
    } catch (err) {
      // Keep what was typed: show the error in place instead of redrawing the form.
      const message = document.getElementById("kickoff-message");
      message.textContent = `Not saved: ${err.message}`;
      message.className = "error";
    }
  }

  return el("form", { id: "kickoff-form", class: "kickoff", onsubmit: save },
    el("p", { class: "muted" }, locked
      ? "This run is complete. These are the kick-off answers it used."
      : "Answer here or in the chat with your AI assistant; both end up in the same place. The newest answer "
        + "to each question wins. Leaving a field blank keeps the existing answer."),
    el("fieldset", locked ? { disabled: "" } : {}, rows,
      locked ? null : el("div", { class: "actions" }, el("button", { type: "submit" }, "Save answers"),
        kickoffDirty ? el("button", { type: "button", class: "link",
          onclick: () => { kickoffDirty = false; kickoffMessage = null; redraw(); } }, "Discard changes") : null)),
    el("p", { id: "kickoff-message", class: kickoffMessage && !kickoffMessage.ok ? "error" : "saved" },
      kickoffMessage ? kickoffMessage.text : ""));
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
  const header = [
    el("h2", {}, a.skill || a.id, a.skill_version ? el("span", { class: "muted" }, ` v${a.skill_version}`) : null),
    el("p", { class: "muted" }, [a.target, a.scope, a.agent && `agent: ${a.agent}`, `started ${when(a.started)}`]
      .filter(Boolean).join(" · ")),
    isRun(a) ? tabs(a) : null,
  ];
  if (isRun(a) && tab === "kickoff") {
    detail.replaceChildren(...[...header, a.completed ? null : statusLine(a, false), kickoffForm(a)].filter(Boolean));
    return;
  }

  // replaceChildren() would print null/false as text, so drop empty optional sections first.
  detail.replaceChildren(...[
    ...header,
    a.incident && a.incident.status !== "closed" ? el("div", { class: "incident" },
      el("strong", {}, `Incident: ${label(a.incident.status)}`), a.incident.summary ? ` ${a.incident.summary}` : "",
      a.incident.containment ? el("ul", {}, a.incident.containment.map((c) => el("li", {}, c))) : null) : null,
    a.completed ? null : statusLine(a, false),
    isRun(a) && !a.completed && !kickoffAnswered(a) ? el("div", { class: "kickoff-needed" },
      "The kick-off questions haven't been answered yet. ",
      el("button", { class: "link", onclick: () => { tab = "kickoff"; render(lastState); } }, "Answer them here →"),
      " or in the chat.") : null,
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
  // Don't redraw the kick-off form under someone who is typing in it.
  const form = document.getElementById("kickoff-form");
  if (form && (kickoffDirty || form.contains(document.activeElement))) return;
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

let pollTimer = null;

function refresh() {
  clearTimeout(pollTimer);
  poll();
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
  pollTimer = setTimeout(poll, POLL_MS);
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
      refresh();
    }
  });
  poll();
});
