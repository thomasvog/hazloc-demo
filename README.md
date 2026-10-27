# Inspecciones HAZLOC (Vercel + base de datos Neon)

Aplicación Flask con base de datos Postgres. Los hallazgos y las fotos se guardan en Neon, así que no se pierden al recargar ni al volver a desplegar.

## Puesta en marcha (todo desde el navegador)

1. **GitHub:** crear un repositorio nuevo, elegir *Add file › Upload files*, arrastrar los 4 archivos (`app.py`, `tpl.py`, `requirements.txt`, `README.md`) y presionar *Commit changes*.
2. **Vercel:** *Add New › Project*, importar el repositorio. Antes de presionar Deploy, abrir *Environment Variables* y agregar `SETUP_KEY` con un código a elección (por ejemplo una frase larga). Presionar *Deploy*.
3. **Base de datos:** dentro del proyecto en Vercel, ir a la pestaña *Storage*, elegir *Neon* (Postgres) y conectarlo al proyecto. Vercel agrega solo la variable `DATABASE_URL`.
4. **Redeploy:** pestaña *Deployments*, menú ⋯ del último despliegue › *Redeploy*.
5. Abrir la URL del proyecto. La primera vez aparece la pantalla de instalación: ingresar el código `SETUP_KEY` y crear el usuario administrador.
6. Cargar las **Áreas** y los **Usuarios** (menú *Áreas* y *Usuarios*, solo administrador) y los **Tags** de equipos (menú *Tags*, supervisores y administrador).

## Notas

- Cada envío admite hasta ~4 MB de fotos. El navegador las reduce solo antes de enviarlas; si subís muchas juntas, hacelo en tandas.
- Tras 5 intentos fallidos de ingreso, el usuario queda bloqueado 10 minutos.
- Roles: *carga* (registra hallazgos eligiendo el tag de una lista y sube fotos del estado encontrado), *cierre* (además cierra, reabre, sube fotos del después y administra los tags), *admin* (además gestiona áreas y usuarios).
- Cada usuario puede cambiar su contraseña desde «Cambiar contraseña» (arriba a la derecha). El administrador puede eliminar usuarios aunque tengan hallazgos: los hallazgos se conservan con el nombre que tenía.
- Un usuario desactivado no puede ingresar; los cambios de rol y de estado se aplican al instante.
- Las plantillas HTML están dentro de `tpl.py`.
