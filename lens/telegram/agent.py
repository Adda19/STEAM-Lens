import hashlib
import hmac
import io
import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from lens.context import AGE_MIN, AGE_MAX, AREAS, MATERIALS, build_context
from lens.services.openai_service import ProviderUnavailable
from lens.views import clean_image
from .client import TelegramError
from . import drive, i18n, lesson, memory

# Several spellings per command so the bot answers to whichever language the person types in,
# even before /idioma or the language buttons have run.
START_COMMANDS = {"/start", "/nueva", "/new", "/nouvelle"}
CANCEL_COMMANDS = {"/cancelar", "/cancel", "/annuler"}
DELETE_COMMANDS = {"/borrar", "/delete", "/effacer"}
CONTINUE_COMMANDS = {"/continuar", "/continue", "/continuer"}
HELP_COMMANDS = {"/ayuda", "/help", "/aide"}
LANGUAGE_COMMANDS = {"/idioma", "/language", "/langue"}
PDF_COMMAND = "/pdf"
MEMORY_LIST_COMMANDS = {"/memoria", "/memory", "/memoire"}
MEMORY_DELETE_COMMANDS = {"/memoria_borrar", "/memory_delete", "/memoire_supprimer"}
MEMORY_SAVE_COMMANDS = {"/memoria_guardar", "/memory_save", "/memoire_sauvegarder"}
DRIVE_COMMAND = "/drive"

class Agent:
    def __init__(self, client):
        self.client = client

    def key(self, chat):
        return hmac.new(settings.SECRET_KEY.encode(), f"telegram:{chat}".encode(), hashlib.sha256).hexdigest()[:32]

    def load(self, chat):
        record = Session.objects.filter(session_key=self.key(chat), expire_date__gt=timezone.now()).first()
        return record.get_decoded() if record else {}

    def save(self, chat, state):
        Session.objects.update_or_create(session_key=self.key(chat), defaults={
            "session_data": SessionStore().encode(state), "expire_date": timezone.now() + timedelta(hours=1)})

    def context(self, state):
        return build_context(state.get("age"), state.get("area"), state.get("minutes"), state.get("materials"))

    def ask(self, chat, state, introduction=""):
        nonce = secrets.token_hex(3)
        state["nonce"] = nonce
        language = state.get("language")
        rows = []
        def buttons(items, prefix):
            return [[{"text": label, "callback_data": f"{nonce}:{prefix}:{code}"}] for code, label in items]
        if not language:
            question = i18n.TEXT["language"][0]
            rows = buttons(list(i18n.LANGUAGES.items()), "language")
        elif not state.get("age"):
            question = i18n.tr(language, "age")
        elif not state.get("area"):
            question = i18n.tr(language, "area")
            rows = buttons([(code, i18n.area_label(code, language)) for code in dict(AREAS)], "area")
        elif not state.get("minutes"):
            question = i18n.tr(language, "duration")
            unit = i18n.tr(language, "minutes")
            rows = buttons([(str(n), f"{n} {unit}") for n in (20, 45, 60, 90)], "minutes")
        elif not state.get("materials_confirmed"):
            question = i18n.tr(language, "materials")
            chosen = state.get("materials", [])
            idx = i18n.index(language)
            rows = buttons([(str(i), ("✓ " if material in chosen else "") + i18n.MATERIAL_LABELS[i][idx])
                            for i, material in enumerate(MATERIALS)], "material")
            rows.append([{"text": i18n.tr(language, "done"), "callback_data": f"{nonce}:done:yes"}])
        elif not state.get("resource"):
            question = i18n.tr(language, "resource")
        elif not state.get("previous_sessions_asked"):
            if state.get("previous_sessions_stage") == "awaiting_text":
                question = i18n.tr(language, "previous_sessions_ask")
            else:
                question = i18n.tr(language, "previous_sessions_prompt")
                rows = buttons([("yes", i18n.tr(language, "yes")), ("no", i18n.tr(language, "no"))], "previous_sessions")
        else:
            question = i18n.tr(language, "ready")
            rows = buttons([("yes", i18n.tr(language, "generate"))], "generate")
        self.save(chat, state)
        self.client.send(chat, (introduction + "\n\n" if introduction else "") + question, rows)

    def handle(self, update):
        callback = update.get("callback_query")
        message = callback.get("message", {}) if callback else update.get("message", {})
        chat_info = message.get("chat", {})
        if chat_info.get("type") != "private":
            return
        chat = chat_info["id"]
        if callback and callback.get("from", {}).get("id") != chat:
            return
        state = self.load(chat)
        if update["update_id"] <= state.get("last_update", -1):
            return
        # Persist before processing; a /continuar or /pdf recovers from delivery failures.
        state["last_update"] = update["update_id"]
        self.save(chat, state)
        language = state.get("language", "es")
        text = message.get("text", "").strip() if not callback else ""
        command = text.split(" ")[0].lower() if text else ""
        try:
            if callback:
                self.client.call("answerCallbackQuery", {"callback_query_id": callback["id"]})
                parts = callback.get("data", "").split(":", 2)
                if len(parts) != 3 or parts[0] != state.get("nonce"):
                    self.ask(chat, state, i18n.tr(language, "old_button"))
                    return
                self.on_button(chat, state, parts[1], parts[2])
                return
            if command in START_COMMANDS or command in CANCEL_COMMANDS:
                state = {"last_update": update["update_id"]}
                self.ask(chat, state, "\n".join(i18n.TEXT["welcome"]))
                return
            if command in DELETE_COMMANDS:
                Session.objects.filter(session_key=self.key(chat)).delete()
                self.client.send(chat, i18n.tr(language, "deleted"))
                return
            if command in LANGUAGE_COMMANDS:
                state.pop("language", None)
                self.ask(chat, state)
                return
            if command in MEMORY_LIST_COMMANDS or command in MEMORY_DELETE_COMMANDS or command in MEMORY_SAVE_COMMANDS or command == DRIVE_COMMAND:
                self.handle_memory_command(chat, state, language, command, text)
                return
            if state.get("awaiting_drive_folder") and text:
                self.handle_drive_folder(chat, state, language, text)
                return
            if command == PDF_COMMAND and state.get("lesson"):
                self.deliver(chat, state)
                return
            if command in CONTINUE_COMMANDS or command in HELP_COMMANDS or command == PDF_COMMAND:
                self.ask(chat, state)
                return
            if not state.get("language"):
                # First contact must pick a language via buttons before anything else is interpreted.
                self.ask(chat, state)
                return
            if not state.get("age") and text.strip().isdigit():
                # A bare number answering "how old" doesn't need an AI round trip.
                age = int(text.strip())
                if not AGE_MIN <= age <= AGE_MAX:
                    raise ValueError("Invalid age")
                state["age"] = age
                self.ask(chat, state)
                return
            if state.get("previous_sessions_stage") == "awaiting_text" and text:
                # Free-form recap of earlier classes: captured as-is, no AI round trip needed either.
                state["previous_sessions"] = text[:2000]
                state["previous_sessions_asked"] = True
                state.pop("previous_sessions_stage", None)
                self.ask(chat, state)
                return
            if message.get("photo") or message.get("document"):
                self.receive_resource(chat, state, message)
                return
            if not text:
                self.ask(chat, state, i18n.tr(language, "unsupported"))
                return
            if len(text) > 4000:
                self.client.send(chat, i18n.tr(language, "long"))
                return
            self.client.call("sendChatAction", {"chat_id": chat, "action": "typing"})
            # The model interprets natural language, revises known slots and chooses the next action.
            public_state = {key: value for key, value in state.items() if key not in {"nonce", "last_update"}}
            if public_state.get("resource"):
                public_state["resource"] = {"kind": state["resource"]["kind"], "summary": state["resource"].get("text", "Recurso adjunto disponible")[:12000]}
            decision = lesson.decide(text, public_state, language)
            candidate = dict(state)
            if decision.area is not None:
                if decision.area not in dict(AREAS):
                    raise ValueError("Unrecognized option")
                candidate["area"] = decision.area
            if decision.age is not None:
                if isinstance(decision.age, bool) or not AGE_MIN <= decision.age <= AGE_MAX:
                    raise ValueError("Invalid age")
                candidate["age"] = decision.age
            if decision.minutes is not None:
                if not 10 <= decision.minutes <= 180:
                    raise ValueError("Invalid duration")
                candidate["minutes"] = decision.minutes
            if decision.materials is not None:
                build_context(AGE_MIN, "integrado", 45, decision.materials)
                candidate["materials"] = decision.materials
                candidate["materials_confirmed"] = True
            if decision.resource_text:
                candidate["resource"] = {"kind": "text", "text": decision.resource_text[:20000]}
            self.save(chat, candidate)
            ready = all(candidate.get(key) for key in ("age", "area", "minutes", "materials_confirmed", "resource", "previous_sessions_asked"))
            if ready and decision.action in {"generate", "revise"}:
                self.generate(chat, candidate, text if decision.action == "revise" else "")
            elif decision.action == "talk":
                self.client.send(chat, decision.message)
            else:
                self.ask(chat, candidate, decision.message)
        except ProviderUnavailable:
            self.client.send(chat, i18n.tr(language, "provider_error"))
        except ValueError:
            self.ask(chat, self.load(chat), i18n.tr(language, "invalid"))

    def on_button(self, chat, state, field, value):
        language = state.get("language")
        if field == "language":
            if value not in i18n.LANGUAGES:
                raise ValueError()
            state["language"] = value
        elif field == "area":
            if value not in dict(AREAS):
                raise ValueError()
            state["area"] = value
        elif field == "minutes":
            if not value.isdigit() or not 10 <= int(value) <= 180:
                raise ValueError()
            state["minutes"] = int(value)
        elif field == "material":
            if not value.isdigit() or int(value) >= len(MATERIALS):
                raise ValueError()
            material = MATERIALS[int(value)]
            chosen = state.get("materials", []).copy()
            if material in chosen:
                chosen.remove(material)
            elif material == "Sin materiales":
                chosen = [material]
            else:
                chosen = [m for m in chosen if m != "Sin materiales"] + [material]
            state["materials"] = chosen
        elif field == "done":
            if not state.get("materials"):
                self.ask(chat, state, i18n.tr(language, "choose_material"))
                return
            state["materials_confirmed"] = True
        elif field == "previous_sessions":
            if value == "yes":
                state["previous_sessions_stage"] = "awaiting_text"
            elif value == "no":
                state["previous_sessions_asked"] = True
                state["previous_sessions"] = None
            else:
                raise ValueError()
        elif field == "generate":
            self.context(state)
            if not state.get("resource"):
                raise ValueError()
            self.generate(chat, state)
            return
        else:
            raise ValueError()
        self.ask(chat, state)

    def handle_memory_command(self, chat, state, language, command, text):
        teacher_key = self.key(chat)
        if command in MEMORY_LIST_COMMANDS:
            listing = memory.format_list(teacher_key, language)
            self.client.send(chat, listing or i18n.tr(language, "memory_empty"))
        elif command in MEMORY_DELETE_COMMANDS:
            parts = text.split()
            if len(parts) != 2 or not parts[1].isdigit():
                self.client.send(chat, i18n.tr(language, "memory_delete_usage"))
                return
            try:
                memory.delete(teacher_key, int(parts[1]))
                self.client.send(chat, i18n.tr(language, "memory_deleted"))
            except ValueError:
                self.client.send(chat, i18n.tr(language, "memory_invalid_index"))
        elif command in MEMORY_SAVE_COMMANDS:
            if not state.get("lesson"):
                self.client.send(chat, i18n.tr(language, "memory_nothing_to_save"))
            elif not memory.has_room(teacher_key):
                self.client.send(chat, i18n.tr(language, "memory_full") + "\n\n" + memory.format_list(teacher_key, language))
            else:
                import json
                memory.add(teacher_key, "lesson", "telegram", state["lesson"].get("title", ""), json.dumps(state["lesson"], ensure_ascii=False))
                self.client.send(chat, i18n.tr(language, "memory_saved"))
        elif command == DRIVE_COMMAND:
            if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
                self.client.send(chat, i18n.tr(language, "drive_not_configured"))
                return
            state["awaiting_drive_folder"] = True
            url = drive.authorization_url(drive.create_connect_state(teacher_key))
            self.save(chat, state)
            self.client.send(chat, i18n.tr(language, "drive_connect_prompt") + "\n" + url)

    def handle_drive_folder(self, chat, state, language, text):
        from lens.models import MAX_MEMORY_ITEMS, TeacherDriveConnection
        teacher_key = self.key(chat)
        connection = TeacherDriveConnection.objects.filter(teacher_key=teacher_key).first()
        if not connection:
            self.client.send(chat, i18n.tr(language, "drive_not_connected_yet"))
            return
        folder_id = drive.parse_folder_id(text)
        if not folder_id:
            self.client.send(chat, i18n.tr(language, "drive_bad_folder"))
            return
        state.pop("awaiting_drive_folder", None)
        self.save(chat, state)
        room = MAX_MEMORY_ITEMS - len(memory.list_items(teacher_key))
        if room <= 0:
            self.client.send(chat, i18n.tr(language, "memory_full") + "\n\n" + memory.format_list(teacher_key, language))
            return
        connection.folder_id = folder_id
        connection.save(update_fields=["folder_id"])
        try:
            files = drive.list_folder_files(connection.refresh_token, folder_id, room)
        except Exception:
            self.client.send(chat, i18n.tr(language, "drive_error"))
            return
        imported = 0
        for file in files:
            try:
                extracted = drive.read_file_text(connection.refresh_token, file["id"], file["mimeType"])
            except Exception:
                continue
            if len(extracted.strip()) < 20:
                continue
            memory.add(teacher_key, "reference", "drive", file["name"], extracted)
            imported += 1
        self.client.send(chat, i18n.tr(language, "drive_imported").format(count=imported))

    def receive_resource(self, chat, state, message):
        language = state.get("language", "es")
        if message.get("photo"):
            item = message["photo"][-1]
            kind = "image"
        else:
            item = message["document"]
            mime = item.get("mime_type", "")
            kind = {"application/pdf": "pdf", "text/plain": "textfile", "image/jpeg": "image", "image/png": "image", "image/webp": "image"}.get(mime)
            if not kind:
                self.client.send(chat, i18n.tr(language, "unsupported"))
                return
        if item.get("file_size", 0) > 5 * 1024 * 1024:
            self.client.send(chat, i18n.tr(language, "size"))
            return
        state["resource"] = {"kind": kind, "file_id": item["file_id"], "text": message.get("caption", "")[:4000]}
        self.save(chat, state)
        if all(state.get(k) for k in ("age", "area", "minutes", "materials_confirmed", "previous_sessions_asked")):
            self.generate(chat, state)
        else:
            self.ask(chat, state, i18n.tr(language, "received"))

    def generate(self, chat, state, revision=""):
        language = state.get("language", "es")
        context = self.context(state)
        resource = state["resource"]
        image = None
        text = resource.get("text", "")
        self.client.send(chat, i18n.tr(language, "working"))
        if "file_id" in resource:
            data = self.client.download(resource["file_id"])
            if resource["kind"] == "image":
                try:
                    image = clean_image(SimpleUploadedFile("resource", data))
                except Exception:
                    state.pop("resource", None)
                    self.ask(chat, state, i18n.tr(language, "bad_image"))
                    return
            else:
                try:
                    if resource["kind"] == "pdf":
                        from pypdf import PdfReader
                        reader = PdfReader(io.BytesIO(data))
                        if reader.is_encrypted or len(reader.pages) > 20:
                            raise ValueError()
                        extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
                    else:
                        extracted = data.decode("utf-8-sig")
                    if len(extracted.strip()) < 20 or len(extracted) > 20000:
                        raise ValueError()
                    text += "\n" + extracted
                except Exception:
                    state.pop("resource", None)
                    self.ask(chat, state, i18n.tr(language, "bad_document"))
                    return
        self.client.send(chat, i18n.tr(language, "verifying"))
        result = lesson.generate(context, text, image, state.get("lesson") if revision else None, revision, language,
                                 state.get("previous_sessions"), memory.summary_for_prompt(self.key(chat)))
        if not result.ready:
            state.pop("resource", None)
            self.ask(chat, state, result.message)
            return
        state["lesson"] = result.lesson.model_dump()
        state["lesson_context"] = context
        state.pop("nonce", None)
        self.save(chat, state)
        self.deliver(chat, state)

    def deliver(self, chat, state):
        language = state.get("language", "es")
        pdf = lesson.render_pdf(lesson.Lesson.model_validate(state["lesson"]), state["lesson_context"], language)
        self.client.document(chat, pdf, i18n.tr(language, "caption"))
        self.client.send(chat, i18n.tr(language, "after"))
