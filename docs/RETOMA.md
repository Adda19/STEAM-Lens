# Retomar STEAM Lens

Actualización: implementación de preparación previa al evento. La fecha de sesión es 2026-09-11. Las reglas de la hackathon siguen pendientes.

## Estado verificable

La especificación original se conserva intacta. Ya existen aplicación Django, cuatro pantallas, integración real con Responses API, schemas estrictos, cámara, carga de respaldo, coach, reinicio, documentación y pruebas.

Servidor iniciado en esta sesión: **http://127.0.0.1:8001/**, Waitress en un proceso con cuatro hilos. Si no responde, arrancar con los comandos de [Operación](OPERACION.md). No se publicó una URL externa.

Entorno: Python 3.12.1, Django 5.2.17, OpenAI SDK 2.54.0, Pydantic 2.13.5, Pillow 12.3.0. Dependencias de ejecución fijadas en `requirements.lock.txt`; Playwright 1.62.0 es solo para pruebas de navegador.

La usuaria confirmó que usará una clave propia. Se detectó una clave en el entorno y se validó con éxito, sin mostrarla ni copiarla a archivos. `.env` fue creado con un secreto Django aleatorio y campo de OpenAI vacío: la variable del entorno tiene prioridad.

## Evidencia de validación

| Comprobación | Resultado y límites |
| --- | --- |
| `manage.py check` | Sin incidencias |
| Migraciones | Contenttypes y sesiones aplicadas en SQLite local |
| `manage.py test lens.tests --verbosity 2` | 14 pruebas aprobadas; usan dobles del proveedor, sin consumo de API |
| `node --check` para ambos JS | Sintaxis válida |
| `collectstatic --noinput` | Archivos estáticos preparados para WhiteNoise |
| `manage.py check_openai` | Conexión y salida estructurada reales aprobadas con `gpt-5.6-terra` |
| `scripts/browser_check.py` | Edge sin ventana: inicio escritorio, 390 px móvil, preferencias, cámara rechazada, carga, descubrimiento, misión sin segunda llamada, coach y reinicio; sin errores JS ni desbordamiento horizontal. Respuestas IA simuladas solo en esta prueba |
| `scripts/live_flow_check.py` | Análisis multimodal real + turno real con continuidad + reinicio aprobados. Entrada: ilustración CSS propia, no foto física. Análisis 7,94 s; coach 3,28 s en una ejecución |
| Revisión visual | Capturas de inicio escritorio y misión móvil inspeccionadas |

Los tiempos son una muestra, no una garantía ni una estimación de costo. La salida real se encuentra en `artifacts/live-flow-result.json`. Tras revisarla se precisó el prompt del coach: feedback sin pistas duplicadas y una tarea cognitiva por pregunta. Esa redacción refinada necesita ensayo pedagógico adicional con objetos reales.

## Decisiones implementadas

- Captura inválida: objeto/misión nulos y conexiones vacías; confianza baja solicita reintento.
- “Sin materiales” es exclusivo. Edad, tiempo, materiales, formato y tamaño se revalidan en servidor.
- La misión se genera junto al análisis y se revela localmente. Los criterios de éxito permanecen en servidor.
- Modelo configurable; prompts y schemas separados de las vistas. Cámara y coach comparten un JS para este MVP.
- `previous_response_id` y `store=True`; se reenvía el rol pedagógico. La interfaz informa del envío a OpenAI y su tratamiento externo. No se promete retención cero.
- Reiniciar borra misión, resultado, continuidad y estado terminal del coach, conservando preferencias. Cámara y blob se liberan.
- Se agregó `coach_status` a la sesión para evitar continuar una misión terminada. No hay modelos de dominio adicionales.
- Un proceso Waitress con coordinación por sesión; antes de escalar procesos se requiere coordinación compartida.

## Pendientes reales antes de presentar

1. Elegir alojamiento o acceso HTTPS y configurar hosts/CSRF/proxy. No existe aún URL móvil pública.
2. Probar cámara trasera física en el teléfono que se usará mañana; la emulación no la sustituye.
3. Ensayar planta real y varios objetos, edades 6/18, ausencia de materiales y tiempos cortos. Revisar exactitud, seguridad y progresión de pistas.
4. Medir varias ejecuciones en la red de presentación y preparar foto propia de respaldo.
5. Aplicar configuración de producción del host y comprobar `check --deploy` antes de exposición pública.
6. Recibir reglas del evento: tema, rúbrica, entregables, servicios obligatorios y admisión de trabajo previo.

La base está implementada y validada localmente. La Definition of Done del documento exige el recorrido físico desde un teléfono por HTTPS, por lo que esa aceptación final sigue pendiente.

## Incorporar las reglas mañana

Guardar las indicaciones exactas en `docs/REGLAS_HACKATHON.md` cuando existan. Compararlas con el recorrido antes de cambiar código. Registrar qué requisito sustituyen, archivos afectados y verificación. Las nuevas instrucciones de la usuaria tienen prioridad.

| Fecha | Instrucción | Cambio | Validación |
| --- | --- | --- | --- |
| Preparación inicial | Analizar primero y documentar | README, análisis y plan; fuente intacta | Lectura y contraste de documentación |
| Construcción | “hagamoslo” | MVP Django completo y documentación de operación | Pruebas de servidor, navegador y API real descritas arriba |

## Para continuar en otra sesión

> Trabajamos en E:\STEAM_Lens. Lee README.md, docs/OPERACION.md y docs/RETOMA.md; consulta la especificación y el análisis cuando sea necesario. Ya hay código y pruebas: no reconstruyas desde cero. Arranca en 8001 y verifica el estado actual. La clave proviene del entorno; no imprimirla. El siguiente trabajo es ensayo físico por HTTPS y adaptación a reglas del evento. Mantén cámara → STEAM → misión → coach, sin ampliar alcance con cuentas, hardware conectado o AR. Actualiza pruebas, límites y próximos pasos con evidencia real.

Validación adicional: scripts/camera_check.py aprobado con cámara simulada de Edge: getUserMedia, preview, captura JPEG de un frame, liberación de tracks y opción de recaptura. Sigue pendiente cámara física por HTTPS.

## Actualización 2026-09-12: Telegram
Se sustituyó WhatsApp por Telegram por petición de la usuaria. Token validado mediante getMe: @STEAM_Lens_bot. Implementados botones de grado/área/duración/materiales, interpretación de texto mediante IA, recursos de imagen/PDF/TXT/texto, sesión estructurada, PDF en memoria y revisiones. 24 pruebas locales aprobadas. Detalles y comandos: TELEGRAM.md. La entrega real al chat se confirma por separado; no confundir validación del token con conversación completa.


Validación real de Telegram/PDF: check_telegram_lesson aprobado con OpenAI; PDF de 4 páginas, duración total 45 minutos, generación 27,2 segundos. Archivo de ensayo: artifacts/sesion_telegram_prueba.pdf. Bot iniciado por long polling y getMe validado. Pendiente confirmación de la usuaria sobre recepción y recorrido completo en su chat.

## Actualización 2026-09-12: edad en vez de grado, tres idiomas y Doc_Oficial

Se reemplazó "grado/curso" por edad (3 a 99 años) como dato de contexto, en el formulario web (`lens/context.py`, `lens/views.py`, plantilla e index.html/setup.js/experience.js) y en el bot de Telegram, porque `Doc_Oficial/curriculo_internacional.json` organiza el currículo por banda de edad, no por grado escolar. El bot de Telegram ahora pregunta idioma (es/en/fr) antes que cualquier otro dato, usando `lens/telegram/i18n.py` (que ya existía escrito pero no estaba conectado a `agent.py`/`lesson.py`); un número suelto respondiendo la edad se procesa sin llamar a la IA.

Se creó `lens/doc_oficial.py`: carga automáticamente cualquier `*.json` de `Doc_Oficial/` (hoy 5 archivos: aula, profesor, currículo internacional, core skills British Council e historial de clases) y busca la banda de edad correspondiente. El agente lo consulta siempre al generar una sesión, cita en el PDF (sección "Fuentes y trazabilidad") qué documento respaldó cada parte, etiqueta 1-2 habilidades transversales del catálogo, y cuando algo no tiene respaldo en `Doc_Oficial` lo señala explícitamente en vez de bloquear la generación. `Doc_Oficial` se trata como ya validado por el equipo: el agente lo usa y lo cita, no lo cuestiona.

Se eliminó `scripts/adapt_educational_context.py` (script de una sola vez que migraba de edad a grado; ejecutarlo ahora habría revertido este cambio). Se actualizaron `scripts/live_flow_check.py` y los tests (`test_context.py`, `test_flow.py`, `test_telegram.py`) al nuevo esquema. 29 pruebas locales aprobadas (sin costo de API) más una llamada real (`check_telegram_lesson`) que confirmó edad, banda curricular, habilidades transversales y cita de fuentes en el PDF resultante. Detalles y comandos multilenguaje: TELEGRAM.md.

## Actualización 2026-09-12 (continuación): sesiones previas y recursos adicionales en el PDF

Se agregaron dos mejoras pedidas explícitamente por la usuaria:

1. **Sesiones previas**: antes de generar (una sola vez por sesión), el bot pregunta si quiere agregar información de clases anteriores sobre el mismo tema. Es opcional (botones Sí/No); si responde Sí, el texto libre que escriba se guarda tal cual (sin llamar a la IA para capturarlo, igual que la edad) y se envía al modelo para reforzar justo lo que costó, sin repetir lo ya dominado, citando "Sesión previa reportada por el docente" en las fuentes.
2. **Recursos al final del PDF** (`Lesson.external_resources`, mínimo un video y un documento, más una simulación PhET opcional "si aplica"): se decidió que el modelo **nunca** genere una URL de video o documento específica — un enlace inventado es peor que no ofrecer nada, y ya existía la regla "sin URLs inventadas" en el proyecto. En su lugar, el modelo solo propone un tema de búsqueda y el servidor arma un enlace de búsqueda real (YouTube/Google), garantizado válido. Para PhET se creó `lens/telegram/phet_catalog.py`, un catálogo cerrado (~15 slugs) del que el modelo solo puede elegir, con doble validación: el modelo recibe la lista exacta, y el servidor además descarta cualquier slug fuera de catálogo antes de armar el PDF. Ese catálogo **no se verificó contra el sitio en vivo** (no hubo acceso a navegador ni a la web en el momento de construirlo): queda marcado en el propio archivo como pendiente de revisión, igual que los archivos de `Doc_Oficial/`.

31 pruebas locales aprobadas (dobles, sin costo de API); no se repitió la llamada real a OpenAI para esta segunda tanda de cambios, a petición de la usuaria.

## Actualización 2026-09-12 (continuación): memoria del docente con Google Drive

Se agregó memoria persistente por docente, capada en 5 elementos combinados (documentos de referencia + sesiones guardadas); al llegar al tope el agente pide borrar uno antes de agregar otro (decisión explícita de la usuaria, no reemplazo automático). Se creó el primer modelo de base de datos del proyecto (`lens/models.py`: `TeacherMemory`, `TeacherDriveConnection`, `DriveConnectState`, migración `lens/migrations/0001_initial.py`) porque el estado de conversación existente (`django.contrib.sessions`) expira en 1 hora y no sirve para algo que debe durar días.

Comandos nuevos en Telegram (con alias es/en/fr): `/memoria`, `/memoria_borrar <n>`, `/memoria_guardar`, y `/drive` para conectar Google Drive. `lesson.generate` recibe un resumen de la memoria y la usa solo si coincide con el recurso actual, citando "Memoria del docente: <título>" — igual que `Doc_Oficial` y `previous_sessions`, nunca bloquea la generación.

**Drive requiere una credencial OAuth que la usuaria debe crear en Google Cloud Console** (el agente no puede hacerlo por ella): proyecto, Drive API habilitada, pantalla de consentimiento y client ID/secret tipo "Web application" con `http://127.0.0.1:8001/telegram/drive/callback` como redirect URI autorizado. Pasos exactos en TELEGRAM.md. Se agregó `manage.py check_google_drive` para validar la configuración (no prueba una conexión real, eso exige un navegador). Limitación real y documentada: como el bot de Telegram (proceso propio, long polling) y el callback OAuth (servidor web) no comparten memoria de proceso, el puente entre ambos es una fila de base de datos (`DriveConnectState`, expira en 10 min) en vez de un caché; y como no hay hosting HTTPS público todavía (pendiente #1 de este documento), `/drive` solo puede autorizarlo alguien con navegador en la misma máquina que el servidor — un docente remoto lo podrá usar cuando exista esa URL pública.

Dependencias nuevas: `google-auth`, `google-auth-oauthlib`, `google-api-python-client` (agregadas a `requirements.txt`/`requirements.lock.txt`). 45 pruebas locales aprobadas (dobles; las llamadas a la API de Drive están mockeadas, nunca se probó contra Google real por falta de credenciales en esta sesión).

Pendiente explícito (fuera de alcance de esta entrega): los otros dos agentes que la usuaria pidió — revisor de currículo planeado y simulador de estudiante para validar dificultad — quedan para una siguiente sesión, junto con el menú de `/start` que elegirá entre los tres modos.

