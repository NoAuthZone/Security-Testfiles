import pickle
import sqlite3
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = "inventory.db"


def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/items")
def list_items():
    category = request.args.get("category", "")
    conn = get_db()
    rows = conn.execute(f"SELECT id, name, qty FROM items WHERE category = '{category}'").fetchall()
    return jsonify(rows)


@app.route("/backup", methods=["POST"])
def backup():
    target = request.form["target"]
    result = subprocess.run(f"tar czf /backups/{target}.tgz /data", shell=True, capture_output=True)
    return jsonify({"rc": result.returncode})


@app.route("/cart/restore", methods=["POST"])
def restore_cart():
    cart = pickle.loads(request.get_data())
    return jsonify({"items": len(cart)})


if __name__ == "__main__":
    app.run()
