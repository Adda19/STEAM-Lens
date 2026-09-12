import io
from unittest.mock import patch
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from lens.schemas.analysis import Analysis
from lens.schemas.coach import CoachReply
from lens.services.openai_service import ProviderUnavailable

def sample_analysis():
    return Analysis.model_validate({"valid_capture": True, "retry_message": None,
        "detected_object": {"name": "Planta", "description": "Una planta en maceta.", "confidence": "high"},
        "steam_connections": [{"area": "science", "title": "Agua y vida", "explanation": "Observa sus necesidades."},
                              {"area": "mathematics", "title": "Compara hojas", "explanation": "Cuenta las hojas."}],
        "mission": {"title": "Observa tu planta", "challenge": "Compara sus hojas.", "learning_goal": "Comparar características.",
                    "difficulty": 1, "estimated_minutes": 10, "materials_required": [], "first_question": "¿Qué diferencias ves?",
                    "success_criteria": "Identifica dos diferencias."}})

def photo():
    output = io.BytesIO()
    Image.new("RGB", (50, 50), "green").save(output, "JPEG")
    return SimpleUploadedFile("plant.jpg", output.getvalue(), content_type="image/jpeg")

@override_settings(STORAGES={"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}})
class FlowTests(TestCase):
    def setUp(self):
        self.client.get("/")

    def capture(self, **extra):
        data = {"image": photo(), "age": "10", "area": "robotica", "time": "45", "materials": ["Sin materiales"]}
        data.update(extra)
        return self.client.post("/api/analyze/", data)

    def test_pages(self):
        self.assertContains(self.client.get("/"), "Comenzar a explorar")
        self.assertContains(self.client.get("/explore/"), "Explora objetos, no personas.")

    @patch("lens.views.openai_service.analyze")
    def test_invalid_inputs_do_not_call_provider(self, provider):
        for extra in [{"age": "2"}, {"age": "100"}, {"area": "inventada"}, {"time": "9"}, {"time": "181"}, {"time": "45.5"}, {"materials": ["Sin materiales", "Arduino"]},
                      {"materials": ["Unknown"]}, {"image": SimpleUploadedFile("bad.jpg", b"not an image")},
                      {"image": SimpleUploadedFile("big.jpg", b"x" * (5 * 1024 * 1024 + 1))}]:
            with self.subTest(extra=list(extra)):
                self.assertEqual(self.capture(**extra).status_code, 400)
        provider.assert_not_called()

    @patch("lens.views.openai_service.analyze")
    def test_analysis_private_fields_stay_server_side(self, provider):
        provider.return_value = sample_analysis(), "resp_private"
        response = self.capture()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("success_criteria", response.json()["mission"])
        self.assertNotContains(response, "resp_private")
        self.assertEqual(self.client.session["last_openai_response_id"], "resp_private")
        self.assertIn("success_criteria", self.client.session["mission"])
        provider.assert_called_once()

    @patch("lens.views.openai_service.analyze")
    def test_low_confidence_and_invalid_capture(self, provider):
        low = sample_analysis()
        low.detected_object.confidence = "low"
        invalid = Analysis(valid_capture=False, retry_message="Prueba otro objeto.", detected_object=None, steam_connections=[], mission=None)
        for value in (low, invalid):
            provider.return_value = value, "unused"
            response = self.capture()
            self.assertFalse(response.json()["valid_capture"])
            self.assertNotIn("mission", self.client.session)

    @patch("lens.views.openai_service.analyze", side_effect=ProviderUnavailable())
    def test_provider_error_is_safe(self, provider):
        response = self.capture()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(set(response.json()), {"error"})

    @patch("lens.views.openai_service.coach")
    def test_coach_requires_mission(self, provider):
        self.assertEqual(self.client.post("/api/coach/", {"answer": "agua"}, content_type="application/json").status_code, 409)
        provider.assert_not_called()

    @patch("lens.views.openai_service.coach")
    @patch("lens.views.openai_service.analyze")
    def test_coach_continuity_failure_completion_and_reset(self, analyze, coach):
        analyze.return_value = sample_analysis(), "resp_1"
        self.capture()
        reply = CoachReply(feedback="Bien observado.", status="continue", hint_level=0, hint=None, next_question="¿Y el tamaño?", celebration=None)
        coach.return_value = reply, "resp_2"
        response = self.client.post("/api/coach/", {"answer": "El color", "mission": "tampered"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(coach.call_args.args[3], "resp_1")
        self.assertEqual(coach.call_args.args[2]["title"], "Observa tu planta")
        coach.side_effect = ProviderUnavailable()
        self.assertEqual(self.client.post("/api/coach/", {"answer": "Tamaño"}, content_type="application/json").status_code, 503)
        self.assertEqual(self.client.session["last_openai_response_id"], "resp_2")
        coach.side_effect = None
        coach.return_value = CoachReply(feedback="Encontraste diferencias.", status="completed", hint_level=0, hint=None, next_question=None, celebration="¡Lo lograste!"), "resp_3"
        self.assertEqual(self.client.post("/api/coach/", {"answer": "Tamaño"}, content_type="application/json").status_code, 200)
        self.assertEqual(self.client.post("/api/coach/", {"answer": "Otra"}, content_type="application/json").status_code, 409)
        self.assertEqual(self.client.post("/api/reset/").status_code, 200)
        self.assertNotIn("mission", self.client.session)
        self.assertNotIn("last_openai_response_id", self.client.session)
        self.assertEqual(self.client.session["learner_age"], 10)
        self.assertEqual(self.client.session["focus_area"], "Robótica")

    def test_csrf_is_required(self):
        browser = Client(enforce_csrf_checks=True)
        browser.get("/")
        response = browser.post("/api/reset/", {}, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.json())

    def test_post_endpoints_reject_get(self):
        for endpoint in ("analyze", "coach", "reset"):
            self.assertEqual(self.client.get(f"/api/{endpoint}/").status_code, 405)
