"""Config-only smoke test: validates the Google OAuth client without needing a real teacher
connection (there's no browser in this process to complete a real handshake with)."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from lens.telegram import drive

class Command(BaseCommand):
    help = "Checks GOOGLE_OAUTH_* settings and that an authorization URL can be built."

    def handle(self, *args, **options):
        if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
            raise CommandError("Configura GOOGLE_OAUTH_CLIENT_ID y GOOGLE_OAUTH_CLIENT_SECRET en .env. Ver docs/TELEGRAM.md.")
        try:
            url = drive.authorization_url(drive.create_connect_state("check-google-drive"))
        except Exception as exc:
            raise CommandError(f"No se pudo construir la URL de autorización ({type(exc).__name__}). Revisa las credenciales.") from None
        if "accounts.google.com" not in url:
            raise CommandError("La URL de autorización no apunta a Google; revisa la configuración.")
        self.stdout.write(self.style.SUCCESS(f"Configuración de Google OAuth OK. Redirect URI: {settings.GOOGLE_OAUTH_REDIRECT_URI}"))
        self.stdout.write("Esto NO prueba una conexión real de un docente: eso requiere abrir la URL en un navegador y completar el consentimiento.")
