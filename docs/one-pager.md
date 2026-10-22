# Sharpener · evaluador de prompts

**Estado:** aprobado · **Fases:** 0 y 1 · **Versión:** 1.0 · **Aprobado:** 2026-10-18 por Àlex Marco

**Problema:** muchas personas no consiguen de una IA el resultado que esperan y no saben por qué. Lo resuelven reescribiendo el prompt a base de prueba y error. Les pasa sobre todo a quienes tienen poco dominio de la IA, aunque también a usuarios con experiencia.

Las causas suelen ser falta de contexto, instrucciones ambiguas o contradictorias, no especificar el formato de salida, no dar ejemplos y no indicar restricciones. Quien escribe el prompt no las detecta.

Coste: es habitual necesitar unas 3 reescrituras por prompt hasta llegar al resultado esperado. A eso se suman el tiempo perdido, los resultados mediocres que se aceptan por cansancio y la frustración con la herramienta.

**Objetivo:** una aplicación que revise un prompt y haga tres cosas:
- Señalar dónde están los problemas y por qué.
- Explicar cómo precisarlo para obtener el resultado esperado.
- Ayudar a comprobar que la versión mejorada funciona mejor que la original.

Tiene que ser comprensible para personas sin conocimientos técnicos de IA.

**Criterios de éxito:**
1. Las reescrituras necesarias para llegar al resultado esperado bajan de 3 a 1 como máximo. Se mide sobre un conjunto de prompts reales: la revisión de la app cuenta como esa reescritura.
2. En una prueba con 5 personas con poco dominio de la IA, al menos 4 obtienen un resultado que consideran mejor con el prompt revisado que con el original, sin ayuda externa.
3. Se puede comprobar con casos de prueba si una versión del prompt es mejor que otra y repetir la comprobación más adelante (por ejemplo, al cambiar de modelo).

Fecha de evaluación: 3 meses después de completar el primer incremento (Fase 9).

**Usuarios y stakeholders:**
- Decide, desarrolla, paga y opera: Àlex Marco.
- Usuario inicial: Àlex Marco.
- Usuarios objetivo: personas con poco dominio de la IA que quieren mejores resultados.
- Puede vetar: nadie externo. Es un proyecto personal, sin relación con mi trabajo.

**Restricciones:**
- Fecha: sin plazo.
- Equipo: 1 persona con asistencia de IA.
- Presupuesto: 0 €. Se empieza con modelos de nivel gratuito.
- Plataforma: sin restricción. Se decide en el plan técnico (Fase 5).
- Proveedor de modelos: sin restricción, siempre que tenga nivel gratuito. Se decide en la Fase 5.
- Confidencialidad: no hay datos de trabajo ni de clientes. Si la usan otras personas, pueden introducir datos personales en sus prompts; se tratará en la Fase 8.
- Las claves de API nunca se integran en una versión publicada.

**Alternativas consideradas:**
- *Usar lo existente:*
  - Pedir directamente a ChatGPT, Claude o Gemini que mejoren el prompt. Es gratis e inmediato, pero el usuario tiene que saber pedirlo y no hay verificación.
  - Optimizadores de prompts de los proveedores, como el de la consola de Anthropic o el del playground de OpenAI. Están orientados a desarrolladores.
  - Herramientas de evaluación como promptfoo o Langfuse. Son técnicas y no ayudan a reescribir.
- *No hacer nada:* coste bajo. Las personas siguen iterando a ciegas.
- *Diferenciación:* la app combina cuatro cosas que un chatbot genérico no ofrece juntas:
  - (a) **Diagnóstico pedagógico:** enseña por qué falla el prompt, no solo da otra versión.
  - (b) **Verificación:** comprueba con casos de prueba que la versión nueva es mejor.
  - (c) **Guía para no expertos:** pregunta lo que falta en lugar de suponerlo.
  - (d) **Historial de versiones** del prompt.

**Decisión go/no-go:** decide Àlex Marco. Criterio: hay al menos una diferencia clara frente a «pedirle a un chatbot que mejore el prompt». Se cumple con (a)–(d). Decisión: **GO** · Fecha: 2026-10-18

---

## Fase 1 · Clasificación (aprobada el 2026-10-18)

| Eje | Valoración | Justificación |
|---|---|---|
| Criticidad | Baja | Si falla, la persona obtiene un mal consejo y lo nota; no hay pérdidas económicas ni riesgo para nadie. |
| Vida útil | Meses, posiblemente años | Herramienta de uso propio que se quiere abrir a otras personas. |
| Tamaño de equipo | 1 persona | Desarrollo individual asistido por IA. |
| Incertidumbre | Media–alta | No se sabe aún si un modelo gratuito diagnostica con calidad suficiente ni cómo explicar los problemas a no expertos. |
| Sensibilidad | Baja ahora; media al abrirla | Al principio solo hay prompts propios. Con otros usuarios pueden entrar datos personales y habrá que custodiar claves de API. |

**Perfil asignado:** **B · Herramienta**, con el rigor de seguridad del perfil **C** desde el momento en que la usen otras personas. Así lo indica la guía: ante la duda, el perfil superior para seguridad y el inferior para lo demás.

**Ciclo de vida:** iterativo e incremental, con entregas pequeñas. Por la incertidumbre, conviene una primera iteración que compruebe pronto la calidad del diagnóstico.

**Cuándo sube a C:** al publicarla para otras personas. En ese momento se revisan la constitución, la especificación y el plan con el nuevo rigor.

**Peso de los artefactos (perfil B):**

| Fase | Artefacto |
|---|---|
| 2 · Constitución | Una página |
| 3 · Especificación | Una página por incremento, con casos límite |
| 4 · Clarificar | Revisión por una persona y checklist |
| 5 · Plan | `plan.md` corto y 2–5 ADRs |
| 6 · Tareas | `tasks.md` priorizado |
| 7 · Harness | CI con linter y pruebas, `AGENTS.md`, evals del diagnóstico (porque el producto usa IA) |
| 8 · Seguridad | Revisión rápida de amenazas, que pasa a modelado completo al abrirla a otras personas |
| 9 · Primer incremento | Skeleton mínimo |
