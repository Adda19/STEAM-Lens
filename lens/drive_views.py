"""The one part of the Google Drive connection that can't happen inside Telegram: the browser
redirect Google sends the teacher back to after they grant (or refuse) access."""
from html import escape
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from .models import TeacherDriveConnection
from .telegram import drive

def _page(message):
    return HttpResponse(
        f"<!doctype html><html><body style='font-family:sans-serif;max-width:32rem;margin:3rem auto;padding:0 1rem;line-height:1.5'>"
        f"<h1>STEAM Lens</h1><p>{escape(message)}</p></body></html>", content_type="text/html; charset=utf-8")

@require_GET
def drive_callback(request):
    if request.GET.get("error"):
        return _page("No se completó la conexión: el permiso fue rechazado en Google. Vuelve a Telegram y escribe /drive para intentarlo de nuevo.")
    teacher_key = drive.resolve_connect_state(request.GET.get("state", ""))
    code = request.GET.get("code", "")
    if not teacher_key or not code:
        return _page("Este enlace ya venció o no es válido. Vuelve a Telegram y escribe /drive para generar uno nuevo.")
    try:
        refresh_token = drive.exchange_code_for_refresh_token(code)
    except Exception:
        return _page("Google no confirmó la conexión. Vuelve a Telegram y escribe /drive para intentarlo de nuevo.")
    TeacherDriveConnection.objects.update_or_create(teacher_key=teacher_key, defaults={"refresh_token": refresh_token})
    return _page("Cuenta de Google conectada. Vuelve a Telegram y envía el enlace o el ID de la carpeta que quieres usar (hasta 5 archivos).")
