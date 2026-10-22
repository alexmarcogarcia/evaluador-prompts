# Tareas: Interfaz atractiva e intuitiva

**Spec:** 002 v1.0 · **Plan:** aprobado 2026-10-22 · **Estado:** aprobado 2026-10-22 por Àlex Marco · **Responsable:** Àlex Marco

`[P]` = paralelizable. La prueba de cada tarea de servidor se escribe primero y debe fallar antes de implementar. El JavaScript se verifica con la lista de comprobación manual del final (ADR-0004).

## Base

- [x] **T100** [P] Archivos estáticos en `adaptadores/web/static/`: tipografías Bricolage Grotesque y Figtree en woff2 con `OFL.txt`, y logotipo SVG. Prueba de que ninguna página carga nada de Google (RF-024, ADR-0004).
- [x] **T101** `static/sharpener.css` con los tokens de la guía visual en claro y oscuro, y plantilla dividida en partes. Prueba que lee los tokens y comprueba el contraste AA de cada par de la guía (RF-024, RF-025, RNF-014).

## Historia P1 · Saber en todo momento qué está pasando

- [x] **T110** Pruebas de aceptación del reintento: un modelo falso que devuelve una respuesta inválida una vez y luego una válida (el usuario ve el resultado); dos veces (ve el error y conserva su texto); un error de otro tipo no se reintenta (RF-018).
- [x] **T111** Reintento en `Diagnosticar` y `Mejorar`, solo ante `RESPUESTA_INVALIDA` (RF-018). Depende de T110.
- [x] **T112** `static/sharpener.js`: al enviar, progreso inmediato con el texto del paso en una región `aria-live`, botón desactivado mientras tanto, envío con `fetch`, sustitución del contenido y desplazamiento a lo nuevo (RF-017, RF-019, RF-023, RNF-013). Prueba de aceptación de que el marcado necesario está presente.
- [x] **T113** [P] Textos del progreso en los 4 idiomas: «Afilando tu prompt…» y «Puliendo la versión mejorada…» (RF-017).

**Punto de control P1:** quickstart, paso 3, con y sin scripts.

## Historia P1 · Usar el resultado sin esfuerzo

- [ ] **T120** Prueba de aceptación: el botón «Copiar» lleva el texto exacto de la mejora; el aviso de `[COMPLETAR]` aparece solo si los hay; sin scripts, el texto se puede seleccionar (RF-020).
- [ ] **T121** Copia en `sharpener.js`, con la alternativa de seleccionar el texto si el navegador no deja copiar (RF-020). Depende de T120.

**Punto de control:** quickstart, paso 4.

## Historia P2 · Una interfaz atractiva y coherente

- [ ] **T130** Aplicar la guía visual a todas las pantallas: barra con logotipo, fosforito, bloques de problemas, botones, foco y comparación (RF-024).
- [ ] **T131** Modo oscuro automático e interruptor que guarda la preferencia en el navegador; sin scripts, solo el automático (RF-025).

## Historia P2 · Un recorrido fluido y guiado

- [ ] **T140** Pasos «1 Escribir · 2 Revisar · 3 Mejorar», con el actual marcado en cada pantalla. Prueba de aceptación por pantalla (RF-022).
- [ ] **T141** Cambio de idioma por POST, que vuelve al inicio conservando el texto escrito y sin datos en la URL. Prueba de aceptación (RF-022, RNF-006).

## Historia P2 · Empezar sin saber qué escribir (depende de la decisión sobre RF-002)

- [ ] **T150** Cuatro ejemplos por idioma en `adaptadores/web/ejemplos.py`, sintéticos, que rellenan el prompt (y el resultado esperado, si sigue existiendo). Prueba de aceptación (RF-021).
- [ ] **T151** Pantalla de inicio según la decisión sobre RF-002: campo de resultado esperado obligatorio u opcional (RF-021).

## Cierre

- [ ] **T160** Revisión de accesibilidad: recorrido completo solo con teclado, lector de pantalla en los controles y comprobación a 360 px (RNF-014, RNF-015).
- [ ] **T161** Lista de comprobación manual del JavaScript en Chrome y Firefox, con el resultado registrado en `research.md` de la spec 002 (RF-017, RF-019, RF-020, RF-023, RF-025, RNF-013).

**Fin del incremento 002:** quickstart completo, con y sin scripts. Después, la T060 (spec 001) mide RNF-012 y RNF-016.

## Estimación

| Bloque | Sesiones |
|---|---|
| Base | 1–2 |
| P1 · Progreso y reintento | 2–3 |
| P1 · Copiar | 1 |
| P2 · Guía visual y modo oscuro | 2–3 |
| P2 · Recorrido | 1–2 |
| P2 · Ejemplos | 1 |
| Cierre | 1 |

**Total:** 9–13 sesiones.
