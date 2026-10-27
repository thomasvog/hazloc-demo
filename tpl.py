"""Plantillas HTML (Jinja2). Se editan aquí, en este mismo archivo."""
TEMPLATES = {}

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
.menu{position:relative}
header .hb{display:flex;align-items:center;justify-content:center;width:2.6rem;height:2.6rem;padding:0;border:1px solid #ffffff55}
#mn{position:absolute;top:calc(100% + .45rem);left:0;z-index:30;min-width:15rem;background:var(--pa);color:var(--tx);border:1px solid var(--ln);border-radius:6px;box-shadow:0 8px 24px #0004;padding:.3rem}
#mn[hidden]{display:none}
.ck{display:flex;gap:.6rem;align-items:center;font-weight:400;margin:0;padding:.45rem .6rem;border-bottom:1px solid var(--ln)}.ck input{width:auto}.ck[hidden]{display:none}
#tl{max-height:18rem;overflow:auto;border:1px solid var(--ib);border-radius:6px;background:var(--in)}
#mn .sep{border-top:1px solid var(--ln);margin:.3rem .4rem}
#mn a{display:block;color:var(--tx);padding:.65rem .8rem;border-radius:4px;border-left:4px solid transparent}
#mn a:hover{background:var(--bg)}#mn a[aria-current]{border-left-color:var(--ye);font-weight:700;background:var(--bg)}
</style></head><body>
{% set ep = request.endpoint or '' %}{% macro it(url, label, on) %}<a href="{{ url }}" {{ 'aria-current=page' if on }}>{{ label }}</a>{% endmacro %}
<header>{% if session.uid %}<div class="menu"><button type="button" id="mb" class="hb" aria-label="Menú" aria-expanded="false" aria-controls="mn"><svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg></button>
<nav id="mn" hidden>{{ it(url_for('dashboard'), 'Resumen', ep=='dashboard') }}{{ it(url_for('listing'), 'Hallazgos', ep in ('listing','detail')) }}{{ it(url_for('new'), 'Nuevo hallazgo', ep=='new') }}{{ it(url_for('declass'), 'Desclasificaciones', ep in ('declass','declass_new','declass_detail')) }}{% if can_close %}{{ it(url_for('equipment'), 'Tags', ep in ('equipment','equipment_edit')) }}{% endif %}{% if session.role=='admin' %}{{ it(url_for('areas'), 'Áreas', ep=='areas') }}{{ it(url_for('users'), 'Usuarios', ep in ('users','user_edit')) }}{% endif %}<div class="sep"></div>{{ it(url_for('password'), 'Cambiar contraseña', ep=='password') }}</nav></div>{% endif %}
<b>Inspecciones HAZLOC</b>
{% if session.uid %}<span class="r">{{ session.name }}<form method="post" action="{{ url_for('logout') }}" style="margin:0"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button>Salir</button></form></span>{% endif %}
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
</script>
<script>
(function(){var b=document.getElementById('mb'),m=document.getElementById('mn');if(!b)return;
function set(o){m.hidden=!o;b.setAttribute('aria-expanded',o)}
b.addEventListener('click',function(e){e.stopPropagation();set(m.hidden)});
document.addEventListener('click',function(e){if(!m.hidden&&!m.contains(e.target))set(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!m.hidden){set(false);b.focus()}});})();
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
 <div class="box"><h3 style="margin-top:0">Pendientes por área</h3>
 {% for label, n in by_area %}<div class="bar"><span style="width:10rem;font-size:.9rem">{{ label }}</span><i style="width:{{ n*100/(pend or 1) }}%"></i><b>{{ n }}</b></div>{% else %}<p class="mu">No hay pendientes.</p>{% endfor %}</div>
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
<dt>Área</dt><dd>{{ path }}</dd><dt>Zona</dt><dd>{{ f.zone }}{% if f.protection %} · {{ f.protection }}{% endif %}</dd>
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

<form method="post" enctype="multipart/form-data" class="box"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Tag / equipo</label>
<select name="equipment_id" id="eq"><option value="">— Sin tag —</option>{% for e in equipment %}<option value="{{ e.id }}" data-loc="{{ e.location_id }}" data-zone="{{ e.zone }}" data-prot="{{ e.protection or '' }}" {{ 'selected' if f.get('equipment_id')==e.id|string }}>{{ e.tag }} · {{ e.area }}{% if e.description %} · {{ e.description }}{% endif %}</option>{% endfor %}</select>
<p class="mu" style="margin:.2rem 0 0">Al elegir un tag se completan área, zona y protección. {% if can_close %}<a href="{{ url_for('equipment') }}">Administrar tags</a>.{% else %}Si falta un tag, pedile a un supervisor que lo cargue.{% endif %}</p>
<div class="row">
<div><label>Área</label><select name="location_id" id="loc" required><option value="">Elegir…</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if f.get('location_id')==i|string }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Zona</label><select name="zone" id="zone" required><option value="">Elegir…</option>{% for z in ZONES %}<option {{ 'selected' if f.get('zone')==z }}>{{ z }}</option>{% endfor %}</select></div>
<div><label>Protección Ex</label><select name="protection" id="prot"><option value="">—</option>{% for p in PROT %}<option {{ 'selected' if f.get('protection')==p }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Criticidad</label><select name="criticality" required><option value="">Elegir…</option>{% for c in CRIT %}<option {{ 'selected' if f.get('criticality')==c }}>{{ c }}</option>{% endfor %}</select></div>
<div><label>Fecha de inspección</label><input type="date" name="inspected_at" value="{{ f.get('inspected_at') or today }}"></div>
</div>
<label>Qué se encontró</label><textarea name="description" required>{{ f.get('description','') }}</textarea>
<label>Fotos del estado encontrado</label><input type="file" name="photos" accept="image/*" multiple>
<p><button class="btn y">Guardar hallazgo</button> <a class="btn l" href="{{ url_for('listing') }}">Cancelar</a></p></form>
<script>
const eq=document.getElementById('eq');
eq.addEventListener('change',()=>{const o=eq.selectedOptions[0];if(!o.value)return;
document.getElementById('loc').value=o.dataset.loc;document.getElementById('zone').value=o.dataset.zone;document.getElementById('prot').value=o.dataset.prot});
</script>{% endblock %}
'''

TEMPLATES['list.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Hallazgos <small>({{ items|length }})</small></h2>
<form class="box" method="get">
<div class="row">
<div><label>Buscar</label><input name="q" placeholder="TAG o texto" value="{{ request.args.q or '' }}"></div>
<div><label>Área</label><select name="loc"><option value="">Todos</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if request.args.loc==i|string }}>{{ p }}</option>{% endfor %}</select></div>
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

TEMPLATES['equipment.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Tags de equipos <small>({{ items|length }})</small></h2>
{% if session.role=='admin' %}<p><a class="btn l" href="{{ url_for('equipment_import') }}">Importar planilla</a></p>{% endif %}

<form method="post" class="box"><h3>Agregar tag</h3><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<div class="row">
<div><label>Tag</label><input name="tag" class="tag" required value=""></div>
<div><label>Descripción</label><input name="description" value=""></div>
<div><label>Área</label><select name="location_id" required><option value="">Elegir…</option>{% for i,p,d in areas %}<option value="{{ i }}" >{{ p }}</option>{% endfor %}</select></div>
<div><label>Zona</label><select name="zone" required><option value="">Elegir…</option>{% for z in ZONES %}<option >{{ z }}</option>{% endfor %}</select></div>
<div><label>Protección Ex</label><select name="protection"><option value="">—</option>{% for p in PROT %}<option >{{ p }}</option>{% endfor %}</select></div>
</div>
<p><button class="btn y">Agregar tag</button></p></form>
<form class="box" method="get"><label>Buscar</label><div class="row"><input name="q" value="{{ q }}" placeholder="Tag, descripción o área"><div><button class="btn">Buscar</button> <a class="btn l" href="{{ url_for('equipment') }}">Limpiar</a></div></div></form>
{% if items %}<div class="scroll"><table><tr><th>Tag</th><th>Área</th><th>Zona</th><th>Hallazgos</th><th></th></tr>
{% for e in items %}<tr><td><b class="tag">{{ e.tag }}</b><div class="mu">{{ e.description or '' }}</div></td><td>{{ e.area }}</td>
<td>{{ e.zone }}<div class="mu">{{ e.protection or '' }}</div></td><td>{{ e.nf }}</td>
<td style="white-space:nowrap"><a class="btn l" href="{{ url_for('equipment_edit', eid=e.id) }}">Editar</a>
<form method="post" action="{{ url_for('equipment_delete', eid=e.id) }}" style="display:inline" onsubmit="return confirm('¿Eliminar este tag? Los hallazgos ya cargados conservan su texto.')"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button class="btn l">Borrar</button></form></td></tr>{% endfor %}
</table></div>{% else %}<p class="mu">No hay tags cargados todavía.</p>{% endif %}{% endblock %}
'''

TEMPLATES['equipment_edit.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Editar tag <span class="tag">{{ e.tag }}</span></h2>
<form method="post" class="box"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<div class="row">
<div><label>Tag</label><input name="tag" class="tag" required value="{{ e.tag }}"></div>
<div><label>Descripción</label><input name="description" value="{{ e.description or '' }}"></div>
<div><label>Área</label><select name="location_id" required><option value="">Elegir…</option>{% for i,p,d in areas %}<option value="{{ i }}" {{ 'selected' if e.location_id==i }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Zona</label><select name="zone" required><option value="">Elegir…</option>{% for z in ZONES %}<option {{ 'selected' if e.zone==z }}>{{ z }}</option>{% endfor %}</select></div>
<div><label>Protección Ex</label><select name="protection"><option value="">—</option>{% for p in PROT %}<option {{ 'selected' if e.protection==p }}>{{ p }}</option>{% endfor %}</select></div>
</div>
<p class="mu">Si cambiás el nombre del tag, también se actualiza en los hallazgos ya cargados.</p>
<p><button class="btn y">Guardar cambios</button> <a class="btn l" href="{{ url_for('equipment') }}">Cancelar</a></p></form>{% endblock %}
'''

TEMPLATES['areas.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Áreas</h2>
<p class="mu">Las áreas son fijas y no se pueden agregar ni quitar.</p>
<div class="scroll"><table><tr><th>Área</th><th>Tags</th><th>Hallazgos pendientes</th><th>Hallazgos totales</th></tr>
{% for a in items %}<tr><td><a class="lk" href="{{ url_for('listing', loc=a.id) }}">{{ a.name }}</a></td><td>{{ a.ne }}</td><td>{{ a.np }}</td><td>{{ a.nf }}</td></tr>{% endfor %}
</table></div>{% endblock %}
'''

TEMPLATES['users.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Usuarios</h2>
<div class="scroll"><table><tr><th>Usuario</th><th>Nombre</th><th>Rol</th><th>Estado</th><th>Hallazgos</th><th></th></tr>
{% for u in items %}<tr><td class="tag">{{ u.username }}</td><td>{{ u.name }}</td><td>{{ ROLE_LABEL[u.role] }}</td>
<td>{{ 'Activo' if u.active else 'Desactivado' }}</td><td>{{ u.nf }}</td><td style="white-space:nowrap"><a class="btn l" href="{{ url_for('user_edit', uid=u.id) }}">Editar</a>
{% if u.id != session.uid %}<form method="post" action="{{ url_for('user_delete', uid=u.id) }}" style="display:inline" onsubmit="return confirm('¿Eliminar este usuario? Sus hallazgos se conservan con su nombre y no podrá volver a ingresar.')"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button class="btn l">Eliminar</button></form>{% endif %}</td></tr>{% endfor %}</table></div>
<form method="post" class="box" style="margin-top:1rem"><h3>Agregar usuario</h3><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<div class="row"><div><label>Usuario</label><input name="username" required autocomplete="off"></div><div><label>Nombre completo</label><input name="name" required></div>
<div><label>Rol</label><select name="role">{% for r in ROLES %}<option value="{{ r }}">{{ ROLE_LABEL[r] }}</option>{% endfor %}</select></div>
<div><label>Contraseña (mín. 8)</label><input name="password" type="password" autocomplete="new-password" required></div></div>
<p><button class="btn y">Crear usuario</button></p></form>{% endblock %}
'''

TEMPLATES['user_edit.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Editar usuario <span class="tag">{{ u.username }}</span></h2>
<form method="post" class="box"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<div class="row"><div><label>Usuario</label><input name="username" required value="{{ u.username }}"></div><div><label>Nombre completo</label><input name="name" required value="{{ u.name }}"></div>
<div><label>Rol</label><select name="role" {{ 'disabled' if me }}>{% for r in ROLES %}<option value="{{ r }}" {{ 'selected' if u.role==r }}>{{ ROLE_LABEL[r] }}</option>{% endfor %}</select></div>
<div><label>Contraseña nueva <span class="mu">(vacía = no cambia)</span></label><input name="password" type="password" autocomplete="new-password"></div></div>
<label style="display:flex;gap:.5rem;align-items:center;font-weight:400"><input type="checkbox" name="active" value="1" style="width:auto" {{ 'checked' if u.active }} {{ 'disabled' if me }}> Usuario activo (si se desactiva, no puede ingresar)</label>
{% if me %}<p class="mu">Tu propio usuario siempre queda como administrador y activo.</p>{% endif %}
<p><button class="btn y">Guardar cambios</button> <a class="btn l" href="{{ url_for('users') }}">Cancelar</a></p></form>
{% if not me %}<form method="post" action="{{ url_for('user_delete', uid=u.id) }}" onsubmit="return confirm('¿Eliminar este usuario? Sus hallazgos se conservan con su nombre y no podrá volver a ingresar.')"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><button class="btn l">Eliminar usuario</button></form>{% endif %}{% endblock %}
'''

TEMPLATES['password.html'] = r'''{% extends "base.html" %}{% block c %}
<form method="post" class="box" style="max-width:420px;margin:1rem auto">
<h2>Cambiar contraseña</h2><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Contraseña actual</label><input name="current" type="password" autocomplete="current-password" required>
<label>Contraseña nueva (mínimo 8 caracteres)</label><input name="new" type="password" autocomplete="new-password" required>
<label>Repetir contraseña nueva</label><input name="repeat" type="password" autocomplete="new-password" required>
<p><button class="btn y">Guardar contraseña</button> <a class="btn l" href="{{ url_for('dashboard') }}">Cancelar</a></p></form>{% endblock %}
'''

TEMPLATES['equipment_import.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Importar tags desde planilla</h2>
<form method="post" enctype="multipart/form-data" class="box">
<input type="hidden" name="_csrf" value="{{ session.csrf }}">
<label>Archivo (.xlsx o .csv)</label><input type="file" name="file" accept=".xlsx,.csv,.txt" required>
<p class="mu">Columnas, en este orden o con estos títulos en la primera fila: <b>Tag</b>, Descripción, <b>Área</b>, <b>Zona</b>, Protección Ex. Son obligatorios Tag, Área y Zona (0, 1, 2, 20, 21, 22 o Segura). Se lee la primera hoja del archivo.<br>
Si el tag ya existe, se actualiza con los datos de la planilla; las celdas vacías de descripción y protección no borran lo que ya estaba cargado. Después podés editar cada tag desde la pestaña Tags.</p>
<p><button class="btn l" name="mode" value="check">Revisar sin guardar</button> <button class="btn y" name="mode" value="import">Importar</button>
<a class="btn l" href="{{ url_for('equipment_template') }}">Descargar planilla modelo</a></p></form>
{% if res %}<div class="box"><h3>{{ 'Importación realizada' if res.saved else 'Revisión (no se guardó nada)' }}</h3>
<dl><dt>Filas leídas</dt><dd>{{ res.total }}</dd><dt>Tags nuevos</dt><dd>{{ res.new }}</dd><dt>Tags actualizados</dt><dd>{{ res.updated }}</dd><dt>Sin cambios</dt><dd>{{ res.same }}</dd>
<dt>Repetidos en la planilla</dt><dd>{{ res.dups }}</dd><dt>Filas con error (no se cargan)</dt><dd>{{ res.errs|length }}</dd></dl>
{% if not res.saved and (res.new or res.updated) %}<p class="mu">Si está todo bien, elegí el mismo archivo y presioná <b>Importar</b>.</p>{% endif %}
{% if res.saved %}<p><a class="btn y" href="{{ url_for('equipment') }}">Ver los tags</a></p>{% endif %}</div>
{% if res.errs %}<div class="box"><h3>Filas con error</h3><div class="scroll"><table><tr><th>Fila</th><th>Motivo</th></tr>{% for n, m in res.errs[:100] %}<tr><td>{{ n }}</td><td>{{ m }}</td></tr>{% endfor %}</table></div>{% if res.errs|length > 100 %}<p class="mu">Se muestran las primeras 100.</p>{% endif %}</div>{% endif %}
{% if res.warns %}<div class="box"><h3>Advertencias</h3><div class="scroll"><table><tr><th>Fila</th><th>Detalle</th></tr>{% for n, m in res.warns[:100] %}<tr><td>{{ n }}</td><td>{{ m }}</td></tr>{% endfor %}</table></div></div>{% endif %}{% endif %}
{% endblock %}
'''

TEMPLATES['declass.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Desclasificaciones <small>({{ items|length }})</small></h2>
<p><a class="btn y" href="{{ url_for('declass_new') }}">Nueva desclasificación</a></p>
<form class="box" method="get"><div class="row">
<div><label>Área</label><select name="loc"><option value="">Todas</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if request.args.loc==i|string }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Buscar</label><input name="q" value="{{ request.args.q or '' }}" placeholder="Tag, motivo, trabajo o responsable"></div></div>
<p><button class="btn">Filtrar</button> <a class="btn l" href="{{ url_for('declass') }}">Limpiar</a></p></form>
{% if items %}<div class="scroll"><table><tr><th>Fecha</th><th>Área y tags</th><th>Motivo</th><th>Responsable</th></tr>
{% for d in items %}<tr><td>{{ d.done_at }}</td><td><a class="lk" href="{{ url_for('declass_detail', did=d.id) }}"><b>{{ d.area }}</b></a><div class="mu tag">{{ d.tags|truncate(70) }}{% if d.nt > 1 %} ({{ d.nt }}){% endif %}</div></td>
<td>{{ d.reason|truncate(100) }}</td><td>{{ d.responsible }}</td></tr>{% endfor %}</table></div>
{% else %}<p class="mu">No hay desclasificaciones cargadas.</p>{% endif %}{% endblock %}
'''

TEMPLATES['declass_form.html'] = r'''{% extends "base.html" %}{% block c %}
<h2>Nueva desclasificación</h2>
<form method="post" enctype="multipart/form-data" class="box"><input type="hidden" name="_csrf" value="{{ session.csrf }}">
<div class="row"><div><label>Área</label><select name="location_id" id="loc" required><option value="">Elegir…</option>{% for i,p,d in locs %}<option value="{{ i }}" {{ 'selected' if f.get('location_id')==i|string }}>{{ p }}</option>{% endfor %}</select></div>
<div><label>Fecha del trabajo</label><input type="date" name="done_at" value="{{ f.get('done_at') or today }}"></div>
<div><label>Responsable</label><input name="responsible" required value="{{ f.get('responsible') or me }}"></div></div>
<label>Tags afectados <span class="mu" id="cnt"></span></label>
<div class="row" style="margin-bottom:.4rem"><input id="flt" placeholder="Filtrar tags del área…" autocomplete="off"><div><button type="button" class="btn l" id="all">Marcar los visibles</button> <button type="button" class="btn l" id="none">Desmarcar todos</button></div></div>
<div id="tl"><p class="mu" id="hint" style="padding:.6rem;margin:0">Elegí un área para ver sus tags.</p>
{% for e in equipment %}<label class="ck" data-loc="{{ e.location_id }}" data-t="{{ e.tag|lower }} {{ (e.description or '')|lower }}" hidden><input type="checkbox" name="equipment_id" value="{{ e.id }}" {{ 'checked' if e.id|string in f.getlist('equipment_id') }}><span><b class="tag">{{ e.tag }}</b> <span class="mu">{{ e.description or '' }} · Zona {{ e.zone }}</span></span></label>{% endfor %}</div>
<label>Motivo (por qué no era una zona con atmósfera explosiva)</label><textarea name="reason" required>{{ f.get('reason','') }}</textarea>
<label>Trabajo realizado</label><textarea name="description" required>{{ f.get('description','') }}</textarea>
<label style="display:flex;gap:.5rem;align-items:center;font-weight:600;margin-top:1rem"><input type="checkbox" name="set_safe" value="1" style="width:auto" checked> Cambiar la zona de los tags marcados a «Segura»</label>
<div class="two"><div><label>Fotos del antes</label><input type="file" name="photos_antes" accept="image/*" multiple></div><div><label>Fotos del después</label><input type="file" name="photos_despues" accept="image/*" multiple></div></div>
<p><button class="btn y">Guardar desclasificación</button> <a class="btn l" href="{{ url_for('declass') }}">Cancelar</a></p></form>
<script>
(function(){var loc=document.getElementById('loc'),flt=document.getElementById('flt'),cnt=document.getElementById('cnt'),hint=document.getElementById('hint'),
L=[].slice.call(document.querySelectorAll('#tl .ck'));
function upd(){var n=0,v=0,t=flt.value.toLowerCase().trim();
L.forEach(function(l){var show=loc.value&&l.dataset.loc===loc.value&&(!t||l.dataset.t.indexOf(t)>-1);l.hidden=!show;if(show)v++;if(l.firstChild.checked)n++});
hint.hidden=!!loc.value&&v>0;hint.textContent=loc.value?'No hay tags para mostrar en esta área.':'Elegí un área para ver sus tags.';
cnt.textContent=n?'('+n+' marcados)':''}
loc.addEventListener('change',function(){L.forEach(function(l){l.firstChild.checked=false});upd()});
flt.addEventListener('input',upd);
document.getElementById('tl').addEventListener('change',upd);
document.getElementById('all').addEventListener('click',function(){L.forEach(function(l){if(!l.hidden)l.firstChild.checked=true});upd()});
document.getElementById('none').addEventListener('click',function(){L.forEach(function(l){l.firstChild.checked=false});upd()});
upd()})();
</script>{% endblock %}
'''

TEMPLATES['declass_detail.html'] = r'''{% extends "base.html" %}{% block c %}
{% macro gallery(items) %}{% if items %}<div class="photos">{% for p in items %}<a href="{{ url_for('dfiles', pid=p.id) }}" target="_blank"><img loading="lazy" src="{{ url_for('dfiles', pid=p.id) }}" alt="Foto {{ p.id }}"></a>{% endfor %}</div>{% else %}<p class="mu">Sin fotos.</p>{% endif %}{% endmacro %}
<p><a class="lk" href="{{ url_for('declass') }}">‹ Volver al listado</a></p>
<h2>Desclasificación · {{ d.area }}</h2>
<div class="box"><dl><dt>Fecha</dt><dd>{{ d.done_at }}</dd><dt>Responsable</dt><dd>{{ d.responsible }}</dd>
<dt>Zona de los tags</dt><dd>{{ 'Se cambió a Segura' if d.set_safe else 'No se modificó' }}</dd></dl></div>
<div class="two"><div class="box"><h3>Motivo</h3><p style="white-space:pre-wrap">{{ d.reason }}</p></div>
<div class="box"><h3>Trabajo realizado</h3><p style="white-space:pre-wrap">{{ d.description }}</p></div></div>
<div class="box"><h3>Tags afectados ({{ tags|length }})</h3><div class="scroll"><table><tr><th>Tag</th><th>Zona antes del trabajo</th></tr>
{% for t in tags %}<tr><td class="tag">{{ t.tag }}</td><td>{{ t.prev_zone or '—' }}</td></tr>{% endfor %}</table></div></div>
<div class="two">{% for k, title in (('antes','Fotos del antes'),('despues','Fotos del después')) %}<div class="box"><h3>{{ title }}</h3>{{ gallery(ph[k]) }}
<form method="post" action="{{ url_for('declass_add_photos', did=d.id) }}" enctype="multipart/form-data"><input type="hidden" name="_csrf" value="{{ session.csrf }}"><input type="hidden" name="kind" value="{{ k }}">
<input type="file" name="photos" accept="image/*" multiple required> <p><button class="btn l">Agregar fotos</button></p></form></div>{% endfor %}</div>{% endblock %}
'''
