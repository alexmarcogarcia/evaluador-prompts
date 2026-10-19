# ADR-0003: Diseño del diagnóstico

**Estado:** aceptada · **Fecha:** 2026-10-19 · **Decide:** Àlex Marco

**Contexto:** en el spike, Gemini Flash-Lite detecta el 66 % de los problemas; RNF-003 pide el 80 % con como máximo un 20 % de falsos positivos. Además:
- los modelos a veces citan mal;
- agrupan carencias de categorías distintas (contra la regla 4);
- confunden categorías vecinas.

RNF-004 exige el 100 % de citas literales, y el invariante de la constitución prohíbe citar algo que no está en el prompt. El margen de tiempo es amplio: 7 s por llamada frente a los 30 s permitidos.

**Decisiones:**

1. **Salida estructurada con contrato propio.** El modelo devuelve JSON con un esquema versionado (`contracts/diagnostico.schema.json`). Si la respuesta no cumple el esquema, se trata como respuesta inválida (RF-014).
2. **Las reglas duras se comprueban en el código, no se confía en el modelo.** El dominio valida y filtra la respuesta:
   - cada fragmento citado existe literalmente (RNF-004);
   - el tipo es coherente con el fragmento (si hay fragmento, es «en el texto»; si no, «por ausencia»);
   - la categoría pertenece al catálogo;
   - hay como máximo 5 preguntas (RF-007).

   Un problema que no supera la validación no se muestra como válido (casos límite de la spec).
3. **La estrategia para subir la detección se elige con evals, no a priori.** Se comparan tres opciones:
   - **3a · Una llamada con ejemplos resueltos** (uno o dos por categoría) en el prompt de sistema.
   - **3b · Dos llamadas:** primero una búsqueda amplia y después un filtrado con las reglas de clasificación (unos 14 s en total).
   - **3c · 3a + 3b.**

   Se adopta la más simple que cumpla RNF-003 (principio 8).

   **Resultado (T035, 2026-10-19): se adopta 3a.** Con 55 casos validados, dos rondas: detección del 87,9 % en las dos, falsos positivos del 20,0 % y del 18,3 %, p95 de 3,7 s y 1,6 s, y rechazos correctos. La línea base sin ejemplos daba 67,7 % y 23,1 %. Como 3a cumple, no se prueban 3b ni 3c. Los resultados están en `evals/resultados/`.
4. **El rechazo (RF-015) se hace en la misma llamada del diagnóstico**, con el campo `rechazado`, en lugar de un clasificador aparte. El spike dio 100 % de rechazos correctos y ningún rechazo erróneo, y así se evita una segunda dependencia. Se revisa si las evals de RNF-007 fallan.
5. **El prompt de sistema es un artefacto versionado.** Vive en el repositorio como archivo de texto, no dentro del código, y cualquier cambio pasa por las evals (principio 5).

**Opciones descartadas:**
- Confiar en que el modelo cite bien sin validarlo: el spike mostró una alucinación (C08).
- Usar un modelo distinto para cada categoría: es complejo y lento, y no hay evidencia de que haga falta.

**Consecuencias:**
- ✅ RNF-004 queda garantizado por construcción, no por probabilidad.
- ✅ El cambio de prompt o de modelo se mide siempre.
- ✅ Estrategia 3 elegida y medida (3a): RNF-003 se cumple con una sola llamada.
- ⚠️ Los falsos positivos quedan cerca del límite (18–20 %). Cualquier cambio del prompt o del modelo tiene que volver a pasar las evals.
