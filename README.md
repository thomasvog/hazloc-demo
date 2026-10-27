# Inspecciones HAZLOC (Vercel + base de datos Neon)

Aplicación Flask con base de datos Postgres. Los hallazgos y las fotos se guardan en Neon, así que no se pierden al recargar ni al volver a desplegar.

## Puesta en marcha (todo desde el navegador)

1. **GitHub:** crear un repositorio nuevo, elegir *Add file › Upload files*, arrastrar los 4 archivos (`app.py`, `tpl.py`, `requirements.txt`, `README.md`) y presionar *Commit changes*.
2. **Vercel:** *Add New › Project*, importar el repositorio. Antes de presionar Deploy, abrir *Environment Variables* y agregar `SETUP_KEY` con un código a elección (por ejemplo una frase larga). Presionar *Deploy*.
3. **Base de datos:** dentro del proyecto en Vercel, ir a la pestaña *Storage*, elegir *Neon* (Postgres) y conectarlo al proyecto. Vercel agrega solo la variable `DATABASE_URL`.
4. **Redeploy:** pestaña *Deployments*, menú ⋯ del último despliegue › *Redeploy*.
5. Abrir la URL del proyecto. La primera vez aparece la pantalla de instalación: ingresar el código `SETUP_KEY` y crear el usuario administrador.
6. Las **Áreas** son fijas (Polímeros, Extrusión, Unidad 500, Servicios, Bagging) y se crean solas. Cargar los **Usuarios** (menú *Usuarios*, solo administrador) y los **Tags** de equipos (menú *Tags*, supervisor y administrador).

## Notas

- Cada envío admite hasta ~4 MB de fotos. El navegador las reduce solo antes de enviarlas; si subís muchas juntas, hacelo en tandas.
- Tras 5 intentos fallidos de ingreso, el usuario queda bloqueado 10 minutos.
- Roles: *Técnico* (carga y cierra hallazgos, sube fotos y registra desclasificaciones), *Supervisor* (lo mismo y además agrega, edita y borra tags) y *Administrador* (además gestiona usuarios, consulta las áreas e importa tags).
- Cada usuario puede cambiar su contraseña desde la última opción del menú de tres rayas. El administrador puede eliminar usuarios aunque tengan hallazgos: los hallazgos se conservan con el nombre que tenía.
- Un usuario desactivado no puede ingresar; los cambios de rol y de estado se aplican al instante.
- Las plantillas HTML están dentro de `tpl.py`.
- Para cambiar la lista de áreas hay que editar `AREAS` al inicio de `app.py`.
- Importar tags (solo administrador): Tags › *Importar planilla*. Acepta .xlsx o .csv con las columnas Tag, Descripción, Área, Zona y Protección Ex. Tiene un botón para revisar sin guardar y una planilla modelo descargable. Los tags que ya existen se actualizan.
- Desclasificaciones (menú › *Desclasificaciones*, todos los roles): registran el trabajo, el motivo, la fecha, el responsable, los tags afectados y las fotos del antes y del después. Una casilla permite cambiar la zona de esos tags a «Segura»; se guarda la zona anterior de cada uno.
- Las zonas posibles son 0, 1, 2, 20, 21, 22 y Segura (también en la importación de tags).
- Las fotos se comprimen para ocupar como máximo 300 KB cada una. En los formularios de hallazgos hay un botón para sacar la foto con la cámara del dispositivo y otro para elegir de la galería.
- Los tags genéricos (cajas de paso, luminarias, etc.) se cargan sin Área ni Zona; el técnico las elige en cada hallazgo. En los tags, la zona también puede ser 0/20, 1/21 o 2/22.
