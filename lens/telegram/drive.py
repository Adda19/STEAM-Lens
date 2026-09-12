"""Google Drive integration for teacher memory: connect once, read a folder's files as reference
material. Read-only scope, one folder per teacher. The OAuth handshake needs a browser (it can't
happen inside Telegram), so /drive sends a link and lens/drive_views.py catches the redirect back;
django.core.cache bridges the two by mapping a short-lived random `state` to the teacher's key.

Requires GOOGLE_OAUTH_CLIENT_ID/SECRET/REDIRECT_URI in settings — see docs/TELEGRAM.md for how to
create them in Google Cloud Console. Without them, ProviderUnavailable-style errors surface as a
plain RuntimeError rather than a cryptic library exception.
"""
import io
import secrets
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

STATE_TTL = timedelta(minutes=10)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
SUPPORTED_MIME_TYPES = {GOOGLE_DOC_MIME, "application/pdf", "text/plain"}

class DriveNotConfigured(Exception):
    pass

def _require_config():
    if not (settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET):
        raise DriveNotConfigured("GOOGLE_OAUTH_CLIENT_ID/SECRET missing from settings")

def _flow():
    from google_auth_oauthlib.flow import Flow
    _require_config()
    return Flow.from_client_config({"web": {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }}, scopes=SCOPES, redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI)

def create_connect_state(teacher_key):
    """The OAuth handshake happens in a browser with no notion of a Telegram chat, and the bot
    (this call) and the web server (resolve_connect_state) run as separate processes — a row in
    the shared SQLite file bridges them for up to STATE_TTL, an in-memory cache would not."""
    from lens.models import DriveConnectState
    state = secrets.token_urlsafe(24)
    DriveConnectState.objects.create(state=state, teacher_key=teacher_key)
    return state

def resolve_connect_state(state):
    from lens.models import DriveConnectState
    record = DriveConnectState.objects.filter(state=state, created_at__gt=timezone.now() - STATE_TTL).first()
    if not record:
        return None
    teacher_key = record.teacher_key
    record.delete()
    return teacher_key

def authorization_url(state):
    url, _ = _flow().authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true", state=state)
    return url

def exchange_code_for_refresh_token(code):
    flow = _flow()
    flow.fetch_token(code=code)
    if not flow.credentials.refresh_token:
        # Happens if the teacher already granted access before without revoking it first.
        raise RuntimeError("Google no devolvió un refresh_token; revoca el acceso previo en myaccount.google.com/permissions y vuelve a intentar /drive.")
    return flow.credentials.refresh_token

def _credentials(refresh_token):
    from google.oauth2.credentials import Credentials
    _require_config()
    return Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token",
                       client_id=settings.GOOGLE_OAUTH_CLIENT_ID, client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET)

def _service(refresh_token):
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=_credentials(refresh_token), cache_discovery=False)

def parse_folder_id(text):
    """Accepts either a bare folder id or a drive.google.com/drive/folders/<id> link."""
    import re
    match = re.search(r"folders/([\w-]{10,})", text)
    if match:
        return match.group(1)
    token = text.strip().split("?")[0]
    return token if re.fullmatch(r"[\w-]{10,}", token) else None

def list_folder_files(refresh_token, folder_id, limit):
    from googleapiclient.errors import HttpError
    try:
        response = _service(refresh_token).files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)", pageSize=max(limit, 1)).execute()
    except HttpError as exc:
        raise RuntimeError(f"Google Drive rechazó la solicitud (HTTP {exc.resp.status}). Revisa el enlace de la carpeta y que la compartiste con la cuenta que autorizó.") from None
    return [f for f in response.get("files", []) if f.get("mimeType") in SUPPORTED_MIME_TYPES][:limit]

def read_file_text(refresh_token, file_id, mime_type):
    from googleapiclient.http import MediaIoBaseDownload
    service = _service(refresh_token)
    if mime_type == GOOGLE_DOC_MIME:
        return service.files().export(fileId=file_id, mimeType="text/plain").execute().decode("utf-8", errors="ignore")
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, service.files().get_media(fileId=file_id))
    done = False
    while not done:
        _, done = downloader.next_chunk()
    raw = buffer.getvalue()
    if mime_type == "application/pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        if reader.is_encrypted:
            return ""
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return raw.decode("utf-8-sig", errors="ignore")
