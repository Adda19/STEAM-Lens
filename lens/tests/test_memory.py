from django.test import TestCase
from lens.telegram import memory

class MemoryTests(TestCase):
    def test_cap_enforced_at_five(self):
        for i in range(5):
            memory.add("teacher-1", "reference", "telegram", f"doc {i}", "content")
        self.assertFalse(memory.has_room("teacher-1"))
        with self.assertRaises(ValueError):
            memory.add("teacher-1", "reference", "telegram", "sixth", "content")

    def test_delete_by_position_then_room_again(self):
        for i in range(5):
            memory.add("teacher-2", "reference", "telegram", f"doc {i}", "content")
        memory.delete("teacher-2", 1)
        self.assertTrue(memory.has_room("teacher-2"))
        self.assertEqual([item.title for item in memory.list_items("teacher-2")], [f"doc {i}" for i in range(1, 5)])

    def test_delete_invalid_position_raises(self):
        memory.add("teacher-3", "reference", "telegram", "only", "content")
        with self.assertRaises(ValueError):
            memory.delete("teacher-3", 5)
        with self.assertRaises(ValueError):
            memory.delete("teacher-3", 0)

    def test_teachers_are_isolated(self):
        memory.add("teacher-a", "reference", "telegram", "a-doc", "content")
        self.assertEqual(memory.list_items("teacher-b"), [])

    def test_summary_for_prompt_excerpts_content(self):
        memory.add("teacher-4", "lesson", "telegram", "Sesión de plantas", "x" * 2000)
        summary = memory.summary_for_prompt("teacher-4")
        self.assertEqual(len(summary[0]["excerpt"]), 1500)

    def test_format_list_is_numbered_and_empty_when_none(self):
        self.assertEqual(memory.format_list("teacher-5"), "")
        memory.add("teacher-5", "reference", "drive", "Guía", "x")
        self.assertTrue(memory.format_list("teacher-5", "es").startswith("1. Guía"))
