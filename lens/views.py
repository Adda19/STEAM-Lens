import io
import json
import threading
import warnings
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from PIL import Image, ImageOps, UnidentifiedImageError
from .services import openai_service

from .context import AREAS, MATERIALS, CONTEXT_KEYS, build_context
LOCKS = [threading.Lock() for _ in range(128)]
STATE_KEYS = ["analysis_result", "mission", "last_openai_response_id", "coach_status"]

def error(message, status=400):
    return JsonResponse({"error": message}, status=status)

def csrf_failure(request, reason=""):
    return error("La sesión de seguridad cambió. Recarga la página e inténtalo de nuevo.", 403)

def serialized(view):
    """Serialize per session in the single-process MVP; save before releasing lock."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        key = request.session.session_key
        if not key:
            return error("Tu sesión terminó. Vuelve al inicio para explorar.", 409)
        with LOCKS[hash(key) % len(LOCKS)]:
            request.session = request.session.__class__(session_key=key)
            response = view(request, *args, **kwargs)
            if request.session.modified:
                request.session.save()
                request.session.modified = False
            return response
    return wrapped

@require_GET
@ensure_csrf_cookie
def index(request):
    if not request.session.session_key:
        request.session.create()
    return render(request, "lens/index.html", {"materials": MATERIALS, "areas": AREAS})

@require_GET
@ensure_csrf_cookie
def explore(request):
    if not request.session.session_key:
        request.session.create()
    return render(request, "lens/explore.html", {"configured": bool(settings.OPENAI_API_KEY)})

def context_from_form(request):
    return build_context(request.POST.get("age"), request.POST.get("area"),
                         request.POST.get("time", ""), request.POST.getlist("materials"))

def clean_image(upload):
    if not upload or upload.size > 5 * 1024 * 1024:
        raise ValueError()
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(upload) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"} or original.width * original.height > 20_000_000:
                raise ValueError()
            original.load()
            picture = ImageOps.exif_transpose(original).convert("RGB")
            picture.thumbnail((1280, 1280))
            out = io.BytesIO()
            picture.save(out, "JPEG", quality=80)  # Re-encode without original metadata.
            return out.getvalue()

@require_POST
@serialized
def analyze(request):
    try:
        context = context_from_form(request)
        image = clean_image(request.FILES.get("image"))
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        return error("Revisa edad (3 a 99 años), área, materiales y duración (10 a 180 minutos). Usa una foto JPEG, PNG o WebP de hasta 5 MB.")
    for key in STATE_KEYS:
        request.session.pop(key, None)
    try:
        result, response_id = openai_service.analyze(image, context)
    except openai_service.ProviderUnavailable:
        return error("No pude analizarlo esta vez. Probemos de nuevo.", 503)
    if not result.valid_capture or result.detected_object.confidence == "low":
        return JsonResponse({"valid_capture": False, "retry_message": result.retry_message or "No alcanzo a reconocerlo con claridad. Acércate y probemos otra vez."})
    data = result.model_dump()
    request.session.update(context)
    request.session["analysis_result"] = data
    request.session["mission"] = data["mission"]
    request.session["last_openai_response_id"] = response_id
    request.session["coach_status"] = "continue"
    public = result.model_dump()
    public["mission"].pop("success_criteria")
    return JsonResponse(public)

@require_POST
@serialized
def coach(request):
    if not request.session.get("mission") or not request.session.get("last_openai_response_id") or any(key not in request.session for key in CONTEXT_KEYS):
        return error("Tu misión ya no está disponible. Explora otro objeto.", 409)
    if request.session.get("coach_status") in {"completed", "blocked"}:
        return error("Esta misión terminó. Puedes explorar otro objeto.", 409)
    try:
        data = json.loads(request.body)
        answer = data.get("answer")
        if not isinstance(answer, str) or not 1 <= len(answer.strip()) <= 1000:
            raise ValueError()
    except (ValueError, AttributeError, UnicodeDecodeError):
        return error("Escribe una respuesta de entre 1 y 1000 caracteres.")
    context = {key: request.session[key] for key in CONTEXT_KEYS}
    try:
        result, response_id = openai_service.coach(answer.strip(), context, request.session["mission"], request.session["last_openai_response_id"])
    except openai_service.ProviderUnavailable:
        return error("No pude responder esta vez. Tu respuesta sigue aquí para reintentar.", 503)
    request.session["last_openai_response_id"] = response_id
    request.session["coach_status"] = result.status
    return JsonResponse(result.model_dump())

@require_POST
@serialized
def reset(request):
    for key in STATE_KEYS:
        request.session.pop(key, None)
    return JsonResponse({"ok": True})
