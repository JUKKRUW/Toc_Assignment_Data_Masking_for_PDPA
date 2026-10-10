// HTTP client for the backend. Contract: docs/API.md.  Owner: M08 (keep in sync with app.py)
// Frontend code must call the backend ONLY through these functions.
const json = async (res) => {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
};

/** @returns {Promise<{parts: Array, masked: string, stats: object}>} */
export const mask = (text, enabled) =>
  fetch("/api/mask", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({text, enabled})}).then(json);

/** @returns {Promise<{text: string, name: string}>} */
export const upload = (file) => {
  const fd = new FormData(); fd.append("file", file);
  return fetch("/api/upload", {method: "POST", body: fd}).then(json);
};

/** @returns {Promise<{text: string}>} */
export const generate = (n = 25) => fetch(`/api/generate?n=${n}`).then(json);

/** @returns {Promise<Array>} */
export const rules = () => fetch("/api/rules").then(json);

/** @returns {Promise<Array>} */
export const tests = () => fetch("/api/tests").then(json);
