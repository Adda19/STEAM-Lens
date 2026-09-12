# Análisis del MVP

Fecha: 2026-09-11. Base: especificación original, secciones 0–30. Estado histórico: análisis previo a la construcción. La implementación posterior y sus resultados están en OPERACION.md y RETOMA.md; las frases de trabajo pendiente en este análisis describen aquel momento.

## Evaluación

El alcance es coherente para un prototipo de hackathon: cuatro pantallas, una llamada inicial y turnos breves de acompañamiento. Su viabilidad depende de validar pronto la cámara en teléfono, el acceso real al modelo y la calidad de las misiones. No se ha medido latencia ni costo, por lo que no puede prometerse todavía una demo rápida o estable.

El valor a demostrar es la transición desde un objeto real hacia el razonamiento del estudiante. Reconocer una planta es solo el inicio: el momento decisivo de la demo será que el coach responda a una idea incompleta con una pista útil y una sola pregunta.

Conviene estabilizar hoy el recorrido, los contratos de datos y la separación entre interfaz, instrucciones pedagógicas e integración de IA. El tema específico, la rúbrica, los servicios exigidos y el formato del pitch deben poder ajustarse mañana sin rehacer la aplicación.

## Puntos que requieren precisión

| Punto de la especificación | Riesgo | Resolución propuesta para implementar |
| --- | --- | --- |
| Modelo `gpt-5.6-terra` (§10) | La documentación no demuestra acceso de esta cuenta | Conservar el valor configurable y hacer una prueba real con imagen y schema antes de construir todo el flujo |
| Foto inválida y 2–5 conexiones (§12) | Forzar campos educativos puede producir contenido inventado | Todas las claves presentes; permitir objeto y misión nulos, conexiones vacías y mensaje de reintento cuando la captura sea inválida; exigir 2–5 conexiones solo en resultados válidos |
| Confianza baja (§20) | Mostrar una misión sobre un objeto incierto | El backend convierte confianza baja en reintento y no habilita misión ni coach |
| Material genérico “Sensores” (§6, §25) | Presuponer un sensor de humedad que no existe | Proponer observar/diseñar; el coach puede preguntar qué sensor tiene antes de indicar una construcción concreta, sin añadir inventario |
| “Sin materiales” junto con otros materiales | Contexto contradictorio | Selección exclusiva; backend rechaza combinaciones contradictorias |
| Sin materiales, pero dibujo o medición | Presuponer papel, lápiz o regla | Ofrecer observación, comparación o conteo sin herramientas; otros objetos cotidianos solo como alternativas |
| Actividad de 10–30 minutos | Confundir observar crecimiento con completar una misión corta | Acotar el logro al tiempo elegido: diseñar una medición es distinto de esperar que crezca una planta |
| `completed` en coach (§13) | Hacer otra pregunta innecesaria o afirmar éxito físico sin evidencia | Permitir `next_question = null`; celebrar el objetivo de razonamiento demostrado o lo reportado por el estudiante, sin afirmar verificación visual |
| `blocked` en coach (§13) | Dejar al estudiante atrapado | Definirlo como imposibilidad segura de continuar; explicación breve y opción de explorar otro objeto |
| Primera pregunta dentro de `mission` (§12) | Mostrar criterios internos que revelan la respuesta | Mostrar `first_question`; mantener `success_criteria` en servidor, fuera de la presentación del reto |
| Cuatro pantallas y dos rutas GET (§7, §16) | Crear rutas y estados duplicados | Inicio en `/`; cámara, descubrimiento y misión como estados de `/explore/` |
| Reiniciar (§16–17) | Arrastrar respuestas de un objeto anterior | Borrar resultado, misión y respuesta de OpenAI; conservar preferencias para otra captura. Cambio de contexto desde Inicio |

Son precisiones propuestas; la especificación original permanece intacta. Validarlas al escribir los schemas y documentar cualquier ajuste real.

## OpenAI: contraste con fuentes oficiales

La ficha de GPT-5.6 Terra indica entrada de imágenes, Responses API y Structured Outputs. El modelo de la especificación es compatible sobre el papel. Falta comprobar acceso y comportamiento con las credenciales del proyecto. [Ficha oficial del modelo](https://developers.openai.com/api/docs/models/gpt-5.6-terra).

Structured Outputs requiere un schema compatible: campos requeridos, propiedades adicionales deshabilitadas y nulabilidad explícita donde corresponda. Además del formato, el backend debe comprobar reglas de negocio y manejar rechazos o respuestas incompletas. Un JSON válido no garantiza una misión pedagógicamente correcta. [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

La continuidad mediante `previous_response_id` encadena turnos. No equivale a un historial gratuito: el contexto previo puede seguir contabilizándose como entrada. Mantener turnos cortos y medir uso durante los ensayos. [Estado de conversación](https://developers.openai.com/api/docs/guides/conversation-state).

Hay que distinguir no guardar fotos en Django de la retención del proveedor. La documentación indica retención de estado de Responses de 30 días por defecto o con `store=true`, con excepciones, y controles separados para monitoreo de abuso. No prometer eliminación inmediata de extremo a extremo ni asumir que `store=false` ofrece por sí solo retención cero. [Controles de datos](https://developers.openai.com/api/docs/guides/your-data).

Decisión pendiente antes de la integración: mantener el encadenamiento requerido por la especificación y describir con precisión el tratamiento externo de datos. Si las reglas de mañana exigen ausencia de estado en el proveedor, revisar esa estrategia y el manejo del contexto; sería un cambio explícito respecto de §11. Borrar la sesión local no borra automáticamente el estado externo.

## Base técnica adaptable

Usar la estructura propuesta en §23 directamente en esta carpeta, evitando una carpeta raíz duplicada. Mantener una sola app Django `lens`.

| Componente previsto | Responsabilidad | Qué permite cambiar mañana |
| --- | --- | --- |
| `config/settings.py` y `.env.example` | Entorno, modelo, credenciales, hosts, límites | Modelo y despliegue sin cambiar vistas |
| `lens/services/openai_service.py` | Solicitudes, parsing, errores del proveedor | Parámetros o integración sin reescribir la UI |
| `lens/prompts/` | Analizador y rol pedagógico enviados en cada turno | Tema, vocabulario y criterios educativos |
| `lens/schemas/` | Contratos de análisis y coach | Cambios controlados de estructura |
| `lens/views.py` | Validación de entrada, sesión y respuesta HTTP | Flujo de aplicación independiente del prompt |
| `lens/templates/lens/` | Cuatro pantallas y mensajes | Pitch, textos y presentación |
| `static/js/camera.js` | Permisos, captura, compresión, galería y liberación de cámara | Ajustes de dispositivo |
| `static/js/coach.js` | Envío de respuesta y representación de turnos | Interacción pedagógica |
| `static/css/` | Colores, tipografía y espaciado centralizados | Identidad visual sin alterar lógica |

CSS propio es suficiente para la primera versión; evita introducir una cadena de compilación solo por estilo. Las cadenas visibles deben quedar agrupadas por responsabilidad para facilitar traducción futura, sin implementar varios idiomas ahora.

La flexibilidad necesaria son estos límites entre archivos, no una arquitectura de plugins ni varios proveedores implementados de antemano.

## Contrato del flujo propuesto

1. Inicio valida edad entera entre 6 y 18, materiales de la lista y tiempo 10/20/30. Las preferencias pasan a Explorar temporalmente en el navegador y se envían con la foto; el servidor las valida de nuevo.
2. Explorar prioriza cámara trasera. La carga de fotografía es respaldo del MVP. Capturar detiene los tracks de cámara y conserva la foto local mientras dure la experiencia.
3. `/api/analyze/` recibe multipart con imagen y contexto. Valida archivo real, dimensiones y tamaño, ejecuta una llamada, valida el resultado y guarda únicamente datos estructurados en sesión.
4. Descubrimiento recibe solo campos destinados a presentación. La misión ya está preparada; revelarla no hace otra llamada de IA. No devolver claves, identificadores del proveedor ni criterios internos de éxito.
5. `/api/coach/` recibe solo el texto del estudiante; toma misión, contexto y último identificador desde la sesión. Actualiza el identificador únicamente tras una respuesta válida.
6. `/api/reset/` invalida la experiencia anterior y libera la foto del navegador. Las respuestas tardías no deben repoblar una experiencia reiniciada.

Límites iniciales sugeridos, sujetos a ensayo: JPEG de hasta 1280 px de lado mayor, compresión aproximada 0,8 y límite de archivo de 5 MB; mensajes del estudiante hasta 1000 caracteres. No son valores medidos. Revalidar en servidor y evitar almacenar cargas grandes en archivos temporales sin limpieza.

Mantener CSRF en POST, sesión del lado del servidor, secretos fuera de Git, mensajes de error seguros y registros sin imágenes ni texto privado. Deshabilitar botones durante envíos y manejar solicitudes concurrentes para no cruzar misiones. La sesión debe tener caducidad y limpieza documentadas: SQLite no implica datos efímeros por sí sola.

Una recarga que pierda la foto local puede devolver al usuario a capturar; no guardar imágenes permanentemente para resolver ese caso. Ante sesión vencida, el coach muestra una ruta clara para comenzar otra exploración.

## Riesgos prioritarios para la demo

- **Cámara en teléfono:** comprobar desde el principio la URL HTTPS real exigida por la especificación; la prueba de escritorio no sustituye el teléfono.
- **Modelo y latencia:** validar una llamada multimodal pronto; medir varias ejecuciones con la red de ensayo.
- **Misión realizable:** ensayar edades extremas, ausencia de materiales y tiempos cortos; “diseñar” puede ser un logro válido sin conectar Arduino.
- **Coach que revela la solución:** probar respuestas erróneas, “no sé” y pedidos de solución; revisar progresión de pistas y una sola pregunta principal.
- **Calidad irregular del objeto:** tener planta real y una foto propia de respaldo para enviar a la API; nunca presentar contenido precargado como reconocimiento en vivo.
- **Reglas desconocidas:** conservar separación entre preparación previa y cambios hechos durante el evento. No se ha confirmado si permiten código previo.

## Alcance protegido

Mantener los elementos excluidos en §27. “Arduino” personaliza el reto, no significa controlar una placa. El coach acompaña la misión actual; no abre chat general. No construir extensiones antes de demostrar el recorrido completo de §26.
