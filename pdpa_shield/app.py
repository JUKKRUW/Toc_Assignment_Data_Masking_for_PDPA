"""Flask application.                                                Owner: M08

Run:  flask --app pdpa_shield.app run --debug      (or: python -m pdpa_shield.app)
The HTTP contract is specified in docs/API.md — the frontend (M09, M10) codes against it,
so do not change field names without updating the doc and telling them.
"""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from pdpa_shield import service
from pdpa_shield.engine import registry


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
    app.json.ensure_ascii = False
    app.config["MAX_CONTENT_LENGTH"] = service.MAX_UPLOAD

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "rules": registry.RULE_KEYS})

    @app.post("/api/mask")
    def api_mask():
        """Body {text, enabled?} -> {parts, masked, stats}.  See docs/API.md."""
        data = request.get_json(force=True) or {}
        return jsonify(service.mask(data.get("text", ""), data.get("enabled")))

    @app.post("/api/upload")
    def api_upload():
        """multipart 'file' -> {text, name}. Try utf-8, utf-8-sig, cp874, tis-620; else 400."""
        f = request.files.get("file")
        if not f:
            return jsonify({"error": "no file"}), 400
        text = service.decode_upload(f.read())
        if text is None:
            return jsonify({"error": "unsupported encoding"}), 400
        return jsonify({"text": text, "name": f.filename})

    @app.get("/api/generate")
    def api_generate():
        """?n=25 (clamped 5..200) -> {text}."""
        return jsonify(service.generate_log(request.args.get("n", 25, type=int)))

    @app.get("/api/rules")
    def api_rules():
        """-> list of rule descriptions incl. highlighted tokens. See docs/API.md."""
        return jsonify(service.rules())

    @app.get("/api/tests")
    def api_tests():
        """-> results of pdpa_shield/cases.py run through the engine. See docs/API.md."""
        return jsonify(service.tests())

    return app


if __name__ == "__main__":
    create_app().run(debug=True)