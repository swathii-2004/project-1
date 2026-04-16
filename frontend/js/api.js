// ── Config ────────────────────────────────────────────────────
const API_BASE = "http://127.0.0.1:8000";

// ── API helpers ───────────────────────────────────────────────
const api = {
  async get(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
  },
  async post(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
  },
  async put(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
  },
  async delete(path) {
    const res = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
  },
};

// ── Toast ─────────────────────────────────────────────────────
function showToast(msg, type = "success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `show ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => (t.className = ""), 3000);
}

// ── Query param helper ────────────────────────────────────────
function getParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}