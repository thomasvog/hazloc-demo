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
ROLES = {"carga": 1, "cierre": 2, "admin": 3}
ROLE_LABEL = {"carga": "Carga hallazgos", "cierre": "Carga y cierra hallazgos", "admin": "Administrador"}

SCHEMA = [
    "CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL, pw TEXT NOT NULL, role TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS locations(id SERIAL PRIMARY KEY, parent_id INT REFERENCES locations(id), name TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS findings(id SERIAL PRIMARY KEY, location_id INT NOT NULL REFERENCES locations(id),
       tag TEXT, zone TEXT NOT NULL, protection TEXT, criticality TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendiente',
       description TEXT NOT NULL, inspector_id INT REFERENCES users(id) ON DELETE SET NULL, inspected_at DATE NOT NULL,
       resolution TEXT, closed_by INT REFERENCES users(id) ON DELETE SET NULL, closed_at DATE)""",
    """CREATE TABLE IF NOT EXISTS photos(id SERIAL PRIMARY KEY, finding_id INT NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
       kind TEXT NOT NULL, data BYTEA NOT NULL, created_at DATE NOT NULL)""",
    "CREATE TABLE IF NOT EXISTS attempts(id SERIAL PRIMARY KEY, username TEXT NOT NULL, at TIMESTAMPTZ NOT NULL DEFAULT now())",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE",
    """CREATE TABLE IF NOT EXISTS equipment(id SERIAL PRIMARY KEY, tag TEXT NOT NULL, description TEXT,
       location_id INT NOT NULL REFERENCES locations(id), zone TEXT NOT NULL, protection TEXT)""",
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_eq_tag ON equipment(lower(tag))",
    "ALTER TABLE findings ADD COLUMN IF NOT EXISTS equipment_id INT REFERENCES equipment(id) ON DELETE SET NULL",
    "ALTER TABLE findings ADD COLUMN IF NOT EXISTS inspector_name TEXT",
    "ALTER TABLE findings ADD COLUMN IF NOT EXISTS closer_name TEXT",
    "ALTER TABLE findings ALTER COLUMN inspector_id DROP NOT NULL",
    "UPDATE findings f SET inspector_name=u.name FROM users u WHERE u.id=f.inspector_id AND f.inspector_name IS NULL",
    "UPDATE findings f SET closer_name=u.name FROM users u WHERE u.id=f.closed_by AND f.closer_name IS NULL",
    *[("DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname='findings_%s_fkey' AND confdeltype <> 'n') THEN "
       "ALTER TABLE findings DROP CONSTRAINT findings_%s_fkey; "
       "ALTER TABLE findings ADD CONSTRAINT findings_%s_fkey FOREIGN KEY (%s) REFERENCES users(id) ON DELETE SET NULL; "
       "END IF; END $$") % (c, c, c, c) for c in ("inspector_id", "closed_by")],
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
    if "uid" in session:
        u = db().execute("SELECT role, active, name FROM users WHERE id=%s", (session["uid"],)).fetchone()
        if not u or not u["active"]:
            session.clear()
            return redirect(url_for("login"))
        session["role"], session["name"] = u["role"], u["name"]


@app.errorhandler(413)
def too_big(_):
    return "Las fotos pesan demasiado (máximo 4 MB por envío). Volvé atrás y subí menos fotos a la vez.", 413


@app.context_processor
def consts():
    return dict(ZONES=ZONES, CRIT=CRIT, PROT=PROT, ROLES=ROLES, ROLE_LABEL=ROLE_LABEL,
                can_close=ROLES.get(session.get("role"), 0) >= 2)


def locs():
    r = rows("SELECT id, name FROM locations ORDER BY lower(name)")
    return [(x["id"], x["name"], 1) for x in r], {x["id"]: x["name"] for x in r}


def findings():
    a, w, p = request.args, [], []
    if a.get("loc", "").isdigit():
        w.append("f.location_id=%s")
        p.append(int(a["loc"]))
    for k, col in (("zone", "zone"), ("crit", "criticality"), ("status", "status")):
        if a.get(k):
            w.append("f.%s=%%s" % col)
            p.append(a[k])
    if a.get("q"):
        w.append("(f.tag ILIKE %s OR f.description ILIKE %s OR f.resolution ILIKE %s)")
        p += ["%" + a["q"] + "%"] * 3
    sql = ("SELECT f.*, COALESCE(u.name, f.inspector_name, 'Usuario eliminado') inspector, "
           "CASE WHEN f.closed_at IS NOT NULL THEN COALESCE(c.name, f.closer_name, 'Usuario eliminado') END closer FROM findings f "
           "LEFT JOIN users u ON u.id=f.inspector_id LEFT JOIN users c ON c.id=f.closed_by"
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
        if u and u['active'] and check_password_hash(u["pw"], request.form.get("password", "")):
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
    by_area = sorted(((paths[r["location_id"]], r["n"]) for r in rows(
        "SELECT location_id, COUNT(*) n FROM findings WHERE status='pendiente' GROUP BY 1")), key=lambda kv: (-kv[1], kv[0]))
    old = one("SELECT COUNT(*) n FROM findings WHERE status='pendiente' AND CURRENT_DATE - inspected_at > 30")["n"]
    top = rows("SELECT id, tag, zone, criticality, location_id, inspected_at, description FROM findings "
               "WHERE status='pendiente' ORDER BY CASE criticality WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, inspected_at LIMIT 8")
    return render_template("dashboard.html", pend=st.get("pendiente", 0), sol=st.get("solucionado", 0),
                           by_crit=by_crit, by_area=by_area, old=old, top=top, paths=paths)


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
    ws.append(["ID", "Área", "TAG / equipo", "Zona", "Protección Ex", "Criticidad", "Estado", "Descripción",
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


def equipment_list():
    return rows("SELECT e.*, l.name area FROM equipment e JOIN locations l ON l.id=e.location_id ORDER BY lower(e.tag)")


@app.route("/findings/new", methods=["GET", "POST"])
@need()
def new():
    lst, _ = locs()
    f = request.form
    if request.method == "POST":
        eq = None
        if f.get("equipment_id", "").isdigit():
            eq = db().execute("SELECT * FROM equipment WHERE id=%s", (int(f["equipment_id"]),)).fetchone()
        loc = f.get("location_id") or (str(eq["location_id"]) if eq else "")
        if not (loc.isdigit() and f.get("zone") in ZONES and f.get("criticality") in CRIT
                and f.get("description", "").strip()):
            flash("Completá área, zona, criticidad y descripción.")
        else:
            r = run("INSERT INTO findings(location_id,tag,equipment_id,zone,protection,criticality,description,inspector_id,inspector_name,inspected_at)"
                    " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", int(loc), eq["tag"] if eq else "", eq["id"] if eq else None,
                    f["zone"], f.get("protection") if f.get("protection") in PROT else None, f["criticality"],
                    f["description"].strip(), session["uid"], session["name"], dt(f.get("inspected_at"))).fetchone()
            add_photos(r["id"], "antes")
            return redirect(url_for("detail", fid=r["id"]))
    return render_template("form.html", locs=lst, equipment=equipment_list(), f=f, today=date.today().isoformat())


@app.route("/findings/<int:fid>")
@need()
def detail(fid):
    f = one("SELECT f.*, COALESCE(u.name, f.inspector_name, 'Usuario eliminado') inspector, "
            "CASE WHEN f.closed_at IS NOT NULL THEN COALESCE(c.name, f.closer_name, 'Usuario eliminado') END closer FROM findings f "
            "LEFT JOIN users u ON u.id=f.inspector_id LEFT JOIN users c ON c.id=f.closed_by WHERE f.id=%s", fid)
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
        run("UPDATE findings SET status='solucionado', resolution=%s, closed_by=%s, closer_name=%s, closed_at=%s WHERE id=%s",
            res, session["uid"], session["name"], dt(request.form.get("closed_at")), fid)
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


def eq_fields(f):
    tag, loc, zone, prot = f.get("tag", "").strip(), f.get("location_id", ""), f.get("zone"), f.get("protection")
    if not tag or not loc.isdigit() or zone not in ZONES:
        return None
    return tag, f.get("description", "").strip(), int(loc), zone, prot if prot in PROT else None


@app.route("/equipment", methods=["GET", "POST"])
@need("cierre")
def equipment():
    if request.method == "POST":
        v = eq_fields(request.form)
        if not v:
            flash("Completá tag, área y zona.")
        else:
            try:
                run("INSERT INTO equipment(tag,description,location_id,zone,protection) VALUES(%s,%s,%s,%s,%s)", *v)
                flash("Tag agregado.")
            except psycopg.errors.UniqueViolation:
                flash("Ya existe un tag con ese nombre.")
            except psycopg.errors.ForeignKeyViolation:
                flash("El área elegida no existe.")
        return redirect(url_for("equipment"))
    q = request.args.get("q", "").strip()
    items = rows("SELECT e.*, l.name area, (SELECT COUNT(*) FROM findings f WHERE f.equipment_id=e.id) nf FROM equipment e "
                 "JOIN locations l ON l.id=e.location_id WHERE (%s='' OR e.tag ILIKE %s OR e.description ILIKE %s OR l.name ILIKE %s) "
                 "ORDER BY lower(e.tag)", q, "%" + q + "%", "%" + q + "%", "%" + q + "%")
    return render_template("equipment.html", items=items, areas=locs()[0], q=q)


@app.route("/equipment/<int:eid>/edit", methods=["GET", "POST"])
@need("cierre")
def equipment_edit(eid):
    e = one("SELECT * FROM equipment WHERE id=%s", eid)
    if request.method == "POST":
        v = eq_fields(request.form)
        if not v:
            flash("Completá tag, área y zona.")
        else:
            try:
                run("UPDATE equipment SET tag=%s, description=%s, location_id=%s, zone=%s, protection=%s WHERE id=%s", *v, eid)
                run("UPDATE findings SET tag=%s WHERE equipment_id=%s", v[0], eid)
                flash("Tag actualizado.")
                return redirect(url_for("equipment"))
            except psycopg.errors.UniqueViolation:
                flash("Ya existe otro tag con ese nombre.")
            except psycopg.errors.ForeignKeyViolation:
                flash("El área elegida no existe.")
    return render_template("equipment_edit.html", e=e, areas=locs()[0])


@app.post("/equipment/<int:eid>/delete")
@need("cierre")
def equipment_delete(eid):
    one("SELECT 1 FROM equipment WHERE id=%s", eid)
    run("DELETE FROM equipment WHERE id=%s", eid)
    flash("Tag eliminado. Los hallazgos ya cargados conservan su texto.")
    return redirect(url_for("equipment"))


@app.route("/areas", methods=["GET", "POST"])
@need("admin")
def areas():
    f = request.form
    if request.method == "POST":
        name, act = f.get("name", "").strip(), f.get("action")
        if act == "add" and name:
            run("INSERT INTO locations(name) VALUES(%s)", name)
            flash("Área agregada.")
        elif act == "rename" and name and f.get("id", "").isdigit():
            run("UPDATE locations SET name=%s WHERE id=%s", name, int(f["id"]))
            flash("Área renombrada.")
        elif act == "delete" and f.get("id", "").isdigit():
            try:
                run("DELETE FROM locations WHERE id=%s", int(f["id"]))
                flash("Área eliminada.")
            except psycopg.errors.ForeignKeyViolation:
                flash("No se puede eliminar: el área tiene tags u hallazgos asociados.")
        else:
            flash("Escribí un nombre.")
        return redirect(url_for("areas"))
    return render_template("areas.html", items=rows(
        "SELECT l.id, l.name, (SELECT COUNT(*) FROM equipment e WHERE e.location_id=l.id) ne, "
        "(SELECT COUNT(*) FROM findings f WHERE f.location_id=l.id) nf FROM locations l ORDER BY lower(l.name)"))


@app.route("/users", methods=["GET", "POST"])
@need("admin")
def users():
    if request.method == "POST":
        f = request.form
        un, nm, role, pw = f.get("username", "").strip().lower(), f.get("name", "").strip(), f.get("role"), f.get("password", "")
        if not un or not nm or role not in ROLES or len(pw) < 8:
            flash("Usuario, nombre y rol son obligatorios; la contraseña debe tener al menos 8 caracteres.")
        else:
            try:
                run("INSERT INTO users(username,name,pw,role) VALUES(%s,%s,%s,%s)", un, nm, generate_password_hash(pw), role)
                flash("Usuario creado.")
            except psycopg.errors.UniqueViolation:
                flash("Ya existe un usuario con ese nombre de usuario.")
        return redirect(url_for("users"))
    return render_template("users.html", items=rows(
        "SELECT u.*, (SELECT COUNT(*) FROM findings f WHERE f.inspector_id=u.id) nf FROM users u ORDER BY lower(u.username)"))


@app.route("/users/<int:uid>/edit", methods=["GET", "POST"])
@need("admin")
def user_edit(uid):
    u = one("SELECT * FROM users WHERE id=%s", uid)
    if request.method == "POST":
        f = request.form
        un, nm, role, pw = f.get("username", "").strip().lower(), f.get("name", "").strip(), f.get("role"), f.get("password", "")
        active = bool(f.get("active"))
        if uid == session["uid"]:
            role, active = "admin", True
        if not un or not nm or role not in ROLES or (pw and len(pw) < 8):
            flash("Usuario, nombre y rol son obligatorios; la contraseña nueva debe tener al menos 8 caracteres.")
        else:
            try:
                run("UPDATE users SET username=%s, name=%s, role=%s, active=%s WHERE id=%s", un, nm, role, active, uid)
                run("UPDATE findings SET inspector_name=%s WHERE inspector_id=%s", nm, uid)
                run("UPDATE findings SET closer_name=%s WHERE closed_by=%s", nm, uid)
                if pw:
                    run("UPDATE users SET pw=%s WHERE id=%s", generate_password_hash(pw), uid)
                    run("DELETE FROM attempts WHERE username=%s", un)
                flash("Usuario actualizado.")
                return redirect(url_for("users"))
            except psycopg.errors.UniqueViolation:
                flash("Ya existe otro usuario con ese nombre de usuario.")
    return render_template("user_edit.html", u=u, me=(uid == session["uid"]))


@app.post("/users/<int:uid>/delete")
@need("admin")
def user_delete(uid):
    if uid == session["uid"]:
        flash("No podés eliminar tu propio usuario.")
        return redirect(url_for("users"))
    u = one("SELECT username FROM users WHERE id=%s", uid)
    run("DELETE FROM attempts WHERE username=%s", u["username"])
    run("DELETE FROM users WHERE id=%s", uid)
    flash("Usuario eliminado. Sus hallazgos se conservan con su nombre.")
    return redirect(url_for("users"))


@app.route("/password", methods=["GET", "POST"])
@need()
def password():
    if request.method == "POST":
        f = request.form
        u = one("SELECT username, pw FROM users WHERE id=%s", session["uid"])
        if one("SELECT COUNT(*) n FROM attempts WHERE username=%s AND at > now() - interval '10 minutes'", u["username"])["n"] >= 5:
            flash("Demasiados intentos fallidos. Esperá 10 minutos.")
        elif not check_password_hash(u["pw"], f.get("current", "")):
            run("INSERT INTO attempts(username) VALUES(%s)", u["username"])
            flash("La contraseña actual no es correcta.")
        elif len(f.get("new", "")) < 8:
            flash("La contraseña nueva debe tener al menos 8 caracteres.")
        elif f.get("new") != f.get("repeat"):
            flash("Las contraseñas nuevas no coinciden.")
        elif f.get("new") == f.get("current"):
            flash("La contraseña nueva debe ser distinta de la actual.")
        else:
            run("UPDATE users SET pw=%s WHERE id=%s", generate_password_hash(f["new"]), session["uid"])
            run("DELETE FROM attempts WHERE username=%s", u["username"])
            flash("Contraseña actualizada.")
            return redirect(url_for("dashboard"))
    return render_template("password.html")
