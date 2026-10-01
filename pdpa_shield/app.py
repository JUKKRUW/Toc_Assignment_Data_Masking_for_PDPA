from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from pdpa_shield.engine import registry


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
    app.json.ensure_ascii = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "rules": registry.RULE_KEYS})

    @app.post("/api/mask")
    def api_mask():
        """Body {text, enabled?} -> {parts, masked, stats}.  See docs/API.md."""
        request.get_json(force=True)
        raise NotImplementedError("M08: implement POST /api/mask")

    @app.post("/api/upload")
    def api_upload():
        """multipart 'file' -> {text, name}. Try utf-8, utf-8-sig, cp874, tis-620; else 400."""
        raise NotImplementedError("M08: implement POST /api/upload")

    @app.get("/api/generate")
    def api_generate():
        """?n=25 (clamped 5..200) -> {text}."""
        raise NotImplementedError("M08: implement GET /api/generate")

    @app.get("/api/rules")
    def api_rules():
        """-> list of rule descriptions incl. highlighted tokens. See docs/API.md."""
        raise NotImplementedError("M08: implement GET /api/rules")

    @app.get("/api/tests")
    def api_tests():
        """-> results of tests/cases.py run through the engine. See docs/API.md."""
        raise NotImplementedError("M08: implement GET /api/tests")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
