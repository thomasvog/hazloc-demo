"""Inspecciones HAZLOC (IEC/IECEx) - versión para Vercel + Postgres (Neon)."""
import hashlib
import io
import os
import secrets
from datetime import date
from functools import wraps

import psycopg
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   send_file, session, url_for)
from jinja2 import DictLoader
from openpyxl import Workbook
from PIL import Image, ImageOps
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash, generate_password_hash

from tpl import TEMPLATES

URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or ""
SETUP_KEY = os.environ.get("SETUP_KEY", "")

app = Flask(__name__)
app.jinja_env.loader = DictLoader(TEMPLATES)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or hashlib.sha256(("hazloc|" + URL).encode()).hexdigest(),
    MAX_CONTENT_LENGTH=4 * 1024 * 1024,  # Vercel admite ~4,5 MB por request
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.environ.get("VERCEL")),
)

ZONES = ["0", "1", "2", "20", "21", "22"]
CRIT = ["alta", "media", "baja"]
PROT = ["Ex d", "Ex e", "Ex i", "Ex p", "Ex n", "Ex m", "Ex o", "Ex q", "Ex t", "Otro / N.A."]
LEVELS = ["Planta", "Sector", "Área", "Equipo"]
ROLES = {"carga": 1, "cierre": 2, "admin": 3}
ROLE_LABEL = {"carga": "Carga hallazgos", "cierre": "Carga y cierra hallazgos", "admin": "Administrador"}

SCHEMA = [
    "CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL, pw TEXT NOT NULL, role TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS locations(id SERIAL PRIMARY KEY, parent_id INT REFERENCES locations(id), name TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS findings(id SERIAL PRIMARY KEY, location_id INT NOT NULL REFERENCES locations(id),
       tag TEXT, zone TEXT NOT NULL, protection TEXT, criticality TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendiente',
       description TEXT NOT NULL, inspector_id INT NOT NULL REFERENCES users(id), inspected_at DATE NOT NULL,
       resolution TEXT, closed_by INT REFERENCES users(id), closed_at DATE)""",
    """CREATE TABLE IF NOT EXISTS photos(id SERIAL PRIMARY KEY, finding_id INT NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
       kind TEXT NOT NULL, data BYTEA NOT NULL, created_at DATE NOT NULL)""",
    "CREATE TABLE IF NOT EXISTS attempts(id SERIAL PRIMARY KEY, username TEXT NOT NULL, at TIMESTAMPTZ NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS ix_f ON findings(status, criticality, zone, location_id)",
    "CREATE INDEX IF NOT EXISTS ix_p ON photos(finding_id)",
]
_ready = _has = False


def db():
    if "db" not in g:
        g.db = psycopg.connect(URL, row_factory=dict_row, autocommit=True, prepare_threshold=None)
    return g.db


@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d:
        d.close()


def rows(sql, *p):
    return db().execute(sql, p).fetchall()


def one(sql, *p):
    r = db().execute(sql, p).fetchone()
    if r is None:
        abort(404)
    return r


def run(sql, *p):
    return db().execute(sql, p)


def dt(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return date.today()


def has_users():
    global _has
    if not _has:
        _has = db().execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    return _has


def need(role="carga"):
    def deco(fn):
        @wraps(fn)
        def w(*a, **k):
            if "uid" not in session:
                return redirect(url_for("login", next=request.path))
            if ROLES[session["role"]] < ROLES[role]:
                abort(403)
            return fn(*a, **k)
        return w
    return deco


@app.before_request
def gate():
    global _ready
    if not URL:
        return "Falta conectar la base de datos (variable DATABASE_URL). Ver el README, paso 3.", 503
    if not _ready:
        for s in SCHEMA:
            try:
                db().execute(s)
            except psycopg.Error:
                pass
        _ready = True
    session.setdefault("csrf", secrets.token_hex(16))
    if request.method == "POST" and request.form.get("_csrf") != session["csrf"]:
        abort(400)
    if request.endpoint not in ("setup", None) and not has_users():
        return redirect(url_for("setup"))


@app.errorhandler(413)
def too_big(_):
    return "Las fotos pesan demasiado (máximo 4 MB por envío). Volvé atrás y subí menos fotos a la vez.", 413


@app.context_processor
def consts():
    return dict(ZONES=ZONES, CRIT=CRIT, PROT=PROT, LEVELS=LEVELS, ROLES=ROLES, ROLE_LABEL=ROLE_LABEL,
                can_close=ROLES.get(session.get("role"), 0) >= 2)


def locs():
    r = rows("SELECT id,parent_id,name FROM locations")
    by = {x["id"]: x for x in r}

    def path(i):
        out = []
        while i:
            out.append(by[i]["name"])
            i = by[i]["parent_id"]
        return out[::-1]

    lst = sorted(((i, " › ".join(path(i)), len(path(i))) for i in by), key=lambda t: t[1])
    return lst, {i: p for i, p, _ in lst}


def descendants(root):
    kids = {}
    for x in rows("SELECT id,parent_id FROM locations"):
        kids.setdefault(x["parent_id"], []).append(x["id"])
    out, st = [], [root]
    while st:
        i = st.pop()
        out.append(i)
        st += kids.get(i, [])
    return out


def findings():
    a, w, p = request.args, [], []
    if a.get("loc", "").isdigit():
        w.append("f.location_id = ANY(%s)")
        p.append(descendants(int(a["loc"])))
    for k, col in (("zone", "zone"), ("crit", "criticality"), ("status", "status")):
        if a.get(k):
            w.append("f.%s=%%s" % col)
            p.append(a[k])
    if a.get("q"):
        w.append("(f.tag ILIKE %s OR f.description ILIKE %s OR f.resolution ILIKE %s)")
        p += ["%" + a["q"] + "%"] * 3
    sql = ("SELECT f.*, u.name inspector, c.name closer FROM findings f "
           "JOIN users u ON u.id=f.inspector_id LEFT JOIN users c ON c.id=f.closed_by"
           + (" WHERE " + " AND ".join(w) if w else "")
           + " ORDER BY f.status='solucionado', CASE f.criticality WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END,"
             " f.inspected_at DESC, f.id DESC")
    return rows(sql, *p)


def add_photos(fid, kind):
    n = 0
    for f in request.files.getlist("photos"):
        if not f.filename:
            continue
        try:
            im = ImageOps.exif_transpose(Image.open(f.stream)).convert("RGB")
            im.thumbnail((1600, 1600))
        except Exception:
            flash("No se pudo leer «%s»: no es una imagen válida." % f.filename)
            continue
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=80)
        run("INSERT INTO photos(finding_id,kind,data,created_at) VALUES(%s,%s,%s,%s)",
            fid, kind, buf.getvalue(), date.today())
        n += 1
    return n


@app.route("/setup", methods=["GET", "POST"])
def setup():
    global _has
    if has_users():
        return redirect(url_for("login"))
    if request.method == "POST":
        f = request.form
        un, nm, pw = f.get("username", "").strip().lower(), f.get("name", "").strip(), f.get("password", "")
        if not SETUP_KEY or not secrets.compare_digest(f.get("key", ""), SETUP_KEY):
            flash("Código de instalación incorrecto (es el valor de la variable SETUP_KEY en Vercel).")
        elif not un or not nm or len(pw) < 8:
            flash("Completá usuario y nombre. La contraseña debe tener al menos 8 caracteres.")
        else:
            run("INSERT INTO users(username,name,pw,role) VALUES(%s,%s,%s,'admin')", un, nm, generate_password_hash(pw))
            _has = True
            flash("Administrador creado. Ya podés ingresar.")
            return redirect(url_for("login"))
    return render_template("setup.html", key_missing=not SETUP_KEY)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        un = request.form.get("username", "").strip().lower()
        if one("SELECT COUNT(*) n FROM attempts WHERE username=%s AND at > now() - interval '10 minutes'", un)["n"] >= 5:
            flash("Demasiados intentos fallidos. Esperá 10 minutos.")
            return render_template("login.html")
        u = db().execute("SELECT * FROM users WHERE username=%s", (un,)).fetchone()
        if u and check_password_hash(u["pw"], request.form.get("password", "")):
            run("DELETE FROM attempts WHERE username=%s", un)
            session.clear()
            session.update(uid=u["id"], name=u["name"], role=u["role"], csrf=secrets.token_hex(16))
            nxt = request.args.get("next", "/")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else "/")
        run("INSERT INTO attempts(username) VALUES(%s)", un)
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@need()
def dashboard():
    st = {r["status"]: r["n"] for r in rows("SELECT status, COUNT(*) n FROM findings GROUP BY 1")}
    by_crit = {r["k"]: r["n"] for r in rows("SELECT criticality k, COUNT(*) n FROM findings WHERE status='pendiente' GROUP BY 1")}
    paths = locs()[1]
    sec = {}
    for r in rows("SELECT location_id, COUNT(*) n FROM findings WHERE status='pendiente' GROUP BY 1"):
        parts = paths[r["location_id"]].split(" › ")
        k = " › ".join(parts[:2]) if len(parts) > 1 else parts[0] + " (sin sector)"
        sec[k] = sec.get(k, 0) + r["n"]
    by_sector = sorted(sec.items(), key=lambda kv: (-kv[1], kv[0]))
    old = one("SELECT COUNT(*) n FROM findings WHERE status='pendiente' AND CURRENT_DATE - inspected_at > 30")["n"]
    top = rows("SELECT id, tag, zone, criticality, location_id, inspected_at, description FROM findings "
               "WHERE status='pendiente' ORDER BY CASE criticality WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, inspected_at LIMIT 8")
    return render_template("dashboard.html", pend=st.get("pendiente", 0), sol=st.get("solucionado", 0),
                           by_crit=by_crit, by_sector=by_sector, old=old, top=top, paths=paths)


@app.route("/findings")
@need()
def listing():
    lst, paths = locs()
    return render_template("list.html", items=findings(), locs=lst, paths=paths)


@app.route("/export.xlsx")
@need()
def export():
    _, paths = locs()
    wb = Workbook()
    ws = wb.active
    ws.title = "Hallazgos"
    ws.append(["ID", "Ubicación", "TAG / equipo", "Zona", "Protección Ex", "Criticidad", "Estado", "Descripción",
               "Inspector", "Fecha inspección", "Resolución", "Cerrado por", "Fecha cierre", "Fotos antes", "Fotos después"])
    cnt = {}
    for r in rows("SELECT finding_id, kind, COUNT(*) n FROM photos GROUP BY 1, 2"):
        cnt[(r["finding_id"], r["kind"])] = r["n"]
    for f in findings():
        ws.append([f["id"], paths[f["location_id"]], f["tag"], f["zone"], f["protection"], f["criticality"],
                   f["status"], f["description"], f["inspector"], f["inspected_at"], f["resolution"], f["closer"],
                   f["closed_at"], cnt.get((f["id"], "antes"), 0), cnt.get((f["id"], "despues"), 0)])
    for col, wd in zip("ABCDEFGHIJKLMNO", (6, 45, 18, 7, 12, 10, 12, 60, 20, 14, 50, 20, 13, 11, 13)):
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = "A2"
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="hallazgos_%s.xlsx" % date.today(),
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/findings/new", methods=["GET", "POST"])
@need()
def new():
    lst, _ = locs()
    f = request.form
    if request.method == "POST":
        if not (f.get("location_id", "").isdigit() and f.get("zone") in ZONES and f.get("criticality") in CRIT
                and f.get("description", "").strip()):
            flash("Completá ubicación, zona, criticidad y descripción.")
        else:
            r = run("INSERT INTO findings(location_id,tag,zone,protection,criticality,description,inspector_id,inspected_at)"
                    " VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", int(f["location_id"]), f.get("tag", "").strip(), f["zone"],
                    f.get("protection") if f.get("protection") in PROT else None, f["criticality"],
                    f["description"].strip(), session["uid"], dt(f.get("inspected_at"))).fetchone()
            add_photos(r["id"], "antes")
            return redirect(url_for("detail", fid=r["id"]))
    return render_template("form.html", locs=lst, f=f, today=date.today().isoformat())


@app.route("/findings/<int:fid>")
@need()
def detail(fid):
    f = one("SELECT f.*, u.name inspector, c.name closer FROM findings f JOIN users u ON u.id=f.inspector_id "
            "LEFT JOIN users c ON c.id=f.closed_by WHERE f.id=%s", fid)
    ph = {"antes": [], "despues": []}
    for p in rows("SELECT id, kind FROM photos WHERE finding_id=%s ORDER BY id", fid):
        ph[p["kind"]].append(p)
    return render_template("detail.html", f=f, ph=ph, path=locs()[1][f["location_id"]], today=date.today().isoformat())


@app.post("/findings/<int:fid>/photos")
@need()
def photos(fid):
    one("SELECT 1 FROM findings WHERE id=%s", fid)
    kind = request.form.get("kind")
    if kind not in ("antes", "despues") or (kind == "despues" and ROLES[session["role"]] < 2):
        abort(403)
    if not add_photos(fid, kind):
        flash("No se agregó ninguna foto.")
    return redirect(url_for("detail", fid=fid))


@app.post("/findings/<int:fid>/close")
@need("cierre")
def close(fid):
    one("SELECT 1 FROM findings WHERE id=%s", fid)
    res = request.form.get("resolution", "").strip()
    if not res:
        flash("Describí qué se reparó o cambió para poder cerrar el hallazgo.")
    else:
        run("UPDATE findings SET status='solucionado', resolution=%s, closed_by=%s, closed_at=%s WHERE id=%s",
            res, session["uid"], dt(request.form.get("closed_at")), fid)
        add_photos(fid, "despues")
    return redirect(url_for("detail", fid=fid))


@app.post("/findings/<int:fid>/reopen")
@need("cierre")
def reopen(fid):
    one("SELECT 1 FROM findings WHERE id=%s", fid)
    run("UPDATE findings SET status='pendiente', resolution=NULL, closed_by=NULL, closed_at=NULL WHERE id=%s", fid)
    return redirect(url_for("detail", fid=fid))


@app.route("/files/<int:pid>")
@need()
def files(pid):
    r = one("SELECT data FROM photos WHERE id=%s", pid)
    resp = send_file(io.BytesIO(r["data"]), mimetype="image/jpeg")
    resp.headers["Cache-Control"] = "private, max-age=86400"
    return resp


@app.route("/admin", methods=["GET", "POST"])
@need("admin")
def admin():
    lst, _ = locs()
    f = request.form
    if request.method == "POST":
        if f.get("action") == "user":
            un, nm, role, pw = f.get("username", "").strip().lower(), f.get("name", "").strip(), f.get("role"), f.get("password", "")
            ex = db().execute("SELECT id FROM users WHERE username=%s", (un,)).fetchone()
            if not un or not nm or role not in ROLES or (not ex and len(pw) < 8) or (pw and len(pw) < 8):
                flash("Usuario, nombre y rol son obligatorios; la contraseña debe tener al menos 8 caracteres.")
            elif ex:
                if ex["id"] == session["uid"]:
                    role = "admin"
                run("UPDATE users SET name=%s, role=%s WHERE id=%s", nm, role, ex["id"])
                if pw:
                    run("UPDATE users SET pw=%s WHERE id=%s", generate_password_hash(pw), ex["id"])
                flash("Usuario actualizado.")
            else:
                run("INSERT INTO users(username,name,pw,role) VALUES(%s,%s,%s,%s)", un, nm, generate_password_hash(pw), role)
                flash("Usuario creado.")
        elif f.get("action") == "loc":
            depth = {i: d for i, _, d in lst}
            parent = int(f["parent"]) if f.get("parent", "").isdigit() else None
            if not f.get("name", "").strip():
                flash("Escribí un nombre.")
            elif parent and depth.get(parent, 9) >= len(LEVELS):
                flash("Un equipo es el último nivel y no admite elementos dentro.")
            else:
                run("INSERT INTO locations(parent_id,name) VALUES(%s,%s)", parent, f["name"].strip())
                flash("Ubicación agregada.")
        return redirect(url_for("admin"))
    return render_template("admin.html", users=rows("SELECT * FROM users ORDER BY username"), locs=locs()[0])
