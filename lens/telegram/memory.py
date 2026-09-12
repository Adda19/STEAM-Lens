"""Teacher memory: a small, bounded, persistent store per teacher (see lens.models.TeacherMemory),
independent of the 1-hour conversation state. Items come from a Telegram upload, a connected
Google Drive folder, or a lesson the teacher chose to keep. lesson.generate() reads a compact
summary of it as extra grounding, distinct from Doc_Oficial (team-validated) and from
previous_sessions (a one-off recap for a single generation).
"""
from lens.models import TeacherMemory, MAX_MEMORY_ITEMS

def list_items(teacher_key):
    return list(TeacherMemory.objects.filter(teacher_key=teacher_key).order_by("created_at"))

def has_room(teacher_key):
    return TeacherMemory.objects.filter(teacher_key=teacher_key).count() < MAX_MEMORY_ITEMS

def add(teacher_key, kind, source, title, content):
    if not has_room(teacher_key):
        raise ValueError("Teacher memory is full")
    return TeacherMemory.objects.create(teacher_key=teacher_key, kind=kind, source=source,
                                        title=(title or "").strip()[:200] or "(sin título)", content=content[:20000])

def delete(teacher_key, position):
    """`position` is the 1-based index the teacher was shown (see format_list), oldest first."""
    items = list_items(teacher_key)
    if not isinstance(position, int) or isinstance(position, bool) or not 1 <= position <= len(items):
        raise ValueError("Invalid position")
    items[position - 1].delete()

def format_list(teacher_key, language="es"):
    """Numbered, human-readable listing for a Telegram message. Empty list -> empty string."""
    from . import i18n
    kind_label = {"reference": i18n.tr(language, "memory_kind_reference"), "lesson": i18n.tr(language, "memory_kind_lesson")}
    source_label = {"telegram": "Telegram", "drive": "Drive"}
    lines = []
    for position, item in enumerate(list_items(teacher_key), start=1):
        lines.append(f"{position}. {item.title} — {kind_label[item.kind]} ({source_label[item.source]}, {item.created_at.strftime('%Y-%m-%d')})")
    return "\n".join(lines)

def summary_for_prompt(teacher_key):
    """Compact view for lesson.generate(): never the raw model instances, and never the sensitive
    Drive refresh token (that lives in TeacherDriveConnection, a separate model entirely)."""
    return [{"title": item.title, "kind": item.kind, "excerpt": item.content[:1500]} for item in list_items(teacher_key)]
