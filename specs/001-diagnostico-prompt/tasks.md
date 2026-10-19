# Tareas: Diagnóstico y mejora de un prompt

**Spec:** 001 v1.2 · **Plan:** aprobado 2026-10-19 · **Estado:** aprobado 2026-10-19 por Àlex Marco · **Responsable:** Àlex Marco

`[P]` = paralelizable (toca ficheros distintos y no depende de otra tarea pendiente). Cada tarea de código empieza por su prueba, que debe fallar antes de implementar (principio 9). Una tarea cabe en una sesión y se verifica con un comando.

## Base: harness (Fase 7, bloquea todo lo demás)

- [x] **T001** Configurar el proyecto en `pyproject.toml`: dependencias con versión fijada, ruff, mypy y pytest. Añadir `.python-version` (3.13) y `.gitattributes` (finales de línea LF). · Verifica: `ruff check`, `mypy` y `pytest` se ejecutan.
- [x] **T002** Crear el entorno con un solo comando, en `scripts/` y documentado en `README.md`. · Verifica: un clon limpio queda listo siguiendo solo el README.
- [x] **T003** [P] Script de comprobación de coherencia en `scripts/coherencia.py`. Falla si hay un RF sin prueba que lo referencie, una tarea sin RF o un identificador que no existe en la spec. · Verifica: falla con la spec actual (no hay pruebas) y pasa al final.
- [x] **T004** CI en `.github/workflows/ci.yml`: instalar, ruff, mypy, pytest, coherencia y búsqueda de secretos. · Verifica: CI en verde con el repositorio casi vacío.
- [x] **T005** [P] Actualizar `AGENTS.md` con los comandos reales.

## Base: contratos y dominio

- [x] **T010** [P] `contracts/diagnostico.schema.json` y `contracts/mejora.schema.json` (RF-003, RF-007, RF-009, RF-015).
- [x] **T011** [P] Entidades en `src/evaluador/dominio/modelos.py`: Prompt inmutable, Problema, Categoria (catálogo de 9), TipoProblema, Gravedad, Diagnostico, Pregunta, VersionMejorada y Cambio. Pruebas en `tests/unit/test_modelos.py` (RF-003, RF-004, RF-012).
- [x] **T012** Reglas en `src/evaluador/dominio/reglas.py`, con pruebas en `tests/unit/test_reglas.py`: (RF-001, RF-007, RF-009, RNF-004)
  - longitud ≤ 8.000;
  - cita literal;
  - tipo coherente con la cita;
  - ≤ 5 preguntas;
  - cada cambio enlaza problemas que existen;
  - descartar los problemas inválidos.

  Depende de T011.
- [x] **T013** [P] Puerto `src/evaluador/puertos/modelo_ia.py` y un doble de prueba en `tests/dobles/modelo_falso.py` (ADR-0001). Depende de T011.

## Base: modelo y evals

- [x] **T020** Adaptador `src/evaluador/adaptadores/modelo_openai_compatible.py` para Gemini y NVIDIA. Pruebas de contrato en `tests/contract/` y de integración en `tests/integration/`: errores 429/503, tiempos agotados y JSON inválido; logs solo con métricas (RF-014, RNF-006, ADR-0001). Depende de T010 y T013.
- [x] **T021** [P] Prompt de sistema versionado en `src/evaluador/prompts/diagnostico.md`, partiendo del de la ronda 3 del spike (RF-004, RF-013, RF-015, RF-016).
- [x] **T022** Evals en `evals/`: llevar ahí los 14 casos y la puntuación del spike, y **ampliar a ≥ 50 casos** con ≥ 5 dañinos y ≥ 5 sensibles pero legítimos. Mide RNF-001, RNF-003, RNF-004 y RNF-007. **Los casos nuevos los valida Àlex Marco.** Depende de T020 y T021.

## Historia P1 · Diagnosticar un prompt (MVP)

- [ ] **T030** Pruebas de aceptación de P1 en `tests/acceptance/test_p1_diagnostico.py`, con el doble del modelo (criterios de P1 y de RF-001, RF-002, RF-005, RF-006, RF-015).
- [ ] **T031** Caso de uso `src/evaluador/casos_uso/diagnosticar.py` (RF-001, RF-002, RF-005, RF-015, RF-016). Depende de T012 y T013.
- [ ] **T032** Interfaz web de P1 en `src/evaluador/adaptadores/web/` (RF-006, RF-013, RF-014, RNF-010):
  - formulario con prompt y resultado esperado;
  - proveedor, modelo y aviso de datos personales visibles antes de enviar;
  - diagnóstico con los fragmentos marcados;
  - mensajes de error en lenguaje llano;
  - todo texto del usuario o del modelo se muestra escapado, con una prueba con `<script>` (RNF-010).
- [ ] **T033** [P] Textos de la interfaz en `i18n/{es,ca,en,de}.json`, con una prueba que comprueba que los 4 tienen las mismas claves (RF-013).
- [ ] **T034** Composición en `src/evaluador/composicion.py`: el único punto donde se conectan las implementaciones. El servidor escucha solo en 127.0.0.1 y no hay almacenamiento (RNF-008, RNF-009, ADR-0001, ADR-0002).
- [ ] **T035** **Elegir la estrategia de detección (ADR-0003, decisión 3):** comparar con las evals 3a (ejemplos resueltos), 3b (dos pasos) y 3c (las dos), y adoptar la más simple que cumpla RNF-003. Actualizar el ADR-0003. Depende de T022.

**Punto de control P1:** se ejecuta el quickstart (pasos 1–3) y las evals cumplen RNF-001, RNF-003, RNF-004 y RNF-007.

## Historia P2 · Preguntas aclaratorias

- [ ] **T040** Pruebas de aceptación de P2 en `tests/acceptance/test_p2_preguntas.py` (RF-007, RF-008, RF-010).
- [ ] **T041** Interfaz: mostrar las preguntas, responderlas u omitirlas (RF-007, RF-008).

**Punto de control P2:** quickstart, paso 4.

## Historia P3 · Versión mejorada explicada

- [ ] **T050** Pruebas de aceptación de P3 en `tests/acceptance/test_p3_mejora.py` (RF-009 a RF-012).
- [ ] **T051** [P] Prompt de mejora en `src/evaluador/prompts/mejora.md` (RF-009, RF-010, RF-013: mejora en el idioma del prompt).
- [ ] **T052** Caso de uso `src/evaluador/casos_uso/mejorar.py`, con marcadores `[COMPLETAR: …]` para las preguntas omitidas (RF-009, RF-010, RF-012).
- [ ] **T053** Interfaz: el original y el mejorado lado a lado, con las diferencias marcadas mediante difflib, y cada cambio con su problema (RF-011).
- [ ] **T054** Evals de la mejora: cambios ligados a problemas, marcadores presentes e idioma del prompt (RF-009, RF-010, RF-013).

**Punto de control P3:** quickstart completo, pasos 1–5. Spec, plan y código coherentes, y CI en verde. **Fin del primer incremento (Fase 9).**

## Después del incremento

- [ ] **T060** Prueba con 5 personas no expertas (criterio de éxito 2, RNF-005).

## Estimación (rangos)

| Bloque | Sesiones de trabajo |
|---|---|
| Base (harness, contratos, dominio, modelo, evals) | 5–8 |
| P1 | 4–6 |
| P2 | 1–2 |
| P3 | 3–5 |

**Total:** 13–21 sesiones. Se revisa al cerrar cada historia.
