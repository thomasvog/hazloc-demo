# Inspecciones HAZLOC (Vercel + base de datos Neon)

Aplicación Flask con base de datos Postgres. Los hallazgos y las fotos se guardan en Neon, así que no se pierden al recargar ni al volver a desplegar.

## Puesta en marcha (todo desde el navegador)

1. **GitHub:** crear un repositorio nuevo, elegir *Add file › Upload files*, arrastrar los 4 archivos (`app.py`, `tpl.py`, `requirements.txt`, `README.md`) y presionar *Commit changes*.
2. **Vercel:** *Add New › Project*, importar el repositorio. Antes de presionar Deploy, abrir *Environment Variables* y agregar `SETUP_KEY` con un código a elección (por ejemplo una frase larga). Presionar *Deploy*.
3. **Base de datos:** dentro del proyecto en Vercel, ir a la pestaña *Storage*, elegir *Neon* (Postgres) y conectarlo al proyecto. Vercel agrega solo la variable `DATABASE_URL`.
4. **Redeploy:** pestaña *Deployments*, menú ⋯ del último despliegue › *Redeploy*.
5. Abrir la URL del proyecto. La primera vez aparece la pantalla de instalación: ingresar el código `SETUP_KEY` y crear el usuario administrador.
6. En *Administración*, cargar las ubicaciones (planta › sector › área › equipo) y los usuarios.

## Notas

- Cada envío admite hasta ~4 MB de fotos. El navegador las reduce solo antes de enviarlas; si subís muchas juntas, hacelo en tandas.
- Tras 5 intentos fallidos de ingreso, el usuario queda bloqueado 10 minutos.
- Roles: *carga* (registra hallazgos y fotos del estado encontrado), *cierre* (además cierra, reabre y sube fotos del después), *admin* (además gestiona usuarios y ubicaciones).
- Las plantillas HTML están dentro de `tpl.py`.
