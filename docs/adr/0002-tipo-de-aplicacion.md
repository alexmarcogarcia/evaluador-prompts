# ADR-0002: Tipo de aplicación e interfaz

**Estado:** aceptada · **Fecha:** 2026-10-19 · **Decide:** Àlex Marco

**Contexto:** el usuario objetivo no es experto (principio 4), así que necesita una interfaz muy sencilla y en 4 idiomas (RF-013). La interfaz tiene que poder:
- mostrar el diagnóstico con fragmentos marcados (RF-003);
- recoger respuestas a preguntas (RF-007, RF-008);
- comparar el prompt original con el mejorado y marcar las diferencias (RF-011).

Al principio la usará solo Àlex Marco, pero se quiere abrir a otras personas (perfil C). La constitución prohíbe integrar claves de API en una versión publicada, así que la clave tiene que quedarse en un servidor. El lenguaje principal es Python.

**Opciones consideradas:**
- **A · Aplicación web con backend Python (FastAPI) y páginas HTML generadas en el servidor (Jinja2), con un poco de JavaScript.**
  - A favor: control total sobre la interfaz, la traducción y el diff; la clave se queda en el servidor; se puede publicar sin rehacer nada; buen valor para el portafolio.
  - En contra: hay que escribir algo de HTML, CSS y JS.
- **B · Streamlit o Gradio (interfaz web generada desde Python).**
  - A favor: es lo más rápido de construir y todo es Python.
  - En contra: poco control del diseño; la traducción a 4 idiomas y el diff marcado son incómodos; mezcla interfaz y lógica, lo que choca con la arquitectura limpia; publicarla para otras personas es menos limpio.
- **C · Aplicación de escritorio (PySide/Tkinter).**
  - En contra: hay que instalarla, lo que no sirve para usuarios no expertos, y es difícil de compartir.
- **D · Página estática en el navegador que llama directamente al proveedor.**
  - A favor: no hace falta servidor.
  - En contra: la clave queda expuesta en el navegador; no se puede publicar sin que cada usuario ponga su clave. Choca con la constitución.

**Decisión:** **A**. Para el primer incremento se ejecuta en local (`localhost`), con el mismo mecanismo que se usará al publicarla.

**Consecuencias:**
- ✅ La interfaz es un adaptador más. El dominio y los casos de uso no dependen de FastAPI.
- ✅ La traducción a los 4 idiomas se gestiona con archivos de textos por idioma.
- ❌ Más trabajo de interfaz que con B.
- ⚠️ Publicarla (perfil C) exigirá autenticación, límites de uso por persona y alojamiento. Queda fuera del primer incremento.
