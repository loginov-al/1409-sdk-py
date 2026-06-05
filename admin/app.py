import os
import json
import hashlib
import mimetypes
import secrets
from pathlib import Path
from functools import wraps

from flask import (
    Flask, request, jsonify, send_from_directory,
    render_template, session, redirect, url_for, abort
)
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
CORS(app, resources={r"/design/*": {"origins": "*"}})

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1409")

STORAGE_ROOT = Path(__file__).parent / "storage"
CATEGORIES = ["logo", "background", "icon", "font", "component"]
ALLOWED_EXTENSIONS = {
    "logo": {"png", "jpg", "jpeg", "svg", "webp"},
    "background": {"png", "jpg", "jpeg", "svg", "webp"},
    "icon": {"png", "jpg", "jpeg", "svg", "ico", "webp"},
    "font": {"ttf", "otf", "woff", "woff2"},
    "component": {"css", "js", "html", "svg"},
}

for cat in CATEGORIES:
    (STORAGE_ROOT / cat).mkdir(parents=True, exist_ok=True)


# ─── helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename: str, category: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS.get(category, set())


def get_file_info(path: Path, category: str) -> dict:
    stat = path.stat()
    mime, _ = mimetypes.guess_type(str(path))
    return {
        "name": path.name,
        "stem": path.stem,
        "category": category,
        "size": stat.st_size,
        "size_human": _human_size(stat.st_size),
        "mime": mime or "application/octet-stream",
        "url": f"/design?component={path.stem}",
        "preview_url": f"/storage/{category}/{path.name}",
        "is_image": (mime or "").startswith("image/"),
        "is_font": (mime or "") in {"font/ttf", "font/otf", "font/woff", "font/woff2"}
                   or path.suffix.lower() in {".ttf", ".otf", ".woff", ".woff2"},
    }


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            if request.is_json or request.path.startswith("/api/"):
                abort(401)
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper


# ─── auth ─────────────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET"])
def login_page():
    if session.get("logged_in"):
        return redirect("/admin")
    return render_template("login.html")


@app.route("/admin/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    login_val = data.get("login", "")
    password = data.get("password", "")
    if login_val == ADMIN_LOGIN and password == ADMIN_PASSWORD:
        session["logged_in"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Неверный логин или пароль"}), 401


@app.route("/admin/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


# ─── admin panel ──────────────────────────────────────────────────────────────

@app.route("/admin")
@app.route("/admin/")
@login_required
def admin_index():
    return render_template("admin.html")


# ─── admin API ────────────────────────────────────────────────────────────────

@app.route("/api/assets", methods=["GET"])
@login_required
def api_list_assets():
    category = request.args.get("category", "")
    search = request.args.get("search", "").lower()
    result = {}
    cats = [category] if category in CATEGORIES else CATEGORIES
    for cat in cats:
        files = []
        for p in sorted((STORAGE_ROOT / cat).iterdir()):
            if p.is_file():
                info = get_file_info(p, cat)
                if not search or search in info["name"].lower():
                    files.append(info)
        result[cat] = files
    return jsonify(result)


@app.route("/api/assets/upload", methods=["POST"])
@login_required
def api_upload():
    category = request.form.get("category", "")
    if category not in CATEGORIES:
        return jsonify({"ok": False, "error": "Неверная категория"}), 400

    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "Файл не выбран"}), 400

    filename = secure_filename(file.filename)
    if not allowed_file(filename, category):
        exts = ", ".join(ALLOWED_EXTENSIONS[category])
        return jsonify({"ok": False, "error": f"Недопустимый тип файла. Разрешено: {exts}"}), 400

    dest = STORAGE_ROOT / category / filename
    file.save(dest)
    return jsonify({"ok": True, "asset": get_file_info(dest, category)})


@app.route("/api/assets/delete", methods=["DELETE"])
@login_required
def api_delete():
    data = request.get_json(silent=True) or {}
    category = data.get("category", "")
    name = data.get("name", "")
    if category not in CATEGORIES:
        return jsonify({"ok": False, "error": "Неверная категория"}), 400
    path = STORAGE_ROOT / category / secure_filename(name)
    if not path.exists() or not path.is_file():
        return jsonify({"ok": False, "error": "Файл не найден"}), 404
    path.unlink()
    return jsonify({"ok": True})


@app.route("/api/assets/rename", methods=["PATCH"])
@login_required
def api_rename():
    data = request.get_json(silent=True) or {}
    category = data.get("category", "")
    old_name = data.get("old_name", "")
    new_name = data.get("new_name", "")
    if category not in CATEGORIES:
        return jsonify({"ok": False, "error": "Неверная категория"}), 400
    old_path = STORAGE_ROOT / category / secure_filename(old_name)
    if not old_path.exists():
        return jsonify({"ok": False, "error": "Файл не найден"}), 404
    new_filename = secure_filename(new_name)
    if not new_filename:
        return jsonify({"ok": False, "error": "Некорректное имя"}), 400
    new_path = STORAGE_ROOT / category / new_filename
    old_path.rename(new_path)
    return jsonify({"ok": True, "asset": get_file_info(new_path, category)})


@app.route("/api/stats", methods=["GET"])
@login_required
def api_stats():
    stats = {}
    total_size = 0
    total_count = 0
    for cat in CATEGORIES:
        files = list((STORAGE_ROOT / cat).iterdir())
        files = [f for f in files if f.is_file()]
        size = sum(f.stat().st_size for f in files)
        stats[cat] = {"count": len(files), "size": size, "size_human": _human_size(size)}
        total_size += size
        total_count += len(files)
    stats["total"] = {"count": total_count, "size": total_size, "size_human": _human_size(total_size)}
    return jsonify(stats)


# ─── public SDK API ───────────────────────────────────────────────────────────

@app.route("/design")
def design_get():
    component = request.args.get("component", "")
    if not component:
        return jsonify({"error": "component parameter required"}), 400
    for cat in CATEGORIES:
        cat_dir = STORAGE_ROOT / cat
        for p in cat_dir.iterdir():
            if p.is_file() and p.stem == component:
                return send_from_directory(cat_dir, p.name)
    return jsonify({"error": "Component not found"}), 404


@app.route("/design/list")
def design_list():
    components = []
    for cat in CATEGORIES:
        for p in (STORAGE_ROOT / cat).iterdir():
            if p.is_file():
                components.append(p.stem)
    return jsonify(components)


# ─── static storage ───────────────────────────────────────────────────────────

@app.route("/storage/<category>/<filename>")
def serve_storage(category, filename):
    if category not in CATEGORIES:
        abort(404)
    return send_from_directory(STORAGE_ROOT / category, filename)


# ─── entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"🚀  1409 Admin Panel → http://{host}:{port}/admin")
    print(f"📦  API endpoints   → http://{host}:{port}/design")
    app.run(host=host, port=port, debug=debug)