# STEAM Lens

**El mundo es tu laboratorio.**

Web app móvil que transforma una fotografía de un objeto en conexiones STEAM, una misión personalizada y acompañamiento mediante preguntas y pistas.

## Estado de la implementación

MVP implementado: Django, cuatro pantallas adaptables al móvil, cámara y carga de respaldo, análisis y misión en una llamada, coach con continuidad, sesión temporal y manejo de errores.

Consulta [Operación](docs/OPERACION.md) para instalar, arrancar, configurar y probar. El servidor de desarrollo de esta sesión utiliza **http://127.0.0.1:8001/**. La disponibilidad depende de que su proceso siga activo.

Ver resultados y pendientes actuales en [Retoma](docs/RETOMA.md). No se considera terminada la validación de demo hasta ensayar cámara física por HTTPS.

## Documentos para continuar

1. [Especificación original](STEAM%20Lens%20%E2%80%94%20Especificaci%C3%B3n%20del%20MVP%20para%20Hackathon.md): alcance de producto; se conserva intacta.
2. [Análisis y decisiones propuestas](docs/ANALISIS.md): viabilidad, ambigüedades y arquitectura adaptable.
3. [Plan de construcción y validación](docs/PLAN.md): orden de implementación, criterios de salida y ensayo de demo.
4. [Punto de retoma para la hackathon](docs/RETOMA.md): estado verificable, pendientes y registro de cambios.

El análisis conserva las propuestas iniciales; Operación y Retoma describen lo implementado y verificado. Las instrucciones posteriores de la usuaria tienen prioridad y deben reflejarse en estos documentos.

## Núcleo del MVP

Edad + materiales + tiempo → cámara → una foto → análisis y misión en una llamada → conexiones STEAM → revelar misión → coach por texto → otra exploración.

Stack previsto: Django, SQLite, Templates, CSS y JavaScript vanilla; SDK oficial de OpenAI y Responses API. Sin cuentas, hardware conectado, vídeo continuo ni realidad aumentada.

## Próximo paso

Ensayar desde un teléfono por HTTPS con un objeto real y adaptar los requisitos del evento cuando estén disponibles. Mantener la especificación original como referencia y registrar los cambios en `docs/RETOMA.md`.

## Agente en Telegram
Canal principal de la nueva experiencia: @STEAM_Lens_bot. Grado, área, duración, recurso y sesión completa en PDF. Consulta [Telegram](docs/TELEGRAM.md) para arrancar, probar y conocer los límites.

