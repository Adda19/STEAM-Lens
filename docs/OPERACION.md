# Ejecutar y adaptar STEAM Lens

## Instalación en Windows

Desde `E:\STEAM_Lens`, con Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe scripts\prepare_local.py
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=4 config.wsgi:application
```

Abrir `http://127.0.0.1:8001/`. El puerto 8001 evita interferir con otros proyectos que usan 8000. Waitress sirve también los archivos recopilados mediante WhiteNoise. Para desarrollo con recarga automática se puede usar `manage.py runserver 127.0.0.1:8001` en lugar de Waitress, deteniendo primero el servidor anterior.

`prepare_local.py` crea `.env` con una clave Django aleatoria solo si no existe. No copia ni imprime credenciales de OpenAI. Completar `OPENAI_API_KEY` en `.env` o definirla en el entorno del proceso; el entorno tiene prioridad sobre `.env`. Reiniciar el servidor después de cambiar configuración o código Python. Con Waitress, después de cambios de CSS/JS ejecutar `collectstatic` y reiniciar.

`requirements.txt` expresa rangos compatibles; `requirements.lock.txt` contiene las versiones concretas de la instalación probada. No actualizar dependencias justo antes de presentar salvo necesidad comprobada.

## Pruebas

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test lens.tests --verbosity 2
node --check static/js/setup.js
node --check static/js/experience.js
```

Estas comprobaciones no llaman a OpenAI. Node se utiliza únicamente para revisar sintaxis; no es necesario para ejecutar la aplicación.

Prueba de navegador opcional, con Microsoft Edge instalado y servidor en 8001:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\browser_check.py
```

El recorrido de navegador usa respuestas de IA simuladas exclusivamente dentro de la prueba. La aplicación no contiene un modo de análisis falso. Las capturas se guardan en `artifacts/`, ignorado por Git.

Pruebas explícitas con consumo real de API:

```powershell
.\.venv\Scripts\python.exe manage.py check_openai
.\.venv\Scripts\python.exe scripts\live_flow_check.py
```

La primera hace una solicitud breve de texto con schema estricto. La segunda envía una captura de nuestra ilustración CSS de planta, realiza análisis y un turno de coach, y reinicia la sesión. Requiere servidor en 8001 y Edge. Sirve para probar el circuito multimodal, no acredita reconocimiento de una fotografía real ni cámara móvil. Guarda resultados sin credenciales en `artifacts/live-flow-result.json`.

## Variables

| Variable | Uso |
| --- | --- |
| `OPENAI_API_KEY` | Credencial solo en servidor |
| `OPENAI_MODEL` | Por defecto `gpt-5.6-terra` |
| `OPENAI_TIMEOUT` | 45 segundos por llamada; sin reintentos automáticos |
| `DJANGO_SECRET_KEY` | Obligatoria en producción; generada localmente por el script |
| `DEBUG` | `True` local; `False` para publicar |
| `ALLOWED_HOSTS` | Nombres de host exactos, separados por comas, sin esquema |
| `CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS exactos, separados por comas |
| `DJANGO_HTTPS` | Cookies seguras, redirección HTTPS y HSTS cuando es `True` |

## Teléfono y despliegue

El host público todavía debe elegirse. Un teléfono no accede al PC usando `127.0.0.1`: esa dirección corresponde al propio teléfono. Para la demo móvil se necesita una URL HTTPS que llegue a este servidor.

Antes de publicar: establecer host y origen CSRF exactos, `DEBUG=False`, secreto propio y configuración HTTPS acorde al proxy del alojamiento. Si el proxy termina TLS, configurar el reconocimiento del protocolo únicamente con cabeceras que dicho proxy limpie y controle; de otro modo una redirección HTTPS puede entrar en bucle. No activar confianza indiscriminada en cabeceras entrantes. Ejecutar `manage.py check --deploy` en esa configuración y resolver sus avisos aplicables.

Esta versión utiliza **un proceso Waitress con varios hilos**, sesión Django en SQLite y bloqueos por sesión dentro del proceso. No desplegar varios procesos o réplicas sin reemplazar esa coordinación por una estrategia compartida. No hay autenticación ni cuotas globales: usar la URL de demostración de forma controlada y configurar límites de gasto en la cuenta antes de exposición pública amplia.

## Datos temporales y continuidad

- La imagen se recibe en memoria, se valida y se vuelve a codificar como JPEG de hasta 1280 px, sin metadatos originales. No se guarda en `media/`, SQLite ni registros.
- La UI conserva un blob durante la experiencia y lo libera al salir o reiniciar. Una recarga devuelve al flujo de captura.
- La sesión almacena edad, materiales, tiempo, análisis, misión, último identificador de respuesta y estado terminal del coach. No se envían al navegador identificadores de OpenAI ni `success_criteria`.
- Se utiliza `store=True` y `previous_response_id` para cumplir la continuidad de la especificación. El rol pedagógico se reenvía en cada turno. El reinicio elimina el estado local de misión, no el del proveedor.
- La sesión vence después de una hora; la cookie también vence al cerrar el navegador. Ejecutar `manage.py clearsessions` para limpiar filas expiradas de SQLite. El cierre del navegador no implica eliminación inmediata de la fila del servidor.
- La interfaz explica que la foto se envía a OpenAI. No se afirma retención cero del proveedor. Referencia: [controles oficiales de datos](https://developers.openai.com/api/docs/guides/your-data).

## Cambios rápidos para mañana

| Necesidad | Archivo |
| --- | --- |
| Cambiar modelo o tiempo de espera | `.env` y reinicio |
| Cambiar enfoque de las misiones | `lens/prompts/analyze.py` |
| Cambiar estilo pedagógico | `lens/prompts/coach.py` |
| Añadir o ajustar campo estructurado | `lens/schemas/`, servicio, vista y representación JS juntos |
| Cambiar materiales | `lens/views.py` (`MATERIALS`) y revisar prompts/pruebas |
| Cambiar identidad visual | Variables de `static/css/app.css` |
| Cambiar textos y pantallas | `lens/templates/lens/` |
| Cambiar interacción móvil | `static/js/experience.js` |

Por simplicidad, cámara y coach comparten `experience.js`; no requieren bibliotecas frontend. Si crece la interacción, dividir por responsabilidades sin alterar los endpoints existentes.

## Recuperación de demo

- Cámara rechazada: habilitar permiso o usar carga de foto JPEG/PNG/WebP de hasta 5 MB.
- Foto poco clara: tomar otra; el resultado inválido no habilita misión.
- Error de IA: reintentar desde el botón. Comprobar clave, acceso al modelo y saldo con `check_openai` si persiste.
- Sesión vencida: volver a Inicio. No tratar de recuperar la misión anterior desde datos del navegador.
- CSS antiguo: ejecutar `collectstatic`, reiniciar y recargar.
- Puerto ocupado: detener únicamente el proceso de STEAM Lens identificado al arrancar, o elegir otro puerto; no detener servidores de otros proyectos.
