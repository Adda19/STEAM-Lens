"""Exercise getUserMedia and single-frame capture with Chromium's fake camera."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True, args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"])
    context = browser.new_context(permissions=["camera"], viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.goto("http://127.0.0.1:8001/")
    page.get_by_role("button", name="Comenzar a explorar").click()
    page.wait_for_url("**/explore/")
    page.get_by_role("button", name="Activar cámara").click()
    page.wait_for_function("document.getElementById('camera').videoWidth > 0")
    count = []
    def analyze(route):
        count.append(1)
        assert "image/jpeg" in route.request.post_data_buffer.decode("latin1")
        route.fulfill(json={"valid_capture": False, "retry_message": "Prueba otro objeto."})
    page.route("**/api/analyze/", analyze)
    page.get_by_role("button", name="Descubrir", exact=True).click()
    page.get_by_text("Prueba otro objeto.", exact=True).wait_for()
    assert page.evaluate("document.getElementById('camera').srcObject === null")
    assert count == [1]
    assert page.locator("#photo").is_visible()
    assert page.get_by_role("button", name="Tomar otra fotografía").is_enabled()
    browser.close()
print("Camera check passed: getUserMedia, live preview, JPEG single frame, stopped tracks and retry. Simulated camera, not a physical phone.")
