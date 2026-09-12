from django.test import SimpleTestCase
from lens.context import build_context
from lens.schemas.analysis import Mission
from .test_flow import sample_analysis

class ContextTests(SimpleTestCase):
    def test_robotics_and_boundaries(self):
        context = build_context(18, "robotica", "90", ["Sin materiales"])
        self.assertEqual(context["focus_area"], "Robótica")
        self.assertEqual(context["available_time"], 90)
        self.assertEqual(context["learner_age"], 18)

    def test_age_boundaries(self):
        for age in (3, 99):
            self.assertEqual(build_context(age, "artes", 45, ["Cartón / MDF"])["learner_age"], age)

    def test_duration_boundaries(self):
        for duration in (10, 180):
            self.assertEqual(build_context(8, "artes", duration, ["Cartón / MDF"])["available_time"], duration)

    def test_long_mission_schema(self):
        data = sample_analysis().mission.model_dump()
        data["estimated_minutes"] = 90
        self.assertEqual(Mission.model_validate(data).estimated_minutes, 90)

    def test_malformed_context(self):
        for duration in (True, "", "45.5", 0, 181):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                build_context(8, "robotica", duration, ["Sin materiales"])

    def test_malformed_age(self):
        for age in (True, "", "8.5", 2, 100, None):
            with self.subTest(age=age), self.assertRaises(ValueError):
                build_context(age, "robotica", 45, ["Sin materiales"])
