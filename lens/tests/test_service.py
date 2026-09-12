from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from pydantic import ValidationError
from lens.services import openai_service as service
from lens.schemas.analysis import Analysis
from lens.schemas.coach import CoachReply
from .test_flow import sample_analysis

@override_settings(OPENAI_API_KEY="test-key-never-real", OPENAI_MODEL="configured-model")
class ServiceTests(SimpleTestCase):
    @patch("lens.services.openai_service.OpenAI")
    def test_analysis_sends_image_and_strict_model(self, constructor):
        parse = constructor.return_value.__enter__.return_value.responses.parse
        parse.return_value = SimpleNamespace(status="completed", output_parsed=sample_analysis(), id="resp_1")
        service.analyze(b"jpeg", {"available_time": 20})
        args = parse.call_args.kwargs
        self.assertEqual(args["model"], "configured-model")
        self.assertIs(args["text_format"], Analysis)
        self.assertTrue(args["input"][0]["content"][1]["image_url"].startswith("data:image/jpeg;base64,"))
        self.assertEqual(constructor.call_args.kwargs["max_retries"], 0)

    @patch("lens.services.openai_service.OpenAI")
    def test_incomplete_rejected(self, constructor):
        constructor.return_value.__enter__.return_value.responses.parse.return_value = SimpleNamespace(status="incomplete", output_parsed=None)
        with self.assertRaises(service.ProviderUnavailable):
            service.analyze(b"jpeg", {"available_time": 20})

    @override_settings(OPENAI_API_KEY="")
    @patch("lens.services.openai_service.OpenAI")
    def test_missing_key_makes_no_request(self, constructor):
        with self.assertRaises(service.ProviderUnavailable):
            service.analyze(b"jpeg", {"available_time": 20})
        constructor.assert_not_called()

    def test_invalid_capture_cannot_contain_mission(self):
        data = sample_analysis().model_dump()
        data["valid_capture"] = False
        with self.assertRaises(ValidationError):
            Analysis.model_validate(data)

    def test_completed_has_no_followup_question(self):
        with self.assertRaises(ValidationError):
            CoachReply(feedback="Bien", status="completed", hint_level=0, hint=None, next_question="¿Otra?", celebration=None)
