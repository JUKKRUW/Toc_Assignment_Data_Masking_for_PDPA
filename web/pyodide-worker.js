// Runs the real `pdpa_shield` Python package inside a Web Worker via Pyodide (static build only).
// A worker keeps Pyodide's globals away from the page and keeps the UI smooth while Python loads.
// Protocol:
//   page -> worker  {type: "init", pyodide: "<indexURL>/"}
//   worker -> page  {type: "progress", key, pct} ... {type: "ready"} | {type: "fatal", message}
//   page -> worker  {id, fn, args}      (fn is a *_json function in pdpa_shield/service.py)
//   worker -> page  {id, result} | {id, error}
let S = null;
let booting = null;

async function boot(indexURL) {
  const progress = (key, pct) => self.postMessage({type: "progress", key, pct});
  progress("boot.load", 10);
  const {loadPyodide} = await import(indexURL + "pyodide.mjs");
  const py = await loadPyodide({indexURL});
  progress("boot.files", 70);
  const files = await (await fetch("py/manifest.json")).json();
  const texts = await Promise.all(files.map((f) => fetch("py/" + f).then((r) => r.text())));
  files.forEach((f, i) => {
    py.FS.mkdirTree("/home/pyodide/" + f.split("/").slice(0, -1).join("/"));
    py.FS.writeFile("/home/pyodide/" + f, texts[i]);
  });
  progress("boot.init", 90);
  py.runPython("import sys\nsys.path.insert(0, '/home/pyodide')\nimport pdpa_shield.service as S");
  S = py.globals.get("S");
  S.rules_json(); // warm up: compiles every pattern once
  self.postMessage({type: "ready"});
}

self.onmessage = async (e) => {
  const m = e.data;
  if (m.type === "init") {
    booting = boot(m.pyodide).catch((err) => self.postMessage({type: "fatal", message: String(err.message || err)}));
    return;
  }
  try {
    await booting;
    self.postMessage({id: m.id, result: S[m.fn](...m.args)});
  } catch (err) {
    self.postMessage({id: m.id, error: String(err.message || err)});
  }
};
