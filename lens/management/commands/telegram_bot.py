import os
import time
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from lens.telegram.client import TelegramClient, TelegramError

class Command(BaseCommand):
    help = "Run the Telegram agent with long polling (no public URL required)."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="Validate token without consuming messages or sending replies.")

    def handle(self, *args, **options):
        try:
            client = TelegramClient(os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
            me = client.call("getMe")
            self.stdout.write(f"Telegram OK: @{me['username']}")
            hook = client.call("getWebhookInfo")
            if hook.get("url"):
                raise CommandError("Este bot ya tiene un webhook. No se modificó; revisa su uso antes de activar polling.")
            if options["check"]:
                return
            from lens.telegram.agent import Agent
            agent = Agent(client)
            runtime = settings.BASE_DIR / ".runtime"
            runtime.mkdir(exist_ok=True)
            # An OS socket prevents accidentally starting a second local consumer.
            import socket
            guard = socket.socket()
            try:
                guard.bind(("127.0.0.1", 18763))
            except OSError:
                raise CommandError("Ya hay un proceso del bot activo (puerto local 18763).") from None
            checkpoint = runtime / "telegram_offset.txt"
            offset = int(checkpoint.read_text()) if checkpoint.exists() else 0
            self.stdout.write("Agente escuchando. En Telegram envía /start. Ctrl+C para detener.")
            while True:
                try:
                    updates = client.call("getUpdates", {"offset": offset, "timeout": 25, "allowed_updates": ["message", "callback_query"]})
                    for update in updates:
                        try:
                            agent.handle(update)
                        except TelegramError:
                            self.stderr.write("Entrega Telegram fallida; el usuario puede usar /continuar. No se registraron datos privados.")
                        except Exception as exc:
                            self.stderr.write(f"Turno fallido ({type(exc).__name__}); sin datos privados en el registro.")
                        offset = update["update_id"] + 1
                        checkpoint.write_text(str(offset))
                except TelegramError as exc:
                    self.stderr.write(str(exc))
                    time.sleep(3)
        except TelegramError as exc:
            raise CommandError(str(exc)) from None
        except KeyboardInterrupt:
            self.stdout.write("Bot detenido.")
