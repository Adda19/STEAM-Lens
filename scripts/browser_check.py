"""UI checks use explicit network fixtures, never presented as a live AI demo."""
import io
import json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)
analysis = {"valid_capture": True, "retry_message": None,
    "detected_object": {"name": "una planta", "description": "Una planta en maceta.", "confidence": "high"},
    "steam_connections": [{"area": "science", "title": "Agua y vida", "explanation": "Observa qué necesita una planta."},
                          {"area": "mathematics", "title": "Compara sus hojas", "explanation": "Encuentra diferencias de tamaño."}],
    "mission": {"title": "Detectives de las hojas", "challenge": "Encuentra dos diferencias entre las hojas de tu planta.",
                "learning_goal": "Observar y comparar características.", "difficulty": 1, "estimated_minutes": 10,
                "materials_required": [], "first_question": "¿En qué se parecen las hojas?"}}
reply = {"feedback": "El color es una buena observación.", "status": "hint", "hint_level": 1,
         "hint": "Mira también sus tamaños.", "next_question": "¿Son todas igual de grandes?", "celebration": None}
image = io.BytesIO()
Image.new("RGB", (400, 400), "#87a86a").save(image, "JPEG")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    desktop = browser.new_page(viewport={"width": 1440, "height": 1050})
    desktop.goto("http://127.0.0.1:8001/")
    desktop.screenshot(path=str(OUT / "home-desktop.png"), full_page=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("http://127.0.0.1:8001/")
    page.screenshot(path=str(OUT / "home-mobile.png"), full_page=True)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.get_by_text("Arduino", exact=True).click()
    assert not page.locator('input[value="Sin materiales"]').is_checked()
    page.get_by_role("button", name="Comenzar a explorar").click()
    page.wait_for_url("**/explore/")
    page.get_by_role("button", name="Activar cámara").click()
    page.wait_for_function("document.getElementById('camera-help').textContent.length > 0")
    page.screenshot(path=str(OUT / "explore-mobile.png"), full_page=True)
    calls = []
    def analyze_route(route):
        calls.append("analyze")
        route.fulfill(json=analysis)
    page.route("**/api/analyze/", analyze_route)
    page.route("**/api/coach/", lambda route: route.fulfill(json=reply))
    page.locator("#upload").set_input_files({"name": "test.jpg", "mimeType": "image/jpeg", "buffer": image.getvalue()})
    page.locator("#discovery-screen").wait_for(state="visible")
    page.screenshot(path=str(OUT / "discovery-mobile.png"), full_page=True)
    page.get_by_role("button", name="Crear una misión").click()
    page.locator("#mission-screen").wait_for(state="visible")
    assert calls == ["analyze"], "Revealing mission must not repeat analysis"
    page.locator("#answer").fill("El color")
    page.get_by_role("button", name="Enviar").click()
    page.get_by_text("¿Son todas igual de grandes?", exact=True).wait_for()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(OUT / "mission-mobile-fixture.png"), full_page=True)
    page.get_by_role("button", name="Explorar otro objeto").click()
    page.locator("#capture-screen").wait_for(state="visible")
    assert page.locator("#conversation").inner_text() == ""
    assert not errors, errors
    browser.close()
print("Browser checks passed: mobile layout, preferences, camera fallback, upload, discovery, one-call mission, coach and reset. AI responses were fixtures.")
