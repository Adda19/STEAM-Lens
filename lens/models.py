"""Persistent per-teacher memory: reference material the teacher supplies — uploaded through
Telegram or read from a connected Google Drive folder — plus sessions STEAM Lens already
generated for them, so they can come back and adjust one without re-uploading anything.

Unlike the Telegram conversation state (django.contrib.sessions, expires after 1 hour of
inactivity), this survives across days until the teacher deletes an item themselves. It is
capped at MAX_MEMORY_ITEMS combined (reference material + generated lessons together): when full,
the agent asks which one to remove before adding another — see lens/telegram/memory.py.
"""
from django.db import models

MAX_MEMORY_ITEMS = 5

class TeacherMemory(models.Model):
    KIND_CHOICES = [("reference", "reference"), ("lesson", "lesson")]
    SOURCE_CHOICES = [("telegram", "telegram"), ("drive", "drive")]
    # Same HMAC(chat) key used to isolate Telegram conversation state (see Agent.key); never the raw chat id.
    teacher_key = models.CharField(max_length=64, db_index=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()  # extracted text (reference) or a JSON dump (lesson)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

class TeacherDriveConnection(models.Model):
    """One Google Drive folder per teacher. refresh_token is sensitive: never logged, never sent
    to OpenAI or included in any Telegram message."""
    teacher_key = models.CharField(max_length=64, unique=True)
    refresh_token = models.TextField()
    folder_id = models.CharField(max_length=200, blank=True, default="")
    connected_at = models.DateTimeField(auto_now_add=True)

class DriveConnectState(models.Model):
    """Bridges the OAuth redirect (handled by the web server process) back to the teacher who
    asked for it (in the Telegram bot process) — they don't share Django's in-memory cache, but
    both point at the same SQLite file, so a plain row works. Rows older than ~10 minutes are
    treated as expired by lens.telegram.drive and may be pruned by manage.py clearsessions-style
    maintenance; there's no harm in a few stale rows accumulating for a hackathon-scale demo."""
    state = models.CharField(max_length=64, unique=True)
    teacher_key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
