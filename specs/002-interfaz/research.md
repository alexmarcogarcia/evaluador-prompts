# Investigación y comprobaciones: spec 002

## T160 · Revisión de accesibilidad (2026-10-22)

**Automática** (`tests/acceptance/test_p2_accesibilidad.py`, 64 comprobaciones). En las cuatro pantallas (inicio, revisión con preguntas, mejora y error) y en los cuatro idiomas:

- cada campo tiene su etiqueta y cada botón un nombre legible (los de idioma dicen «Català», no «CA»);
- hay un solo `h1` y los títulos no saltan de nivel;
- el enlace «Saltar al contenido» es lo primero; no hay `tabindex` positivos, los identificadores no se repiten y los SVG decorativos están ocultos al lector.

El contraste AA de los diez pares de color lo comprueba `tests/unit/test_contraste.py` (RNF-014).

**A 360 px** (RNF-015). Se hicieron capturas con Chrome sin ventana, con la app dentro de un marco de 360 px de ancho, porque Chrome en Windows no deja la ventana por debajo de unos 500 px. Inicio en español y en alemán (los textos más largos), revisión con 3 problemas y 2 preguntas, y mejora con marcador `[COMPLETAR]`. Nada se desborda ni obliga a desplazarse en horizontal. Se corrigió un detalle: la pastilla de importancia se estiraba a todo el ancho en el móvil.

**Cambio hecho por la revisión:** enlace «Saltar al contenido», visible solo al llegar con el teclado (WCAG 2.4.1).

## T161 · Lista de comprobación manual

**Estado:** pendiente de hacer por Àlex Marco en Chrome y Firefox. Marca cada punto con ✅ o ❌ y una nota si falla.

| # | Comprobación | Requisito | Chrome | Firefox |
|---|---|---|---|---|
| 1 | Al pulsar «Revisar mi prompt», el aviso «Afilando tu prompt…» aparece al momento | RF-017, RNF-013 | | |
| 2 | Pulsar el botón dos veces seguidas no envía dos peticiones | RF-019 | | |
| 3 | Al llegar la revisión, la página baja sola hasta ella sin quedarse en blanco | RF-023 | | |
| 4 | «Copiar» pone en el portapapeles el prompt mejorado exacto y dice «Copiado» | RF-020 | | |
| 5 | Con `[COMPLETAR: …]`, el aviso al copiar recuerda completarlo | RF-020 | | |
| 6 | El interruptor de la luna cambia a modo oscuro y se recuerda al recargar | RF-025 | | |
| 7 | Al elegir un ejemplo, el texto aparece en el campo sin recargar | RF-021 | | |
| 8 | Al cambiar de idioma con texto escrito, el texto sigue ahí, sin traducir | RF-022 | | |
| 9 | Con solo el teclado (Tab, Mayús+Tab, Intro) se completa el recorrido entero y el foco siempre se ve | RNF-014 | | |
| 10 | El primer Tab muestra «Saltar al contenido» | RNF-014 | | |
| 11 | Con el lector de pantalla (Narrador de Windows: Ctrl+Win+Intro) se oyen el aviso de progreso y los nombres de los botones | RNF-014 | | |
| 12 | Con los scripts desactivados, el recorrido sigue funcionando | ADR-0004 | | |
