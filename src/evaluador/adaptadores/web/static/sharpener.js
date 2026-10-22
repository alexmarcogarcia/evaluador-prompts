// Sharpener · mejora progresiva de la interfaz (ADR-0004, spec 002).
// Sin este archivo la app funciona igual; con él, añade:
//   - progreso inmediato con el texto del paso (RF-017, RNF-013),
//   - bloqueo del doble envío (RF-019),
//   - envío sin recargar y desplazamiento al contenido nuevo (RF-023).
// Regla: nunca construye HTML con datos del usuario. Solo coloca nodos de la página que devuelve el
// servidor, ya escapada por Jinja2 (RNF-010).
(function () {
  "use strict";

  var progreso = document.getElementById("progreso");

  function mostrarProgreso(texto) {
    if (!progreso) return;
    progreso.querySelector(".progreso-texto").textContent = texto;
    progreso.hidden = false;
  }

  function ocultarProgreso() {
    if (progreso) progreso.hidden = true;
  }

  function bloquear(formulario, bloqueado) {
    formulario.dataset.enviando = bloqueado ? "si" : "";
    formulario.querySelectorAll("button").forEach(function (boton) {
      boton.disabled = bloqueado;
    });
  }

  function colocar(html) {
    var nueva = new DOMParser().parseFromString(html, "text/html");
    var lienzoNuevo = nueva.querySelector("main.lienzo");
    var lienzo = document.querySelector("main.lienzo");
    if (!lienzoNuevo || !lienzo) return false;
    lienzo.replaceChildren.apply(lienzo, Array.prototype.slice.call(lienzoNuevo.childNodes));
    document.title = nueva.title;
    // Lleva la vista y el foco al título de la última sección: lo nuevo (RF-023).
    var titulos = lienzo.querySelectorAll("h2[tabindex='-1']");
    var destino = titulos[titulos.length - 1] || lienzo.querySelector("[role='alert']");
    if (destino) {
      var suave = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      destino.scrollIntoView({ behavior: suave ? "smooth" : "auto", block: "start" });
      destino.focus({ preventScroll: true });
    }
    return true;
  }

  document.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!(formulario instanceof HTMLFormElement) || !formulario.dataset.progreso) return;
    evento.preventDefault();
    if (formulario.dataset.enviando === "si") return; // RF-019: una sola petición a la vez.

    bloquear(formulario, true);
    mostrarProgreso(formulario.dataset.progreso); // RF-017: antes de cualquier espera.

    fetch(formulario.action, { method: "POST", body: new FormData(formulario) })
      .then(function (respuesta) { return respuesta.text(); })
      .then(function (html) {
        ocultarProgreso();
        if (!colocar(html)) throw new Error("respuesta inesperada");
      })
      .catch(function () {
        // Si algo falla en el navegador, se envía de la forma de siempre: la app sigue funcionando.
        ocultarProgreso();
        bloquear(formulario, false);
        formulario.dataset.progreso = "";
        formulario.submit();
      });
  });
})();
