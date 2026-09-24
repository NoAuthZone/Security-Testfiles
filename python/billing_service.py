import json
import re
import sqlite3
import subprocess

from flask import Flask, abort, jsonify, request

app = Flask(__name__)
DB_PATH = "billing.db"
NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/invoices")
def list_invoices():
    customer = request.args.get("customer", "")
    conn = get_db()
    rows = conn.execute(
        "SELECT id, amount, due FROM invoices WHERE customer = ?", (customer,)
    ).fetchall()
    return jsonify(rows)


@app.route("/export", methods=["POST"])
def export():
    name = request.form["name"]
    if not NAME_RE.fullmatch(name):
        abort(400)
    result = subprocess.run(
        ["tar", "czf", f"/exports/{name}.tgz", "/data/invoices"], capture_output=True
    )
    return jsonify({"rc": result.returncode})


@app.route("/draft/restore", methods=["POST"])
def restore_draft():
    draft = json.loads(request.get_data(as_text=True))
    if not isinstance(draft, dict):
        abort(400)
    return jsonify({"fields": sorted(draft.keys())})


if __name__ == "__main__":
    app.run()
