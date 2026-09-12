"""Shared educational context, independent of web or messaging transport."""
AGE_MIN, AGE_MAX = 3, 99
AREAS = [
    ("integrado", "STEAM integrado"),
    ("matematicas", "Matemáticas"), ("fisica", "Física"),
    ("quimica", "Química"), ("naturales", "Ciencias naturales"),
    ("biologia", "Biología"), ("informatica", "Informática y programación"),
    ("tecnologia", "Tecnología"), ("ingenieria", "Ingeniería"),
    ("artes", "Artes y diseño"), ("robotica", "Robótica"),
]
MATERIALS = ["Sin materiales", "Arduino", "micro:bit", "LEDs", "Sensores", "Servomotor", "Motor DC", "Cartón / MDF", "Material reciclado"]
CONTEXT_KEYS = ("learner_age", "focus_area", "available_materials", "available_time")

def build_context(age, area, minutes, materials):
    if area not in dict(AREAS):
        raise ValueError("Invalid area")
    if isinstance(age, bool) or not str(age).isdigit() or not AGE_MIN <= int(age) <= AGE_MAX:
        raise ValueError("Age must be a whole number of years between 3 and 99")
    if isinstance(minutes, bool) or not str(minutes).isdigit() or not 10 <= int(minutes) <= 180:
        raise ValueError("Session must be 10–180 whole minutes")
    if not isinstance(materials, list) or not materials or any(not isinstance(m, str) or m not in MATERIALS for m in materials):
        raise ValueError("Invalid materials")
    if len(materials) != len(set(materials)) or ("Sin materiales" in materials and len(materials) != 1):
        raise ValueError("Conflicting materials")
    return {"learner_age": int(age), "focus_area": dict(AREAS)[area],
            "available_materials": materials, "available_time": int(minutes)}
