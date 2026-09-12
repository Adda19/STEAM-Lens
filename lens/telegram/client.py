"""Small Bot API client. Never expose token-bearing URLs in logs or errors."""
import json
import httpx

class TelegramError(Exception):
    pass

class TelegramClient:
    def __init__(self, token):
        if not token or ":" not in token:
            raise TelegramError("Falta un TELEGRAM_BOT_TOKEN válido en .env.")
        self.base = "https://api.telegram.org/bot" + token + "/"
        self.files = "https://api.telegram.org/file/bot" + token + "/"
        self.http = httpx.Client(timeout=40, follow_redirects=False)

    def call(self, method, data=None, files=None):
        try:
            if files:
                response = self.http.post(self.base + method, data=data, files=files)
            else:
                response = self.http.post(self.base + method, json=data or {})
            payload = response.json()
            if not payload.get("ok"):
                code = payload.get("error_code", response.status_code)
                raise TelegramError(f"Telegram rechazó {method} (HTTP {code}).")
            return payload["result"]
        except (httpx.HTTPError, ValueError):
            raise TelegramError(f"No se pudo conectar con Telegram ({method}).") from None

    def send(self, chat, text, keyboard=None):
        data = {"chat_id": chat, "text": text[:4000]}
        if keyboard is not None:
            data["reply_markup"] = {"inline_keyboard": keyboard}
        return self.call("sendMessage", data)

    def document(self, chat, pdf, caption):
        return self.call("sendDocument", {"chat_id": str(chat), "caption": caption},
                         {"document": ("Sesion_STEAM_Lens.pdf", pdf, "application/pdf")})

    def download(self, file_id):
        info = self.call("getFile", {"file_id": file_id})
        if info.get("file_size", 0) > 5 * 1024 * 1024:
            raise TelegramError("El recurso debe pesar hasta 5 MB.")
        path = info.get("file_path", "")
        if not path or ":" in path or ".." in path:
            raise TelegramError("Telegram no entregó una ruta de archivo válida.")
        try:
            with self.http.stream("GET", self.files + path) as response:
                response.raise_for_status()
                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > 5 * 1024 * 1024:
                        raise TelegramError("El recurso debe pesar hasta 5 MB.")
                return bytes(content)
        except httpx.HTTPError:
            raise TelegramError("No pude descargar el recurso de Telegram.") from None
