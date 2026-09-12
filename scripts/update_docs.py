"""Record implementation status without changing the original specification."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
readme = root / "README.md"
text = readme.read_text(encoding="utf-8")
start = text.index("## Estado al")
end = text.index("## Documentos para continuar")
text = text[:start] + """## Estado de la implementación

MVP implementado: Django, cuatro pantallas adaptables al móvil, cámara y carga de respaldo, análisis y misión en una llamada, coach con continuidad, sesión temporal y manejo de errores.

Consulta [Operación](docs/OPERACION.md) para instalar, arrancar, configurar y probar. El servidor de desarrollo de esta sesión utiliza **http://127.0.0.1:8001/**. La disponibilidad depende de que su proceso siga activo.

Ver resultados y pendientes actuales en [Retoma](docs/RETOMA.md). No se considera terminada la validación de demo hasta ensayar cámara física por HTTPS.

""" + text[end:]
text = text.replace("Las decisiones propuestas complementan la especificación; no representan funciones implementadas ni requisitos nuevos de la hackathon.", "El análisis conserva las propuestas iniciales; Operación y Retoma describen lo implementado y verificado.")
text = text[:text.index("## Próximo paso")] + """## Próximo paso

Ensayar desde un teléfono por HTTPS con un objeto real y adaptar los requisitos del evento cuando estén disponibles. Mantener la especificación original como referencia y registrar los cambios en `docs/RETOMA.md`.
"""
readme.write_text(text, encoding="utf-8")
plan = root / "docs/PLAN.md"
text = plan.read_text(encoding="utf-8").replace("Estado: pendiente de implementación.", "Estado: implementación realizada; consultar RETOMA.md para resultados de pruebas y pendientes de teléfono/HTTPS.")
text = text.replace("Todos los casos están **pendientes**.", "Esta matriz es el guion para pruebas manuales con dispositivos y objetos reales; sus casos siguen **pendientes de ensayo físico**. Las pruebas automatizadas se registran por separado en RETOMA.md.")
plan.write_text(text, encoding="utf-8")
analysis = root / "docs/ANALISIS.md"
text = analysis.read_text(encoding="utf-8").replace("Estado: diseño propuesto, todavía sin implementación.", "Estado histórico: análisis previo a la construcción. La implementación posterior y sus resultados están en OPERACION.md y RETOMA.md; las frases de trabajo pendiente en este análisis describen aquel momento.")
analysis.write_text(text, encoding="utf-8")
