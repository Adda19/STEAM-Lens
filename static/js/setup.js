"use strict";
const form = document.getElementById("setup-form");
const choices = [...form.querySelectorAll('[name="materials"]')];
try {
  const saved = JSON.parse(sessionStorage.getItem("steam-context"));
  if (saved && saved.version === 3) {
    form.elements.age.value = saved.age;
    form.elements.area.value = saved.area;
    form.elements.time.value = saved.time;
    choices.forEach(input => { input.checked = saved.materials.includes(input.value); });
  }
} catch (_) { /* Defaults remain usable when storage is unavailable. */ }
choices.forEach(input => input.addEventListener("change", () => {
  if (input.checked && input.value === "Sin materiales") choices.forEach(other => { if (other !== input) other.checked = false; });
  else if (input.checked) choices[0].checked = false;
  if (!choices.some(item => item.checked)) choices[0].checked = true;
}));
form.addEventListener("submit", event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const context = {version: 3, age: Number(form.elements.age.value), area: form.elements.area.value, areaLabel: form.elements.area.selectedOptions[0].textContent, time: Number(form.elements.time.value), materials: choices.filter(item => item.checked).map(item => item.value)};
  try {
    sessionStorage.setItem("steam-context", JSON.stringify(context));
    location.href = "/explore/";
  } catch (_) {
    const error = document.getElementById("setup-error");
    error.textContent = "Permite el almacenamiento de esta pestaña en tu navegador para continuar.";
    error.hidden = false;
  }
});
