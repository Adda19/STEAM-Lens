import io
import time
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pypdf import PdfReader
from lens.context import build_context
from lens.telegram.lesson import generate, render_pdf
from lens.services.openai_service import ProviderUnavailable

class Command(BaseCommand):
    help = "One real AI call to verify session generation and PDF, without sending a Telegram message."

    def handle(self, *args, **kwargs):
        context = build_context(10, "naturales", 45, ["Sin materiales"])
        started = time.monotonic()
        try:
            result = generate(context, "Tenemos una planta en maceta en el aula. Queremos observar y comparar sus hojas sin arrancarlas.")
            if not result.ready:
                raise CommandError("El modelo pidió más información para este recurso de prueba.")
            pdf = render_pdf(result.lesson, context)
            reader = PdfReader(io.BytesIO(pdf))
            content = "\n".join(page.extract_text() for page in reader.pages)
            if "Evaluación" not in content or "45 minutos" not in content or "Recursos para profundizar" not in content:
                raise CommandError("El PDF no contiene los apartados esperados.")
            folder = settings.BASE_DIR / "artifacts"
            folder.mkdir(exist_ok=True)
            (folder / "sesion_telegram_prueba.pdf").write_bytes(pdf)
            self.stdout.write(f"Sesión real y PDF OK; {len(reader.pages)} páginas; {time.monotonic() - started:.1f} segundos; duración total validada: 45 minutos.")
        except ProviderUnavailable:
            raise CommandError("No se pudo completar la generación real; revisa conexión, modelo y configuración.") from None
