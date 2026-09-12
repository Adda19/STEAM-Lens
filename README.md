# STEAM Lens

**El mundo es tu laboratorio. / The world is your laboratory.**

🌐 **En vivo / Live:** https://steamlens.soymaker.tech/
🤖 **Bot de Telegram / Telegram bot:** https://t.me/STEAM_Lens_bot
Make with/Hecho con **Codex**

[🇪🇸 Español](#español) · [🇬🇧 English](#english)

---

## Español

### ¿Qué es?

STEAM Lens es un asistente de IA para docentes y curiosos que convierte un tema, una foto o un documento en una **sesión STEAM completa y lista para usar**, entregada como PDF por Telegram, más una experiencia web complementaria donde cualquier persona explora un objeto cotidiano con la cámara y recibe una misión guiada por preguntas.

No es un generador genérico de texto: cada sesión se diseña con **respaldo pedagógico verificable** (currículo internacional por banda de edad, habilidades transversales, contexto real de aula) y nunca inventa un enlace, un video o una fuente — cuando no encuentra respaldo, lo dice explícitamente en vez de fingir que sí lo tiene.

### Por qué vale la pena probarlo

- **Agente conversacional real, no un formulario**: en Telegram se puede escribir en lenguaje natural ("hazla de 30 minutos", "adáptala a 6 años", "más práctica") y el agente decide si preguntar, generar, revisar o simplemente conversar — sin gastar una llamada de IA en los pasos que ya se pueden resolver con botones o texto directo (la edad como número, por ejemplo).
- **Grounding real, no relleno**: antes de diseñar cualquier sesión, el agente consulta `Doc_Oficial/` — un conjunto de JSON validados por humanos (currículo internacional CSTA/DigComp/UNESCO por banda de edad, marco de habilidades transversales del British Council, perfil de aula y de docente, historial de clases) — y **cita exactamente qué documento respaldó cada parte** de la sesión en el PDF final. Si para algo no encontró respaldo, lo dice ("conocimiento general, verificar antes de usar") en vez de generar una alucinación silenciosa.
- **Tres idiomas de verdad**: español, inglés y francés, elegidos al inicio de la conversación y aplicados a cada mensaje, botón y al PDF completo (incluyendo encabezados, evaluación, adaptaciones, fuentes).
- **Diseñado por edad, no por curso**: la edad (3–99 años) es el dato central, alineado con cómo los marcos curriculares internacionales realmente organizan el contenido (por banda de edad, no por "grado" de un sistema escolar específico).
- **Cada sesión trae recursos adicionales verificables**: un video y un documento sugeridos (el modelo nunca inventa una URL específica; el servidor arma un enlace de búsqueda real a partir del tema) y, cuando aplica, una simulación interactiva real de PhET.
- **Memoria persistente por docente**: hasta 5 elementos (documentos de referencia o sesiones ya generadas) que sobreviven entre conversaciones, con importación opcional desde una carpeta de Google Drive propia.
- **Refuerza aprendizaje previo**: antes de generar, el agente puede preguntar qué se vio en sesiones anteriores sobre el mismo tema, para no repetir lo ya dominado.
- **Seguridad y límites explícitos en cada prompt**: nunca actividades con fuego, corriente eléctrica, químicos peligrosos o herramientas riesgosas; nunca se piden ni infieren datos personales; los recursos se validan por tamaño, formato y contenido antes de procesarse.

### Qué probar ahora mismo

1. Abre **https://t.me/STEAM_Lens_bot** en Telegram y escribe `/start`.
2. Elige idioma, escribe una edad (ej. `9`), elige área y duración, marca materiales.
3. Cuando pida el recurso, describe un tema (ej. *"quiero enseñar el ciclo del agua"*) o envía una foto/PDF/TXT.
4. Responde si quieres agregar sesiones anteriores (o di que no).
5. Recibe el PDF: revisa la sección **"Fuentes y trazabilidad"** y **"Recursos para profundizar"** al final — ahí se ve el respaldo real y los recursos sugeridos.
6. Pide un ajuste por texto (ej. *"hazla más práctica"*) y compara la nueva versión.
7. Explora también la web en **https://steamlens.soymaker.tech/**: fotografía un objeto y recibe una misión guiada.

### Cómo funciona (arquitectura)

- **Backend**: Django 5 + SQLite. Un solo repositorio sirve la web (misión con cámara) y el bot de Telegram (proceso independiente por long polling, sin necesidad de webhook ni URL pública).
- **IA**: OpenAI Responses API con *Structured Outputs* (Pydantic) — cada respuesta del modelo se valida contra un esquema estricto antes de usarse; nunca se confía en texto libre para datos críticos.
- **Doc_Oficial**: carpeta de JSON validados por el equipo, cargados automáticamente en cada generación (`lens/doc_oficial.py`); agregar un archivo nuevo no requiere tocar código.
- **Memoria del docente**: modelo propio de base de datos (`lens/models.py`), independiente del estado de conversación (que expira en 1 hora); capada en 5 elementos para mantener la idea de "lo esencial", con importación opcional vía OAuth de Google Drive de solo lectura.
- **PDF**: generado en memoria con ReportLab, localizado en los tres idiomas.
- **Despliegue**: Ubuntu + nginx (proxy inverso y HTTPS con Let's Encrypt) + dos servicios `systemd` independientes (web y bot), cada uno con reinicio automático.


### Correrlo localmente

Instrucciones completas y comandos de prueba en [`docs/OPERACION.md`](docs/OPERACION.md) (web) y [`docs/TELEGRAM.md`](docs/TELEGRAM.md) (bot, incluyendo cómo conectar Google Drive). En resumen:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=4 config.wsgi:application
# En otra terminal, para el bot:
.\.venv\Scripts\python.exe manage.py telegram_bot
```

Requiere `OPENAI_API_KEY` y `TELEGRAM_BOT_TOKEN` en `.env` (ver `.env.example`); `GOOGLE_OAUTH_*` es opcional, solo para `/drive`.

### Documentos adicionales

- [Especificación original del MVP](STEAM%20Lens%20%E2%80%94%20Especificaci%C3%B3n%20del%20MVP%20para%20Hackathon.md)
- [Operación (web)](docs/OPERACION.md) · [Telegram (bot, Doc_Oficial, memoria, Drive)](docs/TELEGRAM.md) · [Bitácora de decisiones](docs/RETOMA.md)

---

## English

### What it is

STEAM Lens is an AI teaching assistant that turns a topic, a photo, or a document into a **complete, ready-to-teach STEAM lesson**, delivered as a PDF over Telegram, plus a companion web experience where anyone explores an everyday object with a camera and gets a question-driven guided mission.

It isn't a generic text generator: every lesson is designed with **verifiable pedagogical grounding** (international curriculum by age band, transversal core skills, real classroom context) and never fabricates a link, video, or source — when it can't find grounding, it says so explicitly instead of pretending it did.

### Why it's worth testing

- **A real conversational agent, not a form**: in Telegram you can write in natural language ("make it 30 minutes", "adapt it for age 6", "more hands-on") and the agent decides whether to ask, generate, revise, or just talk — without spending an AI call on steps that a button or a bare number can resolve directly (age, for instance).
- **Real grounding, not filler**: before designing any lesson, the agent consults `Doc_Oficial/` — a set of human-validated JSON files (international curriculum by age band aligned to CSTA/DigComp/UNESCO, the British Council transversal-skills framework, a classroom and teacher profile, class history) — and **cites exactly which document backed each part** of the lesson in the final PDF. When something isn't grounded, it says so ("general knowledge, verify before use") instead of silently hallucinating.
- **Genuinely trilingual**: Spanish, English, and French, chosen at the start of the conversation and applied to every message, button, and the entire PDF (headings, assessment, adaptations, sources included).
- **Designed by age, not by school grade**: age (3–99) is the core input, matching how international curriculum frameworks actually organize content (by age band, not by one country's grade system).
- **Every lesson ships with verifiable extra resources**: a suggested video and document (the model never invents a specific URL; the server builds a real search link from the topic) and, when it applies, a genuine interactive PhET simulation.
- **Persistent per-teacher memory**: up to 5 items (reference documents or previously generated lessons) that survive across conversations, with optional import from the teacher's own Google Drive folder.
- **Reinforces prior learning**: before generating, the agent can ask what was covered in earlier sessions on the same topic, so it doesn't re-teach what's already mastered.
- **Explicit safety limits baked into every prompt**: never fire, mains electricity, hazardous chemicals or risky tools; never personal data requested or inferred; uploaded resources are validated for size, format and content before processing.

### What to try right now

1. Open **https://t.me/STEAM_Lens_bot** on Telegram and send `/start`.
2. Choose a language, type an age (e.g. `9`), pick a subject and duration, check materials.
3. When asked for a resource, describe a topic (e.g. *"I want to teach the water cycle"*) or send a photo/PDF/TXT.
4. Answer whether you want to add info from previous sessions (or say no).
5. Get the PDF: check the **"Sources and traceability"** and **"Resources to go further"** sections at the end — that's where the real grounding and suggested resources live.
6. Ask for a change by text (e.g. *"make it more hands-on"*) and compare the new version.
7. Also try the web experience at **https://steamlens.soymaker.tech/**: photograph an object and get a guided mission.

### How it works (architecture)

- **Backend**: Django 5 + SQLite. One repository serves both the web camera-mission experience and the Telegram bot (an independent long-polling process — no webhook or public URL required for the bot itself).
- **AI**: OpenAI Responses API with Structured Outputs (Pydantic) — every model response is validated against a strict schema before use; free text is never trusted for critical data.
- **Doc_Oficial**: a folder of team-validated JSON files, loaded automatically on every generation (`lens/doc_oficial.py`); dropping in a new file needs no code change.
- **Teacher memory**: its own database model (`lens/models.py`), independent of conversation state (which expires after 1 hour); capped at 5 items on purpose, with optional read-only Google Drive OAuth import.
- **PDF**: generated in memory with ReportLab, localized in all three languages.
- **Deployment**: Ubuntu + nginx (reverse proxy and HTTPS via Let's Encrypt) + two independent `systemd` services (web and bot), each with automatic restart.



```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=4 config.wsgi:application
# In another terminal, for the bot:
.\.venv\Scripts\python.exe manage.py telegram_bot
```

Requires `OPENAI_API_KEY` and `TELEGRAM_BOT_TOKEN` in `.env` (see `.env.example`); `GOOGLE_OAUTH_*` is optional, only needed for `/drive`.
