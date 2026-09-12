import io
from unittest.mock import MagicMock, patch
from django.test import TestCase, SimpleTestCase, override_settings
from pypdf import PdfReader
from lens.telegram.agent import Agent
from lens.telegram.lesson import Lesson, LessonResult, Decision, render_pdf
from lens.telegram import memory
from lens.context import build_context

def example_lesson():
    return Lesson(title="Detectives de las hojas", resource_summary="Observación de una planta.",
        learning_goals=["Comparar hojas."], steam_connections=["Ciencia: observar", "Matemáticas: comparar"], materials=["Sin materiales"],
        phases=[{"title": title, "minutes": 15, "activities": ["Observa dos hojas y compara sin arrancarlas."],
                 "guiding_question": "¿Qué diferencia ves?", "hint": "Fíjate en el tamaño.", "evidence": "Describe una diferencia."}
                for title in ("Inicio", "Exploración", "Cierre")], assessment=["Describe dos diferencias."],
        adaptations=["Explicar oralmente si no se quiere escribir."], safety=["No arrancar ni probar hojas."],
        core_skills=["Pensamiento crítico y resolución de problemas"],
        sources=["Doc_Oficial: curriculo_internacional (banda 8-10)"],
        external_resources=[
            {"kind": "video", "topic": "cómo germina una semilla time lapse", "note": "Muestra el crecimiento que no se ve en una sola clase."},
            {"kind": "document", "topic": "guía de observación de plantas para primaria", "note": "Ficha imprimible para registrar observaciones."},
            {"kind": "simulation", "topic": "states-of-matter", "note": "Complementa con estados de la materia si surge el tema del agua."}])

class TelegramTests(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.agent = Agent(self.client)
        self.serial = 0

    def message(self, text="", **extra):
        self.serial += 1
        self.agent.handle({"update_id": self.serial, "message": {"chat": {"id": 77, "type": "private"}, "text": text, **extra}})

    def click(self, field, value):
        state = self.agent.load(77)
        self.serial += 1
        self.agent.handle({"update_id": self.serial, "callback_query": {"id": "callback", "from": {"id": 77},
            "message": {"chat": {"id": 77, "type": "private"}}, "data": f"{state['nonce']}:{field}:{value}"}})

    def configure(self):
        self.message("/start")
        self.click("language", "es")
        self.message("8")
        self.click("area", "naturales")
        self.click("minutes", "45")
        self.click("material", "0")
        self.click("done", "yes")

    @patch("lens.telegram.lesson.generate")
    @patch("lens.telegram.lesson.decide")
    def test_buttons_resource_pdf_revision_and_delete(self, decide, generate):
        self.configure()
        decide.return_value = Decision(age=None, area=None, minutes=None, materials=None,
            resource_text="Una planta en maceta para observar las hojas.", action="ask", message="¿Algo más?")
        generate.return_value = LessonResult(ready=True, message="Lista", lesson=example_lesson())
        self.message("Una planta en maceta para observar las hojas.")
        self.assertEqual(self.client.document.call_count, 0)  # still pending the previous-sessions question
        self.click("previous_sessions", "no")
        self.click("generate", "yes")
        self.assertEqual(self.client.document.call_count, 1)
        self.assertTrue(self.client.document.call_args.args[1].startswith(b"%PDF"))
        decide.return_value = Decision(age=9, area=None, minutes=None, materials=None, resource_text=None, action="revise", message="La adaptaré.")
        self.message("Adáptala a nueve años")
        self.assertEqual(self.agent.load(77)["age"], 9)
        self.assertEqual(generate.call_args.args[0]["learner_age"], 9)
        self.assertIsNotNone(generate.call_args.args[3])
        self.assertEqual(generate.call_args.args[5], "es")
        self.assertIsNone(generate.call_args.args[6])
        self.assertEqual(self.client.document.call_count, 2)
        self.message("/pdf")
        self.assertEqual(self.client.document.call_count, 3)
        self.message("/borrar")
        self.assertEqual(self.agent.load(77), {})

    @patch("lens.telegram.lesson.generate")
    @patch("lens.telegram.lesson.decide")
    def test_previous_sessions_text_is_forwarded_to_generate(self, decide, generate):
        self.configure()
        decide.return_value = Decision(age=None, area=None, minutes=None, materials=None,
            resource_text="Una planta en maceta.", action="ask", message="¿Algo más?")
        generate.return_value = LessonResult(ready=True, message="Lista", lesson=example_lesson())
        self.message("Una planta en maceta.")
        self.click("previous_sessions", "yes")
        self.message("Ya vimos partes de la planta; les costó distinguir tallo de raíz.")
        state = self.agent.load(77)
        self.assertTrue(state["previous_sessions_asked"])
        self.assertIn("distinguir tallo de raíz", state["previous_sessions"])
        self.click("generate", "yes")
        self.assertEqual(generate.call_args.args[6], "Ya vimos partes de la planta; les costó distinguir tallo de raíz.")

    @patch("lens.telegram.lesson.generate")
    def test_photo_is_downloaded_and_not_stored_in_session(self, generate):
        from PIL import Image
        out = io.BytesIO()
        Image.new("RGB", (20, 20), "green").save(out, "JPEG")
        self.client.download.return_value = out.getvalue()
        generate.return_value = LessonResult(ready=False, message="Necesito otro recurso", lesson=None)
        self.configure()
        self.message(photo=[{"file_id": "telegram-file", "file_size": 1000}])
        self.click("previous_sessions", "no")
        self.click("generate", "yes")
        self.assertIsInstance(generate.call_args.args[2], bytes)
        self.assertNotIn("resource", self.agent.load(77))

    def test_material_exclusivity(self):
        self.configure()
        state = self.agent.load(77)
        state.pop("materials_confirmed")
        self.agent.save(77, state)
        self.agent.ask(77, state)
        self.click("material", "1")
        self.assertEqual(self.agent.load(77)["materials"], ["Arduino"])

    def test_bare_number_sets_age_without_ai_call(self):
        self.message("/start")
        self.click("language", "es")
        self.message("8")
        self.assertEqual(self.agent.load(77)["age"], 8)

    def test_duplicate_update_not_processed(self):
        update = {"update_id": 100, "message": {"chat": {"id": 77, "type": "private"}, "text": "/start"}}
        self.agent.handle(update)
        count = self.client.send.call_count
        self.agent.handle(update)
        self.assertEqual(self.client.send.call_count, count)

    def test_chats_isolated_and_groups_ignored(self):
        self.configure()
        self.assertEqual(self.agent.load(88), {})
        self.agent.handle({"update_id": 100, "message": {"chat": {"id": 99, "type": "group"}, "text": "/start"}})
        self.assertEqual(self.agent.load(99), {})

    def test_language_command_resets_language_only(self):
        self.configure()
        self.message("/idioma")
        state = self.agent.load(77)
        self.assertNotIn("language", state)
        self.assertEqual(state["age"], 8)

    @patch("lens.telegram.lesson.generate")
    @patch("lens.telegram.lesson.decide")
    def test_memory_save_list_and_delete(self, decide, generate):
        self.configure()
        decide.return_value = Decision(age=None, area=None, minutes=None, materials=None,
            resource_text="Una planta en maceta.", action="ask", message="¿Algo más?")
        generate.return_value = LessonResult(ready=True, message="Lista", lesson=example_lesson())
        self.message("Una planta en maceta.")
        self.click("previous_sessions", "no")
        self.click("generate", "yes")
        self.message("/memoria_guardar")
        self.assertIn("Guardé esta sesión", self.client.send.call_args.args[1])
        self.message("/memoria")
        self.assertIn("Detectives de las hojas", self.client.send.call_args.args[1])
        self.message("/memoria_borrar 1")
        self.assertIn("eliminé", self.client.send.call_args.args[1])
        self.message("/memoria")
        self.assertIn("Aún no tienes nada guardado", self.client.send.call_args.args[1])

    def test_memory_save_without_lesson_is_a_no_op(self):
        self.message("/start")
        self.click("language", "es")
        self.message("/memoria_guardar")
        self.assertIn("No tienes una sesión reciente", self.client.send.call_args.args[1])
        self.assertEqual(memory.list_items(self.agent.key(77)), [])

    @patch("lens.telegram.lesson.generate")
    @patch("lens.telegram.lesson.decide")
    def test_memory_full_blocks_save(self, decide, generate):
        self.configure()
        teacher_key = self.agent.key(77)
        for i in range(5):
            memory.add(teacher_key, "reference", "telegram", f"doc{i}", "x")
        decide.return_value = Decision(age=None, area=None, minutes=None, materials=None,
            resource_text="Una planta en maceta.", action="ask", message="¿Algo más?")
        generate.return_value = LessonResult(ready=True, message="Lista", lesson=example_lesson())
        self.message("Una planta en maceta.")
        self.click("previous_sessions", "no")
        self.click("generate", "yes")
        self.message("/memoria_guardar")
        self.assertIn("máximo", self.client.send.call_args.args[1])
        self.assertEqual(len(memory.list_items(teacher_key)), 5)

class DriveTests(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.agent = Agent(self.client)
        self.serial = 0

    def message(self, text="", **extra):
        self.serial += 1
        self.agent.handle({"update_id": self.serial, "message": {"chat": {"id": 55, "type": "private"}, "text": text, **extra}})

    def click(self, field, value):
        state = self.agent.load(55)
        self.serial += 1
        self.agent.handle({"update_id": self.serial, "callback_query": {"id": "callback", "from": {"id": 55},
            "message": {"chat": {"id": 55, "type": "private"}}, "data": f"{state['nonce']}:{field}:{value}"}})

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="", GOOGLE_OAUTH_CLIENT_SECRET="")
    def test_drive_not_configured(self):
        self.message("/start")
        self.click("language", "es")
        self.message("/drive")
        self.assertIn("no está configurada", self.client.send.call_args.args[1])

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="test-id", GOOGLE_OAUTH_CLIENT_SECRET="test-secret")
    def test_drive_command_sends_link_and_awaits_folder(self):
        self.message("/start")
        self.click("language", "es")
        self.message("/drive")
        state = self.agent.load(55)
        self.assertTrue(state["awaiting_drive_folder"])
        self.assertIn("accounts.google.com", self.client.send.call_args.args[1])

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="test-id", GOOGLE_OAUTH_CLIENT_SECRET="test-secret")
    def test_drive_folder_without_connection_prompts_to_authorize(self):
        self.message("/start")
        self.click("language", "es")
        self.message("/drive")
        self.message("https://drive.google.com/drive/folders/abcdefghij1234567890")
        self.assertIn("Primero autoriza", self.client.send.call_args.args[1])

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="test-id", GOOGLE_OAUTH_CLIENT_SECRET="test-secret")
    @patch("lens.telegram.drive.read_file_text")
    @patch("lens.telegram.drive.list_folder_files")
    def test_drive_folder_imports_files_into_memory(self, list_files, read_text):
        from lens.models import TeacherDriveConnection
        self.message("/start")
        self.click("language", "es")
        self.message("/drive")
        teacher_key = self.agent.key(55)
        TeacherDriveConnection.objects.create(teacher_key=teacher_key, refresh_token="fake-token")
        list_files.return_value = [{"id": "f1", "name": "Guía de ondas", "mimeType": "application/pdf"}]
        read_text.return_value = "Contenido suficiente de prueba " * 3
        self.message("https://drive.google.com/drive/folders/abcdefghij1234567890")
        items = memory.list_items(teacher_key)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, "drive")
        self.assertEqual(items[0].title, "Guía de ondas")
        self.assertIn("Importé 1", self.client.send.call_args.args[1])

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="test-id", GOOGLE_OAUTH_CLIENT_SECRET="test-secret")
    def test_drive_folder_respects_full_memory(self):
        from lens.models import TeacherDriveConnection
        self.message("/start")
        self.click("language", "es")
        teacher_key = self.agent.key(55)
        for i in range(5):
            memory.add(teacher_key, "reference", "telegram", f"doc{i}", "x")
        self.message("/drive")
        TeacherDriveConnection.objects.create(teacher_key=teacher_key, refresh_token="fake-token")
        self.message("https://drive.google.com/drive/folders/abcdefghij1234567890")
        self.assertIn("máximo", self.client.send.call_args.args[1])
        self.assertEqual(len(memory.list_items(teacher_key)), 5)

class PdfTests(SimpleTestCase):
    def test_pdf_readable_and_escaped(self):
        value = example_lesson()
        value.title = "Sesión <práctica> & observación"
        pdf = render_pdf(value, build_context(8, "naturales", 45, ["Sin materiales"]), "es")
        reader = PdfReader(io.BytesIO(pdf))
        text = "\n".join(page.extract_text() for page in reader.pages)
        self.assertIn("Sesión <práctica> & observación", text)
        self.assertIn("Evaluación y cierre", text)
        self.assertIn("45 minutos", text)
        self.assertIn("Fuentes y trazabilidad", text)
        self.assertIn("Recursos para profundizar", text)
        self.assertIn("youtube.com/results", text)
        self.assertIn("google.com/search", text)
        self.assertIn("phet.colorado.edu/es/simulations/states-of-matter", text)

    def test_pdf_localized_in_english(self):
        pdf = render_pdf(example_lesson(), build_context(8, "naturales", 45, ["Sin materiales"]), "en")
        reader = PdfReader(io.BytesIO(pdf))
        text = "\n".join(page.extract_text() for page in reader.pages)
        self.assertIn("Assessment and closure", text)
        self.assertIn("Sources and traceability", text)
        self.assertIn("phet.colorado.edu/en/simulations/states-of-matter", text)

    def test_resources_require_video_and_document(self):
        data = example_lesson().model_dump()
        data["external_resources"] = [{"kind": "simulation", "topic": "states-of-matter", "note": "x"},
                                       {"kind": "simulation", "topic": "ph-scale", "note": "y"}]
        with self.assertRaises(ValueError):
            Lesson.model_validate(data)
