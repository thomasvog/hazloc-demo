"""Plantillas HTML (Jinja2). Se editan aquí, en este mismo archivo."""
TEMPLATES = {}

TEMPLATES['admin.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Administración</h2>
<div class="two">
<div class="box"><h3 style="margin-top:0">Ubicaciones</h3>
<form method="post"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><input type="hidden" name="action" value="loc">
<label>Dentro de</label><select name="parent"><option value="">— Nueva planta (nivel superior) —</option>{% for i,p,d in locs if d < LEVELS|length %}<option value="{{ i }}">{{ p }}</option>{% endfor %}</select>
<label>Nombre</label><input name="name" required>
<p class="mu">Niveles: {{ LEVELS|join(' › ') }}.</p><p><button class="btn y">Agregar ubicación</button></p></form>
{% for i,p,d in locs %}<div style="padding-left:{{ (d-1)*1.2 }}rem">{{ p.split(' › ')[-1] }} <span class="mu">({{ LEVELS[d-1] }})</span></div>{% else %}<p class="mu">Todavía no hay ubicaciones.</p>{% endfor %}</div>
<div class="box"><h3 style="margin-top:0">Usuarios</h3>
<form method="post"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><input type="hidden" name="action" value="user">
<label>Usuario</label><input name="username" required><label>Nombre completo</label><input name="name" required>
<label>Rol</label><select name="role">{% for r in ROLES %}<option value="{{ r }}">{{ ROLE_LABEL[r] }}</option>{% endfor %}</select>
<label>Contraseña <span class="mu">(si el usuario ya existe, vacía = no cambia)</span></label><input name="password" type="password" autocomplete="new-password">
<p><button class="btn y">Guardar usuario</button></p></form>
{% for u in users %}<div>{{ u.username }} · {{ u.name }} <span class="mu">({{ ROLE_LABEL[u.role] }})</span></div>{% endfor %}</div>
</div>{% endblock %}
'''

TEMPLATES['base.html'] = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% block t %}Inspecciones HAZLOC{% endblock %}</title>
<style>
:root{--bg:#eceee9;--pa:#fbfbf9;--tx:#1b222b;--mu:#5d6773;--ln:#d3d7d0;--dk:#1c2430;--ye:#f5b400;--alta:#c0392b;--media:#d9830b;--baja:#3b7d4f;--ok:#2f6f4f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.45 system-ui,"Segoe UI",Roboto,sans-serif}
a{color:#0b5cad}
header{background:var(--dk);color:#fff;border-bottom:4px solid var(--ye);display:flex;flex-wrap:wrap;gap:.25rem 1rem;align-items:center;padding:.5rem 1rem}
header b{font-size:1.05rem;margin-right:.5rem}
header a,header button{color:#fff;text-decoration:none;padding:.35rem .6rem;border-radius:4px;background:none;border:0;font:inherit;cursor:pointer}
header a:hover,header button:hover{background:#ffffff22}
header .r{margin-left:auto;display:flex;align-items:center;gap:.5rem;font-size:.9rem}
main{max-width:1100px;margin:0 auto;padding:1rem}
h1,h2{margin:.2rem 0 .8rem;line-height:1.2}
h2 small{color:var(--mu);font-weight:400}
.box{background:var(--pa);border:1px solid var(--ln);border-radius:6px;padding:1rem;margin-bottom:1rem}
.msg{background:#fff4cf;border:1px solid #e3c56b;border-radius:6px;padding:.6rem .9rem;margin-bottom:1rem}
label{display:block;font-weight:600;margin:.7rem 0 .2rem}
input,select,textarea{width:100%;font:inherit;padding:.5rem .6rem;border:1px solid #aab0a8;border-radius:5px;background:#fff;color:var(--tx)}
textarea{min-height:7rem}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0 .8rem}
.btn{display:inline-block;background:var(--dk);color:#fff;border:0;border-radius:5px;padding:.55rem 1rem;font:inherit;font-weight:600;cursor:pointer;text-decoration:none}
.btn.y{background:var(--ye);color:#1b1500}.btn.g{background:var(--ok)}.btn.l{background:#fff;color:var(--tx);border:1px solid #aab0a8}
.pill{display:inline-block;padding:.05rem .55rem;border-radius:99px;color:#fff;font-size:.85rem;font-weight:600}
.pill.alta{background:var(--alta)}.pill.media{background:var(--media)}.pill.baja{background:var(--baja)}
.pill.pendiente{background:#fff;color:var(--alta);border:1px solid var(--alta)}.pill.solucionado{background:var(--ok)}
.tag{font-family:ui-monospace,Menlo,Consolas,monospace}
table{width:100%;border-collapse:collapse;background:var(--pa)}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--ln);vertical-align:top}
th{font-size:.85rem;color:var(--mu);font-weight:600}
td.c{border-left:6px solid var(--baja)}td.c.alta{border-left-color:var(--alta)}td.c.media{border-left-color:var(--media)}td.c.solucionado{border-left-color:var(--ok);opacity:.8}
.scroll{overflow-x:auto;border:1px solid var(--ln);border-radius:6px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1rem}
.big{font-size:2.6rem;font-weight:700;line-height:1}.mu{color:var(--mu)}
.bar{display:flex;align-items:center;gap:.6rem;margin:.35rem 0}.bar span:first-child{width:5.5rem}
.bar i{display:block;height:1.1rem;border-radius:3px;background:var(--dk);min-width:2px}
.split{height:1.6rem;border-radius:4px;overflow:hidden;display:flex;background:#ddd;margin:.7rem 0 .3rem}
.split i{display:block;height:100%}
.photos{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.6rem;margin:.5rem 0}
.photos img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:5px;border:1px solid var(--ln)}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.3rem 1rem;margin:0}dt{color:var(--mu)}dd{margin:0}
:focus-visible{outline:3px solid var(--ye);outline-offset:2px}
@media(max-width:600px){main{padding:.6rem}.big{font-size:2.2rem}}
</style></head><body>
<header><b>Inspecciones HAZLOC</b>
{% if session.uid %}<a href="{{ url_for('dashboard') }}">Resumen</a><a href="{{ url_for('listing') }}">Hallazgos</a>
<a href="{{ url_for('new') }}">Nuevo hallazgo</a>{% if session.role=='admin' %}<a href="{{ url_for('admin') }}">Administración</a>{% endif %}
<span class="r">{{ session.name }}<form method="post" action="{{ url_for('logout') }}" style="margin:0"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button>Salir</button></form></span>{% endif %}
</header><main>
{% for m in get_flashed_messages() %}<div class="msg">{{ m }}</div>{% endfor %}
{% block c %}{% endblock %}
</main>
<script>
/* Reduce las fotos en el navegador antes de enviarlas (Vercel limita cada envío a ~4,5 MB) */
document.addEventListener('change',async e=>{const i=e.target;if(i.type!=='file'||!i.files.length)return;
const dt=new DataTransfer();
for(const f of i.files){if(!f.type.startsWith('image/')){dt.items.add(f);continue}
try{const b=await createImageBitmap(f,{imageOrientation:'from-image'}),k=Math.min(1,1400/Math.max(b.width,b.height)),c=document.createElement('canvas');
c.width=Math.round(b.width*k);c.height=Math.round(b.height*k);c.getContext('2d').drawImage(b,0,0,c.width,c.height);
const blob=await new Promise(r=>c.toBlob(r,'image/jpeg',.8));dt.items.add(new File([blob],f.name.replace(/\.\w+$/,'')+'.jpg',{type:'image/jpeg'}))}catch(x){dt.items.add(f)}}
i.files=dt.files});
</script></body></html>
'''

TEMPLATES['dashboard.html'] = r'''{% extends "base.html" %}{% block c %}
{% set tot = pend + sol %}
<h2>Estado de los hallazgos</h2>
<div class="box">
 <div class="big">{{ pend }} <span class="mu" style="font-size:1.1rem;font-weight:400">pendientes de {{ tot }} registrados</span></div>
 <div class="split">{% if tot %}<i style="width:{{ sol*100/tot }}%;background:var(--ok)"></i>{% endif %}</div>
 <div class="mu">{{ sol }} solucionados{% if tot %} ({{ (sol*100/tot)|round|int }}%){% endif %}{% if old %} · <b style="color:var(--alta)">{{ old }} pendientes con más de 30 días</b>{% endif %}</div>
</div>
<div class="two">
 <div class="box"><h3 style="margin-top:0">Pendientes por criticidad</h3>
 {% for c in CRIT %}{% set n = by_crit.get(c,0) %}<div class="bar"><span><span class="pill {{c}}">{{ c }}</span></span><i style="width:{{ n*100/(pend or 1) }}%;background:var(--{{c}})"></i><b>{{ n }}</b></div>{% endfor %}</div>
 <div class="box"><h3 style="margin-top:0">Pendientes por zona</h3>
 {% for z in ZONES %}{% set n = by_zone.get(z,0) %}<div class="bar"><span>Zona {{ z }}</span><i style="width:{{ n*100/(pend or 1) }}%"></i><b>{{ n }}</b></div>{% endfor %}</div>
</div>
<h3>Pendientes más urgentes</h3>
{% if top %}<div class="scroll"><table>
{% for f in top %}<tr><td class="c {{ f.criticality }}"><a href="{{ url_for('detail', fid=f.id) }}"><b class="tag">{{ f.tag or '#%d'|format(f.id) }}</b></a>
<div class="mu">{{ paths[f.location_id] }} · Zona {{ f.zone }} · {{ f.inspected_at }}</div>{{ f.description|truncate(110) }}</td></tr>{% endfor %}
</table></div>{% else %}<p class="mu">No hay hallazgos pendientes. Registrá el primero con «Nuevo hallazgo».</p>{% endif %}
{% endblock %}
'''

TEMPLATES['detail.html'] = r'''{% extends "base.html" %}{% block c %}
{% macro gallery(items) %}{% if items %}<div class="photos">{% for p in items %}<a href="{{ url_for('files', pid=p.id) }}" target="_blank"><img loading="lazy" src="{{ url_for('files', pid=p.id) }}" alt="Foto {{ p.id }}"></a>{% endfor %}</div>{% else %}<p class="mu">Sin fotos.</p>{% endif %}{% endmacro %}
<h2><span class="tag">{{ f.tag or 'Hallazgo #%d'|format(f.id) }}</span> <span class="pill {{ f.criticality }}">{{ f.criticality }}</span> <span class="pill {{ f.status }}">{{ f.status }}</span></h2>
<div class="box"><dl>
<dt>Ubicación</dt><dd>{{ path }}</dd><dt>Zona</dt><dd>{{ f.zone }}{% if f.protection %} · {{ f.protection }}{% endif %}</dd>
<dt>Inspección</dt><dd>{{ f.inspected_at }} · {{ f.inspector }}</dd>
{% if f.status=='solucionado' %}<dt>Cierre</dt><dd>{{ f.closed_at }} · {{ f.closer }}</dd>{% endif %}</dl></div>
<div class="two">
<div class="box"><h3 style="margin-top:0">Estado encontrado</h3><p style="white-space:pre-wrap">{{ f.description }}</p>{{ gallery(ph.antes) }}
<form method="post" action="{{ url_for('photos', fid=f.id) }}" enctype="multipart/form-data"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><input type="hidden" name="kind" value="antes">
<input type="file" name="photos" accept="image/*" multiple required> <p><button class="btn l">Agregar fotos</button></p></form></div>
<div class="box"><h3 style="margin-top:0">Estado después de la reparación</h3>
{% if f.status=='solucionado' %}<p style="white-space:pre-wrap">{{ f.resolution }}</p>{{ gallery(ph.despues) }}
{% if can_close %}<form method="post" action="{{ url_for('photos', fid=f.id) }}" enctype="multipart/form-data"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><input type="hidden" name="kind" value="despues">
<input type="file" name="photos" accept="image/*" multiple required> <p><button class="btn l">Agregar fotos</button></p></form>
<form method="post" action="{{ url_for('reopen', fid=f.id) }}"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button class="btn l">Reabrir hallazgo</button></form>{% endif %}
{% elif can_close %}<form method="post" action="{{ url_for('close', fid=f.id) }}" enctype="multipart/form-data"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Qué se reparó o cambió</label><textarea name="resolution" required></textarea>
<label>Fecha de cierre</label><input type="date" name="closed_at" value="{{ today }}">
<label>Fotos del resultado</label><input type="file" name="photos" accept="image/*" multiple>
<p><button class="btn g">Marcar como solucionado</button></p></form>
{% else %}<p class="mu">Pendiente. Lo cierra un usuario con permiso de cierre.</p>{% endif %}</div>
</div>{% endblock %}
'''

TEMPLATES['form.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Nuevo hallazgo</h2>
{% if not locs %}<div class="msg">Todavía no hay ubicaciones cargadas. {% if session.role=='admin' %}<a href="{{ url_for('admin') }}">Agregalas en Administración</a>.{% else %}Pedile a un administrador que las cargue.{% endif %}</div>{% endif %}
<form method="post" enctype="multipart/form-data" class="box"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Ubicación</label><select name="location_id" required><option value="">Elegir…</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if f.get('location_id')==i|string }}>{{ p }}</option>{% endfor %}</select>
<div class="row">
<div><label>TAG o equipo afectado</label><input name="tag" class="tag" value="{{ f.get('tag','') }}"></div>
<div><label>Zona</label><select name="zone" required><option value="">Elegir…</option>{% for z in ZONES %}<option {{ 'selected' if f.get('zone')==z }}>{{ z }}</option>{% endfor %}</select></div>
<div><label>Protección Ex</label><select name="protection"><option value="">—</option>{% for p in PROT %}<option {{ 'selected' if f.get('protection')==p }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Criticidad</label><select name="criticality" required><option value="">Elegir…</option>{% for c in CRIT %}<option {{ 'selected' if f.get('criticality')==c }}>{{ c }}</option>{% endfor %}</select></div>
<div><label>Fecha de inspección</label><input type="date" name="inspected_at" value="{{ f.get('inspected_at') or today }}"></div>
</div>
<label>Qué se encontró</label><textarea name="description" required>{{ f.get('description','') }}</textarea>
<label>Fotos del estado encontrado</label><input type="file" name="photos" accept="image/*" multiple>
<p><button class="btn y">Guardar hallazgo</button> <a class="btn l" href="{{ url_for('listing') }}">Cancelar</a></p></form>{% endblock %}
'''

TEMPLATES['list.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Hallazgos <small>({{ items|length }})</small></h2>
<form class="box" method="get">
<div class="row">
<div><label>Buscar</label><input name="q" placeholder="TAG o texto" value="{{ request.args.q or '' }}"></div>
<div><label>Lugar</label><select name="loc"><option value="">Todos</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if request.args.loc==i|string }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Zona</label><select name="zone"><option value="">Todas</option>{% for z in ZONES %}<option {{ 'selected' if request.args.zone==z }}>{{ z }}</option>{% endfor %}</select></div>
<div><label>Criticidad</label><select name="crit"><option value="">Todas</option>{% for c in CRIT %}<option {{ 'selected' if request.args.crit==c }}>{{ c }}</option>{% endfor %}</select></div>
<div><label>Estado</label><select name="status"><option value="">Todos</option>{% for s in ['pendiente','solucionado'] %}<option {{ 'selected' if request.args.status==s }}>{{ s }}</option>{% endfor %}</select></div>
</div>
<p><button class="btn">Filtrar</button> <a class="btn l" href="{{ url_for('listing') }}">Limpiar</a>
<a class="btn y" href="{{ url_for('export', **request.args) }}">Exportar a Excel</a></p></form>
{% if items %}<div class="scroll"><table><tr><th>Hallazgo</th><th>Zona</th><th>Criticidad</th><th>Estado</th><th>Inspección</th></tr>
{% for f in items %}<tr><td class="c {{ 'solucionado' if f.status=='solucionado' else f.criticality }}">
<a href="{{ url_for('detail', fid=f.id) }}"><b class="tag">{{ f.tag or '#%d'|format(f.id) }}</b></a>
<div class="mu">{{ paths[f.location_id] }}</div>{{ f.description|truncate(100) }}</td>
<td>{{ f.zone }}{% if f.protection %}<div class="mu">{{ f.protection }}</div>{% endif %}</td>
<td><span class="pill {{ f.criticality }}">{{ f.criticality }}</span></td>
<td><span class="pill {{ f.status }}">{{ f.status }}</span></td>
<td>{{ f.inspected_at }}<div class="mu">{{ f.inspector }}</div></td></tr>{% endfor %}</table></div>
{% else %}<p class="mu">Ningún hallazgo coincide con estos filtros.</p>{% endif %}{% endblock %}
'''

TEMPLATES['login.html'] = r'''{% extends "base.html" %}{% block c %}
<form method="post" class="box" style="max-width:380px;margin:2rem auto">
<h2>Ingresar</h2><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label for="u">Usuario</label><input id="u" name="username" autofocus autocomplete="username">
<label for="p">Contraseña</label><input id="p" name="password" type="password" autocomplete="current-password">
<p><button class="btn y">Ingresar</button></p></form>{% endblock %}
'''

TEMPLATES['setup.html'] = r'''{% extends "base.html" %}{% block c %}
<form method="post" class="box" style="max-width:420px;margin:2rem auto">
<h2>Instalación inicial</h2><p class="mu">Creá el usuario administrador. Solo se puede hacer una vez.</p>
{% if key_missing %}<div class="msg">Falta la variable <b>SETUP_KEY</b> en Vercel (Settings › Environment Variables). Agregala, hacé un Redeploy y volvé a esta página.</div>{% endif %}
<input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Código de instalación (valor de SETUP_KEY)</label><input name="key" type="password" autocomplete="off">
<label>Usuario</label><input name="username" autocomplete="username"><label>Nombre completo</label><input name="name">
<label>Contraseña (mínimo 8 caracteres)</label><input name="password" type="password" autocomplete="new-password">
<p><button class="btn y">Crear administrador</button></p></form>{% endblock %}
'''
