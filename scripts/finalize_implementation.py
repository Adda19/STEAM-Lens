from pathlib import Path

root = Path(__file__).resolve().parent.parent
coach = root / "lens/prompts/coach.py"
text = coach.read_text(encoding="utf-8")
text = text.replace("Trabaja una decisión a la vez.", "Trabaja una decisión a la vez. feedback solo valora la respuesta: no incluyas allí pistas.\n+Toda ayuda conceptual va exclusivamente en hint. next_question pide una sola tarea cognitiva;\n+no combines 'cómo se llama y qué hace' ni dos decisiones en una misma pregunta.".replace("\n+", "\n"))
coach.write_text(text, encoding="utf-8")
lock = root / "requirements.lock.txt"
lines = lock.read_text(encoding="utf-8-sig").splitlines()
lock.write_text("\n".join(line for line in lines if not line.lower().startswith(("playwright==", "greenlet==", "pyee=="))) + "\n", encoding="utf-8")

(root / "docs/RETOMA.md").write_text('''# Retomar STEAM Lens

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

> Trabajamos en E:\\STEAM_Lens. Lee README.md, docs/OPERACION.md y docs/RETOMA.md; consulta la especificación y el análisis cuando sea necesario. Ya hay código y pruebas: no reconstruyas desde cero. Arranca en 8001 y verifica el estado actual. La clave proviene del entorno; no imprimirla. El siguiente trabajo es ensayo físico por HTTPS y adaptación a reglas del evento. Mantén cámara → STEAM → misión → coach, sin ampliar alcance con cuentas, hardware conectado o AR. Actualiza pruebas, límites y próximos pasos con evidencia real.
''', encoding="utf-8")
print("Implementation status and runtime lock updated.")
