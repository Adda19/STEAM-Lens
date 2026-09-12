"""Loader for Doc_Oficial: curated, human-validated reference JSON the agent must always
consult before designing a session. Content here is treated as ground truth — the agent
cites it, it does not fact-check it. The folder is meant to grow; any *.json file dropped
in is picked up automatically, keyed by its filename (without extension)."""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
DOC_OFICIAL_DIR = settings.BASE_DIR / "Doc_Oficial"

def load_all():
    """Read every JSON file in Doc_Oficial. A malformed file is skipped, not fatal:
    the rest of the folder must still ground the session."""
    docs = {}
    if not DOC_OFICIAL_DIR.is_dir():
        return docs
    for path in sorted(DOC_OFICIAL_DIR.glob("*.json")):
        try:
            docs[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("Doc_Oficial: no se pudo leer %s", path.name)
    return docs

def band_for_age(age, docs=None):
    """Look up the curriculo_internacional.json age band (banda_edad) covering `age`,
    clamping to the closest edge band outside the documented range."""
    docs = docs if docs is not None else load_all()
    bands = (docs.get("curriculo_internacional") or {}).get("bandas") or []
    if not bands:
        return None
    parsed = []
    for band in bands:
        try:
            low, high = band["banda_edad"].split("-")
            parsed.append((int(low), int(high), band))
        except (KeyError, ValueError):
            continue
    if not parsed:
        return None
    parsed.sort(key=lambda item: item[0])
    for low, high, band in parsed:
        if low <= age <= high:
            return band
    return parsed[0][2] if age < parsed[0][0] else parsed[-1][2]
