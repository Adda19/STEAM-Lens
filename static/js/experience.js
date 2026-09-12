"use strict";
(() => {
  const $ = id => document.getElementById(id);
  let context;
  try { context = JSON.parse(sessionStorage.getItem("steam-context")); } catch (_) {}
  if (!context || context.version !== 3 || !Array.isArray(context.materials)) { location.replace("/"); return; }
  $("context-line").textContent = `${context.age} años · ${context.areaLabel} · Sesión de ${context.time} minutos · ${context.materials.join(" + ")}`;
  let stream = null, blob = null, photoURL = null, analysis = null, busy = false, generation = 0;
  const csrf = () => decodeURIComponent(document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1] || "");
  function showError(message, id = "global-error") { $(id).textContent = message || ""; $(id).hidden = !message; }
  function setBusy(value) {
    busy = value;
    for (const id of ["start-camera", "capture", "retry", "retake", "upload", "send-answer", "hint", "reset"]) $(id).disabled = value;
    $("send-answer").textContent = value ? "Pensando…" : "Enviar ↗";
  }
  async function post(url, body) {
    const headers = {"X-CSRFToken": csrf()};
    if (!(body instanceof FormData)) headers["Content-Type"] = "application/json";
    let response;
    try { response = await fetch(url, {method: "POST", headers, body: body instanceof FormData ? body : JSON.stringify(body), credentials: "same-origin", signal: AbortSignal.timeout(60000)}); }
    catch (_) { throw new Error("No se pudo conectar. Revisa tu conexión y vuelve a intentarlo."); }
    let data;
    try { data = await response.json(); } catch (_) { throw new Error("No pude procesarlo. Recarga la página y probemos de nuevo."); }
    if (!response.ok) throw new Error(data.error || "No pude procesarlo. Probemos de nuevo.");
    return data;
  }
  function stopCamera() { if (stream) stream.getTracks().forEach(track => track.stop()); stream = null; $("camera").srcObject = null; }
  function clearPhoto() {
    if (photoURL) URL.revokeObjectURL(photoURL);
    photoURL = null; blob = null;
    for (const id of ["photo", "discovery-photo"]) $(id).removeAttribute("src");
    $("photo").hidden = true;
  }
  function screen(name) {
    for (const value of ["capture", "discovery", "mission"]) $(`${value}-screen`).hidden = value !== name;
    ["step-explore", "step-discover", "step-mission"].forEach((id, i) => $(id).classList.toggle("active", i === ["capture", "discovery", "mission"].indexOf(name)));
    window.scrollTo({top: 0, behavior: "smooth"});
  }
  async function startCamera() {
    if (busy) return;
    showError(""); stopCamera(); clearPhoto();
    $("retry").hidden = true; $("retake").hidden = true;
    $("camera-placeholder").hidden = false; $("capture").hidden = true;
    if (!navigator.mediaDevices?.getUserMedia) { $("camera-help").textContent = "La cámara necesita HTTPS o localhost. Puedes elegir una fotografía."; return; }
    $("start-camera").disabled = true;
    const token = ++generation;
    try {
      const nextStream = await navigator.mediaDevices.getUserMedia({video: {facingMode: {ideal: "environment"}, width: {ideal: 1280}}, audio: false});
      if (token !== generation) { nextStream.getTracks().forEach(track => track.stop()); return; }
      stream = nextStream; $("camera").srcObject = stream;
      await $("camera").play();
      $("camera-placeholder").hidden = true; $("start-camera").hidden = true; $("capture").hidden = false;
      $("camera-help").textContent = "Encuadra un objeto y pulsa Descubrir.";
    } catch (_) {
      stopCamera(); $("start-camera").hidden = false;
      $("camera-help").textContent = "Necesitamos acceso a la cámara para descubrir el mundo contigo. Puedes habilitarla desde los permisos del navegador o elegir una fotografía.";
    } finally { $("start-camera").disabled = false; }
  }
  async function canvasBlob(source, width, height) {
    const scale = Math.min(1, 1280 / Math.max(width, height));
    const canvas = document.createElement("canvas"); canvas.width = Math.round(width * scale); canvas.height = Math.round(height * scale);
    const ctx = canvas.getContext("2d"); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.drawImage(source, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve, reject) => canvas.toBlob(value => value ? resolve(value) : reject(new Error("No se pudo preparar la fotografía.")), "image/jpeg", 0.8));
  }
  async function usePhoto(value) {
    generation++; stopCamera(); clearPhoto(); blob = value; photoURL = URL.createObjectURL(blob);
    $("photo").src = photoURL; $("photo").hidden = false; $("camera-placeholder").hidden = true;
    $("capture").hidden = true; $("start-camera").hidden = true; $("retake").hidden = false;
    await analyzePhoto();
  }
  async function analyzePhoto() {
    if (busy || !blob) return;
    setBusy(true); showError(""); $("retry").hidden = true; $("loading").hidden = false;
    const token = generation;
    const messages = ["Observando tu descubrimiento…", "Buscando ciencia a tu alrededor…", "Conectando ideas STEAM…", "Preparando tu misión…"];
    let n = 0; $("loading-message").textContent = messages[0];
    const timer = setInterval(() => { $("loading-message").textContent = messages[++n % messages.length]; }, 2600);
    try {
      const data = new FormData(); data.append("image", blob, "capture.jpg"); data.append("age", context.age); data.append("area", context.area); data.append("time", context.time);
      context.materials.forEach(material => data.append("materials", material));
      const result = await post("/api/analyze/", data);
      if (token !== generation) return;
      if (!result.valid_capture) { showError(result.retry_message); return; }
      analysis = result; renderDiscovery(); screen("discovery"); $("object-title").focus();
    } catch (error) { showError(error.message); $("retry").hidden = false; }
    finally { clearInterval(timer); $("loading").hidden = true; setBusy(false); }
  }
  function textElement(tag, text, className = "") { const node = document.createElement(tag); node.textContent = text; node.className = className; return node; }
  function renderDiscovery() {
    $("object-title").textContent = `¡Encontré ${analysis.detected_object.name}!`;
    $("object-description").textContent = analysis.detected_object.description;
    $("discovery-photo").src = photoURL; $("connections").replaceChildren();
    const areas = {science: ["Ciencia", "S"], technology: ["Tecnología", "T"], engineering: ["Ingeniería", "E"], arts: ["Arte", "A"], mathematics: ["Matemáticas", "M"]};
    analysis.steam_connections.forEach(connection => {
      const card = textElement("article", "", `connection ${connection.area}`);
      card.append(textElement("span", areas[connection.area][1], "area-icon"));
      const content = document.createElement("div"); content.append(textElement("span", areas[connection.area][0], "area-name"), textElement("h3", connection.title), textElement("p", connection.explanation));
      card.append(content); $("connections").append(card);
    });
  }
  function bubble(text, type = "coach-bubble") { const node = textElement("div", text, `bubble ${type}`); $("conversation").append(node); $("conversation").scrollTop = $("conversation").scrollHeight; return node; }
  $("reveal-mission").addEventListener("click", () => {
    const mission = analysis.mission;
    $("mission-title").textContent = mission.title; $("mission-challenge").textContent = mission.challenge;
    $("learning-goal").textContent = mission.learning_goal;
    $("mission-materials").textContent = mission.materials_required.join(" + ") || "Tu observación y tus ideas.";
    $("mission-meta").replaceChildren(textElement("span", `${mission.estimated_minutes} minutos`), textElement("span", `Dificultad ${"●".repeat(mission.difficulty)}${"○".repeat(3 - mission.difficulty)}`));
    $("conversation").replaceChildren(); bubble("Antes de construir, pensemos.", "coach-intro"); bubble(mission.first_question);
    $("coach-form").hidden = false; $("coach-finished").hidden = true; $("answer").value = ""; showError("", "coach-error");
    screen("mission"); $("mission-title").focus();
  });
  async function sendAnswer(answer) {
    if (busy || !answer.trim()) return;
    setBusy(true); showError("", "coach-error");
    try {
      const result = await post("/api/coach/", {answer});
      bubble(answer, "student-bubble"); bubble(result.feedback);
      if (result.hint) bubble(result.hint, "hint-bubble");
      if (result.next_question) bubble(result.next_question);
      if (result.celebration) bubble(result.celebration, "celebration-bubble");
      $("answer").value = "";
      if (["completed", "blocked"].includes(result.status)) {
        $("coach-form").hidden = true; $("coach-finished").hidden = false;
        $("coach-finished").textContent = result.status === "completed" ? "¡Una idea más para mirar el mundo! Puedes explorar otro objeto." : "Podemos seguir descubriendo con otro objeto.";
      } else $("answer").focus();
    } catch (error) { showError(error.message, "coach-error"); }
    finally { setBusy(false); }
  }
  $("coach-form").addEventListener("submit", event => { event.preventDefault(); sendAnswer($("answer").value); });
  $("hint").addEventListener("click", () => { $("answer").value = "Aún no lo sé. ¿Me das una pista?"; sendAnswer($("answer").value); });
  $("start-camera").addEventListener("click", startCamera); $("retake").addEventListener("click", startCamera); $("retry").addEventListener("click", analyzePhoto);
  $("capture").addEventListener("click", async () => {
    if (busy) return;
    const video = $("camera"); if (!video.videoWidth) { showError("Espera un momento a que la cámara esté lista."); return; }
    try { await usePhoto(await canvasBlob(video, video.videoWidth, video.videoHeight)); } catch (error) { showError(error.message); }
  });
  $("upload").addEventListener("change", async event => {
    const file = event.target.files[0]; event.target.value = ""; if (!file || busy) return;
    if (file.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) { showError("Elige una foto JPEG, PNG o WebP de hasta 5 MB."); return; }
    const url = URL.createObjectURL(file);
    try { const img = new Image(); img.src = url; await img.decode(); await usePhoto(await canvasBlob(img, img.naturalWidth, img.naturalHeight)); }
    catch (_) { showError("No pude leer esta fotografía. Elige otra imagen."); }
    finally { URL.revokeObjectURL(url); }
  });
  $("reset").addEventListener("click", async () => {
    if (busy) return; setBusy(true);
    try {
      await post("/api/reset/", {}); generation++; stopCamera(); clearPhoto(); analysis = null;
      showError(""); $("start-camera").hidden = false; $("capture").hidden = true; $("retry").hidden = true; $("retake").hidden = true;
      $("camera-placeholder").hidden = false; $("camera-help").textContent = ""; $("conversation").replaceChildren(); screen("capture");
    } catch (error) { showError(error.message); } finally { setBusy(false); }
  });
  window.addEventListener("pagehide", () => { generation++; stopCamera(); clearPhoto(); });
})();
