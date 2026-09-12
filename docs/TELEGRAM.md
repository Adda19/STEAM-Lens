# Telegram: agente de preparación de sesiones

Actualización 2026-09-12. El usuario pidió sustituir la conexión de WhatsApp por Telegram tras las dificultades de registro. Esta ampliación agrega sesiones completas en PDF; la especificación original del MVP se mantiene como referencia histórica.

## Conexión

Bot validado por `getMe`: **@STEAM_Lens_bot**. La credencial se toma de `TELEGRAM_BOT_TOKEN` en `.env`, cargado por Django. No mostrarla ni incluirla en Git. La validación del token no acredita por sí sola una conversación completa ni entrega de PDF.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py telegram_bot --check
.\.venv\Scripts\python.exe manage.py telegram_bot
```

El proceso utiliza long polling: no requiere túnel ni URL pública. El PC debe permanecer encendido, conectado a Internet y con el proceso activo. Solo puede haber un consumidor del bot; un puerto local de guarda (18763) previene duplicados en este equipo. Si el bot tiene un webhook existente, se detiene sin borrarlo.

## Recorrido

1. La persona abre `https://t.me/STEAM_Lens_bot` y envía `/start`. El bot pregunta el idioma (es/en/fr) mediante botones antes de cualquier otra cosa; nada se interpreta con IA hasta elegirlo.
2. Escribe la edad de quien participa (un número entre 3 y 99; una respuesta con solo dígitos se procesa directo, sin llamar a la IA) y selecciona área, duración y materiales mediante botones. También puede escribir varios datos en una frase, en su idioma.
3. Envía foto, PDF con texto, TXT o una descripción del recurso. Si lo envía antes de completar el contexto, el agente conserva la referencia y pregunta lo que falta.
4. El bot pregunta si quiere agregar información de **sesiones anteriores** sobre ese mismo tema (qué se vio, qué costó más). Es opcional: con "No" se sigue de inmediato; con "Sí" pide un texto libre, que se usa para reforzar justo lo que costó sin repetir desde cero lo ya dominado. Se pregunta una sola vez por sesión.
5. El modelo diseña una sesión estructurada **con `Doc_Oficial/` como respaldo obligatorio**: busca la banda de edad correspondiente en `curriculo_internacional.json`, etiqueta 1-2 habilidades transversales de `core_skills_british_council.json` y aplica `aula_profile.json`/`profesor_profile.json` como contexto fijo de la demo cuando corresponde. El servidor valida el resultado, comprueba que la suma de fases coincida con la duración y genera el PDF en memoria.
6. El bot entrega el documento en el idioma elegido, con una sección final "Fuentes y trazabilidad": cita qué archivo de `Doc_Oficial` respaldó cada parte y, si para algo no encontró respaldo ahí, lo dice explícitamente en vez de bloquear la generación (usó conocimiento general del modelo: verificar antes de usar). El PDF cierra con "Recursos para profundizar" (ver abajo). La persona puede pedir cambios por texto y recibir una nueva versión.

Ejemplos: «8 años, ciencias naturales, 45 minutos, sin materiales»; «Tengo una planta para comparar sus hojas»; «Adáptala a 10 años»; «Hazla más práctica».

## Recursos adicionales en el PDF

Cada sesión cierra con al menos dos recursos de tipo distinto:

- **Video** y **documento**: el modelo nunca inventa un enlace específico (un video o PDF alucinado es peor que no ofrecer nada). En vez de eso, propone un tema de búsqueda preciso en el idioma elegido, y el servidor arma un enlace de **búsqueda real** (YouTube o Google) a partir de ese texto — siempre válido, nunca un enlace roto ni inventado. El PDF lo deja explícito: son búsquedas sugeridas, no un recurso verificado por STEAM Lens.
- **Simulación PhET** (opcional, solo si aplica): enlace directo a `phet.colorado.edu/{idioma}/simulations/<slug>`, elegido por el modelo únicamente de un catálogo cerrado en `lens/telegram/phet_catalog.py`. Ese catálogo es un borrador inicial (~15 simulaciones clásicas y estables) que **no se verificó contra el sitio en vivo** al construirlo; conviene revisarlo antes de confiar en él, igual que con `Doc_Oficial/`. El servidor además descarta en código cualquier slug que el modelo proponga fuera de ese catálogo, así que nunca llega un enlace inventado al PDF.

El comportamiento de agente está en `lesson.decide`: interpreta el mensaje, propone cambios de contexto y decide preguntar, generar, revisar o conversar. El servidor valida sus decisiones y ejecuta las herramientas. Los botones y la edad como número directo completan datos sin gastar llamadas de IA. El planificador recibe el estado vigente; no depende de un chat vacío en cada turno. La conversación de preparación de una clase puede incluir guía para quien la facilita; la misión web conserva su acompañamiento de indagación.

## Memoria del docente

A diferencia del contexto de conversación (expira tras 1 hora), la memoria vive en su propia tabla (`lens.models.TeacherMemory`) y persiste hasta que el propio docente borra algo. Está aislada por docente con la misma clave HMAC del chat, y **capada en 5 elementos combinados** (documentos de referencia + sesiones guardadas): al llegar al tope, el agente pide borrar uno antes de agregar otro — nunca reemplaza nada sin que el docente lo decida.

- `/memoria`, `/memory`, `/memoire`: lista lo guardado, numerado.
- `/memoria_borrar <n>`, `/memory_delete <n>`, `/memoire_supprimer <n>`: borra el elemento `n` de esa lista.
- `/memoria_guardar`, `/memory_save`, `/memoire_sauvegarder`: guarda la última sesión generada en la conversación actual.
- `/drive`: conecta una carpeta de Google Drive (ver abajo) e importa hasta el cupo disponible.

Cuando hay algo en la memoria, `lesson.generate` recibe un resumen (título + extracto) y lo usa **solo si coincide claramente** con el recurso o tema actual — nunca lo fuerza, y cuando lo usa lo cita en el PDF como "Memoria del docente: <título>". Es un aporte del propio docente, no una fuente validada por el equipo como `Doc_Oficial/`.

### Conectar Google Drive

El enlace de un docente y el callback de Google **no comparten proceso** (el bot corre en `manage.py telegram_bot`; el callback lo atiende el servidor web) — por eso el puente entre ambos (`lens.models.DriveConnectState`) es una fila de base de datos, no un caché en memoria, y expira a los 10 minutos.

Antes de que `/drive` funcione, hay que crear credenciales OAuth en Google Cloud Console (esto lo hace la persona dueña del proyecto de Google, no el agente):

1. https://console.cloud.google.com/ → crear o elegir un proyecto.
2. *APIs & Services → Library* → buscar **Google Drive API** → *Enable*.
3. *APIs & Services → OAuth consent screen* → tipo *External*, modo *Testing* alcanza para un piloto; agregar como *test user* los correos de quienes vayan a probar `/drive`.
4. *APIs & Services → Credentials → Create Credentials → OAuth client ID* → tipo **Web application**.
   - En *Authorized redirect URIs* agregar exactamente `http://127.0.0.1:8001/telegram/drive/callback` (Google permite `localhost`/`127.0.0.1` sin HTTPS para pruebas). Cuando haya hosting real con HTTPS, agregar también esa URL ahí y en `GOOGLE_OAUTH_REDIRECT_URI`.
5. Copiar el *Client ID* y el *Client secret* y ponerlos en `.env` (nunca en el chat ni en Git):
   ```
   GOOGLE_OAUTH_CLIENT_ID=...
   GOOGLE_OAUTH_CLIENT_SECRET=...
   GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8001/telegram/drive/callback
   ```
6. Validar con `manage.py check_google_drive` (solo revisa la configuración; la conexión real de un docente requiere abrir el enlace en un navegador).

**Limitación conocida:** como el proyecto aún corre en `127.0.0.1` sin hosting público (ver docs/RETOMA.md, pendiente #1), `/drive` solo funciona hoy si quien autoriza usa un navegador en la misma máquina donde corre el servidor — típicamente la persona que hace la demo. Un docente remoto podrá usarlo cuando haya una URL HTTPS pública; el resto del bot (Telegram) no tiene esa limitación porque usa long polling, no un webhook.

## Doc_Oficial: documentación interna siempre consultada

`Doc_Oficial/` contiene JSON validados por el equipo (no por la IA) que el agente **siempre** carga antes de diseñar una sesión: `curriculo_internacional.json` (bandas de edad CSTA/DigComp/UNESCO), `core_skills_british_council.json` (habilidades transversales), `aula_profile.json` y `profesor_profile.json` (aula y docente de la demo) e `historial_clases.json` (continuidad de un grupo de referencia, se usa solo si el tema coincide). El cargador (`lens/doc_oficial.py`) lee cualquier `*.json` que exista en la carpeta, así que agregar más archivos no requiere cambios de código. El modelo cita en el PDF exactamente qué documento respaldó cada parte de la sesión; nunca se pide a la IA que valide o corrija ese contenido, solo que lo use y lo referencie.

## Comandos

Cada comando acepta su forma en español, inglés y francés:

- `/start` / `/nueva`, `/new`, `/nouvelle`: nueva sesión.
- `/idioma`, `/language`, `/langue`: cambiar de idioma sin perder el resto del contexto.
- `/continuar`, `/continue`, `/continuer`: recuperar el siguiente paso o volver a generar con el recurso conservado.
- `/pdf`: reenviar la última versión sin otra llamada de IA.
- `/borrar`, `/delete`, `/effacer`: eliminar el estado local de ese chat; no elimina mensajes en Telegram.
- `/ayuda`, `/help`, `/aide`: mostrar el siguiente paso.
- `/memoria`, `/memory`, `/memoire`: listar la memoria persistente del docente.
- `/memoria_borrar <n>`, `/memory_delete <n>`, `/memoire_supprimer <n>`: borrar el elemento `n` de esa lista.
- `/memoria_guardar`, `/memory_save`, `/memoire_sauvegarder`: guardar la última sesión generada en la memoria.
- `/drive`: conectar una carpeta de Google Drive e importarla a la memoria (ver arriba).

## Archivos y datos

- Recursos hasta 5 MB: JPEG/PNG/WebP, PDF con texto seleccionable hasta 20 páginas/20.000 caracteres o TXT UTF-8 hasta 20.000 caracteres. Los PDF escaneados se sustituyen por una foto de la página relevante. No se descargan enlaces arbitrarios; se solicita contenido.
- Imágenes, archivos y PDF de salida se procesan en memoria. La sesión guarda identificadores de archivo de Telegram, contexto, recurso textual cuando aplica y la sesión generada; no guarda los bytes de la foto.
- Las conversaciones privadas están separadas mediante claves HMAC derivadas del chat. No se guardan nombres, teléfonos ni perfiles. Telegram utiliza identificadores para enrutar los mensajes. Los grupos se ignoran.
- El estado local vence tras una hora de inactividad. Ejecutar `manage.py clearsessions` para borrar físicamente filas vencidas. Telegram conserva los mensajes conforme a su política; OpenAI recibe el contenido para generar la sesión. Estas llamadas usan `store=False`, que no equivale a garantía universal de retención cero.
- Excepción a lo anterior: la memoria del docente (`TeacherMemory`, `TeacherDriveConnection`) **no** expira en 1 hora; vive hasta que el docente la borra con `/memoria_borrar`. El refresh token de Drive nunca se envía a OpenAI ni aparece en un mensaje de Telegram.
- `.runtime/telegram_offset.txt` conserva el punto de lectura, sin mensajes ni token. Los IDs de actualización por chat evitan reprocesamiento normal. Un fallo de red justo después del envío puede dejar entrega incierta: usar `/pdf` para recuperación. No se promete entrega exactamente una vez.
- El MVP procesa turnos secuencialmente; una generación demora la atención de otros chats. Para múltiples aulas se requiere cola por conversación, límites y supervisión. Actualmente cualquier persona que inicie el bot privado puede consumir llamadas de IA: no difundir públicamente fuera de la demo sin añadir controles de uso.

## Pruebas

```powershell
.\.venv\Scripts\python.exe manage.py test lens.tests
.\.venv\Scripts\python.exe manage.py check_telegram_lesson
```

La primera usa dobles de Telegram/OpenAI e inspección de PDF. La segunda hace una llamada real con un recurso textual de prueba y guarda `artifacts/sesion_telegram_prueba.pdf`; no envía mensajes a Telegram. La prueba final requiere conversación real iniciada por la usuaria y recepción del documento en su chat.

Fuentes: [Telegram Bot API](https://core.telegram.org/bots/api), [creación del bot](https://core.telegram.org/bots/tutorial), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
