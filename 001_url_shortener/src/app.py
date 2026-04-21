"""Flask web app — redirects, QR codes, REST API."""
import json
from flask import Flask, redirect, abort, jsonify, request, render_template, Response
from . import db
from .models import ShortURL, generate_code, is_valid_url, make_qr_base64

app = Flask(__name__, template_folder="templates")


def _row_to_dict(r) -> dict:
    su = ShortURL.from_row(r)
    return {
        "code":         su.code,
        "display_code": su.display_code,
        "long_url":     su.long_url,
        "alias":        su.alias,
        "clicks":       su.clicks,
        "created_at":   su.created_at,
        "last_click":   su.last_click,
        "expires_at":   su.expires_at,
        "is_expired":   su.is_expired,
    }


# ── Pages ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    rows_data = [_row_to_dict(r) for r in db.list_all()]
    stats     = db.stats()
    rows_json = json.dumps(rows_data, ensure_ascii=False)
    return render_template("index.html", stats=stats, rows_json=rows_json)


@app.route("/+<code>")
def preview(code: str):
    row = db.get_by_code(code)
    if row is None:
        abort(404)
    su = ShortURL.from_row(row)
    if su.is_expired:
        return render_template("expired.html"), 410
    return render_template("preview.html", long_url=row["long_url"], code=code)


@app.route("/<code>")
def redirect_to(code: str):
    row = db.get_by_code(code)
    if row is None:
        abort(404)
    su = ShortURL.from_row(row)
    if su.is_expired:
        return "<h2 style='font-family:sans-serif;color:#ef4444;padding:48px;background:#09090f;min-height:100vh;margin:0'>Link abgelaufen.</h2>", 410
    db.increment_clicks(code, request.referrer)
    return redirect(row["long_url"], code=302)


# ── API ────────────────────────────────────────────────────────────

@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    data       = request.get_json(force=True)
    long_url   = (data.get("url")        or "").strip()
    alias      = (data.get("alias")      or "").strip() or None
    expires_at = (data.get("expires_at") or "").strip() or None

    if not is_valid_url(long_url):
        return jsonify({"error": "Ungültige URL (http/https erforderlich)"}), 400

    code = alias or generate_code()
    if db.code_exists(code):
        return jsonify({"error": f"Code '{code}' bereits vergeben"}), 409

    db.insert(code, long_url, alias, expires_at)
    base = request.host_url.rstrip("/")
    return jsonify({"short_url": f"{base}/{code}", "long_url": long_url, "code": code})


@app.route("/api/urls")
def api_list():
    return jsonify([_row_to_dict(r) for r in db.list_all()])


@app.route("/api/urls/<code>", methods=["DELETE"])
def api_delete(code: str):
    if db.delete(code):
        return jsonify({"ok": True})
    return jsonify({"error": "Nicht gefunden"}), 404


@app.route("/api/urls/<code>", methods=["PUT"])
def api_update(code: str):
    data    = request.get_json(force=True)
    new_url = (data.get("url") or "").strip()
    if not is_valid_url(new_url):
        return jsonify({"error": "Ungültige URL (http/https erforderlich)"}), 400
    if db.update_url(code, new_url):
        return jsonify({"ok": True, "code": code, "long_url": new_url})
    return jsonify({"error": "Nicht gefunden"}), 404


@app.route("/api/stats")
def api_stats():
    return jsonify(db.stats())


@app.route("/api/qr/<code>")
def api_qr(code: str):
    row = db.get_by_code(code)
    if row is None:
        return jsonify({"error": "Nicht gefunden"}), 404
    su        = ShortURL.from_row(row)
    short_url = f"{request.host_url.rstrip('/')}/{su.display_code}"
    qr_b64    = make_qr_base64(short_url)
    return jsonify({"qr": qr_b64, "short_url": short_url, "long_url": row["long_url"]})


@app.route("/api/clicks/<code>")
def api_clicks(code: str):
    days = int(request.args.get("days", 14))
    return jsonify(db.clicks_per_day(code, days))
