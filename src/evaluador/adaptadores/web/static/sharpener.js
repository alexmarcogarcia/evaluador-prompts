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
    // La página nueva trae su propio botón «Copiar», oculto hasta que el script lo activa (RF-020).
    prepararCopia();
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

  // ---------- Copiar el prompt mejorado (RF-020) ----------
  function prepararCopia() {
    document.querySelectorAll("button.copiar").forEach(function (boton) {
      boton.hidden = false; // Sin scripts el botón no aparece: el texto se selecciona a mano.
    });
  }

  function anunciar(boton, mensaje) {
    var estado = boton.closest("section").querySelector(".estado-copia");
    if (estado) estado.textContent = mensaje;
    var etiqueta = boton.querySelector("span");
    var original = etiqueta.textContent;
    etiqueta.textContent = boton.dataset.copiado;
    setTimeout(function () { etiqueta.textContent = original; }, 2000);
  }

  function seleccionarTexto(boton) {
    var texto = document.getElementById("texto-mejorado");
    if (!texto) return;
    var rango = document.createRange();
    rango.selectNodeContents(texto);
    var seleccion = window.getSelection();
    seleccion.removeAllRanges();
    seleccion.addRange(rango);
    var estado = boton.closest("section").querySelector(".estado-copia");
    if (estado) estado.textContent = boton.dataset.manual;
  }

  document.addEventListener("click", function (evento) {
    var boton = evento.target.closest("button.copiar");
    if (!boton) return;
    var mensaje = boton.dataset.avisoCompletar || boton.dataset.copiado;
    if (!navigator.clipboard) { seleccionarTexto(boton); return; }
    navigator.clipboard.writeText(boton.dataset.copiar).then(
      function () { anunciar(boton, mensaje); },
      function () { seleccionarTexto(boton); }
    );
  });

  // ---------- Interruptor de modo oscuro (RF-025) ----------
  function temaActual() {
    var elegido = document.documentElement.dataset.theme;
    if (elegido) return elegido;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function pintarInterruptor(boton) {
    var oscuro = temaActual() === "dark";
    boton.setAttribute("aria-pressed", oscuro ? "true" : "false");
    boton.setAttribute("aria-label", oscuro ? boton.dataset.claro : boton.dataset.oscuro);
  }

  var interruptor = document.getElementById("tema");
  if (interruptor) {
    interruptor.hidden = false;
    pintarInterruptor(interruptor);
    interruptor.addEventListener("click", function () {
      var nuevo = temaActual() === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = nuevo;
      try { localStorage.setItem("sharpener-tema", nuevo); } catch (e) { /* Sin almacenamiento: dura la sesión. */ }
      pintarInterruptor(interruptor);
    });
  }

  prepararCopia();

  // ---------- Ejemplos de la pantalla inicial (RF-021) ----------
  // Con scripts, el ejemplo se coloca al momento en el campo, sin recargar la página.
  document.addEventListener("click", function (evento) {
    var boton = evento.target.closest("button.ejemplo");
    var campo = document.getElementById("prompt");
    if (!boton || !campo) return;
    evento.preventDefault();
    campo.value = boton.dataset.prompt;
    campo.focus();
    campo.setSelectionRange(campo.value.length, campo.value.length);
  });

  document.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!(formulario instanceof HTMLFormElement) || !formulario.dataset.progreso) return;
    // Un botón con su propia acción (el cambio de idioma, T141) se envía de la forma de siempre.
    if (evento.submitter && evento.submitter.hasAttribute("formaction")) return;
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
