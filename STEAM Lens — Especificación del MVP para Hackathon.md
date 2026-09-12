# STEAM Lens — Especificación del MVP para Hackathon

> Documento fuente de verdad para construir el prototipo funcional de **STEAM Lens**.  
> El objetivo es que una IA de programación pueda generar el proyecto sin ampliar el alcance ni inventar funcionalidades adicionales.

## 0. Instrucciones para la IA que construya el proyecto

Construye exactamente el MVP descrito en este documento.

Prioridades, en este orden:

1. Que funcione correctamente desde un teléfono móvil.
2. Que la cámara pueda capturar un objeto del mundo real.
3. Que la imagen sea analizada con la API de OpenAI.
4. Que la respuesta se transforme en una experiencia STEAM estructurada y visual.
5. Que se genere una misión personalizada según edad, materiales y tiempo disponible.
6. Que el agente acompañe al estudiante mediante preguntas y pistas, sin entregar inmediatamente la solución.
7. Que la demo sea estable, rápida de entender y visualmente atractiva.

No agregues funcionalidades fuera del alcance definido aquí. No agregues autenticación, dashboard docente, perfiles, estadísticas, realidad aumentada, voz, streaming de video, gamificación compleja ni integraciones con hardware durante el MVP.

Si existe una decisión técnica menor no especificada, selecciona la alternativa más simple, estable y fácil de demostrar.

---

# 1. Nombre del proyecto

**STEAM Lens**

### Tagline principal

**El mundo es tu laboratorio.**

### Idea de comunicación para pitch

**STEAM Lens convierte cualquier objeto que te rodea en una oportunidad para aprender, experimentar y construir.**

Versión en inglés:

**What if the world became your STEAM classroom?**

**Point. Discover. Build.**

---

# 2. Problema

Las herramientas de IA educativa suelen vivir dentro de una ventana de chat. Para utilizarlas, el estudiante debe abandonar momentáneamente aquello que está observando, abrir otra herramienta, formular una pregunta y explicar el contexto.

STEAM Lens cambia ese flujo.

El estudiante comienza desde el mundo físico. Apunta la cámara hacia un objeto de su entorno y el agente interpreta aquello que está viendo para convertirlo en una experiencia de aprendizaje STEAM contextualizada.

El agente no espera a que el estudiante formule una pregunta perfecta.

**La interacción comienza con la curiosidad.**

---

# 3. Objetivo del MVP

Construir una web app móvil funcional en la que un estudiante pueda:

1. Indicar su edad.
2. Seleccionar los materiales que tiene disponibles.
3. Seleccionar cuánto tiempo tiene para la actividad.
4. Abrir la cámara del celular.
5. Apuntar hacia un objeto del mundo real.
6. Tomar una fotografía mediante el botón **Descubrir**.
7. Permitir que OpenAI interprete la imagen.
8. Mostrar qué oportunidades STEAM existen alrededor del objeto identificado.
9. Presentar una misión práctica adaptada al contexto del estudiante.
10. Iniciar una interacción con un agente pedagógico que guíe al estudiante mediante preguntas y pistas.

El MVP debe demostrar este flujo completo:

**Ver → descubrir → conectar con STEAM → recibir una misión → pensar → recibir una pista → continuar.**

---

# 4. Principio pedagógico

STEAM Lens no debe comportarse como un generador de tutoriales.

La regla principal del agente es:

> **No dar primero la respuesta. Ayudar al estudiante a descubrirla.**

El acompañamiento debe usar una lógica de andamiaje:

1. Preguntar.
2. Escuchar la respuesta.
3. Dar retroalimentación breve.
4. Si el estudiante necesita ayuda, entregar una pista pequeña.
5. Hacer una nueva pregunta.
6. Aumentar gradualmente la claridad de las pistas solo cuando sea necesario.
7. Reconocer cuando el estudiante logra avanzar.

El agente debe trabajar una pregunta o decisión a la vez.

---

# 5. Usuario objetivo del MVP

Estudiantes aproximadamente entre **6 y 18 años**.

La aplicación debe adaptar vocabulario, complejidad, autonomía y dificultad de la misión a la edad indicada.

Para el hackathon no existirán cuentas, perfiles ni autenticación.

---

# 6. Datos de contexto solicitados antes de explorar

La pantalla inicial debe solicitar únicamente la información necesaria para personalizar la misión.

## Edad

Campo numérico simple.

Rango recomendado:

- mínimo: 6
- máximo: 18

## Materiales disponibles

Selección múltiple con opciones visuales:

- Sin materiales
- Arduino
- micro:bit
- LEDs
- Sensores
- Servomotor
- Motor DC
- Cartón / MDF
- Material reciclado

No es necesario construir un inventario detallado de componentes.

## Tiempo disponible

Tres opciones:

- 10 minutos
- 20 minutos
- 30 minutos

## Idioma del MVP

Español.

La arquitectura debe permitir internacionalización futura, pero no es necesario implementarla durante el hackathon.

---

# 7. Experiencia de usuario

El MVP tendrá **cuatro pantallas principales**.

---

## Pantalla 1 — Inicio

Debe ser extremadamente sencilla.

Contenido:

- Logo o nombre STEAM Lens.
- Frase: **El mundo es tu laboratorio.**
- Edad.
- Materiales disponibles.
- Tiempo disponible.
- Botón principal: **Comenzar a explorar**.

No pedir nombre, correo, colegio, curso, ubicación ni ningún otro dato personal.

---

## Pantalla 2 — Explorar

Debe utilizar la cámara trasera del teléfono siempre que esté disponible.

La cámara ocupa la mayor parte de la pantalla.

Elementos:

- Vista previa de cámara.
- Guía visual sencilla en el centro para orientar el objeto.
- Texto: **Apunta a algo que te dé curiosidad.**
- Botón grande: **Descubrir**.

Cuando el usuario presiona el botón:

1. Capturar un solo frame de la cámara.
2. Congelar o mostrar la fotografía capturada.
3. Comprimir/redimensionar la imagen si es necesario.
4. Enviar la fotografía al backend.
5. El backend envía imagen + contexto del estudiante a OpenAI.
6. Mostrar un estado de carga atractivo mientras llega la respuesta.

No realizar análisis continuo de video.

No enviar frames repetidamente.

No implementar AR real.

---

## Pantalla 3 — Descubrimiento

Después del análisis debe aparecer la fotografía tomada y el objeto identificado.

Ejemplo:

# ¡Encontré una planta! 🌱

**Aquí hay STEAM por todas partes.**

Mostrar conexiones relevantes como tarjetas cortas.

Ejemplo:

### Ciencia

Fotosíntesis, agua y necesidades de las plantas.

### Tecnología

Sensores capaces de medir su entorno.

### Ingeniería

Sistemas automáticos de riego.

### Matemáticas

Medición de crecimiento y humedad.

No es obligatorio que las cinco áreas STEAM aparezcan si una conexión sería artificial.

Deben mostrarse únicamente relaciones educativas relevantes.

Botón principal:

**Crear una misión**

### Optimización importante

La misión debe quedar generada en la misma llamada de OpenAI que analiza la imagen.

La interfaz simplemente oculta los datos de la misión hasta que el estudiante pulse **Crear una misión**.

Esto evita una segunda llamada innecesaria, reduce latencia y hace más estable la demo.

---

## Pantalla 4 — Misión + STEAM Coach

Mostrar la misión previamente generada.

Ejemplo:

# Misión: Cuida tu planta 🌿

**Tu desafío**

Construye una forma de descubrir cuándo esta planta necesita agua.

- Tiempo: 20 minutos
- Dificultad: ⭐⭐
- Materiales: Arduino + sensor

Después aparece el agente pedagógico.

### STEAM Coach

La primera interacción NO debe ser una lista completa de instrucciones.

Debe comenzar con una pregunta.

Ejemplo:

**Antes de construir, pensemos.**

> ¿Qué característica de la tierra podríamos medir para saber si la planta necesita agua?

El estudiante puede responder mediante un campo de texto.

Para el MVP no se requiere voz.

Después de cada respuesta, el agente debe:

- validar el razonamiento;
- corregir con tacto si es necesario;
- entregar como máximo una pista breve;
- hacer una sola pregunta siguiente;
- evitar revelar el procedimiento completo salvo que sea realmente necesario para continuar;
- adaptar el lenguaje a la edad.

La pantalla debe incluir un botón **Explorar otro objeto** para reiniciar la experiencia.

---

# 8. Arquitectura técnica

La aplicación debe ser una **web app mobile-first**.

No desarrollar aplicaciones nativas para Android o iOS durante el MVP.

```text
Teléfono / navegador móvil
        │
        │ cámara
        ▼
Captura de una fotografía
        │
        ▼
Frontend HTML + JavaScript
        │
        ▼
Django Backend
        │
        ├── contexto del estudiante
        ├── fotografía capturada
        └── instrucciones pedagógicas
        │
        ▼
OpenAI Responses API
        │
        ▼
Structured Output JSON
        │
        ├── objeto identificado
        ├── conexiones STEAM
        ├── misión
        └── primera pregunta pedagógica
        │
        ▼
Interfaz STEAM Lens
        │
        ▼
STEAM Coach
        │
        ▼
Pregunta → respuesta → pista → siguiente pregunta
```

---

# 9. Stack tecnológico

## Backend

- Python
- Django
- OpenAI Python SDK oficial
- SQLite para el MVP

## Frontend

- Django Templates
- HTML5
- CSS / Tailwind CSS
- JavaScript vanilla

No utilizar React o Next.js salvo que exista una razón técnica inevitable.

## Cámara

Usar la API del navegador:

```javascript
navigator.mediaDevices.getUserMedia(...)
```

Solicitar preferentemente la cámara trasera usando:

```javascript
facingMode: "environment"
```

La aplicación desplegada debe usar HTTPS.

---

# 10. Integración con OpenAI

## API

Utilizar **OpenAI Responses API**.

El backend debe ser el único componente que tenga acceso a la API key.

Nunca enviar la API key al navegador.

## Variables de entorno

Crear `.env.example`:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-terra
DJANGO_SECRET_KEY=
DEBUG=True
```

El modelo debe ser configurable mediante `OPENAI_MODEL`.

Para el MVP utilizar un modelo multimodal que soporte:

- texto como entrada;
- imagen como entrada;
- texto como salida;
- Structured Outputs / JSON Schema.

`gpt-5.6-terra` puede utilizarse como valor inicial por equilibrio entre capacidad y costo, pero no debe quedar rígidamente acoplado al código.

---

# 11. Estrategia de llamadas a OpenAI

El flujo debe minimizar llamadas innecesarias.

## Llamada 1 — Analizar objeto + preparar misión

Entrada:

- fotografía;
- edad;
- materiales disponibles;
- tiempo disponible;
- instrucciones pedagógicas.

Salida estructurada:

- si la fotografía es válida;
- objeto identificado;
- descripción corta;
- conexiones STEAM;
- misión personalizada;
- primera pregunta del coach.

Esta llamada debe generar simultáneamente el contenido de las pantallas 3 y 4.

## Llamadas siguientes — STEAM Coach

Entrada:

- respuesta actual del estudiante;
- contexto de la misión;
- historial necesario de la interacción.

Utilizar `previous_response_id` de Responses API para mantener continuidad entre turnos.

Guardar el último `response_id` en la sesión de Django y actualizarlo después de cada interacción.

Cuando se utilice `previous_response_id`, volver a enviar las instrucciones del rol pedagógico en cada nueva llamada para mantener consistente el comportamiento del agente.

---

# 12. Structured Output del análisis

La aplicación NO debe intentar extraer datos desde texto libre.

Usar Structured Outputs con JSON Schema estricto.

Forma conceptual esperada:

```json
{
  "valid_capture": true,
  "retry_message": null,
  "detected_object": {
    "name": "Planta en maceta",
    "description": "Una planta pequeña en una maceta ubicada cerca de una ventana.",
    "confidence": "high"
  },
  "steam_connections": [
    {
      "area": "science",
      "title": "¿Qué necesita para vivir?",
      "explanation": "Puedes explorar agua, luz y fotosíntesis."
    },
    {
      "area": "technology",
      "title": "Podemos medir su entorno",
      "explanation": "Los sensores permiten conocer humedad, luz o temperatura."
    },
    {
      "area": "engineering",
      "title": "Automatiza su cuidado",
      "explanation": "Un sistema puede detectar cuándo necesita agua."
    }
  ],
  "mission": {
    "title": "Cuida tu planta",
    "challenge": "Construye una forma de descubrir cuándo esta planta necesita agua.",
    "learning_goal": "Comprender cómo una variable física puede medirse y utilizarse para tomar una decisión.",
    "difficulty": 2,
    "estimated_minutes": 20,
    "materials_required": [
      "Arduino",
      "sensor de humedad"
    ],
    "first_question": "¿Qué característica de la tierra podríamos medir para saber si la planta necesita agua?",
    "success_criteria": "El estudiante identifica la humedad como una variable útil y propone cómo medirla."
  }
}
```

## Reglas del schema

- `valid_capture`: booleano obligatorio.
- `retry_message`: texto solo cuando la fotografía no sea apropiada.
- `confidence`: `high`, `medium` o `low`.
- `steam_connections`: entre 2 y 5 elementos relevantes.
- No inventar conexiones únicamente para completar las cinco letras STEAM.
- `difficulty`: entero entre 1 y 3.
- `estimated_minutes`: debe respetar aproximadamente el tiempo seleccionado.
- Los materiales requeridos deben basarse principalmente en los materiales disponibles.
- Si seleccionó **Sin materiales**, la misión debe poder realizarse mediante observación, medición, dibujo, comparación, razonamiento o experimentación segura.

---

# 13. Structured Output del STEAM Coach

Las respuestas del coach también deben ser estructuradas.

```json
{
  "feedback": "Exactamente. La humedad nos ayuda a saber cuánta agua hay en la tierra.",
  "status": "continue",
  "hint_level": 0,
  "hint": null,
  "next_question": "Ahora mira tus materiales. ¿Cuál de ellos podría ayudarte a medir esa humedad?",
  "celebration": null
}
```

Valores posibles para `status`:

- `continue`
- `hint`
- `completed`
- `blocked`

`hint_level`:

- `0`: sin pista;
- `1`: pista ligera;
- `2`: pista más directa;
- `3`: ayuda explícita necesaria para continuar.

El agente debe evitar saltar directamente a nivel 3.

---

# 14. Prompt base — Analizador + diseñador de misión

```text
Eres STEAM Lens, un agente educativo que transforma objetos del mundo real en oportunidades de aprendizaje STEAM.

Recibirás una fotografía tomada por un estudiante y contexto sobre su edad, materiales disponibles y tiempo.

Tu trabajo es:
1. Identificar el objeto principal de la imagen sin exagerar la certeza.
2. Detectar entre 2 y 5 conexiones STEAM realmente relevantes.
3. Crear UNA misión práctica, segura, realizable y apropiada para la edad.
4. Utilizar prioritariamente los materiales que el estudiante indicó que tiene.
5. Diseñar la misión para el tiempo disponible.
6. Generar una primera pregunta que haga pensar al estudiante antes de darle instrucciones.

Principios pedagógicos:
- No conviertas la experiencia en un tutorial paso a paso desde el inicio.
- Prioriza curiosidad, observación, hipótesis, razonamiento y construcción.
- No des la solución completa inmediatamente.
- Evita vocabulario innecesariamente complejo para la edad.
- No fuerces conexiones STEAM artificiales.
- La misión debe tener una meta clara y comprobable.
- Si el estudiante no tiene materiales, crea una actividad de exploración o experimentación posible con objetos cotidianos.

Seguridad:
- No propongas actividades peligrosas.
- No sugieras trabajar con corriente de red, fuego, químicos peligrosos, herramientas riesgosas o desmontaje de equipos eléctricos.
- Si la fotografía muestra principalmente una persona o información privada, no la analices como objeto educativo y solicita apuntar a otro objeto.
- No identifiques personas ni infieras atributos personales.

Devuelve exclusivamente la estructura JSON solicitada.
```

---

# 15. Prompt base — STEAM Coach

```text
Eres STEAM Coach, el agente pedagógico de STEAM Lens.

Tu objetivo es ayudar al estudiante a completar la misión mediante pensamiento guiado.

No eres un solucionador automático.

Reglas:
1. Trabaja una decisión o concepto a la vez.
2. Haz máximo una pregunta principal por turno.
3. Si la respuesta es correcta, reconócela brevemente y avanza.
4. Si es parcialmente correcta, rescata lo acertado y formula una pregunta que permita mejorarla.
5. Si es incorrecta, no reveles inmediatamente la respuesta. Entrega primero una pista pequeña.
6. Incrementa gradualmente el nivel de ayuda cuando el estudiante permanezca bloqueado.
7. Adapta lenguaje, dificultad y longitud a la edad indicada.
8. Mantén respuestas breves y conversacionales.
9. No agregues materiales que el estudiante no tiene salvo objetos cotidianos comunes.
10. Nunca propongas acciones físicas peligrosas.
11. Si la misión se completa, cambia status a completed y celebra de forma breve.

Devuelve exclusivamente el JSON definido para el STEAM Coach.
```

---

# 16. Endpoints Django

```text
GET  /
GET  /explore/
POST /api/analyze/
POST /api/coach/
POST /api/reset/
```

## `GET /`

Muestra configuración inicial.

## `GET /explore/`

Muestra cámara.

## `POST /api/analyze/`

Recibe:

- imagen;
- edad;
- materiales;
- tiempo.

Ejecuta la llamada multimodal a OpenAI.

Devuelve JSON estructurado al frontend.

## `POST /api/coach/`

Recibe:

- respuesta del estudiante.

Obtiene desde sesión:

- misión;
- edad;
- contexto;
- último `response_id`.

Ejecuta el siguiente turno del agente.

## `POST /api/reset/`

Limpia los datos temporales y permite explorar otro objeto.

---

# 17. Estado de sesión

Utilizar Django Session.

Guardar únicamente:

```text
learner_age
available_materials
available_time
analysis_result
mission
last_openai_response_id
```

No construir modelos complejos de base de datos para el MVP.

---

# 18. Manejo de la imagen

La fotografía debe existir únicamente el tiempo necesario para procesar la solicitud.

Preferencias:

- capturar desde canvas o blob;
- redimensionar antes de enviar si es excesivamente grande;
- usar JPEG con compresión razonable;
- enviar al backend;
- enviar a OpenAI como entrada de imagen;
- no guardar fotografías permanentemente en `media/`;
- eliminar archivos temporales después del procesamiento.

La UI puede conservar una copia local únicamente mientras se muestra la experiencia actual.

---

# 19. Privacidad y seguridad para menores

El MVP debe aplicar privacidad por diseño.

No solicitar ni almacenar:

- nombre;
- correo;
- colegio;
- ubicación;
- teléfono;
- datos biométricos;
- fotografías de perfil.

Mostrar cerca de la cámara:

**Explora objetos, no personas.**

Si la imagen contiene principalmente una persona, información personal visible o contenido que no sea apropiado para una actividad educativa, devolver una respuesta de reintento.

No realizar reconocimiento facial.

No inferir identidad, edad, género, emociones, origen u otros atributos personales de personas visibles.

Las misiones físicas deben ser seguras para la edad seleccionada.

---

# 20. Manejo de errores

## Permiso de cámara rechazado

Mostrar:

**Necesitamos acceso a la cámara para descubrir el mundo contigo. Puedes habilitarla desde los permisos del navegador.**

Permitir seleccionar/subir una fotografía como respaldo si resulta sencillo.

## Cámara no disponible

Ofrecer carga de imagen desde galería.

## Imagen borrosa o sin objeto claro

Mostrar el `retry_message`.

Ejemplo:

**No alcanzo a reconocer un objeto con claridad. Acércate un poco y probemos otra vez.**

## Baja confianza

Si `confidence = low`, pedir otra fotografía en vez de inventar una identificación.

## Error de OpenAI

Mostrar:

**No pude analizarlo esta vez. Probemos de nuevo.**

Incluir botón **Reintentar**.

Nunca mostrar stack traces, API keys ni errores internos.

---

# 21. Diseño visual

Objetivo visual:

- moderno;
- tecnológico;
- educativo;
- curioso;
- amigable para estudiantes sin verse infantil para adolescentes.

Priorizar interfaz mobile-first.

Características:

- botones grandes;
- tipografía legible;
- tarjetas cortas;
- iconografía STEAM;
- animaciones sutiles;
- estados de carga atractivos;
- cámara como protagonista.

No sobrecargar la pantalla con navegación.

La pantalla de cámara debe sentirse como una herramienta de exploración, no como un formulario.

---

# 22. Estado de carga

Durante el análisis evitar un spinner genérico si es posible.

Usar mensajes rotativos:

- **Observando tu descubrimiento…**
- **Buscando ciencia a tu alrededor…**
- **Conectando ideas STEAM…**
- **Preparando tu misión…**

Esto convierte parte de la latencia en experiencia.

---

# 23. Estructura sugerida del proyecto

```text
steam_lens/
│
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── lens/
│   ├── urls.py
│   ├── views.py
│   ├── services/
│   │   └── openai_service.py
│   ├── prompts/
│   │   ├── analyze.py
│   │   └── coach.py
│   ├── schemas/
│   │   ├── analysis.py
│   │   └── coach.py
│   └── templates/
│       └── lens/
│           ├── index.html
│           ├── explore.html
│           └── mission.html
│
└── static/
    ├── css/
    ├── js/
    │   ├── camera.js
    │   └── coach.js
    └── img/
```

La estructura puede simplificarse, pero la integración con OpenAI debe permanecer aislada de las vistas tanto como sea práctico.

---

# 24. Requisitos funcionales mínimos

El proyecto se considera funcional únicamente si:

- [ ] Abre correctamente en navegador móvil.
- [ ] Permite definir edad.
- [ ] Permite seleccionar materiales.
- [ ] Permite seleccionar 10, 20 o 30 minutos.
- [ ] Solicita permiso de cámara.
- [ ] Prioriza cámara trasera.
- [ ] Muestra preview en vivo.
- [ ] Captura fotografía al presionar **Descubrir**.
- [ ] Envía la fotografía al backend.
- [ ] El backend llama a OpenAI con imagen + contexto.
- [ ] OpenAI devuelve resultado estructurado.
- [ ] La UI muestra el objeto detectado.
- [ ] La UI muestra conexiones STEAM relevantes.
- [ ] La misión respeta edad, materiales y tiempo.
- [ ] **Crear una misión** revela la misión preparada.
- [ ] STEAM Coach inicia con una pregunta.
- [ ] El estudiante puede responder por texto.
- [ ] El agente entrega feedback y una nueva pregunta o pista.
- [ ] El agente no entrega inmediatamente la solución completa.
- [ ] Existe manejo básico de errores.
- [ ] Existe **Explorar otro objeto**.
- [ ] La API key nunca aparece en frontend.
- [ ] Las fotografías no se almacenan permanentemente.

---

# 25. Escenario oficial para probar la demo

Preparar al menos un objeto conocido antes de presentar.

Objeto recomendado:

**Planta en maceta.**

Configuración:

- Edad: 10 años.
- Tiempo: 20 minutos.
- Materiales: Arduino + sensores.

Resultado aproximado:

### Objeto

**Planta**

### Conexiones

- ciencia: necesidades de las plantas;
- tecnología: sensores;
- ingeniería: automatización del riego;
- matemáticas: medición de humedad o crecimiento.

### Misión

**Diseñar una forma de descubrir cuándo la planta necesita agua.**

### Primera pregunta

**¿Qué característica de la tierra podríamos medir para saber si la planta necesita agua?**

La salida exacta puede variar.

No hardcodear este contenido.

También probar previamente:

- ventilador;
- bicicleta o rueda;
- lámpara;
- botella de agua;
- puerta;
- silla.

---

# 26. Definition of Done

El MVP está terminado cuando durante una demostración real desde un teléfono sea posible realizar, sin intervención técnica manual:

```text
Abrir URL
   ↓
Seleccionar edad + materiales + tiempo
   ↓
Abrir cámara
   ↓
Apuntar a un objeto
   ↓
Descubrir
   ↓
Objeto reconocido
   ↓
Conexiones STEAM
   ↓
Crear una misión
   ↓
Ver misión personalizada
   ↓
Responder primera pregunta
   ↓
Recibir feedback/pista
   ↓
Continuar razonando
```

Si este recorrido funciona bien, el MVP está completo.

No agregar funcionalidades adicionales antes de asegurar este flujo.

---

# 27. Fuera del alcance del MVP

NO implementar durante el hackathon:

- login;
- cuentas;
- dashboard docente;
- notas;
- seguimiento académico;
- estadísticas;
- historial;
- perfiles persistentes;
- chat abierto general;
- voz;
- síntesis de voz;
- análisis continuo de video;
- WebRTC;
- realidad aumentada real;
- detección con YOLO;
- entrenamiento de modelos propios;
- Roboflow;
- TensorFlow;
- inventario avanzado;
- conexión directa con Arduino;
- Bluetooth;
- IoT;
- integración con LMS;
- certificados;
- puntos;
- rankings;
- avatares;
- tienda;
- sistema de profesores;
- generación de planes curriculares completos.

Estas funcionalidades pertenecen al roadmap.

---

# 28. Roadmap posterior al hackathon

Posibles extensiones:

- reconocimiento continuo del entorno;
- etiquetas tipo AR sobre objetos;
- voz conversacional;
- misiones colaborativas;
- perfil progresivo de competencias STEAM;
- inventario real de laboratorios escolares;
- integración con kits educativos;
- verificación visual del progreso de una construcción;
- dashboard docente;
- alineación curricular;
- registro de evidencias;
- modo museo;
- modo aula;
- modo laboratorio;
- retos entre estudiantes.

Ninguna debe bloquear el MVP.

---

# 29. Idea central que nunca debe perderse

STEAM Lens no es un chatbot con acceso a la cámara.

**La cámara es el punto de entrada a la experiencia.**

El agente debe sentirse como una capa de aprendizaje colocada sobre el mundo físico.

El estudiante no comienza escribiendo:

> “Dame una actividad sobre plantas.”

Comienza mirando una planta.

El agente observa el mismo objeto, descubre posibilidades educativas y transforma esa curiosidad en una misión.

Ese cambio de interacción es el corazón del proyecto.

---

# 30. Frase final del producto

> **STEAM Lens doesn't give you the answer. It helps you discover it.**