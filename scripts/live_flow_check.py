"""Two real AI calls using our CSS plant illustration, never a user's photograph."""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
out = root / "artifacts"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto("http://127.0.0.1:8001/")
    picture = page.locator(".object-art").screenshot(type="jpeg")
    token = next(c["value"] for c in page.context.cookies() if c["name"] == "csrftoken")
    headers = {"X-CSRFToken": token}
    started = time.monotonic()
    response = page.request.post("http://127.0.0.1:8001/api/analyze/", headers=headers, multipart={
        "age": "10", "area": "naturales", "time": "45", "materials": "Sin materiales",
        "image": {"name": "css-plant-illustration.jpg", "mimeType": "image/jpeg", "buffer": picture}}, timeout=60000)
    analysis_seconds = round(time.monotonic() - started, 2)
    data = response.json()
    if response.status != 200 or not data.get("valid_capture"):
        raise RuntimeError(f"Analysis failed: HTTP {response.status}; {data}")
    assert "success_criteria" not in data["mission"]
    started = time.monotonic()
    response = page.request.post("http://127.0.0.1:8001/api/coach/", headers=headers,
                                 data={"answer": "No estoy seguro. Veo hojas de diferentes tamaños."}, timeout=60000)
    coach_seconds = round(time.monotonic() - started, 2)
    coach = response.json()
    if response.status != 200:
        raise RuntimeError(f"Coach failed: HTTP {response.status}; {coach}")
    assert coach["status"] in {"continue", "hint", "completed", "blocked"}
    reset = page.request.post("http://127.0.0.1:8001/api/reset/", headers=headers, data={})
    assert reset.status == 200
    result = {"input": "CSS plant illustration created in this project; not a real camera photograph",
              "analysis_seconds": analysis_seconds, "coach_seconds": coach_seconds, "analysis": data, "coach": coach}
    (out / "live-flow-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"live_flow": "passed", "object": data["detected_object"]["name"], "analysis_seconds": analysis_seconds,
                      "coach_seconds": coach_seconds, "coach_status": coach["status"]}, ensure_ascii=True))
    browser.close()
