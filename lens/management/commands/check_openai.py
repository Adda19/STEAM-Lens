"""Explicit opt-in smoke test: one real request, no personal content."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict

class ConnectionCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ready: bool

class Command(BaseCommand):
    help = "Makes one small real Responses API request to verify model, key and Structured Outputs."

    def handle(self, *args, **options):
        if not settings.OPENAI_API_KEY:
            raise CommandError("OPENAI_API_KEY no está configurada.")
        try:
            with OpenAI(api_key=settings.OPENAI_API_KEY, timeout=20, max_retries=0) as client:
                response = client.responses.parse(model=settings.OPENAI_MODEL, input="Return ready=true.",
                                                  text_format=ConnectionCheck, max_output_tokens=1000, store=False)
            if response.output_parsed is None:
                raise CommandError("El proveedor no devolvió una respuesta estructurada completa.")
            self.stdout.write(self.style.SUCCESS(f"Conexión y Structured Outputs OK: {settings.OPENAI_MODEL}"))
        except OpenAIError as exc:
            code = getattr(exc, "code", None)
            self.stderr.write(f"Tipo: {type(exc).__name__}; estado: {getattr(exc, 'status_code', None)}; código: {code}")
            raise CommandError("No se pudo validar OpenAI. Revisa credencial, acceso al modelo y saldo. No se mostraron detalles privados.") from None
