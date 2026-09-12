"""Starter catalog of PhET HTML5 simulations for the "external resources" section of a lesson.

IMPORTANT: unlike Doc_Oficial/, this list was NOT verified against the live site — browser access
wasn't available when it was built, so these slugs come from training knowledge of PhET's most
long-standing, stable simulations, not a live check. Spot-check each URL before trusting it; once
verified, feel free to fold a corrected version into Doc_Oficial/ so it becomes team-validated.

Keys are the exact PhET slug used in the URL. `area` maps loosely to lens.context.AREAS codes so the
agent only offers a simulation when it plausibly fits; `tags` are Spanish search terms describing the
topic, used to help the model match a resource to what the lesson is actually about.
"""
PHET_SIMULATIONS = {
    "build-an-atom": {"area": ["quimica", "fisica"], "tags": ["átomos", "protones", "electrones", "estructura atómica"]},
    "ph-scale": {"area": ["quimica"], "tags": ["ácidos", "bases", "pH"]},
    "states-of-matter": {"area": ["quimica", "fisica", "naturales"], "tags": ["estados de la materia", "sólido", "líquido", "gas"]},
    "molecule-shapes": {"area": ["quimica"], "tags": ["moléculas", "enlaces", "geometría molecular"]},
    "circuit-construction-kit-dc": {"area": ["fisica", "tecnologia", "ingenieria", "robotica"], "tags": ["circuitos", "electricidad", "corriente", "voltaje"]},
    "wave-on-a-string": {"area": ["fisica"], "tags": ["ondas", "frecuencia", "amplitud"]},
    "forces-and-motion-basics": {"area": ["fisica"], "tags": ["fuerzas", "movimiento", "fricción"]},
    "gravity-and-orbits": {"area": ["fisica"], "tags": ["gravedad", "órbitas", "sistema solar"]},
    "energy-skate-park-basics": {"area": ["fisica"], "tags": ["energía", "energía cinética", "energía potencial"]},
    "balancing-act": {"area": ["fisica", "matematicas"], "tags": ["equilibrio", "torque", "palancas"]},
    "graphing-lines": {"area": ["matematicas"], "tags": ["gráficas", "pendiente", "ecuación de la recta"]},
    "fraction-matcher": {"area": ["matematicas"], "tags": ["fracciones"]},
    "area-model-multiplication": {"area": ["matematicas"], "tags": ["multiplicación", "área", "modelo de área"]},
    "natural-selection": {"area": ["biologia", "naturales"], "tags": ["selección natural", "evolución", "genética"]},
    "gene-expression-essentials": {"area": ["biologia"], "tags": ["adn", "genes", "expresión génica"]},
}
PHET_LOCALES = {"es": "es", "en": "en", "fr": "fr"}

def simulation_url(slug, language):
    return f"https://phet.colorado.edu/{PHET_LOCALES.get(language, 'en')}/simulations/{slug}"
